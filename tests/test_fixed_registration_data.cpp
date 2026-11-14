#include "TestSupport.h"
#include "PresetTestOracle.h"
#include "hammond/FixedRegistration.h"

#include <array>
#include <cstddef>
#include <cstdint>
#include <string_view>
#include <type_traits>
#include <utility>

namespace {

using namespace hammond;

static_assert(kFixedRegistrationCount == 9);
static_assert(kPresetSelectionCount == 12);
static_assert(std::is_same_v<std::underlying_type_t<FixedRegistration>, std::uint8_t>);
static_assert(std::is_same_v<std::underlying_type_t<PresetSelection>, std::uint8_t>);
static_assert(!std::is_convertible_v<FixedRegistration, PresetSelection>);
static_assert(!std::is_convertible_v<PresetSelection, FixedRegistration>);
static_assert(std::is_same_v<FixedRegistrationPositions, std::array<std::uint8_t, 9>>);
static_assert(noexcept(fixed_registration_positions(Manual::Upper, FixedRegistration::CSharp,
                                                   std::declval<FixedRegistrationPositions&>())));
static_assert(noexcept(fixed_registration_catalog_id()));
static_assert(noexcept(fixed_registration_catalog_sha256()));
static_assert(noexcept(fixed_registration_label(FixedRegistration::None)));
static_assert(noexcept(preset_selection_label(PresetSelection::Cancel)));

constexpr std::array<FixedRegistration, 10> kFixedValues{
    FixedRegistration::None, FixedRegistration::CSharp, FixedRegistration::D,
    FixedRegistration::DSharp, FixedRegistration::E, FixedRegistration::F,
    FixedRegistration::FSharp, FixedRegistration::G, FixedRegistration::GSharp,
    FixedRegistration::A,
};
constexpr std::array<PresetSelection, 12> kSelectionValues{
    PresetSelection::Cancel, PresetSelection::CSharp, PresetSelection::D,
    PresetSelection::DSharp, PresetSelection::E, PresetSelection::F,
    PresetSelection::FSharp, PresetSelection::G, PresetSelection::GSharp,
    PresetSelection::A, PresetSelection::BankA, PresetSelection::BankB,
};

void test_literal_rows_and_copy_isolation() {
    for (std::size_t manual = 0; manual < 2; ++manual) {
        for (std::size_t row = 0; row < 9; ++row) {
            const auto registration = kFixedValues[row + 1];
            FixedRegistrationPositions actual{};
            actual.fill(255);
            CHECK(fixed_registration_positions(static_cast<Manual>(manual), registration, actual));
            for (std::size_t drawbar = 0; drawbar < 9; ++drawbar) {
                CHECK(actual[drawbar] == preset_test_oracle::kPositions[manual][row][drawbar]);
                CHECK(actual[drawbar] <= 8);
            }
            const auto expected = actual;
            // Every caller owns its copied row. Changing it cannot alter any
            // registration returned on subsequent or opposite-manual calls.
            actual.fill(255);
            CHECK(fixed_registration_positions(static_cast<Manual>(manual), registration, actual));
            CHECK(actual == expected);
        }
    }
}

void test_exhaustive_checked_byte_domains() {
    constexpr FixedRegistrationPositions sentinel{17, 91, 23, 67, 35, 59, 47, 83, 11};
    struct GuardedPositions {
        std::array<std::uint8_t, 4> before{113, 127, 139, 151};
        FixedRegistrationPositions positions{sentinel};
        std::array<std::uint8_t, 4> after{163, 179, 191, 211};
    };
    const GuardedPositions initial{};
    for (std::uint32_t manual = 0; manual <= 255; ++manual) {
        for (std::uint32_t value = 0; value <= 255; ++value) {
            GuardedPositions destination{};
            const auto registration = static_cast<FixedRegistration>(value);
            CHECK(is_valid_fixed_registration(registration) == (value <= 9));
            CHECK(is_valid_preset_selection(static_cast<PresetSelection>(value)) == (value <= 11));
            const bool expected = manual < 2 && value >= 1 && value <= 9;
            CHECK(fixed_registration_positions(static_cast<Manual>(manual), registration,
                                               destination.positions) == expected);
            CHECK(destination.before == initial.before);
            CHECK(destination.after == initial.after);
            if (!expected) {
                CHECK(destination.positions == sentinel);
            } else {
                for (std::size_t drawbar = 0; drawbar < 9; ++drawbar) {
                    CHECK(destination.positions[drawbar] ==
                          preset_test_oracle::kPositions[manual][value - 1][drawbar]);
                }
            }
        }
    }
}

void test_exact_labels_and_stable_views() {
    for (std::size_t value = 0; value < kFixedValues.size(); ++value) {
        CHECK(static_cast<std::size_t>(kFixedValues[value]) == value);
    }
    for (std::size_t value = 0; value < kSelectionValues.size(); ++value) {
        CHECK(static_cast<std::size_t>(kSelectionValues[value]) == value);
    }
    constexpr std::array<std::string_view, 12> selections{
        "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B",
    };
    std::array<std::string_view, 12> retained{};
    for (std::uint32_t value = 0; value <= 255; ++value) {
        const auto fixed = fixed_registration_label(static_cast<FixedRegistration>(value));
        const auto selected = preset_selection_label(static_cast<PresetSelection>(value));
        if (value == 0) {
            CHECK(fixed == "none");
            CHECK(selected == "C");
        } else if (value <= 9) {
            CHECK(fixed == preset_test_oracle::kKeys[value - 1]);
            CHECK(selected == preset_test_oracle::kKeys[value - 1]);
        } else {
            CHECK(fixed.empty());
        }
        if (value < selections.size()) {
            CHECK(selected == selections[value]);
            retained[value] = selected;
        } else {
            CHECK(selected.empty());
        }
    }
    for (std::size_t value = 0; value < retained.size(); ++value) {
        const auto current = preset_selection_label(kSelectionValues[value]);
        CHECK(retained[value] == selections[value]);
        CHECK(retained[value].data() == current.data());
    }
    CHECK(fixed_registration_label(FixedRegistration::A) !=
          preset_selection_label(PresetSelection::BankA));
}

void test_frozen_catalog_identity() {
    const auto id = fixed_registration_catalog_id();
    const auto hash = fixed_registration_catalog_sha256();
    CHECK(id == "atlas-chapel-nominal-v1");
    CHECK(hash == "c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf");
    test_literal_rows_and_copy_isolation();
    CHECK(id.data() == fixed_registration_catalog_id().data());
    CHECK(hash.data() == fixed_registration_catalog_sha256().data());
    CHECK(id == fixed_registration_catalog_id());
    CHECK(hash == fixed_registration_catalog_sha256());
}

} // namespace

int main() {
    test_literal_rows_and_copy_isolation();
    test_exhaustive_checked_byte_domains();
    test_exact_labels_and_stable_views();
    test_frozen_catalog_identity();
    return 0;
}
