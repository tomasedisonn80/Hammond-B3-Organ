#include "PresetTestOracle.h"
#include "TestSupport.h"
#include "hammond/ControlStateIO.h"
#include "hammond/Engine.h"

#include <algorithm>
#include <array>
#include <bit>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <span>
#include <sstream>
#include <string>
#include <vector>

namespace {

using namespace hammond;

constexpr std::array<double, 3> kRates{44100.0, 48000.0, 96000.0};
constexpr std::uint32_t kBlock = 512;
constexpr std::uint64_t kOrigin = 9000000041ULL;
constexpr std::uint64_t kSeed = 0x83ab56c91d207ef4ULL;
constexpr float kSentinel = -173.25F;

struct Counts {
    std::size_t lifecycle_cases{};
    std::size_t rate_boundaries{};
    std::size_t live_restores{};
    std::size_t state_round_trips{};
    std::size_t cold_loads{};
    std::size_t rejected_rates{};
    std::size_t rejected_restores{};
    std::size_t exact_audio_frames{};
    std::size_t phase_oracles{};
    std::size_t position_oracles{};
    std::size_t contact_oracles{};
    std::size_t readiness_oracles{};
    std::size_t snapshots{};
} counts;

// Include every publicly observable dynamic history, not just musical controls.
// The last pedal record is deliberately distinct from the next-sample state.
struct History {
    double rate{};
    std::uint64_t clock{};
    ContactMode mode{};
    std::array<std::size_t, kManualCount> active_keys{};
    std::size_t active_pedals{};
    std::array<std::array<bool, kManualKeyCount>, kManualCount> held{};
    std::array<std::array<ContactKeySnapshot, kManualKeyCount>, kManualCount> contacts{};
    std::array<std::uint64_t, kToneSourceCount> phase_bits{};
    std::uint64_t readiness_bits{};
    std::array<bool, kPedalCount> pedals{};
    PedalContactStates pedal_contacts{};
    PedalRenderDiagnostics last_pedal{};

    [[nodiscard]] bool operator==(const History&) const noexcept = default;
};

struct Snapshot {
    History history{};
    ControlSnapshot controls{};
    PercussionRoutingDiagnostics percussion{};

    [[nodiscard]] bool operator==(const Snapshot&) const noexcept = default;
};

Manual manual_at(std::size_t index) { return static_cast<Manual>(index); }

Snapshot inspect(const Engine& engine) {
    CHECK(engine.prepared());
    ++counts.snapshots;
    Snapshot result;
    auto& history = result.history;
    history.rate = engine.sample_rate();
    history.clock = engine.frame_clock();
    history.mode = engine.contact_mode();
    result.controls = engine.controls_snapshot();
    result.percussion = engine.percussion_diagnostics();
    CHECK(result.percussion.prepared);
    history.readiness_bits = std::bit_cast<std::uint64_t>(result.percussion.readiness);
    CHECK(engine.expression() == result.controls.expression);
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        history.active_keys[manual] = engine.active_key_count(manual_at(manual));
        std::size_t held_count = 0;
        for (std::size_t key = 0; key < kManualKeyCount; ++key) {
            const auto note = static_cast<std::uint32_t>(key) + kMinManualMidiNote;
            history.held[manual][key] = engine.key_down(manual_at(manual), note);
            held_count += history.held[manual][key] ? 1U : 0U;
            CHECK(engine.contact_snapshot(manual_at(manual), note,
                                          history.contacts[manual][key]));
        }
        CHECK(held_count == history.active_keys[manual]);
        DrawbarBank bank = DrawbarBank::A;
        bool enabled = false;
        CHECK(engine.selected_bank(manual_at(manual), bank));
        CHECK(engine.route_enabled(manual_at(manual), enabled));
        CHECK(bank == result.controls.selected_banks[manual]);
        CHECK(enabled == result.controls.route_enabled[manual]);
        for (std::size_t drawbar = 0; drawbar < kDrawbarCount; ++drawbar) {
            std::uint8_t position = 255;
            CHECK(engine.drawbar_position(manual_at(manual), drawbar, position));
            CHECK(position == result.controls.drawbars[manual]
                  [static_cast<std::size_t>(bank)][drawbar]);
        }
    }
    CHECK(engine.active_key_count() == history.active_keys[0] + history.active_keys[1]);
    for (std::size_t tone = 0; tone < kToneSourceCount; ++tone) {
        double phase = -1.0;
        CHECK(engine.source_phase_turns(static_cast<ToneId>(tone + 1), phase));
        history.phase_bits[tone] = std::bit_cast<std::uint64_t>(phase);
    }
    std::size_t held_pedals = 0;
    for (std::size_t pedal = 0; pedal < kPedalCount; ++pedal) {
        history.pedals[pedal] = engine.pedal_down(PedalId{static_cast<std::uint8_t>(pedal + 1)});
        held_pedals += history.pedals[pedal] ? 1U : 0U;
    }
    history.active_pedals = engine.active_pedal_count();
    CHECK(held_pedals == history.active_pedals);
    CHECK(engine.pedal_contacts_snapshot(history.pedal_contacts));
    history.last_pedal = engine.last_pedal_frame();
    return result;
}

void process(Engine& engine, std::uint32_t frames, std::span<float> output = {},
             std::span<const Event> events = {}) {
    const auto result = engine.process(frames, output, events);
    CHECK(result.status == Status::Ok);
    CHECK(result.events_consumed == events.size());
}

void flush(Engine& engine, std::span<const Event> events) {
    std::array<float, 3> untouched{kSentinel, 19.5F, -8.0F};
    const auto original = untouched;
    process(engine, 0, untouched, events);
    CHECK(untouched == original);
}

void exact_audio(std::span<const float> actual, std::span<const float> expected) {
    CHECK(actual.size() == expected.size());
    for (std::size_t frame = 0; frame < actual.size(); ++frame) {
        CHECK(std::bit_cast<std::uint32_t>(actual[frame]) ==
              std::bit_cast<std::uint32_t>(expected[frame]));
        ++counts.exact_audio_frames;
    }
}

ConsoleModel lifecycle_model(ContactMode mode) {
    auto model = make_nominal_console_model();
    model.contacts.mode = mode;
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        for (std::size_t key = 0; key < kManualKeyCount; ++key) {
            auto& contact = model.contacts.keys[manual][key];
            contact.press_seconds = 0.00571 + 0.000013 * static_cast<double>(key) +
                                    0.00043 * static_cast<double>(manual);
            contact.release_seconds = 0.00993 + 0.000017 * static_cast<double>(key) +
                                      0.00027 * static_cast<double>(manual);
            for (std::size_t bar = 0; bar < kDrawbarCount; ++bar) {
                const double offset = 0.00011 * static_cast<double>((key + manual) % 5);
                contact.on_thresholds[bar] = 0.1137 + 0.1003 * static_cast<double>(bar) + offset;
                contact.off_thresholds[bar] = 0.0341 + 0.1003 * static_cast<double>(bar) + offset;
            }
        }
    }
    model.percussion = {0.2813, 0.0637, 0.0191, 0.79, 0.37, 1.31, 0.63};
    return model;
}

ControlSnapshot initial_controls() {
    ControlSnapshot result;
    result.drawbars[0][0] = {8, 0, 6, 0, 4, 0, 2, 0, 1};
    result.drawbars[0][1] = {0, 7, 0, 5, 0, 3, 0, 1, 8};
    result.drawbars[1][0] = {1, 2, 3, 4, 5, 6, 7, 8, 0};
    result.drawbars[1][1] = {8, 7, 6, 5, 4, 3, 2, 1, 0};
    result.selected_banks = {DrawbarBank::B, DrawbarBank::A};
    result.expression = 0.6875;
    result.percussion = {true, PercussionHarmonic::Third,
                         PercussionVolume::Normal, PercussionDecay::Fast};
    result.pedal_drawbars = {6, 3};
    return result;
}

// The comparison engine never uses a fixed registration. Its active bank A is
// independently filled from A10's source-read literal rows, not native lookup.
// Keeping percussion On with upper bank A also reproduces ineligible recovery.
ControlSnapshot bank_reference(const ControlSnapshot& fixed) {
    auto reference = fixed;
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        const auto selected = static_cast<std::size_t>(fixed.fixed_registrations[manual]);
        if (selected != 0) {
            CHECK(selected <= 9);
            for (std::size_t bar = 0; bar < kDrawbarCount; ++bar) {
                reference.drawbars[manual][0][bar] =
                    preset_test_oracle::kPositions[manual][selected - 1][bar];
            }
            reference.selected_banks[manual] = DrawbarBank::A;
            reference.fixed_registrations[manual] = FixedRegistration::None;
        }
    }
    return reference;
}

void check_controls(const Engine& engine, const ControlSnapshot& expected) {
    CHECK(engine.controls_snapshot() == expected);
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        const auto fixed = static_cast<std::uint8_t>(expected.fixed_registrations[manual]);
        const auto wanted = !expected.route_enabled[manual] ? PresetSelection::Cancel :
            (fixed != 0 ? static_cast<PresetSelection>(fixed) :
             (expected.selected_banks[manual] == DrawbarBank::A ?
                  PresetSelection::BankA : PresetSelection::BankB));
        auto actual = static_cast<PresetSelection>(255);
        CHECK(engine.selected_preset(manual_at(manual), actual));
        CHECK(actual == wanted);
    }
}

void restore_live(Engine& engine, const ControlSnapshot& controls) {
    const auto before = inspect(engine);
    CHECK(engine.restore_controls(controls));
    const auto after = inspect(engine);
    CHECK(after.history == before.history);
    CHECK(after.percussion.physical_detector == before.percussion.physical_detector);
    check_controls(engine, controls);
    ++counts.live_restores;
}

ControlSnapshot round_trip(const ControlSnapshot& controls, std::string* saved = nullptr) {
    std::string bytes = "previous destination";
    std::string error = "previous error";
    CHECK(serialize_controls(controls, bytes, error));
    CHECK(error.empty());
    CHECK(bytes.starts_with("B3CONTROLS4\nregistration_catalog atlas-chapel-nominal-v1 sha256 "));
    auto parsed = initial_controls();
    parsed.fixed_registrations = {FixedRegistration::A, FixedRegistration::CSharp};
    parsed.route_enabled = {false, false};
    std::istringstream stream(bytes);
    CHECK(parse_controls(stream, parsed, error));
    CHECK(error.empty());
    CHECK(parsed == controls);
    std::string again;
    CHECK(serialize_controls(parsed, again, error));
    CHECK(again == bytes);
    if (saved != nullptr) *saved = bytes;
    ++counts.state_round_trips;
    return parsed;
}

void restore_pair(Engine& actual, Engine& reference, const ControlSnapshot& controls) {
    restore_live(actual, controls);
    restore_live(reference, bank_reference(controls));
    CHECK(inspect(actual).history == inspect(reference).history);
    CHECK(actual.percussion_diagnostics() == reference.percussion_diagnostics());
}

void rate_boundary(Engine& engine, double rate) {
    auto expected = inspect(engine);
    CHECK(engine.reconfigure_sample_rate(rate) == Status::Ok);
    expected.history.rate = rate;
    CHECK(inspect(engine) == expected);
    ++counts.rate_boundaries;
}

void numerical_history(const Snapshot& before, const Snapshot& after,
                       const RuntimeProfile& profile, const ConsoleModel& model,
                       std::uint32_t frames, bool routed_detector) {
    const long double seconds = static_cast<long double>(frames) / before.history.rate;
    CHECK(after.history.clock == before.history.clock + frames);
    for (std::size_t tone = 0; tone < kToneSourceCount; ++tone) {
        const auto start = std::bit_cast<double>(before.history.phase_bits[tone]);
        const auto actual = std::bit_cast<double>(after.history.phase_bits[tone]);
        const long double expected = std::fmod(static_cast<long double>(start) +
            seconds * static_cast<long double>(profile.sources[tone].frequency_hz), 1.0L);
        const long double distance = std::fabs(static_cast<long double>(actual) - expected);
        CHECK(std::min(distance, 1.0L - distance) <= 8.0e-12L);
        ++counts.phase_oracles;
    }
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        for (std::size_t key = 0; key < kManualKeyCount; ++key) {
            const auto& start = before.history.contacts[manual][key];
            const auto& actual = after.history.contacts[manual][key];
            const auto& parameters = model.contacts.keys[manual][key];
            long double expected = start.position;
            if (model.contacts.mode == ContactMode::LinearTravel) {
                if (start.target > start.position) {
                    expected = std::min(static_cast<long double>(start.target),
                                        expected + seconds / parameters.press_seconds);
                } else if (start.target < start.position) {
                    expected = std::max(static_cast<long double>(start.target),
                                        expected - seconds / parameters.release_seconds);
                }
            }
            CHECK_NEAR(actual.position, expected, 3.0e-13L);
            CHECK(actual.target == start.target);
            CHECK(after.history.held[manual][key] == before.history.held[manual][key]);
            ++counts.position_oracles;
            for (std::size_t bar = 0; bar < kDrawbarCount; ++bar) {
                bool expected_closed = start.closed[bar];
                if (start.position != start.target && model.contacts.mode == ContactMode::LinearTravel) {
                    if (expected_closed && expected <= parameters.off_thresholds[bar]) {
                        expected_closed = false;
                    } else if (!expected_closed && expected >= parameters.on_thresholds[bar]) {
                        expected_closed = true;
                    }
                }
                CHECK(actual.closed[bar] == expected_closed);
                ++counts.contact_oracles;
            }
        }
    }
    CHECK(before.percussion.routed_detector == routed_detector);
    CHECK(after.percussion.routed_detector == routed_detector);
    const long double initial = before.percussion.readiness;
    const auto decay = before.controls.percussion.decay == PercussionDecay::Fast ?
        model.percussion.fast_decay_seconds : model.percussion.slow_decay_seconds;
    const long double expected = routed_detector ? initial * std::exp(-seconds / decay) :
        1.0L - (1.0L - initial) * std::exp(-seconds / model.percussion.recovery_seconds);
    CHECK_NEAR(after.percussion.readiness, expected, 2.0e-12L);
    ++counts.readiness_oracles;
    CHECK(after.history.pedals == before.history.pedals);
    CHECK(after.history.pedal_contacts == before.history.pedal_contacts);
}

void segment(Engine& actual, Engine& reference, const RuntimeProfile& profile,
             const ConsoleModel& model, std::uint32_t frames,
             bool routed_detector, bool disconnected = false) {
    CHECK(frames > 0 && frames <= kBlock);
    const auto before = inspect(actual);
    std::array<float, kBlock + 3> output{}, expected{};
    output.fill(kSentinel);
    expected.fill(kSentinel);
    process(actual, frames, disconnected ? std::span<float>{} : std::span<float>{output});
    process(reference, frames, expected);
    if (!disconnected) {
        exact_audio(std::span<const float>{output}.first(frames),
                    std::span<const float>{expected}.first(frames));
    }
    for (std::size_t index = disconnected ? 0U : frames; index < output.size(); ++index) {
        CHECK(output[index] == kSentinel);
    }
    for (std::size_t index = frames; index < expected.size(); ++index) {
        CHECK(expected[index] == kSentinel);
    }
    const auto after = inspect(actual);
    CHECK(after.history == inspect(reference).history);
    CHECK(after.percussion == reference.percussion_diagnostics());
    CHECK(after.controls == before.controls);
    numerical_history(before, after, profile, model, frames, routed_detector);
    const auto& last = after.history.last_pedal;
    CHECK(last.valid);
    CHECK(last.frame == before.history.clock + frames - 1);
    CHECK(last.sample_rate == before.history.rate);
    CHECK(last.positions == before.controls.pedal_drawbars);
}

Engine prepared(const RuntimeProfile& profile, const ConsoleModel& model, double rate) {
    Engine engine;
    CHECK(engine.prepare(profile, {rate, kBlock, kSeed, kOrigin}, model) == Status::Ok);
    CHECK(engine.restore_controls(initial_controls()));
    const std::array<Event, 9> notes{{
        {0, EventType::NoteOn, Manual::Upper, 36, 100},
        {0, EventType::NoteOn, Manual::Upper, 60, 73},
        {0, EventType::NoteOn, Manual::Upper, 96, 1},
        {0, EventType::NoteOn, Manual::Lower, 38, 90},
        {0, EventType::NoteOn, Manual::Lower, 55, 63},
        {0, EventType::NoteOn, Manual::Lower, 91, 127},
        {0, EventType::PedalOn, Manual::Lower, 1, 64},
        {0, EventType::PedalOn, Manual::Lower, 13, 90},
        {0, EventType::PedalOn, Manual::Lower, 25, 127},
    }};
    flush(engine, notes);
    auto remaining = static_cast<std::uint32_t>(std::ceil(rate * 0.0183));
    while (remaining != 0) {
        const auto count = std::min(remaining, kBlock);
        process(engine, count);
        remaining -= count;
    }
    CHECK(engine.percussion_diagnostics().routed_detector);
    CHECK(engine.percussion_diagnostics().readiness < 0.99);
    const bool travel = model.contacts.mode == ContactMode::LinearTravel;
    const std::array<Event, 6> moving{{
        {0, EventType::NoteOff, Manual::Upper, 36, 0},
        {0, EventType::KeyPosition, Manual::Upper, 60, travel ? 0.573 : 0.0},
        {0, EventType::NoteOn, Manual::Upper, 37, 19},
        {0, EventType::NoteOff, Manual::Lower, 38, 0},
        {0, EventType::KeyPosition, Manual::Lower, 55, travel ? 0.647 : 0.0},
        {0, EventType::NoteOn, Manual::Lower, 95, 80},
    }};
    flush(engine, moving);
    process(engine, static_cast<std::uint32_t>(std::ceil(rate * 0.00137)));
    CHECK(engine.percussion_diagnostics().physical_detector);
    return engine;
}

void check_motion(const Engine& engine) {
    if (engine.contact_mode() != ContactMode::LinearTravel) return;
    ContactKeySnapshot rising{}, falling{}, partial{};
    CHECK(engine.contact_snapshot(Manual::Upper, 37, rising));
    CHECK(engine.contact_snapshot(Manual::Upper, 36, falling));
    CHECK(engine.contact_snapshot(Manual::Lower, 55, partial));
    CHECK(rising.position > 0.0 && rising.position < rising.target);
    CHECK(falling.position > falling.target && falling.position < 1.0);
    CHECK(partial.target == 0.647);
    CHECK(partial.position > partial.target && partial.position < 1.0);
}

void cold_load(const RuntimeProfile& profile, const ConsoleModel& model, double rate,
               const ControlSnapshot& controls) {
    Engine cold;
    CHECK(cold.prepare(profile, {rate, kBlock, kSeed + 17U, 27}, model) == Status::Ok);
    const auto before = inspect(cold);
    CHECK(!before.history.last_pedal.valid);
    restore_live(cold, round_trip(controls));
    CHECK(inspect(cold).history == before.history);
    CHECK(cold.active_key_count() == 0);
    CHECK(cold.active_pedal_count() == 0);
    CHECK(cold.percussion_diagnostics().readiness == 1.0);
    CHECK(!cold.percussion_diagnostics().physical_detector);
    std::array<float, 31> silence{};
    silence.fill(kSentinel);
    process(cold, static_cast<std::uint32_t>(silence.size()), silence);
    for (const auto sample : silence) CHECK(sample == 0.0F);
    CHECK(cold.last_pedal_frame().valid);
    CHECK(cold.last_pedal_frame().frame == 57);
    CHECK(cold.last_pedal_frame().sample_rate == rate);
    CHECK(cold.last_pedal_frame().positions == controls.pedal_drawbars);
    ++counts.cold_loads;
}

void identical_future(Engine actual, Engine untouched);

void fixed_rate_restore_lifecycle(const RuntimeProfile& profile) {
    for (std::size_t from = 0; from < kRates.size(); ++from) {
        for (std::size_t to = 0; to < kRates.size(); ++to) {
            for (const auto mode : {ContactMode::Ideal, ContactMode::LinearTravel}) {
                for (unsigned route_mask = 0; route_mask < 4; ++route_mask) {
                    const auto model = lifecycle_model(mode);
                    auto actual = prepared(profile, model, kRates[from]);
                    auto reference = prepared(profile, model, kRates[from]);
                    CHECK(inspect(actual) == inspect(reference));
                    check_motion(actual);
                    auto fixed = initial_controls();
                    const auto row = from * kRates.size() + to;
                    fixed.fixed_registrations = {
                        static_cast<FixedRegistration>(row + 1),
                        static_cast<FixedRegistration>((2 * row + 3) % 9 + 1)};
                    fixed.route_enabled = {(route_mask & 1U) != 0, (route_mask & 2U) != 0};
                    fixed.expression = 0.8125;
                    fixed.pedal_drawbars = {2, 7};
                    std::string saved;
                    restore_pair(actual, reference, round_trip(fixed, &saved));
                    CHECK(!actual.percussion_diagnostics().eligible);
                    CHECK(actual.percussion_diagnostics().gain == 0.0);
                    CHECK(actual.percussion_diagnostics().upper_sustain_gain == 1.0);
                    // A control/rate boundary cannot relabel the last sample.
                    CHECK(actual.last_pedal_frame().positions == initial_controls().pedal_drawbars);
                    CHECK(actual.last_pedal_frame().sample_rate == kRates[from]);
                    rate_boundary(actual, kRates[to]);
                    rate_boundary(reference, kRates[to]);
                    CHECK(actual.last_pedal_frame().sample_rate == kRates[from]);
                    CHECK(actual.last_pedal_frame().positions != fixed.pedal_drawbars);
                    std::string after_rate, error;
                    CHECK(serialize_controls(actual.controls_snapshot(), after_rate, error));
                    CHECK(after_rate == saved);
                    cold_load(profile, model, kRates[to], fixed);
                    segment(actual, reference, profile, model, 1, false);
                    segment(actual, reference, profile, model, 79, false, true);
                    check_motion(actual);

                    // Identical musical state must also preserve future hidden
                    // trajectory bookkeeping, not merely its copied position.
                    const auto untouched = actual;
                    restore_live(actual, round_trip(actual.controls_snapshot()));
                    identical_future(actual, untouched);

                    // Restore different saved controls while both release and
                    // attack motion continue and q has recovered at the new rate.
                    auto next = fixed;
                    next.fixed_registrations = {
                        static_cast<FixedRegistration>((row + 4) % 9 + 1),
                        static_cast<FixedRegistration>((2 * row + 5) % 9 + 1)};
                    next.route_enabled = {!fixed.route_enabled[0], !fixed.route_enabled[1]};
                    next.selected_banks = {DrawbarBank::A, DrawbarBank::B};
                    next.expression = 0.4375;
                    next.pedal_drawbars = {8, 1};
                    next.percussion.volume = PercussionVolume::Soft;
                    next.percussion.decay = PercussionDecay::Slow;
                    restore_pair(actual, reference, round_trip(next));
                    CHECK(actual.last_pedal_frame().positions == fixed.pedal_drawbars);
                    CHECK(actual.last_pedal_frame().sample_rate == kRates[to]);
                    rate_boundary(actual, kRates[from]);
                    rate_boundary(reference, kRates[from]);
                    CHECK(actual.last_pedal_frame().sample_rate == kRates[to]);
                    segment(actual, reference, profile, model, 131, false);

                    // Loading the earlier file restores controls, not the older
                    // phases, contact positions, pedals, readiness, or clock.
                    auto earlier = next;
                    std::istringstream input(saved);
                    CHECK(parse_controls(input, earlier, error));
                    CHECK(earlier == fixed);
                    restore_pair(actual, reference, earlier);
                    segment(actual, reference, profile, model, 43, false);
                    restore_pair(actual, reference, initial_controls());
                    CHECK(actual.percussion_diagnostics().eligible);
                    CHECK(actual.percussion_diagnostics().routed_detector);
                    CHECK(actual.percussion_diagnostics().readiness < 1.0);
                    segment(actual, reference, profile, model, 193, true);
                    ++counts.lifecycle_cases;
                }
            }
        }
    }
}

void identical_future(Engine actual, Engine untouched) {
    std::array<float, 113> first{}, expected_first{};
    process(actual, 113, first);
    process(untouched, 113, expected_first);
    exact_audio(first, expected_first);
    CHECK(inspect(actual) == inspect(untouched));
    // Expose preserved readiness and retained banks after any rejected change,
    // including when rejection occurred with a dirty coefficient cache.
    const std::array<Event, 2> returning{{
        {0, EventType::SelectBank, Manual::Upper, 0, 1},
        {0, EventType::SelectBank, Manual::Lower, 0, 0},
    }};
    flush(actual, returning);
    flush(untouched, returning);
    std::array<float, 97> second{}, expected_second{};
    process(actual, 97, second);
    process(untouched, 97, expected_second);
    exact_audio(second, expected_second);
    CHECK(inspect(actual) == inspect(untouched));
}

Engine rejection_fixture(const RuntimeProfile& profile, double rate,
                         bool cancelled, bool clean_cache) {
    auto result = prepared(profile, lifecycle_model(ContactMode::LinearTravel), rate);
    auto controls = initial_controls();
    controls.fixed_registrations = {FixedRegistration::E, FixedRegistration::A};
    controls.route_enabled = {!cancelled, false};
    restore_live(result, round_trip(controls));
    if (clean_cache) {
        // A render rebuilds the coefficients; a following advance with no
        // contact-bit change leaves that cache clean. Observe this boundary
        // instead of assuming that an arbitrary final travel frame is clean.
        bool settled_connections = false;
        for (unsigned attempt = 0; attempt < 64 && !settled_connections; ++attempt) {
            const auto before = inspect(result);
            process(result, 1);
            const auto after = inspect(result);
            settled_connections = true;
            for (std::size_t manual = 0; manual < kManualCount; ++manual) {
                for (std::size_t key = 0; key < kManualKeyCount; ++key) {
                    settled_connections = settled_connections &&
                        before.history.contacts[manual][key].closed ==
                        after.history.contacts[manual][key].closed;
                }
            }
        }
        CHECK(settled_connections);
    }
    return result;
}

void rejected_rate(const Engine& original, double rate, Status expected) {
    auto actual = original;
    const auto before = inspect(actual);
    CHECK(actual.reconfigure_sample_rate(rate) == expected);
    CHECK(inspect(actual) == before);
    identical_future(actual, original);
    ++counts.rejected_rates;
}

void rejected_restore(const Engine& original, const ControlSnapshot& bad) {
    auto actual = original;
    const auto before = inspect(actual);
    CHECK(!actual.restore_controls(bad));
    CHECK(inspect(actual) == before);
    identical_future(actual, original);
    ++counts.rejected_restores;
}

void rejection_continuation(const RuntimeProfile& profile) {
    const std::array<double, 7> bad_rates{
        0.0, -48000.0, 32000.0, 88200.0,
        std::numeric_limits<double>::quiet_NaN(),
        std::numeric_limits<double>::infinity(),
        std::nextafter(48000.0, std::numeric_limits<double>::infinity())};
    for (const auto rate : kRates) {
        for (const bool cancelled : {false, true}) {
            for (const bool clean_cache : {false, true}) {
                const auto original = rejection_fixture(profile, rate, cancelled, clean_cache);
                for (const auto bad : bad_rates) rejected_rate(original, bad, Status::InvalidSpec);
                const auto good = original.controls_snapshot();
                auto bad = good;
                bad.fixed_registrations[0] = static_cast<FixedRegistration>(10);
                bad.route_enabled[0] = false;
                rejected_restore(original, bad);
                bad = good;
                bad.fixed_registrations[1] = static_cast<FixedRegistration>(255);
                rejected_restore(original, bad);
                bad = good;
                bad.selected_banks[1] = static_cast<DrawbarBank>(2);
                rejected_restore(original, bad);
                bad = good;
                bad.drawbars[1][1][8] = 9;
                rejected_restore(original, bad);
                bad = good;
                bad.percussion.decay = static_cast<PercussionDecay>(2);
                rejected_restore(original, bad);
                bad = good;
                bad.pedal_drawbars[1] = 9;
                rejected_restore(original, bad);
                bad = good;
                bad.expression = std::numeric_limits<double>::quiet_NaN();
                rejected_restore(original, bad);
            }
        }
    }
    // Supported rates can still reject: one profile crosses Nyquist and another
    // violates the phase-increment floor. Both fixed and Cancel-held memory must
    // survive those deeper validation paths, with clean and dirty route caches.
    auto high = profile;
    high.sources.back().frequency_hz = 30000.0;
    auto tiny = profile;
    tiny.sources.back().frequency_hz = std::ldexp(44100.0, -53);
    for (const bool cancelled : {false, true}) {
        for (const bool clean_cache : {false, true}) {
            const auto high_engine = rejection_fixture(high, 96000.0, cancelled, clean_cache);
            rejected_rate(high_engine, 44100.0, Status::InvalidProfile);
            rejected_rate(high_engine, 48000.0, Status::InvalidProfile);
            const auto tiny_engine = rejection_fixture(tiny, 44100.0, cancelled, clean_cache);
            rejected_rate(tiny_engine, 48000.0, Status::InvalidProfile);
            rejected_rate(tiny_engine, 96000.0, Status::InvalidProfile);
        }
    }
}

} // namespace

int main() {
    const auto profile = load_test_profile();
    fixed_rate_restore_lifecycle(profile);
    rejection_continuation(profile);
    std::cout << "fixed registration lifecycle: " << counts.lifecycle_cases
              << " rate/route/contact scenarios, " << counts.rate_boundaries
              << " preserved rate boundaries, " << counts.live_restores
              << " live restores, " << counts.state_round_trips
              << " state4 round trips, " << counts.cold_loads << " cold loads, "
              << counts.rejected_rates << " rejected rates, " << counts.rejected_restores
              << " rejected restores, " << counts.exact_audio_frames
              << " exact audio frames; " << counts.phase_oracles << " phase, "
              << counts.position_oracles << " position, " << counts.contact_oracles
              << " contact-bit and " << counts.readiness_oracles
              << " readiness oracles; " << counts.snapshots << " full snapshots; passed\n";
}
