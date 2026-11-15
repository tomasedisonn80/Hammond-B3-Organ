#include "TestSupport.h"
#include "hammond/Engine.h"

#include <algorithm>
#include <array>
#include <bit>
#include <cmath>
#include <cstdint>
#include <initializer_list>
#include <limits>
#include <span>

namespace {

using namespace hammond;
constexpr std::uint32_t kBlock = 257;
constexpr std::uint64_t kSeed = 739;
constexpr std::array<double, 3> kRates{44100.0, 48000.0, 96000.0};

void process(Engine& engine, std::uint32_t frames, std::span<float> output = {},
             std::span<const Event> events = {}) {
    const auto result = engine.process(frames, output, events);
    CHECK(result.status == Status::Ok);
    CHECK(result.events_consumed == events.size());
}

void flush(Engine& engine, std::initializer_list<Event> events) {
    std::array<float, 2> sentinel{17.0F, -23.0F};
    const auto before = sentinel;
    const auto clock = engine.frame_clock();
    process(engine, 0, sentinel, {events.begin(), events.size()});
    CHECK(sentinel == before);
    CHECK(engine.frame_clock() == clock);
}

Engine prepared(const RuntimeProfile& profile, double rate = 48000.0,
                bool travel = false) {
    Engine engine;
    CHECK(engine.prepare(profile, {rate, kBlock, kSeed, 0},
        travel ? make_nominal_console_model() : make_legacy_console_model()) == Status::Ok);
    return engine;
}

void same_audio(std::span<const float> actual, std::span<const float> expected) {
    CHECK(actual.size() == expected.size());
    for (std::size_t i = 0; i < actual.size(); ++i) {
        CHECK(std::bit_cast<std::uint32_t>(actual[i]) ==
              std::bit_cast<std::uint32_t>(expected[i]));
    }
}

void same_dynamics(const Engine& actual, const Engine& expected) {
    CHECK(actual.frame_clock() == expected.frame_clock());
    CHECK(actual.sample_rate() == expected.sample_rate());
    CHECK(actual.controls_snapshot() == expected.controls_snapshot());
    CHECK(actual.percussion_diagnostics() == expected.percussion_diagnostics());
    CHECK(actual.active_key_count() == expected.active_key_count());
    CHECK(actual.active_pedal_count() == expected.active_pedal_count());
    for (std::size_t i = 1; i <= kToneSourceCount; ++i) {
        double a = -1.0, b = -2.0;
        CHECK(actual.source_phase_turns(static_cast<ToneId>(i), a));
        CHECK(expected.source_phase_turns(static_cast<ToneId>(i), b));
        CHECK(std::bit_cast<std::uint64_t>(a) == std::bit_cast<std::uint64_t>(b));
    }
    for (const auto manual : {Manual::Upper, Manual::Lower}) {
        for (std::uint32_t note = kMinManualMidiNote; note <= kMaxManualMidiNote; ++note) {
            CHECK(actual.key_down(manual, note) == expected.key_down(manual, note));
            ContactKeySnapshot a{}, b{};
            CHECK(actual.contact_snapshot(manual, note, a));
            CHECK(expected.contact_snapshot(manual, note, b));
            CHECK(a == b);
        }
    }
    PedalContactStates a{}, b{};
    CHECK(actual.pedal_contacts_snapshot(a));
    CHECK(expected.pedal_contacts_snapshot(b));
    CHECK(a == b);
}

void same_future(Engine actual, Engine expected) {
    same_dynamics(actual, expected);
    CHECK(actual.last_pedal_frame() == expected.last_pedal_frame());
    CHECK(actual.source_leakage_configuration() == expected.source_leakage_configuration());
    std::array<float, 113> a{}, b{};
    process(actual, static_cast<std::uint32_t>(a.size()), a);
    process(expected, static_cast<std::uint32_t>(b.size()), b);
    same_audio(a, b);
    same_dynamics(actual, expected);
    CHECK(actual.last_pedal_frame() == expected.last_pedal_frame());
}

void play_console(Engine& engine) {
    flush(engine, {{0, EventType::Drawbar, Manual::Upper, 2, 8.0},
                   {0, EventType::Drawbar, Manual::Lower, 1, 6.0},
                   {0, EventType::Percussion, Manual::Upper, 0, 1.0},
                   {0, EventType::NoteOn, Manual::Upper, 60, 100.0},
                   {0, EventType::NoteOn, Manual::Lower, 48, 100.0},
                   {0, EventType::PedalDrawbar, Manual::Lower, 0, 8.0},
                   {0, EventType::PedalDrawbar, Manual::Lower, 1, 5.0},
                   {0, EventType::PedalOn, Manual::Lower, 1, 100.0}});
}

void identity_at_all_rates(const RuntimeProfile& profile) {
    SourceLeakage empty;
    CHECK(empty.prepare({}) == Status::Ok);
    for (double rate : kRates) {
        for (bool travel : {false, true}) {
            Engine original = prepared(profile, rate, travel);
            Engine identity = original;
            CHECK(identity.set_source_leakage(empty, 1.0) == Status::Ok);
            CHECK(identity.source_leakage_configuration().configured);
            play_console(original);
            play_console(identity);
            std::array<float, kBlock> a{}, b{};
            process(original, kBlock, a);
            // Different partitions still consume one source frame per sample.
            std::size_t offset = 0;
            while (offset < b.size()) {
                const auto count = std::min<std::size_t>(17, b.size() - offset);
                process(identity, static_cast<std::uint32_t>(count),
                        std::span<float>(b).subspan(offset, count));
                offset += count;
            }
            same_audio(a, b);
            same_dynamics(original, identity);
            CHECK(original.last_pedal_frame() == identity.last_pedal_frame());
            for (Engine* engine : {&original, &identity}) {
                flush(*engine, {{0, EventType::AllNotesOff, Manual::Upper, 0, 0.0},
                                {0, EventType::AllNotesOff, Manual::Lower, 0, 0.0},
                                {0, EventType::PedalAllNotesOff, Manual::Lower, 0, 0.0}});
                process(*engine, 91); // Silent/disconnected time is real time.
            }
            process(original, kBlock, a);
            process(identity, kBlock, b);
            same_audio(a, b);
            same_dynamics(original, identity);
        }
        // Negative-zero expression is admitted and produces observable -0 when
        // the input is silent. The identity path must preserve its exact bits.
        Engine original = prepared(profile, rate);
        Engine identity = original;
        CHECK(identity.set_source_leakage(empty, 1.0) == Status::Ok);
        flush(original, {{0, EventType::Expression, Manual::Upper, 0, -0.0}});
        flush(identity, {{0, EventType::Expression, Manual::Upper, 0, -0.0}});
        std::array<float, 1> a{}, b{};
        process(original, 1, a);
        process(identity, 1, b);
        CHECK(std::signbit(a[0]));
        same_audio(a, b);
    }
}

void one_edge_manual_and_percussion(const RuntimeProfile& nominal) {
    // Destination key MIDI60 is held; donor MIDI72 is never held. Only the
    // donor oscillator has nonzero amplitude, exposing the actual insertion.
    for (double rate : kRates) {
        for (unsigned route = 0; route < 3; ++route) {
            auto profile = nominal;
            const Manual manual = route == 1 ? Manual::Lower : Manual::Upper;
            const std::size_t drawbar = route == 2 ? 3 : 2;
            const ToneId destination = profile.manual_map[60 - kMinManualMidiNote][drawbar];
            const ToneId donor = profile.manual_map[72 - kMinManualMidiNote][drawbar];
            CHECK(destination != donor);
            for (auto& source : profile.sources) source.peak_amplitude = 0.0;
            profile.sources[static_cast<std::size_t>(donor) - 1].peak_amplitude = 0.75;
            constexpr double coefficient = -0.125, gain = 0.5;
            SourceLeakage graph;
            const std::array edges{SourceLeakageEdge{donor, destination, coefficient}};
            CHECK(graph.prepare(edges) == Status::Ok);
            Engine engine = prepared(profile, rate);
            CHECK(engine.set_source_leakage(graph, gain) == Status::Ok);
            if (route == 2) {
                flush(engine, {{0, EventType::Percussion, Manual::Upper, 0, 1.0}});
            } else {
                flush(engine, {{0, EventType::Drawbar, manual,
                                static_cast<std::uint8_t>(drawbar), 8.0}});
            }
            flush(engine, {{0, EventType::NoteOn, manual, 60, 127.0}});
            CHECK(!engine.key_down(manual, 72));
            TonewheelBank reference;
            CHECK(reference.prepare(profile, rate, kSeed) == Status::Ok);
            bool heard_donor = false;
            for (std::uint32_t frame = 0; frame < 160; ++frame) {
                if (frame == 96) flush(engine, {{0, EventType::Cancel, manual, 0, 0.0}});
                if (frame == 128) flush(engine, {{0, EventType::SelectBank, manual, 0, 1.0}});
                SourceLeakageFrame source{};
                reference.process_frame(source);
                const double coupled = gain * source[static_cast<std::size_t>(destination) - 1] +
                    coefficient * (gain * source[static_cast<std::size_t>(donor) - 1]);
                const double voice_gain = route == 2 ? engine.percussion_diagnostics().gain :
                    profile.drawbar_gains[8];
                const bool connected = frame < 96 || frame >= 128;
                const double expected = connected ? coupled * voice_gain * profile.output_gain : 0.0;
                std::array<float, 1> output{};
                process(engine, 1, output);
                const double tolerance = 8.0 * std::numeric_limits<float>::epsilon() *
                    std::max(0.001, std::abs(expected));
                CHECK_NEAR(output[0], expected, tolerance);
                if (!connected) CHECK(output[0] == 0.0F);
                heard_donor = heard_donor || output[0] != 0.0F;
            }
            CHECK(heard_donor);
            CHECK(engine.active_key_count() == 1);
        }
    }
}

SourceLeakage full_row(ToneId destination) {
    std::array<SourceLeakageEdge, 8> edges{};
    std::size_t count = 0;
    for (ToneId source = 1; count < edges.size(); ++source) {
        if (source != destination) edges[count++] = {source, destination, 0.0625};
    }
    SourceLeakage graph;
    CHECK(graph.prepare(edges) == Status::Ok);
    CHECK(graph.max_row_absolute_gain_sum() == 0.5);
    return graph;
}

void aligned_headroom_and_actual_pedals(const RuntimeProfile& nominal) {
    constexpr double eta = std::numeric_limits<double>::denorm_min();
    constexpr double largest = 0x1.555555555551cp-1;
    CHECK(compiled_pedal_routes()[0].tone.has_value());
    const auto destination = *compiled_pedal_routes()[0].tone;
    const auto graph = full_row(destination);
    for (double rate : kRates) {
        auto profile = nominal;
        for (auto& source : profile.sources) source.base_phase_turns = 0.0;
        TonewheelBank phase_probe;
        CHECK(phase_probe.prepare(profile, rate, kSeed) == Status::Ok);
        for (std::size_t i = 0; i < kToneSourceCount; ++i) {
            double phase = 0.0;
            CHECK(phase_probe.phase_turns(static_cast<ToneId>(i + 1), phase));
            profile.sources[i].peak_amplitude = 1.0;
            profile.sources[i].base_phase_turns = 0.25 - phase;
            if (profile.sources[i].base_phase_turns < 0.0)
                profile.sources[i].base_phase_turns += 1.0;
        }
        TonewheelBank aligned;
        CHECK(aligned.prepare(profile, rate, kSeed) == Status::Ok);
        SourceLeakageFrame raw{};
        aligned.process_frame(raw);
        for (double sample : raw) CHECK(sample == 1.0);
        for (double gain : {0.0, eta, 9.0 * eta,
                            std::numeric_limits<double>::min(), 0.5, largest}) {
            Engine engine = prepared(profile, rate);
            CHECK(engine.set_source_leakage(graph, gain) == Status::Ok);
            const auto configuration = engine.source_leakage_configuration();
            if (gain == 9.0 * eta) CHECK(configuration.guarded_output_bound == 31.0 * eta);
            if (gain == largest) CHECK(configuration.guarded_output_bound == 1.0);
            SourceLeakageFrame input{}, actual{};
            input.fill(gain);
            CHECK(graph.process_frame(input, actual) == Status::Ok);
            if (gain == 9.0 * eta)
                CHECK(actual[static_cast<std::size_t>(destination) - 1] == 17.0 * eta);
            for (double sample : actual) {
                CHECK(std::abs(sample) <= configuration.guarded_output_bound);
                CHECK(std::abs(sample) <= 1.0);
            }
            PedalBusKernel pedal;
            CHECK(pedal.prepare(compiled_pedal_routes(), nominal_pedal_reference_weights()) == Status::Ok);
            std::array<PedalContactEdit, kPedalContactCount> contacts{};
            for (std::size_t i = 0; i < contacts.size(); ++i)
                contacts[i] = {PedalId{1}, static_cast<std::uint8_t>(i), true};
            CHECK(pedal.apply_contacts(contacts) == Status::Ok);
            PedalBusFrame expected_buses{};
            CHECK(pedal.render_frame(actual, expected_buses) == Status::Ok);
            for (const PedalDrawbarPositions positions :
                 {PedalDrawbarPositions{8, 0}, PedalDrawbarPositions{0, 8}}) {
                Engine audition = engine;
                flush(audition, {{0, EventType::PedalOn, Manual::Lower, 1, 127.0},
                                {0, EventType::PedalDrawbar, Manual::Lower, 0,
                                 static_cast<double>(positions[0])},
                                {0, EventType::PedalDrawbar, Manual::Lower, 1,
                                 static_cast<double>(positions[1])}});
                std::array<float, 1> output{};
                process(audition, 1, output);
                const auto diagnostic = audition.last_pedal_frame();
                CHECK(diagnostic.valid && diagnostic.frame == 0 && diagnostic.sample_rate == rate);
                CHECK(diagnostic.buses == expected_buses);
                PedalVoiceFrame expected_voice{};
                CHECK(render_nominal_pedal_voice(expected_buses, positions, expected_voice) == Status::Ok);
                CHECK(diagnostic.voice == expected_voice);
                CHECK(output[0] == static_cast<float>(expected_voice.output * profile.output_gain));
            }
        }
    }
}

void admission_and_lifecycle(const RuntimeProfile& profile) {
    SourceLeakage unprepared, empty;
    CHECK(empty.prepare({}) == Status::Ok);
    const auto graph = full_row(91);
    Engine cold;
    CHECK(cold.source_leakage_configuration() == SourceLeakageConfiguration{});
    CHECK(cold.set_source_leakage(unprepared, -1.0) == Status::NotPrepared);
    CHECK(cold.clear_source_leakage() == Status::NotPrepared);

    Engine engine = prepared(profile, 48000.0, true);
    Engine baseline = engine;
    play_console(engine);
    play_console(baseline);
    CHECK(engine.set_source_leakage(graph, 0.5) == Status::Ok);
    process(engine, 121);
    process(baseline, 121);
    const auto before = engine;
    // Replacement preserves dynamic histories and owns its caller's graph.
    CHECK(engine.set_source_leakage(empty, 0.5) == Status::Ok);
    same_dynamics(engine, before);
    CHECK(engine.last_pedal_frame() == before.last_pedal_frame());
    CHECK(engine.source_leakage_configuration().edge_count == 0);
    auto caller_graph = graph;
    CHECK(engine.set_source_leakage(caller_graph, 0.5) == Status::Ok);
    CHECK(caller_graph.prepare({}) == Status::Ok);
    same_future(engine, before);
    for (double gain : {-1.0, 1.01, std::numeric_limits<double>::quiet_NaN(),
                        std::numeric_limits<double>::infinity(), 1.0,
                        0x1.555555555551dp-1}) {
        CHECK(engine.set_source_leakage(graph, gain) == Status::InvalidSpec);
        same_future(engine, before);
    }
    CHECK(engine.set_source_leakage(unprepared, -1.0) == Status::InvalidSpec);
    CHECK(engine.set_source_leakage(unprepared, 0.5) == Status::InvalidProfile);
    same_future(engine, before);
    auto bad_profile = profile;
    bad_profile.sources[90].peak_amplitude = 2.0;
    CHECK(engine.prepare(bad_profile, {48000.0, kBlock, kSeed, 0}) == Status::InvalidProfile);
    CHECK(engine.reconfigure_sample_rate(12345.0) == Status::InvalidSpec);
    CHECK(engine.reconfigure_sample_rate(48000.0) == Status::Ok);
    same_future(engine, before);

    const auto history = engine.last_pedal_frame();
    const auto configuration = engine.source_leakage_configuration();
    auto controls = engine.controls_snapshot();
    controls.expression = 0.75;
    CHECK(engine.restore_controls(controls));
    CHECK(baseline.restore_controls(controls));
    CHECK(engine.source_leakage_configuration() == configuration);
    CHECK(engine.last_pedal_frame() == history);
    CHECK(engine.reconfigure_sample_rate(96000.0) == Status::Ok);
    CHECK(baseline.reconfigure_sample_rate(96000.0) == Status::Ok);
    CHECK(engine.source_leakage_configuration() == configuration);
    CHECK(engine.last_pedal_frame() == history);
    same_dynamics(engine, baseline);
    const auto before_clear = engine;
    CHECK(engine.clear_source_leakage() == Status::Ok);
    CHECK(engine.source_leakage_configuration() == SourceLeakageConfiguration{});
    same_dynamics(engine, before_clear);
    CHECK(engine.last_pedal_frame() == history);
    const auto cleared = engine;
    CHECK(engine.clear_source_leakage() == Status::Ok);
    same_future(engine, cleared);
    std::array<float, 71> a{}, b{};
    process(engine, static_cast<std::uint32_t>(a.size()), a);
    process(baseline, static_cast<std::uint32_t>(b.size()), b);
    same_audio(a, b);
    same_dynamics(engine, baseline);

    CHECK(engine.set_source_leakage(empty, 0.0) == Status::Ok);
    process(engine, static_cast<std::uint32_t>(a.size()), a);
    for (float sample : a) CHECK(sample == 0.0F);
    CHECK(engine.source_leakage_configuration().guarded_output_bound == 0.0);
    CHECK(engine.prepare(profile, {48000.0, kBlock, kSeed, 0}) == Status::Ok);
    same_future(engine, prepared(profile));
}

} // namespace

int main() {
    const auto profile = load_test_profile();
    identity_at_all_rates(profile);
    one_edge_manual_and_percussion(profile);
    aligned_headroom_and_actual_pedals(profile);
    admission_and_lifecycle(profile);
    return 0;
}
