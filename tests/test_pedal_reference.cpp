#include "TestSupport.h"
#include "hammond/PedalRouting.h"

#include <algorithm>
#include <array>
#include <charconv>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <limits>
#include <optional>
#include <span>
#include <string>
#include <string_view>
#include <system_error>

namespace {
using hammond::PedalBusFrame;
using hammond::PedalBusKernel;
using hammond::PedalContactEdit;
using hammond::PedalId;
using hammond::PedalSourceFrame;
using hammond::PedalWeights;
using hammond::Status;

// Independent documentary shape and bus membership. The CSV, never the native
// table, JSON, compiler, or constructive source-number formula, selects tones.
using CsvRoutes = std::array<std::array<std::optional<unsigned>, 8>, 25>;
using ContactMask = std::array<std::array<bool, 8>, 25>;
constexpr std::array<std::array<std::size_t, 2>, 4> kBusColumns{{
    {{0, 1}}, {{2, 3}}, {{4, 5}}, {{6, 7}},
}};
constexpr std::array<hammond::PedalBus, 8> kColumnBuses{
    hammond::PedalBus::Brown, hammond::PedalBus::Brown,
    hammond::PedalBus::Red, hammond::PedalBus::Red,
    hammond::PedalBus::Orange, hammond::PedalBus::Orange,
    hammond::PedalBus::Yellow, hammond::PedalBus::Yellow};
static_assert(hammond::kPedalCount == 25 && hammond::kPedalContactCount == 8 &&
              hammond::kPedalBusCount == 4 && hammond::kToneSourceCount == 91);

// Fixed before the experiment: each sum has at most 50 products and 50 adds,
// each |product| <= 1. The two independently ordered dot products each have
// an absolute error bounded conservatively by gamma_100 * 50. Use epsilon,
// rather than epsilon/2, and do not assume long double is wider than double.
constexpr double kEpsilon = std::numeric_limits<double>::epsilon();
constexpr double kGamma100 = (100.0 * kEpsilon) / (1.0 - 100.0 * kEpsilon);
constexpr double kOrdinaryTolerance = 2.0 * kGamma100 * 50.0;

struct Counts {
    std::size_t csv_cells{0};
    std::size_t isolated_contacts{0};
    std::size_t exact_frames{0};
    std::size_t ordinary_frames{0};
    std::size_t duplicate_cases{0};
    std::size_t null_cases{0};
    std::size_t oracle_sensitivity_cases{0};
    double peak_ordinary_error{0.0};
};

CsvRoutes read_csv(std::string_view relative) {
    std::ifstream input(hammond_test::source_path(relative));
    CHECK(input.is_open());
    std::string line;
    const auto read_line = [&]() {
        CHECK(static_cast<bool>(std::getline(input, line)));
        CHECK(line.size() <= 128);
        if (!line.empty() && line.back() == '\r') line.pop_back();
    };
    read_line();
    CHECK(line == "pedal,c1,c2,c3,c4,c5,c6,c7,c8");
    CsvRoutes result{};
    for (std::size_t row = 0; row < result.size(); ++row) {
        read_line();
        std::string_view remaining(line);
        for (std::size_t field = 0; field < 9; ++field) {
            const auto comma = remaining.find(',');
            CHECK((field == 8) == (comma == std::string_view::npos));
            const auto token = remaining.substr(0, comma);
            if (token.empty()) {
                CHECK(field != 0);
                result[row][field - 1] = std::nullopt;
            } else {
                unsigned value = 0;
                const auto parsed = std::from_chars(token.data(), token.data() + token.size(), value);
                CHECK(parsed.ec == std::errc{} && parsed.ptr == token.data() + token.size());
                if (field == 0) {
                    CHECK(value == row + 1);
                } else {
                    CHECK(value >= 1 && value <= 91);
                    result[row][field - 1] = value;
                }
            }
            if (comma != std::string_view::npos) remaining.remove_prefix(comma + 1);
        }
    }
    CHECK(!std::getline(input, line));
    CHECK(input.eof());
    return result;
}

PedalBusFrame reference(const CsvRoutes& csv, const ContactMask& contacts,
                        const PedalWeights& weights, const PedalSourceFrame& sources) {
    PedalBusFrame result{};
    // Bus-first, reverse pedal/column order is intentionally different from the
    // production flattened forward scan. Its only source-number oracle is CSV.
    for (std::size_t bus = 0; bus < kBusColumns.size(); ++bus) {
        long double sum = 0.0L;
        for (std::size_t pedal = csv.size(); pedal-- > 0;) {
            for (std::size_t selected = 2; selected-- > 0;) {
                const auto column = kBusColumns[bus][selected];
                if (contacts[pedal][column] && csv[pedal][column]) {
                    const auto source = static_cast<std::size_t>(*csv[pedal][column]) - 1;
                    sum += static_cast<long double>(weights[pedal * 8 + column]) *
                           static_cast<long double>(sources[source]);
                }
            }
        }
        result[bus] = static_cast<double>(sum);
    }
    return result;
}

PedalWeights rational_weights() {
    PedalWeights weights{};
    for (std::size_t position = 0; position < weights.size(); ++position) {
        const double sign = position % 3 == 0 ? -1.0 : 1.0;
        weights[position] = sign * static_cast<double>(position + 1) / 256.0;
    }
    return weights;
}

PedalSourceFrame rational_sources() {
    PedalSourceFrame frame{};
    for (std::size_t source = 0; source < frame.size(); ++source) {
        const int numerator = static_cast<int>((source * 47 + 13) % 129) - 64;
        frame[source] = static_cast<double>(numerator) / 64.0;
    }
    return frame;
}

std::array<PedalContactEdit, 200> contact_edits(const ContactMask& mask) {
    std::array<PedalContactEdit, 200> edits{};
    std::size_t position = 0;
    for (std::size_t row = 0; row < 25; ++row) {
        for (std::size_t column = 0; column < 8; ++column) {
            edits[position++] = {PedalId{static_cast<std::uint8_t>(row + 1)},
                                 static_cast<std::uint8_t>(column), mask[row][column]};
        }
    }
    return edits;
}

void edit(PedalBusKernel& kernel, ContactMask& mask, std::size_t row,
          std::size_t column, bool closed) {
    const std::array change{PedalContactEdit{PedalId{static_cast<std::uint8_t>(row + 1)},
                                            static_cast<std::uint8_t>(column), closed}};
    CHECK(kernel.apply_contacts(change) == Status::Ok);
    mask[row][column] = closed;
    bool observed = !closed;
    CHECK(kernel.contact_closed(change[0].pedal, change[0].contact, observed));
    CHECK(observed == closed);
}

void compare_exact(PedalBusKernel& kernel, const CsvRoutes& csv,
                   const ContactMask& mask, const PedalWeights& weights,
                   const PedalSourceFrame& sources, Counts& counts) {
    PedalBusFrame actual{99, 98, 97, 96};
    const auto before = kernel.contacts_snapshot();
    CHECK(kernel.render_frame(sources, actual) == Status::Ok);
    const auto expected = reference(csv, mask, weights, sources);
    CHECK(actual == expected);
    CHECK(kernel.contacts_snapshot() == before);
    ++counts.exact_frames;
}

void test_documentary_identity(const CsvRoutes& a, const CsvRoutes& b, Counts& counts) {
    CHECK(a == b);
    std::size_t disconnected = 0;
    const auto& native = hammond::compiled_pedal_routes();
    for (const auto& csv : {a, b}) {
        for (std::size_t row = 0; row < 25; ++row) {
            for (std::size_t column = 0; column < 8; ++column) {
                const auto& route = native[row * 8 + column];
                CHECK(route.pedal.value == row + 1 && route.contact == column);
                CHECK(route.bus == kColumnBuses[column]);
                CHECK(route.tone.has_value() == csv[row][column].has_value());
                if (route.tone) CHECK(static_cast<unsigned>(*route.tone) == *csv[row][column]);
                ++counts.csv_cells;
            }
        }
    }
    for (const auto& row : a) for (const auto& cell : row) if (!cell) ++disconnected;
    CHECK(disconnected == 5);

    // Literal retained boundary readings also protect against synchronized
    // reinterpretation of the documentary exception transitions.
    constexpr std::array<std::size_t, 6> pedals{1, 7, 8, 12, 13, 25};
    constexpr std::array<std::array<int, 8>, 6> boundary{{
        {{1, 13, 13, 25, 32, 37, 41, 44}},
        {{7, 19, 19, 31, 38, 43, 47, 50}},
        {{8, -1, 20, 32, 39, 44, 48, 51}},
        {{12, -1, 24, 36, 43, 48, 52, 55}},
        {{13, 32, 25, 37, 44, 49, 53, 56}},
        {{25, 44, 37, 49, 56, 61, 65, 68}},
    }};
    for (std::size_t i = 0; i < pedals.size(); ++i) {
        for (std::size_t column = 0; column < 8; ++column) {
            const auto& cell = a[pedals[i] - 1][column];
            CHECK((cell ? static_cast<int>(*cell) : -1) == boundary[i][column]);
        }
    }
    const auto identity = hammond::compiled_pedal_identity();
    CHECK(identity.model_id == "linear-pedal-bus-reference-v1");
    CHECK(identity.map_id == "atlas-derived-b3-c3-pedal-v1");
    CHECK(identity.map_raw_sha256 ==
          "58a30850c08933a075cfcec04faeb2cb479f60bd9dda82ace3246552221623bd");
    CHECK(identity.map_canonical_sha256 ==
          "7b2631a0c7d55a18f8225d4ee420e472c23b9f2809eec69865474eafce6f5fb2");
    CHECK(identity.factory_comparison_id == "factory-table-iii-comparison-v1");
    CHECK(identity.factory_comparison_raw_sha256 ==
          "8c52ccca13653c6e379da33a10197bfc9ac1a1f3ab6bea6bbe8edf81f7a47b52");
    CHECK(identity.review_a_sha256 ==
          "b8177479a5af16f4e6b8759313d90148a1213657c83f8a6e6533422bfa104ca1");
    CHECK(identity.review_b_sha256 == identity.review_a_sha256);
}

void test_all_isolated_branches(const CsvRoutes& csv, Counts& counts) {
    const auto weights = rational_weights();
    const auto mixed = rational_sources();
    PedalBusKernel kernel;
    CHECK(kernel.prepare(hammond::compiled_pedal_routes(), weights) == Status::Ok);
    ContactMask mask{};
    for (std::size_t row = 0; row < 25; ++row) {
        for (std::size_t column = 0; column < 8; ++column) {
            edit(kernel, mask, row, column, true);
            CHECK(kernel.closed_contact_count() == 1);
            for (std::size_t source = 0; source < 91; ++source) {
                PedalSourceFrame basis{};
                for (const double polarity : {1.0, -1.0}) {
                    basis[source] = polarity;
                    compare_exact(kernel, csv, mask, weights, basis, counts);
                }
            }
            compare_exact(kernel, csv, mask, weights, mixed, counts);
            edit(kernel, mask, row, column, false);
            CHECK(kernel.closed_contact_count() == 0);
            compare_exact(kernel, csv, mask, weights, mixed, counts);
            ++counts.isolated_contacts;
        }
    }
}

void test_repeated_and_disconnected(const CsvRoutes& csv, Counts& counts) {
    const auto weights = rational_weights();
    PedalBusKernel kernel;
    CHECK(kernel.prepare(hammond::compiled_pedal_routes(), weights) == Status::Ok);
    ContactMask mask{};
    for (std::size_t row = 0; row < 7; ++row) {
        CHECK(csv[row][1] && csv[row][1] == csv[row][2]);
        CHECK(weights[row * 8 + 1] != weights[row * 8 + 2]);
        PedalSourceFrame basis{};
        basis[static_cast<std::size_t>(*csv[row][1]) - 1] = 1.0;
        edit(kernel, mask, row, 1, true);
        compare_exact(kernel, csv, mask, weights, basis, counts);
        edit(kernel, mask, row, 2, true);
        compare_exact(kernel, csv, mask, weights, basis, counts);
        PedalBusFrame both{};
        CHECK(kernel.render_frame(basis, both) == Status::Ok);
        CHECK(both[0] == weights[row * 8 + 1]);
        CHECK(both[1] == weights[row * 8 + 2]);
        CHECK(both[2] == 0.0 && both[3] == 0.0);
        edit(kernel, mask, row, 1, false);
        compare_exact(kernel, csv, mask, weights, basis, counts);
        edit(kernel, mask, row, 2, false);
        compare_exact(kernel, csv, mask, weights, basis, counts);
        ++counts.duplicate_cases;
    }

    for (auto& row : mask) row.fill(true);
    CHECK(kernel.apply_contacts(contact_edits(mask)) == Status::Ok);
    const auto mixed = rational_sources();
    for (std::size_t row = 7; row < 12; ++row) {
        CHECK(!csv[row][1]);
        PedalBusFrame closed{}, opened{};
        CHECK(kernel.render_frame(mixed, closed) == Status::Ok);
        CHECK(kernel.closed_contact_count() == 200);
        edit(kernel, mask, row, 1, false);
        CHECK(kernel.closed_contact_count() == 199);
        CHECK(kernel.render_frame(mixed, opened) == Status::Ok);
        CHECK(closed == opened);
        compare_exact(kernel, csv, mask, weights, mixed, counts);
        edit(kernel, mask, row, 1, true);
        CHECK(kernel.closed_contact_count() == 200);
        compare_exact(kernel, csv, mask, weights, mixed, counts);
        ++counts.null_cases;
    }
}

void test_full_occupancy(const CsvRoutes& csv, Counts& counts) {
    ContactMask all{};
    for (auto& row : all) row.fill(true);
    const auto edits = contact_edits(all);
    for (const auto& weights : {rational_weights(), [] {
            PedalWeights result{}; result.fill(1.0); return result; }()}) {
        PedalBusKernel kernel;
        CHECK(kernel.prepare(hammond::compiled_pedal_routes(), weights) == Status::Ok);
        CHECK(kernel.apply_contacts(edits) == Status::Ok);
        CHECK(kernel.closed_contact_count() == 200);
        compare_exact(kernel, csv, all, weights, rational_sources(), counts);
        for (std::size_t source = 0; source < 91; ++source) {
            PedalSourceFrame basis{};
            basis[source] = 1.0;
            compare_exact(kernel, csv, all, weights, basis, counts);
        }
        for (const double value : {1.0, -1.0}) {
            PedalSourceFrame constant{};
            constant.fill(value);
            compare_exact(kernel, csv, all, weights, constant, counts);
            if (weights[0] == 1.0) {
                PedalBusFrame actual{};
                CHECK(kernel.render_frame(constant, actual) == Status::Ok);
                CHECK((actual == PedalBusFrame{45 * value, 50 * value, 50 * value, 50 * value}));
            }
        }
    }
}

std::uint32_t next_value(std::uint32_t& state) {
    state ^= state << 13;
    state ^= state >> 17;
    state ^= state << 5;
    return state;
}

void test_ordinary_arithmetic(const CsvRoutes& csv, Counts& counts) {
    PedalWeights weights{};
    for (std::size_t i = 0; i < weights.size(); ++i) {
        weights[i] = (i % 2 == 0 ? 1.0 : -1.0) * static_cast<double>(i + 1) / 211.0;
    }
    PedalBusKernel kernel;
    CHECK(kernel.prepare(hammond::compiled_pedal_routes(), weights) == Status::Ok);
    std::uint32_t state = 0x5f3179a3U;
    for (std::size_t scenario = 0; scenario < 96; ++scenario) {
        ContactMask mask{};
        for (auto& row : mask) for (auto& closed : row) {
            closed = scenario == 0 || (next_value(state) & 3U) != 0;
        }
        CHECK(kernel.apply_contacts(contact_edits(mask)) == Status::Ok);
        for (std::size_t frame = 0; frame < 32; ++frame) {
            PedalSourceFrame sources{};
            for (auto& source : sources) {
                const int numerator = static_cast<int>(next_value(state) % 1995U) - 997;
                source = static_cast<double>(numerator) / 997.0;
            }
            PedalBusFrame actual{};
            CHECK(kernel.render_frame(sources, actual) == Status::Ok);
            const auto expected = reference(csv, mask, weights, sources);
            for (std::size_t bus = 0; bus < 4; ++bus) {
                CHECK_NEAR(actual[bus], expected[bus], kOrdinaryTolerance);
                CHECK(std::abs(actual[bus]) <= 50.0);
                counts.peak_ordinary_error = std::max(counts.peak_ordinary_error,
                                                      std::abs(actual[bus] - expected[bus]));
            }
            ++counts.ordinary_frames;
        }
    }
}

void test_oracle_sensitivity(const CsvRoutes& csv, Counts& counts) {
    const auto weights = rational_weights();
    ContactMask mask{};
    mask[0][0] = true;
    mask[0][1] = true;
    mask[0][2] = true;
    PedalSourceFrame sources{};
    sources[0] = 0.5;
    sources[12] = 1.0;
    const auto expected = reference(csv, mask, weights, sources);
    for (std::size_t mutation = 0; mutation < 3; ++mutation) {
        auto routes = hammond::compiled_pedal_routes();
        auto supplied_weights = weights;
        if (mutation == 0) routes[0].tone = hammond::ToneId{2};
        if (mutation == 1) routes[1].tone = std::nullopt;
        if (mutation == 2) supplied_weights[2] = -weights[2];
        PedalBusKernel kernel;
        // Structurally valid deliberate counterexamples must be detected by
        // the independent documentary/weight oracle, not blessed by its table.
        CHECK(kernel.prepare(routes, supplied_weights) == Status::Ok);
        CHECK(kernel.apply_contacts(contact_edits(mask)) == Status::Ok);
        PedalBusFrame actual{};
        CHECK(kernel.render_frame(sources, actual) == Status::Ok);
        CHECK(actual != expected);
        ++counts.oracle_sensitivity_cases;
    }
}

} // namespace

int main() {
    Counts counts;
    const auto a = read_csv("data/references/review-a-pedal.csv");
    const auto b = read_csv("data/references/review-b-pedal.csv");
    test_documentary_identity(a, b, counts);
    test_all_isolated_branches(a, counts);
    test_repeated_and_disconnected(a, counts);
    test_full_occupancy(a, counts);
    test_ordinary_arithmetic(a, counts);
    test_oracle_sensitivity(a, counts);
    CHECK(counts.csv_cells == 400 && counts.isolated_contacts == 200);
    CHECK(counts.duplicate_cases == 7 && counts.null_cases == 5);
    CHECK(counts.ordinary_frames == 3072 && counts.oracle_sensitivity_cases == 3);
    std::cout << std::setprecision(17)
              << "independent pedal reference passed: csv_cells=" << counts.csv_cells
              << "; isolated_contacts=" << counts.isolated_contacts
              << "; exact_frames=" << counts.exact_frames
              << "; ordinary_frames=" << counts.ordinary_frames
              << "; repeated_pairs=" << counts.duplicate_cases
              << "; disconnected_positions=" << counts.null_cases
              << "; oracle_counterexamples=" << counts.oracle_sensitivity_cases
              << "; fixed_tolerance=" << kOrdinaryTolerance
              << "; peak_ordinary_error=" << counts.peak_ordinary_error << '\n';
    return 0;
}
