#include "TestSupport.h"
#include "hammond/PerformanceInput.h"

#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <iostream>
#include <limits>
#include <memory>
#include <span>
#include <type_traits>
#include <variant>
#include <vector>

namespace {

using namespace hammond;
using Input = PerformanceInputEvent;
constexpr float sentinel = -9876.25F;

struct Counts {
    std::uint64_t accepted{};
    std::uint64_t rejected{};
    std::uint64_t future_probes{};
    std::uint64_t audio_samples{};
    std::uint64_t partition_samples{};
    std::uint64_t phase_values{};
    std::uint64_t state_pairs{};
    std::uint64_t owner_rows{};
    std::uint64_t partitions{};
} counts;

[[nodiscard]] Event e(std::uint32_t offset, EventType kind, Manual manual,
                      std::uint8_t index, double value) {
    return {offset, kind, manual, index, value};
}

[[nodiscard]] HostNoteEvent m(std::uint32_t offset, HostNoteKind kind,
                              std::uint8_t bus, std::uint8_t channel,
                              std::uint8_t pitch, std::uint8_t velocity = 0,
                              std::int32_t identity = -1) {
    return {offset, kind, bus, channel, pitch, velocity, identity};
}

[[nodiscard]] PedalNoteEvent p(std::uint32_t offset, PedalNoteKind kind,
                               std::uint8_t bus, std::uint8_t channel,
                               std::uint8_t pedal, std::uint8_t velocity = 0,
                               std::int32_t identity = -1) {
    return {offset, kind, bus, channel, PedalId{pedal}, velocity, identity};
}

struct State {
    bool prepared{};
    double rate{};
    std::uint64_t clock{};
    ControlSnapshot controls{};
    ContactMode mode{};
    std::array<std::array<bool, kManualKeyCount>, kManualCount> keys{};
    std::array<std::array<ContactKeySnapshot, kManualKeyCount>, kManualCount> contacts{};
    std::array<bool, kPedalCount> pedals{};
    PedalContactStates pedal_contacts{};
    PedalRenderDiagnostics last_pedal{};
    PercussionRoutingDiagnostics percussion{};
    std::array<double, kToneSourceCount> phases{};
    [[nodiscard]] bool operator==(const State&) const = default;
};

[[nodiscard]] State state(const Engine& engine) {
    State result;
    result.prepared = engine.prepared();
    result.rate = engine.sample_rate();
    result.clock = engine.frame_clock();
    result.controls = engine.controls_snapshot();
    result.mode = engine.contact_mode();
    result.last_pedal = engine.last_pedal_frame();
    result.percussion = engine.percussion_diagnostics();
    if (!result.prepared) return result;
    for (std::size_t division = 0; division < kManualCount; ++division) {
        const auto manual = static_cast<Manual>(division);
        for (std::size_t key = 0; key < kManualKeyCount; ++key) {
            const auto pitch = static_cast<std::uint32_t>(36 + key);
            result.keys[division][key] = engine.key_down(manual, pitch);
            CHECK(engine.contact_snapshot(manual, pitch, result.contacts[division][key]));
        }
    }
    for (std::size_t pedal = 0; pedal < kPedalCount; ++pedal) {
        result.pedals[pedal] = engine.pedal_down(PedalId{static_cast<std::uint8_t>(pedal + 1)});
    }
    CHECK(engine.pedal_contacts_snapshot(result.pedal_contacts));
    for (std::size_t tone = 0; tone < kToneSourceCount; ++tone) {
        CHECK(engine.source_phase_turns(static_cast<ToneId>(tone + 1), result.phases[tone]));
    }
    return result;
}

void same_state(const State& actual, const State& expected) {
    CHECK(actual == expected);
    if (actual.prepared) {
        for (std::size_t tone = 0; tone < kToneSourceCount; ++tone) {
            CHECK(std::bit_cast<std::uint64_t>(actual.phases[tone]) ==
                  std::bit_cast<std::uint64_t>(expected.phases[tone]));
            ++counts.phase_values;
        }
    }
    ++counts.state_pairs;
}

struct Pair {
    Engine actual;
    Engine expected;
    NoteOwnership manuals;
    PedalNoteOwnership pedals;
    std::uint32_t block_limit{};
};

[[nodiscard]] std::unique_ptr<Pair> prepared(const RuntimeProfile& profile,
                                            double rate = 48000.0,
                                            bool travel = true,
                                            std::uint32_t limit = kHardMaxBlockFrames,
                                            std::uint64_t origin = 37) {
    auto result = std::make_unique<Pair>();
    const auto model = travel ? make_nominal_console_model() : make_legacy_console_model();
    CHECK(result->actual.prepare(profile, {rate, limit, 24, origin}, model) == Status::Ok);
    CHECK(result->expected.prepare(profile, {rate, limit, 24, origin}, model) == Status::Ok);
    result->block_limit = limit;
    return result;
}

// The reference is fed only the explicitly declared physical timeline below.
// It never invokes either ownership translator or the combined facade.
std::vector<float> accept(Pair& pair, std::uint32_t frames, const std::vector<Input>& input,
                          const std::vector<Event>& physical, bool connected = true) {
    const auto before = pair.actual.frame_clock();
    std::vector<float> actual(static_cast<std::size_t>(frames) + 3, sentinel);
    std::vector<float> expected(actual.size(), sentinel);
    const auto actual_output = connected ? std::span<float>{actual} : std::span<float>{};
    const auto expected_output = connected ? std::span<float>{expected} : std::span<float>{};
    const auto result = process_performance_input(pair.actual, pair.manuals, pair.pedals,
                                                   frames, actual_output, input);
    CHECK(result.status == Status::Ok);
    CHECK(result.input_events_consumed == input.size());
    CHECK(result.physical_events_consumed == physical.size());
    const auto reference = pair.expected.process(frames, expected_output, physical);
    CHECK(reference.status == Status::Ok);
    CHECK(reference.events_consumed == physical.size());
    CHECK(pair.actual.frame_clock() == before + frames);
    for (std::size_t sample = 0; sample < actual.size(); ++sample) {
        CHECK(std::bit_cast<std::uint32_t>(actual[sample]) ==
              std::bit_cast<std::uint32_t>(expected[sample]));
        if (connected && sample < frames) ++counts.audio_samples;
        else CHECK(actual[sample] == sentinel);
    }
    same_state(state(pair.actual), state(pair.expected));
    ++counts.accepted;
    return actual;
}

void reject(Pair& pair, std::uint32_t frames, const std::vector<Input>& input,
            Status expected_status,
            std::size_t output_size = std::numeric_limits<std::size_t>::max()) {
    if (output_size == std::numeric_limits<std::size_t>::max()) {
        output_size = static_cast<std::size_t>(frames) + 3;
    }
    const auto before = state(pair.actual);
    const auto manuals = pair.manuals;
    const auto pedals = pair.pedals;
    std::vector<float> output(output_size, sentinel);
    const auto result = process_performance_input(pair.actual, pair.manuals, pair.pedals,
                                                   frames, output, input);
    CHECK(result.status == expected_status);
    CHECK(result.input_events_consumed == 0);
    CHECK(result.physical_events_consumed == 0);
    CHECK(pair.manuals == manuals);
    CHECK(pair.pedals == pedals);
    CHECK(std::all_of(output.begin(), output.end(), [](float value) { return value == sentinel; }));
    same_state(state(pair.actual), before);
    same_state(state(pair.actual), state(pair.expected));
    ++counts.rejected;
    if (pair.actual.prepared()) {
        const auto room = std::numeric_limits<std::uint64_t>::max() - before.clock;
        const auto probe = std::min<std::uint64_t>({64, pair.block_limit, room});
        if (probe != 0) {
            accept(pair, static_cast<std::uint32_t>(probe), {}, {});
            ++counts.future_probes;
        }
    }
}

void manual_rows(const NoteOwnership& owners, const std::vector<NoteOwnerSnapshot>& expected) {
    CHECK(owners.owner_count() == expected.size());
    for (std::size_t index = 0; index < expected.size(); ++index) {
        NoteOwnerSnapshot value;
        CHECK(owners.owner_snapshot(index, value));
        CHECK(value == expected[index]);
        ++counts.owner_rows;
    }
}

void pedal_rows(const PedalNoteOwnership& owners, const std::vector<PedalOwnerSnapshot>& expected) {
    CHECK(owners.owner_count() == expected.size());
    for (std::size_t index = 0; index < expected.size(); ++index) {
        PedalOwnerSnapshot value;
        CHECK(owners.owner_snapshot(index, value));
        CHECK(value == expected[index]);
        ++counts.owner_rows;
    }
}

struct Score {
    std::vector<Input> input;
    std::vector<Event> physical;
};

void control(Score& score, Event event) {
    score.input.emplace_back(event);
    score.physical.push_back(event);
}

[[nodiscard]] Score mixed_score() {
    Score s;
    control(s, e(0, EventType::Drawbar, Manual::Upper, 2, 8));
    control(s, e(0, EventType::Drawbar, Manual::Upper, 8, 8));
    control(s, e(0, EventType::Drawbar, Manual::Lower, 2, 5));
    control(s, e(0, EventType::PedalDrawbar, Manual::Lower, 0, 6));
    control(s, e(0, EventType::PedalDrawbar, Manual::Lower, 1, 2));
    control(s, e(0, EventType::Percussion, Manual::Upper, 0, 1));
    control(s, e(0, EventType::Percussion, Manual::Upper, 3, 1));
    control(s, e(0, EventType::Expression, Manual::Upper, 0, 0.75));

    s.input.emplace_back(m(0, HostNoteKind::On, 0, 0, 60, 100, 10));
    s.physical.push_back(e(0, EventType::NoteOn, Manual::Upper, 60, 100));
    s.input.emplace_back(p(0, PedalNoteKind::On, 0, 0, 13, 90, 10));
    s.physical.push_back(e(0, EventType::PedalOn, Manual::Lower, 13, 90));
    // Other channels/origins overlap the same two physical targets.
    s.input.emplace_back(m(32, HostNoteKind::On, 0, 1, 60, 80, 20));
    s.input.emplace_back(p(32, PedalNoteKind::On, 1, 1, 13, 80, 20));
    s.input.emplace_back(m(64, HostNoteKind::On, 0, 0, 60, 127, 10));
    s.input.emplace_back(p(64, PedalNoteKind::On, 0, 0, 13, 127, 10));
    s.input.emplace_back(m(96, HostNoteKind::On, 0, 2, 60, 70));
    s.input.emplace_back(p(96, PedalNoteKind::On, 0, 2, 13, 70));
    s.input.emplace_back(m(96, HostNoteKind::On, 0, 2, 60, 60));
    s.input.emplace_back(p(96, PedalNoteKind::On, 0, 2, 13, 60));
    s.input.emplace_back(m(128, HostNoteKind::On, 1, 0, 64, 100, 10));
    s.physical.push_back(e(128, EventType::NoteOn, Manual::Lower, 64, 100));
    s.input.emplace_back(p(128, PedalNoteKind::On, 0, 0, 25, 100, 30));
    s.physical.push_back(e(128, EventType::PedalOn, Manual::Lower, 25, 100));
    s.input.emplace_back(m(256, HostNoteKind::Off, 0, 0, 60, 0, 10));
    s.input.emplace_back(p(256, PedalNoteKind::Off, 0, 0, 13, 0, 10));
    control(s, e(384, EventType::Cancel, Manual::Lower, 0, 0));
    control(s, e(384, EventType::PedalDrawbar, Manual::Lower, 1, 4));
    s.input.emplace_back(m(512, HostNoteKind::AllNotesOff, 0, 1, 0));
    s.input.emplace_back(p(512, PedalNoteKind::AllNotesOff, 1, 1, 0));
    // FIFO release leaves the second anonymous owner in each namespace.
    s.input.emplace_back(m(640, HostNoteKind::Off, 0, 2, 60));
    s.input.emplace_back(p(640, PedalNoteKind::Off, 0, 2, 13));
    s.input.emplace_back(m(768, HostNoteKind::Off, 0, 2, 60, 0, 999));
    s.input.emplace_back(p(768, PedalNoteKind::Off, 0, 2, 13, 0, 999));
    s.input.emplace_back(m(896, HostNoteKind::On, 0, 2, 60, 0));
    s.physical.push_back(e(896, EventType::NoteOff, Manual::Upper, 60, 0));
    s.input.emplace_back(p(896, PedalNoteKind::On, 0, 2, 13, 0));
    s.physical.push_back(e(896, EventType::PedalOff, Manual::Lower, 13, 0));
    s.input.emplace_back(m(1024, HostNoteKind::On, 0, 0, 65, 100, 55));
    s.physical.push_back(e(1024, EventType::NoteOn, Manual::Upper, 65, 100));
    s.input.emplace_back(p(1024, PedalNoteKind::On, 0, 0, 13, 100, 55));
    s.physical.push_back(e(1024, EventType::PedalOn, Manual::Lower, 13, 100));
    control(s, e(1024, EventType::Cancel, Manual::Upper, 0, 0));
    control(s, e(1024, EventType::PedalDrawbar, Manual::Lower, 0, 0));
    s.input.emplace_back(m(1152, HostNoteKind::On, 0, 0, 65, 12, 55));
    s.input.emplace_back(p(1152, PedalNoteKind::Off, 0, 0, 25, 0, 30));
    s.physical.push_back(e(1152, EventType::PedalOff, Manual::Lower, 25, 0));
    control(s, e(1280, EventType::SelectBank, Manual::Upper, 0, 1));
    control(s, e(1280, EventType::SelectBank, Manual::Lower, 0, 1));
    control(s, e(1280, EventType::PedalDrawbar, Manual::Lower, 0, 8));
    // Scoped panics emit ordinary final releases, not division-wide panics.
    s.input.emplace_back(m(1536, HostNoteKind::AllNotesOff, 0, 0, 0));
    s.physical.push_back(e(1536, EventType::NoteOff, Manual::Upper, 65, 0));
    s.input.emplace_back(m(1536, HostNoteKind::AllNotesOff, 1, 0, 0));
    s.physical.push_back(e(1536, EventType::NoteOff, Manual::Lower, 64, 0));
    s.input.emplace_back(p(1536, PedalNoteKind::AllNotesOff, 0, 0, 0));
    s.physical.push_back(e(1536, EventType::PedalOff, Manual::Lower, 13, 0));
    s.input.emplace_back(m(1536, HostNoteKind::On, 0, 0, 60, 100, 77));
    s.physical.push_back(e(1536, EventType::NoteOn, Manual::Upper, 60, 100));
    s.input.emplace_back(p(1536, PedalNoteKind::On, 0, 0, 13, 100, 77));
    s.physical.push_back(e(1536, EventType::PedalOn, Manual::Lower, 13, 100));
    s.input.emplace_back(m(1792, HostNoteKind::Off, 0, 0, 60, 0, 77));
    s.physical.push_back(e(1792, EventType::NoteOff, Manual::Upper, 60, 0));
    s.input.emplace_back(p(1792, PedalNoteKind::Off, 0, 0, 13, 0, 77));
    s.physical.push_back(e(1792, EventType::PedalOff, Manual::Lower, 13, 0));
    return s;
}

[[nodiscard]] std::uint32_t offset(const Input& value) {
    return std::visit([](const auto& event) { return event.offset; }, value);
}

void test_partitioned_timeline(const RuntimeProfile& profile) {
    const auto score = mixed_score();
    const std::array<std::vector<std::uint32_t>, 4> partitions{{{2048}, {1}, {7, 13, 64, 127}, {256}}};
    for (const auto rate : {44100.0, 48000.0, 96000.0}) {
        for (const bool travel : {false, true}) {
            auto whole = prepared(profile, rate, travel);
            const auto whole_audio = accept(*whole, 2048, score.input, score.physical);
            for (const auto& sizes : partitions) {
                auto split = prepared(profile, rate, travel);
                std::uint32_t cursor = 0;
                std::size_t piece = 0;
                while (cursor < 2048) {
                    const auto frames = std::min(sizes[piece++ % sizes.size()], 2048U - cursor);
                    std::vector<Input> input;
                    std::vector<Event> physical;
                    for (auto event : score.input) {
                        if (offset(event) < cursor || offset(event) >= cursor + frames) continue;
                        std::visit([cursor](auto& item) { item.offset -= cursor; }, event);
                        input.push_back(event);
                    }
                    for (auto event : score.physical) {
                        if (event.offset < cursor || event.offset >= cursor + frames) continue;
                        event.offset -= cursor;
                        physical.push_back(event);
                    }
                    const auto part_audio = accept(*split, frames, input, physical);
                    for (std::uint32_t sample = 0; sample < frames; ++sample) {
                        CHECK(std::bit_cast<std::uint32_t>(part_audio[sample]) ==
                              std::bit_cast<std::uint32_t>(whole_audio[cursor + sample]));
                        ++counts.partition_samples;
                    }
                    cursor += frames;
                }
                same_state(state(split->actual), state(whole->actual));
                CHECK(split->manuals == whole->manuals);
                CHECK(split->pedals == whole->pedals);
                CHECK(split->manuals.owner_count() == 0);
                CHECK(split->pedals.owner_count() == 0);
                ++counts.partitions;
            }
            auto silent = prepared(profile, rate, travel);
            accept(*silent, 2048, score.input, score.physical, false);
            same_state(state(silent->actual), state(whole->actual));
            accept(*silent, 211, {}, {});
            accept(*whole, 211, {}, {});
            same_state(state(silent->actual), state(whole->actual));
        }
    }
}

void test_routing_fifo_and_ties(const RuntimeProfile& profile) {
    auto pair = prepared(profile);
    CHECK(pair->manuals.set_routes({Manual::Upper, Manual::Upper}));
    accept(*pair, 0,
           {m(0, HostNoteKind::On, 0, 0, 60, 100),
            m(0, HostNoteKind::On, 1, 0, 60, 100, 7),
            p(0, PedalNoteKind::On, 0, 0, 13, 100),
            p(0, PedalNoteKind::On, 1, 0, 13, 100, 7)},
           {e(0, EventType::NoteOn, Manual::Upper, 60, 100),
            e(0, EventType::PedalOn, Manual::Lower, 13, 100)});
    CHECK(pair->manuals.set_bus_route(0, Manual::Lower));
    accept(*pair, 0,
           {m(0, HostNoteKind::On, 0, 0, 60, 90),
            p(0, PedalNoteKind::On, 0, 0, 13, 90)},
           {e(0, EventType::NoteOn, Manual::Lower, 60, 90)});
    manual_rows(pair->manuals, {{0, 0, 60, -1, Manual::Upper},
                               {1, 0, 60, 7, Manual::Upper},
                               {0, 0, 60, -1, Manual::Lower}});
    pedal_rows(pair->pedals, {{0, 0, PedalId{13}, -1}, {1, 0, PedalId{13}, 7},
                             {0, 0, PedalId{13}, -1}});
    // FIFO releases the original Upper owner, despite the current Lower route.
    accept(*pair, 0, {m(0, HostNoteKind::Off, 0, 0, 60),
                      p(0, PedalNoteKind::Off, 0, 0, 13)}, {});
    manual_rows(pair->manuals, {{1, 0, 60, 7, Manual::Upper},
                               {0, 0, 60, -1, Manual::Lower}});
    pedal_rows(pair->pedals, {{1, 0, PedalId{13}, 7}, {0, 0, PedalId{13}, -1}});
    accept(*pair, 0, {m(0, HostNoteKind::AllNotesOff, 1, 0, 0),
                      p(0, PedalNoteKind::AllNotesOff, 1, 0, 0)},
           {e(0, EventType::NoteOff, Manual::Upper, 60, 0)});
    CHECK(pair->actual.key_down(Manual::Lower, 60));
    CHECK(pair->actual.pedal_down(PedalId{13}));
    const auto phase_before = state(pair->actual).phases;
    const std::vector<Event> controls{
        e(0, EventType::BankDrawbar, Manual::Lower, 0, 8),
        e(0, EventType::SelectBank, Manual::Lower, 0, 0),
        e(0, EventType::Drawbar, Manual::Lower, 1, 7),
        e(0, EventType::Cancel, Manual::Lower, 0, 0),
        e(0, EventType::SelectBank, Manual::Lower, 0, 1),
        e(0, EventType::Drawbar, Manual::Lower, 2, 5),
        e(0, EventType::PedalDrawbar, Manual::Lower, 0, 8)};
    std::vector<Input> input(controls.begin(), controls.end());
    accept(*pair, 0, input, controls);
    CHECK(state(pair->actual).phases == phase_before);
    std::uint8_t position = 0;
    CHECK(pair->actual.bank_drawbar_position(Manual::Lower, DrawbarBank::A, 1, position));
    CHECK(position == 7);
    CHECK(pair->actual.bank_drawbar_position(Manual::Lower, DrawbarBank::B, 2, position));
    CHECK(position == 5);
    accept(*pair, 512, {}, {});
    // Manual channel release leaves the independently owned pedal audible.
    accept(*pair, 0, {m(0, HostNoteKind::AllNotesOff, 0, 0, 0)},
           {e(0, EventType::NoteOff, Manual::Lower, 60, 0)});
    CHECK(pair->pedals.owner_count() == 1);
    CHECK(pair->actual.pedal_down(PedalId{13}));
    accept(*pair, 0,
           {p(0, PedalNoteKind::Off, 0, 0, 13),
            p(0, PedalNoteKind::On, 0, 0, 13, 100, 8),
            e(0, EventType::Expression, Manual::Lower, 0, 0.5),
            p(0, PedalNoteKind::Off, 0, 0, 13, 0, 8),
            p(0, PedalNoteKind::On, 0, 0, 13, 70, 9)},
           {e(0, EventType::PedalOff, Manual::Lower, 13, 0),
            e(0, EventType::PedalOn, Manual::Lower, 13, 100),
            e(0, EventType::Expression, Manual::Lower, 0, 0.5),
            e(0, EventType::PedalOff, Manual::Lower, 13, 0),
            e(0, EventType::PedalOn, Manual::Lower, 13, 70)});
    pedal_rows(pair->pedals, {{0, 0, PedalId{13}, 9}});
    accept(*pair, 64, {}, {});
    CHECK(pair->actual.reconfigure_sample_rate(96000.0) == Status::Ok);
    CHECK(pair->expected.reconfigure_sample_rate(96000.0) == Status::Ok);
    accept(*pair, 127, {}, {});
}

void test_capacity(const RuntimeProfile& profile) {
    auto pair = prepared(profile, 48000.0, false);
    Score full;
    std::vector<NoteOwnerSnapshot> manual_expected;
    std::vector<PedalOwnerSnapshot> pedal_expected;
    for (std::uint32_t i = 0; i < 256; ++i) {
        const auto bus = static_cast<std::uint8_t>(i / 128);
        const auto pitch = static_cast<std::uint8_t>(36 + (i % 128) % 61);
        full.input.emplace_back(m(0, HostNoteKind::On, bus, 0, pitch, 100,
                                  static_cast<std::int32_t>(i)));
        manual_expected.push_back({bus, 0, pitch, static_cast<std::int32_t>(i),
                                   static_cast<Manual>(bus)});
        if (i % 128 < 61) full.physical.push_back(
            e(0, EventType::NoteOn, static_cast<Manual>(bus), pitch, 100));
    }
    for (std::uint32_t i = 0; i < 256; ++i) {
        const auto pedal = static_cast<std::uint8_t>(i % 25 + 1);
        full.input.emplace_back(p(0, PedalNoteKind::On, 0, 0, pedal, 100,
                                  static_cast<std::int32_t>(i)));
        pedal_expected.push_back({0, 0, PedalId{pedal}, static_cast<std::int32_t>(i)});
        if (i < 25) full.physical.push_back(e(0, EventType::PedalOn, Manual::Lower, pedal, 100));
    }
    CHECK(full.input.size() == 512);
    CHECK(full.physical.size() == 147);
    accept(*pair, 0, full.input, full.physical);
    manual_rows(pair->manuals, manual_expected);
    pedal_rows(pair->pedals, pedal_expected);
    CHECK(pair->actual.active_key_count() == 122);
    CHECK(pair->actual.active_pedal_count() == 25);
    reject(*pair, 1, {m(0, HostNoteKind::On, 0, 0, 60, 100, 256)}, Status::TooManyEvents);
    reject(*pair, 1, {p(0, PedalNoteKind::On, 0, 0, 13, 100, 256)}, Status::TooManyEvents);

    Score release;
    for (std::uint32_t i = 0; i < 877; ++i) {
        control(release, e(0, EventType::Expression, Manual::Upper, 0, 0.75));
    }
    release.input.emplace_back(m(0, HostNoteKind::AllNotesOff, 0, 0, 0));
    release.input.emplace_back(m(0, HostNoteKind::AllNotesOff, 1, 0, 0));
    release.input.emplace_back(p(0, PedalNoteKind::AllNotesOff, 0, 0, 0));
    for (const auto manual : {Manual::Upper, Manual::Lower}) {
        // Pitches 36..41 have a third owner at the end of each 128-owner set;
        // their final releases therefore follow the two-owner pitches 42..96.
        for (std::uint8_t pitch = 42; pitch <= 96; ++pitch) {
            release.physical.push_back(e(0, EventType::NoteOff, manual, pitch, 0));
        }
        for (std::uint8_t pitch = 36; pitch <= 41; ++pitch) {
            release.physical.push_back(e(0, EventType::NoteOff, manual, pitch, 0));
        }
    }
    // Likewise, pedals 1..6 occur in the final partial repetition of 256 owners.
    for (std::uint8_t pedal = 7; pedal <= 25; ++pedal) {
        release.physical.push_back(e(0, EventType::PedalOff, Manual::Lower, pedal, 0));
    }
    for (std::uint8_t pedal = 1; pedal <= 6; ++pedal) {
        release.physical.push_back(e(0, EventType::PedalOff, Manual::Lower, pedal, 0));
    }
    CHECK(release.input.size() == 880);
    CHECK(release.physical.size() == 1024);
    auto over = release.input;
    over.emplace_back(e(0, EventType::Expression, Manual::Lower, 0, 1));
    reject(*pair, 1, over, Status::TooManyEvents);
    manual_rows(pair->manuals, manual_expected);
    pedal_rows(pair->pedals, pedal_expected);
    accept(*pair, 0, release.input, release.physical);
    CHECK(pair->manuals.owner_count() == 0);
    CHECK(pair->pedals.owner_count() == 0);
    CHECK(pair->actual.active_key_count() == 0);
    CHECK(pair->actual.active_pedal_count() == 0);

    std::vector<Input> raw(1024, m(0, HostNoteKind::Off, 0, 0, 60, 0, 999));
    accept(*pair, 1, raw, {});
    raw.emplace_back(p(0, PedalNoteKind::Off, 0, 0, 13, 0, 999));
    reject(*pair, 1, raw, Status::TooManyEvents);
    raw.front() = e(0, EventType::NoteOn, Manual::Upper, 60, 100);
    reject(*pair, 65537, raw, Status::BlockTooLarge);
    reject(*pair, 1, raw, Status::TooManyEvents);
    accept(*pair, 65536, {}, {}, false);
}

void test_atomic_failures(const RuntimeProfile& profile) {
    auto pair = prepared(profile);
    const std::vector<Event> beginning{
        e(0, EventType::Drawbar, Manual::Upper, 2, 8),
        e(0, EventType::PedalDrawbar, Manual::Lower, 0, 8),
        e(0, EventType::NoteOn, Manual::Upper, 60, 100),
        e(0, EventType::PedalOn, Manual::Lower, 13, 100)};
    accept(*pair, 1024,
           {beginning[0], beginning[1], m(0, HostNoteKind::On, 0, 0, 60, 100, 1),
            p(0, PedalNoteKind::On, 0, 0, 13, 100, 1)}, beginning);
    const std::vector<Input> bad{
        e(2, EventType::NoteOn, Manual::Upper, 61, 100),
        e(2, EventType::NoteOff, Manual::Upper, 60, 0),
        e(2, EventType::KeyPosition, Manual::Upper, 60, 0.5),
        e(2, EventType::AllNotesOff, Manual::Upper, 0, 0),
        e(2, EventType::PedalOn, Manual::Lower, 13, 100),
        e(2, EventType::PedalOff, Manual::Lower, 13, 0),
        e(2, EventType::PedalAllNotesOff, Manual::Lower, 0, 0),
        e(2, static_cast<EventType>(255), Manual::Upper, 0, 0),
        e(2, EventType::Expression, Manual::Upper, 0, std::numeric_limits<double>::quiet_NaN()),
        e(2, EventType::PedalDrawbar, Manual::Upper, 0, 1),
        e(2, EventType::Drawbar, Manual::Upper, 9, 8),
        e(2, EventType::SelectBank, Manual::Lower, 0, 2),
        e(2, EventType::Percussion, Manual::Lower, 0, 1),
        m(2, HostNoteKind::On, 2, 0, 60, 100, 3),
        m(2, HostNoteKind::On, 0, 16, 60, 100, 3),
        m(2, HostNoteKind::On, 0, 0, 35, 100, 3),
        m(2, HostNoteKind::On, 0, 0, 60, 128, 3),
        m(2, HostNoteKind::Off, 0, 0, 60, 1, 1),
        m(2, HostNoteKind::On, 0, 0, 61, 100, 1),
        m(2, HostNoteKind::AllNotesOff, 0, 0, 60),
        p(2, PedalNoteKind::On, 2, 0, 13, 100, 3),
        p(2, PedalNoteKind::On, 0, 16, 13, 100, 3),
        p(2, PedalNoteKind::On, 0, 0, 0, 100, 3),
        p(2, PedalNoteKind::On, 0, 0, 26, 100, 3),
        p(2, PedalNoteKind::On, 0, 0, 13, 100, -2),
        p(2, PedalNoteKind::On, 0, 0, 14, 100, 1),
        p(2, PedalNoteKind::AllNotesOff, 0, 0, 13)};
    for (const auto& invalid : bad) {
        reject(*pair, 8,
               {e(0, EventType::Drawbar, Manual::Upper, 0, 8),
                m(1, HostNoteKind::On, 0, 3, 64, 100, 5000),
                p(1, PedalNoteKind::On, 1, 3, 25, 100, 5000), invalid}, Status::InvalidEvent);
    }
    reject(*pair, 8, {m(4, HostNoteKind::Off, 0, 0, 60, 0, 1),
                       p(3, PedalNoteKind::Off, 0, 0, 13, 0, 1)}, Status::InvalidEvent);
    reject(*pair, 8, {p(8, PedalNoteKind::Off, 0, 0, 13, 0, 1)}, Status::InvalidEvent);
    reject(*pair, 0, {m(1, HostNoteKind::Off, 0, 0, 60, 0, 1)}, Status::InvalidEvent);
    reject(*pair, 8, {m(0, HostNoteKind::Off, 0, 0, 60, 0, 1),
                       p(0, PedalNoteKind::Off, 0, 0, 13, 0, 1)}, Status::InvalidBuffer, 7);
    // Global kind/offset admission precedes even Engine's unprepared/buffer gate.
    auto empty = std::make_unique<Pair>();
    reject(*empty, 8, {e(0, EventType::NoteOn, Manual::Upper, 60, 100)}, Status::InvalidEvent, 1);
    reject(*empty, 8, {m(0, HostNoteKind::On, 0, 0, 60, 100, 1),
                       p(0, PedalNoteKind::On, 0, 0, 13, 100, 1)}, Status::NotPrepared, 1);
    auto small = prepared(profile, 48000.0, true, 32);
    reject(*small, 33, {m(0, HostNoteKind::On, 0, 0, 60, 100, 1)}, Status::BlockTooLarge, 1);
    auto end = prepared(profile, 48000.0, true, 32,
                        std::numeric_limits<std::uint64_t>::max() - 2);
    reject(*end, 3, {m(0, HostNoteKind::On, 0, 0, 60, 100, 1),
                    p(0, PedalNoteKind::On, 0, 0, 13, 100, 1)}, Status::TimelineOverflow);
}

} // namespace

int main() {
    const auto profile = load_test_profile();
    test_partitioned_timeline(profile);
    test_routing_fifo_and_ties(profile);
    test_capacity(profile);
    test_atomic_failures(profile);
    std::cout << "performance acceptance: accepted=" << counts.accepted
              << " atomic_rejections=" << counts.rejected
              << " rejected_future_probes=" << counts.future_probes
              << " bitwise_audio_samples=" << counts.audio_samples
              << " partition_audio_samples=" << counts.partition_samples
              << " bitwise_phase_values=" << counts.phase_values
              << " complete_state_pairs=" << counts.state_pairs
              << " explicit_owner_rows=" << counts.owner_rows
              << " partition_runs=" << counts.partitions << '\n';
}
