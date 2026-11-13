#include "TestSupport.h"
#include "hammond/ControlStateIO.h"

#include <algorithm>
#include <array>
#include <bit>
#include <cfenv>
#include <cstdint>
#include <iterator>
#include <limits>
#include <sstream>
#include <string>
#include <string_view>
#include <vector>

namespace {
using namespace hammond;
using Tokens = std::vector<std::string>;

// Independently authored fixed fixtures. Earlier grammars intentionally contain
// no pedal record; changing their version marker alone must never migrate them.
constexpr std::string_view kManualRecords =
    "manual upper selected A route_enabled 0\n"
    "bank A 0 1 2 3 4 5 6 7 8\n"
    "bank B 8 7 6 5 4 3 2 1 0\n"
    "manual lower selected B route_enabled 1\n"
    "bank A 1 3 5 7 0 2 4 6 8\n"
    "bank B 8 6 4 2 0 7 5 3 1\n"
    "end\n";
constexpr std::string_view kPercussion =
    "percussion enabled 1 harmonic third volume soft decay fast\n";

std::size_t round_trips = 0;
std::size_t migrations = 0;
std::size_t rejected_documents = 0;
std::size_t rejected_snapshots = 0;

ControlSnapshot reference() {
    ControlSnapshot state;
    state.expression = 0.375;
    state.selected_banks = {DrawbarBank::A, DrawbarBank::B};
    state.route_enabled = {false, true};
    state.drawbars[0][0] = {0, 1, 2, 3, 4, 5, 6, 7, 8};
    state.drawbars[0][1] = {8, 7, 6, 5, 4, 3, 2, 1, 0};
    state.drawbars[1][0] = {1, 3, 5, 7, 0, 2, 4, 6, 8};
    state.drawbars[1][1] = {8, 6, 4, 2, 0, 7, 5, 3, 1};
    state.percussion = {true, PercussionHarmonic::Third,
                        PercussionVolume::Soft, PercussionDecay::Fast};
    state.pedal_drawbars = {2, 7};
    return state;
}

void same(const ControlSnapshot& actual, const ControlSnapshot& expected) {
    CHECK(actual == expected);
    CHECK(std::bit_cast<std::uint64_t>(actual.expression) ==
          std::bit_cast<std::uint64_t>(expected.expression));
}

std::string version1() {
    return std::string("B3CONTROLS1\nexpression 0.375\n") + std::string(kManualRecords);
}

std::string version2() {
    return std::string("B3CONTROLS2\nexpression 0.375\n") +
           std::string(kPercussion) + std::string(kManualRecords);
}

std::string version3(std::uint8_t first = 2, std::uint8_t second = 7) {
    return std::string("B3CONTROLS3\nexpression 0.375\n") + std::string(kPercussion) +
           "pedal drawbars " + std::to_string(first) + ' ' + std::to_string(second) + '\n' +
           std::string(kManualRecords);
}

std::string encode(const ControlSnapshot& state) {
    std::string result = "preserved output";
    std::string error = "old error";
    CHECK(serialize_controls(state, result, error));
    CHECK(error.empty());
    return result;
}

ControlSnapshot decode(const std::string& bytes, ControlSnapshot destination = reference()) {
    std::istringstream input(bytes);
    std::string error = "old error";
    CHECK(parse_controls(input, destination, error));
    CHECK(error.empty());
    return destination;
}

Tokens tokenize(const std::string& bytes) {
    std::istringstream input(bytes);
    return Tokens{std::istream_iterator<std::string>(input),
                  std::istream_iterator<std::string>()};
}

std::string join(const Tokens& tokens) {
    std::string result;
    for (const auto& token : tokens) result += token + ' ';
    return result;
}

void reject(const std::string& bytes) {
    auto destination = reference();
    destination.expression = -0.0;
    destination.pedal_drawbars = {8, 6};
    const auto before = destination;
    std::istringstream input(bytes);
    std::string error = "old error";
    CHECK(!parse_controls(input, destination, error));
    CHECK(!error.empty() && error != "old error");
    same(destination, before);
    ++rejected_documents;
}

void test_retained_controls() {
    ControlState controls;
    CHECK(controls.pedal_drawbar_positions() == PedalDrawbarPositions{});
    CHECK(controls.snapshot().pedal_drawbars == PedalDrawbarPositions{});
    CHECK(controls.restore(reference()));
    auto expected = reference();
    for (std::uint8_t first = 0; first <= 8; ++first) {
        for (std::uint8_t second = 0; second <= 8; ++second) {
            CHECK(controls.set_pedal_drawbar(0, first));
            CHECK(controls.set_pedal_drawbar(1, second));
            expected.pedal_drawbars = {first, second};
            same(controls.snapshot(), expected);
            CHECK(controls.pedal_drawbar_positions() == expected.pedal_drawbars);
            for (std::size_t index = 0; index < kPedalDrawbarCount; ++index) {
                std::uint8_t observed = 255;
                CHECK(controls.pedal_drawbar_position(index, observed));
                CHECK(observed == expected.pedal_drawbars[index]);
            }
            CHECK(controls.set_pedal_drawbar(1, second)); // Accepted no-op.
            same(controls.snapshot(), expected);
        }
    }
    auto copy = controls.pedal_drawbar_positions();
    copy.fill(0);
    CHECK(copy != controls.pedal_drawbar_positions());
    CHECK(controls.cancel(Manual::Lower));
    expected.route_enabled[1] = false;
    same(controls.snapshot(), expected);
    CHECK(controls.select_bank(Manual::Lower, DrawbarBank::A));
    expected.selected_banks[1] = DrawbarBank::A;
    expected.route_enabled[1] = true;
    same(controls.snapshot(), expected);
    CHECK(controls.set_percussion_settings(PercussionSettings{}));
    expected.percussion = {};
    same(controls.snapshot(), expected);
    CHECK(controls.pedal_drawbar_positions() == (PedalDrawbarPositions{8, 8}));

    const auto before = controls.snapshot();
    for (const auto index : {std::size_t{2}, std::size_t{255},
                             std::numeric_limits<std::size_t>::max()}) {
        CHECK(!controls.set_pedal_drawbar(index, 0));
        std::uint8_t destination = 217;
        CHECK(!controls.pedal_drawbar_position(index, destination));
        CHECK(destination == 217);
        same(controls.snapshot(), before);
    }
    for (std::size_t index = 0; index < kPedalDrawbarCount; ++index) {
        for (unsigned value = 9; value <= 255; ++value) {
            const auto invalid = static_cast<std::uint8_t>(value);
            CHECK(!controls.set_pedal_drawbar(index, invalid));
            same(controls.snapshot(), before);
            auto candidate = reference();
            candidate.expression = 0.875;
            candidate.drawbars[1][0].fill(4);
            candidate.pedal_drawbars[index] = invalid;
            CHECK(!is_valid_control_snapshot(candidate));
            CHECK(!controls.restore(candidate));
            same(controls.snapshot(), before);
            std::string bytes = "original bytes";
            std::string error = "old error";
            CHECK(!serialize_controls(candidate, bytes, error));
            CHECK(bytes == "original bytes");
            CHECK(!error.empty() && error != "old error");
            ++rejected_snapshots;
        }
    }
}

void test_roundtrip_and_legacy_migration() {
    CHECK(tokenize(version1()).size() == 60);
    CHECK(tokenize(version2()).size() == 69);
    CHECK(tokenize(version3()).size() == 73);
    CHECK(encode(reference()) == version3());
    for (std::uint8_t first = 0; first <= 8; ++first) {
        for (std::uint8_t second = 0; second <= 8; ++second) {
            auto candidate = reference();
            candidate.pedal_drawbars = {first, second};
            const auto bytes = version3(first, second);
            CHECK(encode(candidate) == bytes);
            same(decode(bytes), candidate);
            same(decode(encode(candidate)), candidate);
            ++round_trips;
            for (const unsigned version : {1U, 2U}) {
                auto expected = reference();
                expected.pedal_drawbars = {};
                if (version == 1) expected.percussion = {};
                // Every previous pair, including nonzero destination controls,
                // must load identical explicit defaults from each old grammar.
                const auto restored = decode(version == 1 ? version1() : version2(), candidate);
                same(restored, expected);
                CHECK(encode(restored).starts_with("B3CONTROLS3\n"));
                ++migrations;
            }
        }
    }
    // All admitted expression bit patterns retain nonzero pedal values under
    // each standard rounding mode; neither new control affects decimal state.
    const int original_mode = std::fegetround();
    CHECK(original_mode != -1);
    const std::array<double, 6> expressions{0.0, -0.0, 0.1, 1.0,
        std::numeric_limits<double>::min(), std::numeric_limits<double>::denorm_min()};
    CHECK(std::fesetround(FE_TONEAREST) == 0);
    std::array<std::string, expressions.size()> nearest;
    for (std::size_t index = 0; index < expressions.size(); ++index) {
        auto candidate = reference();
        candidate.expression = expressions[index];
        nearest[index] = encode(candidate);
    }
    for (const int mode : {FE_TONEAREST, FE_DOWNWARD, FE_UPWARD, FE_TOWARDZERO}) {
        CHECK(std::fesetround(mode) == 0);
        for (std::size_t index = 0; index < expressions.size(); ++index) {
            auto candidate = reference();
            candidate.expression = expressions[index];
            const auto bytes = encode(candidate);
            CHECK(bytes == nearest[index]);
            same(decode(bytes), candidate);
            CHECK(std::fegetround() == mode);
            ++round_trips;
        }
    }
    CHECK(std::fesetround(original_mode) == 0);
}

void test_current_grammar_rejection() {
    const auto original = tokenize(version3());
    auto change = [&](std::size_t index, std::string_view value) {
        auto changed = original;
        changed.at(index) = value;
        reject(join(changed));
    };
    for (const auto version : {"B3CONTROLS0", "B3CONTROLS1", "B3CONTROLS2",
                               "B3CONTROLS4", "B3CONTROLS03", "B3CONTROLS3.0"}) change(0, version);
    change(12, "pedals");
    change(13, "drawbar");
    for (const std::size_t index : {std::size_t{14}, std::size_t{15}}) {
        for (const auto value : {"9", "255", "256", "-1", "+1", "01", "1.0", "0x1",
                                 "nan", "inf", "1e0", "true", "1junk", ""}) change(index, value);
    }
    for (const auto expression : {"nan", "inf", "-inf", "1e9999", "1e-9999",
                                   "-0.1", "1.0000000000000002"}) change(2, expression);
    std::string prefix;
    for (const auto& token : original) {
        reject(prefix);
        prefix += token + ' ';
    }
    for (std::size_t index = 12; index < 16; ++index) {
        auto missing = original;
        missing.erase(missing.begin() + static_cast<Tokens::difference_type>(index));
        reject(join(missing));
    }
    auto missing_record = original;
    missing_record.erase(missing_record.begin() + 12, missing_record.begin() + 16);
    reject(join(missing_record)); // Version 3 cannot inherit a destination pair.
    auto duplicate = original;
    duplicate.insert(duplicate.begin() + 16, original.begin() + 12, original.begin() + 16);
    reject(join(duplicate));
    auto reordered = original;
    std::rotate(reordered.begin() + 3, reordered.begin() + 12, reordered.begin() + 16);
    reject(join(reordered));
    for (const auto suffix : {"pedal drawbars 1 2", "end", "extension 1", "# comment"}) {
        reject(version3() + suffix);
    }
    auto old_with_pedals = version2();
    old_with_pedals.insert(old_with_pedals.find("manual upper"), "pedal drawbars 1 2\n");
    reject(old_with_pedals);
    old_with_pedals = version1();
    old_with_pedals.insert(old_with_pedals.find("manual upper"), "pedal drawbars 1 2\n");
    reject(old_with_pedals);

    auto exact = version3();
    exact.resize(kMaxControlStateBytes, ' ');
    same(decode(exact), reference());
    reject(exact + ' ');
    reject(std::string("\xef\xbb\xbf") + version3());
    reject(version3() + std::string(1, '\0'));
    reject(version3() + std::string("\xc2\xa0"));
    std::string alias = "preserved alias";
    CHECK(!serialize_controls(reference(), alias, alias));
    CHECK(alias == "preserved alias");
}
} // namespace

int main() {
    try {
        test_retained_controls();
        test_roundtrip_and_legacy_migration();
        test_current_grammar_rejection();
        std::cout << "Pedal controls passed: " << round_trips << " round trips, "
                  << migrations << " legacy migrations, " << rejected_documents
                  << " rejected documents, " << rejected_snapshots
                  << " rejected snapshots; all failures preserve destinations.\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Pedal controls failed: " << error.what() << '\n';
        return 1;
    }
}
