#include "TestSupport.h"
#include "hammond/PedalRouting.h"

#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <span>
#include <type_traits>
#include <utility>

namespace {
using namespace hammond;

static_assert(!std::is_convertible_v<PedalId, ToneId>);
static_assert(!std::is_convertible_v<ToneId, PedalId>);
static_assert(kPedalContactPositionCount == 200);

PedalWeights unit_weights() {
    PedalWeights result{};
    result.fill(1.0);
    return result;
}

PedalSourceFrame constant_sources(double value) {
    PedalSourceFrame result{};
    result.fill(value);
    return result;
}

std::array<PedalContactEdit, kPedalContactPositionCount> all_contacts(bool closed) {
    std::array<PedalContactEdit, kPedalContactPositionCount> edits{};
    for (std::size_t position = 0; position < edits.size(); ++position) {
        edits[position] = {PedalId{static_cast<std::uint8_t>(position / 8 + 1)},
                           static_cast<std::uint8_t>(position % 8), closed};
    }
    return edits;
}

void test_checked_domains() {
    PedalId pedal{17};
    for (const std::uint32_t value : {0U, 26U, 255U, 256U,
                                    std::numeric_limits<std::uint32_t>::max()}) {
        CHECK(!make_pedal_id(value, pedal));
        CHECK(pedal == PedalId{17});
    }
    for (std::uint32_t value = 1; value <= 25; ++value) {
        CHECK(make_pedal_id(value, pedal));
        CHECK(pedal.value == value);
        std::size_t index = 999;
        CHECK(pedal_id_to_index(pedal, index));
        CHECK(index == value - 1);
        for (std::uint32_t contact = 0; contact < 8; ++contact) {
            CHECK(pedal_contact_to_index(pedal, contact, index));
            CHECK(index == (value - 1) * 8 + contact);
        }
    }
    std::size_t index = 999;
    for (const PedalId invalid : {PedalId{0}, PedalId{26}, PedalId{255}}) {
        CHECK(!pedal_id_to_index(invalid, index));
        CHECK(index == 999);
        CHECK(!pedal_contact_to_index(invalid, 0, index));
        CHECK(index == 999);
    }
    for (const std::uint32_t contact : {8U, 255U, 256U,
                                      std::numeric_limits<std::uint32_t>::max()}) {
        CHECK(!pedal_contact_to_index(PedalId{25}, contact, index));
        CHECK(index == 999);
    }
}

void test_documentary_boundaries() {
    const auto& routes = compiled_pedal_routes();
    // Fixed documentary boundary rows; -1 means an explicitly absent branch.
    constexpr std::array<std::uint8_t, 6> pedals{1, 7, 8, 12, 13, 25};
    constexpr std::array<std::array<int, 8>, 6> expected{{
        {{1, 13, 13, 25, 32, 37, 41, 44}},
        {{7, 19, 19, 31, 38, 43, 47, 50}},
        {{8, -1, 20, 32, 39, 44, 48, 51}},
        {{12, -1, 24, 36, 43, 48, 52, 55}},
        {{13, 32, 25, 37, 44, 49, 53, 56}},
        {{25, 44, 37, 49, 56, 61, 65, 68}},
    }};
    std::size_t disconnected = 0;
    for (std::size_t position = 0; position < routes.size(); ++position) {
        const auto& route = routes[position];
        CHECK(route.pedal.value == position / 8 + 1);
        CHECK(route.contact == position % 8);
        CHECK(static_cast<std::size_t>(route.bus) == (position % 8) / 2);
        if (!route.tone) ++disconnected;
    }
    CHECK(disconnected == 5);
    for (std::size_t row = 0; row < pedals.size(); ++row) {
        for (std::size_t column = 0; column < 8; ++column) {
            const auto& actual = routes[(static_cast<std::size_t>(pedals[row]) - 1) * 8 + column];
            CHECK((actual.tone ? static_cast<int>(*actual.tone) : -1) == expected[row][column]);
        }
    }
    const auto identity = compiled_pedal_identity();
    CHECK(identity.model_id == "linear-pedal-bus-reference-v1");
    CHECK(identity.map_id == "atlas-derived-b3-c3-pedal-v1");
    CHECK(identity.map_raw_sha256 ==
          "58a30850c08933a075cfcec04faeb2cb479f60bd9dda82ace3246552221623bd");
    CHECK(identity.map_canonical_sha256 ==
          "7b2631a0c7d55a18f8225d4ee420e472c23b9f2809eec69865474eafce6f5fb2");
    CHECK(identity.factory_comparison_id == "factory-table-iii-comparison-v1");
    CHECK(identity.factory_comparison_raw_sha256.size() == 64);
    CHECK(identity.review_a_sha256 ==
          "b8177479a5af16f4e6b8759313d90148a1213657c83f8a6e6533422bfa104ca1");
    CHECK(identity.review_b_sha256 == identity.review_a_sha256);
}

void test_unprepared_and_contact_transactions() {
    PedalBusKernel kernel;
    const auto initial = kernel;
    bool destination = true;
    CHECK(!kernel.prepared());
    CHECK(kernel.closed_contact_count() == 0);
    CHECK(!kernel.contact_closed(PedalId{1}, 0, destination));
    CHECK(destination);
    CHECK(kernel.contacts_snapshot() == PedalContactStates{});
    std::array<PedalContactEdit, 201> too_many{};
    CHECK(kernel.apply_contacts(too_many) == Status::NotPrepared);
    CHECK(kernel.apply_contacts({}) == Status::NotPrepared);
    auto invalid_sources = constant_sources(std::numeric_limits<double>::quiet_NaN());
    PedalBusFrame output{1, 2, 3, 4};
    const auto output_before = output;
    CHECK(kernel.render_frame(invalid_sources, output) == Status::NotPrepared);
    CHECK(output == output_before);
    CHECK(kernel.prepare({}, unit_weights()) == Status::InvalidProfile);
    CHECK(kernel == initial);

    CHECK(kernel.prepare(compiled_pedal_routes(), unit_weights()) == Status::Ok);
    const std::array repeated{
        PedalContactEdit{PedalId{1}, 0, true},
        PedalContactEdit{PedalId{8}, 1, true}, // Physically tracked, electrically null.
        PedalContactEdit{PedalId{1}, 0, false},
        PedalContactEdit{PedalId{1}, 0, true}};
    CHECK(kernel.apply_contacts(repeated) == Status::Ok);
    CHECK(kernel.closed_contact_count() == 2);
    CHECK(kernel.contact_closed(PedalId{1}, 0, destination) && destination);
    CHECK(kernel.contact_closed(PedalId{8}, 1, destination) && destination);
    const auto before = kernel;
    CHECK(kernel.apply_contacts({}) == Status::Ok);
    CHECK(kernel == before);
    CHECK(kernel.apply_contacts(too_many) == Status::TooManyEvents);
    CHECK(kernel == before);
    for (const auto invalid : {PedalContactEdit{PedalId{0}, 0, true},
                               PedalContactEdit{PedalId{26}, 0, true},
                               PedalContactEdit{PedalId{255}, 0, true},
                               PedalContactEdit{PedalId{25}, 8, true},
                               PedalContactEdit{PedalId{25}, 255, true}}) {
        const std::array edits{PedalContactEdit{PedalId{1}, 0, false}, invalid};
        CHECK(kernel.apply_contacts(edits) == Status::InvalidEvent);
        CHECK(kernel == before);
        destination = true;
        CHECK(!kernel.contact_closed(invalid.pedal, invalid.contact, destination));
        CHECK(destination);
    }
    CHECK(kernel.apply_contacts(all_contacts(true)) == Status::Ok);
    CHECK(kernel.closed_contact_count() == 200);
    CHECK(kernel.apply_contacts(all_contacts(false)) == Status::Ok);
    CHECK(kernel.closed_contact_count() == 0);
}

void test_prepare_transactions_and_ownership() {
    auto routes = compiled_pedal_routes();
    auto weights = unit_weights();
    PedalBusKernel kernel;
    CHECK(kernel.prepare(routes, weights) == Status::Ok);
    CHECK(kernel.apply_contacts(all_contacts(true)) == Status::Ok);
    const auto before = kernel;
    const auto invalid_definition = [&](const PedalRouteDefinition& candidate) {
        CHECK(kernel.prepare(candidate, weights) == Status::InvalidProfile);
        CHECK(kernel == before);
    };
    CHECK(kernel.prepare(std::span<const PedalRoute>(routes).first(199), weights) ==
          Status::InvalidProfile);
    CHECK(kernel == before);
    std::array<PedalRoute, 201> oversized{};
    CHECK(kernel.prepare(oversized, weights) == Status::InvalidProfile);
    CHECK(kernel == before);
    for (std::size_t position : {std::size_t{0}, std::size_t{57}, std::size_t{199}}) {
        auto candidate = routes;
        candidate[position] = {};
        invalid_definition(candidate); // Missing/default slot, including null position57.
        candidate = routes;
        candidate[position].pedal = PedalId{26};
        invalid_definition(candidate);
        candidate = routes;
        candidate[position].contact = 8;
        invalid_definition(candidate);
        candidate = routes;
        candidate[position].bus = static_cast<PedalBus>(255);
        invalid_definition(candidate);
        candidate = routes;
        candidate[position].bus = static_cast<PedalBus>((position % 8 / 2 + 1) % 4);
        invalid_definition(candidate);
        candidate = routes;
        candidate[position].tone = ToneId{0};
        invalid_definition(candidate);
        candidate[position].tone = ToneId{92};
        invalid_definition(candidate);
    }
    auto duplicate = routes;
    duplicate[199] = duplicate[0];
    invalid_definition(duplicate);
    auto swapped = routes;
    std::swap(swapped[0], swapped[1]);
    invalid_definition(swapped);

    const std::array invalid_values{std::numeric_limits<double>::quiet_NaN(),
                                    std::numeric_limits<double>::infinity(),
                                    -std::numeric_limits<double>::infinity(),
                                    std::nextafter(1.0, 2.0), std::nextafter(-1.0, -2.0)};
    for (std::size_t position = 0; position < weights.size(); ++position) {
        for (double invalid : invalid_values) {
            auto candidate = weights;
            candidate[position] = invalid;
            CHECK(kernel.prepare(routes, candidate) == Status::InvalidProfile);
            CHECK(kernel == before);
        }
    }

    auto sources = constant_sources(1.0);
    sources[0] = 0.25;
    sources[90] = -0.75;
    PedalBusFrame expected{};
    CHECK(kernel.render_frame(sources, expected) == Status::Ok);
    routes[0].tone = ToneId{91};
    PedalBusFrame actual{};
    CHECK(kernel.render_frame(sources, actual) == Status::Ok);
    CHECK(actual == expected); // Runtime owns the prior inputs, not their addresses.
    weights.fill(0.0);
    CHECK(kernel.render_frame(sources, actual) == Status::Ok);
    CHECK(actual == expected);
    CHECK(kernel == before);
    CHECK(kernel.prepare(routes, weights) == Status::Ok);
    CHECK(kernel.closed_contact_count() == 0); // Successful reprepare starts open.
}

void test_independent_branches_and_bounds() {
    PedalBusKernel kernel;
    auto weights = unit_weights();
    weights[1] = 0.25;
    weights[2] = -0.75;
    CHECK(kernel.prepare(compiled_pedal_routes(), weights) == Status::Ok);
    PedalSourceFrame sources{};
    sources[12] = -0.5;
    const auto source_before = sources;
    const std::array collision{PedalContactEdit{PedalId{1}, 1, true},
                               PedalContactEdit{PedalId{1}, 2, true},
                               PedalContactEdit{PedalId{8}, 1, true}};
    CHECK(kernel.apply_contacts(collision) == Status::Ok);
    PedalBusFrame actual{};
    CHECK(kernel.render_frame(sources, actual) == Status::Ok);
    CHECK((actual == PedalBusFrame{-0.125, 0.375, 0, 0}));
    const auto repeated = kernel;
    CHECK(kernel.render_frame(sources, actual) == Status::Ok);
    CHECK(kernel == repeated);
    CHECK(sources == source_before);
    const std::array release{PedalContactEdit{PedalId{1}, 1, false}};
    CHECK(kernel.apply_contacts(release) == Status::Ok);
    CHECK(kernel.render_frame(sources, actual) == Status::Ok);
    CHECK((actual == PedalBusFrame{0, 0.375, 0, 0}));
    CHECK(kernel.closed_contact_count() == 2);

    CHECK(kernel.prepare(compiled_pedal_routes(), unit_weights()) == Status::Ok);
    CHECK(kernel.apply_contacts(all_contacts(true)) == Status::Ok);
    CHECK(kernel.render_frame(constant_sources(1.0), actual) == Status::Ok);
    CHECK((actual == PedalBusFrame{45, 50, 50, 50}));
    CHECK(kernel.render_frame(constant_sources(-1.0), actual) == Status::Ok);
    CHECK((actual == PedalBusFrame{-45, -50, -50, -50}));

    // Generic, structurally valid reference table attains all four bus bounds.
    // This is explicitly a test fixture, not the compiled factory map.
    auto fixture = compiled_pedal_routes();
    for (auto& route : fixture) route.tone = ToneId{91};
    CHECK(kernel.prepare(fixture, unit_weights()) == Status::Ok);
    CHECK(kernel.apply_contacts(all_contacts(true)) == Status::Ok);
    CHECK(kernel.render_frame(constant_sources(1.0), actual) == Status::Ok);
    CHECK((actual == PedalBusFrame{50, 50, 50, 50}));
    for (auto& route : fixture) route.tone = std::nullopt;
    CHECK(kernel.prepare(fixture, unit_weights()) == Status::Ok);
    CHECK(kernel.apply_contacts(all_contacts(true)) == Status::Ok);
    CHECK(kernel.render_frame(constant_sources(1.0), actual) == Status::Ok);
    CHECK(actual == PedalBusFrame{});
    CHECK(kernel.closed_contact_count() == 200);
}

void test_source_admission() {
    PedalBusKernel kernel;
    CHECK(kernel.prepare(compiled_pedal_routes(), unit_weights()) == Status::Ok);
    // Keep contacts open: validation must include unused sources and silent paths.
    const auto before = kernel;
    const std::array invalid_values{std::numeric_limits<double>::quiet_NaN(),
                                    std::numeric_limits<double>::infinity(),
                                    -std::numeric_limits<double>::infinity(),
                                    std::nextafter(1.0, 2.0), std::nextafter(-1.0, -2.0)};
    for (std::size_t source = 0; source < kToneSourceCount; ++source) {
        for (double invalid : invalid_values) {
            auto frame = constant_sources(0.0);
            frame[source] = invalid;
            PedalBusFrame output{7, 8, 9, 10};
            const auto destination_before = output;
            CHECK(kernel.render_frame(frame, output) == Status::InvalidBuffer);
            CHECK(output == destination_before);
            CHECK(kernel == before);
        }
    }
    PedalBusFrame output{7, 8, 9, 10};
    CHECK(kernel.render_frame(constant_sources(-0.0), output) == Status::Ok);
    CHECK(output == PedalBusFrame{});
}

} // namespace

int main() {
    test_checked_domains();
    test_documentary_boundaries();
    test_unprepared_and_contact_transactions();
    test_prepare_transactions_and_ownership();
    test_independent_branches_and_bounds();
    test_source_admission();
    std::cout << "pedal routing: six focused admission, atomicity, branch and bound groups passed\n";
}
