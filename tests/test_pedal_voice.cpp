#include "TestSupport.h"
#include "hammond/PedalVoice.h"

#include <array>
#include <bit>
#include <cfenv>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <limits>

namespace {

using hammond::PedalBusFrame;
using hammond::PedalDrawbarPositions;
using hammond::PedalVoiceFrame;
using hammond::Status;

std::size_t exact_frames = 0;
std::size_t floating_frames = 0;
std::size_t rejected_frames = 0;
long double maximum_error = 0.0L;

// Fixed before execution: a conservative 32 rounded operations across the
// production and independent reference paths, at the maximum output scale100.
// Use epsilon rather than half-epsilon so directed rounding modes are covered.
// This is an absolute arithmetic bound, never an audio/fidelity tolerance.
constexpr long double kAbsoluteTolerance =
    32.0L * static_cast<long double>(std::numeric_limits<double>::epsilon()) * 100.0L;

std::array<std::uint64_t, 3> bits(const PedalVoiceFrame& frame) {
    return {std::bit_cast<std::uint64_t>(frame.mixtures[0]),
            std::bit_cast<std::uint64_t>(frame.mixtures[1]),
            std::bit_cast<std::uint64_t>(frame.output)};
}

PedalVoiceFrame sentinel() {
    return {{std::bit_cast<double>(std::uint64_t{0x7ff8000000000137ULL}), -0.0}, 51.125};
}

// Independent integer-numerator equations, not an iteration over the exported
// production matrix or gain table. Long double improves reference resolution
// where available; the fixed bound also supports ABIs where it equals double.
std::array<long double, 3> reference(const PedalBusFrame& bus,
                                    const PedalDrawbarPositions& positions) {
    const long double brown = static_cast<long double>(bus[0]);
    const long double red = static_cast<long double>(bus[1]);
    const long double orange = static_cast<long double>(bus[2]);
    const long double yellow = static_cast<long double>(bus[3]);
    const long double first = (4.0L * brown + 2.0L * red + orange + yellow) / 8.0L;
    const long double second = (brown + 4.0L * red + 2.0L * orange + yellow) / 8.0L;
    const long double output =
        (static_cast<long double>(positions[0]) * first +
         static_cast<long double>(positions[1]) * second) / 8.0L;
    return {first, second, output};
}

void checked_frame(const PedalBusFrame& buses, const PedalDrawbarPositions& positions,
                   bool exact) {
    auto actual = sentinel();
    CHECK(hammond::render_nominal_pedal_voice(buses, positions, actual) == Status::Ok);
    const auto expected = reference(buses, positions);
    const std::array<double, 3> values{actual.mixtures[0], actual.mixtures[1], actual.output};
    for (std::size_t i = 0; i < values.size(); ++i) {
        CHECK(std::isfinite(values[i]));
        const long double difference = std::fabs(static_cast<long double>(values[i]) - expected[i]);
        if (difference > maximum_error) maximum_error = difference;
        if (exact) {
            CHECK(static_cast<long double>(values[i]) == expected[i]);
        } else {
            CHECK_NEAR(values[i], expected[i], kAbsoluteTolerance);
        }
    }
    CHECK(std::fabs(actual.mixtures[0]) <= 50.0);
    CHECK(std::fabs(actual.mixtures[1]) <= 50.0);
    CHECK(std::fabs(actual.output) <= 100.0);
    if (positions == PedalDrawbarPositions{0, 0}) {
        CHECK(std::bit_cast<std::uint64_t>(actual.output) == 0);
    }
    if (exact) ++exact_frames;
    else ++floating_frames;
}

void all_positions(const PedalBusFrame& buses, bool exact) {
    for (std::uint8_t first = 0; first <= 8; ++first) {
        for (std::uint8_t second = 0; second <= 8; ++second) {
            checked_frame(buses, {first, second}, exact);
        }
    }
}

void test_metadata_and_weights() {
    CHECK(hammond::kNominalPedalVoiceModelId == "nominal-static-pedal-mixture-v1");
    CHECK(hammond::kNominalPedalGainLawId == "linear-pedal-position-v1");
    CHECK(hammond::kNominalPedalMixtureLabels[0] == "Pedal Mixture 1");
    CHECK(hammond::kNominalPedalMixtureLabels[1] == "Pedal Mixture 2");
    CHECK(hammond::kNominalPedalBusInputLimit == 50.0);
    CHECK(hammond::kNominalPedalMixtureOutputLimit == 50.0);
    CHECK(hammond::kNominalPedalOutputLimit == 100.0);
    const hammond::PedalMixtureMatrix expected{{
        {{0.5, 0.25, 0.125, 0.125}}, {{0.125, 0.5, 0.25, 0.125}}}};
    CHECK(hammond::kNominalPedalMixtureMatrix == expected);
    for (std::size_t i = 0; i < hammond::kPedalDrawbarPositionCount; ++i) {
        CHECK(hammond::kNominalPedalPositionGains[i] == static_cast<double>(i) / 8.0);
    }
    constexpr auto weights = hammond::nominal_pedal_reference_weights();
    static_assert(weights.size() == 200 && weights[0] == 1.0 && weights[199] == 1.0);
    for (const double weight : weights) CHECK(weight == 1.0);
    auto changed_copy = weights;
    changed_copy[0] = -1.0;
    CHECK(hammond::nominal_pedal_reference_weights()[0] == 1.0);
    CHECK(changed_copy[0] == -1.0);
    CHECK(hammond::is_valid_pedal_drawbar_positions({0, 8}));
    CHECK(!hammond::is_valid_pedal_drawbar_positions({0, 9}));
}

void test_exact_basis_and_corners() {
    for (std::size_t bus = 0; bus < 4; ++bus) {
        for (const double level : {-50.0, -1.0, 0.0, 1.0, 50.0}) {
            PedalBusFrame frame{};
            frame[bus] = level;
            all_positions(frame, true);
        }
    }
    for (unsigned mask = 0; mask < 16; ++mask) {
        PedalBusFrame frame{};
        for (std::size_t bus = 0; bus < 4; ++bus) {
            frame[bus] = (mask & (1U << bus)) == 0 ? -50.0 : 50.0;
        }
        all_positions(frame, true);
    }
    for (const PedalBusFrame& frame : std::array<PedalBusFrame, 4>{{
             {{32.0, -16.0, 8.0, -4.0}}, {{-0.0, 0.0, -0.0, 0.0}},
             {{0.125, -0.25, 0.5, -1.0}}, {{1.5, -2.75, 3.125, -4.5}}}}) {
        all_positions(frame, true);
    }
    PedalVoiceFrame actual;
    CHECK(hammond::render_nominal_pedal_voice({50, 50, 50, 50}, {8, 8}, actual) == Status::Ok);
    CHECK(actual.output == 100.0); // No hidden limiter or polyphony normalization.
    CHECK(hammond::render_nominal_pedal_voice({32, -16, 8, -4}, {0, 0}, actual) == Status::Ok);
    CHECK(actual.mixtures[0] == 12.5 && actual.mixtures[1] == -2.5);
    CHECK(actual.output == 0.0); // Diagnostic mixtures remain visible while muted.
}

void rejected(const PedalBusFrame& buses, const PedalDrawbarPositions& positions,
              Status expected) {
    auto destination = sentinel();
    const auto before = bits(destination);
    CHECK(hammond::render_nominal_pedal_voice(buses, positions, destination) == expected);
    CHECK(bits(destination) == before);
    ++rejected_frames;
}

void test_rejection_atomicity() {
    const std::array<double, 7> invalid{
        std::numeric_limits<double>::quiet_NaN(),
        std::numeric_limits<double>::infinity(),
        -std::numeric_limits<double>::infinity(),
        std::nextafter(50.0, std::numeric_limits<double>::infinity()),
        std::nextafter(-50.0, -std::numeric_limits<double>::infinity()),
        std::numeric_limits<double>::max(), -std::numeric_limits<double>::max()};
    for (std::size_t bus = 0; bus < 4; ++bus) {
        for (const double value : invalid) {
            PedalBusFrame frame{4, 3, 2, 1};
            frame[bus] = value;
            rejected(frame, {0, 0}, Status::InvalidBuffer);
            rejected(frame, {8, 8}, Status::InvalidBuffer);
            rejected(frame, {9, 255}, Status::InvalidBuffer); // Bus errors precede controls.
        }
    }
    for (std::size_t drawbar = 0; drawbar < 2; ++drawbar) {
        for (std::uint16_t invalid_position = 9; invalid_position <= 255; ++invalid_position) {
            PedalDrawbarPositions positions{4, 7};
            positions[drawbar] = static_cast<std::uint8_t>(invalid_position);
            CHECK(!hammond::is_valid_pedal_drawbar_positions(positions));
            rejected({4, 3, 2, 1}, positions, Status::InvalidEvent);
            rejected({}, positions, Status::InvalidEvent);
        }
    }
}

void test_rounding_and_finite_bounds() {
    std::array<PedalBusFrame, 257> frames{};
    for (std::size_t i = 0; i < frames.size(); ++i) {
        for (std::size_t bus = 0; bus < 4; ++bus) {
            const auto integer = static_cast<std::int64_t>((i * 131 + bus * 977) % 10001) - 5000;
            frames[i][bus] = static_cast<double>(integer) / 101.0;
        }
    }
    frames[0] = {50.0, 50.0, 50.0, 50.0};
    frames[1] = {-50.0, -50.0, -50.0, -50.0};
    const double inside = std::nextafter(50.0, 0.0);
    frames[2] = {inside, -inside, inside, -inside};
    const double tiny = std::numeric_limits<double>::denorm_min();
    frames[3] = {tiny, -tiny, tiny, tiny};
    frames[4] = {-0.0, 0.0, -0.0, 0.0};

    const int original = std::fegetround();
    CHECK(original != -1);
    for (const int mode : {FE_TONEAREST, FE_DOWNWARD, FE_UPWARD, FE_TOWARDZERO}) {
        CHECK(std::fesetround(mode) == 0);
        for (const auto& frame : frames) all_positions(frame, false);
        CHECK(std::fegetround() == mode);
    }
    CHECK(std::fesetround(original) == 0);
}

void test_stateless_repeatability() {
    PedalVoiceFrame first;
    PedalVoiceFrame unrelated;
    PedalVoiceFrame repeated;
    CHECK(hammond::render_nominal_pedal_voice({2.5, -4.5, 3, -7}, {7, 2}, first) == Status::Ok);
    CHECK(hammond::render_nominal_pedal_voice({50, 50, 50, 50}, {8, 8}, unrelated) == Status::Ok);
    rejected({0, 0, 51, 0}, {1, 1}, Status::InvalidBuffer);
    CHECK(hammond::render_nominal_pedal_voice({2.5, -4.5, 3, -7}, {7, 2}, repeated) == Status::Ok);
    CHECK(bits(first) == bits(repeated));
    CHECK(unrelated.output == 100.0);
}

} // namespace

int main() {
    test_metadata_and_weights();
    test_exact_basis_and_corners();
    test_rejection_atomicity();
    test_rounding_and_finite_bounds();
    test_stateless_repeatability();
    std::cout << "pedal_voice_groups=5 exact_frames=" << exact_frames
              << " floating_frames=" << floating_frames
              << " rejected_frames=" << rejected_frames
              << std::setprecision(std::numeric_limits<long double>::max_digits10)
              << " maximum_error=" << maximum_error
              << " absolute_tolerance=" << kAbsoluteTolerance << '\n';
    return EXIT_SUCCESS;
}
