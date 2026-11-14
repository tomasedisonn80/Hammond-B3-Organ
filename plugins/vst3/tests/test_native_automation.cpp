#include "NativeHarness.h"
#include "NativePresetOracle.h"

#include "hammond/ConsoleModel.h"
#include "hammond/Engine.h"
#include "hammond/Profile.h"

#include <algorithm>
#include <array>
#include <bit>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <span>
#include <string>
#include <string_view>
#include <vector>

namespace {

using namespace hammond;
using namespace hammond::native_test;
using Steinberg::int16;
using Steinberg::int32;
constexpr float kSentinel = -93.25F;
constexpr std::uint32_t kScoreFrames = 4096;
constexpr int kUnit = 8192;
using LegacyValues = std::array<int, 45>;

// Permanent native identities written independently of the compiled registry.
// Array positions below describe physical targets, not descriptor enumeration.
constexpr std::array<std::uint32_t, 45> kLegacyIds{{
    0x1000, 0x1001, 0x1002, 0x1003, 0x1004, 0x1005, 0x1006, 0x1007, 0x1008,
    0x1010, 0x1011, 0x1012, 0x1013, 0x1014, 0x1015, 0x1016, 0x1017, 0x1018,
    0x1020, 0x1021, 0x1022, 0x1023, 0x1024, 0x1025, 0x1026, 0x1027, 0x1028,
    0x1030, 0x1031, 0x1032, 0x1033, 0x1034, 0x1035, 0x1036, 0x1037, 0x1038,
    0x2000, 0x2010, 0x2011, 0x3000, 0x3001, 0x3002, 0x3003, 0x4000, 0x4001}};
static_assert(kLegacyIds.size() == 45);
static_assert(kScoreFrames > 1024);

struct Statistics {
    std::uint64_t callbacks{0};
    std::uint64_t zero_callbacks{0};
    std::uint64_t state_reads{0};
    std::uint64_t reference_frames{0};
    std::uint64_t channel_samples{0};
    std::uint64_t partition_samples{0};
    std::uint64_t future_channel_samples{0};
    std::uint64_t nonzero_channel_samples{0};
    std::uint64_t long_callbacks{0};
    std::uint64_t guaranteed_expression_events{0};
    std::uint64_t legacy45_score_cases{0};
    std::uint64_t restore_cases{0};
    std::uint64_t gap_cases{0};
    std::uint64_t isolated_windows{0};
    std::uint64_t preset_commands{0};
    std::uint64_t preset_thresholds{0};
    std::uint64_t preset_alias_cases{0};
    std::uint64_t preset_restore_cases{0};
    std::uint64_t preset_partition_cases{0};
    std::uint64_t checksum{1469598103934665603ULL};
    std::array<double, 3> division_min_rms{{1.0, 1.0, 1.0}};
    double maximum_error{0.0};
    double maximum_peak{0.0};
    double reconnect_difference{0.0};
} stats;

double normalized(int units) {
    require(units >= 0 && units <= kUnit, "oracle normalized units out of range");
    return static_cast<double>(units) / static_cast<double>(kUnit);
}

Event physical_control(std::size_t index, int units) {
    // Integer half-up arithmetic at exact 1/16 drawbar / 1/2 switch thresholds.
    const auto bar = static_cast<double>((units + 512) / 1024);
    const double selected = units >= 4096 ? 1.0 : 0.0;
    if (index < 36) {
        return {0, EventType::BankDrawbar, index < 18 ? Manual::Upper : Manual::Lower,
                static_cast<std::uint8_t>(index % 18), bar};
    }
    if (index == 36) return {0, EventType::Expression, Manual::Upper, 0, normalized(units)};
    if (index == 37 || index == 38) {
        return {0, EventType::SelectBank, index == 37 ? Manual::Upper : Manual::Lower,
                0, selected};
    }
    if (index >= 39 && index < 43) {
        return {0, EventType::Percussion, Manual::Upper,
                static_cast<std::uint8_t>(index - 39), selected};
    }
    if (index == 43 || index == 44) {
        return {0, EventType::PedalDrawbar, Manual::Lower,
                static_cast<std::uint8_t>(index - 43), bar};
    }
    require(index == 45 || index == 46, "unknown independent physical control index");
    return {0, EventType::SelectPreset, index == 45 ? Manual::Upper : Manual::Lower,
            0, static_cast<double>(preset_oracle::plain(normalized(units)))};
}

ControlSnapshot controls_from(const LegacyValues& values) {
    ControlSnapshot controls;
    for (std::size_t index = 0; index < 36; ++index) {
        controls.drawbars[index / 18][(index % 18) / 9][index % 9] =
            static_cast<std::uint8_t>((values[index] + 512) / 1024);
    }
    controls.expression = normalized(values[36]);
    controls.selected_banks = {values[37] >= 4096 ? DrawbarBank::B : DrawbarBank::A,
                              values[38] >= 4096 ? DrawbarBank::B : DrawbarBank::A};
    controls.percussion = {values[39] >= 4096,
        values[40] >= 4096 ? PercussionHarmonic::Third : PercussionHarmonic::Second,
        values[41] >= 4096 ? PercussionVolume::Soft : PercussionVolume::Normal,
        values[42] >= 4096 ? PercussionDecay::Fast : PercussionDecay::Slow};
    controls.pedal_drawbars = {static_cast<std::uint8_t>((values[43] + 512) / 1024),
                               static_cast<std::uint8_t>((values[44] + 512) / 1024)};
    return controls;
}

std::vector<Event> controls_at(const LegacyValues& values, bool lower_selector = true) {
    std::vector<Event> events;
    events.reserve(56);
    for (std::size_t index = 0; index < values.size(); ++index) {
        if (index != 38 || lower_selector) events.push_back(physical_control(index, values[index]));
    }
    return events;
}

Event key(Manual manual, std::uint8_t pitch, bool on, std::uint32_t offset = 0) {
    return {offset, on ? EventType::NoteOn : EventType::NoteOff, manual, pitch, on ? 127.0 : 0.0};
}

Event pedal(std::uint8_t id, bool on, std::uint32_t offset = 0) {
    return {offset, on ? EventType::PedalOn : EventType::PedalOff,
            Manual::Lower, id, on ? 127.0 : 0.0};
}

void append(std::vector<Event>& destination, std::span<const Event> source) {
    destination.insert(destination.end(), source.begin(), source.end());
}

class Session {
public:
    NativePlugin plugin;
    Engine reference;
    StereoBlock block{8196};
    std::string label;

    Session(const std::string& bundle, const RuntimeProfile& profile, double rate,
            const ControlSnapshot& initial, std::string_view scenario)
        : plugin(bundle), label(std::string(scenario) + " rate=" + std::to_string(rate)) {
        plugin.start(rate, 8192);
        require(reference.prepare(profile, {rate, 8192, 0, 0}, make_nominal_console_model()) ==
                Status::Ok, "direct Engine preparation failed");
        require(plugin.load_state(snapshot_text(initial)) == Steinberg::kResultOk,
                "initial native state load failed");
        require(reference.restore_controls(initial), "initial direct restore failed");
    }

    void native(std::uint32_t frames, ParameterChanges* parameters, EventList* notes) {
        block.set_frames(static_cast<int32>(frames));
        block.fill(kSentinel);
        block.bus.silenceFlags = 0xA5U;
        block.data.inputParameterChanges = parameters;
        block.data.inputEvents = notes;
        const auto result = plugin.processor->process(block.data);
        require(result == Steinberg::kResultOk,
                label + ": native process result=" + std::to_string(result));
        ++stats.callbacks;
        if (frames == 0) ++stats.zero_callbacks;
    }

    std::vector<float> render(std::uint32_t frames, std::span<const Event> events = {}) {
        std::vector<float> output(frames);
        const auto before = reference.frame_clock();
        const auto result = reference.process(frames, output, events);
        require(result.ok() && result.events_consumed == events.size(), "direct oracle rejected");
        require(reference.frame_clock() == before + frames, "direct oracle elapsed-frame sum changed");
        stats.reference_frames += frames;
        return output;
    }

    ControlSnapshot saved() {
        std::string text;
        require(plugin.save_state(text) == Steinberg::kResultOk, "native state save failed");
        ++stats.state_reads;
        return parse_snapshot(text);
    }

    void compare(std::span<const float> expected, bool future = false) {
        bool silent = true;
        for (std::size_t i = 0; i < expected.size(); ++i) {
            silent = silent && expected[i] == 0.0F;
            for (const auto* samples : {block.left.data(), block.right.data()}) {
                const float actual = samples[i];
                require(std::isfinite(actual) && std::isfinite(expected[i]), "nonfinite native audio");
                stats.maximum_error = std::max(stats.maximum_error,
                    std::abs(static_cast<double>(actual) - static_cast<double>(expected[i])));
                require(std::bit_cast<std::uint32_t>(actual) == std::bit_cast<std::uint32_t>(expected[i]),
                        label + ": audio differs at callback sample " + std::to_string(i));
                stats.maximum_peak = std::max(stats.maximum_peak, std::abs(static_cast<double>(actual)));
                ++stats.channel_samples;
                if (future) ++stats.future_channel_samples;
                if (actual != 0.0F) ++stats.nonzero_channel_samples;
                stats.checksum ^= std::bit_cast<std::uint32_t>(actual);
                stats.checksum *= 1099511628211ULL;
            }
        }
        require(block.bus.silenceFlags == (silent ? 3U : 0U), "native silence flags disagree");
        require(std::all_of(block.left.begin() + static_cast<std::ptrdiff_t>(expected.size()),
                            block.left.end(), [](float sample) { return sample == kSentinel; }) &&
                std::all_of(block.right.begin() + static_cast<std::ptrdiff_t>(expected.size()),
                            block.right.end(), [](float sample) { return sample == kSentinel; }),
                "native callback wrote beyond its frame range");
        const auto actual = saved();
        const auto wanted = reference.controls_snapshot();
        require(actual == wanted, label + ": complete saved controls differ");
        require(std::bit_cast<std::uint64_t>(actual.expression) ==
                std::bit_cast<std::uint64_t>(wanted.expression), "saved expression bits differ");
    }

    std::vector<float> process(std::uint32_t frames, std::span<const Event> events = {},
                              ParameterChanges* parameters = nullptr, EventList* notes = nullptr,
                              bool future = false) {
        native(frames, parameters, notes);
        auto expected = render(frames, events);
        compare(expected, future);
        return expected;
    }
};

// q[-1]=0. The four 1024-sample legs rise, fall, rise, fall. All values
// are exact multiples of 1/8192, including endpoints at arbitrary partitions.
LegacyValues score_values(std::uint32_t sample_plus_one) {
    const auto cycle = sample_plus_one % 2048U;
    const int tick = static_cast<int>(cycle <= 1024U ? cycle : 2048U - cycle);
    constexpr std::array<unsigned, 4> patterns{{0b101010101U, 0b001110001U,
                                               0b011001100U, 0b110100010U}};
    LegacyValues result{};
    for (std::size_t i = 0; i < 36; ++i) {
        const bool rising = ((patterns[i / 9] >> (i % 9)) & 1U) != 0;
        result[i] = 8 * (rising ? tick : 1024 - tick);
    }
    result[36] = 1024 + tick; // expression = 1/8 + q/8
    for (const auto index : {37U, 39U, 41U, 43U}) result[index] = 8 * tick;
    for (const auto index : {38U, 40U, 42U, 44U}) result[index] = 8192 - 8 * tick;
    return result;
}

void audible_prelude(Session& session) {
    for (int32 division = 0; division < 3; ++division) {
        const int16 pitch = division == 0 ? 60 : division == 1 ? 43 : 36;
        EventList notes;
        notes.events = {note_on(division, pitch, 0, 0, 10 + division),
                        note_off(division, pitch, 1024, 0, 10 + division)};
        const Event on = division == 2 ? pedal(1, true) :
            key(division == 0 ? Manual::Upper : Manual::Lower, static_cast<std::uint8_t>(pitch), true);
        const Event off = division == 2 ? pedal(1, false, 1024) :
            key(division == 0 ? Manual::Upper : Manual::Lower, static_cast<std::uint8_t>(pitch), false, 1024);
        const std::array<Event, 2> physical{{on, off}};
        const auto output = session.process(2048, physical, nullptr, &notes);
        double energy = 0.0;
        std::size_t nonzero = 0;
        for (std::size_t i = 0; i < 1024; ++i) {
            energy += static_cast<double>(output[i]) * output[i];
            if (output[i] != 0.0F) ++nonzero;
        }
        const double rms = std::sqrt(energy / 1024.0);
        require(rms > 0.00001 && nonzero > 400, "score registration failed isolated audibility");
        auto& minimum = stats.division_min_rms[static_cast<std::size_t>(division)];
        minimum = std::min(minimum, rms);
        ++stats.isolated_windows;
    }
    require(session.reference.active_key_count() == 0 && session.reference.active_pedal_count() == 0,
            "isolated prelude did not release every physical target");
    EventList notes;
    notes.events = {note_on(0, 60, 0, 0, 1), note_on(1, 43, 0, 1, 2), note_on(2, 36, 0, 2, 3)};
    const std::array<Event, 3> physical{{key(Manual::Upper, 60, true),
        key(Manual::Lower, 43, true), pedal(1, true)}};
    (void)session.process(1024, physical, nullptr, &notes);
}

struct ScoreNote {
    std::uint32_t frame;
    sv::Event native;
    Event physical;
};

std::vector<ScoreNote> score_notes() {
    // Literal musical correspondence, including independently written pedal IDs.
    return {{0, note_on(0, 72, 0, 0, 4), key(Manual::Upper, 72, true)},
        {511, note_off(0, 60, 0, 0, 1), key(Manual::Upper, 60, false)},
        {511, note_on(0, 67, 0, 0, 5), key(Manual::Upper, 67, true)},
        {1024, note_off(1, 43, 0, 1, 2), key(Manual::Lower, 43, false)},
        {1024, note_on(1, 55, 0, 1, 6), key(Manual::Lower, 55, true)},
        {1024, note_off(2, 36, 0, 2, 3), pedal(1, false)},
        {1024, note_on(2, 48, 0, 2, 7), pedal(13, true)},
        {2047, note_off(0, 72, 0, 0, 4), key(Manual::Upper, 72, false)},
        {2047, note_on(0, 76, 0, 0, 8), key(Manual::Upper, 76, true)},
        {3072, note_off(0, 67, 0, 0, 5), key(Manual::Upper, 67, false)},
        {3072, note_on(0, 79, 0, 0, 9), key(Manual::Upper, 79, true)},
        {4096, note_on(0, 96, 0, 0, 10), key(Manual::Upper, 96, true)},
        {4096, note_off(2, 48, 0, 2, 7), pedal(13, false)},
        {4096, note_on(2, 52, 0, 2, 11), pedal(17, true)}};
}

std::vector<std::uint32_t> irregular_partition() {
    // Before/on/after every rising drawbar threshold, plus Boolean and turning
    // points. The other long intervals cross arbitrary musical boundaries.
    std::vector<std::uint32_t> cuts{1, 7, 128, 255, 511, 512, 513, 1023, 1024, 1025,
        1535, 1536, 1537, 2047, 2048, 2049, 3071, 3072, 3073, 4095, 4096};
    for (std::uint32_t threshold = 64; threshold < 1024; threshold += 128) {
        cuts.insert(cuts.end(), {threshold - 1, threshold, threshold + 1});
    }
    std::sort(cuts.begin(), cuts.end());
    cuts.erase(std::unique(cuts.begin(), cuts.end()), cuts.end());
    std::vector<std::uint32_t> lengths;
    std::uint32_t prior = 0;
    for (const auto cut : cuts) { lengths.push_back(cut - prior); prior = cut; }
    return lengths;
}

void retained_gap(Session& session, std::vector<float>& joined) {
    // Start at q=1/1024, installed by the preceding consumed boundary. End
    // at q=17/1024 on sample 15 (not N), leaving no parameter carry. Retain
    // this noncanonical normalized anchor through absent AND empty queues.
    ParameterChanges first;
    for (std::size_t i = 0; i < kLegacyIds.size(); ++i) {
        first.add_queue(kLegacyIds[i]).points = {{15, normalized(score_values(4113)[i])}};
    }
    session.native(16, &first, nullptr);
    std::vector<float> expected;
    for (std::uint32_t i = 0; i < 16; ++i) {
        expected.push_back(session.render(1, controls_at(score_values(4098 + i)))[0]);
    }
    session.compare(expected);
    joined.insert(joined.end(), expected.begin(), expected.end());
    const auto absent = session.process(13);
    joined.insert(joined.end(), absent.begin(), absent.end());
    ParameterChanges empty;
    for (auto it = kLegacyIds.rbegin(); it != kLegacyIds.rend(); ++it) (void)empty.add_queue(*it);
    const auto empty_output = session.process(7, {}, &empty);
    joined.insert(joined.end(), empty_output.begin(), empty_output.end());

    // q[i] = (17 + 25*(i+1))/1024, i=0..31. Restoring an anchor from the
    // rounded drawbar/switch value would move thresholds by actual samples.
    ParameterChanges resumed;
    for (std::size_t i = 0; i < kLegacyIds.size(); ++i) {
        resumed.add_queue(kLegacyIds[i]).points = {{31, normalized(score_values(4913)[i])}};
    }
    session.native(32, &resumed, nullptr);
    expected.clear();
    for (std::uint32_t i = 0; i < 32; ++i) {
        const auto tick = 17 + 25 * (i + 1);
        expected.push_back(session.render(1, controls_at(score_values(4096 + tick)))[0]);
    }
    session.compare(expected);
    joined.insert(joined.end(), expected.begin(), expected.end());
    const auto future = session.process(257, {}, nullptr, nullptr, true);
    require(std::count_if(future.begin(), future.end(), [](float x) { return x != 0.0F; }) > 240,
            "gap continuation was vacuous silence");
    joined.insert(joined.end(), future.begin(), future.end());
    ++stats.gap_cases;
}

std::vector<float> legacy45_curves(const std::string& bundle, const RuntimeProfile& profile,
                              double rate, const std::vector<std::uint32_t>& partition) {
    Session session(bundle, profile, rate, controls_from(score_values(0)), "all 45 curves");
    audible_prelude(session);
    const auto before = session.reference.frame_clock();
    const auto notes = score_notes();
    std::vector<float> joined;
    std::uint32_t start = 0;
    for (const auto count : partition) {
        const auto end = start + count;
        ParameterChanges parameters;
        for (std::size_t j = 0; j < kLegacyIds.size(); ++j) {
            const auto i = (17 * j + start) % kLegacyIds.size(); // Queue enumeration is not ID order.
            auto& queue = parameters.add_queue(kLegacyIds[i]);
            for (const std::uint32_t knot : {1023U, 2047U, 3071U, 4095U}) {
                if (knot >= start && knot < end) {
                    queue.points.push_back({static_cast<int32>(knot - start),
                                            normalized(score_values(knot + 1)[i])});
                }
            }
            queue.points.push_back({static_cast<int32>(count), normalized(score_values(end + 1)[i])});
        }
        require(parameters.queues.size() == 45, "score omitted a native parameter queue");
        EventList events;
        for (const auto& note : notes) {
            if (note.frame <= end && (note.frame > start || (start == 0 && note.frame == 0))) {
                auto copy = note.native;
                copy.sampleOffset = static_cast<int32>(note.frame - start);
                events.events.push_back(copy);
            }
        }
        session.native(count, &parameters, &events);
        std::vector<float> expected;
        expected.reserve(count);
        std::uint32_t expression_changes = 0;
        auto previous = score_values(start)[36];
        for (std::uint32_t i = 0; i < count; ++i) {
            const auto values = score_values(start + i + 1);
            if (values[36] != previous) ++expression_changes;
            previous = values[36];
            auto physical = controls_at(values);
            for (const auto& note : notes) {
                if (note.frame == start + i) physical.push_back(note.physical);
            }
            expected.push_back(session.render(1, physical)[0]);
        }
        if (count == kScoreFrames) {
            require(expression_changes == kScoreFrames && expression_changes > 1024,
                    "workload did not force emitted-event slicing");
            ++stats.long_callbacks;
            stats.guaranteed_expression_events += expression_changes;
        }
        session.compare(expected);
        joined.insert(joined.end(), expected.begin(), expected.end());
        start = end;
    }
    require(start == kScoreFrames && session.reference.frame_clock() == before + kScoreFrames,
            "score partitions did not cover the exact elapsed interval");
    require(session.saved().expression == 0.125, "offset-N endpoint replaced last actual sample");
    auto boundary = controls_at(score_values(4097));
    for (const auto& note : notes) if (note.frame == 4096) boundary.push_back(note.physical);
    (void)session.process(0, boundary);
    (void)session.process(0); // No endpoint/note replay and no elapsed frame.
    require(session.reference.frame_clock() == before + kScoreFrames, "zero boundary advanced reference time");
    const auto future = session.process(2048, {}, nullptr, nullptr, true);
    require(std::count_if(future.begin(), future.end(), [](float x) { return x != 0.0F; }) > 1800,
            "slicing continuation was vacuous silence");
    joined.insert(joined.end(), future.begin(), future.end());
    retained_gap(session, joined);
    ++stats.legacy45_score_cases;
    return joined;
}

void restored_curves(const std::string& bundle, const RuntimeProfile& profile, double rate) {
    const auto initial = score_values(0);
    Session session(bundle, profile, rate, controls_from(initial), "restores, carry and Cancel");
    EventList held;
    held.events = {note_on(0, 60, 0, 0, 1), note_on(1, 48, 0, 1, 2), note_on(2, 48, 0, 2, 3)};
    const std::array<Event, 3> on{{key(Manual::Upper, 60, true), key(Manual::Lower, 48, true), pedal(13, true)}};
    (void)session.process(512, on, nullptr, &held);

    constexpr std::array<std::size_t, 4> carried_indices{{9, 36, 37, 43}};
    constexpr std::array<int, 4> carried_units{{7168, 7168, 8192, 6144}};
    ParameterChanges prime;
    for (std::size_t i = 0; i < carried_indices.size(); ++i) {
        prime.add_queue(kLegacyIds[carried_indices[i]]).points = {{31, normalized(carried_units[i])}};
    }
    EventList old_notes;
    old_notes.events = {note_on(0, 76, 31, 0, 21), note_off(1, 48, 31, 1, 2),
                        note_on(2, 49, 31, 2, 22)};
    session.native(31, &prime, &old_notes);
    std::vector<float> primed;
    for (int frame = 0; frame < 31; ++frame) {
        auto values = initial;
        for (std::size_t i = 0; i < carried_indices.size(); ++i) {
            const auto index = carried_indices[i];
            values[index] += ((carried_units[i] - initial[index]) / 32) * (frame + 1);
        }
        primed.push_back(session.render(1, controls_at(values))[0]);
    }
    session.compare(primed);

    LegacyValues loaded{};
    for (int state = 0; state < 4; ++state) {
        for (std::size_t i = 0; i < 36; ++i) loaded[i] = (1 + (static_cast<int>(i) + 2 * state) % 7) * 1024;
        loaded[36] = (state + 1) * 1024;
        for (const auto i : {37U, 38U, 39U, 40U, 41U, 42U}) loaded[i] = 8192;
        loaded[43] = (state + 2) * 1024;
        loaded[44] = 2048;
        auto snapshot = controls_from(loaded);
        snapshot.route_enabled = {false, false};
        require(session.plugin.load_state(snapshot_text(snapshot)) == Steinberg::kResultOk,
                "pending state restore rejected");
        require(session.saved() == snapshot, "newest pending state was not saved");
        require(session.reference.restore_controls(snapshot), "direct pending restore rejected");
    }
    require(session.reference.active_key_count() == 2 && session.reference.active_pedal_count() == 1,
            "reference restore altered owners/held targets");

    LegacyValues target{};
    for (std::size_t i = 0; i < target.size(); ++i) target[i] = 8192 - loaded[i];
    target[9] = 1024;
    target[36] = 5120;
    target[37] = 8192;
    target[38] = 8192;
    target[43] = 8192;
    LegacyValues fresh = loaded;
    fresh[9] = 5120;
    fresh[36] = 3072;
    fresh[37] = 8192;
    fresh[43] = 2048;
    ParameterChanges curves;
    for (std::size_t reverse = kLegacyIds.size(); reverse != 0; --reverse) {
        const auto i = reverse - 1;
        if (i == 38) continue; // Absent lower selector must retain Cancel through all other curves.
        auto& queue = curves.add_queue(kLegacyIds[i]);
        if (std::find(carried_indices.begin(), carried_indices.end(), i) != carried_indices.end()) {
            queue.points = {{0, 0.125}, {0, normalized(fresh[i])}, {128, normalized(target[i])}};
        } else {
            queue.points = {{127, normalized(target[i])}, {128, normalized(target[i])}};
        }
    }
    EventList current;
    current.events = {note_off(0, 76, 0, 0, 21), note_on(0, 67, 0, 0, 30),
        note_on(1, 55, 0, 1, 31), note_off(2, 49, 0, 2, 22), note_on(2, 52, 0, 2, 33),
        note_on(0, 96, 128, 0, 40), note_off(1, 55, 128, 1, 31), note_off(2, 52, 128, 2, 33)};
    const std::array<Event, 8> boundary_music{{key(Manual::Upper, 76, true),
        key(Manual::Lower, 48, false), pedal(14, true), key(Manual::Upper, 76, false),
        key(Manual::Upper, 67, true), key(Manual::Lower, 55, true), pedal(14, false), pedal(17, true)}};
    session.native(128, &curves, &current);
    std::vector<float> expected;
    for (int frame = 0; frame < 128; ++frame) {
        LegacyValues values{};
        for (std::size_t i = 0; i < values.size(); ++i) {
            const bool carried = std::find(carried_indices.begin(), carried_indices.end(), i) !=
                                 carried_indices.end();
            values[i] = carried ? fresh[i] + ((target[i] - fresh[i]) / 128) * frame :
                                  loaded[i] + ((target[i] - loaded[i]) / 128) * (frame + 1);
        }
        auto physical = controls_at(values, false);
        if (frame == 0) append(physical, boundary_music);
        expected.push_back(session.render(1, physical)[0]);
    }
    session.compare(expected);
    require(session.saved().route_enabled == std::array<bool, 2>{true, false},
            "same-value Upper selector or absent Lower selector mishandled Cancel");
    require(session.saved().expression == 319.0 / 512.0,
            "restore/carry curve did not retain the actual last sample");

    ParameterChanges zero;
    zero.add_queue(0x2000U).points = {{0, 0.25}, {0, 0.5}};
    EventList fresh_notes;
    fresh_notes.events = {note_off(0, 96, 0, 0, 40), note_on(1, 55, 0, 1, 41),
                          note_on(2, 52, 0, 2, 42)};
    target[36] = 4096;
    auto zero_physical = controls_at(target, false);
    const std::array<Event, 6> zero_music{{key(Manual::Upper, 96, true),
        key(Manual::Lower, 55, false), pedal(17, false), key(Manual::Upper, 96, false),
        key(Manual::Lower, 55, true), pedal(17, true)}};
    append(zero_physical, zero_music);
    const auto clock = session.reference.frame_clock();
    (void)session.process(0, zero_physical, &zero, &fresh_notes);
    (void)session.process(0);
    require(session.reference.frame_clock() == clock, "state/carry zero callback advanced time");
    (void)session.process(1024, {}, nullptr, nullptr, true);
    require(!session.saved().route_enabled[1], "absent lower selector reconnected after carry consumption");

    // Same source epoch and held notes, but one explicit same-value selector.
    // This counterfactual proves Lower contributes audible sound after reconnect.
    auto cancelled = session.reference;
    std::vector<float> without_lower(1024);
    require(cancelled.process(1024, without_lower, {}).ok(), "Cancel counterfactual rejected");
    ParameterChanges reconnect;
    reconnect.add_queue(0x2011U).points = {{0, 1.0}};
    const std::array<Event, 1> select{{{0, EventType::SelectBank, Manual::Lower, 0, 1.0}}};
    const auto connected = session.process(1024, select, &reconnect, nullptr, true);
    double difference = 0.0;
    for (std::size_t i = 0; i < connected.size(); ++i) {
        difference = std::max(difference, std::abs(static_cast<double>(connected[i]) - without_lower[i]));
    }
    require(difference > 0.00001, "same-value reconnect had no meaningful audible Lower contribution");
    stats.reconnect_difference = std::max(stats.reconnect_difference, difference);
    require(session.saved().route_enabled[1], "explicit same-value Lower selector failed to reconnect");
    ++stats.restore_cases;
}

void preset_commands_and_aliases(const std::string& bundle, const RuntimeProfile& profile, double rate) {
    auto initial = controls_from(score_values(0));
    initial.fixed_registrations = {FixedRegistration::FSharp, FixedRegistration::CSharp};
    initial.route_enabled = {false, true};
    Session session(bundle, profile, rate, initial, "fixed selectors, aliases and raw controller cache");
    EventList held;
    held.events = {note_on(0, 60, 0, 0, 1), note_on(1, 48, 0, 1, 2), note_on(2, 48, 0, 2, 3)};
    const std::array<Event, 3> on{{key(Manual::Upper, 60, true), key(Manual::Lower, 48, true), pedal(13, true)}};
    (void)session.process(257, on, nullptr, &held);
    const auto send = [&](std::uint32_t id, double value, Event event) {
        ParameterChanges point;
        point.add_queue(id).points = {{0, value}};
        const std::array<Event, 1> physical{{event}};
        (void)session.process(0, physical, &point);
    };
    require_ok(session.plugin.controller->setParamNormalized(0x2010U, 0.6), "cache legacy bank");
    require_ok(session.plugin.controller->setParamNormalized(0x5000U, 0.12345678901234567), "cache raw selector");
    require_ok(session.plugin.controller->setParamNormalized(0x5001U, -0.0), "cache raw negative zero");
    for (const auto index : {45U, 46U}) {
        for (int selection = 0; selection < 12; ++selection) {
            const int units = (selection * kUnit + 5) / 11;
            const auto event = physical_control(index, units);
            require(event.type == EventType::SelectPreset && event.index == 0 &&
                    event.value == static_cast<double>(selection), "new selector became a pedal or wrong key");
            send(index == 45 ? 0x5000U : 0x5001U, normalized(units), event);
            (void)session.process(13);
            ++stats.preset_commands;
        }
    }
    for (const auto id : {0x5000U, 0x5001U}) {
        for (std::size_t lower = 0; lower < preset_oracle::thresholds.size(); ++lower) {
            const auto threshold = preset_oracle::thresholds[lower];
            const std::array<double, 3> values{{std::nextafter(threshold, 0.0), threshold,
                                               std::nextafter(threshold, 1.0)}};
            for (std::size_t at = 0; at < values.size(); ++at) {
                send(id, values[at], {0, EventType::SelectPreset,
                    id == 0x5000U ? Manual::Upper : Manual::Lower, 0,
                    static_cast<double>(lower + (at == 0 ? 0U : 1U))});
                (void)session.process(1);
                ++stats.preset_thresholds;
            }
        }
    }
    ParameterChanges conflict;
    conflict.add_queue(0x5001U).points = {{0, preset_oracle::canonical[5]}};
    conflict.add_queue(0x5000U).points = {{0, preset_oracle::canonical[3]}};
    conflict.add_queue(0x2011U).points = {{0, 0.61}};
    conflict.add_queue(0x2010U).points = {{0, 0.6}};
    const std::array<Event, 4> ordered{{
        {0, EventType::SelectBank, Manual::Upper, 0, 1.0},
        {0, EventType::SelectBank, Manual::Lower, 0, 1.0},
        {0, EventType::SelectPreset, Manual::Upper, 0, 3.0},
        {0, EventType::SelectPreset, Manual::Lower, 0, 5.0}}};
    (void)session.process(0, ordered, &conflict);
    require(session.saved().fixed_registrations ==
            std::array<FixedRegistration, 2>{FixedRegistration::DSharp, FixedRegistration::F},
            "higher selector IDs did not win reverse-enumerated same-sample aliases");
    (void)session.process(17);
    ParameterChanges empty;
    (void)empty.add_queue(0x5000U);
    (void)empty.add_queue(0x2010U);
    (void)session.process(19, {}, &empty);

    // The old bank's raw 0.6 anchor is still B. A changed normalized plateau
    // does not reassert B until its explicit endpoint becomes a carried point.
    ParameterChanges old_plateau;
    old_plateau.add_queue(0x2010U).points = {{7, 0.61}};
    (void)session.process(7, {}, &old_plateau);
    require(session.saved().fixed_registrations[0] == FixedRegistration::DSharp,
            "unchanged old-bank plateau reasserted routing");
    const std::array<Event, 1> old_endpoint{{{0, EventType::SelectBank, Manual::Upper, 0, 1.0}}};
    (void)session.process(0, old_endpoint);
    require(session.saved().fixed_registrations[0] == FixedRegistration::None,
            "explicit carried old-bank endpoint failed to exit fixed mode");

    // Conversely the new selector retains raw 3/11 even while the old bank
    // command has selected B. Its same-plain plateau must leave B connected.
    ParameterChanges new_plateau;
    new_plateau.add_queue(0x5000U).points = {{7, 0.28}};
    (void)session.process(7, {}, &new_plateau);
    require(session.saved().fixed_registrations[0] == FixedRegistration::None,
            "unchanged new-selector plateau reasserted fixed mode");
    const std::array<Event, 1> new_endpoint{{{0, EventType::SelectPreset, Manual::Upper, 0, 3.0}}};
    (void)session.process(0, new_endpoint);
    send(0x5000U, -0.0, {0, EventType::SelectPreset, Manual::Upper, 0, 0.0});
    require(session.saved().fixed_registrations[0] == FixedRegistration::DSharp &&
            !session.saved().route_enabled[0], "Cancel discarded remembered fixed mode");
    (void)session.process(23);
    send(0x2010U, 0.61, {0, EventType::SelectBank, Manual::Upper, 0, 1.0});
    require(session.saved().fixed_registrations[0] == FixedRegistration::None &&
            session.saved().route_enabled[0], "same-value old bank did not reconnect and clear fixed mode");
    ++stats.preset_alias_cases;

    // Prime a real selector curve and a boundary note. Four complete restores
    // then precede carry/fresh commands, with fresh duplicate selectors last.
    ParameterChanges prime;
    prime.add_queue(0x5000U).points = {{0, preset_oracle::canonical[2]},
                                     {16, preset_oracle::canonical[7]}};
    EventList boundary_note;
    boundary_note.events = {note_on(0, 76, 16, 0, 4)};
    session.native(16, &prime, &boundary_note);
    std::vector<float> primed;
    for (std::uint32_t frame = 0; frame < 16; ++frame) {
        const auto value = preset_oracle::canonical[2] + (static_cast<double>(frame) / 16.0) *
                           (preset_oracle::canonical[7] - preset_oracle::canonical[2]);
        const std::array<Event, 1> event{{{0, EventType::SelectPreset, Manual::Upper, 0,
                                         static_cast<double>(preset_oracle::plain(value))}}};
        primed.push_back(session.render(1, event)[0]);
    }
    session.compare(primed);
    for (unsigned index = 0; index < 4; ++index) {
        auto restored = initial;
        restored.fixed_registrations = {static_cast<FixedRegistration>(index + 1), FixedRegistration::A};
        restored.selected_banks = {DrawbarBank::A, DrawbarBank::B};
        restored.route_enabled = {false, false};
        require_ok(session.plugin.load_state(snapshot_text(restored)), "fixed state with pending carry");
        require(session.saved() == restored, "pending fixed save lost raw mode");
        require(session.reference.restore_controls(restored), "fixed direct restore failed");
    }
    ParameterChanges fresh;
    fresh.add_queue(0x5001U).points = {{0, 0.0}};
    fresh.add_queue(0x5000U).points = {{0, preset_oracle::canonical[1]}, {0, preset_oracle::canonical[4]}};
    fresh.add_queue(0x2010U).points = {{0, 0.6}};
    EventList releases;
    releases.events = {note_off(0, 76, 0, 0, 4)};
    const std::array<Event, 5> restored_events{{
        {0, EventType::SelectBank, Manual::Upper, 0, 1.0},
        {0, EventType::SelectPreset, Manual::Upper, 0, 4.0},
        {0, EventType::SelectPreset, Manual::Lower, 0, 0.0},
        key(Manual::Upper, 76, true), key(Manual::Upper, 76, false)}};
    const auto clock = session.reference.frame_clock();
    (void)session.process(0, restored_events, &fresh, &releases);
    (void)session.process(0);
    require(session.reference.frame_clock() == clock && session.reference.active_key_count() == 2 &&
            session.reference.active_pedal_count() == 1, "zero restore/carry changed elapsed time or held targets");
    (void)session.process(257, {}, nullptr, nullptr, true);
    require(session.saved().fixed_registrations ==
            std::array<FixedRegistration, 2>{FixedRegistration::E, FixedRegistration::A} &&
            session.saved().route_enabled == std::array<bool, 2>{true, false},
            "restore/carry/fresh selector precedence lost retained state");
    ++stats.preset_restore_cases;

    require(std::bit_cast<std::uint64_t>(session.plugin.controller->getParamNormalized(0x2010U)) ==
            std::bit_cast<std::uint64_t>(0.6), "audio changed the controller raw bank cache");
    require(std::bit_cast<std::uint64_t>(session.plugin.controller->getParamNormalized(0x5000U)) ==
            std::bit_cast<std::uint64_t>(0.12345678901234567), "audio changed the controller raw selector cache");
    require(std::signbit(session.plugin.controller->getParamNormalized(0x5001U)),
            "audio canonicalized raw cached negative zero");
    MemoryStream component_state(snapshot_text(session.saved()));
    require_ok(session.plugin.controller->setComponentState(&component_state), "explicit controller state refresh");
    require(session.plugin.controller->getParamNormalized(0x5000U) == preset_oracle::canonical[4] &&
            session.plugin.controller->getParamNormalized(0x5001U) == 0.0 &&
            session.plugin.controller->getParamNormalized(0x2010U) == 1.0 &&
            session.plugin.controller->getParamNormalized(0x2011U) == 1.0,
            "controller state refresh did not separate effective selection and retained bank");
}

std::vector<float> preset_curve_partition(const std::string& bundle, const RuntimeProfile& profile,
                                         double rate, const std::vector<std::uint32_t>& partition) {
    auto initial = controls_from(score_values(0));
    initial.selected_banks = {DrawbarBank::B, DrawbarBank::B};
    initial.route_enabled = {true, false};
    Session session(bundle, profile, rate, initial, "new selector curve partitions");
    EventList held;
    held.events = {note_on(0, 60, 0, 0, 1), note_on(1, 48, 0, 1, 2), note_on(2, 48, 0, 2, 3)};
    const std::array<Event, 3> on{{key(Manual::Upper, 60, true), key(Manual::Lower, 48, true), pedal(13, true)}};
    (void)session.process(257, on, nullptr, &held);
    std::vector<float> joined;
    std::uint32_t start = 0;
    for (const auto frames : partition) {
        ParameterChanges curves;
        const auto endpoint = static_cast<double>(start + frames) / 512.0;
        curves.add_queue(0x5001U).points = {{static_cast<int32>(frames - 1), endpoint}};
        curves.add_queue(0x5000U).points = {{static_cast<int32>(frames - 1), 1.0 - endpoint}};
        session.native(frames, &curves, nullptr);
        std::vector<float> expected;
        for (std::uint32_t frame = 0; frame < frames; ++frame) {
            const auto lower = static_cast<double>(start + frame + 1) / 512.0;
            const std::array<Event, 2> events{{
                {0, EventType::SelectPreset, Manual::Upper, 0,
                 static_cast<double>(preset_oracle::plain(1.0 - lower))},
                {0, EventType::SelectPreset, Manual::Lower, 0,
                 static_cast<double>(preset_oracle::plain(lower))}}};
            expected.push_back(session.render(1, events)[0]);
        }
        session.compare(expected);
        joined.insert(joined.end(), expected.begin(), expected.end());
        start += frames;
    }
    require(start == 512, "preset partitions do not cover their complete curve");
    const auto future = session.process(257, {}, nullptr, nullptr, true);
    joined.insert(joined.end(), future.begin(), future.end());
    ++stats.preset_partition_cases;
    return joined;
}

} // namespace

int main(int argc, char** argv) {
    try {
        require(argc == 3, "usage: test_native_automation <bundle> <compiled-profile>");
        RuntimeProfile profile;
        std::string error;
        require(load_runtime_profile_file(argv[2], profile, error), error);
        const std::string bundle = argv[1];
        for (const double rate : {44100.0, 48000.0, 96000.0}) {
            const auto whole = legacy45_curves(bundle, profile, rate, {kScoreFrames});
            const auto partitioned = legacy45_curves(bundle, profile, rate, irregular_partition());
            require(whole.size() == partitioned.size(), "partition length differs");
            for (std::size_t i = 0; i < whole.size(); ++i) {
                require(std::bit_cast<std::uint32_t>(whole[i]) == std::bit_cast<std::uint32_t>(partitioned[i]),
                        "whole/irregular audio or future continuation differs");
                ++stats.partition_samples;
            }
            restored_curves(bundle, profile, rate);
            preset_commands_and_aliases(bundle, profile, rate);
            const auto preset_whole = preset_curve_partition(bundle, profile, rate, {512});
            for (const auto& partition : std::array<std::vector<std::uint32_t>, 2>{{
                     {1, 7, 13, 29, 63, 127, 272}, {17, 31, 2, 63, 15, 128, 256}}}) {
                const auto divided = preset_curve_partition(bundle, profile, rate, partition);
                require(divided.size() == preset_whole.size(), "preset partition length differs");
                for (std::size_t i = 0; i < divided.size(); ++i) {
                    require(std::bit_cast<std::uint32_t>(divided[i]) == std::bit_cast<std::uint32_t>(preset_whole[i]),
                            "preset partition/future audio differs");
                    ++stats.partition_samples;
                }
            }
        }
        require(stats.maximum_error == 0.0 && stats.maximum_peak < 1.0, "reference error or clipping");
        std::cout << "native automation: legacy45_score_cases=" << stats.legacy45_score_cases
                  << " restore_cases=" << stats.restore_cases << " gap_cases=" << stats.gap_cases
                  << " preset_commands=" << stats.preset_commands
                  << " preset_thresholds=" << stats.preset_thresholds
                  << " preset_alias_cases=" << stats.preset_alias_cases
                  << " preset_restore_cases=" << stats.preset_restore_cases
                  << " preset_partition_cases=" << stats.preset_partition_cases
                  << " callbacks=" << stats.callbacks
                  << " zero_callbacks=" << stats.zero_callbacks << " state_reads=" << stats.state_reads
                  << " direct_reference_frames=" << stats.reference_frames
                  << " exact_channel_samples=" << stats.channel_samples
                  << " partition_mono_samples=" << stats.partition_samples
                  << " future_channel_samples=" << stats.future_channel_samples
                  << " nonzero_channel_samples=" << stats.nonzero_channel_samples
                  << " long_callbacks=" << stats.long_callbacks
                  << " guaranteed_expression_events=" << stats.guaranteed_expression_events
                  << " isolated_windows=" << stats.isolated_windows
                  << " division_min_rms=" << stats.division_min_rms[0] << ','
                  << stats.division_min_rms[1] << ',' << stats.division_min_rms[2]
                  << " reconnect_difference=" << stats.reconnect_difference
                  << " maximum_error=" << stats.maximum_error << " peak=" << stats.maximum_peak
                  << " checksum=" << std::hex << stats.checksum << std::dec << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "native automation failure: " << error.what() << '\n';
        return 1;
    }
}
