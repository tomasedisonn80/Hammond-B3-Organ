#include "hammond/Engine.h"
#include "TestSupport.h"

#include <algorithm>
#include <array>
#include <bit>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numbers>
#include <span>
#include <vector>

namespace {

using namespace hammond;

constexpr std::array<double, 3> kRates{44100.0, 48000.0, 96000.0};
constexpr std::array<ContactMode, 2> kModes{ContactMode::Ideal, ContactMode::LinearTravel};
constexpr std::uint32_t kBlock = 257;
constexpr std::uint64_t kOrigin = 1000003;
constexpr std::uint64_t kSeed = 0xd73a6912bc8e450fULL;
constexpr long double kPhaseTolerance = 3e-11L;
constexpr long double kPositionTolerance = 3e-13L;
constexpr long double kReadinessTolerance = 3e-12L;

struct Measurements {
    std::size_t pair_scenarios{};
    std::size_t rejected_changes{};
    std::size_t same_rate_calls{};
    std::size_t snapshots{};
    std::size_t phase_checks{};
    std::size_t position_checks{};
    std::size_t contact_bit_checks{};
    std::size_t readiness_checks{};
    std::size_t sample_oracles{};
    std::size_t exact_audio_frames{};
    std::size_t mixed_segments{};
    std::size_t ownership_cases{};
    std::size_t detector_edge_scenarios{};
    long double max_phase_error{};
    long double max_position_error{};
    long double max_readiness_error{};
    long double max_sample_error{};
} measured;

struct Snapshot {
    bool prepared{};
    double rate{};
    std::uint64_t clock{};
    std::size_t active_total{};
    std::array<std::size_t, kManualCount> active{};
    std::array<std::array<bool, kManualKeyCount>, kManualCount> held{};
    std::array<std::array<ContactKeySnapshot, kManualKeyCount>, kManualCount> contacts{};
    std::array<double, kToneSourceCount> phases{};
    ControlSnapshot controls{};
    double expression{};
    ContactMode mode{};
    PercussionRoutingDiagnostics percussion{};
    [[nodiscard]] bool operator==(const Snapshot&) const noexcept = default;
};

Manual manual_at(std::size_t index) {
    return static_cast<Manual>(index);
}

std::uint8_t note_at(std::size_t key) {
    return static_cast<std::uint8_t>(key + kMinManualMidiNote);
}

Snapshot inspect(const Engine& engine) {
    ++measured.snapshots;
    Snapshot result;
    result.prepared = engine.prepared();
    result.rate = engine.sample_rate();
    result.clock = engine.frame_clock();
    result.active_total = engine.active_key_count();
    result.controls = engine.controls_snapshot();
    result.expression = engine.expression();
    result.mode = engine.contact_mode();
    result.percussion = engine.percussion_diagnostics();
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        result.active[manual] = engine.active_key_count(manual_at(manual));
        for (std::size_t key = 0; key < kManualKeyCount; ++key) {
            result.held[manual][key] = engine.key_down(manual_at(manual), note_at(key));
            CHECK(engine.contact_snapshot(manual_at(manual), note_at(key),
                                          result.contacts[manual][key]) == result.prepared);
        }
        if (result.prepared) {
            DrawbarBank selected = DrawbarBank::A;
            bool enabled = false;
            CHECK(engine.selected_bank(manual_at(manual), selected));
            CHECK(engine.route_enabled(manual_at(manual), enabled));
            CHECK(selected == result.controls.selected_banks[manual]);
            CHECK(enabled == result.controls.route_enabled[manual]);
            for (std::size_t drawbar = 0; drawbar < kDrawbarCount; ++drawbar) {
                std::uint8_t position = 255;
                CHECK(engine.drawbar_position(manual_at(manual), drawbar, position));
                CHECK(position == result.controls.drawbars[manual]
                    [static_cast<std::size_t>(selected)][drawbar]);
                for (std::size_t bank = 0; bank < kDrawbarBankCount; ++bank) {
                    CHECK(engine.bank_drawbar_position(manual_at(manual),
                        static_cast<DrawbarBank>(bank), drawbar, position));
                    CHECK(position == result.controls.drawbars[manual][bank][drawbar]);
                }
            }
        }
    }
    CHECK(result.active_total == result.active[0] + result.active[1]);
    CHECK(result.expression == result.controls.expression);
    for (std::size_t source = 0; source < kToneSourceCount; ++source) {
        CHECK(engine.source_phase_turns(static_cast<ToneId>(source + 1),
                                        result.phases[source]) == result.prepared);
    }
    return result;
}

void unchanged_dynamics(const Snapshot& before, const Snapshot& after) {
    CHECK(after.prepared == before.prepared);
    CHECK(after.rate == before.rate);
    CHECK(after.clock == before.clock);
    CHECK(after.active_total == before.active_total);
    CHECK(after.active == before.active);
    CHECK(after.held == before.held);
    CHECK(after.contacts == before.contacts);
    CHECK(after.phases == before.phases);
    CHECK(after.mode == before.mode);
    CHECK(after.percussion.readiness == before.percussion.readiness);
    CHECK(after.percussion.physical_detector == before.percussion.physical_detector);
}

void migrate(Engine& engine, double rate) {
    auto expected = inspect(engine);
    CHECK(engine.reconfigure_sample_rate(rate) == Status::Ok);
    expected.rate = rate;
    CHECK(inspect(engine) == expected);
}

void flush(Engine& engine, std::span<const Event> events = {}) {
    std::array<float, 3> untouched{13.0F, -7.0F, 19.0F};
    const auto original = untouched;
    const auto result = engine.process(0, untouched, events);
    CHECK(result.status == Status::Ok);
    CHECK(result.events_consumed == events.size());
    CHECK(untouched == original);
}

void discard(Engine& engine, std::uint32_t frames) {
    while (frames != 0) {
        const auto count = std::min(frames, kBlock);
        const auto result = engine.process(count, {}, {});
        CHECK(result.status == Status::Ok);
        CHECK(result.events_consumed == 0);
        frames -= count;
    }
}

void exact_audio(std::span<const float> actual, std::span<const float> expected) {
    CHECK(actual.size() == expected.size());
    for (std::size_t frame = 0; frame < actual.size(); ++frame) {
        CHECK(std::bit_cast<std::uint32_t>(actual[frame]) ==
              std::bit_cast<std::uint32_t>(expected[frame]));
        ++measured.exact_audio_frames;
    }
}

ConsoleModel varied_model(ContactMode mode) {
    auto model = make_nominal_console_model();
    model.contacts.mode = mode;
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        for (std::size_t key = 0; key < kManualKeyCount; ++key) {
            auto& profile = model.contacts.keys[manual][key];
            profile.press_seconds = 0.0067 + 0.000031 * static_cast<double>(key) +
                                    0.0013 * static_cast<double>(manual);
            profile.release_seconds = 0.0109 + 0.000043 * static_cast<double>(key) +
                                      0.0021 * static_cast<double>(manual);
            for (std::size_t contact = 0; contact < kDrawbarCount; ++contact) {
                // Deliberately nonidentical per-key thresholds, away from the
                // short test segments' exact sample boundaries.
                const auto offset = 0.00007 * static_cast<double>((key + manual) % 7);
                profile.on_thresholds[contact] = 0.1157 +
                    0.1001 * static_cast<double>(contact) + offset;
                profile.off_thresholds[contact] = 0.0353 +
                    0.1001 * static_cast<double>(contact) + offset;
            }
        }
    }
    model.percussion = {0.317, 0.0719, 0.0237, 0.83, 0.39, 1.27, 0.67};
    return model;
}

ControlSnapshot varied_controls(bool alternate = false) {
    ControlSnapshot controls;
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        for (std::size_t bank = 0; bank < kDrawbarBankCount; ++bank) {
            for (std::size_t drawbar = 0; drawbar < kDrawbarCount; ++drawbar) {
                controls.drawbars[manual][bank][drawbar] = static_cast<std::uint8_t>(
                    (3 * manual + 2 * bank + drawbar + (alternate ? 2U : 0U)) % 9);
            }
        }
    }
    controls.selected_banks = {DrawbarBank::B, alternate ? DrawbarBank::B : DrawbarBank::A};
    controls.expression = alternate ? 0.43 : 0.73;
    controls.percussion = {true,
        alternate ? PercussionHarmonic::Third : PercussionHarmonic::Second,
        alternate ? PercussionVolume::Soft : PercussionVolume::Normal,
        alternate ? PercussionDecay::Fast : PercussionDecay::Slow};
    return controls;
}

Engine moving_engine(const RuntimeProfile& profile, const ConsoleModel& model,
                     double rate, bool alternate = false) {
    Engine engine;
    CHECK(engine.prepare(profile, {rate, kBlock, kSeed, kOrigin}, model) == Status::Ok);
    CHECK(engine.restore_controls(varied_controls(alternate)));
    std::vector<Event> events;
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        for (std::size_t key = 0; key < kManualKeyCount; ++key) {
            if (key % 3 != 1) {
                events.push_back({0, EventType::NoteOn, manual_at(manual), note_at(key), 103});
            }
        }
    }
    flush(engine, events);
    discard(engine, static_cast<std::uint32_t>(std::ceil(rate * 0.037)));
    events.clear();
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        for (std::size_t key = 0; key < kManualKeyCount; ++key) {
            if (key % 3 == 1) {
                events.push_back({0, EventType::NoteOn, manual_at(manual), note_at(key), 17});
            } else if (key % 3 == 2) {
                events.push_back({0, EventType::NoteOff, manual_at(manual), note_at(key), 0});
            }
        }
    }
    flush(engine, events);
    discard(engine, static_cast<std::uint32_t>(std::ceil(rate * 0.00173)));
    CHECK(engine.percussion_diagnostics().routed_detector);
    CHECK(engine.percussion_diagnostics().readiness < 1.0);
    if (model.contacts.mode == ContactMode::LinearTravel) {
        const auto state = inspect(engine);
        for (std::size_t manual = 0; manual < kManualCount; ++manual) {
            for (std::size_t key = 0; key < kManualKeyCount; ++key) {
                const auto& contact = state.contacts[manual][key];
                if (key % 3 == 0) {
                    CHECK(contact.position == 1.0 && contact.target == 1.0);
                } else {
                    CHECK(contact.position > 0.0 && contact.position < 1.0);
                    CHECK(contact.target == (key % 3 == 1 ? 1.0 : 0.0));
                }
            }
        }
    }
    return engine;
}

void phase_oracle(const Snapshot& origin, const Snapshot& actual,
                  const RuntimeProfile& profile, long double elapsed_seconds) {
    for (std::size_t source = 0; source < kToneSourceCount; ++source) {
        const auto expected = std::fmod(static_cast<long double>(origin.phases[source]) +
            static_cast<long double>(profile.sources[source].frequency_hz) * elapsed_seconds, 1.0L);
        CHECK(actual.phases[source] >= 0.0 && actual.phases[source] < 1.0);
        const auto difference = std::fabs(static_cast<long double>(actual.phases[source]) - expected);
        const auto error = std::min(difference, 1.0L - difference);
        measured.max_phase_error = std::max(measured.max_phase_error, error);
        ++measured.phase_checks;
        CHECK_NEAR(error, 0.0L, kPhaseTolerance);
    }
}

void contact_oracle(const Snapshot& origin, const Snapshot& actual,
                    const ConsoleModel& model, long double elapsed_seconds) {
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        for (std::size_t key = 0; key < kManualKeyCount; ++key) {
            const auto& start = origin.contacts[manual][key];
            const auto& end = actual.contacts[manual][key];
            const auto& parameters = model.contacts.keys[manual][key];
            auto expected = static_cast<long double>(start.position);
            if (model.contacts.mode == ContactMode::LinearTravel) {
                if (start.target > start.position) {
                    expected = std::min(static_cast<long double>(start.target),
                        expected + elapsed_seconds / parameters.press_seconds);
                } else if (start.target < start.position) {
                    expected = std::max(static_cast<long double>(start.target),
                        expected - elapsed_seconds / parameters.release_seconds);
                }
            }
            const auto error = std::fabs(static_cast<long double>(end.position) - expected);
            measured.max_position_error = std::max(measured.max_position_error, error);
            ++measured.position_checks;
            CHECK_NEAR(end.position, expected, kPositionTolerance);
            CHECK(end.target == start.target);
            CHECK(actual.held[manual][key] == origin.held[manual][key]);
            for (std::size_t contact = 0; contact < kDrawbarCount; ++contact) {
                bool closed = start.closed[contact];
                if (model.contacts.mode == ContactMode::LinearTravel) {
                    if (expected >= parameters.on_thresholds[contact]) {
                        closed = true;
                    } else if (expected <= parameters.off_thresholds[contact]) {
                        closed = false;
                    }
                }
                ++measured.contact_bit_checks;
                CHECK(end.closed[contact] == closed);
            }
        }
    }
}

long double readiness_after(long double q, long double seconds, bool detector,
                            const PercussionProfile& profile, PercussionDecay decay) {
    // Independent continuous-time solutions over a known constant-detector
    // interval; no second per-sample implementation of the production recurrence.
    if (detector) {
        const auto tau = decay == PercussionDecay::Fast ?
            profile.fast_decay_seconds : profile.slow_decay_seconds;
        return q * std::exp(-seconds / tau);
    }
    return 1.0L - (1.0L - q) * std::exp(-seconds / profile.recovery_seconds);
}

void readiness_oracle(const Snapshot& actual, long double expected) {
    const auto error = std::fabs(static_cast<long double>(actual.percussion.readiness) - expected);
    measured.max_readiness_error = std::max(measured.max_readiness_error, error);
    ++measured.readiness_checks;
    CHECK_NEAR(actual.percussion.readiness, expected, kReadinessTolerance);
}

long double current_sample(const Snapshot& state, const RuntimeProfile& profile,
                           const ConsoleModel& model) {
    std::array<long double, kToneSourceCount> sources{};
    for (std::size_t source = 0; source < sources.size(); ++source) {
        sources[source] = profile.sources[source].peak_amplitude *
            std::sin(2.0L * std::numbers::pi_v<long double> * state.phases[source]);
    }
    const auto& controls = state.controls;
    const bool eligible = controls.percussion.enabled && controls.route_enabled[0] &&
                          controls.selected_banks[0] == DrawbarBank::B;
    const auto sustain_gain = eligible && controls.percussion.volume == PercussionVolume::Normal ?
        model.percussion.normal_sustain_gain : 1.0;
    const auto percussion_gain = eligible ? state.percussion.readiness *
        (controls.percussion.volume == PercussionVolume::Normal ?
            model.percussion.normal_gain : model.percussion.soft_gain) *
        (controls.percussion.decay == PercussionDecay::Fast ?
            model.percussion.fast_gain_multiplier : 1.0) : 0.0;
    const std::size_t percussion_contact =
        controls.percussion.harmonic == PercussionHarmonic::Second ? 3U : 4U;
    long double sum = 0.0L;
    // Sum physical branches directly. This is deliberately independent of the
    // engine's cached per-source accumulation order and uses the public map.
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        if (!controls.route_enabled[manual]) {
            continue;
        }
        const auto bank = static_cast<std::size_t>(controls.selected_banks[manual]);
        for (std::size_t key = 0; key < kManualKeyCount; ++key) {
            for (std::size_t contact = 0; contact < kDrawbarCount; ++contact) {
                if (!state.contacts[manual][key].closed[contact]) {
                    continue;
                }
                const auto source = static_cast<std::size_t>(profile.manual_map[key][contact] - 1);
                if (!(manual == 0 && eligible && contact == 8)) {
                    sum += sources[source] * profile.drawbar_gains[controls.drawbars[manual][bank][contact]] *
                           (manual == 0 ? sustain_gain : 1.0);
                }
                if (manual == 0 && eligible && contact == percussion_contact) {
                    sum += sources[source] * percussion_gain;
                }
            }
        }
    }
    return sum * profile.output_gain * controls.expression;
}

void sample_oracle(float actual, long double expected) {
    const auto error = std::fabs(static_cast<long double>(actual) - expected);
    measured.max_sample_error = std::max(measured.max_sample_error, error);
    ++measured.sample_oracles;
    // Covers one final float conversion and differing legal sum/trig rounding.
    CHECK_NEAR(actual, expected, 2e-6L * std::max(1.0L, std::fabs(expected)));
}

void all_rate_pairs(const RuntimeProfile& profile) {
    for (const auto mode : kModes) {
        const auto model = varied_model(mode);
        for (const auto before_rate : kRates) {
            for (const auto after_rate : kRates) {
                for (const bool pending_controls : {false, true}) {
                    ++measured.pair_scenarios;
                    auto engine = moving_engine(profile, model, before_rate);
                    if (pending_controls) {
                        const auto before_restore = inspect(engine);
                        CHECK(engine.restore_controls(varied_controls(true)));
                        unchanged_dynamics(before_restore, inspect(engine));
                    }
                    const auto origin = inspect(engine);
                    auto old_rate_copy = engine;
                    migrate(engine, after_rate);
                    const auto no_time = inspect(engine);
                    flush(engine);
                    CHECK(inspect(engine) == no_time);
                    std::array<float, 1> changed{}, original{};
                    CHECK(engine.process(1, changed, {}));
                    CHECK(old_rate_copy.process(1, original, {}));
                    exact_audio(changed, original);
                    sample_oracle(changed[0], current_sample(origin, profile, model));
                    auto actual = inspect(engine);
                    auto seconds = 1.0L / after_rate;
                    phase_oracle(origin, actual, profile, seconds);
                    contact_oracle(origin, actual, model, seconds);
                    readiness_oracle(actual, readiness_after(origin.percussion.readiness,
                        seconds, true, model.percussion, origin.controls.percussion.decay));
                    CHECK(actual.clock == origin.clock + 1);
                    discard(engine, 193);
                    seconds = 194.0L / after_rate;
                    actual = inspect(engine);
                    phase_oracle(origin, actual, profile, seconds);
                    contact_oracle(origin, actual, model, seconds);
                    readiness_oracle(actual, readiness_after(origin.percussion.readiness,
                        seconds, true, model.percussion, origin.controls.percussion.decay));
                    CHECK(actual.clock == origin.clock + 194);
                    CHECK(actual.controls == origin.controls);
                    CHECK(actual.rate == after_rate);
                    CHECK(actual.active == origin.active);
                    std::array<float, 1> subsequent{};
                    CHECK(engine.process(1, subsequent, {}));
                    sample_oracle(subsequent[0], current_sample(actual, profile, model));
                    if (before_rate == after_rate) {
                        discard(old_rate_copy, 193);
                        std::array<float, 1> continuation{};
                        CHECK(old_rate_copy.process(1, continuation, {}));
                        exact_audio(subsequent, continuation);
                        CHECK(inspect(engine) == inspect(old_rate_copy));
                    }
                }
            }
        }
    }
}

void detector_edges(const RuntimeProfile& profile) {
    constexpr std::uint8_t note = 69;
    constexpr std::size_t key_index = note - kMinManualMidiNote;
    for (const auto mode : kModes) {
        const auto model = varied_model(mode);
        const auto& key_profile = model.contacts.keys[0][key_index];
        for (const auto old_rate : kRates) {
            for (const auto new_rate : kRates) {
                for (const bool pressing : {false, true}) {
                    Engine engine;
                    CHECK(engine.prepare(profile, {old_rate, kBlock, kSeed, kOrigin}, model) == Status::Ok);
                    CHECK(engine.restore_controls(varied_controls(true)));
                    const std::array<Event, 1> on{{{0, EventType::NoteOn, Manual::Upper, note, 63}}};
                    flush(engine, on);
                    if (pressing) {
                        discard(engine, static_cast<std::uint32_t>(std::ceil(0.0037 * old_rate)));
                    } else {
                        discard(engine, static_cast<std::uint32_t>(std::ceil(0.027 * old_rate)));
                        const std::array<Event, 1> off{{{0, EventType::NoteOff, Manual::Upper, note, 0}}};
                        flush(engine, off);
                        discard(engine, static_cast<std::uint32_t>(std::ceil(0.00053 * old_rate)));
                    }
                    const auto origin = inspect(engine);
                    const auto& key = origin.contacts[0][key_index];
                    const bool detector = key.closed[8];
                    CHECK(origin.percussion.routed_detector == detector);
                    std::uint32_t edge_frame = 0;
                    if (mode == ContactMode::LinearTravel) {
                        CHECK(key.position > 0.0 && key.position < 1.0);
                        CHECK(detector != pressing);
                        // The continuous trajectory reaches its make/break
                        // threshold after distance * full-travel seconds.
                        // Rounding UP locates the first subsequent sample state
                        // with that contact edge. Render-before-advance means
                        // exactly edge_frame samples still use the old detector.
                        const auto distance = pressing ?
                            static_cast<long double>(key_profile.on_thresholds[8]) - key.position :
                            static_cast<long double>(key.position) - key_profile.off_thresholds[8];
                        const auto travel_seconds = pressing ? key_profile.press_seconds : key_profile.release_seconds;
                        const auto crossing = distance * travel_seconds * new_rate;
                        CHECK(crossing > 1.0L);
                        CHECK(std::fabs(crossing - std::round(crossing)) > 1e-6L);
                        edge_frame = static_cast<std::uint32_t>(std::ceil(crossing));
                    } else {
                        CHECK(detector == pressing);
                    }
                    const auto frames = static_cast<std::uint32_t>(std::ceil(0.014 * new_rate));
                    CHECK(edge_frame < frames);
                    auto original = engine;
                    migrate(engine, new_rate);
                    std::array<float, 1> actual_sample{}, original_sample{};
                    CHECK(engine.process(1, actual_sample, {}));
                    CHECK(original.process(1, original_sample, {}));
                    exact_audio(actual_sample, original_sample);
                    sample_oracle(actual_sample[0], current_sample(origin, profile, model));
                    discard(engine, frames - 1);
                    const auto actual = inspect(engine);
                    auto expected_q = static_cast<long double>(origin.percussion.readiness);
                    if (mode == ContactMode::LinearTravel) {
                        expected_q = readiness_after(expected_q,
                            static_cast<long double>(edge_frame) / new_rate, detector,
                            model.percussion, origin.controls.percussion.decay);
                        expected_q = readiness_after(expected_q,
                            static_cast<long double>(frames - edge_frame) / new_rate, !detector,
                            model.percussion, origin.controls.percussion.decay);
                    } else {
                        expected_q = readiness_after(expected_q,
                            static_cast<long double>(frames) / new_rate, detector,
                            model.percussion, origin.controls.percussion.decay);
                    }
                    CHECK(actual.percussion.physical_detector == pressing);
                    CHECK(actual.percussion.routed_detector == pressing);
                    CHECK(std::fabs(expected_q - origin.percussion.readiness) > 0.001L);
                    readiness_oracle(actual, expected_q);
                    phase_oracle(origin, actual, profile, static_cast<long double>(frames) / new_rate);
                    contact_oracle(origin, actual, model, static_cast<long double>(frames) / new_rate);
                    CHECK(actual.clock == origin.clock + frames);
                    ++measured.detector_edge_scenarios;
                }
            }
        }
    }
}

void exact_future(Engine actual, Engine expected) {
    const std::array<Event, 6> events{{
        {0, EventType::Drawbar, Manual::Lower, 8, 8},
        {7, EventType::NoteOff, Manual::Upper, 60, 0},
        {31, EventType::Cancel, Manual::Upper, 0, 0},
        {79, EventType::SelectBank, Manual::Upper, 0, 1},
        {101, EventType::NoteOn, Manual::Upper, 60, 87},
        {137, EventType::Percussion, Manual::Upper, 3, 1},
    }};
    std::array<float, 176> a{}, b{};
    a.fill(-123.25F);
    b = a;
    const auto result_a = actual.process(171, a, events);
    const auto result_b = expected.process(171, b, events);
    CHECK(result_a.status == Status::Ok && result_b.status == Status::Ok);
    CHECK(result_a.events_consumed == events.size());
    CHECK(result_b.events_consumed == events.size());
    exact_audio(std::span<const float>(a).first(171), std::span<const float>(b).first(171));
    for (std::size_t index = 171; index < a.size(); ++index) {
        CHECK(a[index] == -123.25F);
        CHECK(b[index] == -123.25F);
    }
    CHECK(inspect(actual) == inspect(expected));
    discard(actual, 43);
    discard(expected, 43);
    CHECK(inspect(actual) == inspect(expected));
    CHECK(actual.process(176, a, {}));
    CHECK(expected.process(176, b, {}));
    exact_audio(a, b);
    CHECK(inspect(actual) == inspect(expected));
}

void rejected_rate(Engine engine, double requested, Status status) {
    const auto untouched = engine;
    const auto before = inspect(engine);
    CHECK(engine.reconfigure_sample_rate(requested) == status);
    CHECK(inspect(engine) == before);
    ++measured.rejected_changes;
    exact_future(engine, untouched);
}

void rejection_contract(const RuntimeProfile& profile) {
    const std::array<double, 10> bad_rates{
        0.0, -48000.0, 44100.5, std::nextafter(48000.0, 0.0), 88200.0,
        192000.0, std::numeric_limits<double>::quiet_NaN(),
        std::numeric_limits<double>::infinity(), -std::numeric_limits<double>::infinity(),
        std::numeric_limits<double>::denorm_min()};
    Engine unprepared;
    const auto empty = inspect(unprepared);
    CHECK(unprepared.sample_rate() == 0.0);
    for (const auto rate : bad_rates) {
        CHECK(unprepared.reconfigure_sample_rate(rate) == Status::NotPrepared);
        CHECK(inspect(unprepared) == empty);
        ++measured.rejected_changes;
    }
    for (const auto rate : kRates) {
        CHECK(unprepared.reconfigure_sample_rate(rate) == Status::NotPrepared);
        CHECK(inspect(unprepared) == empty);
        ++measured.rejected_changes;
    }
    std::array<float, 1> output{29.0F};
    const auto not_ready = unprepared.process(1, output, {});
    CHECK(not_ready.status == Status::NotPrepared && not_ready.events_consumed == 0);
    CHECK(output[0] == 29.0F);
    Engine fresh;
    const auto model = varied_model(ContactMode::LinearTravel);
    CHECK(unprepared.prepare(profile, {48000, kBlock, kSeed, kOrigin}, model) == Status::Ok);
    CHECK(fresh.prepare(profile, {48000, kBlock, kSeed, kOrigin}, model) == Status::Ok);
    CHECK(inspect(unprepared) == inspect(fresh));
    exact_future(unprepared, fresh);

    for (const auto mode : kModes) {
        const auto console = varied_model(mode);
        for (const auto rate : kRates) {
            const auto engine = moving_engine(profile, console, rate, true);
            for (const auto bad : bad_rates) {
                rejected_rate(engine, bad, Status::InvalidSpec);
            }
        }
        auto high = profile;
        high.sources.back().frequency_hz = 30000.0;
        const auto high_engine = moving_engine(high, console, 96000, true);
        rejected_rate(high_engine, 44100, Status::InvalidProfile);
        rejected_rate(high_engine, 48000, Status::InvalidProfile);

        auto tiny = profile;
        tiny.sources.back().frequency_hz = std::ldexp(44100.0, -53);
        const auto tiny_engine = moving_engine(tiny, console, 44100, true);
        rejected_rate(tiny_engine, 48000, Status::InvalidProfile);
        rejected_rate(tiny_engine, 96000, Status::InvalidProfile);

        auto engine = moving_engine(profile, console, 48000);
        migrate(engine, 96000);
        const auto original = engine;
        const auto snapshot = inspect(engine);
        CHECK(engine.prepare(profile, {32000, kBlock, kSeed, 0}, console) == Status::InvalidSpec);
        CHECK(inspect(engine) == snapshot);
        exact_future(engine, original);
    }
}

void repeated_same_rate(const RuntimeProfile& profile) {
    for (const auto mode : kModes) {
        const auto model = varied_model(mode);
        for (const auto rate : kRates) {
            auto engine = moving_engine(profile, model, rate, true);
            auto uninterrupted = engine;
            for (std::uint32_t frame = 0; frame < 512; ++frame) {
                const auto before = inspect(engine);
                CHECK(engine.reconfigure_sample_rate(rate) == Status::Ok);
                CHECK(engine.reconfigure_sample_rate(rate) == Status::Ok);
                measured.same_rate_calls += 2;
                CHECK(inspect(engine) == before);
                if (frame == 37 || frame == 139 || frame == 277) {
                    const std::array<Event, 1> event{{
                        {0, frame == 139 ? EventType::NoteOn : EventType::NoteOff,
                         Manual::Upper, 40, frame == 139 ? 97.0 : 0.0}}};
                    flush(engine, event);
                    flush(uninterrupted, event);
                }
                std::array<float, 1> a{}, b{};
                CHECK(engine.process(1, a, {}));
                CHECK(uninterrupted.process(1, b, {}));
                exact_audio(a, b);
                CHECK(inspect(engine) == inspect(uninterrupted));
            }
            // A copy can follow its own lifecycle without modifying the source.
            const auto frozen = inspect(engine);
            auto independent = engine;
            migrate(independent, rate == 96000 ? 44100 : 96000);
            discard(independent, 127);
            CHECK(inspect(engine) == frozen);
        }
    }
}

void mixed_rate_controls(const RuntimeProfile& profile) {
    constexpr std::array<double, 7> rates{96000, 44100, 48000, 96000, 44100, 48000, 96000};
    constexpr std::array<std::uint32_t, 7> counts{163, 211, 71, 257, 113, 97, 191};
    for (const auto mode : kModes) {
        const auto model = varied_model(mode);
        auto engine = moving_engine(profile, model, 48000);
        const auto origin = inspect(engine);
        long double elapsed = 0.0L;
        long double q = origin.percussion.readiness;
        std::uint64_t frames = 0;
        for (std::size_t segment = 0; segment < rates.size(); ++segment) {
            const auto before_controls = inspect(engine);
            if (segment == 1) {
                const std::array<Event, 1> cancel{{{0, EventType::Cancel, Manual::Upper, 0, 0}}};
                flush(engine, cancel);
            } else {
                auto controls = varied_controls(segment >= 3);
                if (segment == 2) {
                    controls.selected_banks[0] = DrawbarBank::A;
                } else if (segment == 4) {
                    controls.expression = 0.0;
                } else if (segment == 5) {
                    controls.percussion.enabled = false;
                } else if (segment == 6) {
                    controls.percussion.decay = PercussionDecay::Slow;
                }
                CHECK(engine.restore_controls(controls));
            }
            const auto before_rate = inspect(engine);
            unchanged_dynamics(before_controls, before_rate);
            CHECK(before_rate.percussion.physical_detector);
            const bool detector = segment != 1 && segment != 2 && segment != 5;
            CHECK(before_rate.percussion.routed_detector == detector);
            migrate(engine, rates[segment]);
            const auto before_zero = inspect(engine);
            flush(engine);
            CHECK(inspect(engine) == before_zero);
            auto connected = engine;
            std::array<float, kBlock + 3> audio{};
            audio.fill(31.0F);
            CHECK(connected.process(counts[segment], audio, {}));
            CHECK(engine.process(counts[segment], {}, {}));
            CHECK(inspect(engine) == inspect(connected));
            sample_oracle(audio[0], current_sample(before_zero, profile, model));
            for (std::size_t frame = counts[segment]; frame < audio.size(); ++frame) {
                CHECK(audio[frame] == 31.0F);
            }
            if (segment == 4) {
                for (std::size_t frame = 0; frame < counts[segment]; ++frame) {
                    CHECK(audio[frame] == 0.0F);
                }
            }
            const auto seconds = static_cast<long double>(counts[segment]) / rates[segment];
            elapsed += seconds;
            frames += counts[segment];
            q = readiness_after(q, seconds, detector, model.percussion,
                                before_zero.controls.percussion.decay);
            const auto after = inspect(engine);
            phase_oracle(origin, after, profile, elapsed);
            contact_oracle(origin, after, model, elapsed);
            readiness_oracle(after, q);
            CHECK(after.clock == origin.clock + frames);
            CHECK(after.controls == before_zero.controls);
            ++measured.mixed_segments;
        }
        CHECK(std::fabs(elapsed - static_cast<long double>(frames) / rates.back()) > 0.001L);
        auto invalid = engine.controls_snapshot();
        invalid.drawbars[1][1][8] = 9;
        const auto before_bad_restore = inspect(engine);
        const auto reference = engine;
        CHECK(!engine.restore_controls(invalid));
        CHECK(inspect(engine) == before_bad_restore);
        exact_future(engine, reference);
    }
}

bool same_profile(const RuntimeProfile& a, const RuntimeProfile& b) {
    if (a.profile_id != b.profile_id || a.authoring_sha256 != b.authoring_sha256 ||
        a.output_gain != b.output_gain || a.drawbar_gains != b.drawbar_gains ||
        a.manual_map != b.manual_map) {
        return false;
    }
    for (std::size_t source = 0; source < kToneSourceCount; ++source) {
        if (a.sources[source].frequency_hz != b.sources[source].frequency_hz ||
            a.sources[source].peak_amplitude != b.sources[source].peak_amplitude ||
            a.sources[source].base_phase_turns != b.sources[source].base_phase_turns) {
            return false;
        }
    }
    return true;
}

void caller_ownership(const RuntimeProfile& original_profile) {
    for (const auto mode : kModes) {
        for (const auto rate : kRates) {
            auto supplied_profile = original_profile;
            auto supplied_model = varied_model(mode);
            const auto immutable_model = supplied_model;
            auto engine = moving_engine(supplied_profile, supplied_model, rate, true);
            auto reference = moving_engine(original_profile, immutable_model, rate, true);
            CHECK(same_profile(supplied_profile, original_profile));
            CHECK(supplied_model == immutable_model);
            CHECK(inspect(engine) == inspect(reference));
            // Poison every field of both caller-owned inputs. Successful future
            // migration must use the prepared owned values, never these bytes.
            supplied_profile.profile_id.fill('x');
            supplied_profile.authoring_sha256.fill('q');
            supplied_profile.output_gain = -1.0;
            supplied_profile.drawbar_gains.fill(-3.0);
            for (auto& source : supplied_profile.sources) {
                source = {30000.0, -2.0, 4.0};
            }
            for (auto& key : supplied_profile.manual_map) {
                key.fill(0);
            }
            supplied_model.contacts.mode = static_cast<ContactMode>(255);
            for (auto& manual : supplied_model.contacts.keys) {
                for (auto& key : manual) {
                    key.on_thresholds.fill(-1.0);
                    key.off_thresholds.fill(2.0);
                    key.press_seconds = 0.0;
                    key.release_seconds = -1.0;
                }
            }
            supplied_model.percussion = {-1, -2, -3, -4, -5, -6, -7};
            for (const auto next_rate : kRates) {
                migrate(engine, next_rate);
                migrate(reference, next_rate);
                CHECK(inspect(engine) == inspect(reference));
                const auto before = inspect(engine);
                std::array<float, 113> actual{}, expected{};
                CHECK(engine.process(113, actual, {}));
                CHECK(reference.process(113, expected, {}));
                exact_audio(actual, expected);
                sample_oracle(actual[0], current_sample(before, original_profile, immutable_model));
                const auto after = inspect(engine);
                CHECK(after == inspect(reference));
                phase_oracle(before, after, original_profile, 113.0L / next_rate);
                contact_oracle(before, after, immutable_model, 113.0L / next_rate);
                readiness_oracle(after, readiness_after(before.percussion.readiness,
                    113.0L / next_rate, true, immutable_model.percussion,
                    before.controls.percussion.decay));
            }
            ++measured.ownership_cases;
        }
    }
}

void block_and_clock_contract(const RuntimeProfile& profile) {
    for (const auto mode : kModes) {
        auto engine = moving_engine(profile, varied_model(mode), 44100);
        for (const auto rate : kRates) {
            migrate(engine, rate);
            const auto before = inspect(engine);
            const auto copy = engine;
            std::array<float, kBlock + 1> too_large{};
            too_large.fill(-19.0F);
            const std::array<Event, 1> event{{{0, EventType::NoteOn, Manual::Lower, 37, 127}}};
            const auto rejected = engine.process(kBlock + 1, too_large, event);
            CHECK(rejected.status == Status::BlockTooLarge && rejected.events_consumed == 0);
            CHECK(inspect(engine) == before);
            CHECK(std::all_of(too_large.begin(), too_large.end(), [](float v) { return v == -19.0F; }));
            exact_future(engine, copy);
            CHECK(engine.process(kBlock, too_large, {}));
            CHECK(too_large.back() == -19.0F);
            CHECK(engine.frame_clock() == before.clock + kBlock);
        }
    }
    const auto model = varied_model(ContactMode::LinearTravel);
    constexpr auto maximum = std::numeric_limits<std::uint64_t>::max();
    Engine near_end, zero_origin;
    CHECK(near_end.prepare(profile, {48000, kBlock, kSeed, maximum - 3}, model) == Status::Ok);
    CHECK(zero_origin.prepare(profile, {48000, kBlock, kSeed, 0}, model) == Status::Ok);
    CHECK(inspect(near_end).phases == inspect(zero_origin).phases);
    migrate(near_end, 96000);
    discard(near_end, 3);
    CHECK(near_end.frame_clock() == maximum);
    migrate(near_end, 44100);
    const auto before = inspect(near_end);
    std::array<float, 1> untouched{41.0F};
    const auto overflow = near_end.process(1, untouched, {});
    CHECK(overflow.status == Status::TimelineOverflow && overflow.events_consumed == 0);
    CHECK(untouched[0] == 41.0F);
    CHECK(inspect(near_end) == before);
    flush(near_end);
    CHECK(inspect(near_end) == before);
}

} // namespace

int main() {
    const auto profile = load_test_profile();
    all_rate_pairs(profile);
    detector_edges(profile);
    rejection_contract(profile);
    repeated_same_rate(profile);
    mixed_rate_controls(profile);
    caller_ownership(profile);
    block_and_clock_contract(profile);
    std::cout << std::setprecision(17)
              << "rate_pair_scenarios=" << measured.pair_scenarios
              << " rejected_changes=" << measured.rejected_changes
              << " same_rate_calls=" << measured.same_rate_calls
              << " complete_snapshots=" << measured.snapshots
              << " phase_checks=" << measured.phase_checks
              << " position_checks=" << measured.position_checks
              << " contact_bit_checks=" << measured.contact_bit_checks
              << " readiness_checks=" << measured.readiness_checks
              << " sample_oracles=" << measured.sample_oracles
              << " exact_audio_frames=" << measured.exact_audio_frames
              << " mixed_segments=" << measured.mixed_segments
              << " ownership_cases=" << measured.ownership_cases
              << " detector_edge_scenarios=" << measured.detector_edge_scenarios << '\n'
              << "max_phase_error_turns=" << measured.max_phase_error
              << " max_position_error=" << measured.max_position_error
              << " max_readiness_error=" << measured.max_readiness_error
              << " max_sample_error=" << measured.max_sample_error << '\n';
}
