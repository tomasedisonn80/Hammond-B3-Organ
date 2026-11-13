#include "TestSupport.h"
#include "hammond/ScannerRotor.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <limits>
#include <string_view>
#include <vector>

namespace {

using namespace hammond;
using Taps = std::array<double, 19>;
using Terminals = std::array<double, 9>;
using Weights = std::array<long double, 9>;

constexpr std::array<ScannerMode, 6> kModes{
    ScannerMode::V1, ScannerMode::V2, ScannerMode::V3,
    ScannerMode::C1, ScannerMode::C2, ScannerMode::C3};
constexpr std::array<std::string_view, 6> kNames{"V1", "V2", "V3", "C1", "C2", "C3"};
constexpr std::array<std::size_t, 6> kModeDepths{0, 1, 2, 0, 1, 2};
constexpr std::array<ScannerReturnMode, 6> kReturns{
    ScannerReturnMode::Vibrato, ScannerReturnMode::Vibrato, ScannerReturnMode::Vibrato,
    ScannerReturnMode::Chorus, ScannerReturnMode::Chorus, ScannerReturnMode::Chorus};
// Independently transcribed one-based values: atlas p.170 / DAFx2016 Table 2.
// These expectations do not read a production map, traversal or helper.
constexpr std::array<std::array<std::size_t, 9>, 3> kTapNumbers{{
    {1, 2, 3, 4, 5, 6, 7, 8, 9},
    {1, 2, 3, 5, 7, 9, 11, 12, 13},
    {1, 2, 4, 7, 10, 13, 16, 18, 19},
}};
constexpr std::array<std::size_t, 16> kTerminalNumbers{
    1, 2, 3, 4, 5, 6, 7, 8, 9, 8, 7, 6, 5, 4, 3, 2};
constexpr std::array<double, 3> kHostRates{44100.0, 48000.0, 96000.0};
constexpr std::array<double, 5> kFactors{1.0, 2.0, 4.0, 8.0, 16.0};
constexpr long double kDocumentarySpeedHz = 412.0L / 60.0L;
constexpr double kTapLimit = 131072.0;

std::size_t stateless_cases = 0;
std::size_t chorus_cases = 0;
std::size_t rejected_calls = 0;
std::size_t continuation_frames = 0;
std::size_t clock_frames = 0;
std::size_t partition_paths = 0;
std::size_t rate_pairs = 0;
long double maximum_oracle_error = 0.0L;
long double maximum_chorus_error = 0.0L;
long double maximum_clock_drift = 0.0L;

// An independent angular reference sums triangular basis functions centered on
// each terminal's occurrences around the circle. It never selects an interval
// or interpolates the production traversal's two adjacent entries.
[[nodiscard]] long double circular_hat(long double phase, long double center) {
    const long double direct = std::fabs(phase - center);
    const long double distance = std::min(direct, 1.0L - direct);
    return std::max(0.0L, 1.0L - 16.0L * distance);
}

[[nodiscard]] Weights angular_weights(double phase) {
    const long double p = phase;
    Weights weights{};
    weights[0] = circular_hat(p, 0.0L);
    weights[8] = circular_hat(p, 0.5L);
    for (std::size_t terminal = 1; terminal < 8; ++terminal) {
        const long double center = static_cast<long double>(terminal) / 16.0L;
        weights[terminal] = circular_hat(p, center) + circular_hat(p, 1.0L - center);
    }
    return weights;
}

[[nodiscard]] long double reference_output(double phase, const Taps& taps, std::size_t depth) {
    const auto weights = angular_weights(phase);
    long double result = 0.0L;
    for (std::size_t terminal = 0; terminal < 9; ++terminal) {
        result += weights[terminal] * static_cast<long double>(taps[kTapNumbers[depth][terminal] - 1]);
    }
    return result;
}

[[nodiscard]] std::vector<double> required_phases() {
    std::vector<double> phases;
    for (std::size_t position = 0; position < 16; ++position) {
        const double center = static_cast<double>(position) / 16.0;
        phases.push_back(center);
        for (const double quarter : std::array<double, 3>{0.25, 0.5, 0.75}) {
            phases.push_back((static_cast<double>(position) + quarter) / 16.0);
        }
        // Left of zero is represented on the admitted circle just below one.
        phases.push_back(position == 0 ? std::nextafter(1.0, 0.0)
                                      : std::nextafter(center, 0.0));
        phases.push_back(std::nextafter(center, 1.0));
    }
    CHECK(phases.size() == 96);
    return phases;
}

[[nodiscard]] Taps selected_taps(const Terminals& terminals, std::size_t depth) {
    Taps taps{};
    // Distinct nonzero unselected values detect accidental use of another map.
    for (std::size_t tap = 0; tap < taps.size(); ++tap) {
        taps[tap] = (tap % 2 == 0 ? 1.0 : -1.0) * (4.0 + static_cast<double>(tap) / 8.0);
    }
    for (std::size_t terminal = 0; terminal < terminals.size(); ++terminal) {
        taps[kTapNumbers[depth][terminal] - 1] = terminals[terminal];
    }
    return taps;
}

[[nodiscard]] Taps driven_taps(std::size_t frame) {
    Taps taps{};
    for (std::size_t tap = 0; tap < taps.size(); ++tap) {
        const auto residue = (frame * 13 + tap * 7) % 101;
        taps[tap] = (static_cast<double>(residue) - 50.0) / 32.0;
    }
    return taps;
}

[[nodiscard]] ScannerRotorFrame sentinel_frame() {
    ScannerRotorFrame result;
    result.selection.phase_turns = 0.8125;
    result.selection.position_index = 71;
    result.selection.terminal_indices = {72, 73};
    result.selection.tap_indices = {74, 75};
    result.selection.weights = {-3.25, 4.25};
    result.output_volts = -7.125;
    result.frame = 999999;
    return result;
}

void check_selection(double phase, std::size_t mode_index,
                     const ScannerRotorSelection& selection) {
    const auto position = static_cast<std::size_t>(std::floor(static_cast<long double>(phase) * 16.0L));
    const auto next = (position + 1) % 16;
    const auto depth = kModeDepths[mode_index];
    CHECK(selection.phase_turns == phase);
    CHECK(selection.position_index == position);
    CHECK(selection.terminal_indices[0] == kTerminalNumbers[position] - 1);
    CHECK(selection.terminal_indices[1] == kTerminalNumbers[next] - 1);
    for (std::size_t side = 0; side < 2; ++side) {
        CHECK(selection.tap_indices[side] == kTapNumbers[depth][selection.terminal_indices[side]] - 1);
        CHECK(std::isfinite(selection.weights[side]));
        CHECK(selection.weights[side] >= 0.0);
        CHECK(selection.weights[side] <= 1.0);
        const auto weights = angular_weights(phase);
        CHECK_NEAR(selection.weights[side], weights[selection.terminal_indices[side]], 2.0e-15L);
    }
    CHECK_NEAR(selection.weights[0] + selection.weights[1], 1.0, 2.0e-15L);
}

void check_stateless_case(double phase, const Taps& taps, std::size_t mode_index) {
    auto frame = sentinel_frame();
    CHECK(ScannerRotor::evaluate(phase, taps, kModes[mode_index], frame) == Status::Ok);
    CHECK(frame.frame == 0);
    check_selection(phase, mode_index, frame.selection);
    const auto expected = reference_output(phase, taps, kModeDepths[mode_index]);
    const auto error = std::fabs(static_cast<long double>(frame.output_volts) - expected);
    maximum_oracle_error = std::max(maximum_oracle_error, error);
    CHECK_NEAR(frame.output_volts, expected, 2.0e-12L + 2.0e-12L * std::fabs(expected));
    auto selection = sentinel_frame().selection;
    CHECK(ScannerRotor::select(phase, kModes[mode_index], selection) == Status::Ok);
    CHECK(selection == frame.selection);
    ++stateless_cases;
}

void static_maps_and_weights() {
    const auto phases = required_phases();
    for (std::size_t mode_index = 0; mode_index < kModes.size(); ++mode_index) {
        const auto depth = kModeDepths[mode_index];
        for (const double phase : phases) {
            for (std::size_t terminal = 0; terminal < 9; ++terminal) {
                for (const double sign : std::array<double, 2>{-1.0, 1.0}) {
                    Terminals values{};
                    values[terminal] = sign;
                    check_stateless_case(phase, selected_taps(values, depth), mode_index);
                }
            }
            for (const double sign : std::array<double, 2>{-1.0, 1.0}) {
                Terminals values{};
                values.fill(sign);
                check_stateless_case(phase, selected_taps(values, depth), mode_index);
            }
            const Terminals unequal{-0.875, 0.25, -0.5, 0.0625, 0.9375, -0.125, 0.5, -0.75, 0.3125};
            check_stateless_case(phase, selected_taps(unequal, depth), mode_index);
            // Every line output, including outputs not selected by this depth,
            // also receives an independent signed basis test.
            for (std::size_t tap = 0; tap < 19; ++tap) {
                Taps values{};
                values[tap] = tap % 2 == 0 ? 1.0 : -1.0;
                check_stateless_case(phase, values, mode_index);
            }
        }
        std::array<std::size_t, 9> visits{};
        for (std::size_t position = 0; position < 16; ++position) {
            ScannerRotorSelection selection;
            CHECK(ScannerRotor::select(static_cast<double>(position) / 16.0,
                                       kModes[mode_index], selection) == Status::Ok);
            CHECK(selection.weights[0] == 1.0);
            CHECK(selection.weights[1] == 0.0);
            ++visits[selection.terminal_indices[0]];
        }
        CHECK(visits[0] == 1);
        CHECK(visits[8] == 1);
        for (std::size_t terminal = 1; terminal < 8; ++terminal) CHECK(visits[terminal] == 2);
    }
    // Inclusive finite endpoint voltage bounds must remain convex, including
    // opposite polarities. No magnitude rectification or overshoot is allowed.
    for (std::size_t mode_index = 0; mode_index < 6; ++mode_index) {
        for (const double phase : phases) {
            Taps taps{};
            for (std::size_t tap = 0; tap < 19; ++tap) taps[tap] = tap % 2 == 0 ? kTapLimit : -kTapLimit;
            check_stateless_case(phase, taps, mode_index);
            ScannerRotorFrame frame;
            CHECK(ScannerRotor::evaluate(phase, taps, kModes[mode_index], frame) == Status::Ok);
            CHECK(std::fabs(frame.output_volts) <= kTapLimit);
        }
    }
}

void chorus_return_once() {
    const Terminals local{-0.875, 0.25, -0.5, 0.0625, 0.9375, -0.125, 0.5, -0.75, 0.3125};
    for (std::size_t depth = 0; depth < 3; ++depth) {
        const auto local_taps = selected_taps(local, depth);
        auto ground_taps = local_taps;
        for (double& value : ground_taps) value += 0.375;
        for (const double phase : required_phases()) {
            ScannerRotorFrame vibrato, chorus;
            CHECK(ScannerRotor::evaluate(phase, local_taps, kModes[depth], vibrato) == Status::Ok);
            CHECK(ScannerRotor::evaluate(phase, ground_taps, kModes[depth + 3], chorus) == Status::Ok);
            CHECK(vibrato.selection == chorus.selection);
            const auto expected = 0.375L + reference_output(phase, local_taps, depth);
            const auto error = std::fabs(static_cast<long double>(chorus.output_volts) - expected);
            maximum_chorus_error = std::max(maximum_chorus_error, error);
            CHECK_NEAR(chorus.output_volts, expected, 2.0e-12L + 2.0e-12L * std::fabs(expected));
            CHECK_NEAR(chorus.output_volts, 0.375L + vibrato.output_volts,
                       2.0e-12L + 2.0e-12L * std::fabs(expected));
            ++chorus_cases;
        }
    }
}

void mode_helpers() {
    for (std::size_t index = 0; index < kModes.size(); ++index) {
        CHECK(is_valid_scanner_mode(kModes[index]));
        CHECK(scanner_mode_name(kModes[index]) == kNames[index]);
        ScannerReturnMode returned = static_cast<ScannerReturnMode>(99);
        std::size_t depth = 99;
        CHECK(scanner_mode_return(kModes[index], returned));
        CHECK(scanner_mode_depth(kModes[index], depth));
        CHECK(returned == kReturns[index]);
        CHECK(depth == kModeDepths[index]);
    }
    for (unsigned value = 6; value <= 255; ++value) {
        const auto mode = static_cast<ScannerMode>(value);
        ScannerReturnMode returned = ScannerReturnMode::Chorus;
        std::size_t depth = 99;
        CHECK(!is_valid_scanner_mode(mode));
        CHECK(scanner_mode_name(mode).empty());
        CHECK(!scanner_mode_return(mode, returned));
        CHECK(!scanner_mode_depth(mode, depth));
        CHECK(returned == ScannerReturnMode::Chorus);
        CHECK(depth == 99);
    }
}

[[nodiscard]] ScannerRotor precharged(double rate = 48000.0) {
    ScannerRotor rotor;
    CHECK(rotor.prepare(rate) == Status::Ok);
    for (std::size_t frame = 0; frame < 237; ++frame) {
        ScannerRotorFrame result;
        CHECK(rotor.process_frame(driven_taps(frame), kModes[frame % 6], result) == Status::Ok);
    }
    CHECK(rotor.state().phase_turns > 0.0);
    CHECK(rotor.state().frames == 237);
    return rotor;
}

void equal_continuation(ScannerRotor& actual, ScannerRotor& control) {
    for (std::size_t frame = 0; frame < 41; ++frame) {
        ScannerRotorFrame a, b;
        const auto taps = driven_taps(frame + 127);
        const auto mode = kModes[(frame * 5) % 6];
        CHECK(actual.process_frame(taps, mode, a) == Status::Ok);
        CHECK(control.process_frame(taps, mode, b) == Status::Ok);
        CHECK(a == b);
        CHECK(actual.state() == control.state());
        ++continuation_frames;
    }
}

template <typename Operation>
void rejected(ScannerRotor actual, Status expected, Operation operation) {
    auto control = actual;
    auto destination = sentinel_frame();
    const auto original_destination = destination;
    CHECK(operation(actual, destination) == expected);
    CHECK(destination == original_destination);
    CHECK(actual.prepared() == control.prepared());
    CHECK(actual.sample_rate() == control.sample_rate());
    CHECK(actual.phase_increment_turns() == control.phase_increment_turns());
    CHECK(actual.state() == control.state());
    ++rejected_calls;
    equal_continuation(actual, control);
}

void errors_and_transactions() {
    const double nan = std::numeric_limits<double>::quiet_NaN();
    const double infinity = std::numeric_limits<double>::infinity();
    const Taps valid = driven_taps(17);
    const auto prepared = precharged();
    for (const double phase : std::array<double, 8>{
            -std::numeric_limits<double>::denorm_min(), -1.0, 1.0,
            std::nextafter(1.0, 2.0), 2.0, nan, infinity, -infinity}) {
        auto destination = sentinel_frame();
        const auto before = destination;
        auto selection = destination.selection;
        CHECK(ScannerRotor::select(phase, ScannerMode::C3, selection) == Status::InvalidSpec);
        CHECK(selection == before.selection);
        CHECK(ScannerRotor::evaluate(phase, valid, ScannerMode::C3, destination) == Status::InvalidSpec);
        CHECK(destination == before);
        rejected(prepared, Status::InvalidProfile, [phase](ScannerRotor& rotor, ScannerRotorFrame&) {
            return rotor.restore_state(ScannerRotorState{phase, 100});
        });
    }
    for (const double rate : std::array<double, 9>{
            0.0, -48000.0, 44101.0, 192001.0, std::nextafter(48000.0, 0.0),
            1536001.0, nan, infinity, -infinity}) {
        rejected(prepared, Status::InvalidSpec, [rate](ScannerRotor& rotor, ScannerRotorFrame&) {
            return rotor.prepare(rate);
        });
        rejected(prepared, Status::InvalidSpec, [rate](ScannerRotor& rotor, ScannerRotorFrame&) {
            return rotor.reconfigure_sample_rate(rate);
        });
    }
    for (unsigned value = 6; value <= 255; ++value) {
        const auto mode = static_cast<ScannerMode>(value);
        auto destination = sentinel_frame();
        const auto before = destination;
        auto selection = destination.selection;
        CHECK(ScannerRotor::select(0.25, mode, selection) == Status::InvalidEvent);
        CHECK(selection == before.selection);
        CHECK(ScannerRotor::evaluate(0.25, valid, mode, destination) == Status::InvalidEvent);
        CHECK(destination == before);
        rejected(prepared, Status::InvalidEvent, [&](ScannerRotor& rotor, ScannerRotorFrame& frame) {
            return rotor.observe(valid, mode, frame);
        });
        rejected(prepared, Status::InvalidEvent, [&](ScannerRotor& rotor, ScannerRotorFrame& frame) {
            return rotor.process_frame(valid, mode, frame);
        });
    }
    for (std::size_t tap = 0; tap < 19; ++tap) {
        for (const double invalid : std::array<double, 5>{
                nan, infinity, -infinity, std::nextafter(kTapLimit, infinity),
                std::nextafter(-kTapLimit, -infinity)}) {
            auto taps = valid;
            taps[tap] = invalid;
            auto destination = sentinel_frame();
            const auto before = destination;
            CHECK(ScannerRotor::evaluate(0.0, taps, ScannerMode::V1, destination) == Status::InvalidBuffer);
            CHECK(destination == before);
            rejected(prepared, Status::InvalidBuffer, [&](ScannerRotor& rotor, ScannerRotorFrame& frame) {
                return rotor.observe(taps, ScannerMode::V1, frame);
            });
            rejected(prepared, Status::InvalidBuffer, [&](ScannerRotor& rotor, ScannerRotorFrame& frame) {
                return rotor.process_frame(taps, ScannerMode::V1, frame);
            });
        }
    }
    // Contract precedence is explicit even when several arguments are invalid.
    auto destination = sentinel_frame();
    const auto before = destination;
    auto bad_taps = valid;
    bad_taps[0] = nan;
    CHECK(ScannerRotor::evaluate(nan, bad_taps, static_cast<ScannerMode>(255), destination)
          == Status::InvalidEvent);
    CHECK(ScannerRotor::evaluate(nan, bad_taps, ScannerMode::V1, destination) == Status::InvalidSpec);
    CHECK(destination == before);

    ScannerRotor cold;
    CHECK(!cold.prepared());
    CHECK(cold.sample_rate() == 0.0);
    CHECK(cold.state() == ScannerRotorState{});
    CHECK(cold.phase_increment_turns() == 0.0);
    CHECK(cold.observe(bad_taps, static_cast<ScannerMode>(255), destination) == Status::NotPrepared);
    CHECK(cold.process_frame(bad_taps, static_cast<ScannerMode>(255), destination) == Status::NotPrepared);
    CHECK(cold.restore_state(ScannerRotorState{nan, 9}) == Status::NotPrepared);
    CHECK(cold.reconfigure_sample_rate(nan) == Status::NotPrepared);
    CHECK(cold.prepare(nan) == Status::InvalidSpec);
    CHECK(!cold.prepared());
    CHECK(cold.sample_rate() == 0.0);
    CHECK(cold.state() == ScannerRotorState{});
    CHECK(destination == before);
}

void clock_and_lifecycle() {
    for (const double host : kHostRates) {
        for (const double factor : kFactors) {
            const double rate = host * factor;
            ScannerRotor rotor;
            CHECK(rotor.prepare(rate) == Status::Ok);
            CHECK(rotor.prepared());
            CHECK(rotor.sample_rate() == rate);
            CHECK(rotor.state() == ScannerRotorState{});
            const long double increment = kDocumentarySpeedHz / rate;
            CHECK_NEAR(rotor.phase_increment_turns(), increment,
                       4.0L * std::numeric_limits<double>::epsilon() * increment);
            auto quiet = rotor;
            auto discarded = rotor;
            for (std::size_t index = 0; index < 4096; ++index) {
                const auto previous = rotor.state();
                const auto taps = driven_taps(index);
                const auto mode_index = (index / 17) % 6;
                ScannerRotorFrame observation, frame, silence, ignored;
                CHECK(rotor.observe(taps, kModes[mode_index], observation) == Status::Ok);
                CHECK(rotor.state() == previous);
                CHECK(observation.frame == previous.frames);
                CHECK(observation.selection.phase_turns == previous.phase_turns);
                CHECK(rotor.process_frame(taps, kModes[mode_index], frame) == Status::Ok);
                CHECK(frame.frame == previous.frames + 1);
                CHECK(frame.selection == observation.selection);
                CHECK(frame.output_volts == observation.output_volts);
                check_selection(previous.phase_turns, mode_index, frame.selection);
                const auto expected_output = reference_output(previous.phase_turns, taps, kModeDepths[mode_index]);
                CHECK_NEAR(frame.output_volts, expected_output,
                           2.0e-12L + 2.0e-12L * std::fabs(expected_output));
                CHECK(quiet.process_frame(Taps{}, kModes[(mode_index + 3) % 6], silence) == Status::Ok);
                CHECK(silence.output_volts == 0.0);
                CHECK(discarded.process_frame(taps, ScannerMode::V3, ignored) == Status::Ok);
                CHECK(rotor.state() == quiet.state());
                CHECK(rotor.state() == discarded.state());
                const long double exact_phase = std::fmod(
                    static_cast<long double>(index + 1) * increment, 1.0L);
                const long double direct = std::fabs(rotor.state().phase_turns - exact_phase);
                const long double error = std::min(direct, 1.0L - direct);
                maximum_clock_drift = std::max(maximum_clock_drift, error);
                // Sum-of-rounding allowance, separate from the frozen direct
                // angle/electrical-output comparison budget above.
                CHECK(error <= static_cast<long double>(index + 1)
                               * 4.0L * std::numeric_limits<double>::epsilon());
                ++clock_frames;
            }
            const auto prior = rotor.state();
            for (const auto mode : kModes) {
                ScannerRotorFrame observation;
                CHECK(rotor.observe(driven_taps(3), mode, observation) == Status::Ok);
                CHECK(rotor.state() == prior);
            }
            // Cross an actual running wrap at every research rate, including
            // the highest rate whose cold 4096-frame path has not wrapped yet.
            CHECK(rotor.restore_state(ScannerRotorState{0.999, 71}) == Status::Ok);
            bool crossed_wrap = false;
            for (std::size_t index = 0; index < 1024; ++index) {
                const auto before = rotor.state();
                ScannerRotorFrame frame;
                const auto mode_index = index % 6;
                const auto taps = driven_taps(index);
                CHECK(rotor.process_frame(taps, kModes[mode_index], frame) == Status::Ok);
                CHECK(frame.selection.phase_turns == before.phase_turns);
                CHECK(frame.frame == 72 + index);
                check_selection(before.phase_turns, mode_index, frame.selection);
                const auto expected_output = reference_output(before.phase_turns, taps, kModeDepths[mode_index]);
                CHECK_NEAR(frame.output_volts, expected_output,
                           2.0e-12L + 2.0e-12L * std::fabs(expected_output));
                crossed_wrap = crossed_wrap || rotor.state().phase_turns < before.phase_turns;
                const auto exact_phase = std::fmod(static_cast<long double>(0.999)
                    + static_cast<long double>(index + 1) * increment, 1.0L);
                const auto direct = std::fabs(rotor.state().phase_turns - exact_phase);
                const auto error = std::min(direct, 1.0L - direct);
                maximum_clock_drift = std::max(maximum_clock_drift, error);
                CHECK(error <= static_cast<long double>(index + 1)
                               * 4.0L * std::numeric_limits<double>::epsilon());
                ++clock_frames;
            }
            CHECK(crossed_wrap);
            CHECK(rotor.prepare(rate) == Status::Ok);
            CHECK(rotor.state() == ScannerRotorState{});
        }
    }
    for (const double from : kHostRates) {
        for (const double to : kHostRates) {
            auto actual = precharged(from);
            const auto previous = actual.state();
            CHECK(actual.reconfigure_sample_rate(to) == Status::Ok);
            CHECK(actual.state() == previous);
            CHECK(actual.sample_rate() == to);
            ScannerRotor control;
            CHECK(control.prepare(to) == Status::Ok);
            CHECK(control.restore_state(previous) == Status::Ok);
            equal_continuation(actual, control);
            ++rate_pairs;
        }
    }
    for (const double phase : std::array<double, 4>{
            -0.0, 0.0, std::numeric_limits<double>::denorm_min(), std::nextafter(1.0, 0.0)}) {
        ScannerRotor rotor;
        CHECK(rotor.prepare(44100.0) == Status::Ok);
        CHECK(rotor.restore_state(ScannerRotorState{phase, 71}) == Status::Ok);
        CHECK(rotor.state().phase_turns == phase);
        ScannerRotorFrame frame;
        CHECK(rotor.process_frame(driven_taps(17), ScannerMode::C3, frame) == Status::Ok);
        CHECK(frame.selection.phase_turns == phase);
        CHECK(frame.frame == 72);
        CHECK(rotor.state().phase_turns >= 0.0 && rotor.state().phase_turns < 1.0);
        CHECK_NEAR(rotor.state().phase_turns,
                   std::fmod(static_cast<long double>(phase) + kDocumentarySpeedHz / 44100.0L, 1.0L),
                   4.0L * std::numeric_limits<double>::epsilon());
    }
}

void overflow_and_replay() {
    auto rotor = precharged();
    const auto maximum = std::numeric_limits<std::uint64_t>::max();
    CHECK(rotor.restore_state(ScannerRotorState{0.9375, maximum - 1}) == Status::Ok);
    ScannerRotorFrame last;
    CHECK(rotor.process_frame(driven_taps(7), ScannerMode::C3, last) == Status::Ok);
    CHECK(last.frame == maximum);
    CHECK(last.selection.phase_turns == 0.9375);
    const auto saturated = rotor.state();
    auto control = rotor;
    auto destination = sentinel_frame();
    const auto before = destination;
    CHECK(rotor.process_frame(driven_taps(8), ScannerMode::V1, destination) == Status::TimelineOverflow);
    CHECK(rotor.state() == saturated);
    CHECK(destination == before);
    CHECK(rotor.sample_rate() == control.sample_rate());
    CHECK(rotor.phase_increment_turns() == control.phase_increment_turns());
    CHECK(rotor.observe(driven_taps(8), ScannerMode::V1, destination) == Status::Ok);
    CHECK(destination.frame == maximum);
    CHECK(rotor.state() == saturated);
    CHECK(rotor.restore_state(saturated) == Status::Ok);
    // A saturated timeline cannot advance; replay the same physical phase at a
    // usable counter to verify that rejection did not corrupt future behavior.
    const ScannerRotorState replay{saturated.phase_turns, 127};
    CHECK(rotor.restore_state(replay) == Status::Ok);
    CHECK(control.restore_state(replay) == Status::Ok);
    equal_continuation(rotor, control);
}

struct Rendered {
    std::vector<ScannerRotorFrame> frames;
    ScannerRotorState final_state;
};

[[nodiscard]] Rendered grouped(double rate, const std::vector<std::size_t>& groups) {
    auto rotor = precharged(rate);
    Rendered result;
    std::size_t cursor = 0, group = 0;
    while (cursor < 4096) {
        const auto count = std::min(groups[group % groups.size()], 4096 - cursor);
        // A control-only observation has no elapsed interval. This is not a
        // host callback API; external grouping must not invent extra advances.
        const auto before = rotor.state();
        ScannerRotorFrame observation;
        CHECK(rotor.observe(driven_taps(cursor), kModes[(cursor / 17) % 6], observation) == Status::Ok);
        CHECK(rotor.state() == before);
        for (std::size_t offset = 0; offset < count; ++offset) {
            ScannerRotorFrame frame;
            const auto index = cursor + offset;
            CHECK(rotor.process_frame(index % 29 < 7 ? Taps{} : driven_taps(index),
                                      kModes[(index / 17) % 6], frame) == Status::Ok);
            result.frames.push_back(frame);
        }
        cursor += count;
        ++group;
    }
    result.final_state = rotor.state();
    return result;
}

void partition_invariance() {
    for (const double rate : kHostRates) {
        const auto expected = grouped(rate, {1});
        for (const auto& groups : std::array<std::vector<std::size_t>, 4>{
                std::vector<std::size_t>{1}, {64}, {127}, {1, 17, 64, 3, 127, 2, 31}}) {
            const auto actual = grouped(rate, groups);
            CHECK(actual.frames == expected.frames);
            CHECK(actual.final_state == expected.final_state);
            ++partition_paths;
        }
    }
}

} // namespace

int main() {
    mode_helpers();
    static_maps_and_weights();
    chorus_return_once();
    errors_and_transactions();
    clock_and_lifecycle();
    overflow_and_replay();
    partition_invariance();
    std::cout << std::setprecision(std::numeric_limits<long double>::max_digits10)
              << "scanner rotor: stateless_cases=" << stateless_cases
              << " chorus_return_cases=" << chorus_cases
              << " max_oracle_error_volts=" << maximum_oracle_error
              << " max_chorus_error_volts=" << maximum_chorus_error
              << " clock_frames=" << clock_frames
              << " max_clock_drift_turns=" << maximum_clock_drift
              << " rejected_calls=" << rejected_calls
              << " continuation_frames=" << continuation_frames
              << " rate_pairs=" << rate_pairs
              << " partition_paths=" << partition_paths << '\n';
    return 0;
}
