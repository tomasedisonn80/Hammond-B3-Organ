#include "TestSupport.h"
#include "hammond/ContactBank.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <limits>

namespace {

using namespace hammond;
using Snapshots = std::array<std::array<ContactKeySnapshot, kManualKeyCount>, kManualCount>;
constexpr std::array<double, 3> kRates{44100.0, 48000.0, 96000.0};
constexpr std::array<Manual, 2> kManuals{Manual::Upper, Manual::Lower};
constexpr long double kPositionTolerance = 4e-15L;

struct Evidence {
    std::uint64_t migrations{0};
    std::uint64_t rejected_migrations{0};
    std::uint64_t same_rate_calls{0};
    std::uint64_t position_comparisons{0};
    std::uint64_t contact_comparisons{0};
    std::uint64_t exact_future_frames{0};
    std::uint64_t threshold_samples{0};
    long double maximum_position_error{0.0L};
} evidence;

[[nodiscard]] std::uint32_t midi(std::size_t key) {
    return static_cast<std::uint32_t>(key) + kMinManualMidiNote;
}

[[nodiscard]] ContactKeySnapshot snapshot(const ContactBank& bank, Manual manual,
                                           std::uint32_t note) {
    ContactKeySnapshot result;
    CHECK(bank.key_snapshot(manual, note, result));
    return result;
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

void advance(ContactBank& bank, std::uint32_t frames) {
    for (std::uint32_t frame = 0; frame < frames; ++frame) {
        (void)bank.advance_frame();
    }
}

void near_position(double actual, long double expected) {
    const auto error = std::fabs(static_cast<long double>(actual) - expected);
    evidence.maximum_position_error = std::max(evidence.maximum_position_error, error);
    ++evidence.position_comparisons;
    CHECK_NEAR(actual, expected, kPositionTolerance);
    CHECK(actual >= 0.0 && actual <= 1.0);
}

void migrated(ContactBank& bank, double rate) {
    const auto before = snapshots(bank);
    const auto mode = bank.mode();
    CHECK(bank.reconfigure_sample_rate(rate) == Status::Ok);
    ++evidence.migrations;
    CHECK(bank.sample_rate() == rate);
    CHECK(bank.prepared());
    CHECK(bank.mode() == mode);
    CHECK(snapshots(bank) == before);
}

void same_future(ContactBank actual, ContactBank expected, std::uint32_t frames = 73) {
    CHECK(actual.sample_rate() == expected.sample_rate());
    CHECK(actual.mode() == expected.mode());
    CHECK(actual.prepared() == expected.prepared());
    CHECK(snapshots(actual) == snapshots(expected));
    for (std::uint32_t frame = 0; frame < frames; ++frame) {
        if (frame == 19) {
            CHECK(actual.set_position_target(Manual::Lower, 72,
                actual.mode() == ContactMode::Ideal ? 1.0 : 0.743));
            CHECK(expected.set_position_target(Manual::Lower, 72,
                expected.mode() == ContactMode::Ideal ? 1.0 : 0.743));
        }
        CHECK(actual.advance_frame() == expected.advance_frame());
        CHECK(snapshots(actual) == snapshots(expected));
        ++evidence.exact_future_frames;
    }
}

[[nodiscard]] ContactProfile varied_profile() {
    auto result = make_nominal_contact_profile();
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        for (std::size_t key = 0; key < kManualKeyCount; ++key) {
            auto& item = result.keys[manual][key];
            item.press_seconds = 0.00317 + static_cast<double>(key % 7) * 0.000013 +
                                 static_cast<double>(manual) * 0.000073;
            item.release_seconds = 0.00509 + static_cast<double>(key % 11) * 0.000021 +
                                   static_cast<double>(manual) * 0.000051;
            for (std::size_t contact = 0; contact < kDrawbarCount; ++contact) {
                const auto order = (contact * 4 + key + manual) % kDrawbarCount;
                item.on_thresholds[contact] = 0.0912345 + static_cast<double>(order) * 0.1012345;
                item.off_thresholds[contact] = item.on_thresholds[contact] -
                    (0.0312345 + static_cast<double>(key % 5) * 0.0011);
            }
        }
    }
    CHECK(is_valid_contact_profile(result));
    return result;
}

void prime_varied_histories(ContactBank& bank, double rate) {
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        for (std::size_t key = 0; key < kManualKeyCount; ++key) {
            if (key % 4 != 3) {
                CHECK(bank.set_key_target(kManuals[manual], midi(key), true));
            }
        }
    }
    advance(bank, static_cast<std::uint32_t>(std::ceil(rate * 0.004)) + 2);
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        for (std::size_t key = 0; key < kManualKeyCount; ++key) {
            const double target = key % 4 == 0 ? 0.0 :
                                  key % 4 == 1 ? 0.51 :
                                  key % 4 == 2 ? 1.0 : 0.88;
            CHECK(bank.set_position_target(kManuals[manual], midi(key), target));
        }
    }
    advance(bank, static_cast<std::uint32_t>(std::ceil(rate * 0.00291)) + 1);
    // Some keys are releasing; some retain a hysteretic partial hold; others
    // remain fully held. Rearticulate the fourth group from its current travel.
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        for (std::size_t key = 3; key < kManualKeyCount; key += 4) {
            CHECK(bank.set_position_target(kManuals[manual], midi(key), 0.973));
        }
    }
    advance(bank, 3);
}

// Analytic monotone-segment distance and threshold passage, not the module's
// per-sample recurrence or segment counter. Each check starts from an observed
// preserved boundary; time after that boundary is independently known.
void check_segment(const ContactBank& bank, const Snapshots& start,
                   const ContactProfile& profile, double rate, std::uint32_t frames) {
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        for (std::size_t key = 0; key < kManualKeyCount; ++key) {
            const auto& before = start[manual][key];
            const auto actual = snapshot(bank, kManuals[manual], midi(key));
            const auto& parameters = profile.keys[manual][key];
            const bool increasing = before.target > before.position;
            const bool decreasing = before.target < before.position;
            const long double elapsed = static_cast<long double>(frames) /
                                        static_cast<long double>(rate);
            const long double distance = elapsed / static_cast<long double>(
                increasing ? parameters.press_seconds : parameters.release_seconds);
            const long double expected = increasing ?
                std::min(static_cast<long double>(before.target),
                         static_cast<long double>(before.position) + distance) :
                decreasing ? std::max(static_cast<long double>(before.target),
                                      static_cast<long double>(before.position) - distance) :
                             static_cast<long double>(before.position);
            near_position(actual.position, expected);
            CHECK(actual.target == before.target);
            for (std::size_t contact = 0; contact < kDrawbarCount; ++contact) {
                // These varied thresholds deliberately avoid the tested time
                // grid. Dedicated quarter-sample fixtures below check edge time.
                const bool connected = increasing ?
                    before.closed[contact] || expected >= parameters.on_thresholds[contact] :
                    decreasing ? before.closed[contact] &&
                                 expected > parameters.off_thresholds[contact] :
                                 before.closed[contact];
                CHECK(actual.closed[contact] == connected);
                ++evidence.contact_comparisons;
            }
        }
    }
}

void every_pair_preserves_mixed_motion_and_owned_parameters() {
    for (const double before_rate : kRates) {
        for (const double after_rate : kRates) {
            auto caller_profile = varied_profile();
            const auto owned_parameters = caller_profile;
            ContactBank bank;
            CHECK(bank.prepare(caller_profile, before_rate) == Status::Ok);
            CHECK(bank.sample_rate() == before_rate);
            prime_varied_histories(bank, before_rate);
            const auto start = snapshots(bank);
            CHECK(start[0][0].target == 0.0 && start[0][0].position > 0.0);
            CHECK(start[1][1].position == 0.51);
            CHECK(start[0][2].position == 1.0);
            CHECK(start[1][3].position < start[1][3].target);
            // Reconfiguration must use the installed values, not caller memory.
            for (auto& manual : caller_profile.keys) {
                for (auto& key : manual) {
                    key.press_seconds = 1.0;
                    key.release_seconds = 1.0;
                    key.on_thresholds.fill(0.95);
                    key.off_thresholds.fill(0.9);
                }
            }
            caller_profile.keys[1][60].press_seconds = std::numeric_limits<double>::quiet_NaN();
            migrated(bank, after_rate);
            const auto frames = static_cast<std::uint32_t>(std::ceil(after_rate * 0.006)) + 3;
            for (std::uint32_t frame = 1; frame <= frames; ++frame) {
                (void)bank.advance_frame();
                check_segment(bank, start, owned_parameters, after_rate, frame);
            }
            const auto final = snapshots(bank);
            for (const auto& manual : final) {
                for (const auto& key : manual) {
                    CHECK(key.position == key.target);
                }
            }
        }
    }
}

void ideal_pairs_preserve_immediate_semantics() {
    for (const double before_rate : kRates) {
        for (const double after_rate : kRates) {
            auto profile = varied_profile();
            profile.mode = ContactMode::Ideal;
            ContactBank bank;
            CHECK(bank.prepare(profile, before_rate) == Status::Ok);
            for (std::size_t manual = 0; manual < kManualCount; ++manual) {
                for (std::size_t key = 0; key < kManualKeyCount; ++key) {
                    CHECK(bank.set_key_target(kManuals[manual], midi(key),
                                               (key + manual) % 3 != 0));
                }
            }
            const auto before = snapshots(bank);
            migrated(bank, after_rate);
            advance(bank, 31);
            CHECK(snapshots(bank) == before);
            for (std::size_t manual = 0; manual < kManualCount; ++manual) {
                for (std::size_t key = 0; key < kManualKeyCount; ++key) {
                    const bool next = !before[manual][key].closed[0];
                    CHECK(bank.set_key_target(kManuals[manual], midi(key), next));
                    const auto result = snapshot(bank, kManuals[manual], midi(key));
                    CHECK(result.position == (next ? 1.0 : 0.0));
                    CHECK(result.target == result.position);
                    for (const bool closed : result.closed) {
                        CHECK(closed == next);
                        ++evidence.contact_comparisons;
                    }
                    CHECK(!bank.set_position_target(kManuals[manual], midi(key), 0.5));
                    CHECK(snapshot(bank, kManuals[manual], midi(key)) == result);
                }
            }
        }
    }
}

void exact_same_rate_no_op_preserves_segment_origin() {
    for (const double rate : kRates) {
        ContactBank bank;
        CHECK(bank.prepare(varied_profile(), rate) == Status::Ok);
        prime_varied_histories(bank, rate);
        ContactBank untouched = bank;
        for (std::uint32_t frame = 0; frame < 2048; ++frame) {
            if (frame % 43 == 0) {
                const double target = (frame / 43) % 2 == 0 ? 0.137 : 0.873;
                for (const auto manual : kManuals) {
                    for (const std::uint32_t note : {36U, 69U, 96U}) {
                        CHECK(bank.set_position_target(manual, note, target));
                        CHECK(untouched.set_position_target(manual, note, target));
                    }
                }
            }
            for (int repetition = 0; repetition < 2; ++repetition) {
                CHECK(bank.reconfigure_sample_rate(rate) == Status::Ok);
                ++evidence.same_rate_calls;
                CHECK(snapshots(bank) == snapshots(untouched));
            }
            CHECK(bank.advance_frame() == untouched.advance_frame());
            CHECK(snapshots(bank) == snapshots(untouched));
            ++evidence.exact_future_frames;
        }
    }
}

void each_threshold_keeps_its_new_sample_coordinate() {
    constexpr double press_seconds = 0.01031;
    constexpr double release_seconds = 0.02027;
    constexpr std::uint32_t old_press_frames = 37;
    constexpr std::uint32_t old_release_frames = 23;
    for (const double before_rate : kRates) {
        for (const double after_rate : kRates) {
            for (const bool release : {false, true}) {
                auto profile = make_nominal_contact_profile();
                auto& key = profile.keys[1][60];
                key.press_seconds = press_seconds;
                key.release_seconds = release_seconds;
                const long double origin = release ?
                    1.0L - static_cast<long double>(old_release_frames) /
                        (static_cast<long double>(before_rate) * release_seconds) :
                    static_cast<long double>(old_press_frames) /
                        (static_cast<long double>(before_rate) * press_seconds);
                std::array<std::uint32_t, kDrawbarCount> crossing{};
                for (std::size_t contact = 0; contact < kDrawbarCount; ++contact) {
                    const auto order = (contact * 4) % kDrawbarCount;
                    const auto whole = static_cast<std::uint32_t>(7 + order * 13);
                    crossing[contact] = whole + 1;
                    const long double distance = (static_cast<long double>(whole) + 0.25L) /
                        (static_cast<long double>(after_rate) *
                         (release ? release_seconds : press_seconds));
                    if (release) {
                        key.off_thresholds[contact] = static_cast<double>(origin - distance);
                        key.on_thresholds[contact] = (key.off_thresholds[contact] + 1.0) * 0.5;
                    } else {
                        key.on_thresholds[contact] = static_cast<double>(origin + distance);
                        key.off_thresholds[contact] = key.on_thresholds[contact] * 0.5;
                    }
                }
                ContactBank bank;
                CHECK(bank.prepare(profile, before_rate) == Status::Ok);
                CHECK(bank.set_key_target(Manual::Lower, 96, true));
                if (release) {
                    advance(bank, static_cast<std::uint32_t>(
                        std::ceil(before_rate * press_seconds)) + 2);
                    CHECK(snapshot(bank, Manual::Lower, 96).position == 1.0);
                    CHECK(bank.set_key_target(Manual::Lower, 96, false));
                    advance(bank, old_release_frames);
                } else {
                    advance(bank, old_press_frames);
                }
                near_position(snapshot(bank, Manual::Lower, 96).position, origin);
                migrated(bank, after_rate);
                for (std::uint32_t frame = 0; frame <= 114; ++frame) {
                    const auto state = snapshot(bank, Manual::Lower, 96);
                    for (std::size_t contact = 0; contact < kDrawbarCount; ++contact) {
                        const bool crossed = frame >= crossing[contact];
                        CHECK(state.closed[contact] == (release ? !crossed : crossed));
                        ++evidence.threshold_samples;
                    }
                    (void)bank.advance_frame();
                }
            }
        }
    }
}

void repeated_boundaries_preserve_partial_hysteresis() {
    auto profile = make_nominal_contact_profile();
    ContactBank bank;
    CHECK(bank.prepare(profile, 48000.0) == Status::Ok);
    CHECK(bank.set_key_target(Manual::Upper, 60, true));
    CHECK(bank.set_position_target(Manual::Lower, 60, 0.5));
    advance(bank, 500);
    CHECK(bank.set_position_target(Manual::Upper, 60, 0.5));
    advance(bank, 500);
    const auto held = snapshots(bank);
    CHECK(held[0][24].position == held[1][24].position);
    CHECK(held[0][24].closed[4] && !held[1][24].closed[4]);
    for (int repetition = 0; repetition < 5; ++repetition) {
        for (const double rate : kRates) {
            migrated(bank, rate);
            CHECK(snapshots(bank) == held);
        }
    }
    CHECK(bank.set_position_target(Manual::Upper, 60, 0.437));
    CHECK(bank.set_position_target(Manual::Lower, 60, 0.437));
    advance(bank, 7);
    auto current = snapshots(bank);
    // Reversal before returning to rest must start from the incomplete release.
    CHECK(current[0][24].position > current[0][24].target);
    CHECK(bank.set_position_target(Manual::Upper, 60, 0.731));
    CHECK(bank.set_position_target(Manual::Lower, 60, 0.731));
    current = snapshots(bank);
    migrated(bank, 44100.0);
    for (std::uint32_t frame = 1; frame <= 137; ++frame) {
        (void)bank.advance_frame();
        check_segment(bank, current, profile, 44100.0, frame);
    }
}

void supported_duration_extremes_and_endpoint_clamping() {
    for (const double before_rate : kRates) {
        for (const double after_rate : kRates) {
            auto profile = make_nominal_contact_profile();
            auto& fast = profile.keys[0][0];
            fast.press_seconds = kMinContactTravelSeconds;
            fast.release_seconds = kMinContactTravelSeconds;
            fast.on_thresholds[0] = 0.498;
            fast.off_thresholds[0] = 0.495;
            auto& slow = profile.keys[1][60];
            slow.press_seconds = kMaxContactTravelSeconds;
            slow.release_seconds = kMaxContactTravelSeconds;
            ContactBank bank;
            CHECK(bank.prepare(profile, before_rate) == Status::Ok);
            CHECK(bank.set_position_target(Manual::Upper, 36, 0.5));
            CHECK(bank.set_position_target(Manual::Lower, 96, 0.000137));
            advance(bank, 1);
            const auto start = snapshots(bank);
            migrated(bank, after_rate);
            for (std::uint32_t frame = 1; frame <= 20; ++frame) {
                (void)bank.advance_frame();
                check_segment(bank, start, profile, after_rate, frame);
            }
            CHECK(snapshot(bank, Manual::Upper, 36).position == 0.5);
            CHECK(snapshot(bank, Manual::Lower, 96).position == 0.000137);
            CHECK(bank.set_position_target(Manual::Upper, 36, 0.49));
            CHECK(bank.set_key_target(Manual::Lower, 96, false));
            const auto release_start = snapshots(bank);
            migrated(bank, before_rate);
            (void)bank.advance_frame();
            check_segment(bank, release_start, profile, before_rate, 1);
            const auto fast_released = snapshot(bank, Manual::Upper, 36);
            CHECK(fast_released.position == 0.49);
            CHECK(!fast_released.closed[0]);
            advance(bank, 20);
            CHECK(snapshot(bank, Manual::Lower, 96).position == 0.0);
        }
    }
    // Bound the longest full-travel segment after a rate change, with explicit
    // exact arrival. The implementation's old frame counter must not survive.
    auto profile = make_nominal_contact_profile();
    profile.keys[0][0].press_seconds = 1.0;
    ContactBank bank;
    CHECK(bank.prepare(profile, 44100.0) == Status::Ok);
    CHECK(bank.set_key_target(Manual::Upper, 36, true));
    advance(bank, 100);
    const double start = snapshot(bank, Manual::Upper, 36).position;
    migrated(bank, 96000.0);
    const auto remaining = static_cast<std::uint32_t>(
        std::ceil((1.0L - static_cast<long double>(start)) * 96000.0L));
    CHECK(remaining < 96001);
    advance(bank, remaining - 1);
    CHECK(snapshot(bank, Manual::Upper, 36).position < 1.0);
    advance(bank, 2);
    CHECK(snapshot(bank, Manual::Upper, 36).position == 1.0);
}

void invalid_rates_and_prepare_are_atomic() {
    const std::array<double, 16> invalid{
        0.0, -0.0, -1.0, 1.0, 32000.0, 88200.0, 192000.0,
        std::nextafter(44100.0, 0.0), std::nextafter(44100.0, 48000.0),
        std::nextafter(48000.0, 44100.0), std::nextafter(96000.0, 192000.0),
        std::numeric_limits<double>::denorm_min(), std::numeric_limits<double>::max(),
        std::numeric_limits<double>::infinity(), -std::numeric_limits<double>::infinity(),
        std::numeric_limits<double>::quiet_NaN()};
    ContactBank empty;
    CHECK(empty.sample_rate() == 0.0 && !empty.prepared());
    for (const double rate : invalid) {
        CHECK(empty.reconfigure_sample_rate(rate) == Status::NotPrepared);
        ++evidence.rejected_migrations;
        CHECK(empty.sample_rate() == 0.0 && !empty.prepared());
    }
    for (const double rate : kRates) {
        CHECK(empty.reconfigure_sample_rate(rate) == Status::NotPrepared);
        ++evidence.rejected_migrations;
        CHECK(empty.sample_rate() == 0.0 && !empty.prepared());
    }
    CHECK(empty.prepare(make_nominal_contact_profile(), 32000.0) == Status::InvalidSpec);
    CHECK(empty.sample_rate() == 0.0 && !empty.prepared());

    for (const double rate : kRates) {
        for (const ContactMode mode : {ContactMode::Ideal, ContactMode::LinearTravel}) {
            auto profile = varied_profile();
            profile.mode = mode;
            ContactBank bank;
            CHECK(bank.prepare(profile, rate) == Status::Ok);
            if (mode == ContactMode::Ideal) {
                CHECK(bank.set_key_target(Manual::Upper, 36, true));
                CHECK(bank.set_key_target(Manual::Lower, 96, true));
            } else {
                prime_varied_histories(bank, rate);
            }
            const ContactBank expected = bank;
            for (const double invalid_rate : invalid) {
                CHECK(bank.reconfigure_sample_rate(invalid_rate) == Status::InvalidSpec);
                ++evidence.rejected_migrations;
                CHECK(bank.sample_rate() == rate);
                same_future(bank, expected);
            }
            auto bad_profile = profile;
            bad_profile.keys[1][60].release_seconds = std::numeric_limits<double>::quiet_NaN();
            CHECK(bank.prepare(bad_profile, 96000.0) == Status::InvalidProfile);
            same_future(bank, expected);
            CHECK(bank.prepare(profile, 32000.0) == Status::InvalidSpec);
            same_future(bank, expected);
            CHECK(bank.sample_rate() == rate);
            CHECK(bank.prepare(profile, 96000.0) == Status::Ok);
            CHECK(bank.sample_rate() == 96000.0);
            for (const auto& manual : snapshots(bank)) {
                for (const auto& key : manual) {
                    CHECK(key == ContactKeySnapshot{});
                }
            }
        }
    }
}

} // namespace

int main() {
    every_pair_preserves_mixed_motion_and_owned_parameters();
    ideal_pairs_preserve_immediate_semantics();
    exact_same_rate_no_op_preserves_segment_origin();
    each_threshold_keeps_its_new_sample_coordinate();
    repeated_boundaries_preserve_partial_hysteresis();
    supported_duration_extremes_and_endpoint_clamping();
    invalid_rates_and_prepare_are_atomic();
    std::cout << "contact rate lifecycle: " << evidence.migrations
              << " tracked migrations, " << evidence.rejected_migrations
              << " rejected migrations, " << evidence.same_rate_calls
              << " same-rate no-ops, " << evidence.position_comparisons
              << " position and " << evidence.contact_comparisons
              << " contact comparisons, " << evidence.exact_future_frames
              << " exact future frames, " << evidence.threshold_samples
              << " threshold samples; maximum position error="
              << std::setprecision(std::numeric_limits<long double>::max_digits10)
              << evidence.maximum_position_error << '\n';
}
