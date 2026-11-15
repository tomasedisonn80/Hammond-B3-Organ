#include "TestSupport.h"
#include "hammond/Engine.h"

#include <array>
#include <bit>
#include <cmath>
#include <cstdint>
#include <initializer_list>
#include <limits>
#include <span>

namespace {
using namespace hammond;
constexpr std::uint32_t kBlock = 1024;
constexpr std::uint64_t kSeed = 0x231b;
constexpr double kLargestGain = 0x1.555555555551cp-1;
constexpr double kNextGain = 0x1.555555555551dp-1;

void run(Engine& engine, std::uint32_t frames, std::span<float> output = {},
         std::span<const Event> events = {}) {
    const auto result = engine.process(frames, output, events);
    CHECK(result.status == Status::Ok && result.events_consumed == events.size());
}

void events(Engine& engine, std::initializer_list<Event> edits) {
    run(engine, 0, {}, {edits.begin(), edits.size()});
}

Engine prepared(const RuntimeProfile& profile, double rate, bool travel = false) {
    Engine engine;
    CHECK(engine.prepare(profile, {rate, kBlock, kSeed, 19},
        travel ? make_nominal_console_model() : make_legacy_console_model()) == Status::Ok);
    return engine;
}

// Independent maximum-capacity construction: eight circular neighbors per
// destination. All 91 rows have exact L1 sum 1/2; cycles must remain simultaneous.
SourceLeakage full_field() {
    std::array<SourceLeakageEdge, 728> edges{};
    std::size_t cursor = 0;
    for (std::size_t destination = 0; destination < 91; ++destination) {
        for (std::size_t offset = 1; offset <= 8; ++offset) {
            edges[cursor++] = {static_cast<ToneId>((destination + offset) % 91 + 1),
                               static_cast<ToneId>(destination + 1), 0.0625};
        }
    }
    SourceLeakage graph;
    CHECK(graph.prepare(edges) == Status::Ok);
    CHECK(graph.edge_count() == 728 && graph.max_row_absolute_gain_sum() == 0.5);
    return graph;
}

void same_history(const Engine& actual, const Engine& reference) {
    CHECK(actual.prepared() == reference.prepared());
    CHECK(actual.frame_clock() == reference.frame_clock());
    CHECK(actual.sample_rate() == reference.sample_rate());
    CHECK(actual.controls_snapshot() == reference.controls_snapshot());
    CHECK(actual.percussion_diagnostics() == reference.percussion_diagnostics());
    CHECK(actual.active_key_count() == reference.active_key_count());
    CHECK(actual.active_pedal_count() == reference.active_pedal_count());
    for (std::uint32_t source = 1; source <= 91; ++source) {
        double a = -1, b = -2;
        CHECK(actual.source_phase_turns(static_cast<ToneId>(source), a));
        CHECK(reference.source_phase_turns(static_cast<ToneId>(source), b));
        CHECK(std::bit_cast<std::uint64_t>(a) == std::bit_cast<std::uint64_t>(b));
    }
    for (const Manual manual : {Manual::Upper, Manual::Lower}) {
        for (std::uint32_t note = 36; note <= 96; ++note) {
            ContactKeySnapshot a{}, b{};
            CHECK(actual.contact_snapshot(manual, note, a));
            CHECK(reference.contact_snapshot(manual, note, b));
            CHECK(a == b && actual.key_down(manual, note) == reference.key_down(manual, note));
        }
    }
    PedalContactStates a{}, b{};
    CHECK(actual.pedal_contacts_snapshot(a) && reference.pedal_contacts_snapshot(b));
    CHECK(a == b);
}

// Comparing positive future samples also checks private caches and trajectory
// segment bookkeeping that copied public snapshots alone cannot establish.
void same_future(Engine actual, Engine reference) {
    std::array<float, 127> a{}, b{};
    run(actual, 127, a);
    run(reference, 43, std::span<float>(b).first(43));
    run(reference, 84, std::span<float>(b).subspan(43));
    for (std::size_t i = 0; i < a.size(); ++i)
        CHECK(std::bit_cast<std::uint32_t>(a[i]) == std::bit_cast<std::uint32_t>(b[i]));
    same_history(actual, reference);
    CHECK(actual.last_pedal_frame() == reference.last_pedal_frame());
    CHECK(actual.source_leakage_configuration() == reference.source_leakage_configuration());
}

RuntimeProfile aligned_profile(const RuntimeProfile& nominal, double rate, double sign) {
    auto profile = nominal;
    for (auto& source : profile.sources) {
        source.base_phase_turns = 0;
        source.peak_amplitude = 1;
    }
    const auto phase_seed = prepared(profile, rate);
    const double desired = sign > 0 ? 0.25 : 0.75;
    for (std::size_t index = 0; index < 91; ++index) {
        double phase = -1;
        CHECK(phase_seed.source_phase_turns(static_cast<ToneId>(index + 1), phase));
        double base = desired - phase;
        if (base < 0) base += 1;
        profile.sources[index].base_phase_turns = base;
    }
    // Establish the fixture's exact first source frame, not a leakage oracle.
    TonewheelBank sources;
    CHECK(sources.prepare(profile, rate, kSeed) == Status::Ok);
    SourceLeakageFrame first{};
    sources.process_frame(first);
    for (const double value : first) CHECK(value == sign);
    return profile;
}

void whole_field_headroom(const RuntimeProfile& nominal) {
    const auto graph = full_field();
    CHECK(std::nextafter(kLargestGain, 1.0) == kNextGain);
    // Pedal 1 has two connected +1 branches on each bus. At 9*eta each source
    // is exactly 17*eta and each bus is 34*eta. The unchanged pedal mixer permits
    // same-expression contraction: independently enumerating every per-term
    // rounding choice gives exactly 33*eta or 34*eta for either mixture row.
    // Rows need not contract identically. Normal fixtures retain one exact
    // result; no leakage bound, gain threshold or tolerance is changed.
    // See docs/reviews/SOURCE_LEAKAGE_PORTABILITY.md for the retained failure
    // and exact rational derivation of the permitted downstream tuples.
    struct Fixture { double gain, bound, bus; std::array<double, 2> mixtures; };
    constexpr std::array<Fixture, 3> fixtures{{
        {0x0.0000000000009p-1022, 0x0.000000000001fp-1022,
         0x0.0000000000022p-1022,
         {0x0.0000000000021p-1022, 0x0.0000000000022p-1022}},
        {0.5, 0x1.8000000000041p-1, 1.5, {1.5, 1.5}},
        {kLargestGain, 1.0, 0x1.fffffffffffacp+0,
         {0x1.fffffffffffacp+0, 0x1.fffffffffffacp+0}},
    }};
    for (const double rate : {44100.0, 48000.0, 96000.0}) {
        for (const double sign : {1.0, -1.0}) {
            const auto profile = aligned_profile(nominal, rate, sign);
            for (const auto& fixture : fixtures) {
                const auto base = prepared(profile, rate);
                for (const PedalDrawbarPositions positions :
                     {PedalDrawbarPositions{8, 0}, PedalDrawbarPositions{0, 8},
                      PedalDrawbarPositions{8, 8}}) {
                    auto engine = base;
                    CHECK(engine.set_source_leakage(graph, fixture.gain) == Status::Ok);
                    const auto configuration = engine.source_leakage_configuration();
                    CHECK(configuration.edge_count == 728);
                    CHECK(configuration.guarded_output_bound == fixture.bound);
                    CHECK(configuration.guarded_output_bound <= 1.0);
                    events(engine, {{0, EventType::PedalOn, Manual::Lower, 1, 127},
                        {0, EventType::PedalDrawbar, Manual::Lower, 0,
                         static_cast<double>(positions[0])},
                        {0, EventType::PedalDrawbar, Manual::Lower, 1,
                         static_cast<double>(positions[1])}});
                    const auto before = engine;
                    CHECK(engine.set_source_leakage(graph, kNextGain) == Status::InvalidSpec);
                    CHECK(engine.source_leakage_configuration() == configuration);
                    same_history(engine, before);
                    CHECK(engine.last_pedal_frame() == before.last_pedal_frame());
                    same_future(engine, before);
                    std::array<float, 1> output{};
                    run(engine, 1, output);
                    const auto actual = engine.last_pedal_frame();
                    CHECK(actual.valid && actual.frame == 19 && actual.sample_rate == rate);
                    CHECK(actual.positions == positions);
                    for (const double bus : actual.buses) CHECK(bus == sign * fixture.bus);
                    bool matched_exact_tuple = false;
                    for (const double first : fixture.mixtures) {
                        for (const double second : fixture.mixtures) {
                            const double expected_first = sign * first;
                            const double expected_second = sign * second;
                            const double expected_voice =
                                (positions[0] == 8 ? expected_first : 0.0) +
                                (positions[1] == 8 ? expected_second : 0.0);
                            matched_exact_tuple |=
                                actual.voice.mixtures[0] == expected_first &&
                                actual.voice.mixtures[1] == expected_second &&
                                actual.voice.output == expected_voice &&
                                output[0] == static_cast<float>(
                                    expected_voice * profile.output_gain);
                        }
                    }
                    CHECK(matched_exact_tuple);
                }
            }
        }
    }
}

void active_console(Engine& engine) {
    events(engine, {{0, EventType::Drawbar, Manual::Upper, 2, 8},
        {0, EventType::Drawbar, Manual::Lower, 3, 6},
        {0, EventType::Percussion, Manual::Upper, 0, 1},
        {0, EventType::NoteOn, Manual::Upper, 63, 127},
        {0, EventType::NoteOn, Manual::Lower, 48, 127},
        {0, EventType::PedalOn, Manual::Lower, 1, 127},
        {0, EventType::PedalDrawbar, Manual::Lower, 0, 7},
        {0, EventType::PedalDrawbar, Manual::Lower, 1, 5}});
    run(engine, 1024);
    events(engine, {{0, EventType::NoteOff, Manual::Upper, 63, 0},
        {0, EventType::KeyPosition, Manual::Lower, 48, 0.37}});
    run(engine, 31);
    ContactKeySnapshot moving{};
    CHECK(engine.contact_snapshot(Manual::Upper, 63, moving));
    CHECK(moving.target == 0 && moving.position > 0 && moving.position < 1);
    CHECK(engine.percussion_diagnostics().readiness < 1.0);
}

void lifecycle_in_motion(const RuntimeProfile& profile) {
    const auto graph = full_field();
    for (const double rate : {44100.0, 48000.0, 96000.0}) {
        auto baseline = prepared(profile, rate, true);
        active_console(baseline);
        auto engine = baseline;
        const auto old_pedal = engine.last_pedal_frame();
        CHECK(engine.set_source_leakage(graph, 0.5) == Status::Ok);
        same_history(engine, baseline);
        CHECK(engine.last_pedal_frame() == old_pedal);
        run(engine, 73);
        run(baseline, 73);
        same_history(engine, baseline);
        const auto before_mute = engine.last_pedal_frame();
        CHECK(engine.set_source_leakage(graph, 0.0) == Status::Ok);
        CHECK(engine.last_pedal_frame() == before_mute);
        CHECK(engine.source_leakage_configuration().guarded_output_bound == 0);
        std::array<float, 97> silent{};
        run(engine, 97, silent);
        run(baseline, 97);
        for (const float value : silent) CHECK(value == 0.0F);
        same_history(engine, baseline);
        CHECK(engine.last_pedal_frame().voice.output == 0);
        const auto retained = engine.last_pedal_frame();
        const auto next_rate = rate == 96000.0 ? 44100.0 : 96000.0;
        CHECK(engine.reconfigure_sample_rate(next_rate) == Status::Ok);
        CHECK(baseline.reconfigure_sample_rate(next_rate) == Status::Ok);
        CHECK(engine.last_pedal_frame() == retained);
        auto controls = baseline.controls_snapshot();
        controls.expression = 0.625;
        CHECK(engine.restore_controls(controls) && baseline.restore_controls(controls));
        CHECK(engine.source_leakage_configuration().configured);
        CHECK(engine.source_leakage_configuration().input_gain == 0);
        CHECK(engine.last_pedal_frame() == retained);
        CHECK(engine.clear_source_leakage() == Status::Ok);
        CHECK(engine.source_leakage_configuration() == SourceLeakageConfiguration{});
        CHECK(engine.last_pedal_frame() == retained);
        same_history(engine, baseline);
        same_future(engine, baseline);
        CHECK(engine.clear_source_leakage() == Status::Ok);
        same_future(engine, baseline);
    }
}

void rejected_transitions(const RuntimeProfile& nominal) {
    const auto graph = full_field();
    SourceLeakage unprepared;
    Engine cold;
    CHECK(cold.set_source_leakage(unprepared, std::numeric_limits<double>::quiet_NaN()) ==
          Status::NotPrepared);
    CHECK(cold.clear_source_leakage() == Status::NotPrepared);
    CHECK(cold.source_leakage_configuration() == SourceLeakageConfiguration{});

    auto profile = nominal;
    profile.sources[90].frequency_hz = 30000; // Valid at 96 kHz, invalid at 48 kHz.
    auto engine = prepared(profile, 96000.0, true);
    active_console(engine);
    CHECK(engine.set_source_leakage(graph, 0.5) == Status::Ok);
    run(engine, 11);
    const auto baseline = engine;
    const auto reject = [&](Status actual, Status expected) {
        CHECK(actual == expected);
        same_history(engine, baseline);
        CHECK(engine.last_pedal_frame() == baseline.last_pedal_frame());
        CHECK(engine.source_leakage_configuration() == baseline.source_leakage_configuration());
        same_future(engine, baseline);
    };
    for (const double gain : {-1.0, std::nextafter(1.0, 2.0),
                             std::numeric_limits<double>::quiet_NaN(),
                             std::numeric_limits<double>::infinity()})
        reject(engine.set_source_leakage(unprepared, gain), Status::InvalidSpec);
    reject(engine.set_source_leakage(unprepared, 0.5), Status::InvalidProfile);
    reject(engine.set_source_leakage(graph, kNextGain), Status::InvalidSpec);
    reject(engine.reconfigure_sample_rate(48000.0), Status::InvalidProfile);
    reject(engine.reconfigure_sample_rate(12345.0), Status::InvalidSpec);
    reject(engine.prepare(profile, {48000.0, kBlock, kSeed, 0}), Status::InvalidProfile);
    reject(engine.prepare(nominal, {96000.0, 0, kSeed, 0}), Status::InvalidSpec);
    auto invalid_console = make_nominal_console_model();
    invalid_console.contacts.keys[1][60].off_thresholds[8] = 1.0;
    reject(engine.prepare(nominal, {96000.0, kBlock, kSeed, 0}, invalid_console),
           Status::InvalidProfile);
    CHECK(engine.reconfigure_sample_rate(96000.0) == Status::Ok);
    same_future(engine, baseline);
    CHECK(engine.prepare(nominal, {96000.0, kBlock, kSeed, 19},
                         make_nominal_console_model()) == Status::Ok);
    CHECK(engine.source_leakage_configuration() == SourceLeakageConfiguration{});
    same_future(engine, prepared(nominal, 96000.0, true));
}
} // namespace

int main() {
    const auto profile = load_test_profile();
    whole_field_headroom(profile);
    lifecycle_in_motion(profile);
    rejected_transitions(profile);
    return 0;
}
