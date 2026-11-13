#include "TestSupport.h"
#include "hammond/HostTimeline.h"

#include <algorithm>
#include <array>
#include <bit>
#include <cmath>
#include <cstdint>
#include <limits>
#include <memory>
#include <span>
#include <vector>

namespace {

using namespace hammond;
constexpr float sentinel = -987.25F;
constexpr double audio_tolerance = 2.0e-7;
constexpr double curve_tolerance = 8.0 * std::numeric_limits<double>::epsilon();

struct Counts {
    std::uint64_t calls{};
    std::uint64_t oracle_frames{};
    std::uint64_t phase_values{};
    std::uint64_t exact_samples{};
    std::uint64_t rejections{};
    std::uint64_t future_probes{};
    std::uint64_t threshold_cases{};
    std::uint64_t partitions{};
    double maximum_audio_error{};
    double maximum_curve_error{};
} counts;

[[nodiscard]] bool bits(double a, double b) {
    return std::bit_cast<std::uint64_t>(a) == std::bit_cast<std::uint64_t>(b);
}

void phases(const Engine& a, const Engine& b) {
    CHECK(a.prepared() == b.prepared());
    if (!a.prepared()) return;
    for (std::uint8_t tone = 1; tone <= kToneSourceCount; ++tone) {
        double left = 0.0;
        double right = 0.0;
        CHECK(a.source_phase_turns(tone, left));
        CHECK(b.source_phase_turns(tone, right));
        CHECK(bits(left, right));
        ++counts.phase_values;
    }
}

void exact_audio(std::span<const float> actual, std::span<const float> expected) {
    CHECK(actual.size() == expected.size());
    for (std::size_t i = 0; i < actual.size(); ++i) {
        CHECK(std::bit_cast<std::uint32_t>(actual[i]) == std::bit_cast<std::uint32_t>(expected[i]));
        ++counts.exact_samples;
    }
}

void carry_equal(const HostCarryEvent& a, const HostCarryEvent& b) {
    CHECK(a.index() == b.index());
    if (const auto* p = std::get_if<HostParameterCarry>(&a)) {
        const auto& q = std::get<HostParameterCarry>(b);
        CHECK(p->parameter_id == q.parameter_id);
        CHECK(bits(p->normalized, q.normalized));
    } else if (const auto* n = std::get_if<HostNoteEvent>(&a)) {
        const auto& m = std::get<HostNoteEvent>(b);
        CHECK(n->offset == m.offset && n->kind == m.kind && n->bus == m.bus &&
              n->channel == m.channel && n->midi_note == m.midi_note &&
              n->velocity == m.velocity && n->note_id == m.note_id);
    } else {
        const auto& pedal_a = std::get<PedalNoteEvent>(a);
        const auto& pedal_b = std::get<PedalNoteEvent>(b);
        CHECK(pedal_a.offset == pedal_b.offset && pedal_a.kind == pedal_b.kind &&
              pedal_a.bus == pedal_b.bus && pedal_a.channel == pedal_b.channel &&
              pedal_a.pedal == pedal_b.pedal && pedal_a.velocity == pedal_b.velocity &&
              pedal_a.note_id == pedal_b.note_id);
    }
}

void live_equal(const HostTimeline& a, const HostTimeline& b) {
    CHECK(a.max_block_frames() == b.max_block_frames());
    CHECK(a.engine().prepared() == b.engine().prepared());
    CHECK(a.engine().frame_clock() == b.engine().frame_clock());
    CHECK(bits(a.engine().sample_rate(), b.engine().sample_rate()));
    CHECK(a.engine().controls_snapshot() == b.engine().controls_snapshot());
    CHECK(bits(a.engine().expression(), b.engine().expression()));
    CHECK(a.engine().percussion_diagnostics() == b.engine().percussion_diagnostics());
    CHECK(a.engine().last_pedal_frame() == b.engine().last_pedal_frame());
    CHECK(a.manual_ownership() == b.manual_ownership());
    CHECK(a.pedal_ownership() == b.pedal_ownership());
    CHECK(a.carry_count() == b.carry_count());
    for (std::size_t i = 0; i < a.carry_count(); ++i) {
        HostCarryEvent left;
        HostCarryEvent right;
        CHECK(a.carry_event(i, left) && b.carry_event(i, right));
        carry_equal(left, right);
    }
    if (!a.engine().prepared()) return;
    for (const auto& descriptor : parameter_descriptors()) {
        double left = 0.0;
        double right = 0.0;
        CHECK(a.normalized_anchor(descriptor.id, left));
        CHECK(b.normalized_anchor(descriptor.id, right));
        CHECK(bits(left, right));
    }
    for (const auto manual : {Manual::Upper, Manual::Lower}) {
        for (std::uint32_t midi = 36; midi <= 96; ++midi) {
            CHECK(a.engine().key_down(manual, midi) == b.engine().key_down(manual, midi));
            ContactKeySnapshot left;
            ContactKeySnapshot right;
            CHECK(a.engine().contact_snapshot(manual, midi, left));
            CHECK(b.engine().contact_snapshot(manual, midi, right));
            CHECK(left == right);
        }
    }
    PedalContactStates left;
    PedalContactStates right;
    CHECK(a.engine().pedal_contacts_snapshot(left));
    CHECK(b.engine().pedal_contacts_snapshot(right));
    CHECK(left == right);
    phases(a.engine(), b.engine());
}

[[nodiscard]] HostTimelineResult accepted(
    HostTimeline& timeline, std::uint32_t frames, std::span<float> output,
    std::span<const HostParameterQueue> queues = {},
    std::span<const HostMusicalEvent> music = {},
    std::span<const ControlSnapshot> restores = {}) {
    const auto before = timeline.engine().frame_clock();
    const auto old_carry = timeline.carry_count();
    auto raw = music.size();
    for (const auto& queue : queues) raw += queue.points.size();
    const auto result = timeline.process(frames, output, queues, music, restores);
    CHECK(result.status == Status::Ok);
    CHECK(result.input_records_consumed == raw);
    CHECK(result.carried_records_consumed == old_carry);
    CHECK(result.restores_consumed == restores.size());
    CHECK(timeline.engine().frame_clock() == before + frames);
    CHECK(result.engine_calls >= 1);
    ++counts.calls;
    return result;
}

void rejected(HostTimeline& timeline, Status expected, std::uint32_t frames,
              std::span<const HostParameterQueue> queues = {},
              std::span<const HostMusicalEvent> music = {},
              std::span<const ControlSnapshot> restores = {}, bool small_output = false) {
    auto reference = std::make_unique<HostTimeline>(timeline);
    std::vector<float> output(static_cast<std::size_t>(std::min(frames, 65536U)) + 4, sentinel);
    const auto span = small_output ? std::span<float>{output.data(), 1} : std::span<float>{output};
    const auto result = timeline.process(frames, span, queues, music, restores);
    CHECK(result.status == expected);
    CHECK(result.input_records_consumed == 0 && result.carried_records_consumed == 0 &&
          result.restores_consumed == 0 && result.physical_events_applied == 0 &&
          result.engine_calls == 0);
    CHECK(std::all_of(output.begin(), output.end(), [](float v) { return v == sentinel; }));
    live_equal(timeline, *reference);
    ++counts.rejections;
    if (timeline.engine().prepared() &&
        timeline.engine().frame_clock() <= std::numeric_limits<std::uint64_t>::max() - 16) {
        const auto length = std::min(16U, timeline.max_block_frames());
        std::array<float, 16> actual{};
        std::array<float, 16> expected_output{};
        (void)accepted(timeline, length, std::span<float>{actual}.first(length));
        (void)accepted(*reference, length, std::span<float>{expected_output}.first(length));
        exact_audio(std::span<const float>{actual}.first(length),
                    std::span<const float>{expected_output}.first(length));
        live_equal(timeline, *reference);
        ++counts.future_probes;
    }
}

// A separate barycentric long-double oracle, with explicit tie collapse. It
// does not use the production cursor, interpolation expression or gain table.
[[nodiscard]] double oracle_curve(double anchor, std::span<const HostParameterPoint> points,
                                   std::int32_t sample) {
    long double prior_time = -1.0L;
    long double prior_value = anchor;
    std::size_t next = 0;
    while (next < points.size()) {
        auto point = points[next++];
        while (next < points.size() && points[next].offset == point.offset) point = points[next++];
        if (sample == point.offset) return point.normalized;
        if (sample < point.offset) {
            const auto right_time = static_cast<long double>(point.offset);
            const auto at = static_cast<long double>(sample);
            return static_cast<double>((prior_value * (right_time - at) +
                static_cast<long double>(point.normalized) * (at - prior_time)) /
                (right_time - prior_time));
        }
        prior_time = point.offset;
        prior_value = point.normalized;
    }
    return static_cast<double>(prior_value);
}

[[nodiscard]] double oracle_position(double normalized) {
    unsigned position = 0;
    for (unsigned step = 0; step < 8; ++step) {
        if (16.0L * static_cast<long double>(normalized) >= static_cast<long double>(2 * step + 1)) {
            ++position;
        }
    }
    return static_cast<double>(position);
}

[[nodiscard]] Event oracle_event(std::uint32_t id, double normalized) {
    for (std::uint32_t group = 0; group < 4; ++group) {
        const auto first = 0x1000U + group * 0x10U;
        if (id >= first && id <= first + 8) {
            return {0, EventType::BankDrawbar, group < 2 ? Manual::Upper : Manual::Lower,
                static_cast<std::uint8_t>((group % 2) * 9 + id - first), oracle_position(normalized)};
        }
    }
    if (id == 0x2000U) return {0, EventType::Expression, Manual::Upper, 0, normalized};
    if (id == 0x2010U || id == 0x2011U) {
        return {0, EventType::SelectBank, id == 0x2010U ? Manual::Upper : Manual::Lower,
                0, normalized >= 0.5 ? 1.0 : 0.0};
    }
    if (id >= 0x3000U && id <= 0x3003U) {
        return {0, EventType::Percussion, Manual::Upper,
                static_cast<std::uint8_t>(id - 0x3000U), normalized >= 0.5 ? 1.0 : 0.0};
    }
    CHECK(id == 0x4000U || id == 0x4001U);
    return {0, EventType::PedalDrawbar, Manual::Lower,
            static_cast<std::uint8_t>(id - 0x4000U), oracle_position(normalized)};
}

[[nodiscard]] ControlSnapshot registration() {
    ControlSnapshot result;
    result.drawbars[0][1][2] = 4;
    result.drawbars[0][0][2] = 2;
    result.drawbars[1][1][2] = 3;
    result.pedal_drawbars = {6, 2};
    result.percussion.enabled = true;
    return result;
}

void test_all_ids_and_thresholds(const RuntimeProfile& profile) {
    auto timeline = std::make_unique<HostTimeline>();
    CHECK(timeline->prepare(profile, {48000.0, 64, 28, 0}) == Status::Ok);
    Engine reference;
    CHECK(reference.prepare(profile, {48000.0, 65536, 28, 0}) == Status::Ok);
    std::array<std::uint32_t, 45> ids{};
    std::size_t index = 0;
    for (std::uint32_t group = 0; group < 4; ++group) {
        for (std::uint32_t bar = 0; bar < 9; ++bar) ids[index++] = 0x1000U + group * 0x10U + bar;
    }
    for (const auto id : {0x2000U, 0x2010U, 0x2011U, 0x3000U, 0x3001U, 0x3002U,
                          0x3003U, 0x4000U, 0x4001U}) ids[index++] = id;
    CHECK(index == ids.size());
    for (const auto id : ids) {
        const auto discrete_eight = id < 0x2000U || id >= 0x4000U;
        const auto steps = discrete_eight ? 8U : 1U;
        for (unsigned step = 0; step < steps; ++step) {
            const auto threshold = discrete_eight ? static_cast<double>(2 * step + 1) / 16.0 : 0.5;
            for (const auto value : {std::nextafter(threshold, 0.0), threshold,
                                     std::nextafter(threshold, 1.0)}) {
                const std::array<HostParameterPoint, 1> points{{{0, value}}};
                const std::array<HostParameterQueue, 1> queues{{{id, points}}};
                (void)accepted(*timeline, 0, {}, queues);
                const auto expected = oracle_event(id, value);
                CHECK(reference.process(0, {}, std::span<const Event>{&expected, 1}));
                CHECK(timeline->engine().controls_snapshot() == reference.controls_snapshot());
                double anchor = -1.0;
                CHECK(timeline->normalized_anchor(id, anchor));
                CHECK(bits(anchor, value));
                CHECK(timeline->carry_count() == 0);
                ++counts.threshold_cases;
            }
        }
    }
    std::array<HostParameterPoint, 45> points{};
    std::array<HostParameterQueue, 45> queues{};
    std::array<Event, 45> expected{};
    for (std::size_t i = 0; i < ids.size(); ++i) {
        points[i] = {0, i % 2 == 0 ? 0.5 : 0.875};
        queues[ids.size() - 1 - i] = {ids[i], std::span<const HostParameterPoint>{&points[i], 1}};
        expected[i] = oracle_event(ids[i], points[i].normalized);
    }
    std::array<float, 19> output{};
    output.fill(sentinel);
    const auto result = accepted(*timeline, 16, output, queues);
    CHECK(result.physical_events_applied == 45);
    std::array<float, 16> oracle{};
    CHECK(reference.process(16, oracle, expected));
    exact_audio(std::span<const float>{output}.first(16), oracle);
    for (std::size_t i = 16; i < output.size(); ++i) CHECK(output[i] == sentinel);
    phases(timeline->engine(), reference);
}

void test_interpolation_and_boundary(const RuntimeProfile& profile) {
    constexpr std::uint32_t length = 1536;
    const std::array<HostParameterPoint, 6> expression{{
        {0, 0.125}, {17, 0.875}, {17, 0.625}, {300, 0.125}, {1024, 0.75}, {1536, 0.5}}};
    const std::array<HostParameterPoint, 4> pedal{{{15, 1.0}, {31, 0.0}, {700, 1.0}, {1536, 0.25}}};
    const std::array<HostParameterPoint, 4> upper{{{63, 0.5}, {128, 0.125}, {900, 0.875}, {1535, 0.25}}};
    const std::array<HostParameterQueue, 3> queues{{{0x4000U, pedal}, {0x2000U, expression},
                                                  {0x1012U, upper}}};
    const std::array<HostMusicalEvent, 12> notes{{
        HostNoteEvent{0, HostNoteKind::On, 0, 0, 60, 100, 1},
        HostNoteEvent{0, HostNoteKind::On, 1, 0, 48, 100, 2},
        PedalNoteEvent{0, PedalNoteKind::On, 0, 0, PedalId{1}, 100, 3},
        PedalNoteEvent{1, PedalNoteKind::On, 1, 1, PedalId{1}, 100, 4},
        HostNoteEvent{11, HostNoteKind::On, 0, 1, 60, 100, 5},
        HostNoteEvent{20, HostNoteKind::Off, 0, 0, 60, 0, 1},
        PedalNoteEvent{20, PedalNoteKind::Off, 0, 0, PedalId{1}, 0, 3},
        HostNoteEvent{35, HostNoteKind::Off, 0, 1, 60, 0, 5},
        HostNoteEvent{37, HostNoteKind::On, 0, 0, 60, 100, -1},
        HostNoteEvent{70, HostNoteKind::Off, 0, 0, 60, 0, -1},
        HostNoteEvent{length, HostNoteKind::Off, 1, 0, 48, 0, 2},
        PedalNoteEvent{length, PedalNoteKind::On, 0, 0, PedalId{25}, 100, 6}
    }};
    for (const double rate : {44100.0, 48000.0, 96000.0}) {
        for (const auto nominal : {false, true}) {
            const auto model = nominal ? make_nominal_console_model() : make_legacy_console_model();
            auto timeline = std::make_unique<HostTimeline>();
            CHECK(timeline->prepare(profile, {rate, length, 28, 91}, model) == Status::Ok);
            Engine reference;
            CHECK(reference.prepare(profile, {rate, 65536, 28, 91}, model) == Status::Ok);
            const auto controls = registration();
            CHECK(reference.restore_controls(controls));
            std::vector<float> actual(length + 3, sentinel);
            const auto result = accepted(*timeline, length, actual, queues, notes,
                                          std::span<const ControlSnapshot>{&controls, 1});
            CHECK(result.engine_calls > 1 && result.engine_calls < 16);
            CHECK(timeline->carry_count() == 4);
            for (std::uint32_t frame = 0; frame < length; ++frame) {
                const auto e = oracle_curve(1.0, expression, static_cast<std::int32_t>(frame));
                const auto p = oracle_curve(0.75, pedal, static_cast<std::int32_t>(frame));
                const auto u = oracle_curve(0.5, upper, static_cast<std::int32_t>(frame));
                std::vector<Event> events{
                    {0, EventType::BankDrawbar, Manual::Upper, 11, oracle_position(u)},
                    {0, EventType::Expression, Manual::Upper, 0, e},
                    {0, EventType::PedalDrawbar, Manual::Lower, 0, oracle_position(p)}};
                if (frame == 0) {
                    events.push_back({0, EventType::NoteOn, Manual::Upper, 60, 100});
                    events.push_back({0, EventType::NoteOn, Manual::Lower, 48, 100});
                    events.push_back({0, EventType::PedalOn, Manual::Lower, 1, 100});
                }
                if (frame == 35 || frame == 70) events.push_back({0, EventType::NoteOff, Manual::Upper, 60, 0});
                if (frame == 37) events.push_back({0, EventType::NoteOn, Manual::Upper, 60, 100});
                float expected = 0.0F;
                CHECK(reference.process(1, std::span<float>{&expected, 1}, events));
                const auto error = std::abs(static_cast<double>(actual[frame]) - expected);
                counts.maximum_audio_error = std::max(counts.maximum_audio_error, error);
                CHECK(error <= audio_tolerance);
                ++counts.oracle_frames;
            }
            for (std::size_t i = length; i < actual.size(); ++i) CHECK(actual[i] == sentinel);
            phases(timeline->engine(), reference);
            double anchor = 0.0;
            CHECK(timeline->normalized_anchor(0x2000U, anchor));
            const auto expected_anchor = oracle_curve(1.0, expression, length - 1);
            const auto error = std::abs(anchor - expected_anchor);
            counts.maximum_curve_error = std::max(counts.maximum_curve_error, error);
            CHECK(error <= curve_tolerance);
            CHECK(anchor != 0.5); // The future endpoint is not the previous sample.
            CHECK(timeline->engine().key_down(Manual::Lower, 48));
            CHECK(!timeline->engine().pedal_down(PedalId{25}));
            const std::array<HostParameterPoint, 2> fresh{{{0, 0.25}, {0, 0.75}}};
            const std::array<HostParameterQueue, 1> fresh_queue{{{0x2000U, fresh}}};
            const std::array<HostMusicalEvent, 2> fresh_notes{{
                HostNoteEvent{0, HostNoteKind::On, 1, 0, 48, 100, 8},
                PedalNoteEvent{0, PedalNoteKind::Off, 0, 0, PedalId{25}, 0, 6}}};
            (void)accepted(*timeline, 0, {}, fresh_queue, fresh_notes);
            CHECK(timeline->carry_count() == 0);
            CHECK(timeline->engine().expression() == 0.75);
            const std::array<Event, 6> expected{{
                {0, EventType::Expression, Manual::Upper, 0, 0.75},
                {0, EventType::PedalDrawbar, Manual::Lower, 0, 2},
                {0, EventType::NoteOff, Manual::Lower, 48, 0},
                {0, EventType::PedalOn, Manual::Lower, 25, 100},
                {0, EventType::NoteOn, Manual::Lower, 48, 100},
                {0, EventType::PedalOff, Manual::Lower, 25, 0}}};
            CHECK(reference.process(0, {}, expected));
            phases(timeline->engine(), reference);
            std::array<float, 32> left{};
            std::array<float, 32> right{};
            (void)accepted(*timeline, 32, left);
            CHECK(reference.process(32, right, {}));
            exact_audio(left, right);
            phases(timeline->engine(), reference);
        }
    }
}

void test_partitions(const RuntimeProfile& profile) {
    constexpr std::uint32_t length = 1024;
    for (const auto rate : {44100.0, 48000.0, 96000.0}) {
        auto whole = std::make_unique<HostTimeline>();
        CHECK(whole->prepare(profile, {rate, length, 91, 0}) == Status::Ok);
        auto controls = registration();
        controls.expression = 0.0;
        const std::array<HostMusicalEvent, 2> notes{{
            HostNoteEvent{0, HostNoteKind::On, 0, 0, 60, 100, 1},
            PedalNoteEvent{0, PedalNoteKind::On, 0, 0, PedalId{1}, 100, 2}}};
        const std::array<HostParameterPoint, 1> points{{{1023, 1.0}}};
        const std::array<HostParameterQueue, 1> queues{{{0x2000U, points}}};
        std::array<float, length> expected{};
        (void)accepted(*whole, length, expected, queues, notes,
                       std::span<const ControlSnapshot>{&controls, 1});
        for (const auto size : {1U, 7U, 31U, 64U, 127U, 257U, 1024U}) {
            auto split = std::make_unique<HostTimeline>();
            CHECK(split->prepare(profile, {rate, length, 91, 0}) == Status::Ok);
            std::array<float, length> actual{};
            for (std::uint32_t start = 0; start < length;) {
                const auto count = std::min(size, length - start);
                const std::array<HostParameterPoint, 1> part_points{{
                    {static_cast<std::int32_t>(count - 1), static_cast<double>(start + count) / 1024.0}}};
                const std::array<HostParameterQueue, 1> part_queues{{{0x2000U, part_points}}};
                (void)accepted(*split, count, std::span<float>{actual}.subspan(start, count),
                    part_queues, start == 0 ? std::span<const HostMusicalEvent>{notes} : std::span<const HostMusicalEvent>{},
                    start == 0 ? std::span<const ControlSnapshot>{&controls, 1} : std::span<const ControlSnapshot>{});
                start += count;
            }
            exact_audio(actual, expected);
            live_equal(*whole, *split);
            ++counts.partitions;
        }
    }
}

void test_capacity_and_dense_slices(const RuntimeProfile& profile) {
    auto timeline = std::make_unique<HostTimeline>();
    CHECK(timeline->prepare(profile, {48000.0, 65536, 73, 0}) == Status::Ok);
    std::vector<HostMusicalEvent> initial;
    std::vector<Event> physical;
    for (std::uint8_t bus = 0; bus < 2; ++bus) {
        for (std::uint8_t note = 36; note <= 96; ++note) {
            initial.emplace_back(HostNoteEvent{0, HostNoteKind::On, bus, 0, note, 100, -1});
            physical.push_back({0, EventType::NoteOn, static_cast<Manual>(bus), note, 100});
        }
    }
    for (std::uint8_t pedal = 1; pedal <= 25; ++pedal) {
        initial.emplace_back(PedalNoteEvent{0, PedalNoteKind::On, 0, 0, PedalId{pedal}, 100, -1});
        physical.push_back({0, EventType::PedalOn, Manual::Lower, pedal, 100});
    }
    const auto controls = registration();
    (void)accepted(*timeline, 0, {}, {}, initial, std::span<const ControlSnapshot>{&controls, 1});
    Engine reference;
    CHECK(reference.prepare(profile, {48000.0, 65536, 73, 0}) == Status::Ok);
    CHECK(reference.restore_controls(controls));
    CHECK(reference.process(0, {}, physical));
    std::vector<HostMusicalEvent> dense{
        HostNoteEvent{0, HostNoteKind::AllNotesOff, 0, 0, 0, 0, -1},
        HostNoteEvent{0, HostNoteKind::AllNotesOff, 1, 0, 0, 0, -1},
        PedalNoteEvent{0, PedalNoteKind::AllNotesOff, 0, 0, PedalId{0}, 0, -1}};
    const std::array<Event, 3> panics{{
        {0, EventType::AllNotesOff, Manual::Upper, 0, 0},
        {0, EventType::AllNotesOff, Manual::Lower, 0, 0},
        {0, EventType::PedalAllNotesOff, Manual::Lower, 0, 0}}};
    CHECK(reference.process(0, {}, panics));
    for (std::size_t i = 0; i < 1021; ++i) {
        const auto on = i % 2 == 0;
        dense.emplace_back(HostNoteEvent{0, on ? HostNoteKind::On : HostNoteKind::Off,
            0, 0, 60, static_cast<std::uint8_t>(on ? 100 : 0), -1});
        const Event event{0, on ? EventType::NoteOn : EventType::NoteOff, Manual::Upper, 60, on ? 100.0 : 0.0};
        CHECK(reference.process(0, {}, std::span<const Event>{&event, 1}));
    }
    float actual = 0.0F;
    float expected = 0.0F;
    const auto dense_result = accepted(*timeline, 1, std::span<float>{&actual, 1}, {}, dense);
    CHECK(dense_result.physical_events_applied == 1168);
    CHECK(dense_result.engine_calls >= 2 && dense_result.engine_calls <= 4);
    CHECK(reference.process(1, std::span<float>{&expected, 1}, {}));
    exact_audio(std::span<const float>{&actual, 1}, std::span<const float>{&expected, 1});
    phases(timeline->engine(), reference);
    dense.push_back(HostNoteEvent{0, HostNoteKind::Off, 0, 0, 60, 0, -1});
    rejected(*timeline, Status::TooManyEvents, 1, {}, dense);

    auto boundary = std::make_unique<HostTimeline>();
    CHECK(boundary->prepare(profile, {48000.0, 64, 0, 0}) == Status::Ok);
    std::array<HostParameterPoint, 1024> endpoint_points{};
    for (std::size_t i = 0; i < endpoint_points.size(); ++i) {
        endpoint_points[i] = {4, static_cast<double>(i % 9) / 8.0};
    }
    const std::array<HostParameterQueue, 1> endpoint_queue{{{0x4000U, endpoint_points}}};
    (void)accepted(*boundary, 4, {}, endpoint_queue);
    CHECK(boundary->carry_count() == 1024);
    const std::array<HostMusicalEvent, 1> extra{{HostNoteEvent{0, HostNoteKind::On, 0, 0, 60, 100, -1}}};
    auto saved = std::make_unique<HostTimeline>(*boundary);
    std::array<float, 4> sentinel_output{};
    sentinel_output.fill(sentinel);
    const auto overflow = boundary->process(4, sentinel_output, {}, extra);
    CHECK(overflow.status == Status::TooManyEvents && overflow.input_records_consumed == 0);
    CHECK(std::all_of(sentinel_output.begin(), sentinel_output.end(), [](float v) { return v == sentinel; }));
    live_equal(*boundary, *saved);
    ++counts.rejections;
    const auto consumed = accepted(*boundary, 0, {});
    CHECK(consumed.carried_records_consumed == 1024 && consumed.physical_events_applied == 1);
    CHECK(boundary->carry_count() == 0);
    std::uint8_t position = 0;
    CHECK(boundary->engine().pedal_drawbar_position(0, position));
    CHECK(position == 1023 % 9);
    (void)accepted(*boundary, 4, sentinel_output, {}, extra);

    auto owners = std::make_unique<HostTimeline>();
    CHECK(owners->prepare(profile, {48000.0, 64, 0, 0}) == Status::Ok);
    std::vector<HostMusicalEvent> all_owners;
    for (std::size_t i = 0; i < 256; ++i) {
        all_owners.emplace_back(HostNoteEvent{0, HostNoteKind::On, 0, 0, 60, 100, -1});
        all_owners.emplace_back(PedalNoteEvent{0, PedalNoteKind::On, 0, 0, PedalId{1}, 100, -1});
    }
    (void)accepted(*owners, 0, {}, {}, all_owners);
    CHECK(owners->manual_ownership().owner_count() == 256);
    CHECK(owners->pedal_ownership().owner_count() == 256);
    rejected(*owners, Status::TooManyEvents, 16, {}, extra);
    const std::array<HostMusicalEvent, 1> extra_pedal{{
        PedalNoteEvent{16, PedalNoteKind::On, 0, 0, PedalId{1}, 100, -1}}};
    rejected(*owners, Status::TooManyEvents, 16, {}, extra_pedal);
}

void test_maximum_and_disconnected(const RuntimeProfile& profile) {
    auto connected = std::make_unique<HostTimeline>();
    auto disconnected = std::make_unique<HostTimeline>();
    const auto model = make_nominal_console_model();
    CHECK(connected->prepare(profile, {96000.0, 65536, 17, 0}, model) == Status::Ok);
    CHECK(disconnected->prepare(profile, {96000.0, 65536, 17, 0}, model) == Status::Ok);
    auto controls = registration();
    controls.expression = 0.0;
    const std::array<HostParameterPoint, 1> expression{{{65535, 1.0}}};
    const std::array<HostParameterPoint, 1> pedal{{{65536, 0.0}}};
    const std::array<HostParameterQueue, 2> queues{{{0x2000U, expression}, {0x4000U, pedal}}};
    const std::array<HostMusicalEvent, 2> notes{{
        HostNoteEvent{0, HostNoteKind::On, 0, 0, 60, 100, 1},
        PedalNoteEvent{0, PedalNoteKind::On, 0, 0, PedalId{1}, 100, 2}}};
    std::vector<float> output(65537, sentinel);
    const auto result = accepted(*connected, 65536, output, queues, notes,
                                  std::span<const ControlSnapshot>{&controls, 1});
    (void)accepted(*disconnected, 65536, {}, queues, notes,
                   std::span<const ControlSnapshot>{&controls, 1});
    CHECK(result.engine_calls > 1 && result.engine_calls < 200);
    CHECK(result.physical_events_applied >= 65536);
    CHECK(output.back() == sentinel);
    CHECK(std::all_of(output.begin(), output.end() - 1, [](float v) { return std::isfinite(v); }));
    CHECK(std::any_of(output.begin(), output.end() - 1, [](float v) { return v != 0.0F; }));
    live_equal(*connected, *disconnected);
    CHECK(connected->carry_count() == 1);
    std::array<float, 64> left{};
    std::array<float, 64> right{};
    (void)accepted(*connected, 64, left);
    (void)accepted(*disconnected, 64, right);
    exact_audio(left, right);
    live_equal(*connected, *disconnected);
}

void test_restores_lifecycle_and_routes(const RuntimeProfile& profile) {
    auto timeline = std::make_unique<HostTimeline>();
    CHECK(timeline->prepare(profile, {48000.0, 16, 28, 91}, make_nominal_console_model()) == Status::Ok);
    auto controls = registration();
    const std::array<HostMusicalEvent, 2> held{{
        HostNoteEvent{0, HostNoteKind::On, 0, 0, 60, 100, 1},
        PedalNoteEvent{0, PedalNoteKind::On, 0, 0, PedalId{1}, 100, 2}}};
    (void)accepted(*timeline, 16, {}, {}, held, std::span<const ControlSnapshot>{&controls, 1});
    const auto old = std::make_unique<HostTimeline>(*timeline);
    std::array<ControlSnapshot, 4> restores{controls, controls, controls, controls};
    restores[0].expression = 0.5;
    restores[1].pedal_drawbars = {1, 2};
    restores[2].selected_banks = {DrawbarBank::A, DrawbarBank::A};
    restores[3].expression = -0.0;
    restores[3].route_enabled = {false, false};
    restores[3].pedal_drawbars = {3, 7};
    (void)accepted(*timeline, 0, {}, {}, {}, restores);
    CHECK(timeline->engine().controls_snapshot() == restores[3]);
    CHECK(std::signbit(timeline->engine().expression()));
    CHECK(timeline->manual_ownership() == old->manual_ownership());
    CHECK(timeline->pedal_ownership() == old->pedal_ownership());
    CHECK(timeline->engine().percussion_diagnostics().readiness == old->engine().percussion_diagnostics().readiness);
    CHECK(timeline->engine().last_pedal_frame() == old->engine().last_pedal_frame());
    phases(timeline->engine(), old->engine());
    double anchor = 0.0;
    CHECK(timeline->normalized_anchor(0x2000U, anchor) && std::signbit(anchor));
    CHECK(timeline->normalized_anchor(0x4000U, anchor) && anchor == 3.0 / 8.0);
    (void)accepted(*timeline, 1, {});
    CHECK(!timeline->engine().controls_snapshot().route_enabled[0]);
    const std::array<HostParameterPoint, 1> selector{{{0, 1.0}}};
    const std::array<HostParameterQueue, 1> selected{{{0x2010U, selector}}};
    (void)accepted(*timeline, 0, {}, selected);
    CHECK(timeline->engine().controls_snapshot().route_enabled[0]);
    CHECK(!timeline->engine().controls_snapshot().route_enabled[1]);

    CHECK(timeline->set_manual_bus_route(0, Manual::Lower));
    const std::array<HostMusicalEvent, 1> routed{{HostNoteEvent{0, HostNoteKind::On, 0, 0, 60, 100, 3}}};
    (void)accepted(*timeline, 0, {}, {}, routed);
    CHECK(timeline->engine().key_down(Manual::Upper, 60) && timeline->engine().key_down(Manual::Lower, 60));
    const std::array<HostMusicalEvent, 1> release{{HostNoteEvent{0, HostNoteKind::Off, 0, 0, 60, 0, 1}}};
    (void)accepted(*timeline, 0, {}, {}, release);
    CHECK(!timeline->engine().key_down(Manual::Upper, 60) && timeline->engine().key_down(Manual::Lower, 60));
    const std::array<HostParameterPoint, 1> endpoint{{{8, 0.5}}};
    const std::array<HostParameterQueue, 1> endpoint_queue{{{0x2000U, endpoint}}};
    (void)accepted(*timeline, 8, {}, endpoint_queue);
    auto before_rate = std::make_unique<HostTimeline>(*timeline);
    CHECK(timeline->reconfigure(96000.0, 64) == Status::Ok);
    phases(timeline->engine(), before_rate->engine());
    CHECK(timeline->engine().frame_clock() == before_rate->engine().frame_clock());
    CHECK(timeline->engine().last_pedal_frame() == before_rate->engine().last_pedal_frame());
    CHECK(timeline->carry_count() == 1);
    double changed_anchor = 0.0;
    CHECK(timeline->normalized_anchor(0x2000U, changed_anchor));
    CHECK(before_rate->normalized_anchor(0x2000U, anchor) && bits(anchor, changed_anchor));
    auto valid = std::make_unique<HostTimeline>(*timeline);
    CHECK(timeline->reconfigure(88200.0, 32) == Status::InvalidSpec);
    CHECK(timeline->reconfigure(44100.0, 0) == Status::InvalidSpec);
    live_equal(*timeline, *valid);
    (void)accepted(*timeline, 64, {});
    CHECK(timeline->engine().last_pedal_frame().sample_rate == 96000.0);
    CHECK(timeline->engine().expression() == 0.5);
    auto bad_profile = profile;
    bad_profile.output_gain = std::numeric_limits<double>::quiet_NaN();
    valid = std::make_unique<HostTimeline>(*timeline);
    CHECK(timeline->prepare(bad_profile, {44100.0, 8, 0, 0}) == Status::InvalidProfile);
    CHECK(timeline->prepare(profile, {44100.0, 0, 0, 0}) == Status::InvalidSpec);
    live_equal(*timeline, *valid);
    CHECK(timeline->prepare(profile, {44100.0, 8, 2, 13}) == Status::Ok);
    CHECK(timeline->engine().frame_clock() == 13 && timeline->carry_count() == 0);
    CHECK(timeline->manual_ownership().owner_count() == 0 && timeline->pedal_ownership().owner_count() == 0);
    CHECK(timeline->engine().active_key_count() == 0 && timeline->engine().active_pedal_count() == 0);
    CHECK(timeline->normalized_anchor(0x2000U, anchor) && anchor == 1.0);
    CHECK(!timeline->engine().last_pedal_frame().valid);
}

void test_atomic_failures(const RuntimeProfile& profile) {
    auto timeline = std::make_unique<HostTimeline>();
    rejected(*timeline, Status::NotPrepared, 16);
    CHECK(timeline->prepare(profile, {48000.0, 64, 31, 0}, make_nominal_console_model()) == Status::Ok);
    const auto controls = registration();
    const std::array<HostMusicalEvent, 2> held{{
        HostNoteEvent{0, HostNoteKind::On, 0, 0, 60, 100, 1},
        PedalNoteEvent{0, PedalNoteKind::On, 0, 0, PedalId{1}, 100, 2}}};
    (void)accepted(*timeline, 8, {}, {}, held, std::span<const ControlSnapshot>{&controls, 1});
    rejected(*timeline, Status::BlockTooLarge, 65);
    rejected(*timeline, Status::InvalidBuffer, 16, {}, {}, {}, true);
    std::array<HostParameterPoint, 2> points{{{0, 0.5}, {15, 1.0}}};
    std::array<HostParameterQueue, 1> queues{{{0x2000U, points}}};
    for (const auto invalid : {-1.0, 1.01, std::numeric_limits<double>::quiet_NaN(),
                               std::numeric_limits<double>::infinity()}) {
        points[1].normalized = invalid;
        rejected(*timeline, Status::InvalidEvent, 16, queues);
    }
    points[1] = {-1, 1.0};
    rejected(*timeline, Status::InvalidEvent, 16, queues);
    points[1] = {17, 1.0};
    rejected(*timeline, Status::InvalidEvent, 16, queues);
    points = {{{10, 0.5}, {9, 1.0}}};
    rejected(*timeline, Status::InvalidEvent, 16, queues);
    points = {{{0, 0.5}, {15, 1.0}}};
    queues[0].parameter_id = 0x2001U;
    rejected(*timeline, Status::InvalidEvent, 16, queues);
    queues[0].parameter_id = 0x2000U;
    const std::array<HostParameterQueue, 2> duplicate{{queues[0], {0x2000U, {}}}};
    rejected(*timeline, Status::InvalidEvent, 16, duplicate);
    const std::array<HostParameterQueue, 2> duplicate_empty{{{0x2000U, {}}, {0x2000U, {}}}};
    rejected(*timeline, Status::InvalidEvent, 16, duplicate_empty);
    std::array<HostParameterQueue, 46> excessive_queues{};
    rejected(*timeline, Status::TooManyEvents, 16, excessive_queues);
    std::array<HostParameterPoint, 1025> excessive_points{};
    const std::array<HostParameterQueue, 1> excessive{{{0x2000U, excessive_points}}};
    rejected(*timeline, Status::TooManyEvents, 16, excessive);
    std::array<ControlSnapshot, 5> restores{};
    rejected(*timeline, Status::TooManyEvents, 16, {}, {}, restores);
    restores[1].pedal_drawbars[0] = 9;
    rejected(*timeline, Status::InvalidEvent, 16, {}, {}, std::span<const ControlSnapshot>{restores}.first(2));
    restores[1] = {};
    restores[1].expression = std::numeric_limits<double>::quiet_NaN();
    rejected(*timeline, Status::InvalidEvent, 16, {}, {}, std::span<const ControlSnapshot>{restores}.first(2));

    const std::array<HostNoteEvent, 9> invalid_manual{{
        {15, HostNoteKind::On, 2, 0, 60, 100, 3},
        {15, HostNoteKind::On, 0, 16, 60, 100, 3},
        {15, HostNoteKind::On, 0, 0, 35, 100, 3},
        {15, HostNoteKind::On, 0, 0, 60, 128, 3},
        {15, HostNoteKind::On, 0, 0, 60, 100, -2},
        {15, HostNoteKind::On, 0, 0, 61, 100, 1},
        {15, static_cast<HostNoteKind>(3), 0, 0, 60, 100, 3},
        {17, HostNoteKind::On, 0, 0, 60, 100, 3},
        {std::numeric_limits<std::uint32_t>::max(), HostNoteKind::On, 0, 0, 60, 100, 3}}};
    for (const auto note : invalid_manual) {
        const std::array<HostMusicalEvent, 2> music{{
            PedalNoteEvent{0, PedalNoteKind::On, 0, 0, PedalId{25}, 100, 9}, note}};
        rejected(*timeline, Status::InvalidEvent, 16, queues, music);
    }
    const std::array<PedalNoteEvent, 7> invalid_pedal{{
        {15, PedalNoteKind::On, 2, 0, PedalId{1}, 100, 3},
        {15, PedalNoteKind::On, 0, 16, PedalId{1}, 100, 3},
        {15, PedalNoteKind::On, 0, 0, PedalId{0}, 100, 3},
        {15, PedalNoteKind::On, 0, 0, PedalId{26}, 100, 3},
        {15, PedalNoteKind::On, 0, 0, PedalId{1}, 128, 3},
        {15, PedalNoteKind::On, 0, 0, PedalId{2}, 100, 2},
        {15, PedalNoteKind::Off, 0, 0, PedalId{1}, 1, 2}}};
    for (const auto note : invalid_pedal) {
        const std::array<HostMusicalEvent, 2> music{{
            HostNoteEvent{0, HostNoteKind::On, 0, 1, 70, 100, 11}, note}};
        rejected(*timeline, Status::InvalidEvent, 16, queues, music);
    }
    const std::array<HostMusicalEvent, 2> unsorted{{
        HostNoteEvent{1, HostNoteKind::On, 0, 1, 70, 100, 11},
        PedalNoteEvent{0, PedalNoteKind::On, 0, 1, PedalId{2}, 100, 12}}};
    rejected(*timeline, Status::InvalidEvent, 16, {}, unsorted);
    points = {{{0, 0.5}, {1, 1.0}}};
    rejected(*timeline, Status::InvalidEvent, 0, queues);
    const std::array<HostMusicalEvent, 1> future_invalid{{
        HostNoteEvent{16, HostNoteKind::On, 0, 0, 61, 100, 1}}};
    rejected(*timeline, Status::InvalidEvent, 16, {}, future_invalid);

    auto clock = std::make_unique<HostTimeline>();
    CHECK(clock->prepare(profile, {48000.0, 64, 0,
        std::numeric_limits<std::uint64_t>::max() - 1}) == Status::Ok);
    rejected(*clock, Status::TimelineOverflow, 2);
    (void)accepted(*clock, 1, {});
    rejected(*clock, Status::TimelineOverflow, 1);
    (void)accepted(*clock, 0, {});
}

} // namespace

int main() {
    const auto profile = load_test_profile();
    test_all_ids_and_thresholds(profile);
    test_interpolation_and_boundary(profile);
    test_partitions(profile);
    test_capacity_and_dense_slices(profile);
    test_maximum_and_disconnected(profile);
    test_restores_lifecycle_and_routes(profile);
    test_atomic_failures(profile);
    std::cout << "host timeline: accepted=" << counts.calls << ", oracle_frames=" << counts.oracle_frames
              << ", phase_values=" << counts.phase_values << ", exact_samples=" << counts.exact_samples
              << ", rejections=" << counts.rejections << ", future_probes=" << counts.future_probes
              << ", threshold_cases=" << counts.threshold_cases << ", partitions=" << counts.partitions
              << ", max_audio_error=" << std::setprecision(17) << counts.maximum_audio_error
              << ", max_curve_error=" << counts.maximum_curve_error
              << ", sizeof(HostTimeline)=" << sizeof(HostTimeline) << '\n';
}
