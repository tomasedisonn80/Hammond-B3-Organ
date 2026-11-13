#include "TestSupport.h"
#include "hammond/ScannerLine.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <complex>
#include <cstddef>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <limits>
#include <vector>

namespace {

using namespace hammond;

constexpr std::array<double, 3> kHostRates{44100.0, 48000.0, 96000.0};
constexpr std::array<double, 5> kFactors{1.0, 2.0, 4.0, 8.0, 16.0};
constexpr std::array<ScannerReturnMode, 2> kModes{
    ScannerReturnMode::Vibrato, ScannerReturnMode::Chorus};
// Literal documentary values from atlas pp. 157-159; no generated/runtime data.
constexpr std::array<long double, 6> kUpperOhms{
    27000.0L, 56000.0L, 39000.0L, 33000.0L, 18000.0L, 12000.0L};
constexpr std::array<long double, 6> kLowerOhms{
    68000.0L, 150000.0L, 150000.0L, 180000.0L, 180000.0L, 180000.0L};
constexpr std::array<long double, 6> kVibratoDc{
    68.0L / 95.0L, 75.0L / 103.0L, 50.0L / 63.0L,
    60.0L / 71.0L, 10.0L / 11.0L, 15.0L / 16.0L};
constexpr std::array<long double, 6> kChorusDc{
    12463311899.0L / 13657495547.0L,
    12515270267.0L / 13657495547.0L,
    12790466267.0L / 13657495547.0L,
    13006519067.0L / 13657495547.0L,
    146030693737.0L / 150232451017.0L,
    13394885717.0L / 13657495547.0L};
constexpr long double kChorusReturnDc = 9455738267.0L / 13657495547.0L;
constexpr long double kVibratoInputDc = 9455738267.0L / 92438660160000.0L;
constexpr long double kChorusInputDc = 9455738267.0L / 300464902034000.0L;

std::size_t dc_responses = 0;
std::size_t basis_paths = 0;
std::size_t energy_paths = 0;
std::size_t energy_frames = 0;
std::size_t retune_pairs = 0;
std::size_t rejected_calls = 0;
std::size_t partition_paths = 0;
long double maximum_dc_error = 0.0L;
long double maximum_energy_increase = 0.0L;
long double maximum_final_energy = 0.0L;
struct EnergyObservation {
    double rate;
    ScannerReturnMode mode;
    std::size_t fixture;
    long double initial;
    long double final;
    long double positive_step_increase;
};
std::vector<EnergyObservation> energy_observations;

[[nodiscard]] long double physical_energy(const ScannerLineState& state) {
    long double result = 0.0L;
    for (std::size_t section = 0; section < 18; ++section) {
        const long double capacitance = section == 17 ? 1.0e-9L : 4.0e-9L;
        const long double voltage = state.capacitor_volts[section];
        const long double current = state.inductor_amps[section];
        result += 0.5L * capacitance * voltage * voltage;
        result += 0.25L * current * current; // 0.5 * L, L = 0.5 H.
    }
    return result;
}

[[nodiscard]] ScannerLineFrame sentinel_frame() {
    ScannerLineFrame frame;
    frame.taps_volts.fill(7.125);
    frame.return_volts = -0.75;
    frame.input_current_amps = 3.0;
    frame.energy_joules = 0.75;
    frame.frame = 9999;
    return frame;
}

[[nodiscard]] ScannerLineResponse sentinel_response() {
    ScannerLineResponse response;
    response.taps.fill({7.0, -3.0});
    response.return_gain = {9.0, 1.0};
    response.input_admittance = {5.0, -2.0};
    response.normalized_residual = 0.125;
    response.condition_inf = 7.0;
    return response;
}

void check_physical_observation(const ScannerLineState& state,
                                ScannerReturnMode mode,
                                const ScannerLineFrame& frame) {
    const long double input = state.previous_input_volts;
    // KCL at the return with only the input-side branch and input current
    // crossing the enclosing circuit boundary. This is an algebraic check,
    // not the runtime's state/transition matrix construction.
    const long double returned = mode == ScannerReturnMode::Vibrato ? 0.0L :
        (static_cast<long double>(state.inductor_amps[0]) + input / 95000.0L) /
            (1.0L / 22000.0L + 1.0L / 95000.0L);
    CHECK_NEAR(frame.return_volts, returned, 1.0e-12L + 1.0e-12L * std::fabs(returned));
    for (std::size_t divider = 0; divider < 6; ++divider) {
        const long double upstream = divider == 0 ? input :
            returned + static_cast<long double>(state.capacitor_volts[divider - 1]);
        const long double expected =
            (kLowerOhms[divider] * upstream + kUpperOhms[divider] * returned) /
            (kUpperOhms[divider] + kLowerOhms[divider]);
        CHECK_NEAR(frame.taps_volts[divider], expected,
                   1.0e-12L + 1.0e-12L * std::fabs(expected));
    }
    for (std::size_t tap = 6; tap < 19; ++tap) {
        const long double expected = returned + state.capacitor_volts[tap - 1];
        CHECK_NEAR(frame.taps_volts[tap], expected,
                   1.0e-12L + 1.0e-12L * std::fabs(expected));
    }
    const long double input_current = state.inductor_amps[0] + (input - returned) / 95000.0L;
    CHECK_NEAR(frame.input_current_amps, input_current,
               1.0e-15L + 1.0e-12L * std::fabs(input_current));
    if (mode == ScannerReturnMode::Chorus) {
        CHECK_NEAR(frame.input_current_amps, returned / 22000.0L,
                   1.0e-15L + 1.0e-12L * std::fabs(input_current));
    }
    const long double energy = physical_energy(state);
    CHECK_NEAR(frame.energy_joules, energy, 1.0e-24L + 1.0e-12L * energy);
    CHECK(frame.energy_joules >= 0.0);
    CHECK(frame.frame == state.frames);
    for (const double voltage : frame.taps_volts) CHECK(std::isfinite(voltage));
    for (const double voltage : state.capacitor_volts) CHECK(std::isfinite(voltage));
    for (const double current : state.inductor_amps) CHECK(std::isfinite(current));
}

[[nodiscard]] ScannerLineState sign_reversed(ScannerLineState state) {
    for (double& voltage : state.capacitor_volts) voltage = -voltage;
    for (double& current : state.inductor_amps) current = -current;
    state.previous_input_volts = -state.previous_input_volts;
    return state;
}

void check_sign_pair(const ScannerLineState& positive, const ScannerLineState& negative,
                     const ScannerLineFrame& positive_frame,
                     const ScannerLineFrame& negative_frame) {
    CHECK(positive.frames == negative.frames);
    for (std::size_t section = 0; section < 18; ++section) {
        CHECK_NEAR(negative.capacitor_volts[section], -positive.capacitor_volts[section],
                   1.0e-12L + 1.0e-12L * std::fabs(positive.capacitor_volts[section]));
        CHECK_NEAR(negative.inductor_amps[section], -positive.inductor_amps[section],
                   1.0e-15L + 1.0e-12L * std::fabs(positive.inductor_amps[section]));
    }
    for (std::size_t tap = 0; tap < 19; ++tap) {
        CHECK_NEAR(negative_frame.taps_volts[tap], -positive_frame.taps_volts[tap],
                   1.0e-12L + 1.0e-12L * std::fabs(positive_frame.taps_volts[tap]));
    }
    CHECK_NEAR(negative_frame.return_volts, -positive_frame.return_volts,
               1.0e-12L + 1.0e-12L * std::fabs(positive_frame.return_volts));
    CHECK_NEAR(negative_frame.input_current_amps, -positive_frame.input_current_amps,
               1.0e-15L + 1.0e-12L * std::fabs(positive_frame.input_current_amps));
    CHECK_NEAR(negative_frame.energy_joules, positive_frame.energy_joules,
               1.0e-24L + 1.0e-12L * positive_frame.energy_joules);
}

[[nodiscard]] ScannerLine precharged(double rate = 48000.0) {
    ScannerLine line;
    CHECK(line.prepare(rate) == Status::Ok);
    ScannerLineFrame frame;
    for (std::size_t index = 0; index < 127; ++index) {
        const double input = 0.6 * std::sin(static_cast<double>(index + 1) * 0.137);
        const auto mode = index % 7 < 3 ? ScannerReturnMode::Vibrato : ScannerReturnMode::Chorus;
        CHECK(line.process_frame(input, mode, frame) == Status::Ok);
    }
    CHECK(line.state().frames == 127);
    CHECK(physical_energy(line.state()) > 0.0L);
    CHECK(line.state().previous_input_volts != 0.0);
    return line;
}

void equal_future(ScannerLine actual, ScannerLine control) {
    CHECK(actual.prepared() == control.prepared());
    CHECK(actual.sample_rate() == control.sample_rate());
    CHECK(actual.preparation_residual() == control.preparation_residual());
    CHECK(actual.state() == control.state());
    for (std::size_t index = 0; index < 41; ++index) {
        const double input = (static_cast<double>(index % 13) - 6.0) / 16.0;
        const auto mode = index % 3 == 0 ? ScannerReturnMode::Chorus : ScannerReturnMode::Vibrato;
        ScannerLineFrame a;
        ScannerLineFrame b;
        CHECK(actual.process_frame(input, mode, a) == Status::Ok);
        CHECK(control.process_frame(input, mode, b) == Status::Ok);
        CHECK(a == b);
        CHECK(actual.state() == control.state());
    }
}

void test_defaults_and_preparation() {
    ScannerLine line;
    const ScannerLineState zero{};
    CHECK(!line.prepared());
    CHECK(line.sample_rate() == 0.0);
    CHECK(line.state() == zero);
    auto frame = sentinel_frame();
    const auto frame_before = frame;
    auto response = sentinel_response();
    const auto response_before = response;
    CHECK(line.process_frame(0.0, ScannerReturnMode::Vibrato, frame) == Status::NotPrepared);
    CHECK(line.observe(ScannerReturnMode::Chorus, frame) == Status::NotPrepared);
    CHECK(line.response(0.0, ScannerReturnMode::Vibrato, response) == Status::NotPrepared);
    CHECK(line.restore_state(zero) == Status::NotPrepared);
    CHECK(line.reconfigure_sample_rate(48000.0) == Status::NotPrepared);
    const double nan = std::numeric_limits<double>::quiet_NaN();
    const auto invalid_mode = static_cast<ScannerReturnMode>(255);
    auto invalid_state = zero;
    invalid_state.capacitor_volts[0] = nan;
    CHECK(line.process_frame(nan, invalid_mode, frame) == Status::NotPrepared);
    CHECK(line.observe(invalid_mode, frame) == Status::NotPrepared);
    CHECK(line.response(nan, invalid_mode, response) == Status::NotPrepared);
    CHECK(line.restore_state(invalid_state) == Status::NotPrepared);
    CHECK(line.reconfigure_sample_rate(nan) == Status::NotPrepared);
    CHECK(frame == frame_before);
    CHECK(response == response_before);
    CHECK(line.state() == zero);
    CHECK(kScannerLineModelId == "atlas-late-b3-nominal-line-v1");
    CHECK(ScannerLine::authoring_sha256().size() == 64);
    for (const char c : ScannerLine::authoring_sha256()) {
        CHECK((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f'));
    }
    for (const double rate : kHostRates) {
        for (const double factor : kFactors) {
            CHECK(is_supported_scanner_sample_rate(rate * factor));
            CHECK(line.prepare(rate * factor) == Status::Ok);
            CHECK(line.prepared());
            CHECK(line.sample_rate() == rate * factor);
            CHECK(line.state() == zero);
            CHECK(std::isfinite(line.preparation_residual()));
            CHECK(line.preparation_residual() >= 0.0);
            CHECK(line.preparation_residual() <= 1.0e-9);
            for (const auto mode : kModes) {
                CHECK(line.observe(mode, frame) == Status::Ok);
                ScannerLineFrame silent;
                silent.frame = line.state().frames;
                CHECK(frame == silent);
                CHECK(line.process_frame(0.0, mode, frame) == Status::Ok);
                CHECK(frame.frame == line.state().frames);
                CHECK(frame.energy_joules == 0.0);
                for (const double tap : frame.taps_volts) CHECK(tap == 0.0);
            }
        }
    }
    line = precharged();
    CHECK(line.prepare(96000.0) == Status::Ok);
    CHECK(line.state() == zero); // Explicit prepare is a cold initialization.
}

void check_dc_complex(const std::complex<double>& actual, long double expected) {
    const long double difference = std::abs(std::complex<long double>{actual.real(), actual.imag()} - expected);
    maximum_dc_error = std::max(maximum_dc_error, difference);
    CHECK_NEAR(difference, 0.0L, 1.0e-10L + 1.0e-9L * std::fabs(expected));
}

void test_literal_dc_answers() {
    for (const double rate : kHostRates) {
        for (const double factor : kFactors) {
            auto line = precharged(rate * factor);
            const auto before = line.state();
            for (const auto mode : kModes) {
                ScannerLineResponse response;
                CHECK(line.response(0.0, mode, response) == Status::Ok);
                const auto& first_six = mode == ScannerReturnMode::Vibrato ? kVibratoDc : kChorusDc;
                for (std::size_t tap = 0; tap < 6; ++tap) check_dc_complex(response.taps[tap], first_six[tap]);
                for (std::size_t tap = 6; tap < 19; ++tap) check_dc_complex(response.taps[tap], 1.0L);
                check_dc_complex(response.return_gain,
                                 mode == ScannerReturnMode::Vibrato ? 0.0L : kChorusReturnDc);
                // Scale admittance to dimensionless units, matching the frozen contract.
                check_dc_complex(15000.0 * response.input_admittance,
                    15000.0L * (mode == ScannerReturnMode::Vibrato ? kVibratoInputDc : kChorusInputDc));
                CHECK(response.normalized_residual >= 0.0);
                CHECK(response.normalized_residual <= 1.0e-9);
                CHECK(std::isfinite(response.condition_inf));
                CHECK(response.condition_inf >= 1.0);
                CHECK(response.condition_inf * 0x1p-52 <= 1.0e-4);
                CHECK(line.state() == before);
                ++dc_responses;
            }
        }
    }
}

void test_basis_states_and_polarity() {
    for (const double rate : kHostRates) {
        for (const auto mode : kModes) {
            for (std::size_t coordinate = 0; coordinate < 36; ++coordinate) {
                ScannerLine positive;
                ScannerLine negative;
                CHECK(positive.prepare(rate) == Status::Ok);
                CHECK(negative.prepare(rate) == Status::Ok);
                ScannerLineState initial;
                initial.frames = 37;
                if (coordinate < 18) initial.capacitor_volts[coordinate] = 1.0;
                else initial.inductor_amps[coordinate - 18] = 1.0e-4;
                CHECK(positive.restore_state(initial) == Status::Ok);
                CHECK(negative.restore_state(sign_reversed(initial)) == Status::Ok);
                ScannerLineFrame p;
                ScannerLineFrame n;
                CHECK(positive.observe(mode, p) == Status::Ok);
                CHECK(negative.observe(mode, n) == Status::Ok);
                check_physical_observation(initial, mode, p);
                check_physical_observation(negative.state(), mode, n);
                const long double expected_energy = coordinate < 18 ?
                    (coordinate == 17 ? 0.5e-9L : 2.0e-9L) : 2.5e-9L;
                CHECK_NEAR(p.energy_joules, expected_energy, 1.0e-24L + 1.0e-12L * expected_energy);
                for (std::size_t sample = 0; sample < 64; ++sample) {
                    CHECK(positive.process_frame(0.0, mode, p) == Status::Ok);
                    CHECK(negative.process_frame(0.0, mode, n) == Status::Ok);
                    check_physical_observation(positive.state(), mode, p);
                    check_physical_observation(negative.state(), mode, n);
                    check_sign_pair(positive.state(), negative.state(), p, n);
                    CHECK(p.frame == 38 + static_cast<std::uint64_t>(sample));
                }
                basis_paths += 2;
            }
        }
    }
}

void test_driven_polarity() {
    for (const double rate : kHostRates) {
        ScannerLine positive;
        ScannerLine negative;
        CHECK(positive.prepare(rate) == Status::Ok);
        CHECK(negative.prepare(rate) == Status::Ok);
        for (std::size_t sample = 0; sample < 1024; ++sample) {
            const double input = std::sin(static_cast<double>(sample) * 0.173) * 0.5;
            const auto mode = sample % 101 < 51 ? ScannerReturnMode::Vibrato : ScannerReturnMode::Chorus;
            ScannerLineFrame p;
            ScannerLineFrame n;
            CHECK(positive.process_frame(input, mode, p) == Status::Ok);
            CHECK(negative.process_frame(-input, mode, n) == Status::Ok);
            CHECK(positive.state().previous_input_volts == input);
            CHECK(negative.state().previous_input_volts == -input);
            check_sign_pair(positive.state(), negative.state(), p, n);
        }
    }
}

void test_zero_drive_energy() {
    // Frozen contract's four charged states, both modes, 250 ms at each host rate.
    for (const double rate : kHostRates) {
        for (const auto mode : kModes) {
            for (std::size_t fixture = 0; fixture < 4; ++fixture) {
                ScannerLine line;
                CHECK(line.prepare(rate) == Status::Ok);
                ScannerLineState initial;
                if (fixture == 0) initial.capacitor_volts[0] = 1.0;
                else if (fixture == 1) initial.capacitor_volts[17] = -1.0;
                else if (fixture == 2) initial.inductor_amps[0] = 1.0e-4;
                else initial.inductor_amps[17] = -1.0e-4;
                CHECK(line.restore_state(initial) == Status::Ok);
                const long double starting_energy = physical_energy(initial);
                long double previous_energy = starting_energy;
                long double positive_step_increase = 0.0L;
                const auto samples = static_cast<std::size_t>(rate / 4.0);
                for (std::size_t sample = 0; sample < samples; ++sample) {
                    ScannerLineFrame frame;
                    CHECK(line.process_frame(0.0, mode, frame) == Status::Ok);
                    const long double current_energy = physical_energy(line.state());
                    const long double increase = current_energy - previous_energy;
                    maximum_energy_increase = std::max(maximum_energy_increase, increase);
                    positive_step_increase = std::max(positive_step_increase, increase);
                    CHECK(increase <= 1.0e-12L * starting_energy + 1.0e-24L);
                    CHECK(current_energy - starting_energy <= 1.0e-10L * starting_energy + 1.0e-24L);
                    CHECK_NEAR(frame.energy_joules, current_energy,
                               1.0e-24L + 1.0e-12L * current_energy);
                    CHECK(line.state().previous_input_volts == 0.0);
                    previous_energy = current_energy;
                    ++energy_frames;
                }
                maximum_final_energy = std::max(maximum_final_energy, previous_energy);
                energy_observations.push_back({rate, mode, fixture, starting_energy,
                                               previous_energy, positive_step_increase});
                ++energy_paths;
            }
        }
    }
}

void test_rate_and_mode_observation() {
    for (const double old_rate : kHostRates) {
        for (const double new_rate : kHostRates) {
            auto line = precharged(old_rate);
            const auto state = line.state();
            std::array<ScannerLineFrame, 2> before;
            for (std::size_t mode_index = 0; mode_index < kModes.size(); ++mode_index) {
                CHECK(line.observe(kModes[mode_index], before[mode_index]) == Status::Ok);
                check_physical_observation(state, kModes[mode_index], before[mode_index]);
                CHECK(line.state() == state);
            }
            CHECK(before[0].return_volts == 0.0);
            CHECK(before[1].return_volts != 0.0);
            CHECK(line.reconfigure_sample_rate(new_rate) == Status::Ok);
            CHECK(line.sample_rate() == new_rate);
            CHECK(line.state() == state);
            for (std::size_t mode_index = 0; mode_index < kModes.size(); ++mode_index) {
                ScannerLineFrame after;
                CHECK(line.observe(kModes[mode_index], after) == Status::Ok);
                CHECK(after == before[mode_index]);
                CHECK(line.state() == state);
            }
            ScannerLine independently_prepared;
            CHECK(independently_prepared.prepare(new_rate) == Status::Ok);
            CHECK(independently_prepared.restore_state(state) == Status::Ok);
            equal_future(line, independently_prepared);
            ++retune_pairs;
        }
    }
}

void test_admission_and_rejection() {
    const auto original = precharged();
    const auto invalid_mode = static_cast<ScannerReturnMode>(255);
    const double nan = std::numeric_limits<double>::quiet_NaN();
    const double infinity = std::numeric_limits<double>::infinity();
    const std::array<double, 8> invalid_inputs{
        nan, infinity, -infinity, std::nextafter(kScannerMaxInputVolts, infinity),
        -std::nextafter(kScannerMaxInputVolts, infinity), 65.0, -65.0, 1.0e100};
    for (const double input : invalid_inputs) {
        auto line = original;
        auto frame = sentinel_frame();
        const auto before = frame;
        CHECK(line.process_frame(input, ScannerReturnMode::Chorus, frame) == Status::InvalidBuffer);
        CHECK(frame == before);
        equal_future(line, original);
        ++rejected_calls;
    }
    {
        auto line = original;
        auto frame = sentinel_frame();
        const auto before = frame;
        CHECK(line.process_frame(0.25, invalid_mode, frame) == Status::InvalidEvent);
        CHECK(frame == before);
        equal_future(line, original);
        CHECK(line.observe(invalid_mode, frame) == Status::InvalidEvent);
        CHECK(frame == before);
        equal_future(line, original);
        auto response = sentinel_response();
        const auto response_before = response;
        CHECK(line.response(1000.0, invalid_mode, response) == Status::InvalidEvent);
        CHECK(response == response_before);
        equal_future(line, original);
        rejected_calls += 3;
    }
    const std::array<double, 10> invalid_rates{
        nan, infinity, -infinity, 0.0, -48000.0, 22050.0, 48001.0,
        std::nextafter(44100.0, infinity), std::nextafter(1536000.0, infinity), 1000000.0};
    for (const double rate : invalid_rates) {
        CHECK(!is_supported_scanner_sample_rate(rate));
        auto line = original;
        CHECK(line.prepare(rate) == Status::InvalidSpec);
        equal_future(line, original);
        CHECK(line.reconfigure_sample_rate(rate) == Status::InvalidSpec);
        equal_future(line, original);
        rejected_calls += 2;
    }
    const std::array<double, 6> invalid_frequencies{
        nan, infinity, -infinity, -1.0, 24000.0, std::nextafter(24000.0, infinity)};
    for (const double frequency : invalid_frequencies) {
        auto line = original;
        auto response = sentinel_response();
        const auto before = response;
        CHECK(line.response(frequency, ScannerReturnMode::Chorus, response) == Status::InvalidSpec);
        CHECK(response == before);
        equal_future(line, original);
        ++rejected_calls;
    }
    for (const double value : {nan, infinity, -infinity}) {
        for (std::size_t coordinate = 0; coordinate < 37; ++coordinate) {
            auto line = original;
            auto invalid = original.state();
            if (coordinate < 18) invalid.capacitor_volts[coordinate] = value;
            else if (coordinate < 36) invalid.inductor_amps[coordinate - 18] = value;
            else invalid.previous_input_volts = value;
            CHECK(line.restore_state(invalid) == Status::InvalidProfile);
            equal_future(line, original);
            ++rejected_calls;
        }
    }
    for (const double sign : {-1.0, 1.0}) {
        for (std::size_t coordinate = 0; coordinate < 37; ++coordinate) {
            auto line = original;
            ScannerLineState invalid;
            if (coordinate < 18) invalid.capacitor_volts[coordinate] =
                sign * std::nextafter(kScannerMaxCapacitorVolts, infinity);
            else if (coordinate < 36) invalid.inductor_amps[coordinate - 18] =
                sign * std::nextafter(kScannerMaxInductorAmps, infinity);
            else invalid.previous_input_volts = sign * std::nextafter(kScannerMaxInputVolts, infinity);
            CHECK(line.restore_state(invalid) == Status::InvalidProfile);
            equal_future(line, original);
            ++rejected_calls;
        }
    }
    {
        auto line = original;
        ScannerLineState invalid;
        invalid.inductor_amps[7] = 1.5;
        invalid.inductor_amps[8] = -1.5;
        CHECK(physical_energy(invalid) > 1.0L); // Both individual currents remain legal.
        CHECK(line.restore_state(invalid) == Status::InvalidProfile);
        equal_future(line, original);
        ++rejected_calls;
    }
    // Inclusive energy and input-history boundaries, independently meaningful
    // even though the capacitor coordinate cap cannot itself fit the 1 J limit.
    for (const double sign : {-1.0, 1.0}) {
        ScannerLine line;
        CHECK(line.prepare(48000.0) == Status::Ok);
        ScannerLineState boundary;
        boundary.inductor_amps[17] = 2.0 * sign;
        CHECK(physical_energy(boundary) == 1.0L);
        CHECK(line.restore_state(boundary) == Status::Ok);
        for (const auto mode : kModes) {
            ScannerLineFrame frame;
            CHECK(line.observe(mode, frame) == Status::Ok);
            check_physical_observation(boundary, mode, frame);
        }
        boundary = {};
        boundary.previous_input_volts = 64.0 * sign;
        CHECK(line.restore_state(boundary) == Status::Ok);
        ScannerLineFrame frame;
        CHECK(line.observe(ScannerReturnMode::Chorus, frame) == Status::Ok);
        check_physical_observation(boundary, ScannerReturnMode::Chorus, frame);
        CHECK(line.prepare(48000.0) == Status::Ok);
        CHECK(line.process_frame(64.0 * sign, ScannerReturnMode::Vibrato, frame) == Status::Ok);
    }
}

void test_candidate_energy_rejection() {
    // A legal nearly 1 J interior inductor checkpoint plus a legal 64 V
    // endpoint exceeds the joint next-state energy bound. The 1e-9 J initial
    // headroom makes this a finite forcing case, not a boundary-rounding test.
    for (const double rate : kHostRates) {
        for (const auto mode : kModes) {
            for (const double sign : {-1.0, 1.0}) {
                ScannerLine line;
                CHECK(line.prepare(rate) == Status::Ok);
                ScannerLineState state;
                state.inductor_amps[9] = sign * 1.999999999;
                state.frames = 127;
                CHECK(physical_energy(state) < 1.0L);
                CHECK(physical_energy(state) > 0.999999998L);
                CHECK(line.restore_state(state) == Status::Ok);
                const auto control = line;
                // The half-amplitude process is admitted. Linearity permits
                // reconstruction of the full candidate, whose independently
                // calculated physical energy exceeds 1 J while each coordinate
                // remains within its individual bound. No transition matrix or
                // producer energy calculation supplies this expectation.
                auto half = line;
                auto half_initial = state;
                half_initial.inductor_amps[9] *= 0.5;
                CHECK(half.restore_state(half_initial) == Status::Ok);
                ScannerLineFrame half_frame;
                CHECK(half.process_frame(sign * 32.0, mode, half_frame) == Status::Ok);
                auto full_candidate = half.state();
                for (double& voltage : full_candidate.capacitor_volts) {
                    voltage *= 2.0;
                    CHECK(std::abs(voltage) <= kScannerMaxCapacitorVolts);
                }
                for (double& current : full_candidate.inductor_amps) {
                    current *= 2.0;
                    CHECK(std::abs(current) <= kScannerMaxInductorAmps);
                }
                CHECK(physical_energy(full_candidate) > 1.0L + 1.0e-10L);
                auto frame = sentinel_frame();
                const auto before = frame;
                CHECK(line.process_frame(sign * 64.0, mode, frame) == Status::InvalidBuffer);
                CHECK(frame == before);
                CHECK(line.state() == state);
                equal_future(line, control);
                ++rejected_calls;
            }
        }
    }
}

void test_frame_overflow() {
    auto line = precharged();
    auto state = line.state();
    state.frames = std::numeric_limits<std::uint64_t>::max() - 1;
    CHECK(line.restore_state(state) == Status::Ok);
    ScannerLineFrame frame;
    CHECK(line.process_frame(0.0, ScannerReturnMode::Vibrato, frame) == Status::Ok);
    CHECK(frame.frame == std::numeric_limits<std::uint64_t>::max());
    const auto before = line.state();
    auto untouched = line;
    const auto frame_before = frame;
    CHECK(line.process_frame(0.0, ScannerReturnMode::Chorus, frame) == Status::TimelineOverflow);
    CHECK(line.state() == before);
    CHECK(frame == frame_before);
    CHECK(line.observe(ScannerReturnMode::Chorus, frame) == Status::Ok);
    CHECK(frame.frame == std::numeric_limits<std::uint64_t>::max());
    check_physical_observation(before, ScannerReturnMode::Chorus, frame);
    CHECK(line.state() == before);
    ++rejected_calls;
    ScannerLine restored;
    CHECK(restored.prepare(48000.0) == Status::Ok);
    CHECK(restored.restore_state(before) == Status::Ok);
    const auto observed_before = frame;
    CHECK(restored.process_frame(0.0, ScannerReturnMode::Vibrato, frame) == Status::TimelineOverflow);
    CHECK(frame == observed_before);
    CHECK(restored.state() == before);
    ++rejected_calls;
    // A saturated timeline cannot process a successful next frame. Restore
    // the same physical endpoint at a usable count to compare continuation.
    auto replay = before;
    replay.frames = 127;
    CHECK(line.restore_state(replay) == Status::Ok);
    CHECK(restored.restore_state(replay) == Status::Ok);
    CHECK(untouched.restore_state(replay) == Status::Ok);
    equal_future(line, untouched);
    equal_future(restored, untouched);
}

void test_external_partitions_and_observation() {
    constexpr std::size_t samples = 1024;
    constexpr std::array<std::size_t, 7> irregular{1, 17, 64, 3, 127, 2, 31};
    std::array<double, samples> input{};
    for (std::size_t index = 0; index < samples; ++index) {
        input[index] = 0.4 * std::sin(static_cast<double>(index) * 0.113) +
                       0.2 * std::cos(static_cast<double>(index) * 0.039);
    }
    const auto mode_at = [](std::size_t index) {
        return index % 313 < 155 ? ScannerReturnMode::Vibrato : ScannerReturnMode::Chorus;
    };
    for (const double rate : kHostRates) {
        auto reference = precharged(rate);
        const auto initial = reference;
        std::vector<ScannerLineFrame> expected(samples);
        for (std::size_t index = 0; index < samples; ++index) {
            CHECK(reference.process_frame(input[index], mode_at(index), expected[index]) == Status::Ok);
        }
        for (const std::size_t partition : {std::size_t{1}, std::size_t{64}, std::size_t{127}, std::size_t{0}}) {
            auto line = initial;
            std::size_t cursor = 0;
            std::size_t chunk = 0;
            while (cursor < samples) {
                const auto state = line.state();
                for (const auto mode : kModes) {
                    ScannerLineFrame observation;
                    CHECK(line.observe(mode, observation) == Status::Ok);
                    check_physical_observation(state, mode, observation);
                    CHECK(line.state() == state);
                }
                const std::size_t count = std::min(samples - cursor,
                    partition == 0 ? irregular[chunk % irregular.size()] : partition);
                for (std::size_t within = 0; within < count; ++within) {
                    const std::size_t index = cursor + within;
                    ScannerLineFrame actual;
                    CHECK(line.process_frame(input[index], mode_at(index), actual) == Status::Ok);
                    CHECK(actual == expected[index]);
                }
                cursor += count;
                ++chunk;
            }
            CHECK(line.state() == reference.state());
            ++partition_paths;
        }
    }
}

} // namespace

int main() {
    test_defaults_and_preparation();
    test_literal_dc_answers();
    test_basis_states_and_polarity();
    test_driven_polarity();
    test_zero_drive_energy();
    test_rate_and_mode_observation();
    test_admission_and_rejection();
    test_candidate_energy_rejection();
    test_frame_overflow();
    test_external_partitions_and_observation();
    std::cout << std::setprecision(17)
              << "scanner line state acceptance passed\n"
              << "dc_responses=" << dc_responses
              << " maximum_dc_complex_error=" << static_cast<double>(maximum_dc_error) << '\n'
              << "basis_paths=" << basis_paths << " energy_paths=" << energy_paths
              << " energy_frames=" << energy_frames << '\n'
              << "maximum_zero_drive_energy_increase_joules=" << static_cast<double>(maximum_energy_increase)
              << " maximum_final_energy_joules=" << static_cast<double>(maximum_final_energy) << '\n'
              << "retune_pairs=" << retune_pairs << " rejected_calls=" << rejected_calls
              << " external_partition_paths=" << partition_paths << '\n';
    constexpr std::array<const char*, 4> fixtures{"x1=+1V", "x18=-1V", "i1=+1e-4A", "i18=-1e-4A"};
    for (const auto& observation : energy_observations) {
        std::cout << "energy rate=" << observation.rate
                  << " mode=" << (observation.mode == ScannerReturnMode::Vibrato ? "vibrato" : "chorus")
                  << " fixture=" << fixtures[observation.fixture]
                  << " initial_joules=" << static_cast<double>(observation.initial)
                  << " final_joules=" << static_cast<double>(observation.final)
                  << " maximum_positive_step_increase_joules="
                  << static_cast<double>(observation.positive_step_increase) << '\n';
    }
}
