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
#include <functional>
#include <iostream>
#include <limits>
#include <span>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

namespace {

using namespace hammond;
using namespace hammond::native_test;
using Steinberg::int32;
using Steinberg::int16;
constexpr float kSentinel = -123.25F;
constexpr Steinberg::uint64 kFlagSentinel = 0xA5U;
constexpr std::uint32_t kExpression = 0x2000U;
constexpr std::uint32_t kUpperSelector = 0x2010U;
constexpr std::uint32_t kLowerSelector = 0x2011U;
constexpr std::uint32_t kPedalOne = 0x4000U;
constexpr std::uint32_t kPedalTwo = 0x4001U;

struct Statistics {
    std::uint64_t checks{0};
    std::uint64_t accepted_callbacks{0};
    std::uint64_t rejected_callbacks{0};
    std::uint64_t zero_callbacks{0};
    std::uint64_t direct_reference_frames{0};
    std::uint64_t exact_channel_samples{0};
    std::uint64_t paired_setup_channel_samples{0};
    std::uint64_t future_audio_samples{0};
    std::uint64_t audible_samples{0};
    std::uint64_t state_reads{0};
    std::uint64_t rejected_state_loads{0};
    std::uint64_t threshold_cases{0};
    std::uint64_t rollback_cases{0};
    std::uint64_t partition_cases{0};
    std::uint64_t rate_changes{0};
    std::uint64_t isolated_division_cases{0};
    std::uint64_t checksum{1469598103934665603ULL};
    std::array<double, 3> division_peaks{};
    double peak{0.0};
} stats;

void check(bool condition, std::string_view message) {
    ++stats.checks;
    require(condition, message);
}

void native_call(NativePlugin& plugin, sv::ProcessData& data,
                 bool expected_success, std::string_view label) {
    const auto result = plugin.processor->process(data);
    check((result == Steinberg::kResultOk) == expected_success,
          std::string(label) + ": native result " + std::to_string(result));
    if (expected_success) {
        ++stats.accepted_callbacks;
        if (data.numSamples == 0) ++stats.zero_callbacks;
    } else {
        ++stats.rejected_callbacks;
    }
}

ControlSnapshot saved(NativePlugin& plugin) {
    std::string bytes;
    check(plugin.save_state(bytes) == Steinberg::kResultOk, "native getState failed");
    ++stats.state_reads;
    check(bytes.starts_with("B3CONTROLS4\n"), "native save did not write controls v4");
    return parse_snapshot(bytes);
}

void same_controls(const ControlSnapshot& actual, const ControlSnapshot& expected,
                   std::string_view label) {
    check(actual == expected, std::string(label) + ": complete controls differ");
    check(std::bit_cast<std::uint64_t>(actual.expression) ==
          std::bit_cast<std::uint64_t>(expected.expression),
          std::string(label) + ": expression representation differs");
}

ControlSnapshot registration() {
    ControlSnapshot controls{};
    controls.selected_banks = {DrawbarBank::B, DrawbarBank::B};
    controls.drawbars[0][1][2] = 4;
    controls.drawbars[1][1][2] = 3;
    controls.pedal_drawbars = {2, 1};
    controls.expression = 0.625;
    controls.percussion.enabled = true;
    return controls;
}

Event key(std::uint32_t offset, Manual manual, std::uint8_t pitch, bool on) {
    return {offset, on ? EventType::NoteOn : EventType::NoteOff, manual, pitch,
            on ? 127.0 : 0.0};
}

Event pedal(std::uint32_t offset, std::uint8_t id, bool on) {
    return {offset, on ? EventType::PedalOn : EventType::PedalOff,
            Manual::Lower, id, on ? 127.0 : 0.0};
}

Event expression(double value) {
    return {0, EventType::Expression, Manual::Upper, 0, value};
}

void restore(Engine& engine, const ControlSnapshot& controls) {
    check(engine.restore_controls(controls), "reference restore failed");
}

std::vector<float> reference_block(Engine& engine, std::uint32_t frames,
                                 std::span<const Event> events = {}) {
    std::vector<float> result(frames);
    const auto before = engine.frame_clock();
    const auto status = engine.process(frames, result, events);
    check(status.ok() && status.events_consumed == events.size(), "plain Engine rejected oracle");
    check(engine.frame_clock() == before + frames, "plain Engine clock mismatch");
    stats.direct_reference_frames += frames;
    return result;
}

void sample_equal(float actual, float expected, std::string_view label) {
    check(std::isfinite(actual) && std::isfinite(expected), "nonfinite audio sample");
    check(std::bit_cast<std::uint32_t>(actual) == std::bit_cast<std::uint32_t>(expected),
          std::string(label) + ": sample differs (actual " + std::to_string(actual) +
          ", expected " + std::to_string(expected) + ")");
    ++stats.exact_channel_samples;
    if (actual != 0.0F) ++stats.audible_samples;
    stats.peak = std::max(stats.peak, std::abs(static_cast<double>(actual)));
    stats.checksum ^= std::bit_cast<std::uint32_t>(actual);
    stats.checksum *= 1099511628211ULL;
}

void compare_audio(const StereoBlock& block, std::span<const float> expected,
                   std::string_view label) {
    bool silent = true;
    for (std::size_t i = 0; i < expected.size(); ++i) {
        sample_equal(block.channels[0][i], expected[i], label);
        sample_equal(block.channels[1][i], expected[i], label);
        silent = silent && expected[i] == 0.0F;
    }
    check(block.bus.silenceFlags == (silent ? 3U : 0U), "silence flags disagree with actual audio");
    for (std::size_t i = expected.size(); i < block.left.size(); ++i) {
        check(block.left[i] == kSentinel && block.right[i] == kSentinel,
              "successful callback overwrote output tail");
    }
}

void reset_block(StereoBlock& block, int32 frames, EventList* notes = nullptr,
                 ParameterChanges* parameters = nullptr) {
    block.channels = {block.left.data(), block.right.data()};
    block.bus.numChannels = 2;
    block.bus.channelBuffers32 = block.channels.data();
    block.bus.silenceFlags = kFlagSentinel;
    block.data = {};
    block.data.processMode = sv::kRealtime;
    block.data.symbolicSampleSize = sv::kSample32;
    block.data.numOutputs = 1;
    block.data.outputs = &block.bus;
    block.data.inputEvents = notes;
    block.data.inputParameterChanges = parameters;
    block.set_frames(frames);
    block.fill(kSentinel);
}

class ReferenceSession {
public:
    NativePlugin plugin;
    Engine engine{};
    StereoBlock block;

    ReferenceSession(const std::string& bundle, const RuntimeProfile& profile,
                     double rate, const ControlSnapshot& controls = registration(),
                     int32 maximum = static_cast<int32>(kHardMaxBlockFrames))
        : plugin(bundle), block(static_cast<std::size_t>(maximum) + 4) {
        plugin.start(rate, maximum);
        check(engine.prepare(profile, {rate, kHardMaxBlockFrames, 0, 0},
                             make_nominal_console_model()) == Status::Ok,
              "plain Engine preparation failed");
        check(plugin.load_state(snapshot_text(controls)) == Steinberg::kResultOk,
              "initial native state load failed");
        restore(engine, controls);
    }

    std::vector<float> process(std::uint32_t frames, EventList* notes = nullptr,
                               std::span<const Event> physical = {},
                               ParameterChanges* parameters = nullptr,
                               std::string_view label = "direct reference") {
        reset_block(block, static_cast<int32>(frames), notes, parameters);
        native_call(plugin, block.data, true, label);
        auto expected = reference_block(engine, frames, physical);
        compare_audio(block, expected, label);
        same_controls(saved(plugin), engine.controls_snapshot(), label);
        return expected;
    }

    std::vector<float> sampled(std::uint32_t frames, EventList* notes,
                               ParameterChanges& parameters,
                               const std::function<std::vector<Event>(std::uint32_t)>& oracle,
                               std::string_view label) {
        reset_block(block, static_cast<int32>(frames), notes, &parameters);
        native_call(plugin, block.data, true, label);
        std::vector<float> expected;
        expected.reserve(frames);
        for (std::uint32_t frame = 0; frame < frames; ++frame) {
            const auto events = oracle(frame);
            const auto one = reference_block(engine, 1, events);
            expected.push_back(one[0]);
        }
        compare_audio(block, expected, label);
        same_controls(saved(plugin), engine.controls_snapshot(), label);
        return expected;
    }
};

void isolated_divisions(const std::string& bundle, const RuntimeProfile& profile, double rate) {
    for (int32 division = 0; division < 3; ++division) {
        ControlSnapshot controls{};
        controls.selected_banks = {DrawbarBank::B, DrawbarBank::B};
        controls.expression = 0.5;
        if (division == 2) controls.pedal_drawbars = {2, 1};
        else controls.drawbars[static_cast<std::size_t>(division)][1][2] = 8;
        ReferenceSession session(bundle, profile, rate, controls);
        const int16 pitch = division == 0 ? 60 : 48;
        EventList note;
        note.events = {note_on(division, pitch, 0, 7, 123)};
        const std::array<Event, 1> physical{{division == 2 ? pedal(0, 13, true) :
            key(0, division == 0 ? Manual::Upper : Manual::Lower,
                static_cast<std::uint8_t>(pitch), true)}};
        const auto samples = session.process(2048, &note, physical, nullptr,
                                             "isolated audible native division");
        double peak = 0.0;
        std::size_t nonzero = 0;
        for (const float sample : samples) {
            peak = std::max(peak, std::abs(static_cast<double>(sample)));
            if (sample != 0.0F) ++nonzero;
        }
        check(peak > 0.00001 && peak < 1.0 && nonzero > 1000,
              "isolated division was inaudible or trivial");
        auto& maximum = stats.division_peaks[static_cast<std::size_t>(division)];
        maximum = std::max(maximum, peak);
        ++stats.isolated_division_cases;
    }
}

void musical_ownership(const std::string& bundle, const RuntimeProfile& profile, double rate) {
    ReferenceSession session(bundle, profile, rate);
    EventList notes;
    notes.events = {
        note_on(0, 60, 0, 0, 10), note_on(0, 60, 5, 1, 11), note_on(0, 60, 7, 0, 10),
        note_on(1, 60, 9, 0, 20), note_on(2, 48, 11, 0, 30), note_on(2, 48, 13, 1, 31),
        note_on(0, 64, 15, 2), note_on(0, 64, 16, 2),
        note_on(2, 52, 17, 3), note_on(2, 52, 18, 3),
        note_on(2, 36, 21, 0, 40, std::numeric_limits<float>::denorm_min()),
        note_on(0, 67, 22, 0, 50, std::numeric_limits<float>::denorm_min()),
        note_on(0, 0, 23, 0, 60),
        note_on(0, 67, 25, 0, 50),
        note_off(0, 60, 80, 0, 10), note_off(0, 60, 90, 1, 11),
        note_off(1, 60, 91, 0, 20), note_off(2, 48, 92, 0, 30), note_off(2, 48, 100, 1, 31),
        note_off(0, 64, 110, 2), note_off(2, 52, 111, 3),
        note_off(0, 64, 120, 2), note_off(2, 52, 121, 3),
        note_on(2, 36, 122, 0, 40, 0.0F), note_on(0, 67, 125, 0, 50, 0.0F)};
    notes.events[13].noteOn.tuning = 17.0F; // Explicitly ignored, no new source.
    sv::Event pressure{};
    pressure.type = sv::Event::kPolyPressureEvent;
    pressure.busIndex = 0;
    pressure.sampleOffset = 24;
    pressure.polyPressure = {0, 60, 0.5F, 10};
    notes.events.insert(notes.events.begin() + 13, pressure);
    const std::array<Event, 16> physical{{
        key(0, Manual::Upper, 60, true), key(9, Manual::Lower, 60, true), pedal(11, 13, true),
        key(15, Manual::Upper, 64, true), pedal(17, 17, true), pedal(21, 1, true),
        key(22, Manual::Upper, 67, true), key(90, Manual::Upper, 60, false),
        key(91, Manual::Lower, 60, false), pedal(100, 13, false),
        key(120, Manual::Upper, 64, false), pedal(121, 17, false), pedal(122, 1, false),
        key(125, Manual::Upper, 67, false),
        // No-op physical releases make the explicit schedule's final state clear.
        pedal(200, 13, false), key(201, Manual::Lower, 60, false)}};
    (void)session.process(256, &notes, physical, nullptr, "manual/pedal owner collisions");
    (void)session.process(1024, nullptr, {}, nullptr, "complete release travel");
    check(session.engine.active_key_count() == 0 && session.engine.active_pedal_count() == 0,
          "reference fixture did not release every target");
}

void output_and_lifecycle(const std::string& bundle, const RuntimeProfile& profile, double rate) {
    ReferenceSession session(bundle, profile, rate);
    EventList held;
    held.events = {note_on(0, 96, 0, 0, 1), note_on(1, 48, 0, 1, 2), note_on(2, 48, 0, 2, 3)};
    const std::array<Event, 3> physical{{key(0, Manual::Upper, 96, true),
        key(0, Manual::Lower, 48, true), pedal(0, 13, true)}};
    (void)session.process(1024, &held, physical);
    check(session.engine.percussion_diagnostics().readiness < 1.0,
          "held percussion fixture did not consume readiness");
    session.plugin.stop_processing();
    session.plugin.begin_processing();
    (void)session.process(1, nullptr, {}, nullptr, "stop/restart preserves epoch");
    (void)session.process(kHardMaxBlockFrames, nullptr, {}, nullptr, "maximum native callback");

    reset_block(session.block, 37);
    session.block.data.numOutputs = 0;
    session.block.data.outputs = nullptr;
    native_call(session.plugin, session.block.data, true, "disconnected output");
    (void)reference_block(session.engine, 37);
    check(std::all_of(session.block.left.begin(), session.block.left.end(),
                     [](float value) { return value == kSentinel; }), "disconnected output written");
    (void)session.process(71, nullptr, {}, nullptr, "after disconnected interval");

    session.plugin.stop_processing();
    check(session.plugin.component->activateBus(sv::kAudio, sv::kOutput, 0, false) ==
          Steinberg::kResultOk, "could not deactivate output bus");
    session.plugin.begin_processing();
    reset_block(session.block, 47);
    session.block.channels = {nullptr, nullptr};
    native_call(session.plugin, session.block.data, true, "inactive output null channels");
    (void)reference_block(session.engine, 47);
    check(session.block.bus.silenceFlags == kFlagSentinel, "inactive silence flags changed");
    check(std::all_of(session.block.left.begin(), session.block.left.end(),
                     [](float value) { return value == kSentinel; }) &&
          std::all_of(session.block.right.begin(), session.block.right.end(),
                     [](float value) { return value == kSentinel; }), "inactive output memory changed");
    session.plugin.stop_processing();
    check(session.plugin.component->activateBus(sv::kAudio, sv::kOutput, 0, true) ==
          Steinberg::kResultOk, "could not reactivate output bus");
    session.plugin.begin_processing();
    (void)session.process(29, nullptr, {}, nullptr, "after inactive output interval");

    reset_block(session.block, 53);
    session.block.channels[1] = session.block.channels[0];
    native_call(session.plugin, session.block.data, true, "exact stereo alias");
    const auto alias_expected = reference_block(session.engine, 53);
    compare_audio(session.block, alias_expected, "exact stereo alias");
    check(std::all_of(session.block.right.begin(), session.block.right.end(),
                     [](float value) { return value == kSentinel; }), "unused alias destination changed");

    ParameterChanges flush_parameters;
    flush_parameters.add_queue(kExpression).points = {{0, 0.5}};
    EventList flush_notes;
    flush_notes.events = {note_off(2, 48, 0, 2, 3)};
    reset_block(session.block, 0, &flush_notes, &flush_parameters);
    session.block.bus.numChannels = 0;
    session.block.bus.channelBuffers32 = nullptr;
    native_call(session.plugin, session.block.data, true, "zero-channel zero-frame flush");
    const std::array<Event, 2> flush{{expression(0.5), pedal(0, 13, false)}};
    (void)reference_block(session.engine, 0, flush);
    check(session.block.bus.silenceFlags == 0, "zero-channel flags were not zero");
    reset_block(session.block, 0);
    session.block.channels = {nullptr, nullptr};
    native_call(session.plugin, session.block.data, true, "empty zero-frame flush");
    (void)reference_block(session.engine, 0);
    same_controls(saved(session.plugin), session.engine.controls_snapshot(), "zero flush state");
    (void)session.process(33);

    const double next_rate = rate == 44100.0 ? 96000.0 : rate == 96000.0 ? 48000.0 : 44100.0;
    const auto clock = session.engine.frame_clock();
    session.plugin.stop_processing();
    session.plugin.deactivate();
    session.plugin.configure(next_rate, 127);
    session.plugin.activate();
    session.plugin.begin_processing();
    check(session.engine.reconfigure_sample_rate(next_rate) == Status::Ok, "reference rate migration failed");
    check(session.engine.frame_clock() == clock, "reference migration advanced time");
    ++stats.rate_changes;
    (void)session.process(71, nullptr, {}, nullptr, "stopped rate/block migration");
    reset_block(session.block, 128);
    native_call(session.plugin, session.block.data, false, "new maximum bound");
    check(session.block.left[0] == kSentinel && session.block.bus.silenceFlags == kFlagSentinel,
          "oversized migrated callback changed output");
    (void)session.process(31, nullptr, {}, nullptr, "after rejected migrated maximum");
}

void boundary_automation(const std::string& bundle, const RuntimeProfile& profile, double rate) {
    auto controls = registration();
    controls.expression = 0.25;
    controls.pedal_drawbars[0] = 0;
    ReferenceSession session(bundle, profile, rate, controls);
    EventList held;
    held.events = {note_on(0, 60, 0, 0, 1), note_on(1, 48, 0, 1, 2), note_on(2, 48, 0, 2, 3)};
    const std::array<Event, 3> initial{{key(0, Manual::Upper, 60, true),
        key(0, Manual::Lower, 48, true), pedal(0, 13, true)}};
    (void)session.process(512, &held, initial);
    ParameterChanges curves;
    curves.add_queue(kPedalOne).points = {{15, 1.0}}; // Deliberately reverse ID order.
    curves.add_queue(kExpression).points = {{15, 1.0}};
    EventList boundary;
    boundary.events = {note_on(0, 72, 15, 0, 4), note_off(2, 48, 15, 2, 3), note_on(2, 49, 15, 2, 5)};
    (void)session.sampled(15, &boundary, curves, [](std::uint32_t i) {
        // Closed-form dyadic reference; no HostTimeline or ParameterBridge use.
        return std::vector<Event>{expression(0.25 + static_cast<double>(i + 1) * 3.0 / 64.0),
            {0, EventType::PedalDrawbar, Manual::Lower, 0, static_cast<double>((i + 2) / 2)}};
    }, "offset-N interpolation and discrete thresholds");
    check(saved(session.plugin).expression == 0.953125, "future endpoint replaced last-sample anchor");

    ParameterChanges at_zero;
    at_zero.add_queue(kExpression).points = {{0, 0.375}, {0, 0.5}};
    at_zero.add_queue(kPedalOne).points = {{0, 0.25}};
    EventList fresh;
    fresh.events = {note_off(0, 72, 0, 0, 4), note_off(2, 49, 0, 2, 5), note_on(2, 50, 0, 2, 6)};
    const std::array<Event, 8> zero_expected{{expression(0.5),
        {0, EventType::PedalDrawbar, Manual::Lower, 0, 2.0},
        key(0, Manual::Upper, 72, true), pedal(0, 13, false), pedal(0, 14, true),
        key(0, Manual::Upper, 72, false), pedal(0, 14, false), pedal(0, 15, true)}};
    (void)session.process(0, &fresh, zero_expected, &at_zero, "carried/fresh zero-offset ordering");
    (void)session.process(0, nullptr, {}, nullptr, "consumed zero boundary does not replay");
    (void)session.process(128);

    // A late malformed queue must not change an otherwise unmasked anchor.
    ParameterChanges invalid;
    invalid.add_queue(kExpression).points = {{0, 0.125}, {15, std::numeric_limits<double>::quiet_NaN()}};
    reset_block(session.block, 16, nullptr, &invalid);
    native_call(session.plugin, session.block.data, false, "late invalid curve preserves unmasked anchor");
    same_controls(saved(session.plugin), session.engine.controls_snapshot(), "rejected curve state");
    ParameterChanges recovery;
    recovery.add_queue(kExpression).points = {{15, 0.75}};
    (void)session.sampled(16, nullptr, recovery, [](std::uint32_t i) {
        return std::vector<Event>{expression(0.5 + static_cast<double>(i + 1) / 64.0)};
    }, "future curve from preserved previous-sample anchor");
}

void control_mapping_and_cancel(const std::string& bundle, const RuntimeProfile& profile) {
    auto initial_controls = registration();
    initial_controls.route_enabled = {false, false};
    ReferenceSession session(bundle, profile, 48000.0, initial_controls);
    EventList notes;
    notes.events = {note_on(0, 60, 0, 0, 1), note_on(1, 48, 0, 1, 2), note_on(2, 48, 0, 2, 3)};
    const std::array<Event, 3> held{{key(0, Manual::Upper, 60, true),
        key(0, Manual::Lower, 48, true), pedal(0, 13, true)}};
    (void)session.process(512, &notes, held);
    check(!saved(session.plugin).route_enabled[0], "absent selector reconnected Cancel");
    ParameterChanges same_selector;
    same_selector.add_queue(kUpperSelector).points = {{0, 1.0}};
    const std::array<Event, 1> reconnect{{{0, EventType::SelectBank, Manual::Upper, 0, 1.0}}};
    (void)session.process(0, nullptr, reconnect, &same_selector, "same-value selector reconnects Cancel");
    check(saved(session.plugin).route_enabled[0] && !saved(session.plugin).route_enabled[1],
          "selector did not reconnect only its own route");
    (void)session.process(67);

    // All 47 IDs enter the actual processor in reverse queue enumeration order.
    // Expected fields and ID arithmetic follow the permanent registry contract,
    // without calling the production parameter descriptor/conversion routines.
    ParameterChanges all;
    std::vector<std::pair<std::uint32_t, double>> values;
    ControlSnapshot expected{};
    for (std::size_t group = 0; group < 4; ++group) {
        for (std::size_t drawbar = 0; drawbar < 9; ++drawbar) {
            const auto position = static_cast<std::uint8_t>((group * 9 + drawbar + 1) % 9);
            expected.drawbars[group / 2][group % 2][drawbar] = position;
            values.emplace_back(0x1000U + static_cast<std::uint32_t>(group * 16 + drawbar),
                                static_cast<double>(position) / 8.0);
        }
    }
    expected.expression = 0.375;
    expected.selected_banks = {DrawbarBank::A, DrawbarBank::B};
    expected.percussion = {true, PercussionHarmonic::Third, PercussionVolume::Soft, PercussionDecay::Fast};
    expected.pedal_drawbars = {6, 5};
    expected.fixed_registrations = {FixedRegistration::CSharp, FixedRegistration::A};
    values.insert(values.end(), {{kExpression, 0.375}, {kUpperSelector, 0.0}, {kLowerSelector, 1.0},
        {0x3000U, 1.0}, {0x3001U, 1.0}, {0x3002U, 1.0}, {0x3003U, 1.0},
        {kPedalOne, 0.75}, {kPedalTwo, 0.625},
        {0x5000U, preset_oracle::canonical[1]}, {0x5001U, preset_oracle::canonical[9]}});
    check(values.size() == 47, "independent native mapping fixture is not 47 parameters");
    for (auto it = values.rbegin(); it != values.rend(); ++it) {
        all.add_queue(it->first).points = {{0, 0.0}, {0, it->second}};
    }
    restore(session.engine, expected);
    (void)session.process(0, nullptr, {}, &all, "all 47 actual native parameter targets");
    (void)session.process(257);

    for (const auto id : {0x1012U, kPedalOne, kPedalTwo}) {
        for (std::uint8_t step = 1; step <= 8; ++step) {
            const double threshold = static_cast<double>(2 * step - 1) / 16.0;
            const std::array<std::pair<double, double>, 3> cases{{
                {std::nextafter(threshold, 0.0), static_cast<double>(step - 1)},
                {threshold, static_cast<double>(step)},
                {std::nextafter(threshold, 1.0), static_cast<double>(step)}}};
            for (const auto& [normalized, plain] : cases) {
                ParameterChanges point;
                point.add_queue(id).points = {{0, normalized}};
                const Event event = id == 0x1012U
                    ? Event{0, EventType::BankDrawbar, Manual::Upper, 11, plain}
                    : Event{0, EventType::PedalDrawbar, Manual::Lower,
                            static_cast<std::uint8_t>(id - kPedalOne), plain};
                const std::array<Event, 1> one{{event}};
                (void)session.process(0, nullptr, one, &point, "native drawbar threshold");
                (void)session.process(1);
                ++stats.threshold_cases;
            }
        }
    }
    for (const auto id : {kUpperSelector, kLowerSelector, 0x3000U, 0x3001U, 0x3002U, 0x3003U}) {
        const std::array<std::pair<double, double>, 3> cases{{
            {std::nextafter(0.5, 0.0), 0.0}, {0.5, 1.0}, {std::nextafter(0.5, 1.0), 1.0}}};
        for (const auto& [normalized, plain] : cases) {
            ParameterChanges point;
            point.add_queue(id).points = {{0, normalized}};
            Event event{0, EventType::Percussion, Manual::Upper,
                        static_cast<std::uint8_t>(id >= 0x3000U ? id - 0x3000U : 0), plain};
            if (id == kUpperSelector || id == kLowerSelector) {
                event = {0, EventType::SelectBank,
                         id == kUpperSelector ? Manual::Upper : Manual::Lower, 0, plain};
            }
            const std::array<Event, 1> one{{event}};
            (void)session.process(0, nullptr, one, &point, "native Boolean threshold");
            ++stats.threshold_cases;
        }
    }
    ParameterChanges signed_zero;
    signed_zero.add_queue(kExpression).points = {{0, -0.0}};
    const std::array<Event, 1> zero{{expression(-0.0)}};
    (void)session.process(0, nullptr, zero, &signed_zero, "native expression signed zero");
}

void partition_curves(const std::string& bundle, const RuntimeProfile& profile, double rate) {
    const std::array<std::vector<std::uint32_t>, 3> partitions{{
        {128}, {1, 7, 13, 29, 78}, {17, 31, 2, 63, 15}}};
    std::vector<float> whole;
    for (const auto& partition : partitions) {
        auto controls = registration();
        controls.expression = 0.125;
        ReferenceSession session(bundle, profile, rate, controls);
        EventList notes;
        notes.events = {note_on(0, 60, 0, 0, 1), note_on(2, 48, 0, 2, 3)};
        const std::array<Event, 2> initial{{key(0, Manual::Upper, 60, true), pedal(0, 13, true)}};
        (void)session.process(257, &notes, initial);
        std::vector<float> joined;
        std::uint32_t start = 0;
        for (const auto count : partition) {
            ParameterChanges curve;
            curve.add_queue(kExpression).points = {{static_cast<int32>(count),
                0.125 + static_cast<double>(start + count + 1) / 512.0}};
            const auto output = session.sampled(count, nullptr, curve, [start](std::uint32_t i) {
                return std::vector<Event>{expression(0.125 + static_cast<double>(start + i + 1) / 512.0)};
            }, "partitioned closed-form boundary ramp");
            joined.insert(joined.end(), output.begin(), output.end());
            start += count;
        }
        check(start == 128, "partition fixture does not cover 128 frames");
        if (whole.empty()) whole = joined;
        else {
            for (std::size_t i = 0; i < whole.size(); ++i) sample_equal(joined[i], whole[i], "native partition identity");
        }
        const std::array<Event, 1> carried{{expression(0.125 + 129.0 / 512.0)}};
        (void)session.process(0, nullptr, carried, nullptr, "final partition endpoint flush");
        (void)session.process(0);
        (void)session.process(19);
        ++stats.partition_cases;
    }
}

std::string legacy_text(int version) {
    check(version >= 1 && version <= 3, "legacy fixture version");
    std::string text = "B3CONTROLS" + std::to_string(version) + "\nexpression 0.625\n";
    if (version >= 2) text += "percussion enabled 1 harmonic third volume soft decay fast\n";
    if (version == 3) text += "pedal drawbars 8 7\n";
    text += "manual upper selected B route_enabled 0\n"
        "bank A 0 0 0 0 0 0 0 0 0\nbank B 0 0 4 0 0 0 0 0 0\n"
        "manual lower selected B route_enabled 1\n"
        "bank A 0 0 0 0 0 0 0 0 0\nbank B 0 0 3 0 0 0 0 0 0\nend\n";
    return text;
}

void active_state(const std::string& bundle, const RuntimeProfile& profile, double rate) {
    ReferenceSession session(bundle, profile, rate);
    EventList held;
    held.events = {note_on(0, 96, 0, 0, 1), note_on(1, 48, 0, 1, 2), note_on(2, 48, 0, 2, 3)};
    const std::array<Event, 3> initial{{key(0, Manual::Upper, 96, true),
        key(0, Manual::Lower, 48, true), pedal(0, 13, true)}};
    (void)session.process(384, &held, initial);
    std::array<ControlSnapshot, 4> queued{};
    for (std::size_t i = 0; i < queued.size(); ++i) {
        queued[i] = registration();
        queued[i].expression = 0.125 + static_cast<double>(i) / 8.0;
        queued[i].pedal_drawbars = {static_cast<std::uint8_t>(i + 1), 1};
        queued[i].route_enabled[1] = i != 3;
        queued[i].fixed_registrations = {static_cast<FixedRegistration>(i + 1),
                                          static_cast<FixedRegistration>(9 - i)};
        check(session.plugin.load_state(snapshot_text(queued[i])) == Steinberg::kResultOk, "active queued load failed");
        same_controls(saved(session.plugin), queued[i], "newest pending state save");
    }
    auto fifth = registration();
    fifth.expression = 0.875;
    check(session.plugin.load_state(snapshot_text(fifth)) != Steinberg::kResultOk, "fifth pending state accepted");
    ++stats.rejected_state_loads;
    check(session.plugin.load_state("B3CONTROLS3\ninvalid\n") != Steinberg::kResultOk, "malformed active state accepted");
    ++stats.rejected_state_loads;
    reset_block(session.block, 16);
    session.block.data.symbolicSampleSize = sv::kSample64;
    native_call(session.plugin, session.block.data, false, "state queue survives bad callback");
    same_controls(saved(session.plugin), queued.back(), "failed callback pending save");
    check(session.plugin.load_state(snapshot_text(fifth)) != Steinberg::kResultOk, "failed callback consumed queue");
    ++stats.rejected_state_loads;

    const auto before = session.engine.frame_clock();
    for (const auto& controls : queued) restore(session.engine, controls);
    check(session.engine.frame_clock() == before && session.engine.active_key_count() == 2 &&
          session.engine.active_pedal_count() == 1, "reference control restoration reset musical history");
    ParameterChanges after_load;
    after_load.add_queue(kExpression).points = {{15, 0.75}};
    (void)session.sampled(16, nullptr, after_load, [](std::uint32_t i) {
        return std::vector<Event>{expression(0.5 + static_cast<double>(i + 1) / 64.0)};
    }, "active restores retain held notes/contact/percussion histories");

    for (const int version : {3, 2, 1}) {
        auto legacy = registration();
        legacy.route_enabled = {false, true};
        legacy.pedal_drawbars = {8, 7}; // Only state3 supplies these fields.
        legacy.percussion = {true, PercussionHarmonic::Third, PercussionVolume::Soft, PercussionDecay::Fast};
        const auto text = legacy_text(version);
        auto migrated = legacy;
        if (version < 3) migrated.pedal_drawbars = {0, 0};
        if (version == 1) migrated.percussion = {};
        check(session.plugin.load_state(text) == Steinberg::kResultOk, "native legacy state load failed");
        same_controls(saved(session.plugin), migrated, "pending migrated state");
        restore(session.engine, migrated);
        (void)session.process(64, nullptr, {}, nullptr, "active legacy migration");
        auto unmuted = migrated;
        unmuted.pedal_drawbars = {3, 2};
        check(session.plugin.load_state(snapshot_text(unmuted)) == Steinberg::kResultOk, "post-migration pedal restore failed");
        restore(session.engine, unmuted);
        (void)session.process(67, nullptr, {}, nullptr, "held pedal survives muted migration");
    }

    // No intervening UI save: publication must not stop when a reader is absent.
    for (std::uint32_t i = 0; i < 32; ++i) {
        const double value = i % 2 == 0 ? 0.25 : 0.75;
        ParameterChanges point;
        point.add_queue(kExpression).points = {{0, value}};
        reset_block(session.block, 1, nullptr, &point);
        native_call(session.plugin, session.block.data, true, "publication without UI reads");
        const std::array<Event, 1> event{{expression(value)}};
        const auto expected = reference_block(session.engine, 1, event);
        compare_audio(session.block, expected, "publication without UI reads");
    }
    same_controls(saved(session.plugin), session.engine.controls_snapshot(), "late UI save sees last automation");
}

void carry_capacity(const std::string& bundle, const RuntimeProfile& profile) {
    auto controls = registration();
    controls.percussion.enabled = false;
    ReferenceSession session(bundle, profile, 48000.0, controls);
    EventList onset;
    onset.events = {note_on(2, 48, 0, 2, 3)};
    const std::array<Event, 1> on{{pedal(0, 13, true)}};
    (void)session.process(64, &onset, on);
    ParameterChanges maximum;
    auto& curve = maximum.add_queue(kExpression);
    curve.points.assign(1024, {1, 0.5});
    const std::array<Event, 1> current{{expression(0.5625)}};
    (void)session.process(1, nullptr, current, &maximum, "1024 raw endpoint records retained");
    EventList release;
    release.events = {note_off(2, 48, 0, 2, 3)};
    reset_block(session.block, 1, &release);
    native_call(session.plugin, session.block.data, false, "carry plus one rejects without losing release");
    check(session.block.left[0] == kSentinel && session.block.bus.silenceFlags == kFlagSentinel,
          "rejected carry overflow wrote output");
    const std::array<Event, 1> endpoint{{expression(0.5)}};
    (void)session.process(1, nullptr, endpoint, nullptr, "full retained carry consumes once");
    const std::array<Event, 1> off{{pedal(0, 13, false)}};
    (void)session.process(1, &release, off, nullptr, "deferred caller release can be retried");
    (void)session.process(17);
    onset.events = {note_on(2, 50, 0, 2, 44)};
    const std::array<Event, 1> new_on{{pedal(0, 15, true)}};
    (void)session.process(19, &onset, new_on);

    EventList filtered;
    filtered.events.assign(1024, note_on(0, 35));
    (void)session.process(1, &filtered, {}, nullptr, "1024 valid filtered records still admitted");
    filtered.events.push_back(note_off(2, 50, 0, 2, 44));
    reset_block(session.block, 1, &filtered);
    native_call(session.plugin, session.block.data, false, "1025 native records reject before dropping release");
    (void)session.process(29, nullptr, {}, nullptr, "filtered over-capacity failure preserves held pedal");
    filtered.events.erase(filtered.events.begin());
    const std::array<Event, 1> final_off{{pedal(0, 15, false)}};
    (void)session.process(1, &filtered, final_off, nullptr, "1023 filtered records plus supported release");

    EventList dense;
    std::vector<Event> dense_physical;
    for (std::size_t i = 0; i < 512; ++i) {
        dense.events.push_back(note_on(2, 36, 0, 15));
        dense.events.push_back(note_off(2, 36, 0, 15));
        dense_physical.push_back(pedal(0, 1, true));
        dense_physical.push_back(pedal(0, 1, false));
    }
    (void)session.process(1, &dense, dense_physical, nullptr, "1024 same-sample physical transitions");
    (void)session.process(31);
}

void full_ownership(const std::string& bundle, const RuntimeProfile& profile) {
    ControlSnapshot controls{};
    controls.selected_banks = {DrawbarBank::B, DrawbarBank::B};
    controls.drawbars[0][1][2] = 1;
    controls.drawbars[1][1][2] = 1;
    controls.pedal_drawbars = {1, 1};
    controls.expression = 0.125;
    ReferenceSession session(bundle, profile, 48000.0, controls);
    EventList onsets;
    std::vector<Event> physical;
    std::array<std::size_t, 122> manual_counts{};
    std::array<std::size_t, 25> pedal_counts{};
    for (std::size_t i = 0; i < 256; ++i) {
        const auto slot = i % 122;
        const auto bus = static_cast<int32>(slot / 61);
        const auto pitch = static_cast<int16>(36 + slot % 61);
        onsets.events.push_back(note_on(bus, pitch, 0, static_cast<int16>(i % 16), static_cast<int32>(i)));
        if (manual_counts[slot]++ == 0) physical.push_back(key(0, bus == 0 ? Manual::Upper : Manual::Lower,
                                                            static_cast<std::uint8_t>(pitch), true));
    }
    for (std::size_t i = 0; i < 256; ++i) {
        const auto slot = i % 25;
        onsets.events.push_back(note_on(2, static_cast<int16>(36 + slot), 0,
                                       static_cast<int16>(i % 16), static_cast<int32>(i)));
        if (pedal_counts[slot]++ == 0) physical.push_back(pedal(0, static_cast<std::uint8_t>(slot + 1), true));
    }
    check(physical.size() == 147, "full-capacity reference did not select all physical targets");
    (void)session.process(512, &onsets, physical, nullptr, "256 manual plus 256 pedal owners");
    for (const int32 bus : {0, 2}) {
        EventList overflow;
        overflow.events = {note_on(bus, 36, 0, 0, 1000)};
        reset_block(session.block, 32, &overflow);
        native_call(session.plugin, session.block.data, false, "257th native owner rejects");
        (void)session.process(29, nullptr, {}, nullptr, "owner capacity preserves future audio");
    }
    for (std::size_t i = 0; i < 4; ++i) {
        auto pending = controls;
        pending.expression = static_cast<double>(i + 1) / 16.0;
        check(session.plugin.load_state(snapshot_text(pending)) == Steinberg::kResultOk,
              "full-owner pending state failed");
        restore(session.engine, pending);
    }
    (void)session.process(65, nullptr, {}, nullptr, "four queued restores with 512 live owners");
    EventList releases;
    physical.clear();
    for (std::size_t i = 0; i < 256; ++i) {
        const auto slot = i % 122;
        const auto bus = static_cast<int32>(slot / 61);
        const auto pitch = static_cast<int16>(36 + slot % 61);
        releases.events.push_back(note_off(bus, pitch, 0, static_cast<int16>(i % 16), static_cast<int32>(i)));
        if (--manual_counts[slot] == 0) physical.push_back(key(0, bus == 0 ? Manual::Upper : Manual::Lower,
                                                            static_cast<std::uint8_t>(pitch), false));
    }
    for (std::size_t i = 0; i < 256; ++i) {
        const auto slot = i % 25;
        releases.events.push_back(note_off(2, static_cast<int16>(36 + slot), 0,
                                          static_cast<int16>(i % 16), static_cast<int32>(i)));
        if (--pedal_counts[slot] == 0) physical.push_back(pedal(0, static_cast<std::uint8_t>(slot + 1), false));
    }
    check(physical.size() == 147, "full-capacity release schedule does not cover every target");
    (void)session.process(1024, &releases, physical, nullptr, "all 512 final owner releases");
    (void)session.process(257);
}

struct BadInput {
    StereoBlock block{1030};
    EventList notes{};
    ParameterChanges parameters{};
    BadInput() {
        notes.events = {note_off(1, 48, 0, 1, 202), note_on(0, 67, 1, 0, 999)};
        parameters.add_queue(kExpression).points = {{0, 0.125}, {31, 0.875}};
        reset_block(block, 32, &notes, &parameters);
    }
};

using Mutation = std::function<void(BadInput&)>;

void compare_native_blocks(const StereoBlock& left, const StereoBlock& right,
                           std::size_t frames, std::string_view label,
                           bool after_rejection = false) {
    for (std::size_t i = 0; i < frames; ++i) {
        sample_equal(left.left[i], right.left[i], label);
        sample_equal(left.right[i], right.right[i], label);
        if (after_rejection) stats.future_audio_samples += 2;
        else stats.paired_setup_channel_samples += 2;
    }
    check(left.bus.silenceFlags == right.bus.silenceFlags, "paired native silence flags differ");
}

void rejection_case(const std::string& bundle, std::string_view name, const Mutation& mutate) {
    NativePlugin subject(bundle);
    NativePlugin control(bundle);
    subject.start(48000.0, 1024);
    control.start(48000.0, 1024);
    StereoBlock actual(1030);
    StereoBlock expected(1030);
    for (auto* instance : {&subject, &control}) {
        check(instance->load_state(snapshot_text(registration())) == Steinberg::kResultOk, "rollback initial state failed");
    }
    EventList held;
    held.events = {note_on(0, 96, 0, 0, 101), note_on(1, 48, 0, 1, 202), note_on(2, 48, 0, 2, 303)};
    reset_block(actual, 512, &held);
    reset_block(expected, 512, &held);
    native_call(subject, actual.data, true, "rollback setup");
    native_call(control, expected.data, true, "rollback control setup");
    compare_native_blocks(actual, expected, 512, "rollback initial audio");
    ParameterChanges curve;
    curve.add_queue(kExpression).points = {{8, 0.75}};
    EventList boundary;
    boundary.events = {note_off(0, 96, 8, 0, 101), note_on(2, 49, 8, 2, 404)};
    reset_block(actual, 8, &boundary, &curve);
    reset_block(expected, 8, &boundary, &curve);
    native_call(subject, actual.data, true, "rollback retained endpoint setup");
    native_call(control, expected.data, true, "rollback control retained endpoint setup");
    compare_native_blocks(actual, expected, 8, "rollback endpoint audio");
    ControlSnapshot newest{};
    for (std::size_t i = 0; i < 4; ++i) {
        newest = registration();
        newest.expression = 0.25 + static_cast<double>(i) / 8.0;
        newest.drawbars[0][1][2] = static_cast<std::uint8_t>(i + 1);
        newest.fixed_registrations = {static_cast<FixedRegistration>(i + 1), FixedRegistration::A};
        newest.route_enabled[1] = false;
        for (auto* instance : {&subject, &control}) {
            check(instance->load_state(snapshot_text(newest)) == Steinberg::kResultOk, "rollback queued restore failed");
        }
    }
    BadInput bad;
    mutate(bad);
    native_call(subject, bad.block.data, false, name);
    check(std::all_of(bad.block.left.begin(), bad.block.left.end(), [](float v) { return v == kSentinel; }) &&
          std::all_of(bad.block.right.begin(), bad.block.right.end(), [](float v) { return v == kSentinel; }),
          std::string(name) + ": rejection wrote sample memory");
    check(bad.block.bus.silenceFlags == kFlagSentinel, std::string(name) + ": rejection wrote flags");
    same_controls(saved(subject), newest, "rejected callback keeps newest pending state");
    auto fifth = newest;
    fifth.expression = 0.9;
    check(subject.load_state(snapshot_text(fifth)) != Steinberg::kResultOk,
          std::string(name) + ": rejection consumed state queue");
    ++stats.rejected_state_loads;
    reset_block(actual, 49);
    reset_block(expected, 49);
    native_call(subject, actual.data, true, "after rejected callback");
    native_call(control, expected.data, true, "untouched counterfactual callback");
    compare_native_blocks(actual, expected, 49, name, true);
    same_controls(saved(subject), saved(control), "post-rejection published controls");
    EventList probe;
    probe.events = {note_off(1, 48, 0, 1, 202), note_off(2, 48, 0, 2, 303),
                    note_off(2, 49, 0, 2, 404), note_on(0, 67, 1, 0, 555)};
    reset_block(actual, 127, &probe);
    reset_block(expected, 127, &probe);
    native_call(subject, actual.data, true, "post-rejection owner probe");
    native_call(control, expected.data, true, "counterfactual owner probe");
    compare_native_blocks(actual, expected, 127, name, true);
    probe.events = {note_off(0, 67, 0, 0, 555)};
    reset_block(actual, 513, &probe);
    reset_block(expected, 513, &probe);
    native_call(subject, actual.data, true, "post-rejection hidden-owner release probe");
    native_call(control, expected.data, true, "counterfactual hidden-owner release probe");
    compare_native_blocks(actual, expected, 513, name, true);
    ++stats.rollback_cases;
}

void native_rejections(const std::string& bundle) {
    const double nan = std::numeric_limits<double>::quiet_NaN();
    const float fnan = std::numeric_limits<float>::quiet_NaN();
    const std::vector<std::pair<std::string, Mutation>> cases{
        {"negative audio input count", [](BadInput& b) { b.block.data.numInputs = -1; }},
        {"unadvertised audio input", [](BadInput& b) { b.block.data.numInputs = 1; }},
        {"negative output count", [](BadInput& b) { b.block.data.numOutputs = -1; }},
        {"too many output buses", [](BadInput& b) { b.block.data.numOutputs = 2; }},
        {"missing output bus", [](BadInput& b) { b.block.data.outputs = nullptr; }},
        {"negative channel count", [](BadInput& b) { b.block.bus.numChannels = -1; }},
        {"mono output mismatch", [](BadInput& b) { b.block.bus.numChannels = 1; }},
        {"positive zero-channel output", [](BadInput& b) { b.block.bus.numChannels = 0; }},
        {"missing channel array", [](BadInput& b) { b.block.bus.channelBuffers32 = nullptr; }},
        {"missing left channel", [](BadInput& b) { b.block.channels[0] = nullptr; }},
        {"missing right channel", [](BadInput& b) { b.block.channels[1] = nullptr; }},
        {"partial stereo overlap", [](BadInput& b) { b.block.channels[1] = b.block.left.data() + 1; }},
        {"misaligned sample span", [](BadInput& b) {
            b.block.channels[0] = reinterpret_cast<float*>(reinterpret_cast<unsigned char*>(b.block.left.data()) + 1);
        }},
        {"float64 processing", [](BadInput& b) { b.block.data.symbolicSampleSize = sv::kSample64; }},
        {"unknown sample precision", [](BadInput& b) { b.block.data.symbolicSampleSize = -1; }},
        {"negative frame count", [](BadInput& b) { b.block.data.numSamples = -1; }},
        {"maximum plus one", [](BadInput& b) { b.block.data.numSamples = 1025; }},
        {"unknown process mode", [](BadInput& b) { b.block.data.processMode = -1; }},
        {"unstopped offline transition", [](BadInput& b) { b.block.data.processMode = sv::kOffline; }},
        {"negative event count", [](BadInput& b) { b.notes.count_override = -1; }},
        {"native event count over limit", [](BadInput& b) { b.notes.count_override = 1025; }},
        {"negative queue count", [](BadInput& b) { b.parameters.count_override = -1; }},
        {"too many parameter queues", [](BadInput& b) { b.parameters.count_override = 48; }},
        {"missing parameter queue", [](BadInput& b) { b.parameters.null_index = 0; }},
        {"unknown parameter ID", [](BadInput& b) { b.parameters.queues[0]->id = 0xDEADU; }},
        {"first ID after new selectors", [](BadInput& b) { b.parameters.queues[0]->id = 0x5002U; }},
        {"late invalid upper preset", [nan](BadInput& b) {
            b.parameters.add_queue(0x5000U).points = {{0, preset_oracle::canonical[1]}, {31, nan}};
        }},
        {"late invalid lower preset", [](BadInput& b) {
            b.parameters.add_queue(0x5001U).points = {{0, preset_oracle::canonical[9]}, {31, 1.01}};
        }},
        {"duplicate parameter queue", [](BadInput& b) { b.parameters.add_queue(kExpression).points = {{0, 0.5}}; }},
        {"duplicate empty queue", [](BadInput& b) { b.parameters.queues[0]->points.clear(); (void)b.parameters.add_queue(kExpression); }},
        {"negative point count", [](BadInput& b) { b.parameters.queues[0]->count_override = -1; }},
        {"too many raw points", [](BadInput& b) { b.parameters.queues[0]->count_override = 1025; }},
        {"failed late queue accessor", [](BadInput& b) { b.parameters.queues[0]->fail_index = 1; }},
        {"nonfinite late queue value", [nan](BadInput& b) { b.parameters.queues[0]->points[1].normalized = nan; }},
        {"negative normalized value", [](BadInput& b) { b.parameters.queues[0]->points[1].normalized = -0.01; }},
        {"normalized value over one", [](BadInput& b) { b.parameters.queues[0]->points[1].normalized = 1.01; }},
        {"negative point offset", [](BadInput& b) { b.parameters.queues[0]->points[0].offset = -1; }},
        {"point after block boundary", [](BadInput& b) { b.parameters.queues[0]->points[1].offset = 33; }},
        {"decreasing queue offsets", [](BadInput& b) { b.parameters.queues[0]->points = {{10, 0.25}, {9, 0.5}}; }},
        {"failed late event accessor", [](BadInput& b) { b.notes.fail_index = 1; }},
        {"negative native bus", [](BadInput& b) { b.notes.events.back().busIndex = -1; }},
        {"invalid native bus", [](BadInput& b) { b.notes.events.back().busIndex = 3; }},
        {"negative note channel", [](BadInput& b) { b.notes.events.back().noteOn.channel = -1; }},
        {"channel outside 16", [](BadInput& b) { b.notes.events.back().noteOn.channel = 16; }},
        {"negative MIDI pitch", [](BadInput& b) { b.notes.events.back().noteOn.pitch = -1; }},
        {"MIDI pitch over 127", [](BadInput& b) { b.notes.events.back().noteOn.pitch = 128; }},
        {"invalid note identity", [](BadInput& b) { b.notes.events.back().noteOn.noteId = -2; }},
        {"nonfinite velocity", [fnan](BadInput& b) { b.notes.events.back().noteOn.velocity = fnan; }},
        {"negative velocity", [](BadInput& b) { b.notes.events.back().noteOn.velocity = -0.1F; }},
        {"velocity over one", [](BadInput& b) { b.notes.events.back().noteOn.velocity = 1.1F; }},
        {"nonfinite note tuning", [fnan](BadInput& b) { b.notes.events.back().noteOn.tuning = fnan; }},
        {"nonfinite project position", [nan](BadInput& b) { b.notes.events.back().ppqPosition = nan; }},
        {"negative event offset", [](BadInput& b) { b.notes.events.front().sampleOffset = -1; }},
        {"event beyond boundary", [](BadInput& b) { b.notes.events.back().sampleOffset = 33; }},
        {"decreasing event offsets", [](BadInput& b) { b.notes.events.front().sampleOffset = 10; }},
        {"malformed filtered pitch still rejects", [fnan](BadInput& b) { b.notes.events.back().noteOn.pitch = 0; b.notes.events.back().noteOn.velocity = fnan; }},
        {"unknown native event type", [](BadInput& b) { b.notes.events.back().type = 1234; }},
        {"output-only native MIDI event", [](BadInput& b) { b.notes.events.back().type = sv::Event::kLegacyMIDICCOutEvent; }},
        {"malformed ignored data pointer", [](BadInput& b) { auto& event = b.notes.events.back(); event.type = sv::Event::kDataEvent; event.data = {1, sv::DataEvent::kMidiSysEx, nullptr}; }},
        {"late future identified-note conflict", [](BadInput& b) { b.notes.events.back() = note_on(2, 50, 32, 2, 303); }},
        {"filtered records cannot evade carry budget", [](BadInput& b) { b.parameters.queues.clear(); b.notes.events.assign(1022, note_on(0, 35)); }},
        {"point records cannot evade carry budget", [](BadInput& b) { b.notes.events.clear(); b.parameters.queues[0]->points.assign(1022, {0, 0.5}); }}
    };
    for (const auto& [name, mutate] : cases) rejection_case(bundle, name, mutate);
}

} // namespace

int main(int argc, char* argv[]) {
    try {
        if (argc != 3) throw std::runtime_error("usage: test_native_behavior BUNDLE COMPILED_PROFILE");
        RuntimeProfile profile{};
        std::string error;
        check(load_runtime_profile_file(argv[2], profile, error), "could not load independent profile: " + error);
        const std::string bundle(argv[1]);
        for (const double rate : {44100.0, 48000.0, 96000.0}) {
            isolated_divisions(bundle, profile, rate);
            musical_ownership(bundle, profile, rate);
            output_and_lifecycle(bundle, profile, rate);
            boundary_automation(bundle, profile, rate);
            partition_curves(bundle, profile, rate);
            active_state(bundle, profile, rate);
        }
        control_mapping_and_cancel(bundle, profile);
        carry_capacity(bundle, profile);
        full_ownership(bundle, profile);
        native_rejections(bundle);
        check(stats.audible_samples > 10000 && stats.peak > 0.001 && stats.peak < 1.0,
              "audio evidence was silent, trivial or clipped");
        std::cout << "native behavior checks=" << stats.checks
                  << " accepted_callbacks=" << stats.accepted_callbacks
                  << " rejected_callbacks=" << stats.rejected_callbacks
                  << " zero_callbacks=" << stats.zero_callbacks
                  << " direct_reference_frames=" << stats.direct_reference_frames
                  << " exact_channel_samples=" << stats.exact_channel_samples
                  << " paired_setup_channel_samples=" << stats.paired_setup_channel_samples
                  << " future_audio_samples=" << stats.future_audio_samples
                  << " audible_samples=" << stats.audible_samples
                  << " state_reads=" << stats.state_reads
                  << " rejected_state_loads=" << stats.rejected_state_loads
                  << " threshold_cases=" << stats.threshold_cases
                  << " rollback_cases=" << stats.rollback_cases
                  << " partition_cases=" << stats.partition_cases
                  << " rate_changes=" << stats.rate_changes
                  << " isolated_division_cases=" << stats.isolated_division_cases
                  << " division_peaks=" << stats.division_peaks[0] << ','
                  << stats.division_peaks[1] << ',' << stats.division_peaks[2]
                  << " peak=" << stats.peak
                  << " checksum=" << std::hex << stats.checksum << std::dec << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "native behavior failure: " << error.what() << '\n';
        return 1;
    }
}
