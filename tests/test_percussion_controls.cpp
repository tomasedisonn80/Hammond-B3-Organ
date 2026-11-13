#include "TestSupport.h"
#include "hammond/ControlStateIO.h"
#include "hammond/Engine.h"

#include <array>
#include <bit>
#include <sstream>

namespace {
using hammond::ControlSnapshot;
using hammond::DrawbarBank;
using hammond::Engine;
using hammond::Event;
using hammond::EventType;
using hammond::Manual;
using hammond::PercussionDecay;
using hammond::PercussionHarmonic;
using hammond::PercussionSettings;
using hammond::PercussionVolume;

constexpr auto upper = Manual::Upper;
constexpr auto lower = Manual::Lower;

// A control snapshot deliberately has no place for any member of this history.
struct DynamicHistory {
    std::uint64_t clock{};
    std::array<std::size_t, 3> key_counts{};
    std::array<std::array<bool, hammond::kManualKeyCount>, hammond::kManualCount> keys{};
    std::array<std::array<hammond::ContactKeySnapshot, hammond::kManualKeyCount>,
               hammond::kManualCount> contacts{};
    std::array<std::uint64_t, hammond::kToneSourceCount> phases{};
    std::uint64_t readiness{};
    bool physical_detector{};
    bool operator==(const DynamicHistory&) const = default;
};

DynamicHistory history(const Engine& engine) {
    DynamicHistory result;
    result.clock = engine.frame_clock();
    result.key_counts = {engine.active_key_count(), engine.active_key_count(upper),
                         engine.active_key_count(lower)};
    for (std::size_t manual = 0; manual < hammond::kManualCount; ++manual) {
        for (std::size_t key = 0; key < hammond::kManualKeyCount; ++key) {
            const auto midi = static_cast<std::uint32_t>(key) + hammond::kMinManualMidiNote;
            result.keys[manual][key] = engine.key_down(static_cast<Manual>(manual), midi);
            CHECK(engine.contact_snapshot(static_cast<Manual>(manual), midi,
                                          result.contacts[manual][key]));
        }
    }
    for (std::size_t source = 0; source < hammond::kToneSourceCount; ++source) {
        double phase = -1.0;
        CHECK(engine.source_phase_turns(static_cast<hammond::ToneId>(source + 1), phase));
        result.phases[source] = std::bit_cast<std::uint64_t>(phase);
    }
    const auto percussion = engine.percussion_diagnostics();
    CHECK(percussion.prepared);
    result.readiness = std::bit_cast<std::uint64_t>(percussion.readiness);
    result.physical_detector = percussion.physical_detector;
    return result;
}

void process_ok(Engine& engine, std::uint32_t frames, std::span<float> output = {},
                std::span<const Event> events = {}) {
    const auto result = engine.process(frames, output, events);
    CHECK(result.ok());
    CHECK(result.events_consumed == events.size());
}

Engine live_engine(const hammond::RuntimeProfile& profile) {
    Engine engine;
    CHECK(engine.prepare(profile, {48000.0, 1024, 17, 321},
                         hammond::make_nominal_console_model()) == hammond::Status::Ok);
    auto controls = engine.controls_snapshot();
    controls.drawbars[0][1] = {5, 4, 3, 2, 1, 2, 3, 4, 5};
    controls.drawbars[1][1] = {3, 2, 4, 1, 2, 1, 2, 3, 1};
    controls.percussion = {true, PercussionHarmonic::Third,
                           PercussionVolume::Soft, PercussionDecay::Fast};
    CHECK(engine.restore_controls(controls));
    const std::array held{
        Event{0, EventType::NoteOn, upper, 60, 100},
        Event{0, EventType::NoteOn, upper, 64, 100},
        Event{0, EventType::NoteOn, lower, 48, 100}};
    process_ok(engine, 512, {}, held);
    const std::array moving{
        Event{0, EventType::NoteOff, upper, 60, 0},
        Event{70, EventType::NoteOn, lower, 67, 100}};
    process_ok(engine, 100, {}, moving);
    hammond::ContactKeySnapshot release;
    CHECK(engine.contact_snapshot(upper, 60, release));
    CHECK(release.target == 0.0 && release.position > 0.0 && release.position < 1.0);
    hammond::ContactKeySnapshot press;
    CHECK(engine.contact_snapshot(lower, 67, press));
    CHECK(press.target == 1.0 && press.position > 0.0 && press.position < 1.0);
    CHECK(!engine.key_down(upper, 60) && engine.key_down(upper, 64));
    CHECK(engine.percussion_diagnostics().physical_detector);
    CHECK(engine.percussion_diagnostics().readiness > 0.0);
    CHECK(engine.percussion_diagnostics().readiness < 1.0);
    return engine;
}

void same_future(Engine actual, Engine expected) {
    for (unsigned block = 0; block < 4; ++block) {
        const std::array events{
            Event{0, EventType::NoteOff, upper, 64, 0},
            Event{23, EventType::NoteOn, upper, 72, 100},
            Event{91, EventType::AllNotesOff, lower, 0, 0}};
        std::array<float, 128> actual_audio{};
        std::array<float, 128> expected_audio{};
        const auto pending = block == 0 ? std::span<const Event>(events) : std::span<const Event>{};
        process_ok(actual, 128, actual_audio, pending);
        process_ok(expected, 128, expected_audio, pending);
        for (std::size_t sample = 0; sample < actual_audio.size(); ++sample) {
            CHECK(std::bit_cast<std::uint32_t>(actual_audio[sample]) ==
                  std::bit_cast<std::uint32_t>(expected_audio[sample]));
        }
        CHECK(actual.controls_snapshot() == expected.controls_snapshot());
        CHECK(actual.percussion_diagnostics() == expected.percussion_diagnostics());
        CHECK(history(actual) == history(expected));
    }
}

void test_ordinary_restore(const hammond::RuntimeProfile& profile) {
    auto engine = live_engine(profile);
    const auto before = history(engine);
    auto candidate = engine.controls_snapshot();
    candidate.expression = 0.25;
    candidate.drawbars[0][0].fill(7);
    candidate.drawbars[0][1].fill(2);
    candidate.selected_banks = {DrawbarBank::A, DrawbarBank::A};
    candidate.route_enabled = {false, true};
    candidate.percussion = {true, PercussionHarmonic::Second,
                            PercussionVolume::Normal, PercussionDecay::Slow};
    CHECK(engine.restore_controls(candidate));
    CHECK(engine.controls_snapshot() == candidate);
    CHECK(history(engine) == before);
    CHECK(!engine.percussion_diagnostics().eligible);

    for (unsigned switches = 0; switches < 16; ++switches) {
        candidate.percussion = {
            (switches & 1U) != 0,
            (switches & 2U) != 0 ? PercussionHarmonic::Third : PercussionHarmonic::Second,
            (switches & 4U) != 0 ? PercussionVolume::Soft : PercussionVolume::Normal,
            (switches & 8U) != 0 ? PercussionDecay::Fast : PercussionDecay::Slow};
        CHECK(engine.restore_controls(candidate));
        CHECK(engine.controls_snapshot().percussion == candidate.percussion);
        CHECK(history(engine) == before);
    }
}

void test_retention_through_routing(const hammond::RuntimeProfile& profile) {
    auto engine = live_engine(profile);
    const auto stored = engine.controls_snapshot().percussion;
    const auto before = history(engine);
    const std::array select_a{Event{0, EventType::SelectBank, upper, 0, 0}};
    process_ok(engine, 0, {}, select_a);
    CHECK(!engine.percussion_diagnostics().eligible);
    CHECK(engine.controls_snapshot().percussion == stored);
    CHECK(history(engine) == before);

    const std::array hidden_edit{Event{0, EventType::BankDrawbar, upper, 17, 8}};
    process_ok(engine, 0, {}, hidden_edit);
    CHECK(engine.controls_snapshot().drawbars[0][1][8] == 8);
    CHECK(engine.controls_snapshot().percussion == stored);
    CHECK(history(engine) == before);
    const std::array cancel{Event{0, EventType::Cancel, upper, 0, 0}};
    process_ok(engine, 0, {}, cancel);
    CHECK(!engine.controls_snapshot().route_enabled[0]);
    CHECK(engine.controls_snapshot().selected_banks[0] == DrawbarBank::A);
    CHECK(!engine.percussion_diagnostics().eligible);
    CHECK(engine.controls_snapshot().percussion == stored);
    CHECK(history(engine) == before);

    const std::array select_b{Event{0, EventType::SelectBank, upper, 0, 1}};
    process_ok(engine, 0, {}, select_b);
    CHECK(engine.percussion_diagnostics().eligible);
    CHECK(engine.percussion_diagnostics().routed_detector);
    CHECK(engine.controls_snapshot().percussion == stored);
    CHECK(history(engine) == before);
    process_ok(engine, 0, {}, cancel);
    CHECK(!engine.percussion_diagnostics().eligible);
    CHECK(engine.controls_snapshot().selected_banks[0] == DrawbarBank::B);
    CHECK(engine.controls_snapshot().percussion == stored);
    CHECK(history(engine) == before);
}

void test_legacy_restore_keeps_history(const hammond::RuntimeProfile& profile) {
    auto engine = live_engine(profile);
    const auto before = history(engine);
    auto destination = engine.controls_snapshot();
    std::istringstream legacy{
        "B3CONTROLS1\nexpression 0.5\n"
        "manual upper selected B route_enabled 1\n"
        "bank A 0 0 0 0 0 0 0 0 0\nbank B 8 7 6 5 4 3 2 1 0\n"
        "manual lower selected A route_enabled 0\n"
        "bank A 1 1 1 1 1 1 1 1 1\nbank B 0 0 0 0 0 0 0 0 0\nend\n"};
    std::string error;
    CHECK(hammond::parse_controls(legacy, destination, error));
    CHECK(error.empty());
    CHECK(destination.percussion == PercussionSettings{});
    CHECK(destination.expression == 0.5);
    CHECK(destination.selected_banks[1] == DrawbarBank::A);
    CHECK(!destination.route_enabled[1]);
    CHECK(engine.restore_controls(destination));
    CHECK(engine.controls_snapshot() == destination);
    CHECK(history(engine) == before);
    CHECK(!engine.percussion_diagnostics().eligible);
}

void test_failed_restores_and_parse(const hammond::RuntimeProfile& profile) {
    const auto reference = live_engine(profile);
    for (unsigned invalid : {2U, 127U, 255U}) {
        for (unsigned field = 0; field < 3; ++field) {
            auto engine = reference;
            auto candidate = engine.controls_snapshot();
            candidate.expression = 0.75;
            candidate.drawbars[0][1].fill(8);
            candidate.route_enabled = {false, false};
            candidate.percussion.enabled = false;
            if (field == 0) candidate.percussion.harmonic = static_cast<PercussionHarmonic>(invalid);
            if (field == 1) candidate.percussion.volume = static_cast<PercussionVolume>(invalid);
            if (field == 2) candidate.percussion.decay = static_cast<PercussionDecay>(invalid);
            CHECK(!engine.restore_controls(candidate));
            CHECK(engine.controls_snapshot() == reference.controls_snapshot());
            CHECK(history(engine) == history(reference));
            same_future(engine, reference);
        }
    }

    auto engine = reference;
    auto destination = engine.controls_snapshot();
    auto changed = destination;
    changed.expression = 0.125;
    changed.percussion = {};
    std::string valid;
    std::string error;
    CHECK(hammond::serialize_controls(changed, valid, error));
    // Rejection after reading valid changed controls must publish nothing.
    std::istringstream malformed(valid + "unsupported trailing record");
    CHECK(!hammond::parse_controls(malformed, destination, error));
    CHECK(!error.empty());
    CHECK(destination == reference.controls_snapshot());
    CHECK(engine.restore_controls(destination));
    CHECK(history(engine) == history(reference));
    same_future(engine, reference);
}
} // namespace

int main() {
    const auto profile = load_test_profile();
    test_ordinary_restore(profile);
    test_retention_through_routing(profile);
    test_legacy_restore_keeps_history(profile);
    test_failed_restores_and_parse(profile);
    std::cout << "Percussion control/history migration tests passed.\n";
}
