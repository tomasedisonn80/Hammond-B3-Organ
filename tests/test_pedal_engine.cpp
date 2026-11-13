#include "TestSupport.h"
#include "hammond/Engine.h"

#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <initializer_list>
#include <span>
#include <vector>

namespace {
using namespace hammond;
constexpr auto upper = Manual::Upper;
constexpr auto lower = Manual::Lower;
std::size_t audio_checks = 0;
std::size_t rejected_calls = 0;
std::size_t phase_checks = 0;

static_assert(static_cast<unsigned>(EventType::NoteOn) == 0);
static_assert(static_cast<unsigned>(EventType::KeyPosition) == 9);
static_assert(static_cast<unsigned>(EventType::PedalOn) == 10);
static_assert(static_cast<unsigned>(EventType::PedalOff) == 11);
static_assert(static_cast<unsigned>(EventType::PedalDrawbar) == 12);
static_assert(static_cast<unsigned>(EventType::PedalAllNotesOff) == 13);
static_assert(static_cast<unsigned>(Manual::Upper) == 0);
static_assert(static_cast<unsigned>(Manual::Lower) == 1);

Event pedal_on(std::uint8_t pedal, double velocity = 127.0, std::uint32_t offset = 0) {
    return {offset, EventType::PedalOn, lower, pedal, velocity};
}
Event pedal_off(std::uint8_t pedal, std::uint32_t offset = 0) {
    return {offset, EventType::PedalOff, lower, pedal, 0.0};
}
Event pedal_bar(std::uint8_t index, double position, std::uint32_t offset = 0) {
    return {offset, EventType::PedalDrawbar, lower, index, position};
}
Event pedal_panic() { return {0, EventType::PedalAllNotesOff, lower, 0, 0.0}; }

void process(Engine& engine, std::uint32_t frames, std::span<float> output = {},
             std::span<const Event> events = {}) {
    const auto result = engine.process(frames, output, events);
    CHECK(result.status == Status::Ok);
    CHECK(result.events_consumed == events.size());
}
void flush(Engine& engine, std::initializer_list<Event> events) {
    process(engine, 0, {}, {events.begin(), events.size()});
}
Engine prepared(const RuntimeProfile& profile, double rate = 48000.0,
                 std::uint64_t origin = 0, bool travel = false) {
    Engine engine;
    CHECK(engine.prepare(profile, {rate, 1024, 17, origin},
                         travel ? make_nominal_console_model() : make_legacy_console_model()) ==
          Status::Ok);
    return engine;
}
void same_double(double actual, double expected) {
    CHECK(std::bit_cast<std::uint64_t>(actual) == std::bit_cast<std::uint64_t>(expected));
}
void same_audio(std::span<const float> actual, std::span<const float> expected) {
    CHECK(actual.size() == expected.size());
    for (std::size_t i = 0; i < actual.size(); ++i) {
        CHECK(std::bit_cast<std::uint32_t>(actual[i]) ==
              std::bit_cast<std::uint32_t>(expected[i]));
        ++audio_checks;
    }
}
void same_diagnostic(const PedalRenderDiagnostics& actual,
                      const PedalRenderDiagnostics& expected) {
    CHECK(actual.valid == expected.valid && actual.frame == expected.frame);
    CHECK(actual.positions == expected.positions);
    same_double(actual.sample_rate, expected.sample_rate);
    for (std::size_t i = 0; i < kPedalBusCount; ++i) {
        same_double(actual.buses[i], expected.buses[i]);
    }
    for (std::size_t i = 0; i < kPedalDrawbarCount; ++i) {
        same_double(actual.voice.mixtures[i], expected.voice.mixtures[i]);
    }
    same_double(actual.voice.output, expected.voice.output);
}
void same_phases(const Engine& actual, const Engine& expected) {
    for (std::uint32_t id = 1; id <= kToneSourceCount; ++id) {
        double a = -1.0, e = -1.0;
        CHECK(actual.source_phase_turns(static_cast<ToneId>(id), a));
        CHECK(expected.source_phase_turns(static_cast<ToneId>(id), e));
        same_double(a, e);
        ++phase_checks;
    }
}
void same_state(const Engine& actual, const Engine& expected) {
    CHECK(actual.prepared() == expected.prepared());
    CHECK(actual.frame_clock() == expected.frame_clock());
    same_double(actual.sample_rate(), expected.sample_rate());
    CHECK(actual.controls_snapshot() == expected.controls_snapshot());
    same_double(actual.expression(), expected.expression());
    CHECK(actual.active_key_count() == expected.active_key_count());
    CHECK(actual.active_pedal_count() == expected.active_pedal_count());
    CHECK(actual.percussion_diagnostics() == expected.percussion_diagnostics());
    same_diagnostic(actual.last_pedal_frame(), expected.last_pedal_frame());
    PedalContactStates a{}, e{};
    CHECK(actual.pedal_contacts_snapshot(a) && expected.pedal_contacts_snapshot(e));
    CHECK(a == e);
    for (std::uint32_t pedal = 1; pedal <= kPedalCount; ++pedal) {
        const auto id = PedalId{static_cast<std::uint8_t>(pedal)};
        CHECK(actual.pedal_down(id) == expected.pedal_down(id));
    }
    for (const auto manual : {upper, lower}) {
        for (std::uint32_t note = 36; note <= 96; ++note) {
            CHECK(actual.key_down(manual, note) == expected.key_down(manual, note));
            ContactKeySnapshot ac{}, ec{};
            CHECK(actual.contact_snapshot(manual, note, ac));
            CHECK(expected.contact_snapshot(manual, note, ec));
            CHECK(ac == ec);
        }
    }
    same_phases(actual, expected);
}
void same_future(Engine actual, Engine expected) {
    same_state(actual, expected);
    std::array<float, 37> a{}, e{};
    process(actual, static_cast<std::uint32_t>(a.size()), a);
    process(expected, static_cast<std::uint32_t>(e.size()), e);
    same_audio(a, e);
    same_state(actual, expected);
}

void defaults_and_identity(const RuntimeProfile& profile) {
    Engine cold;
    CHECK(!cold.last_pedal_frame().valid);
    CHECK(cold.active_key_count() == 0 && cold.active_pedal_count() == 0);
    CHECK(!cold.pedal_down(PedalId{1}));
    bool bit = true;
    std::uint8_t bar = 99;
    PedalContactStates contacts;
    contacts.fill(true);
    const auto old = contacts;
    CHECK(!cold.pedal_contact_closed(PedalId{1}, 0, bit) && bit);
    CHECK(!cold.pedal_drawbar_position(0, bar) && bar == 99);
    CHECK(!cold.pedal_contacts_snapshot(contacts) && contacts == old);
    CHECK(cold.process(0, {}, {}).status == Status::NotPrepared);

    auto engine = prepared(profile, 48000.0, 1234);
    CHECK(engine.active_pedal_count() == 0 && !engine.last_pedal_frame().valid);
    CHECK(engine.pedal_contacts_snapshot(contacts));
    CHECK(std::none_of(contacts.begin(), contacts.end(), [](bool value) { return value; }));
    for (std::size_t i = 0; i < kPedalDrawbarCount; ++i) {
        CHECK(engine.pedal_drawbar_position(i, bar) && bar == 0);
    }
    CHECK(!engine.pedal_down(PedalId{0}) && !engine.pedal_down(PedalId{26}));
    bit = true;
    CHECK(!engine.pedal_contact_closed(PedalId{0}, 0, bit) && bit);
    CHECK(!engine.pedal_contact_closed(PedalId{1}, 8, bit) && bit);
    bar = 99;
    CHECK(!engine.pedal_drawbar_position(2, bar) && bar == 99);

    // One pedal closes eight states, including pedal 8's disconnected c2.
    flush(engine, {pedal_on(8), pedal_on(8, 1)});
    CHECK(engine.frame_clock() == 1234 && !engine.last_pedal_frame().valid);
    CHECK(engine.active_key_count() == 0 && engine.active_pedal_count() == 1);
    for (std::uint32_t i = 0; i < kPedalContactCount; ++i) {
        bit = false;
        CHECK(engine.pedal_contact_closed(PedalId{8}, i, bit) && bit);
    }
    flush(engine, {pedal_on(8, 0)});
    CHECK(engine.active_pedal_count() == 0);
    flush(engine, {pedal_on(8), pedal_off(8), pedal_on(8)});
    CHECK(engine.active_pedal_count() == 1);
    flush(engine, {pedal_panic()});
    CHECK(engine.active_pedal_count() == 0);
}

void single_source_voice_and_tag(const RuntimeProfile& original) {
    auto profile = original;
    for (auto& source : profile.sources) source.peak_amplitude = 0.0;
    profile.sources[0].peak_amplitude = 0.5;
    auto engine = prepared(profile, 48000.0, 500);
    TonewheelBank reference;
    CHECK(reference.prepare(profile, 48000.0, 17) == Status::Ok);
    flush(engine, {pedal_on(1), pedal_bar(0, 8),
                   Event{0, EventType::Expression, upper, 0, 0.75}});
    for (std::uint32_t frame = 0; frame < 79; ++frame) {
        std::array<double, kToneSourceCount> source{};
        reference.process_frame(source);
        std::array<float, 1> audio{};
        process(engine, 1, audio);
        // CSV p1/c1 is source1; all other sources are exactly muted. Independent
        // rational voice equations: z0=Brown/2; z1=Brown/8; only mixture1 is up.
        const float expected = static_cast<float>((source[0] * 0.5) *
                                                   profile.output_gain * 0.75);
        same_audio(audio, std::array<float, 1>{expected});
        const auto diagnostic = engine.last_pedal_frame();
        CHECK(diagnostic.valid && diagnostic.frame == 500 + frame);
        CHECK(diagnostic.sample_rate == 48000.0);
        CHECK((diagnostic.positions == PedalDrawbarPositions{8, 0}));
        same_double(diagnostic.buses[0], source[0]);
        CHECK(diagnostic.buses[1] == 0.0 && diagnostic.buses[2] == 0.0 &&
              diagnostic.buses[3] == 0.0);
        same_double(diagnostic.voice.mixtures[0], source[0] * 0.5);
        same_double(diagnostic.voice.mixtures[1], source[0] * 0.125);
        same_double(diagnostic.voice.output, source[0] * 0.5);
        for (std::uint32_t id = 1; id <= kToneSourceCount; ++id) {
            double actual = 0.0, expected_phase = 0.0;
            CHECK(engine.source_phase_turns(static_cast<ToneId>(id), actual));
            CHECK(reference.phase_turns(static_cast<ToneId>(id), expected_phase));
            same_double(actual, expected_phase);
            ++phase_checks;
        }
    }
    const auto previous = engine.last_pedal_frame();
    flush(engine, {pedal_bar(0, 0), pedal_bar(1, 8), pedal_off(1)});
    same_diagnostic(engine.last_pedal_frame(), previous);
    CHECK(engine.reconfigure_sample_rate(96000.0) == Status::Ok);
    same_diagnostic(engine.last_pedal_frame(), previous);
    process(engine, 1); // Disconnected output still produces an actual diagnostic.
    CHECK(engine.last_pedal_frame().valid && engine.last_pedal_frame().frame == 579);
    CHECK(engine.last_pedal_frame().sample_rate == 96000.0);
    CHECK((engine.last_pedal_frame().positions == PedalDrawbarPositions{0, 8}));
    CHECK(engine.last_pedal_frame().voice.output == 0.0);
    CHECK(engine.prepare(profile, {44100.0, 1024, 17, 100}) == Status::Ok);
    CHECK(!engine.last_pedal_frame().valid && engine.active_pedal_count() == 0);
}

void division_independence(const RuntimeProfile& profile) {
    for (const bool travel : {false, true}) {
        auto actual = prepared(profile, 48000.0, 0, travel);
        auto reference = actual;
        for (auto* engine : {&actual, &reference}) {
            flush(*engine, {pedal_on(13), pedal_bar(0, 8), pedal_bar(1, 3)});
        }
        flush(actual, {{0, EventType::NoteOn, lower, 60, 100},
                        {0, EventType::Cancel, lower, 0, 0},
                        {0, EventType::AllNotesOff, lower, 0, 0}});
        std::array<float, 128> a{}, r{};
        process(actual, 128, a);
        process(reference, 128, r);
        same_audio(a, r);
        CHECK(actual.pedal_down(PedalId{13}));
        same_phases(actual, reference);

        // Pedals do not enter upper detector/recharge/masking, including while
        // all their controls are audible and the nominal manual is travelling.
        actual = prepared(profile, 48000.0, 0, travel);
        reference = actual;
        for (auto* engine : {&actual, &reference}) {
            flush(*engine, {{0, EventType::Percussion, upper, 0, 1},
                            {0, EventType::Drawbar, upper, 8, 8},
                            {0, EventType::NoteOn, upper, 60, 100}});
        }
        flush(actual, {pedal_on(1), pedal_on(25), pedal_bar(0, 8), pedal_bar(1, 8)});
        for (std::uint32_t frame = 0; frame < 513; ++frame) {
            process(actual, 1);
            process(reference, 1);
            CHECK(actual.percussion_diagnostics() == reference.percussion_diagnostics());
        }
        same_phases(actual, reference);
        const auto q = actual.percussion_diagnostics();
        flush(actual, {pedal_panic()});
        CHECK(actual.active_pedal_count() == 0 && actual.key_down(upper, 60));
        CHECK(actual.percussion_diagnostics() == q);

        // Muted, held pedals are a genuinely inaudible path, not fewer voices.
        actual = prepared(profile, 48000.0, 0, travel);
        reference = actual;
        for (auto* engine : {&actual, &reference}) {
            flush(*engine, {{0, EventType::Drawbar, upper, 2, 8},
                            {0, EventType::NoteOn, upper, 60, 100},
                            {0, EventType::Expression, upper, 0, -0.0}});
        }
        for (std::uint8_t pedal = 1; pedal <= 25; ++pedal) flush(actual, {pedal_on(pedal)});
        process(actual, 128, a);
        process(reference, 128, r);
        same_audio(a, r); // Includes the exact signed-zero output bits.
        CHECK(actual.active_pedal_count() == 25 && actual.active_key_count() == 1);
    }
}

void occupancy_restore_and_lifecycle(const RuntimeProfile& profile) {
    auto engine = prepared(profile, 48000.0, 99);
    std::vector<Event> on;
    for (const auto manual : {upper, lower}) {
        for (std::uint8_t note = 36; note <= 96; ++note) {
            on.push_back({0, EventType::NoteOn, manual, note, 100.0});
        }
    }
    for (std::uint8_t pedal = 1; pedal <= 25; ++pedal) on.push_back(pedal_on(pedal));
    process(engine, 0, {}, on);
    CHECK(engine.active_key_count() == 122 && engine.active_pedal_count() == 25);
    PedalContactStates contacts{};
    CHECK(engine.pedal_contacts_snapshot(contacts));
    CHECK(std::all_of(contacts.begin(), contacts.end(), [](bool value) { return value; }));
    flush(engine, {pedal_bar(0, 8), pedal_bar(1, 8)});
    std::array<float, 17> output{};
    process(engine, 17, output);
    CHECK(std::all_of(output.begin(), output.end(), [](float value) { return std::isfinite(value); }));
    const auto old = engine;
    auto controls = engine.controls_snapshot();
    controls.pedal_drawbars = {0, 0};
    controls.route_enabled[1] = false;
    CHECK(engine.restore_controls(controls));
    CHECK(engine.active_key_count() == 122 && engine.active_pedal_count() == 25);
    CHECK(engine.pedal_contacts_snapshot(contacts));
    CHECK(std::all_of(contacts.begin(), contacts.end(), [](bool value) { return value; }));
    same_phases(engine, old);
    same_diagnostic(engine.last_pedal_frame(), old.last_pedal_frame());
    CHECK(engine.frame_clock() == old.frame_clock());
    CHECK(engine.reconfigure_sample_rate(44100.0) == Status::Ok);
    same_phases(engine, old);
    same_diagnostic(engine.last_pedal_frame(), old.last_pedal_frame());
    CHECK(engine.active_pedal_count() == 25 && engine.controls_snapshot() == controls);
    const auto changed = engine;
    CHECK(engine.reconfigure_sample_rate(44100.0) == Status::Ok);
    same_future(engine, changed);
    CHECK(engine.reconfigure_sample_rate(88200.0) == Status::InvalidSpec);
    same_future(engine, changed);
    auto invalid = controls;
    invalid.pedal_drawbars[1] = 9;
    CHECK(!engine.restore_controls(invalid));
    same_future(engine, changed);
    auto invalid_profile = profile;
    invalid_profile.sources[0].peak_amplitude = 2.0;
    CHECK(engine.prepare(invalid_profile, {48000.0, 1024, 0, 0}) == Status::InvalidProfile);
    same_future(engine, changed);
}

void atomic_event_rejection(const RuntimeProfile& profile) {
    auto original = prepared(profile, 48000.0, 700, true);
    flush(original, {pedal_on(8), pedal_bar(0, 8),
                      Event{0, EventType::Drawbar, upper, 2, 8},
                      Event{0, EventType::NoteOn, upper, 60, 100}});
    process(original, 19);
    const std::array<Event, 17> invalid{
        Event{2, EventType::PedalOn, upper, 1, 127},
        Event{2, EventType::PedalOff, upper, 1, 0},
        Event{2, EventType::PedalDrawbar, upper, 0, 8},
        Event{2, EventType::PedalAllNotesOff, upper, 0, 0},
        pedal_on(0, 127, 2), pedal_on(26, 127, 2), pedal_on(1, -1, 2),
        pedal_on(1, 128, 2), pedal_on(1, 0.5, 2),
        pedal_on(1, std::numeric_limits<double>::quiet_NaN(), 2),
        Event{2, EventType::PedalOff, lower, 1, 1},
        pedal_off(0, 2), pedal_bar(2, 8, 2), pedal_bar(0, 9, 2),
        Event{2, EventType::PedalAllNotesOff, lower, 1, 0},
        Event{2, EventType::PedalAllNotesOff, lower, 0, 1},
        pedal_on(1, 127, 8)};
    for (const auto bad : invalid) {
        auto actual = original;
        std::array<float, 8> output;
        output.fill(-123.25F);
        const std::array<Event, 2> events{pedal_off(8), bad};
        const auto result = actual.process(8, output, events);
        CHECK(result.status == Status::InvalidEvent && result.events_consumed == 0);
        CHECK(std::all_of(output.begin(), output.end(), [](float x) { return x == -123.25F; }));
        same_future(actual, original);
        ++rejected_calls;
    }
    auto actual = original;
    std::array<float, 8> output;
    output.fill(-123.25F);
    const std::array<Event, 2> unsorted{pedal_off(8, 3), pedal_on(1, 127, 2)};
    CHECK(actual.process(8, output, unsorted).status == Status::InvalidEvent);
    same_future(actual, original);
    const std::array<Event, 1> zero_bad{pedal_on(1, 127, 1)};
    CHECK(actual.process(0, output, zero_bad).status == Status::InvalidEvent);
    same_future(actual, original);
    CHECK(std::all_of(output.begin(), output.end(), [](float x) { return x == -123.25F; }));
    rejected_calls += 2;
}

} // namespace

int main() {
    const auto profile = load_test_profile();
    defaults_and_identity(profile);
    single_source_voice_and_tag(profile);
    division_independence(profile);
    occupancy_restore_and_lifecycle(profile);
    atomic_event_rejection(profile);
    std::cout << "Pedal Engine passed: " << audio_checks << " exact audio comparisons, "
              << phase_checks << " exact phase comparisons, " << rejected_calls
              << " event rejection cases.\n";
}
