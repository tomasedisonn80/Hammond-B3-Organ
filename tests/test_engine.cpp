#include "TestSupport.h"
#include "hammond/Engine.h"

#include <algorithm>
#include <array>
#include <bit>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <numbers>
#include <span>
#include <vector>

namespace {

using hammond::Engine;
using hammond::Event;
using hammond::EventType;
using hammond::Manual;
using hammond::ProcessSpec;
using hammond::RuntimeProfile;
using hammond::Status;
using hammond::ToneId;

constexpr Manual upper = Manual::Upper;
constexpr Manual lower = Manual::Lower;
constexpr std::uint32_t max_block = 1024;
constexpr float sentinel = -12345.25F;

[[nodiscard]] Event note_on(std::uint32_t offset, Manual manual, std::uint8_t note,
                            double velocity = 100.0) {
    return {offset, EventType::NoteOn, manual, note, velocity};
}

[[nodiscard]] Event note_off(std::uint32_t offset, Manual manual, std::uint8_t note) {
    return {offset, EventType::NoteOff, manual, note, 0.0};
}

[[nodiscard]] Event drawbar(std::uint32_t offset, Manual manual, std::uint8_t index,
                            double position) {
    return {offset, EventType::Drawbar, manual, index, position};
}

[[nodiscard]] Event expression(std::uint32_t offset, double value) {
    return {offset, EventType::Expression, upper, 0, value};
}

[[nodiscard]] Event all_off(std::uint32_t offset, Manual manual) {
    return {offset, EventType::AllNotesOff, manual, 0, 0.0};
}

void process_ok(Engine& engine, std::uint32_t frames, std::span<float> output = {},
                std::span<const Event> events = {}) {
    const auto result = engine.process(frames, output, events);
    CHECK(result.status == Status::Ok);
    CHECK(result.ok());
    CHECK(static_cast<bool>(result));
    CHECK(result.events_consumed == events.size());
}

[[nodiscard]] Engine prepare_engine(const RuntimeProfile& profile, double rate = 48000.0,
                                     std::uint64_t origin = 0) {
    Engine engine;
    CHECK(engine.prepare(profile, ProcessSpec{rate, max_block, 0, origin}) == Status::Ok);
    CHECK(engine.prepared());
    CHECK(engine.frame_clock() == origin);
    return engine;
}

void check_same_audio(std::span<const float> actual, std::span<const float> expected) {
    CHECK(actual.size() == expected.size());
    for (std::size_t i = 0; i < actual.size(); ++i) {
        CHECK(std::bit_cast<std::uint32_t>(actual[i]) ==
              std::bit_cast<std::uint32_t>(expected[i]));
    }
}

// Compare values, never object padding. Snapshot all public musical state and
// all 91 phases; later audio also detects corruption in private cached gains.
struct State {
    bool prepared{};
    std::uint64_t clock{};
    std::uint64_t expression_bits{};
    std::array<std::size_t, 3> key_counts{};
    std::array<std::array<bool, hammond::kManualKeyCount>, hammond::kManualCount> keys{};
    std::array<std::array<std::uint8_t, hammond::kDrawbarCount>, hammond::kManualCount> bars{};
    std::array<std::uint64_t, hammond::kToneSourceCount> phase_bits{};
    bool operator==(const State&) const = default;
};

[[nodiscard]] State state_of(const Engine& engine) {
    State state;
    state.prepared = engine.prepared();
    state.clock = engine.frame_clock();
    state.expression_bits = std::bit_cast<std::uint64_t>(engine.expression());
    state.key_counts = {engine.active_key_count(), engine.active_key_count(upper),
                        engine.active_key_count(lower)};
    for (std::size_t m = 0; m < hammond::kManualCount; ++m) {
        const auto manual = static_cast<Manual>(m);
        for (std::size_t key = 0; key < hammond::kManualKeyCount; ++key) {
            state.keys[m][key] = engine.key_down(
                manual, static_cast<std::uint32_t>(key) + hammond::kMinManualMidiNote);
        }
        for (std::size_t bar = 0; bar < hammond::kDrawbarCount; ++bar) {
            std::uint8_t position = 255;
            CHECK(engine.drawbar_position(manual, bar, position) == state.prepared);
            if (!state.prepared) CHECK(position == 255);
            state.bars[m][bar] = position;
        }
    }
    for (std::size_t source = 0; source < hammond::kToneSourceCount; ++source) {
        double phase = -17.0;
        CHECK(engine.source_phase_turns(static_cast<ToneId>(source + 1), phase) ==
              state.prepared);
        if (state.prepared) CHECK(phase >= 0.0 && phase < 1.0);
        else CHECK(phase == -17.0);
        state.phase_bits[source] = std::bit_cast<std::uint64_t>(phase);
    }
    return state;
}

[[nodiscard]] std::uint8_t bar_position(const Engine& engine, Manual manual,
                                       std::size_t index) {
    std::uint8_t position = 255;
    CHECK(engine.drawbar_position(manual, index, position));
    return position;
}

// Frozen SplitMix64 seed-zero offsets, independently calculated with Python
// integer masking from the documented seed convention. The source-bank suite
// covers the PRNG itself. This oracle never calls TonewheelBank, reads engine
// phases to create its expectation, or repeats the double phase recurrence.
struct PhaseFixture { ToneId id; double offset; };
constexpr std::array<PhaseFixture, 7> phase_fixtures{{
    {13, 0x1.0c43407fc177bp-1}, {25, 0x1.baf803a9ea80ep-1},
    {61, 0x1.daf2805a3ab8bp-1}, {73, 0x1.73379e080f0d8p-2},
    {80, 0x1.a89ffe01d106ep-2}, {85, 0x1.5b90e62a63e28p-2},
    {89, 0x1.b389942052348p-4},
}};

[[nodiscard]] long double oracle_phase(const RuntimeProfile& profile, ToneId id,
                                        std::uint64_t elapsed_frames, double rate) {
    const auto fixture = std::find_if(phase_fixtures.begin(), phase_fixtures.end(),
        [id](const PhaseFixture& candidate) { return candidate.id == id; });
    CHECK(fixture != phase_fixtures.end());
    const auto& source = profile.sources[static_cast<std::size_t>(id) - 1];
    const long double elapsed = static_cast<long double>(elapsed_frames) / rate;
    return std::fmod(static_cast<long double>(source.base_phase_turns) + fixture->offset +
                     elapsed * source.frequency_hz, 1.0L);
}

[[nodiscard]] long double oracle_source(const RuntimeProfile& profile, ToneId id,
                                         std::uint64_t elapsed_frames, double rate) {
    const auto& source = profile.sources[static_cast<std::size_t>(id) - 1];
    return source.peak_amplitude * std::sin(2.0L * std::numbers::pi_v<long double> *
                                          oracle_phase(profile, id, elapsed_frames, rate));
}

[[nodiscard]] RuntimeProfile probe_profile(const RuntimeProfile& nominal) {
    auto profile = nominal;
    profile.output_gain = 0.5;
    profile.sources[12] = {997.25, 0.625, 0.125};
    profile.sources[24] = {313.5, 0.5, 0.25};
    profile.drawbar_gains = {0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0};
    return profile;
}

void test_initial_state_and_independent_sine(const RuntimeProfile& nominal) {
    const auto profile = probe_profile(nominal);
    for (const double rate : {44100.0, 48000.0, 96000.0}) {
        auto engine = prepare_engine(profile, rate, 9876543210ULL);
        CHECK(engine.active_key_count() == 0);
        CHECK(engine.expression() == 1.0);
        for (const Manual manual : {upper, lower}) {
            for (std::size_t bar = 0; bar < hammond::kDrawbarCount; ++bar)
                CHECK(bar_position(engine, manual, bar) == 0);
        }
        // The clock origin must not pre-run or phase-shift the source field.
        double initial_phase = -1.0;
        CHECK(engine.source_phase_turns(13, initial_phase));
        CHECK_NEAR(initial_phase, oracle_phase(profile, 13, 0, rate), 2e-16L);
        const std::array events{drawbar(0, upper, 2, 8), note_on(0, upper, 36)};
        std::array<float, 1009> output{};
        process_ok(engine, static_cast<std::uint32_t>(output.size()), output, events);
        long double energy = 0.0L;
        for (std::size_t frame = 0; frame < output.size(); ++frame) {
            const auto expected = profile.output_gain * oracle_source(profile, 13, frame, rate);
            CHECK_NEAR(output[frame], expected, 3e-8L);
            energy += static_cast<long double>(output[frame]) * output[frame];
        }
        CHECK(energy > 30.0L);
        double final_phase = -1.0;
        CHECK(engine.source_phase_turns(13, final_phase));
        CHECK_NEAR(final_phase, oracle_phase(profile, 13, output.size(), rate), 2e-12L);
        CHECK(engine.frame_clock() == 9876543210ULL + output.size());
    }
}

void test_coherent_foldback_and_printed_top_key(const RuntimeProfile& nominal) {
    auto profile = nominal;
    profile.output_gain = 1.0;
    CHECK(profile.manual_map[0][0] == 13);
    CHECK(profile.manual_map[0][2] == 13);
    auto single = prepare_engine(profile);
    auto folded = prepare_engine(profile);
    auto two_keys = prepare_engine(profile);
    const std::array one_events{drawbar(0, upper, 0, 8), note_on(0, upper, 36)};
    const std::array fold_events{drawbar(0, upper, 0, 8), drawbar(0, upper, 2, 8),
                                 note_on(0, upper, 36)};
    const std::array key_events{drawbar(0, upper, 0, 8), note_on(0, upper, 36),
                                note_on(0, upper, 48)};
    std::array<float, 257> one{}, two{}, keys{};
    process_ok(single, 257, one, one_events);
    process_ok(folded, 257, two, fold_events);
    process_ok(two_keys, 257, keys, key_events);
    long double one_energy = 0.0L;
    long double two_energy = 0.0L;
    float peak = 0.0F;
    for (std::size_t frame = 0; frame < one.size(); ++frame) {
        CHECK(two[frame] == 2.0F * one[frame]);
        CHECK(keys[frame] == two[frame]);
        CHECK_NEAR(one[frame], oracle_source(profile, 13, frame, 48000.0), 6e-8L);
        one_energy += static_cast<long double>(one[frame]) * one[frame];
        two_energy += static_cast<long double>(two[frame]) * two[frame];
        peak = std::max(peak, std::abs(two[frame]));
    }
    CHECK(one_energy > 1.0L);
    const long double amplitude_ratio = std::sqrt(two_energy / one_energy);
    CHECK_NEAR(amplitude_ratio, 2.0L, 1e-15L);
    CHECK_NEAR(20.0L * std::log10(amplitude_ratio), 6.020599913279624L, 1e-12L);
    CHECK(peak > 1.5F); // No hidden limiter; a power sum would yield sqrt(2).
    CHECK(folded.active_key_count() == 1);
    CHECK(two_keys.active_key_count() == 2);

    // Atlas p.102, printed key 61 row; explicitly independent of its map formula.
    constexpr std::array<ToneId, 9> printed_top{61, 80, 73, 85, 80, 85, 89, 80, 85};
    CHECK(profile.manual_map[60] == printed_top);
    for (std::uint8_t bar = 0; bar < 9; ++bar) {
        auto route = prepare_engine(profile);
        const std::array route_events{drawbar(0, upper, bar, 8), note_on(0, upper, 96)};
        std::array<float, 31> route_output{};
        process_ok(route, 31, route_output, route_events);
        for (std::size_t frame = 0; frame < route_output.size(); ++frame)
            CHECK_NEAR(route_output[frame],
                       oracle_source(profile, printed_top[bar], frame, 48000.0), 6e-8L);
    }
    auto top = prepare_engine(profile);
    std::vector<Event> top_events;
    for (std::uint8_t bar = 0; bar < 9; ++bar)
        top_events.push_back(drawbar(0, upper, bar, 8));
    top_events.push_back(note_on(0, upper, 96));
    std::array<float, 257> top_output{};
    process_ok(top, 257, top_output, top_events);
    for (std::size_t frame = 0; frame < top_output.size(); ++frame) {
        const long double expected = oracle_source(profile, 61, frame, 48000.0) +
            oracle_source(profile, 73, frame, 48000.0) +
            3.0L * oracle_source(profile, 80, frame, 48000.0) +
            3.0L * oracle_source(profile, 85, frame, 48000.0) +
            oracle_source(profile, 89, frame, 48000.0);
        CHECK_NEAR(top_output[frame], expected, 5e-7L);
    }
}

void test_velocity_boolean_ownership_and_drawbars(const RuntimeProfile& nominal) {
    const auto profile = probe_profile(nominal);
    auto quiet_velocity = prepare_engine(profile);
    auto loud_repeated = prepare_engine(profile);
    const std::array quiet{drawbar(0, upper, 2, 8), note_on(0, upper, 36, 1)};
    const std::array repeated{drawbar(0, upper, 2, 8), note_on(0, upper, 36, 127),
                              note_on(16, upper, 36, 42), note_on(128, upper, 36, 1)};
    std::array<float, 257> a{}, b{};
    process_ok(quiet_velocity, 257, a, quiet);
    process_ok(loud_repeated, 257, b, repeated);
    check_same_audio(a, b);
    CHECK(state_of(quiet_velocity) == state_of(loud_repeated));
    CHECK(loud_repeated.active_key_count() == 1);
    const std::array release{note_off(9, upper, 36)};
    process_ok(quiet_velocity, 32, std::span<float>(a).first(32), release);
    process_ok(loud_repeated, 32, std::span<float>(b).first(32), release);
    check_same_audio(std::span<const float>(a).first(32), std::span<const float>(b).first(32));
    CHECK(!loud_repeated.key_down(upper, 36));
    CHECK(loud_repeated.active_key_count() == 0);
    for (std::size_t frame = 9; frame < 32; ++frame) CHECK(b[frame] == 0.0F);

    auto held = prepare_engine(profile);
    std::vector<Event> moves{note_on(0, upper, 36)};
    for (std::uint8_t position = 1; position <= 8; ++position)
        moves.push_back(drawbar(static_cast<std::uint32_t>(position) * 11,
                                upper, 2, position));
    moves.push_back(drawbar(99, upper, 2, 0));
    std::array<float, 110> output{};
    process_ok(held, 110, output, moves);
    for (std::size_t frame = 0; frame < output.size(); ++frame) {
        const auto position = frame < 99 ? frame / 11 : 0;
        const auto expected = profile.output_gain * profile.drawbar_gains[position] *
                              oracle_source(profile, 13, frame, 48000.0);
        CHECK_NEAR(output[frame], expected, 3e-8L);
    }
    CHECK(held.key_down(upper, 36));
    CHECK(held.active_key_count() == 1);
    CHECK(bar_position(held, upper, 2) == 0);
}

void test_manual_sharing_and_selected_all_off(const RuntimeProfile& nominal) {
    const auto profile = probe_profile(nominal);
    auto reference = prepare_engine(profile);
    auto shared = prepare_engine(profile);
    const std::array reference_events{drawbar(0, upper, 2, 8), note_on(0, upper, 36),
                                      expression(0, 0.5)};
    const std::array shared_events{drawbar(0, upper, 2, 8), drawbar(0, lower, 2, 8),
                                   note_on(0, upper, 36), expression(0, 0.5),
                                   note_on(31, lower, 36)};
    std::array<float, 127> one{}, both{};
    process_ok(reference, 127, one, reference_events);
    process_ok(shared, 127, both, shared_events);
    for (std::size_t frame = 0; frame < one.size(); ++frame)
        CHECK(both[frame] == one[frame] * (frame < 31 ? 1.0F : 2.0F));
    CHECK(state_of(shared).phase_bits == state_of(reference).phase_bits);
    CHECK(shared.active_key_count(upper) == 1);
    CHECK(shared.active_key_count(lower) == 1);

    const std::array release_upper{all_off(7, upper)};
    process_ok(reference, 127, one);
    process_ok(shared, 127, both, release_upper);
    for (std::size_t frame = 0; frame < one.size(); ++frame)
        CHECK(both[frame] == one[frame] * (frame < 7 ? 2.0F : 1.0F));
    CHECK(!shared.key_down(upper, 36));
    CHECK(shared.key_down(lower, 36));
    CHECK(shared.active_key_count() == 1);
    CHECK(bar_position(shared, upper, 2) == 8);
    CHECK(bar_position(shared, lower, 2) == 8);
    CHECK(shared.expression() == 0.5);
    CHECK(shared.frame_clock() == reference.frame_clock());
    CHECK(state_of(shared).phase_bits == state_of(reference).phase_bits);

    const auto before = state_of(shared);
    const std::array release_lower{all_off(0, lower)};
    process_ok(shared, 0, {}, release_lower);
    CHECK(shared.active_key_count() == 0);
    CHECK(state_of(shared).phase_bits == before.phase_bits);
    CHECK(shared.frame_clock() == before.clock);
    CHECK(state_of(shared).bars == before.bars);
    CHECK(shared.expression() == 0.5);
    const std::array lower_again{note_on(0, lower, 36)};
    process_ok(reference, 127, one);
    process_ok(shared, 127, both, lower_again);
    check_same_audio(both, one); // Retained controls and uninterrupted source time.
}

void test_exact_timing_tie_order_and_flush(const RuntimeProfile& nominal) {
    const auto profile = probe_profile(nominal);
    auto engine = prepare_engine(profile, 48000.0, 100);
    const std::array events{
        drawbar(0, upper, 2, 8), note_on(3, upper, 36), note_off(9, upper, 36),
        note_on(12, upper, 36), note_off(12, upper, 36),
        note_off(15, upper, 36), note_on(15, upper, 36),
        note_on(18, upper, 36), all_off(18, upper),
        all_off(20, upper), note_on(20, upper, 36),
        drawbar(24, upper, 2, 0), drawbar(24, upper, 2, 8),
        expression(24, 0.125), expression(24, 0.5), note_on(27, upper, 36, 0)};
    std::array<float, 32> output{};
    process_ok(engine, 32, output, events);
    for (std::size_t frame = 0; frame < output.size(); ++frame) {
        const bool sounding = (frame >= 3 && frame < 9) ||
                              (frame >= 15 && frame < 18) || (frame >= 20 && frame < 27);
        const auto gain = frame < 24 ? 1.0L : 0.5L;
        const auto expected = sounding ? gain * profile.output_gain *
            oracle_source(profile, 13, frame, 48000.0) : 0.0L;
        CHECK_NEAR(output[frame], expected, 3e-8L);
        if (!sounding) CHECK(output[frame] == 0.0F);
        else CHECK(output[frame] != 0.0F);
    }
    CHECK(engine.frame_clock() == 132);
    CHECK(!engine.key_down(upper, 36));
    CHECK(engine.expression() == 0.5);

    const auto before = state_of(engine);
    output.fill(sentinel);
    const std::array flush{drawbar(0, upper, 2, 4), expression(0, 0.25),
                           note_on(0, upper, 36)};
    std::span<const Event> pending(flush);
    const auto accepted = engine.process(0, output, pending);
    CHECK(accepted.ok());
    CHECK(accepted.events_consumed == flush.size());
    pending = pending.subspan(accepted.events_consumed); // Caller consumes once.
    CHECK(pending.empty());
    CHECK(engine.frame_clock() == before.clock);
    CHECK(state_of(engine).phase_bits == before.phase_bits);
    CHECK(engine.key_down(upper, 36));
    CHECK(bar_position(engine, upper, 2) == 4);
    CHECK(engine.expression() == 0.25);
    for (const float sample : output) CHECK(sample == sentinel);
    const auto flushed = state_of(engine);
    process_ok(engine, 0, {}, pending);
    CHECK(state_of(engine) == flushed);
    process_ok(engine, 32, output, pending);
    for (std::size_t frame = 0; frame < output.size(); ++frame)
        CHECK_NEAR(output[frame], 0.125L * profile.output_gain *
                   oracle_source(profile, 13, frame + 32, 48000.0), 3e-8L);
    const std::array release{note_off(0, upper, 36)};
    process_ok(engine, 0, {}, release);
    process_ok(engine, 32, output, pending);
    for (const float sample : output) CHECK(sample == 0.0F);
    CHECK(!engine.key_down(upper, 36)); // A consumed flush is never queued again.
}

[[nodiscard]] Engine active_engine(const RuntimeProfile& profile) {
    auto engine = prepare_engine(profile, 48000.0, 500);
    const std::array events{drawbar(0, upper, 0, 7), drawbar(0, upper, 2, 5),
                            drawbar(0, lower, 2, 8), expression(0, 0.625),
                            note_on(0, upper, 36), note_on(0, upper, 48),
                            note_on(0, lower, 96)};
    process_ok(engine, 37, {}, events);
    return engine;
}

void check_continuation(Engine& actual, Engine& reference) {
    const std::array events{drawbar(2, upper, 2, 4), note_off(7, upper, 48),
                            expression(11, 0.875), note_on(13, lower, 36)};
    std::array<float, 31> a{}, b{};
    process_ok(actual, 31, a, events);
    process_ok(reference, 31, b, events);
    check_same_audio(a, b);
    CHECK(state_of(actual) == state_of(reference));
}

void expect_rejected(const Engine& baseline, Status expected, std::uint32_t frames,
                      std::span<float> output, std::span<const Event> events = {}) {
    auto engine = baseline;
    auto reference = baseline;
    const auto before = state_of(engine);
    const std::vector<float> original_output(output.begin(), output.end());
    const auto result = engine.process(frames, output, events);
    CHECK(result.status == expected);
    CHECK(!result.ok());
    CHECK(!static_cast<bool>(result));
    CHECK(result.events_consumed == 0);
    CHECK(state_of(engine) == before);
    check_same_audio(output, original_output);
    if (engine.prepared() && engine.frame_clock() <=
        std::numeric_limits<std::uint64_t>::max() - 31)
        check_continuation(engine, reference);
}

void test_invalid_calls_are_atomic(const RuntimeProfile& nominal) {
    const auto baseline = active_engine(probe_profile(nominal));
    std::array<float, 40> output{};
    output.fill(sentinel);
    const auto invalid_manual = static_cast<Manual>(255);
    const auto invalid_type = static_cast<EventType>(255);
    const std::vector<Event> bad_events{
        {15, EventType::NoteOn, invalid_manual, 36, 1},
        {15, invalid_type, upper, 36, 1},
        {15, static_cast<EventType>(255), upper, 0, 0},
        note_on(15, upper, 35), note_on(15, lower, 97), note_on(15, upper, 255),
        note_on(15, upper, 36, -1), note_on(15, upper, 36, 128),
        note_on(15, upper, 36, 0.5), note_off(15, upper, 35), note_off(15, lower, 97),
        {15, EventType::NoteOff, upper, 36, 1},
        drawbar(15, upper, 9, 8), drawbar(15, lower, 255, 0),
        drawbar(15, upper, 2, -1), drawbar(15, upper, 2, 9), drawbar(15, upper, 2, 1.5),
        expression(15, -0.01), expression(15, 1.01),
        {15, EventType::Expression, lower, 1, 0.5},
        {15, EventType::AllNotesOff, upper, 1, 0},
        {15, EventType::AllNotesOff, lower, 0, 1},
        note_on(16, upper, 36), note_on(std::numeric_limits<std::uint32_t>::max(), upper, 36),
    };
    for (const auto& invalid : bad_events) {
        // The valid prefix would audibly alter state if dispatch preceded full validation.
        const std::array events{expression(0, 0.125), all_off(3, upper), invalid};
        expect_rejected(baseline, Status::InvalidEvent, 16, output, events);
    }
    const std::array event_bases{note_on(15, upper, 36), note_off(15, upper, 36),
                                 drawbar(15, upper, 2, 8), expression(15, 0.5),
                                 all_off(15, lower)};
    for (auto event : event_bases) {
        for (const double nonfinite : {std::numeric_limits<double>::quiet_NaN(),
                                       std::numeric_limits<double>::infinity(),
                                       -std::numeric_limits<double>::infinity()}) {
            event.value = nonfinite;
            const std::array events{expression(0, 0.125), event};
            expect_rejected(baseline, Status::InvalidEvent, 16, output, events);
        }
        event.value = event.type == EventType::NoteOn ? 1.0 : 0.0;
        event.manual = static_cast<Manual>(2);
        const std::array events{expression(0, 0.125), event};
        expect_rejected(baseline, Status::InvalidEvent, 16, output, events);
    }
    const std::array unsorted{expression(0, 0.25), note_on(8, upper, 60), all_off(7, lower)};
    expect_rejected(baseline, Status::InvalidEvent, 16, output, unsorted);
    const std::array bad_flush{expression(0, 0.125), note_off(1, upper, 36)};
    expect_rejected(baseline, Status::InvalidEvent, 0, output, bad_flush);
    const std::array valid{expression(0, 0.125), all_off(0, upper)};
    expect_rejected(baseline, Status::InvalidBuffer, 16,
                     std::span<float>(output).first(15), valid);
    expect_rejected(baseline, Status::BlockTooLarge, max_block + 1, {}, valid);

    std::vector<Event> capacity(hammond::kMaxEventsPerBlock + 1, expression(0, 0.25));
    expect_rejected(baseline, Status::TooManyEvents, 16, output, capacity);
    expect_rejected(baseline, Status::TooManyEvents, 0, output, capacity);
    capacity.pop_back();
    capacity.back().value = std::numeric_limits<double>::quiet_NaN();
    expect_rejected(baseline, Status::InvalidEvent, 16, output, capacity);
    capacity.back().value = 0.75;
    auto full_capacity = baseline;
    process_ok(full_capacity, 0, {}, capacity);
    CHECK(full_capacity.expression() == 0.75);
    process_ok(full_capacity, 1, std::span<float>(output).first(1), capacity);
    CHECK(full_capacity.expression() == 0.75);

    const Engine unprepared;
    output.fill(sentinel);
    expect_rejected(unprepared, Status::NotPrepared, 16, output, valid);
    expect_rejected(unprepared, Status::NotPrepared, 0, output, valid);
}

void test_overflow_and_end_boundary(const RuntimeProfile& nominal) {
    const auto profile = probe_profile(nominal);
    const auto maximum = std::numeric_limits<std::uint64_t>::max();
    auto engine = prepare_engine(profile, 48000.0, maximum - 2);
    const std::array setup{drawbar(0, upper, 2, 8), note_on(0, upper, 36)};
    process_ok(engine, 0, {}, setup);
    std::array<float, 4> output{};
    output.fill(sentinel);
    const std::array changes{expression(0, 0.25), all_off(1, upper)};
    expect_rejected(engine, Status::TimelineOverflow, 3, output, changes);
    process_ok(engine, 2, output);
    CHECK(engine.frame_clock() == maximum);
    CHECK(output[2] == sentinel && output[3] == sentinel);
    for (std::size_t frame = 0; frame < 2; ++frame)
        CHECK_NEAR(output[frame], profile.output_gain *
                   oracle_source(profile, 13, frame, 48000.0), 3e-8L);
    expect_rejected(engine, Status::TimelineOverflow, 1, output);
    const auto phase_before = state_of(engine).phase_bits;
    const std::array flush{note_off(0, upper, 36), expression(0, 0.125)};
    process_ok(engine, 0, output, flush);
    CHECK(engine.frame_clock() == maximum);
    CHECK(state_of(engine).phase_bits == phase_before);
    CHECK(engine.expression() == 0.125);
    CHECK(!engine.key_down(upper, 36));

    auto boundary = prepare_engine(profile);
    const std::array end_event{drawbar(0, upper, 2, 8), note_on(8, upper, 36)};
    expect_rejected(boundary, Status::InvalidEvent, 8, {}, end_event);
    const std::array registration{drawbar(0, upper, 2, 8)};
    process_ok(boundary, 8, {}, registration);
    const std::array retained_by_caller{note_on(0, upper, 36)};
    process_ok(boundary, 1, std::span<float>(output).first(1), retained_by_caller);
    CHECK_NEAR(output[0], profile.output_gain * oracle_source(profile, 13, 8, 48000.0), 3e-8L);
}

void test_disconnected_and_trailing_output(const RuntimeProfile& nominal) {
    const auto profile = probe_profile(nominal);
    auto disconnected = active_engine(profile);
    auto connected = active_engine(profile);
    const std::array events{expression(0, 0.25), note_on(17, upper, 96),
                            all_off(80, upper), all_off(128, lower)};
    std::array<float, 136> output{};
    output.fill(sentinel);
    process_ok(disconnected, 129, {}, events);
    process_ok(connected, 129, output, events);
    CHECK(state_of(disconnected) == state_of(connected));
    CHECK(connected.active_key_count() == 0);
    CHECK(output[0] != sentinel);
    CHECK(output[128] == 0.0F);
    for (std::size_t frame = 129; frame < output.size(); ++frame)
        CHECK(output[frame] == sentinel);
    check_continuation(disconnected, connected);

    auto silent = prepare_engine(profile);
    auto audible = prepare_engine(profile);
    process_ok(silent, 127, {});
    const std::array note{drawbar(0, upper, 2, 8), note_on(0, upper, 36)};
    process_ok(audible, 127, {}, note);
    CHECK(state_of(silent).phase_bits == state_of(audible).phase_bits);
    std::array<float, 31> a{}, b{};
    process_ok(silent, 31, a, note);
    process_ok(audible, 31, b);
    check_same_audio(a, b);
}

void test_prepare_atomicity_and_profile_ownership(const RuntimeProfile& nominal) {
    const auto profile = probe_profile(nominal);
    const auto baseline = active_engine(profile);
    const auto reject = [&](const RuntimeProfile& candidate, const ProcessSpec& spec,
                             Status expected) {
        auto engine = baseline;
        auto reference = baseline;
        const auto before = state_of(engine);
        CHECK(engine.prepare(candidate, spec) == expected);
        CHECK(state_of(engine) == before);
        check_continuation(engine, reference);
    };
    for (const double rate : {0.0, -48000.0, 22050.0, 48000.5,
                              std::numeric_limits<double>::quiet_NaN(),
                              std::numeric_limits<double>::infinity()})
        reject(profile, ProcessSpec{rate, max_block, 123, 900}, Status::InvalidSpec);
    for (const std::uint32_t block : {0U, hammond::kHardMaxBlockFrames + 1})
        reject(profile, ProcessSpec{48000.0, block, 123, 900}, Status::InvalidSpec);
    auto invalid = profile;
    invalid.sources.back().peak_amplitude = std::numeric_limits<double>::quiet_NaN();
    reject(invalid, ProcessSpec{}, Status::InvalidProfile);
    invalid = profile;
    invalid.sources.back().frequency_hz = 24000.0;
    reject(invalid, ProcessSpec{}, Status::InvalidProfile);
    invalid = profile;
    invalid.sources.back().frequency_hz = std::numeric_limits<double>::denorm_min();
    reject(invalid, ProcessSpec{}, Status::InvalidProfile);
    invalid = profile;
    invalid.manual_map.back().back() = 0;
    reject(invalid, ProcessSpec{}, Status::InvalidProfile);
    Engine unprepared;
    const auto initial = state_of(unprepared);
    CHECK(unprepared.prepare(invalid, ProcessSpec{}) == Status::InvalidProfile);
    CHECK(state_of(unprepared) == initial);

    auto caller_profile = profile;
    auto owned = prepare_engine(caller_profile);
    auto reference = prepare_engine(profile);
    caller_profile.output_gain = 0.125;
    caller_profile.sources[12] = {421.25, 0.25, 0.75};
    caller_profile.drawbar_gains[4] = 0.25;
    caller_profile.manual_map[0][2] = 91;
    CHECK(hammond::validate_runtime_profile(caller_profile, 48000.0) == Status::Ok);
    const std::array events{drawbar(0, upper, 2, 8), note_on(0, upper, 36),
                            drawbar(17, upper, 2, 4)};
    std::array<float, 127> a{}, b{};
    process_ok(owned, 127, a, events);
    process_ok(reference, 127, b, events);
    check_same_audio(a, b);
    CHECK(state_of(owned) == state_of(reference));

    // Local profile storage legitimately expires; no borrowed span outlives it.
    auto from_expired_profile = [&profile] {
        const auto local = profile;
        return prepare_engine(local);
    }();
    auto lifetime_reference = prepare_engine(profile);
    process_ok(from_expired_profile, 127, a, events);
    process_ok(lifetime_reference, 127, b, events);
    check_same_audio(a, b);
    CHECK(state_of(from_expired_profile) == state_of(lifetime_reference));
}

struct AbsoluteEvent { std::uint64_t frame; Event event; };
constexpr std::uint64_t timeline_origin = 1234567890ULL;
constexpr std::uint32_t timeline_frames = 2053;

[[nodiscard]] std::vector<AbsoluteEvent> absolute_timeline() {
    // Times straddle all requested block boundaries. Ties retain source order.
    const std::array relative{
        drawbar(0, upper, 0, 8), drawbar(0, upper, 2, 4), drawbar(0, lower, 2, 8),
        note_on(0, upper, 36, 1), note_on(1, upper, 36, 127),
        note_on(16, lower, 36), drawbar(17, upper, 0, 4), expression(18, 0.25),
        note_on(63, upper, 48), note_off(64, upper, 36), note_on(65, upper, 36, 0),
        drawbar(126, lower, 2, 2), note_off(127, upper, 48), note_on(127, upper, 48, 64),
        all_off(128, lower), drawbar(511, upper, 2, 8), expression(512, 0.75),
        all_off(513, upper), note_on(1023, lower, 36), note_on(1024, upper, 36),
        note_on(1025, upper, 48), drawbar(2047, upper, 0, 0),
        all_off(2048, lower), drawbar(2048, upper, 2, 0), drawbar(2052, upper, 2, 4)};
    std::vector<AbsoluteEvent> result;
    for (auto event : relative) {
        const auto frame = timeline_origin + event.offset;
        event.offset = 0;
        result.push_back({frame, event});
    }
    return result;
}

struct TimelineRender { std::vector<float> output; State final_state; };

[[nodiscard]] TimelineRender render_timeline(const RuntimeProfile& profile, double rate,
                                             std::uint32_t block_size, bool flush_at_boundary) {
    const auto timeline = absolute_timeline();
    auto engine = prepare_engine(profile, rate, timeline_origin);
    TimelineRender result{std::vector<float>(timeline_frames, sentinel), {}};
    std::size_t next_event = 0;
    std::size_t consumed = 0;
    for (std::uint32_t start = 0; start < timeline_frames;) {
        const auto count = std::min(block_size, timeline_frames - start);
        const auto begin = timeline_origin + start;
        const auto end = begin + count;
        std::vector<Event> events;
        while (next_event < timeline.size() && timeline[next_event].frame < end) {
            CHECK(timeline[next_event].frame >= begin);
            auto event = timeline[next_event].event;
            event.offset = static_cast<std::uint32_t>(timeline[next_event].frame - begin);
            events.push_back(event);
            ++next_event;
        }
        std::span<const Event> pending(events);
        if (flush_at_boundary) {
            std::size_t flush_count = 0;
            while (flush_count < pending.size() && pending[flush_count].offset == 0)
                ++flush_count;
            const auto before = state_of(engine);
            const auto flushed = engine.process(0, {}, pending.first(flush_count));
            CHECK(flushed.ok());
            CHECK(flushed.events_consumed == flush_count);
            consumed += flushed.events_consumed;
            pending = pending.subspan(flushed.events_consumed);
            CHECK(engine.frame_clock() == before.clock);
            CHECK(state_of(engine).phase_bits == before.phase_bits);
        }
        const auto accepted = engine.process(count,
            std::span<float>(result.output).subspan(start, count), pending);
        CHECK(accepted.ok());
        CHECK(accepted.events_consumed == pending.size());
        consumed += accepted.events_consumed;
        pending = pending.subspan(accepted.events_consumed);
        CHECK(pending.empty());
        start += count;
        CHECK(engine.frame_clock() == timeline_origin + start);
    }
    CHECK(next_event == timeline.size());
    CHECK(consumed == timeline.size());
    CHECK(engine.frame_clock() == timeline_origin + timeline_frames);
    result.final_state = state_of(engine);
    return result;
}

void test_absolute_timeline_partition_invariance(const RuntimeProfile& nominal) {
    const auto profile = probe_profile(nominal);
    // Hand-written gain schedule, not an event interpreter or a second Engine.
    // Only sources 13 and 25 are routed by this timeline's keys and drawbars.
    struct Segment { std::uint32_t begin; long double tone13; long double tone25; long double gain; };
    constexpr std::array segments{
        Segment{0, 1.5L, 0.0L, 1.0L}, Segment{16, 2.5L, 0.0L, 1.0L},
        Segment{17, 2.0L, 0.0L, 1.0L}, Segment{18, 2.0L, 0.0L, 0.25L},
        Segment{63, 2.5L, 0.5L, 0.25L}, Segment{64, 1.5L, 0.5L, 0.25L},
        Segment{126, 0.75L, 0.5L, 0.25L}, Segment{128, 0.5L, 0.5L, 0.25L},
        Segment{511, 0.5L, 1.0L, 0.25L}, Segment{512, 0.5L, 1.0L, 0.75L},
        Segment{513, 0.0L, 0.0L, 0.75L}, Segment{1023, 0.25L, 0.0L, 0.75L},
        Segment{1024, 1.75L, 0.0L, 0.75L}, Segment{1025, 2.25L, 1.0L, 0.75L},
        Segment{2047, 1.25L, 1.0L, 0.75L}, Segment{2048, 0.0L, 0.0L, 0.75L},
        Segment{2052, 0.5L, 0.5L, 0.75L},
    };
    for (const double rate : {44100.0, 48000.0, 96000.0}) {
        const auto reference = render_timeline(profile, rate, 1, false);
        std::size_t segment = 0;
        for (std::uint32_t frame = 0; frame < timeline_frames; ++frame) {
            if (segment + 1 < segments.size() && segments[segment + 1].begin == frame)
                ++segment;
            const auto& expected = segments[segment];
            const auto sample = profile.output_gain * expected.gain *
                (expected.tone13 * oracle_source(profile, 13, frame, rate) +
                 expected.tone25 * oracle_source(profile, 25, frame, rate));
            CHECK_NEAR(reference.output[frame], sample, 8e-8L);
            if (expected.tone13 == 0.0L && expected.tone25 == 0.0L)
                CHECK(reference.output[frame] == 0.0F);
        }
        CHECK(reference.final_state.key_counts == (std::array<std::size_t, 3>{2, 2, 0}));
        CHECK(reference.final_state.bars[0][0] == 0);
        CHECK(reference.final_state.bars[0][2] == 4);
        CHECK(reference.final_state.bars[1][2] == 2);
        CHECK(reference.final_state.expression_bits == std::bit_cast<std::uint64_t>(0.75));
        for (const std::uint32_t block : {1U, 17U, 64U, 127U, 512U, 1024U}) {
            if (block != 1) CHECK(timeline_frames % block != 0); // Partial final block.
            for (const bool flush : {false, true}) {
                const auto actual = render_timeline(profile, rate, block, flush);
                check_same_audio(actual.output, reference.output);
                CHECK(actual.final_state == reference.final_state);
            }
        }
    }
}

void test_checked_diagnostics(const RuntimeProfile& nominal) {
    const auto engine = active_engine(nominal);
    const auto before = state_of(engine);
    const auto invalid_manual = static_cast<Manual>(255);
    CHECK(engine.active_key_count(invalid_manual) == 0);
    CHECK(!engine.key_down(invalid_manual, 36));
    for (const std::uint32_t note : {0U, 35U, 97U, 255U, UINT32_MAX})
        CHECK(!engine.key_down(upper, note));
    std::uint8_t position = 77;
    CHECK(!engine.drawbar_position(invalid_manual, 0, position));
    CHECK(position == 77);
    CHECK(!engine.drawbar_position(upper, 9, position));
    CHECK(position == 77);
    double phase = -17.0;
    for (const ToneId id : {ToneId{0}, ToneId{92}, ToneId{255}}) {
        CHECK(!engine.source_phase_turns(id, phase));
        CHECK(phase == -17.0);
    }
    CHECK(state_of(engine) == before);
}

} // namespace

int main() {
    const auto nominal = load_test_profile();
    test_initial_state_and_independent_sine(nominal);
    test_coherent_foldback_and_printed_top_key(nominal);
    test_velocity_boolean_ownership_and_drawbars(nominal);
    test_manual_sharing_and_selected_all_off(nominal);
    test_exact_timing_tie_order_and_flush(nominal);
    test_invalid_calls_are_atomic(nominal);
    test_overflow_and_end_boundary(nominal);
    test_disconnected_and_trailing_output(nominal);
    test_prepare_atomicity_and_profile_ownership(nominal);
    test_absolute_timeline_partition_invariance(nominal);
    test_checked_diagnostics(nominal);
    std::cout << "Engine: independent sine/routing, musical state, atomic rejection, "
                 "and 3-rate/6-partition timelines passed.\n";
}
