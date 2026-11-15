#include "TestSupport.h"
#include "hammond/Engine.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <initializer_list>
#include <limits>
#include <span>

namespace {
using namespace hammond;
constexpr std::size_t kCapacity = 1536;
constexpr long double kGain = 0.5L, kPositive = 0.125L, kNegative = -0.0625L;
struct Source { ToneId id; unsigned bin; double amplitude, phase, base; };

// Independently fixed before production execution: Python integer SplitMix64,
// seed zero, ascending IDs 1..91, top 53 bits / 2^53; base=(phase-offset) mod 1.
// All bases and initial additions are exact dyadics. Copying base phases between
// IDs would be WRONG: destinations 13/25 have different seeded offsets from
// donors 69/57. These literal corrections, not observed Engine samples/phases,
// align the donor-only default Engines with the actual original donor sources.
constexpr std::array<Source, 4> kOriginals{{
    {13, 3, 0.375, 0.375, 0x1.b3bcbf803e885p-1},
    {25, 11, 0.25, 0.5, 0x1.4507fc56157f2p-1},
    {57, 31, 0.375, 0.25, 0x1.fb3f97444c3f0p-5},
    {69, 7, 0.5, 0.125, 0x1.da06a944a2549p-1},
}};
constexpr std::array<Source, 2> kClones{{
    {13, 7, 0.5, 0.125, 0x1.33bcbf803e885p-1},
    {25, 31, 0.375, 0.25, 0x1.8a0ff8ac2afe4p-2},
}};
constexpr std::array<SourceLeakageEdge, 2> kEdges{{
    {69, 13, static_cast<double>(kPositive)},
    {57, 25, static_cast<double>(kNegative)},
}};
struct Counts {
    std::uint64_t fixtures{}, rendered_frames{}, waveform_samples{}, exact_zero_samples{};
    std::uint64_t phase_checks{}, history_checks{}, positive_samples{}, negative_samples{};
    long double maximum_error{}, maximum_output{}, maximum_leakage_delta{};
} counts;

RuntimeProfile profile_for(const RuntimeProfile& nominal, double rate, std::size_t role) {
    auto profile = nominal;
    for (auto& source : profile.sources) source.peak_amplitude = 0;
    const auto set = [&](const Source& source) {
        profile.sources[static_cast<std::size_t>(source.id) - 1] = {
            static_cast<double>(source.bin) * rate / 1024.0, source.amplitude, source.base};
    };
    if (role < 2) {
        for (const auto& source : kOriginals) set(source);
    } else {
        set(kClones[role - 2]);
    }
    // Fixed small output gain bounds the independent float-reference rounding
    // near cancellation; the contracted error threshold is never adjusted.
    profile.output_gain = 1.0 / 256.0;
    CHECK(profile.manual_map[0][2] == 13 && profile.manual_map[0][3] == 25);
    for (const auto source : profile.manual_map[0]) CHECK(source != 57 && source != 69);
    CHECK(profile.manual_map[80 - 36][2] == 57 && profile.manual_map[92 - 36][2] == 69);
    return profile;
}

// Linear-composition oracle: only engine[0] uses SourceLeakage. Engines 1/2/3
// use the unchanged source path and identical nominal contact/routing histories.
// This qualifies insertion before those consumers; it does not independently
// validate physical contact trajectories or the existing console implementation.
struct Fixture {
    std::array<Engine, 4> engines{};
    std::array<std::array<float, kCapacity>, 4> outputs{};
    double rate{};

    void process(Engine& engine, std::uint32_t frames, std::span<float> output = {}) {
        const auto result = engine.process(frames, output, {});
        CHECK(result.status == Status::Ok && result.events_consumed == 0);
        counts.rendered_frames += frames;
    }
    void phase(const Engine& engine, const Source& source) const {
        double actual = -1;
        CHECK(engine.source_phase_turns(source.id, actual));
        const double expected = std::fmod(source.phase + static_cast<double>(source.bin) *
            static_cast<double>(engine.frame_clock()) / 1024.0, 1.0);
        CHECK(actual == expected);
        ++counts.phase_checks;
    }
    ContactKeySnapshot contact(Manual manual) const {
        ContactKeySnapshot snapshot{};
        CHECK(engines[0].contact_snapshot(manual, 36, snapshot));
        return snapshot;
    }
    void histories() const {
        const auto& actual = engines[0];
        for (std::size_t role = 0; role < engines.size(); ++role) {
            const auto& engine = engines[role];
            CHECK(engine.frame_clock() == actual.frame_clock());
            CHECK(engine.controls_snapshot() == actual.controls_snapshot());
            CHECK(engine.percussion_diagnostics() == actual.percussion_diagnostics());
            CHECK(engine.active_key_count() == actual.active_key_count());
            CHECK(engine.active_pedal_count() == 0);
            for (const auto manual : {Manual::Upper, Manual::Lower}) {
                ContactKeySnapshot other{};
                CHECK(engine.contact_snapshot(manual, 36, other));
                CHECK(other == contact(manual));
                CHECK(engine.key_down(manual, 36) == actual.key_down(manual, 36));
                CHECK(!engine.key_down(manual, 80) && !engine.key_down(manual, 92));
                ++counts.history_checks;
            }
            if (role < 2) {
                for (const auto& source : kOriginals) phase(engine, source);
            } else {
                phase(engine, kClones[role - 2]);
                CHECK(!engine.source_leakage_configuration().configured);
            }
        }
        CHECK(!engines[1].source_leakage_configuration().configured);
        CHECK(actual.source_leakage_configuration().configured);
    }
    void events(std::initializer_list<Event> edits) {
        for (auto& engine : engines) {
            const auto clock = engine.frame_clock();
            const auto result = engine.process(0, {}, {edits.begin(), edits.size()});
            CHECK(result.status == Status::Ok && result.events_consumed == edits.size());
            CHECK(engine.frame_clock() == clock);
        }
        histories();
    }
    void selected(PresetSelection upper, PresetSelection lower) const {
        for (const auto manual : {Manual::Upper, Manual::Lower}) {
            PresetSelection actual{};
            CHECK(engines[0].selected_preset(manual, actual));
            CHECK(actual == (manual == Manual::Upper ? upper : lower));
        }
    }
    void moving(Manual manual, double target) const {
        const auto state = contact(manual);
        CHECK(state.target == target && state.position > 0 && state.position < 1);
        CHECK(state.position != state.target);
    }
    std::uint32_t milliseconds(double duration) const {
        return static_cast<std::uint32_t>(std::ceil(rate * duration / 1000.0));
    }
    void render(std::uint32_t frames, bool exact_zero = false, bool disconnected = false) {
        CHECK(frames > 0 && frames <= kCapacity);
        constexpr std::array<std::uint32_t, 6> partitions{1, 7, 31, 97, 13, 257};
        for (std::size_t role = 0; role < engines.size(); ++role) {
            std::uint32_t offset = 0;
            std::size_t partition = role;
            while (offset < frames) {
                const auto length = std::min(frames - offset,
                    partitions[partition++ % partitions.size()]);
                process(engines[role], length, disconnected ? std::span<float>{} :
                    std::span<float>(outputs[role]).subspan(offset, length));
                offset += length;
            }
        }
        if (!disconnected) {
            bool audible = false;
            for (std::size_t frame = 0; frame < frames; ++frame) {
                const long double baseline = outputs[1][frame];
                const long double positive = kPositive * outputs[2][frame];
                const long double negative = kNegative * outputs[3][frame];
                const long double expected = kGain * (baseline + positive + negative);
                const long double actual = outputs[0][frame];
                const long double tolerance = 8.0L * std::numeric_limits<float>::epsilon() *
                    std::max(0.001L, std::abs(expected));
                CHECK_NEAR(actual, expected, tolerance);
                CHECK(std::abs(actual) < 1.0L && std::abs(expected) < 1.0L);
                if (exact_zero) {
                    for (const auto& output : outputs) CHECK(output[frame] == 0.0F);
                    ++counts.exact_zero_samples;
                }
                audible = audible || actual != 0;
                counts.positive_samples += positive != 0 ? 1U : 0U;
                counts.negative_samples += negative != 0 ? 1U : 0U;
                counts.maximum_error = std::max(counts.maximum_error, std::abs(actual - expected));
                counts.maximum_output = std::max(counts.maximum_output, std::abs(actual));
                counts.maximum_leakage_delta = std::max(counts.maximum_leakage_delta,
                    std::abs(actual - kGain * baseline));
                ++counts.waveform_samples;
            }
            CHECK(audible != exact_zero);
        }
        histories();
    }
};
// Keep four full Engines and bounded output arrays out of small native stacks.
Fixture fixture;

void qualify(const RuntimeProfile& nominal, const SourceLeakage& graph,
             double rate, bool soft_fast) {
    auto& f = fixture;
    f.rate = rate;
    for (std::size_t role = 0; role < f.engines.size(); ++role) {
        CHECK(f.engines[role].prepare(profile_for(nominal, rate, role),
            {rate, static_cast<std::uint32_t>(kCapacity), 0, 0},
            make_nominal_console_model()) == Status::Ok);
    }
    CHECK(f.engines[0].set_source_leakage(graph, static_cast<double>(kGain)) == Status::Ok);
    f.events({{0, EventType::Drawbar, Manual::Upper, 2, 8},
              {0, EventType::Drawbar, Manual::Upper, 3, 5},
              {0, EventType::Drawbar, Manual::Lower, 2, 7},
              {0, EventType::Drawbar, Manual::Lower, 3, 6},
              {0, EventType::Expression, Manual::Upper, 0, 0.75},
              {0, EventType::Percussion, Manual::Upper, 0, 1},
              {0, EventType::Percussion, Manual::Upper, 2, soft_fast ? 1.0 : 0.0},
              {0, EventType::Percussion, Manual::Upper, 3, soft_fast ? 1.0 : 0.0}});
    f.selected(PresetSelection::BankB, PresetSelection::BankB);
    f.render(17, true);
    f.events({{0, EventType::NoteOn, Manual::Upper, 36, 1},
              {0, EventType::NoteOn, Manual::Lower, 36, 127}});
    f.render(f.milliseconds(4));
    for (const auto manual : {Manual::Upper, Manual::Lower}) {
        f.moving(manual, 1);
        const auto state = f.contact(manual);
        CHECK(state.closed[2] && state.closed[3] && !state.closed[8]);
    }
    f.render(f.milliseconds(6));
    CHECK(f.contact(Manual::Upper).position == 1 && f.contact(Manual::Lower).position == 1);
    CHECK(f.engines[0].percussion_diagnostics().eligible);
    CHECK(f.engines[0].percussion_diagnostics().readiness < 1);

    f.events({{0, EventType::SelectPreset, Manual::Upper, 0, 2},
              {0, EventType::SelectPreset, Manual::Lower, 0, 2}}); // Fixed D.
    f.selected(PresetSelection::D, PresetSelection::D);
    CHECK(!f.engines[0].percussion_diagnostics().eligible);
    f.render(f.milliseconds(3));
    f.events({{0, EventType::Cancel, Manual::Upper, 0, 0},
              {0, EventType::SelectPreset, Manual::Lower, 0, 0}});
    f.selected(PresetSelection::Cancel, PresetSelection::Cancel);
    CHECK(f.engines[0].active_key_count() == 2);
    f.render(17, true);
    f.events({{0, EventType::Expression, Manual::Upper, 0, 0.375}});
    f.render(f.milliseconds(3), false, true);
    f.events({{0, EventType::SelectPreset, Manual::Upper, 0, 11},
              {0, EventType::SelectBank, Manual::Lower, 0, 1}});
    f.selected(PresetSelection::BankB, PresetSelection::BankB);
    CHECK(f.engines[0].percussion_diagnostics().eligible);
    f.render(f.milliseconds(4));
    f.events({{0, EventType::Expression, Manual::Upper, 0, 0}});
    f.render(47, true);
    f.events({{0, EventType::Expression, Manual::Upper, 0, 0.625}});
    f.render(61);

    f.events({{0, EventType::NoteOff, Manual::Upper, 36, 0}});
    f.render(f.milliseconds(4));
    f.moving(Manual::Upper, 0);
    CHECK(f.contact(Manual::Lower).position == 1);
    f.events({{0, EventType::KeyPosition, Manual::Upper, 36, 0.37},
              {0, EventType::NoteOff, Manual::Lower, 36, 0}});
    f.render(f.milliseconds(4));
    CHECK(f.contact(Manual::Upper).position == 0.37);
    CHECK(f.contact(Manual::Upper).closed[3]); // Retained release hysteresis.
    f.moving(Manual::Lower, 0);
    f.events({{0, EventType::NoteOn, Manual::Upper, 36, 64},
              {0, EventType::Cancel, Manual::Lower, 0, 0}});
    f.render(f.milliseconds(3));
    f.moving(Manual::Upper, 1);
    f.moving(Manual::Lower, 0);
    f.events({{0, EventType::SelectPreset, Manual::Lower, 0, 11}});
    f.render(f.milliseconds(2)); // Reconnect while the released key still travels.
    f.events({{0, EventType::NoteOff, Manual::Upper, 36, 0},
              {0, EventType::NoteOff, Manual::Lower, 36, 0}});
    f.render(f.milliseconds(15));
    for (const auto manual : {Manual::Upper, Manual::Lower}) {
        const auto state = f.contact(manual);
        CHECK(state.position == 0 && state.target == 0);
        for (const auto closed : state.closed) CHECK(!closed);
    }
    f.render(17, true);
    ++counts.fixtures;
}
} // namespace

int main() {
    const auto nominal = load_test_profile();
    SourceLeakage graph;
    CHECK(graph.prepare(kEdges) == Status::Ok);
    CHECK(graph.edge_count() == 2 && graph.max_row_absolute_gain_sum() == 0.125);
    for (const double rate : {44100.0, 48000.0, 96000.0})
        for (const bool soft_fast : {false, true}) qualify(nominal, graph, rate, soft_fast);
    CHECK(counts.positive_samples > 100 && counts.negative_samples > 100);
    CHECK(counts.maximum_leakage_delta > 0.00001L);
    std::cout << std::setprecision(std::numeric_limits<long double>::max_digits10)
              << "{\"test\":\"source-leakage-nominal-contact-composition-v1\",\"fixtures\":" << counts.fixtures
              << ",\"rendered_frames\":" << counts.rendered_frames
              << ",\"waveform_samples\":" << counts.waveform_samples
              << ",\"exact_zero_samples\":" << counts.exact_zero_samples
              << ",\"phase_checks\":" << counts.phase_checks
              << ",\"history_checks\":" << counts.history_checks
              << ",\"positive_samples\":" << counts.positive_samples
              << ",\"negative_samples\":" << counts.negative_samples
              << ",\"maximum_error\":" << counts.maximum_error
              << ",\"maximum_output\":" << counts.maximum_output
              << ",\"maximum_leakage_delta\":" << counts.maximum_leakage_delta << "}\n";
}
