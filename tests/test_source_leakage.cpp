#include "TestSupport.h"
#include "hammond/SourceLeakage.h"

#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <limits>
#include <span>
#include <string_view>

namespace {

using hammond::SourceLeakage;
using hammond::SourceLeakageEdge;
using hammond::SourceLeakageFrame;
using hammond::SourceLeakageProfile;
using hammond::Status;

void check_frame_bits(const SourceLeakageFrame& actual,
                      const SourceLeakageFrame& expected) {
    for (std::size_t i = 0; i < actual.size(); ++i) {
        CHECK(std::bit_cast<std::uint64_t>(actual[i]) ==
              std::bit_cast<std::uint64_t>(expected[i]));
    }
}

SourceLeakageProfile synthetic_profile() {
    SourceLeakageProfile profile;
    constexpr std::string_view id = "synthetic-authored-test-v1";
    std::copy(id.begin(), id.end(), profile.profile_id.begin());
    std::fill_n(profile.authoring_sha256.begin(),
                hammond::kSourceLeakageSha256HexLength, 'a');
    return profile;
}

void check_unprepared_and_identity() {
    SourceLeakage leakage;
    CHECK(!leakage.prepared());
    CHECK(leakage.edge_count() == 0);
    CHECK(leakage.max_row_absolute_gain_sum() == 0.0);
    double sum = 123.0;
    CHECK(!leakage.row_absolute_gain_sum(1, sum));
    CHECK(sum == 123.0);

    SourceLeakageFrame input{};
    for (std::size_t i = 0; i < input.size(); ++i) {
        input[i] = static_cast<double>(i % 17) / 8.0 - 1.0;
    }
    input[3] = -0.0;
    input[90] = std::numeric_limits<double>::denorm_min();
    SourceLeakageFrame output;
    output.fill(17.0);
    const auto sentinel = output;
    CHECK(leakage.process_frame(input, output) == Status::NotPrepared);
    check_frame_bits(output, sentinel);
    auto invalid = input;
    invalid[90] = std::numeric_limits<double>::quiet_NaN();
    CHECK(leakage.process_frame(invalid, output) == Status::NotPrepared);
    check_frame_bits(output, sentinel);

    CHECK(leakage.prepare({}) == Status::Ok);
    CHECK(leakage.prepared());
    CHECK(leakage.edge_count() == 0);
    CHECK(leakage.row_absolute_gain_sum(91, sum));
    CHECK(sum == 0.0);
    sum = 123.0;
    CHECK(!leakage.row_absolute_gain_sum(0, sum));
    CHECK(!leakage.row_absolute_gain_sum(92, sum));
    CHECK(sum == 123.0);
    CHECK(leakage.process_frame(input, output) == Status::Ok);
    check_frame_bits(output, input);
    auto alias = input;
    CHECK(leakage.process_frame(alias, alias) == Status::Ok);
    check_frame_bits(alias, input);
}

void check_one_edge_and_original_frame_chain() {
    SourceLeakage leakage;
    std::array one_edge{SourceLeakageEdge{37, 25, -0.125}};
    CHECK(leakage.prepare(one_edge) == Status::Ok);
    SourceLeakageFrame input{};
    input[24] = 0.25;
    input[36] = 0.5;
    input[90] = -0.0;
    auto expected = input;
    expected[24] = 0.1875;
    SourceLeakageFrame output{};
    CHECK(leakage.process_frame(input, output) == Status::Ok);
    check_frame_bits(output, expected);

    const SourceLeakage copied = leakage;
    one_edge[0].gain = 0.25; // Prepared objects retain no authoring pointers.
    CHECK(copied.process_frame(input, output) == Status::Ok);
    check_frame_bits(output, expected);
    CHECK(leakage.process_frame(input, output) == Status::Ok);
    check_frame_bits(output, expected);

    // Shuffled 1 -> 2 -> 3 -> 1 cycle. Every donor is the original input;
    // cascading a modified destination would add an unintended C*C term.
    const std::array cycle{SourceLeakageEdge{2, 3, -0.25},
                           SourceLeakageEdge{3, 1, -0.125},
                           SourceLeakageEdge{1, 2, 0.25}};
    CHECK(leakage.prepare(cycle) == Status::Ok);
    input.fill(0.0);
    input[0] = 0.5;
    input[1] = 0.25;
    input[2] = -0.5;
    input[90] = -0.0;
    expected = input;
    expected[0] = 0.5625;
    expected[1] = 0.375;
    expected[2] = -0.5625;
    CHECK(leakage.process_frame(input, output) == Status::Ok);
    check_frame_bits(output, expected);
    auto alias = input;
    CHECK(leakage.process_frame(alias, alias) == Status::Ok);
    check_frame_bits(alias, expected);
}

void check_rejections_preserve_state_and_output() {
    SourceLeakage leakage;
    const std::array admitted{SourceLeakageEdge{1, 2, 0.125}};
    CHECK(leakage.prepare(admitted) == Status::Ok);
    SourceLeakageFrame input{};
    input[0] = 0.5;
    SourceLeakageFrame expected{};
    expected[0] = 0.5;
    expected[1] = 0.0625;
    const auto reject = [&](std::span<const SourceLeakageEdge> edges) {
        CHECK(leakage.prepare(edges) == Status::InvalidProfile);
        CHECK(leakage.prepared());
        CHECK(leakage.edge_count() == 1);
        CHECK(leakage.max_row_absolute_gain_sum() == 0.125);
        double sum = -1.0;
        CHECK(leakage.row_absolute_gain_sum(2, sum));
        CHECK(sum == 0.125);
        SourceLeakageFrame output{};
        CHECK(leakage.process_frame(input, output) == Status::Ok);
        check_frame_bits(output, expected);
    };

    const std::array invalid_edges{
        SourceLeakageEdge{1, 1, 0.125}, SourceLeakageEdge{0, 2, 0.125},
        SourceLeakageEdge{92, 2, 0.125}, SourceLeakageEdge{1, 0, 0.125},
        SourceLeakageEdge{1, 92, 0.125}, SourceLeakageEdge{1, 2, 0.0},
        SourceLeakageEdge{1, 2, -0.0},
        SourceLeakageEdge{1, 2, std::numeric_limits<double>::infinity()},
        SourceLeakageEdge{1, 2, std::numeric_limits<double>::quiet_NaN()},
        SourceLeakageEdge{1, 2, std::nextafter(0.25, 1.0)}};
    for (const auto& edge : invalid_edges) {
        const std::array single{edge};
        reject(single);
    }
    const std::array duplicates{SourceLeakageEdge{1, 2, 0.125},
                                SourceLeakageEdge{1, 2, -0.125}};
    reject(duplicates);
    const std::array excessive_sum{SourceLeakageEdge{1, 91, 0.25},
                                   SourceLeakageEdge{2, 91, 0.25},
                                   SourceLeakageEdge{3, 91, 0.125}};
    reject(excessive_sum);
    std::array<SourceLeakageEdge, 9> ninth{};
    for (std::size_t i = 0; i < ninth.size(); ++i) {
        ninth[i] = {static_cast<hammond::ToneId>(i + 1), 91, 0.03125};
    }
    reject(ninth);
    const std::array<SourceLeakageEdge, hammond::kMaxSourceLeakageEdges + 1> excess{};
    reject(excess);

    const std::array invalid_samples{
        std::numeric_limits<double>::quiet_NaN(),
        std::numeric_limits<double>::infinity(),
        std::nextafter(1.0, 2.0), std::nextafter(-1.0, -2.0)};
    for (double value : invalid_samples) {
        auto invalid = input;
        invalid[90] = value; // Validate even an entirely unused donor.
        SourceLeakageFrame output;
        output.fill(-17.0);
        const auto sentinel = output;
        CHECK(leakage.process_frame(invalid, output) == Status::InvalidBuffer);
        check_frame_bits(output, sentinel);
        const auto original = invalid;
        CHECK(leakage.process_frame(invalid, invalid) == Status::InvalidBuffer);
        check_frame_bits(invalid, original);
    }
    CHECK(leakage.prepare({}) == Status::Ok);
    CHECK(leakage.edge_count() == 0);
    CHECK(leakage.max_row_absolute_gain_sum() == 0.0);
    SourceLeakageFrame output{};
    CHECK(leakage.process_frame(input, output) == Status::Ok);
    check_frame_bits(output, input);
}

void check_canonical_sum_boundary() {
    std::array<SourceLeakageEdge, 8> admitted{};
    std::array<SourceLeakageEdge, 8> rejected{};
    for (std::size_t i = 0; i < admitted.size(); ++i) {
        admitted[i] = {static_cast<hammond::ToneId>(i + 1), 91, 0x1p-56};
        rejected[i] = admitted[i];
    }
    admitted[0].gain = 0.25;
    admitted[7].gain = 0.25;
    rejected[6].gain = 0.25;
    rejected[7].gain = 0.25;

    SourceLeakage leakage;
    CHECK(leakage.prepare(admitted) == Status::Ok);
    double sum = -1.0;
    CHECK(leakage.row_absolute_gain_sum(91, sum));
    CHECK(sum == 0.5);
    CHECK(leakage.max_row_absolute_gain_sum() == 0.5);
    SourceLeakageFrame input;
    input.fill(1.0);
    SourceLeakageFrame expected{};
    CHECK(leakage.process_frame(input, expected) == Status::Ok);
    CHECK(expected[90] == 1.5);
    std::reverse(admitted.begin(), admitted.end());
    CHECK(leakage.prepare(admitted) == Status::Ok);
    CHECK(leakage.prepare(rejected) == Status::InvalidProfile);
    std::reverse(rejected.begin(), rejected.end());
    CHECK(leakage.prepare(rejected) == Status::InvalidProfile);
    CHECK(leakage.edge_count() == 8);
    CHECK(leakage.row_absolute_gain_sum(91, sum));
    CHECK(sum == 0.5);
    SourceLeakageFrame output{};
    CHECK(leakage.process_frame(input, output) == Status::Ok);
    check_frame_bits(output, expected);

    const std::array subnormal{
        SourceLeakageEdge{1, 2, std::numeric_limits<double>::denorm_min()}};
    CHECK(leakage.prepare(subnormal) == Status::Ok);
    CHECK(leakage.row_absolute_gain_sum(2, sum));
    CHECK(sum == std::numeric_limits<double>::denorm_min());
}

void check_profile_metadata_and_order() {
    CHECK(hammond::validate_source_leakage_profile(SourceLeakageProfile{}) ==
          Status::InvalidProfile);
    auto profile = synthetic_profile();
    CHECK(hammond::validate_source_leakage_profile(profile) == Status::Ok);
    // Unused slots are not part of the graph.
    profile.edges.back() = {0, 0, std::numeric_limits<double>::quiet_NaN()};
    CHECK(hammond::validate_source_leakage_profile(profile) == Status::Ok);
    profile.edge_count = 2;
    profile.edges[0] = {37, 25, -0.125};
    profile.edges[1] = {25, 37, 0.25};
    CHECK(hammond::validate_source_leakage_profile(profile) == Status::Ok);
    auto invalid = profile;
    std::swap(invalid.edges[0], invalid.edges[1]);
    CHECK(hammond::validate_source_leakage_profile(invalid) == Status::InvalidProfile);
    invalid = profile;
    invalid.profile_id[40] = 'x'; // Nonzero padding after its terminator.
    CHECK(hammond::validate_source_leakage_profile(invalid) == Status::InvalidProfile);
    invalid = profile;
    invalid.profile_id[10] = '-'; // First suffix character must be alphanumeric.
    CHECK(hammond::validate_source_leakage_profile(invalid) == Status::InvalidProfile);
    invalid = profile;
    invalid.authoring_sha256[0] = 'A';
    CHECK(hammond::validate_source_leakage_profile(invalid) == Status::InvalidProfile);
    invalid = profile;
    invalid.authoring_sha256[64] = 'a';
    CHECK(hammond::validate_source_leakage_profile(invalid) == Status::InvalidProfile);
    invalid = profile;
    invalid.edge_count = hammond::kMaxSourceLeakageEdges + 1;
    CHECK(hammond::validate_source_leakage_profile(invalid) == Status::InvalidProfile);
}

} // namespace

int main() {
    check_unprepared_and_identity();
    check_one_edge_and_original_frame_chain();
    check_rejections_preserve_state_and_output();
    check_canonical_sum_boundary();
    check_profile_metadata_and_order();
    return 0;
}
