#include "TestSupport.h"
#include "hammond/ContactBank.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <limits>

namespace {

using namespace hammond;
using Snapshots = std::array<std::array<ContactKeySnapshot, kManualKeyCount>, kManualCount>;
constexpr std::array<double, 3> kRates{44100.0, 48000.0, 96000.0};
constexpr std::array<Manual, 2> kManuals{Manual::Upper, Manual::Lower};
constexpr Manual kBadManual = static_cast<Manual>(255);

[[nodiscard]] std::uint32_t midi(std::size_t key) {
    return static_cast<std::uint32_t>(key) + kMinManualMidiNote;
}

[[nodiscard]] ContactKeySnapshot key_state(const ContactBank& bank, Manual manual,
                                           std::uint32_t note) {
    ContactKeySnapshot state;
    CHECK(bank.key_snapshot(manual, note, state));
    return state;
}

[[nodiscard]] Snapshots snapshots(const ContactBank& bank) {
    Snapshots result{};
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        for (std::size_t key = 0; key < kManualKeyCount; ++key) {
            CHECK(bank.key_snapshot(kManuals[manual], midi(key), result[manual][key]));
        }
    }
    return result;
}

void advance(ContactBank& bank, std::uint32_t count) {
    for (std::uint32_t frame = 0; frame < count; ++frame) {
        (void)bank.advance_frame();
    }
}

void same_future(ContactBank actual, ContactBank expected, std::uint32_t frames = 64) {
    CHECK(actual.mode() == expected.mode());
    CHECK(snapshots(actual) == snapshots(expected));
    for (std::uint32_t frame = 0; frame < frames; ++frame) {
        CHECK(actual.advance_frame() == expected.advance_frame());
        CHECK(snapshots(actual) == snapshots(expected));
    }
}

void unprepared_and_checked_queries() {
    ContactBank bank;
    ContactKeySnapshot state{0.375, 0.875, {true, false, true}};
    const auto before = state;
    double number = 3.25;
    bool flag = true;
    CHECK(!bank.key_snapshot(Manual::Upper, 36, state));
    CHECK(state == before);
    CHECK(!bank.position(Manual::Upper, 36, number) && number == 3.25);
    CHECK(!bank.position_target(Manual::Upper, 36, number) && number == 3.25);
    CHECK(!bank.key_target(Manual::Upper, 36, flag) && flag);
    CHECK(!bank.contact_closed(Manual::Upper, 36, 0, flag) && flag);
    CHECK(!bank.any_closed(Manual::Upper, 0, flag) && flag);
    CHECK(!bank.set_key_target(Manual::Upper, 36, true));
    CHECK(!bank.set_position_target(Manual::Upper, 36, 0.5));
    CHECK(!bank.panic_manual(Manual::Upper));
    CHECK(!bank.advance_frame());
    CHECK(!bank.prepared());

    CHECK(bank.prepare(make_nominal_contact_profile(), 48000.0) == Status::Ok);
    for (const auto note : {35U, 97U, std::numeric_limits<std::uint32_t>::max()}) {
        CHECK(!bank.key_snapshot(Manual::Upper, note, state) && state == before);
        CHECK(!bank.position(Manual::Upper, note, number) && number == 3.25);
        CHECK(!bank.position_target(Manual::Upper, note, number) && number == 3.25);
        CHECK(!bank.key_target(Manual::Upper, note, flag) && flag);
        CHECK(!bank.contact_closed(Manual::Upper, note, 0, flag) && flag);
        CHECK(!bank.set_key_target(Manual::Upper, note, true));
    }
    CHECK(!bank.key_snapshot(kBadManual, 60, state) && state == before);
    CHECK(!bank.position(kBadManual, 60, number) && number == 3.25);
    CHECK(!bank.position_target(kBadManual, 60, number) && number == 3.25);
    CHECK(!bank.key_target(kBadManual, 60, flag) && flag);
    CHECK(!bank.contact_closed(kBadManual, 60, 0, flag) && flag);
    CHECK(!bank.contact_closed(Manual::Upper, 60, kDrawbarCount, flag) && flag);
    CHECK(!bank.any_closed(kBadManual, 0, flag) && flag);
    CHECK(!bank.any_closed(Manual::Lower, kDrawbarCount, flag) && flag);
    CHECK(!bank.set_key_target(kBadManual, 60, true));
    CHECK(!bank.panic_manual(kBadManual));
}

void ideal_legacy_behavior() {
    ContactBank bank;
    CHECK(bank.prepare(make_ideal_contact_profile(), 48000.0) == Status::Ok);
    for (const auto manual : kManuals) {
        for (std::size_t key = 0; key < kManualKeyCount; ++key) {
            CHECK(bank.set_key_target(manual, midi(key), true));
            const auto state = key_state(bank, manual, midi(key));
            CHECK(state.position == 1.0 && state.target == 1.0);
            CHECK(std::all_of(state.closed.begin(), state.closed.end(), [](bool closed) {
                return closed;
            }));
            CHECK(bank.set_key_target(manual, midi(key), true));
            CHECK(key_state(bank, manual, midi(key)) == state);
        }
    }
    const auto held = snapshots(bank);
    CHECK(!bank.advance_frame());
    CHECK(snapshots(bank) == held);
    for (const double target : {0.25, 0.5, 0.999}) {
        CHECK(!bank.set_position_target(Manual::Upper, 60, target));
        CHECK(snapshots(bank) == held);
    }
    CHECK(bank.set_key_target(Manual::Upper, 60, false));
    CHECK(key_state(bank, Manual::Upper, 60) == ContactKeySnapshot{});
    CHECK(key_state(bank, Manual::Lower, 60).closed[8]);
    CHECK(bank.panic_manual(Manual::Upper));
    for (std::size_t key = 0; key < kManualKeyCount; ++key) {
        CHECK(key_state(bank, Manual::Upper, midi(key)) == ContactKeySnapshot{});
        CHECK(key_state(bank, Manual::Lower, midi(key)) == held[1][key]);
    }
}

void every_contact_has_independent_identity() {
    // One-hot partial holds traverse every manual/key/contact identity. The
    // singled-out make threshold is deliberately out of physical-index order.
    // No source map or implementation recurrence supplies the expected mask.
    for (std::size_t selected_manual = 0; selected_manual < kManualCount; ++selected_manual) {
        for (std::size_t selected_key = 0; selected_key < kManualKeyCount; ++selected_key) {
            for (std::size_t selected_contact = 0; selected_contact < kDrawbarCount;
                 ++selected_contact) {
                auto profile = make_nominal_contact_profile();
                auto& custom = profile.keys[selected_manual][selected_key];
                custom.press_seconds = 0.001;
                custom.release_seconds = 0.001;
                custom.on_thresholds.fill(0.875);
                custom.off_thresholds.fill(0.75);
                custom.on_thresholds[selected_contact] = 0.25;
                custom.off_thresholds[selected_contact] = 0.125;
                CHECK(is_valid_contact_profile(profile));
                ContactBank bank;
                CHECK(bank.prepare(profile, 48000.0) == Status::Ok);
                CHECK(bank.set_position_target(kManuals[selected_manual], midi(selected_key), 0.5));
                advance(bank, 32);
                for (std::size_t manual = 0; manual < kManualCount; ++manual) {
                    for (std::size_t key = 0; key < kManualKeyCount; ++key) {
                        const auto state = key_state(bank, kManuals[manual], midi(key));
                        const bool selected = manual == selected_manual && key == selected_key;
                        CHECK(state.position == (selected ? 0.5 : 0.0));
                        for (std::size_t contact = 0; contact < kDrawbarCount; ++contact) {
                            const bool expected = selected && contact == selected_contact;
                            CHECK(state.closed[contact] == expected);
                            bool queried = !expected;
                            CHECK(bank.contact_closed(kManuals[manual], midi(key), contact, queried));
                            CHECK(queried == expected);
                        }
                    }
                    for (std::size_t contact = 0; contact < kDrawbarCount; ++contact) {
                        bool any = false;
                        CHECK(bank.any_closed(kManuals[manual], contact, any));
                        CHECK(any == (manual == selected_manual && contact == selected_contact));
                    }
                }
                CHECK(bank.set_key_target(kManuals[selected_manual], midi(selected_key), false));
                advance(bank, 32);
                CHECK(key_state(bank, kManuals[selected_manual], midi(selected_key)) ==
                      ContactKeySnapshot{});
            }
        }
    }
}

void analytical_make_break_timing() {
    const auto profile = make_nominal_contact_profile();
    const auto& key = profile.keys[0][24];
    for (const double rate : kRates) {
        ContactBank bank;
        CHECK(bank.prepare(profile, rate) == Status::Ok);
        CHECK(bank.set_key_target(Manual::Upper, 60, true));
        CHECK(key_state(bank, Manual::Upper, 60).position == 0.0);
        std::array<std::uint32_t, kDrawbarCount> closed_at{};
        const auto make_limit = static_cast<std::uint32_t>(std::ceil(rate * key.press_seconds)) + 2;
        for (std::uint32_t frame = 1; frame <= make_limit; ++frame) {
            const auto previous = key_state(bank, Manual::Upper, 60);
            const bool changed = bank.advance_frame();
            const auto state = key_state(bank, Manual::Upper, 60);
            CHECK(changed == (previous.closed != state.closed));
            const auto expected_position = std::min(1.0L, static_cast<long double>(frame) /
                (static_cast<long double>(rate) * static_cast<long double>(key.press_seconds)));
            CHECK_NEAR(state.position, expected_position, 3.0e-16L);
            for (std::size_t contact = 0; contact < kDrawbarCount; ++contact) {
                if (state.closed[contact] && closed_at[contact] == 0) {
                    closed_at[contact] = frame;
                }
            }
        }
        CHECK(key_state(bank, Manual::Upper, 60).position == 1.0);
        for (std::size_t contact = 0; contact < kDrawbarCount; ++contact) {
            const long double edge = static_cast<long double>(key.on_thresholds[contact]) *
                static_cast<long double>(rate) * static_cast<long double>(key.press_seconds);
            // These nominal fixtures have non-integral edges, so the sample
            // lattice has an unambiguous closed-form first-closure frame.
            CHECK(std::fabs(edge - std::round(edge)) > 0.001L);
            CHECK(closed_at[contact] == static_cast<std::uint32_t>(std::ceil(edge)));
        }

        CHECK(bank.set_key_target(Manual::Upper, 60, false));
        CHECK(key_state(bank, Manual::Upper, 60).position == 1.0);
        std::array<std::uint32_t, kDrawbarCount> opened_at{};
        const auto break_limit = static_cast<std::uint32_t>(std::ceil(rate * key.release_seconds)) + 2;
        for (std::uint32_t frame = 1; frame <= break_limit; ++frame) {
            const auto previous = key_state(bank, Manual::Upper, 60);
            const bool changed = bank.advance_frame();
            const auto state = key_state(bank, Manual::Upper, 60);
            CHECK(changed == (previous.closed != state.closed));
            const auto expected_position = std::max(0.0L, 1.0L - static_cast<long double>(frame) /
                (static_cast<long double>(rate) * static_cast<long double>(key.release_seconds)));
            CHECK_NEAR(state.position, expected_position, 3.0e-16L);
            for (std::size_t contact = 0; contact < kDrawbarCount; ++contact) {
                if (!state.closed[contact] && opened_at[contact] == 0) {
                    opened_at[contact] = frame;
                }
            }
        }
        CHECK(key_state(bank, Manual::Upper, 60) == ContactKeySnapshot{});
        for (std::size_t contact = 0; contact < kDrawbarCount; ++contact) {
            const long double edge = (1.0L - static_cast<long double>(key.off_thresholds[contact])) *
                static_cast<long double>(rate) * static_cast<long double>(key.release_seconds);
            CHECK(std::fabs(edge - std::round(edge)) > 0.001L);
            CHECK(opened_at[contact] == static_cast<std::uint32_t>(std::ceil(edge)));
        }
    }
}

void partial_holds_hysteresis_and_reversal() {
    ContactBank bank;
    CHECK(bank.prepare(make_nominal_contact_profile(), 48000.0) == Status::Ok);
    CHECK(bank.set_position_target(Manual::Upper, 60, 0.5));
    advance(bank, 600);
    auto state = key_state(bank, Manual::Upper, 60);
    CHECK(state.position == 0.5 && state.target == 0.5);
    for (std::size_t contact = 0; contact < kDrawbarCount; ++contact) {
        CHECK(state.closed[contact] == (contact < 4));
    }
    for (unsigned frame = 0; frame < 1000; ++frame) {
        CHECK(!bank.advance_frame());
        CHECK(key_state(bank, Manual::Upper, 60) == state);
    }
    CHECK(bank.set_key_target(Manual::Upper, 60, true));
    advance(bank, 600);
    CHECK(bank.set_position_target(Manual::Upper, 60, 0.5));
    advance(bank, 600);
    state = key_state(bank, Manual::Upper, 60);
    CHECK(state.position == 0.5);
    for (std::size_t contact = 0; contact < kDrawbarCount; ++contact) {
        CHECK(state.closed[contact] == (contact < 5));
    }
    bool held = false;
    double target = -1.0;
    CHECK(bank.key_target(Manual::Upper, 60, held) && held);
    CHECK(bank.position_target(Manual::Upper, 60, target) && target == 0.5);

    CHECK(bank.panic_manual(Manual::Upper));
    CHECK(bank.set_key_target(Manual::Upper, 60, true));
    advance(bank, 100);
    const double press_end = key_state(bank, Manual::Upper, 60).position;
    CHECK_NEAR(press_end, 100.0L / 384.0L, 2.0e-16L);
    CHECK(bank.set_key_target(Manual::Upper, 60, false));
    advance(bank, 17);
    const double release_end = key_state(bank, Manual::Upper, 60).position;
    CHECK_NEAR(release_end, 100.0L / 384.0L - 17.0L / 576.0L, 2.0e-16L);
    CHECK(bank.set_key_target(Manual::Upper, 60, true));
    CHECK(key_state(bank, Manual::Upper, 60).position == release_end);
    advance(bank, 41);
    CHECK_NEAR(key_state(bank, Manual::Upper, 60).position,
               100.0L / 384.0L - 17.0L / 576.0L + 41.0L / 384.0L, 3.0e-16L);

    // An accepted duplicate must not rebase the in-flight segment. This checks
    // hidden future state, not merely unchanged immediate diagnostics.
    ContactBank reference = bank;
    for (unsigned frame = 0; frame < 500; ++frame) {
        CHECK(bank.set_key_target(Manual::Upper, 60, true));
        CHECK(bank.advance_frame() == reference.advance_frame());
        CHECK(snapshots(bank) == snapshots(reference));
    }
    const auto before = key_state(bank, Manual::Upper, 60);
    CHECK(bank.set_key_target(Manual::Upper, 60, false));
    CHECK(bank.set_key_target(Manual::Upper, 60, true));
    CHECK(key_state(bank, Manual::Upper, 60) == before);
    for (unsigned repeat = 0; repeat < 50; ++repeat) {
        CHECK(bank.set_position_target(Manual::Upper, 60, 0.375));
        CHECK(bank.set_key_target(Manual::Upper, 60, true));
        const auto observed = key_state(bank, Manual::Upper, 60);
        CHECK(observed.position == before.position && observed.closed == before.closed);
    }
}

void exact_thresholds_endpoints_and_panic() {
    for (const double rate : kRates) {
        auto profile = make_nominal_contact_profile();
        auto& key = profile.keys[0][24];
        key.press_seconds = 0.001001; // Non-integral frame duration at all rates.
        key.release_seconds = 0.001501;
        key.on_thresholds[0] = 0.5;
        key.off_thresholds[0] = 0.25;
        key.on_thresholds[8] = 1.0;
        key.off_thresholds[8] = 0.0;
        ContactBank bank;
        CHECK(bank.prepare(profile, rate) == Status::Ok);
        CHECK(bank.set_position_target(Manual::Upper, 60, 0.5));
        advance(bank, 200);
        CHECK(key_state(bank, Manual::Upper, 60).closed[0]); // Equality closes.
        CHECK(bank.set_position_target(Manual::Upper, 60, 0.25));
        advance(bank, 200);
        CHECK(!key_state(bank, Manual::Upper, 60).closed[0]); // Equality opens.
        CHECK(bank.panic_manual(Manual::Upper));
        CHECK(bank.set_key_target(Manual::Upper, 60, true));
        const auto make = static_cast<std::uint32_t>(std::ceil(rate * key.press_seconds));
        advance(bank, make - 1);
        CHECK(key_state(bank, Manual::Upper, 60).position < 1.0);
        CHECK(!key_state(bank, Manual::Upper, 60).closed[8]);
        advance(bank, 1);
        CHECK(key_state(bank, Manual::Upper, 60).position == 1.0);
        CHECK(key_state(bank, Manual::Upper, 60).closed[8]);
        CHECK(bank.set_key_target(Manual::Upper, 60, false));
        const auto release = static_cast<std::uint32_t>(std::ceil(rate * key.release_seconds));
        advance(bank, release - 1);
        CHECK(key_state(bank, Manual::Upper, 60).position > 0.0);
        CHECK(key_state(bank, Manual::Upper, 60).closed[8]);
        advance(bank, 1);
        CHECK(key_state(bank, Manual::Upper, 60) == ContactKeySnapshot{});
    }

    auto profile = make_nominal_contact_profile();
    profile.keys[0][24].press_seconds = kMaxContactTravelSeconds;
    profile.keys[0][24].release_seconds = kMaxContactTravelSeconds;
    profile.keys[1][60].press_seconds = kMinContactTravelSeconds;
    profile.keys[1][60].release_seconds = kMinContactTravelSeconds;
    ContactBank bank;
    CHECK(bank.prepare(profile, 96000.0) == Status::Ok);
    CHECK(bank.set_key_target(Manual::Upper, 60, true));
    CHECK(bank.set_key_target(Manual::Lower, 96, true));
    advance(bank, 96002);
    CHECK(key_state(bank, Manual::Upper, 60).position == 1.0);
    CHECK(key_state(bank, Manual::Lower, 96).position == 1.0);
    CHECK(bank.set_key_target(Manual::Upper, 60, false));
    CHECK(bank.set_key_target(Manual::Lower, 96, false));
    advance(bank, 7);
    ContactBank reference = bank;
    CHECK(bank.panic_manual(Manual::Upper));
    CHECK(key_state(bank, Manual::Upper, 60) == ContactKeySnapshot{});
    for (unsigned frame = 0; frame < 1000; ++frame) {
        (void)bank.advance_frame();
        (void)reference.advance_frame();
        CHECK(key_state(bank, Manual::Upper, 60) == ContactKeySnapshot{});
        CHECK(key_state(bank, Manual::Lower, 96) == key_state(reference, Manual::Lower, 96));
    }
    advance(reference, 96002);
    CHECK(key_state(reference, Manual::Upper, 60) == ContactKeySnapshot{});
}

void validation_atomicity_and_owned_profile() {
    const double nan = std::numeric_limits<double>::quiet_NaN();
    const double infinity = std::numeric_limits<double>::infinity();
    auto good = make_nominal_contact_profile();
    ContactBank original;
    CHECK(original.prepare(good, 48000.0) == Status::Ok);
    CHECK(original.set_position_target(Manual::Upper, 36, 0.6));
    CHECK(original.set_key_target(Manual::Lower, 96, true));
    advance(original, 101);
    CHECK(original.set_key_target(Manual::Upper, 36, false));

    const auto reject = [&original](const ContactProfile& invalid) {
        CHECK(!is_valid_contact_profile(invalid));
        ContactBank bank = original;
        CHECK(bank.prepare(invalid, 48000.0) == Status::InvalidProfile);
        same_future(bank, original);
    };
    auto invalid = good;
    invalid.mode = static_cast<ContactMode>(255);
    reject(invalid);
    CHECK(contact_model_id(invalid.mode).empty());
    for (const auto mode : {ContactMode::Ideal, ContactMode::LinearTravel}) {
        for (const double bad : {0.0, -1.0, std::nextafter(kMinContactTravelSeconds, 0.0),
                                std::nextafter(kMaxContactTravelSeconds, infinity), nan, infinity}) {
            invalid = good;
            invalid.mode = mode;
            invalid.keys[1][60].press_seconds = bad;
            reject(invalid);
            invalid.keys[1][60].press_seconds = good.keys[1][60].press_seconds;
            invalid.keys[1][60].release_seconds = bad;
            reject(invalid);
        }
        for (const double bad : {0.0, -1.0, 1.001, nan, infinity}) {
            invalid = good;
            invalid.mode = mode;
            invalid.keys[1][60].on_thresholds[8] = bad;
            reject(invalid);
        }
        for (const double bad : {-0.001, 1.0, nan, infinity}) {
            invalid = good;
            invalid.mode = mode;
            invalid.keys[1][60].off_thresholds[8] = bad;
            reject(invalid);
        }
        invalid = good;
        invalid.mode = mode;
        invalid.keys[1][60].off_thresholds[8] = invalid.keys[1][60].on_thresholds[8];
        reject(invalid);
    }
    for (const double rate : {0.0, -48000.0, 47999.0, 192000.0, nan, infinity}) {
        ContactBank bank = original;
        CHECK(bank.prepare(good, rate) == Status::InvalidSpec);
        same_future(bank, original);
    }
    for (const double target : {-0.001, 1.001, nan, infinity, -infinity}) {
        ContactBank bank = original;
        CHECK(!bank.set_position_target(Manual::Upper, 36, target));
        same_future(bank, original);
    }
    ContactBank bank = original;
    CHECK(!bank.set_position_target(kBadManual, 36, 0.5));
    CHECK(!bank.set_position_target(Manual::Upper, 35, 0.5));
    CHECK(!bank.set_position_target(Manual::Upper, 97, 0.5));
    CHECK(!bank.panic_manual(kBadManual));
    same_future(bank, original);

    // Prepare the comparison against separate authoring memory: two objects
    // accidentally borrowing the same mutated profile would be a weak oracle.
    auto caller_profile = make_nominal_contact_profile();
    const auto reference_profile = caller_profile;
    ContactBank owned;
    ContactBank separate_reference;
    CHECK(owned.prepare(caller_profile, 48000.0) == Status::Ok);
    CHECK(separate_reference.prepare(reference_profile, 48000.0) == Status::Ok);
    CHECK(owned.set_key_target(Manual::Upper, 60, true));
    CHECK(separate_reference.set_key_target(Manual::Upper, 60, true));
    advance(owned, 41);
    advance(separate_reference, 41);
    caller_profile.mode = static_cast<ContactMode>(255);
    for (auto& manual : caller_profile.keys) {
        for (auto& key : manual) {
            key.press_seconds = nan;
            key.release_seconds = infinity;
            key.on_thresholds.fill(nan);
            key.off_thresholds.fill(infinity);
        }
    }
    same_future(owned, separate_reference, 700);
    CHECK(bank.prepare(make_ideal_contact_profile(), 44100.0) == Status::Ok);
    CHECK(bank.mode() == ContactMode::Ideal);
    for (const auto& manual : snapshots(bank)) {
        for (const auto& state : manual) CHECK(state == ContactKeySnapshot{});
    }
}

} // namespace

int main() {
    unprepared_and_checked_queries();
    ideal_legacy_behavior();
    every_contact_has_independent_identity();
    analytical_make_break_timing();
    partial_holds_hysteresis_and_reversal();
    exact_thresholds_endpoints_and_panic();
    validation_atomicity_and_owned_profile();
    std::cout << "Contact bank: 1098 one-hot identities, three-rate analytic edges, "
                 "hysteresis, reversal, endpoints and atomic failures passed.\n";
}
