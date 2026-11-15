#include "TestSupport.h"
#include "hammond/Engine.h"

#include <algorithm>
#include <array>
#include <bit>
#include <cmath>
#include <complex>
#include <cstdint>
#include <initializer_list>
#include <limits>
#include <numbers>
#include <span>
#include <string_view>

namespace {
using namespace hammond;
using Complex = std::complex<long double>;
using Weights = std::array<long double, 3>;
constexpr std::size_t kLength = 1024;
constexpr std::uint32_t kSilent = 257, kDisconnected = 113;
constexpr long double kTau = 2.0L * std::numbers::pi_v<long double>;
constexpr long double kInputGain = 0.5L, kOutputGain = 0.25L, kExpression = 0.75L;
constexpr long double kSpectrumTolerance = 2.0e-7L;
constexpr long double kSlowSeconds = 1.551L;
constexpr long double kFastSeconds = ((1.5e6L * 4.7e6L) / (1.5e6L + 4.7e6L)) * 3.3e-7L;
constexpr long double kRecoverySeconds = 0.03432L;

struct Source {
    ToneId id;
    unsigned bin;
    long double amplitude, phase;
    double base;
};
// Frozen seed-zero offsets were calculated with independent Python integer
// SplitMix64 arithmetic and exact rational 2^-53 phases, before this test ran.
// The bases below give exactly 1/8, 1/4 and 5/8 turns. No production oscillator
// or inspected production sample supplies the waveform/spectral oracle.
constexpr std::array<Source, 3> kSources{{
    {69, 7, 0.5L, 0.125L, 0x1.da06a944a2549p-1},
    {80, 31, 0.375L, 0.25L, 0x1.abb000ff177c9p-1},
    {91, 97, 0.25L, 0.625L, 0x1.f8e47667194f6p-2},
}};

// x13=x25=x32=x50=0. The 13<->50 cycle must NOT carry y13 into y50.
constexpr std::array<SourceLeakageEdge, 11> kEdges{{
    {69, 13, 0.25}, {80, 13, -0.125}, {91, 13, 0.0625},
    {69, 25, -0.125}, {80, 25, 0.25}, {91, 25, -0.0625},
    {69, 32, 0.0625}, {80, 32, 0.125}, {91, 32, 0.25},
    {13, 50, 0.25}, {50, 13, -0.0625},
}};
constexpr Weights k13{0.25L, -0.125L, 0.0625L};
constexpr Weights k25{-0.125L, 0.25L, -0.0625L};
constexpr Weights k32{0.0625L, 0.125L, 0.25L};

enum class Route { Upper, Lower, Both, Second, Third, Pedal };
struct Fixture {
    std::string_view name;
    Route route;
    std::uint8_t note;
    Weights weights;
    long double decay, level;
    PedalDrawbarPositions pedals;
};
// Independent, literal route algebra. Pedal 1's documentary contacts are
// [1,13,13,25,32,37,41,44], two per Brown/Red/Orange/Yellow bus. Thus its
// nonzero buses are y13, y13+y25, y32, 0. Applying the documented fixture
// mixtures gives the literal donor rows below; no PedalBusKernel or leakage
// process call calculates expected values. The last two fixtures are exact zero.
constexpr std::array<Fixture, 10> kFixtures{{
    {"upper13", Route::Upper, 36, k13, 0, 1, {0, 0}},
    {"lower13", Route::Lower, 36, k13, 0, 1, {0, 0}},
    {"shared13", Route::Both, 36, {0.5L, -0.25L, 0.125L}, 0, 1, {0, 0}},
    {"second25-normal-slow", Route::Second, 36, k25, kSlowSeconds, 1, {0, 0}},
    {"third32-soft-fast", Route::Third, 36, k32, kFastSeconds, 0.75L, {0, 0}},
    {"pedal-mixture1", Route::Pedal, 0, {21.0L/128, -1.0L/64, 1.0L/16}, 0, 1, {8, 0}},
    {"pedal-mixture2", Route::Pedal, 0, {7.0L/64, 5.0L/64, 9.0L/128}, 0, 1, {0, 8}},
    {"pedal-both", Route::Pedal, 0, {21.0L/128, 13.0L/256, 43.0L/512}, 0, 1, {4, 6}},
    {"noncascaded50", Route::Upper, 73, {0, 0, 0}, 0, 1, {0, 0}},
    {"unaffected14", Route::Upper, 37, {0, 0, 0}, 0, 1, {0, 0}},
}};

struct Counts {
    std::uint64_t fixtures{}, windows{}, rendered_frames{}, waveform_samples{};
    std::uint64_t bit_checks{}, silent_samples{}, spectrum_checks{}, pedal_checks{};
    long double max_waveform_error{}, max_raw_spectral_error{};
    long double max_coherent_error{}, max_unprovided_bin{};
} counts;

void run(Engine& engine, std::uint32_t frames, std::span<float> output = {},
         std::span<const Event> edits = {}) {
    const auto result = engine.process(frames, output, edits);
    CHECK(result.status == Status::Ok && result.events_consumed == edits.size());
    counts.rendered_frames += frames;
}
void events(Engine& engine, std::initializer_list<Event> edits) {
    const auto clock = engine.frame_clock();
    run(engine, 0, {}, {edits.begin(), edits.size()});
    CHECK(engine.frame_clock() == clock);
}
void render(Engine& engine, std::span<float> output, bool partitioned) {
    constexpr std::array<std::size_t, 6> blocks{17, 31, 127, 7, 256, 43};
    std::size_t offset = 0, part = 0;
    while (offset < output.size()) {
        const auto count = partitioned ? std::min(blocks[part++ % blocks.size()], output.size() - offset)
                                       : output.size();
        run(engine, static_cast<std::uint32_t>(count), output.subspan(offset, count));
        offset += count;
    }
}
void same_samples(std::span<const float> actual, std::span<const float> other) {
    CHECK(actual.size() == other.size());
    for (std::size_t index = 0; index < actual.size(); ++index) {
        CHECK(std::bit_cast<std::uint32_t>(actual[index]) == std::bit_cast<std::uint32_t>(other[index]));
        ++counts.bit_checks;
    }
}
void zero_samples(std::span<const float> samples) {
    for (float value : samples) { CHECK(value == 0.0F); ++counts.silent_samples; }
}
void check_phases(const Engine& engine, const Engine& other, std::uint64_t frames) {
    CHECK(engine.frame_clock() == frames && other.frame_clock() == frames);
    CHECK(engine.controls_snapshot() == other.controls_snapshot());
    CHECK(engine.percussion_diagnostics() == other.percussion_diagnostics());
    CHECK(engine.last_pedal_frame() == other.last_pedal_frame());
    for (ToneId id = 1; id <= 91; ++id) {
        double a = -1, b = -2;
        CHECK(engine.source_phase_turns(id, a) && other.source_phase_turns(id, b));
        CHECK(std::bit_cast<std::uint64_t>(a) == std::bit_cast<std::uint64_t>(b));
    }
    for (const auto& source : kSources) {
        double phase = -1;
        CHECK(engine.source_phase_turns(source.id, phase));
        const double expected = std::fmod(static_cast<double>(source.phase) +
            static_cast<double>(source.bin) * static_cast<double>(frames) / 1024.0, 1.0);
        CHECK(phase == expected); // The declared phases/increments are exact dyadics.
    }
    // No donor's own manual fundamental or any other pedal is held.
    CHECK(!engine.key_down(Manual::Upper, 92) && !engine.key_down(Manual::Lower, 92));
    for (std::uint8_t pedal = 2; pedal <= 25; ++pedal) CHECK(!engine.pedal_down({pedal}));
}

RuntimeProfile coherent_profile(const RuntimeProfile& nominal, double rate) {
    auto profile = nominal;
    for (auto& source : profile.sources) source.peak_amplitude = 0;
    for (const auto& source : kSources) {
        auto& selected = profile.sources[static_cast<std::size_t>(source.id) - 1];
        selected.frequency_hz = static_cast<double>(source.bin) * rate / 1024.0;
        selected.peak_amplitude = static_cast<double>(source.amplitude);
        selected.base_phase_turns = source.base;
    }
    profile.output_gain = static_cast<double>(kOutputGain);
    CHECK(profile.drawbar_gains[0] == 0 && profile.drawbar_gains[8] == 1);
    CHECK(profile.manual_map[0][2] == 13 && profile.manual_map[0][3] == 25 &&
          profile.manual_map[0][4] == 32 && profile.manual_map[37][2] == 50 &&
          profile.manual_map[1][2] == 14);
    return profile;
}
void configure(Engine& engine, const Fixture& fixture) {
    events(engine, {{0, EventType::Expression, Manual::Upper, 0, static_cast<double>(kExpression)}});
    if (fixture.route == Route::Pedal) {
        events(engine, {{0, EventType::PedalDrawbar, Manual::Lower, 0, static_cast<double>(fixture.pedals[0])},
                        {0, EventType::PedalDrawbar, Manual::Lower, 1, static_cast<double>(fixture.pedals[1])},
                        {0, EventType::PedalOn, Manual::Lower, 1, 127}});
        CHECK(engine.active_key_count() == 0 && engine.active_pedal_count() == 1);
        return;
    }
    if (fixture.decay != 0) {
        const double third = fixture.route == Route::Third ? 1.0 : 0.0;
        events(engine, {{0, EventType::Percussion, Manual::Upper, 0, 1},
                        {0, EventType::Percussion, Manual::Upper, 1, third},
                        {0, EventType::Percussion, Manual::Upper, 2, third},
                        {0, EventType::Percussion, Manual::Upper, 3, third}});
    }
    const Manual first = fixture.route == Route::Lower ? Manual::Lower : Manual::Upper;
    if (fixture.decay == 0) events(engine, {{0, EventType::Drawbar, first, 2, 8}});
    events(engine, {{0, EventType::NoteOn, first, fixture.note, 127}});
    if (fixture.route == Route::Both) {
        events(engine, {{0, EventType::Drawbar, Manual::Lower, 2, 8},
                        {0, EventType::NoteOn, Manual::Lower, fixture.note, 127}});
    }
    CHECK(engine.active_key_count() == (fixture.route == Route::Both ? 2U : 1U));
    CHECK(engine.active_pedal_count() == 0);
}
void route(Engine& engine, const Fixture& fixture, bool enabled) {
    if (fixture.route == Route::Pedal) {
        events(engine, {{0, enabled ? EventType::PedalOn : EventType::PedalOff,
                         Manual::Lower, 1, enabled ? 127.0 : 0.0}});
        return;
    }
    const Manual first = fixture.route == Route::Lower ? Manual::Lower : Manual::Upper;
    const EventType type = enabled ? EventType::SelectBank : EventType::Cancel;
    events(engine, {{0, type, first, 0, enabled ? 1.0 : 0.0}});
    if (fixture.route == Route::Both)
        events(engine, {{0, type, Manual::Lower, 0, enabled ? 1.0 : 0.0}});
}
void mute(Engine& engine, const Fixture& fixture) {
    if (fixture.route == Route::Pedal) {
        events(engine, {{0, EventType::PedalDrawbar, Manual::Lower, 0, 0},
                        {0, EventType::PedalDrawbar, Manual::Lower, 1, 0}});
    } else if (fixture.decay != 0) {
        events(engine, {{0, EventType::Percussion, Manual::Upper, 0, 0}});
    } else {
        const Manual first = fixture.route == Route::Lower ? Manual::Lower : Manual::Upper;
        events(engine, {{0, EventType::Drawbar, first, 2, 0}});
        if (fixture.route == Route::Both) events(engine, {{0, EventType::Drawbar, Manual::Lower, 2, 0}});
    }
}

long double raw_source(std::size_t source, std::uint64_t frame) {
    const auto& definition = kSources[source];
    const long double turns = definition.phase +
        static_cast<long double>(definition.bin) * static_cast<long double>(frame) / 1024.0L;
    return definition.amplitude * std::sin(kTau * std::fmod(turns, 1.0L));
}
long double weighted(const Weights& weights, std::uint64_t frame) {
    long double value = 0;
    for (std::size_t source = 0; source < 3; ++source)
        value += weights[source] * raw_source(source, frame);
    return kInputGain * value;
}
void pedal_oracle(const Engine& engine, std::uint64_t frame, const Fixture& fixture) {
    if (fixture.route != Route::Pedal) return;
    const long double a = weighted(k13, frame), b = weighted(k25, frame), c = weighted(k32, frame);
    const std::array<long double, 4> buses{a, a + b, c, 0};
    const std::array<long double, 2> mixtures{
        weighted({21.0L/128, -1.0L/64, 1.0L/16}, frame),
        weighted({7.0L/64, 5.0L/64, 9.0L/128}, frame)};
    const auto& actual = engine.last_pedal_frame();
    CHECK(actual.valid && actual.frame == frame && actual.positions == fixture.pedals);
    const auto compare = [](double value, long double expected) {
        const long double limit = 32.0L * std::numeric_limits<double>::epsilon() *
            std::max(1.0L, std::abs(expected));
        CHECK_NEAR(value, expected, limit);
        ++counts.pedal_checks;
    };
    for (std::size_t index = 0; index < 4; ++index) compare(actual.buses[index], buses[index]);
    for (std::size_t index = 0; index < 2; ++index) compare(actual.voice.mixtures[index], mixtures[index]);
    compare(actual.voice.output, (static_cast<long double>(fixture.pedals[0]) / 8) * mixtures[0] +
                                 (static_cast<long double>(fixture.pedals[1]) / 8) * mixtures[1]);
}

void spectrum(std::span<const float, kLength> actual, const Fixture& fixture,
              double rate, std::uint64_t first_frame, long double readiness) {
    std::array<long double, kLength> clean{}, expected_raw{};
    bool audible = false;
    const bool expected_audible = fixture.weights != Weights{};
    for (std::size_t index = 0; index < kLength; ++index) {
        const long double envelope = fixture.decay == 0 ? 1.0L : readiness *
            std::exp(-static_cast<long double>(index) / (static_cast<long double>(rate) * fixture.decay));
        expected_raw[index] = weighted(fixture.weights, first_frame + index) *
            fixture.level * kOutputGain * kExpression * envelope;
        clean[index] = static_cast<long double>(actual[index]) / envelope;
        const long double error = std::abs(static_cast<long double>(actual[index]) - expected_raw[index]);
        const long double limit = 8.0L * std::numeric_limits<float>::epsilon() *
            std::max(0.001L, std::abs(expected_raw[index]));
        CHECK_NEAR(actual[index], expected_raw[index], limit);
        if (!expected_audible) CHECK(actual[index] == 0.0F);
        audible = audible || actual[index] != 0.0F;
        counts.max_waveform_error = std::max(counts.max_waveform_error, error);
        ++counts.waveform_samples;
    }
    CHECK(audible == expected_audible);
    // Steady output is coherent directly. Percussion has intended exponential
    // sidebands: compare its RAW DFT to an independent damped-sine waveform,
    // and separately inspect the analytically de-enveloped coherent spectrum.
    // No window is used; positive bins use 2/N, DC/Nyquist use 1/N.
    for (std::size_t bin = 0; bin <= kLength / 2; ++bin) {
        Complex observed_clean{}, observed_raw{}, expected_damped{};
        for (std::size_t index = 0; index < kLength; ++index) {
            const long double angle = -kTau * static_cast<long double>(bin * index) / 1024.0L;
            const Complex basis{std::cos(angle), std::sin(angle)};
            observed_clean += clean[index] * basis;
            if (fixture.decay != 0) {
                observed_raw += static_cast<long double>(actual[index]) * basis;
                expected_damped += expected_raw[index] * basis;
            }
        }
        const long double scale = (bin == 0 || bin == kLength / 2) ? 1.0L/1024 : 2.0L/1024;
        observed_clean *= scale;
        Complex expected_clean{};
        bool provided = false;
        for (std::size_t source = 0; source < 3; ++source) {
            if (bin != kSources[source].bin || fixture.weights[source] == 0) continue;
            const long double phase = kTau * (kSources[source].phase +
                static_cast<long double>(kSources[source].bin) *
                static_cast<long double>(first_frame) / 1024.0L);
            const long double amplitude = kInputGain * kOutputGain * kExpression *
                fixture.level * fixture.weights[source] * kSources[source].amplitude;
            expected_clean += amplitude * Complex{std::sin(phase), -std::cos(phase)};
            provided = true;
        }
        const long double coherent_error = std::abs(observed_clean - expected_clean);
        CHECK(coherent_error <= kSpectrumTolerance);
        counts.max_coherent_error = std::max(counts.max_coherent_error, coherent_error);
        if (!provided) counts.max_unprovided_bin = std::max(counts.max_unprovided_bin, std::abs(observed_clean));
        ++counts.spectrum_checks;
        long double raw_error = coherent_error;
        if (fixture.decay != 0) {
            raw_error = std::abs((observed_raw - expected_damped) * scale);
            CHECK(raw_error <= kSpectrumTolerance);
            ++counts.spectrum_checks;
        }
        counts.max_raw_spectral_error = std::max(counts.max_raw_spectral_error, raw_error);
    }
    ++counts.windows;
}

void fixture_run(const RuntimeProfile& nominal, const SourceLeakage& graph,
                 double rate, const Fixture& fixture) {
    const auto profile = coherent_profile(nominal, rate);
    Engine whole;
    CHECK(whole.prepare(profile, {rate, static_cast<std::uint32_t>(kLength), 0, 0}) == Status::Ok);
    CHECK(whole.set_source_leakage(graph, static_cast<double>(kInputGain)) == Status::Ok);
    Engine partitioned = whole;
    configure(whole, fixture); configure(partitioned, fixture);
    check_phases(whole, partitioned, 0);
    std::array<float, kLength> a{}, b{};
    render(whole, a, false); render(partitioned, b, true);
    same_samples(a, b);
    check_phases(whole, partitioned, kLength);
    spectrum(a, fixture, rate, 0, 1);
    pedal_oracle(whole, kLength - 1, fixture);

    route(whole, fixture, false); route(partitioned, fixture, false);
    std::array<float, kSilent> silent_a{}, silent_b{};
    render(whole, silent_a, false); render(partitioned, silent_b, true);
    same_samples(silent_a, silent_b); zero_samples(silent_a);
    run(whole, kDisconnected);
    run(partitioned, 19); run(partitioned, kDisconnected - 19);
    constexpr std::uint64_t resumed = kLength + kSilent + kDisconnected;
    check_phases(whole, partitioned, resumed);
    const long double readiness = fixture.decay == 0 ? 1.0L : 1.0L -
        (1.0L - std::exp(-1024.0L / (static_cast<long double>(rate) * fixture.decay))) *
        std::exp(-static_cast<long double>(kSilent + kDisconnected) /
                 (static_cast<long double>(rate) * kRecoverySeconds));
    if (fixture.decay != 0) CHECK_NEAR(whole.percussion_diagnostics().readiness, readiness, 1.0e-11L);
    route(whole, fixture, true); route(partitioned, fixture, true);
    render(whole, a, false); render(partitioned, b, true);
    same_samples(a, b); check_phases(whole, partitioned, resumed + kLength);
    spectrum(a, fixture, rate, resumed, readiness);
    pedal_oracle(whole, resumed + kLength - 1, fixture);

    mute(whole, fixture); mute(partitioned, fixture);
    std::array<float, 64> muted_a{}, muted_b{};
    render(whole, muted_a, false); render(partitioned, muted_b, true);
    same_samples(muted_a, muted_b); zero_samples(muted_a);
    check_phases(whole, partitioned, resumed + kLength + muted_a.size());
    ++counts.fixtures;
}

} // namespace

int main() {
    const auto nominal = load_test_profile();
    constexpr std::array<ToneId, 8> pedal_one{1, 13, 13, 25, 32, 37, 41, 44};
    for (std::size_t contact = 0; contact < pedal_one.size(); ++contact) {
        const auto& route_record = compiled_pedal_routes()[contact];
        CHECK(route_record.pedal == PedalId{1} && route_record.contact == contact);
        CHECK(route_record.tone == pedal_one[contact]);
        CHECK(static_cast<std::size_t>(route_record.bus) == contact / 2);
    }
    SourceLeakage graph;
    CHECK(graph.prepare(kEdges) == Status::Ok && graph.edge_count() == 11);
    CHECK(graph.max_row_absolute_gain_sum() == 0.5);
    for (double rate : {44100.0, 48000.0, 96000.0}) {
        for (const auto& fixture : kFixtures) fixture_run(nominal, graph, rate, fixture);
    }
    std::cout << std::setprecision(std::numeric_limits<long double>::max_digits10)
              << "{\"test\":\"source-leakage-engine-spectrum-v1\",\"fixtures\":" << counts.fixtures
              << ",\"windows\":" << counts.windows << ",\"rendered_frames\":" << counts.rendered_frames
              << ",\"waveform_samples\":" << counts.waveform_samples << ",\"bit_checks\":" << counts.bit_checks
              << ",\"silent_samples\":" << counts.silent_samples << ",\"spectral_checks\":" << counts.spectrum_checks
              << ",\"pedal_checks\":" << counts.pedal_checks << ",\"rates\":[44100,48000,96000]"
              << ",\"bins\":[7,31,97],\"max_waveform_error\":" << counts.max_waveform_error
              << ",\"max_raw_spectral_error\":" << counts.max_raw_spectral_error
              << ",\"max_coherent_error\":" << counts.max_coherent_error
              << ",\"max_unprovided_bin\":" << counts.max_unprovided_bin << "}\n";
}
