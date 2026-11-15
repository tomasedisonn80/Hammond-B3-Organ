#include "TestSupport.h"
#include "hammond/LeslieCrossover.h"

#include <algorithm>
#include <array>
#include <bit>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <iomanip>
#include <limits>
#include <span>

namespace {
using namespace hammond;
constexpr std::array<double, 4> rates{44100.0, 48000.0, 96000.0, 192000.0};
constexpr std::array<LeslieCrossoverLoads, 7> loads{{
    {1.0, 1.0}, {1.0, 1024.0}, {1024.0, 1.0}, {1024.0, 1024.0},
    {16.0, 16.0}, {8.0, 32.0}, {23.75, 57.125}}};
constexpr auto maximum_frame = std::numeric_limits<std::uint64_t>::max();
constexpr double infinity = std::numeric_limits<double>::infinity();
constexpr LeslieCrossoverState precharge{{12.25, -7.75}, {0.2, -0.12}, -31.25, 123};
std::size_t intervals{}, transitions{}, rejected{}, boundary_states{}, alias_cases{};
long double maximum_kcl{}, maximum_energy{}, maximum_port{};

bool identical(double left, double right) {
    return std::bit_cast<std::uint64_t>(left) == std::bit_cast<std::uint64_t>(right);
}
bool identical(const LeslieCrossoverState& left, const LeslieCrossoverState& right) {
    for (std::size_t index = 0; index < 2; ++index) {
        if (!identical(left.capacitor_volts[index], right.capacitor_volts[index]) ||
            !identical(left.inductor_amps[index], right.inductor_amps[index])) return false;
    }
    return identical(left.previous_input_volts, right.previous_input_volts) && left.frames == right.frames;
}
bool identical(const LeslieCrossoverFrame& left, const LeslieCrossoverFrame& right) {
    return identical(left.treble_volts, right.treble_volts) && identical(left.bass_volts, right.bass_volts) &&
        identical(left.treble_current_amps, right.treble_current_amps) &&
        identical(left.bass_current_amps, right.bass_current_amps) &&
        identical(left.input_current_amps, right.input_current_amps) &&
        identical(left.energy_joules, right.energy_joules) && left.frame == right.frame;
}
LeslieCrossoverFrame sentinel() {
    return {std::bit_cast<double>(UINT64_C(0x7ff8deadbeef0042)), -0.0, -73.0, 29.0, -11.0, 4.0, 777};
}
void near(long double actual, long double expected, long double tolerance, long double& maximum) {
    const auto error = std::abs(actual - expected) / std::max(1.0L, std::abs(expected));
    CHECK(std::isfinite(error));
    maximum = std::max(maximum, error);
    CHECK(error <= tolerance);
}

// Independently evaluate SI charge, flux and stored energy from exposed physical
// coordinates. This oracle neither constructs F/G nor trusts native port/energy
// values to validate its own power identity.
long double energy(const LeslieCrossoverState& state) {
    const long double vh = state.capacitor_volts[0], vw = state.capacitor_volts[1];
    const long double il2 = state.inductor_amps[0], il3 = state.inductor_amps[1];
    return (7.8e-6L * vh * vh + 12.5e-6L * vw * vw + 3.2e-3L * il2 * il2 + 5.2e-3L * il3 * il3) / 2;
}
void ports(const LeslieCrossoverState& state, LeslieCrossoverLoads load, const LeslieCrossoverFrame& frame) {
    const long double treble = static_cast<long double>(state.previous_input_volts) - state.capacitor_volts[0];
    const long double bass = state.capacitor_volts[1];
    const long double it = treble / load.treble_ohms, iw = bass / load.bass_ohms;
    near(frame.treble_volts, treble, 4e-13L, maximum_port);
    near(frame.bass_volts, bass, 4e-13L, maximum_port);
    near(frame.treble_current_amps, it, 4e-13L, maximum_port);
    near(frame.bass_current_amps, iw, 4e-13L, maximum_port);
    near(frame.input_current_amps, state.inductor_amps[0] + it + state.inductor_amps[1], 4e-13L, maximum_port);
    near(frame.energy_joules, energy(state), 4e-13L, maximum_port);
    CHECK(frame.frame == state.frames);
}
void physical_interval(const LeslieCrossoverState& before, const LeslieCrossoverState& after,
                       double rate, LeslieCrossoverLoads load, const LeslieCrossoverFrame& frame) {
    const long double h = 1.0L / rate;
    const long double u = (static_cast<long double>(before.previous_input_volts) + after.previous_input_volts) / 2;
    const long double vh = (static_cast<long double>(before.capacitor_volts[0]) + after.capacitor_volts[0]) / 2;
    const long double vw = (static_cast<long double>(before.capacitor_volts[1]) + after.capacitor_volts[1]) / 2;
    const long double il2 = (static_cast<long double>(before.inductor_amps[0]) + after.inductor_amps[0]) / 2;
    const long double il3 = (static_cast<long double>(before.inductor_amps[1]) + after.inductor_amps[1]) / 2;
    const long double it = (u - vh) / load.treble_ohms, iw = vw / load.bass_ohms;
    near(7.8e-6L * (static_cast<long double>(after.capacitor_volts[0]) - before.capacitor_volts[0]),
         h * (il2 + it), 4e-12L, maximum_kcl);
    near(12.5e-6L * (static_cast<long double>(after.capacitor_volts[1]) - before.capacitor_volts[1]),
         h * (il3 - iw), 4e-12L, maximum_kcl);
    near(3.2e-3L * (static_cast<long double>(after.inductor_amps[0]) - before.inductor_amps[0]),
         h * (u - vh), 4e-12L, maximum_kcl);
    near(5.2e-3L * (static_cast<long double>(after.inductor_amps[1]) - before.inductor_amps[1]),
         h * (u - vw), 4e-12L, maximum_kcl);
    const long double source_work = h * u * (il2 + it + il3);
    const long double load_work = h * ((u - vh) * it + vw * iw);
    const long double e0 = energy(before), e1 = energy(after);
    const auto error = std::abs(e1 - e0 - source_work + load_work) /
        std::max({1.0L, std::abs(e0), std::abs(e1), std::abs(source_work)});
    maximum_energy = std::max(maximum_energy, error);
    CHECK(error <= 2e-11L);
    ports(after, load, frame);
    CHECK(after.frames == before.frames + 1);
    ++intervals;
}

void same_public_state(const LeslieCrossover& actual, const LeslieCrossover& expected) {
    CHECK(actual.prepared() == expected.prepared());
    CHECK(identical(actual.sample_rate(), expected.sample_rate()));
    CHECK(actual.loads() == expected.loads());
    CHECK(identical(actual.preparation_residual(), expected.preparation_residual()));
    CHECK(identical(actual.state(), expected.state()));
}
void continued_twins(LeslieCrossover actual, LeslieCrossover untouched) {
    same_public_state(actual, untouched);
    for (std::size_t index = 0; index < 31; ++index) {
        const double input = static_cast<double>((index * 19) % 41) - 20.0;
        LeslieCrossoverFrame observed, expected;
        CHECK(actual.process_frame(input, observed) == Status::Ok);
        CHECK(untouched.process_frame(input, expected) == Status::Ok);
        CHECK(identical(observed, expected));
        same_public_state(actual, untouched);
    }
}

void rate_changes_and_physical_laws() {
    std::array<double, 257> inputs{};
    for (std::size_t index = 0; index < inputs.size(); ++index)
        inputs[index] = static_cast<double>((index * 29) % 127) - 63.0;
    inputs[0] = 64.0;
    inputs[1] = -64.0;
    for (const auto load : loads) for (const auto from : rates) for (const auto to : rates) {
        LeslieCrossover subject;
        CHECK(subject.prepare(from, load) == Status::Ok);
        CHECK(subject.restore_state(precharge) == Status::Ok);
        for (std::size_t index = 0; index < 13; ++index) {
            const auto before = subject.state();
            LeslieCrossoverFrame frame;
            CHECK(subject.process_frame(inputs[index], frame) == Status::Ok);
            physical_interval(before, subject.state(), from, load, frame);
        }
        const auto checkpoint = subject.state();
        CHECK(checkpoint.previous_input_volts != 0.0);
        LeslieCrossoverFrame old_endpoint, new_endpoint;
        CHECK(subject.observe(old_endpoint) == Status::Ok);
        CHECK(subject.reconfigure_sample_rate(to) == Status::Ok);
        CHECK(identical(subject.state(), checkpoint));
        CHECK(subject.loads() == load);
        CHECK(subject.sample_rate() == to);
        CHECK(subject.observe(new_endpoint) == Status::Ok);
        CHECK(identical(old_endpoint, new_endpoint));

        LeslieCrossover fresh;
        CHECK(fresh.prepare(to, load) == Status::Ok);
        CHECK(fresh.restore_state(checkpoint) == Status::Ok);
        auto block = subject, partitioned = subject;
        std::array<LeslieCrossoverFrame, 257> scalar_frames{}, block_frames{}, partition_frames{};
        for (std::size_t index = 0; index < inputs.size(); ++index) {
            const auto before = subject.state();
            CHECK(subject.process_frame(inputs[index], scalar_frames[index]) == Status::Ok);
            physical_interval(before, subject.state(), to, load, scalar_frames[index]);
            LeslieCrossoverFrame fresh_frame;
            CHECK(fresh.process_frame(inputs[index], fresh_frame) == Status::Ok);
            CHECK(identical(fresh_frame, scalar_frames[index]));
        }
        CHECK(block.process(inputs, block_frames) == Status::Ok);
        std::size_t offset = 0;
        for (const auto size : std::array<std::size_t, 7>{1, 2, 17, 64, 3, 129, 41}) {
            CHECK(partitioned.process(std::span{inputs}.subspan(offset, size),
                                      std::span{partition_frames}.subspan(offset, size)) == Status::Ok);
            const auto point = partitioned.state();
            CHECK(partitioned.process({}, {}) == Status::Ok);
            CHECK(identical(point, partitioned.state()));
            offset += size;
        }
        CHECK(offset == inputs.size());
        for (std::size_t index = 0; index < inputs.size(); ++index) {
            CHECK(identical(scalar_frames[index], block_frames[index]));
            CHECK(identical(scalar_frames[index], partition_frames[index]));
        }
        same_public_state(subject, block);
        same_public_state(subject, partitioned);
        same_public_state(subject, fresh);
        ++transitions;
    }
}

void boundary_admission_and_recovery() {
    LeslieCrossover subject;
    CHECK(subject.prepare(96000.0, {1024.0, 1.0}) == Status::Ok);
    CHECK(subject.restore_state(precharge) == Status::Ok);
    const auto intact = subject;
    for (const double rate : rates) for (const double direction : {-infinity, infinity}) {
        CHECK(subject.reconfigure_sample_rate(std::nextafter(rate, direction)) == Status::InvalidSpec);
        continued_twins(subject, intact);
        ++rejected;
    }
    for (const double bad_load : {std::nextafter(1.0, 0.0), std::nextafter(1024.0, infinity)}) {
        CHECK(subject.prepare(44100.0, {bad_load, 16.0}) == Status::InvalidSpec);
        continued_twins(subject, intact);
        CHECK(subject.prepare(192000.0, {16.0, bad_load}) == Status::InvalidSpec);
        continued_twins(subject, intact);
        rejected += 2;
    }
    for (std::size_t coordinate = 0; coordinate < 5; ++coordinate) for (const double sign : {-1.0, 1.0}) {
        auto edge = precharge;
        double* field = coordinate < 2 ? &edge.capacitor_volts[coordinate]
            : coordinate < 4 ? &edge.inductor_amps[coordinate - 2] : &edge.previous_input_volts;
        const double limit = coordinate < 2 ? 65536.0 : coordinate < 4 ? 256.0 : 64.0;
        *field = sign * limit;
        CHECK(subject.restore_state(edge) == Status::Ok);
        CHECK(identical(subject.state(), edge));
        LeslieCrossoverFrame frame;
        CHECK(subject.observe(frame) == Status::Ok);
        ports(edge, subject.loads(), frame);
        ++boundary_states;
        CHECK(subject.restore_state(precharge) == Status::Ok);
        *field = std::nextafter(*field, sign * infinity);
        CHECK(subject.restore_state(edge) == Status::InvalidProfile);
        continued_twins(subject, intact);
        ++rejected;
    }
    for (const double sign : {-1.0, 1.0}) {
        auto destination = sentinel();
        CHECK(subject.process_frame(std::nextafter(sign * 64.0, sign * infinity), destination) == Status::InvalidBuffer);
        CHECK(identical(destination, sentinel()));
        continued_twins(subject, intact);
        ++rejected;
    }
    // A last-element failure must also retain NaN payloads and signed zeros in
    // caller storage, not merely values comparable with operator==.
    std::array<double, 257> samples{};
    std::array<LeslieCrossoverFrame, 257> destination{};
    destination.fill(sentinel());
    samples.back() = std::nextafter(64.0, infinity);
    CHECK(subject.process(samples, destination) == Status::InvalidBuffer);
    for (const auto& frame : destination) CHECK(identical(frame, sentinel()));
    continued_twins(subject, intact);
    ++rejected;

    for (const auto load : loads) for (const auto rate : rates) {
        CHECK(subject.prepare(rate, load) == Status::Ok);
        CHECK(subject.restore_state(precharge) == Status::Ok);
        const auto before = subject;
        for (const double frequency : {0.0, std::numeric_limits<double>::denorm_min(),
                                      std::nextafter(rate / 2.0, 0.0)}) {
            LeslieCrossoverResponse response;
            CHECK(subject.response(frequency, response) == Status::Ok);
            CHECK(std::isfinite(std::abs(response.treble_gain)));
            CHECK(std::isfinite(std::abs(response.bass_gain)));
            CHECK(std::isfinite(std::abs(response.input_admittance)));
            CHECK(std::isfinite(response.normalized_residual));
            same_public_state(subject, before);
        }
        LeslieCrossoverResponse response{{-0.0, 3.0}, {4.0, 5.0}, {6.0, 7.0}, 8.0};
        const auto saved = response;
        CHECK(subject.response(rate / 2.0, response) == Status::InvalidSpec);
        CHECK(response == saved);
        CHECK(identical(response.treble_gain.real(), saved.treble_gain.real()));
        continued_twins(subject, before);
        ++rejected;
    }
}

void overlap_and_counter_edges() {
    LeslieCrossover subject;
    CHECK(subject.prepare(48000.0, {1.0, 1024.0}) == Status::Ok);
    CHECK(subject.restore_state(precharge) == Status::Ok);
    const auto intact = subject;
    for (std::size_t member = 0; member < 6; ++member) {
        auto frame = sentinel();
        const std::array<const double*, 6> fields{&frame.treble_volts, &frame.bass_volts,
            &frame.treble_current_amps, &frame.bass_current_amps, &frame.input_current_amps, &frame.energy_joules};
        CHECK(subject.process(std::span<const double>{fields[member], 1},
                              std::span<LeslieCrossoverFrame>{&frame, 1}) == Status::InvalidBuffer);
        CHECK(identical(frame, sentinel()));
        continued_twins(subject, intact);
        ++alias_cases;
    }
    // The legal disjoint spans touch at an exact byte boundary in both orders.
    struct InputFirst { double input; LeslieCrossoverFrame output; } input_first{7.25, sentinel()};
    struct OutputFirst { LeslieCrossoverFrame output; double input; } output_first{sentinel(), 7.25};
    static_assert(offsetof(InputFirst, output) == sizeof(double));
    static_assert(offsetof(OutputFirst, input) == sizeof(LeslieCrossoverFrame));
    auto twin = subject;
    LeslieCrossoverFrame expected;
    CHECK(twin.process_frame(7.25, expected) == Status::Ok);
    CHECK(subject.process(std::span<const double>{&input_first.input, 1},
                          std::span<LeslieCrossoverFrame>{&input_first.output, 1}) == Status::Ok);
    CHECK(identical(input_first.output, expected));
    CHECK(input_first.input == 7.25);
    subject = intact;
    CHECK(subject.process(std::span<const double>{&output_first.input, 1},
                          std::span<LeslieCrossoverFrame>{&output_first.output, 1}) == Status::Ok);
    CHECK(identical(output_first.output, expected));
    CHECK(output_first.input == 7.25);

    auto last = precharge;
    last.frames = maximum_frame - 256;
    CHECK(subject.restore_state(last) == Status::Ok);
    std::array<double, 257> samples{};
    std::array<LeslieCrossoverFrame, 257> output{};
    output.fill(sentinel());
    samples.back() = infinity;
    CHECK(subject.process(samples, output) == Status::TimelineOverflow);
    CHECK(identical(subject.state(), last));
    for (const auto& frame : output) CHECK(identical(frame, sentinel()));
    auto scalar = subject;
    CHECK(subject.process(std::span{samples}.first(256), std::span{output}.first(256)) == Status::Ok);
    for (std::size_t index = 0; index < 256; ++index) {
        LeslieCrossoverFrame frame;
        CHECK(scalar.process_frame(0.0, frame) == Status::Ok);
        CHECK(identical(frame, output[index]));
    }
    CHECK(subject.state().frames == maximum_frame);
    same_public_state(subject, scalar);
    CHECK(identical(output.back(), sentinel()));
    CHECK(subject.process({}, {}) == Status::Ok);
    same_public_state(subject, scalar);
    CHECK(subject.restore_state(precharge) == Status::Ok);
    continued_twins(subject, intact);
}
} // namespace

int main() {
    rate_changes_and_physical_laws();
    boundary_admission_and_recovery();
    overlap_and_counter_edges();
    std::cout << std::setprecision(17) << "Independent crossover lifecycle passed: rate_load_transitions=" << transitions
              << " physical_intervals=" << intervals << " rejected_transactions=" << rejected
              << " exact_boundary_checkpoints=" << boundary_states << " overlapping_members=" << alias_cases
              << " max_integral_KCL_or_flux_error=" << maximum_kcl
              << " max_midpoint_energy_error=" << maximum_energy
              << " max_independent_port_error=" << maximum_port << '\n';
}
