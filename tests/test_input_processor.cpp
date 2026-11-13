#include "TestSupport.h"
#include "hammond/InputProcessor.h"

#include <algorithm>
#include <array>
#include <bit>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <span>
#include <vector>

namespace {
using namespace hammond;

std::uint64_t wrapper_calls = 0;
std::uint64_t rejected_calls = 0;
std::uint64_t future_probes = 0;
std::uint64_t compared_systems = 0;
std::uint64_t reference_events = 0;
std::uint64_t compared_samples = 0;
std::uint64_t partition_variants = 0;

struct System {
    Engine engine;
    NoteOwnership owners;
    double rate{48000.0};
    ContactMode mode{ContactMode::Ideal};
    std::uint32_t maximum{4096};
};

HostNoteEvent on(std::uint32_t frame, std::uint8_t bus, std::uint8_t channel,
                 std::uint8_t note, std::int32_t id, std::uint8_t velocity = 100) {
    return {frame, HostNoteKind::On, bus, channel, note, velocity, id};
}

HostNoteEvent off(std::uint32_t frame, std::uint8_t bus, std::uint8_t channel,
                  std::uint8_t note, std::int32_t id) {
    return {frame, HostNoteKind::Off, bus, channel, note, 0, id};
}

HostNoteEvent channel_off(std::uint32_t frame, std::uint8_t bus,
                          std::uint8_t channel) {
    return {frame, HostNoteKind::AllNotesOff, bus, channel, 0, 0, -1};
}

Event physical(std::uint32_t frame, Manual manual, std::uint8_t note,
               bool down, double velocity = 100.0) {
    return {frame, down ? EventType::NoteOn : EventType::NoteOff,
            manual, note, down ? velocity : 0.0};
}

void same_float(float a, float b) {
    CHECK(std::bit_cast<std::uint32_t>(a) == std::bit_cast<std::uint32_t>(b));
}

void same_audio(std::span<const float> a, std::span<const float> b) {
    CHECK(a.size() == b.size());
    for (std::size_t i = 0; i < a.size(); ++i) {
        same_float(a[i], b[i]);
    }
    compared_samples += a.size();
}

std::vector<float> sentinels(std::size_t count) {
    std::vector<float> result(count);
    for (std::size_t i = 0; i < count; ++i) {
        // Exact finite binary values, with a negative zero sentinel as well.
        result[i] = i == 0 ? -0.0F : 0.25F + static_cast<float>(i % 128) / 256.0F;
    }
    return result;
}

System prepared(const RuntimeProfile& profile, ContactMode mode, double rate,
                std::uint32_t maximum = 4096, std::uint64_t initial_frame = 17) {
    System result;
    result.rate = rate;
    result.mode = mode;
    result.maximum = maximum;
    auto model = mode == ContactMode::Ideal ? make_legacy_console_model()
                                           : make_nominal_console_model();
    CHECK(result.engine.prepare(profile, ProcessSpec{rate, maximum, 130151, initial_frame},
                                model) == Status::Ok);
    auto controls = result.engine.controls_snapshot();
    controls.drawbars[0][1][2] = 8;
    controls.drawbars[0][1][8] = 5;
    controls.drawbars[1][1][2] = 7;
    controls.drawbars[1][1][4] = 3;
    controls.drawbars[0][0][0] = 6;
    controls.drawbars[1][0][2] = 5;
    controls.expression = 0.375;
    controls.percussion = {true, PercussionHarmonic::Second,
                           PercussionVolume::Normal, PercussionDecay::Fast};
    CHECK(result.engine.restore_controls(controls));
    return result;
}

void same_engine(const Engine& actual, const Engine& expected) {
    CHECK(actual.prepared() == expected.prepared());
    CHECK(actual.frame_clock() == expected.frame_clock());
    CHECK(actual.controls_snapshot() == expected.controls_snapshot());
    CHECK(std::bit_cast<std::uint64_t>(actual.expression()) ==
          std::bit_cast<std::uint64_t>(expected.expression()));
    CHECK(actual.contact_mode() == expected.contact_mode());
    CHECK(actual.active_key_count() == expected.active_key_count());
    CHECK(actual.percussion_diagnostics() == expected.percussion_diagnostics());
    for (const Manual manual : {Manual::Upper, Manual::Lower}) {
        CHECK(actual.active_key_count(manual) == expected.active_key_count(manual));
        for (std::uint32_t note = 36; note <= 96; ++note) {
            CHECK(actual.key_down(manual, note) == expected.key_down(manual, note));
            ContactKeySnapshot a{-1.0, -2.0, {}}, b = a;
            CHECK(actual.contact_snapshot(manual, note, a) ==
                  expected.contact_snapshot(manual, note, b));
            CHECK(a == b);
            CHECK(std::bit_cast<std::uint64_t>(a.position) ==
                  std::bit_cast<std::uint64_t>(b.position));
            CHECK(std::bit_cast<std::uint64_t>(a.target) ==
                  std::bit_cast<std::uint64_t>(b.target));
        }
    }
    for (std::uint32_t number = 1; number <= 91; ++number) {
        double a = -3.0, b = a;
        const auto id = static_cast<ToneId>(number);
        CHECK(actual.source_phase_turns(id, a) == expected.source_phase_turns(id, b));
        CHECK(std::bit_cast<std::uint64_t>(a) == std::bit_cast<std::uint64_t>(b));
    }
}

void same_system(const System& actual, const System& expected) {
    CHECK(actual.owners == expected.owners);
    same_engine(actual.engine, expected.engine);
    ++compared_systems;
}

InputProcessResult success(System& system, std::uint32_t frames, std::span<float> output,
                           std::span<const HostNoteEvent> input,
                           std::uint32_t expected_physical) {
    const auto before = std::vector<float>(output.begin(), output.end());
    const auto clock = system.engine.frame_clock();
    const auto result = process_owned_notes(system.engine, system.owners, frames, output, input);
    ++wrapper_calls;
    CHECK(result.status == Status::Ok);
    CHECK(result.ok());
    CHECK(static_cast<bool>(result));
    CHECK(result.host_events_consumed == input.size());
    CHECK(result.physical_events_consumed == expected_physical);
    CHECK(system.engine.frame_clock() == clock + frames);
    if (!output.empty()) {
        for (std::size_t i = 0; i < frames; ++i) {
            CHECK(std::isfinite(output[i]));
        }
        for (std::size_t i = frames; i < output.size(); ++i) {
            same_float(output[i], before[i]);
        }
    }
    return result;
}

void known_reference(Engine& engine, std::uint32_t frames, std::span<float> output,
                     std::span<const Event> events) {
    const auto result = engine.process(frames, output, events);
    CHECK(result.status == Status::Ok);
    CHECK(result.events_consumed == events.size());
    reference_events += events.size();
}

void future_equal(System left, System right, const RuntimeProfile& profile) {
    if (!left.engine.prepared()) {
        CHECK(!right.engine.prepared());
        // Coordinated preparation of two empty unprepared systems, never a
        // hidden ownership reset of a running engine.
        CHECK(left.owners.owner_count() == 0);
        CHECK(right.owners.owner_count() == 0);
        left = prepared(profile, ContactMode::LinearTravel, 48000.0);
        right = prepared(profile, ContactMode::LinearTravel, 48000.0);
    }
    CHECK(left.maximum >= 64);
    CHECK(left.engine.frame_clock() <= std::numeric_limits<std::uint64_t>::max() - 64);
    const std::array input{channel_off(0, 0, 0), channel_off(0, 1, 0),
                           on(3, 0, 0, 65, 9000), on(9, 1, 0, 72, 9001),
                           off(31, 0, 0, 65, 9000)};
    auto a = sentinels(80), b = a;
    // Counts must agree, but no adapter-derived count is used as the behavioral
    // oracle for the rollback: identical future PCM and complete diagnostics are.
    const auto x = process_owned_notes(left.engine, left.owners, 64, a, input);
    const auto y = process_owned_notes(right.engine, right.owners, 64, b, input);
    wrapper_calls += 2;
    CHECK(x.ok() && y.ok());
    CHECK(x.host_events_consumed == input.size());
    CHECK(y.host_events_consumed == input.size());
    CHECK(x.physical_events_consumed == y.physical_events_consumed);
    same_audio(a, b);
    same_system(left, right);
    // Continue far enough for new nominal contacts to make at 96 kHz, so a
    // cached-mix or hidden-trajectory mutation cannot hide behind initial silence.
    // A near-overflow case consumes exactly its remaining legal clock interval.
    std::uint32_t elapsed = 64;
    while (elapsed < 1024 &&
           left.engine.frame_clock() != std::numeric_limits<std::uint64_t>::max()) {
        const auto remaining = std::numeric_limits<std::uint64_t>::max() - left.engine.frame_clock();
        const auto frames = static_cast<std::uint32_t>(
            std::min<std::uint64_t>(64, std::min<std::uint64_t>(1024 - elapsed, remaining)));
        (void)success(left, frames, a, {}, 0);
        (void)success(right, frames, b, {}, 0);
        same_audio(a, b);
        same_system(left, right);
        elapsed += frames;
    }
    ++future_probes;
}

void rejected(System& system, const RuntimeProfile& profile, std::uint32_t frames,
              std::vector<float>& storage, std::size_t exposed,
              std::span<const HostNoteEvent> input, Status expected) {
    const auto before = system;
    const auto original_output = storage;
    CHECK(exposed <= storage.size());
    const auto result = process_owned_notes(system.engine, system.owners, frames,
                                            std::span<float>(storage).first(exposed), input);
    ++wrapper_calls;
    ++rejected_calls;
    CHECK(result.status == expected);
    CHECK(!result.ok());
    CHECK(!static_cast<bool>(result));
    CHECK(result.host_events_consumed == 0);
    CHECK(result.physical_events_consumed == 0);
    same_audio(storage, original_output);
    same_system(system, before);
    future_equal(system, before, profile);
}

void test_engine_admission_rollback(const RuntimeProfile& profile) {
    for (const auto mode : {ContactMode::Ideal, ContactMode::LinearTravel}) {
        for (const auto rate : {44100.0, 48000.0, 96000.0}) {
            auto system = prepared(profile, mode, rate, 128);
            const std::array first{on(0, 0, 0, 69, 10)};
            (void)success(system, 128, {}, first, 1);
            const std::array new_owner{on(0, 1, 0, 74, 11)};
            auto output = sentinels(160);
            rejected(system, profile, 128, output, 127, new_owner, Status::InvalidBuffer);
            rejected(system, profile, 129, output, 160, new_owner, Status::BlockTooLarge);
            rejected(system, profile, 65537, output, 160, new_owner, Status::BlockTooLarge);

            auto overflow = prepared(profile, mode, rate, 1024,
                                      std::numeric_limits<std::uint64_t>::max() - 1000);
            (void)success(overflow, 256, {}, first, 1);
            rejected(overflow, profile, 1024, output, 0, new_owner, Status::TimelineOverflow);
            // Every remaining valid frame can still be consumed, then a flush
            // at the final clock changes ownership without inventing time.
            (void)success(overflow, 744, {}, {}, 0);
            CHECK(overflow.engine.frame_clock() == std::numeric_limits<std::uint64_t>::max());
            const auto charge = overflow.engine.percussion_diagnostics().readiness;
            (void)success(overflow, 0, output, new_owner, 1);
            CHECK(overflow.engine.percussion_diagnostics().readiness == charge);
        }
    }
    System unprepared;
    auto output = sentinels(40);
    const std::array valid{on(0, 0, 0, 60, 1)};
    rejected(unprepared, profile, 32, output, 32, valid, Status::NotPrepared);
    auto bad = valid;
    bad[0].bus = 2;
    rejected(unprepared, profile, 32, output, 32, bad, Status::InvalidEvent);
}

void test_translation_rollback(const RuntimeProfile& profile) {
    for (const auto mode : {ContactMode::Ideal, ContactMode::LinearTravel}) {
        auto system = prepared(profile, mode, 48000.0);
        const std::array first{on(0, 0, 0, 69, 10)};
        (void)success(system, 200, {}, first, 1);
        auto output = sentinels(128);
        const std::array late_conflict{off(0, 0, 0, 69, 10), on(1, 0, 0, 72, 42),
                                       on(2, 0, 0, 73, 42)};
        rejected(system, profile, 64, output, 80, late_conflict, Status::InvalidEvent);
        const std::array unsorted{on(5, 1, 0, 72, 42), off(4, 1, 0, 72, 42)};
        rejected(system, profile, 64, output, 80, unsorted, Status::InvalidEvent);
        const std::array bad_velocity{on(0, 1, 0, 72, 42, 128)};
        rejected(system, profile, 64, output, 80, bad_velocity, Status::InvalidEvent);
        const std::array at_end{on(64, 1, 0, 72, 42)};
        rejected(system, profile, 64, output, 80, at_end, Status::InvalidEvent);
        const std::array bad_flush{on(1, 1, 0, 72, 42)};
        rejected(system, profile, 0, output, 80, bad_flush, Status::InvalidEvent);
        // Translation errors precede the also-invalid short Engine buffer.
        rejected(system, profile, 64, output, 1, late_conflict, Status::InvalidEvent);
        std::vector<HostNoteEvent> excessive(1025, off(0, 0, 0, 60, 999));
        rejected(system, profile, 64, output, 80, excessive, Status::TooManyEvents);

        auto saturated = prepared(profile, mode, 48000.0);
        std::vector<HostNoteEvent> fill;
        for (std::int32_t id = 0; id < 256; ++id) fill.push_back(on(0, 0, 0, 69, id));
        (void)success(saturated, 200, {}, fill, 1);
        CHECK(saturated.owners.owner_count() == 256);
        const std::array overflow{off(0, 0, 0, 69, 0), on(1, 0, 0, 69, 256),
                                  on(2, 0, 0, 69, 257)};
        rejected(saturated, profile, 64, output, 80, overflow, Status::TooManyEvents);

        // Five full two-manual press/release cycles need 1,220 physical events
        // from just 620 host commands. This is a bounded output-capacity failure,
        // not a host-input-count failure or a simultaneous-owner overflow.
        auto expanded = prepared(profile, mode, 48000.0);
        (void)success(expanded, 128, {}, {}, 0);
        std::vector<HostNoteEvent> fanout;
        for (std::uint32_t cycle = 0; cycle < 5; ++cycle) {
            for (std::uint8_t bus = 0; bus < 2; ++bus) {
                for (std::uint8_t note = 36; note <= 96; ++note) {
                    fanout.push_back(on(0, bus, 0, note, static_cast<std::int32_t>(note)));
                }
            }
            fanout.push_back(channel_off(0, 0, 0));
            fanout.push_back(channel_off(0, 1, 0));
        }
        CHECK(fanout.size() == 620);
        rejected(expanded, profile, 0, output, 80, fanout, Status::TooManyEvents);
    }
}

void test_physical_ownership_and_remapping(const RuntimeProfile& profile) {
    for (const auto mode : {ContactMode::Ideal, ContactMode::LinearTravel}) {
        auto system = prepared(profile, mode, 48000.0);
        auto expected = system.engine;
        CHECK(system.owners.set_bus_route(1, Manual::Upper));
        const std::array notes{on(0, 0, 0, 69, 1), on(4, 0, 1, 69, 1, 23),
                               on(8, 1, 0, 69, 1, 127), on(12, 0, 0, 72, 2)};
        const std::array intended{physical(0, Manual::Upper, 69, true),
                                  physical(12, Manual::Upper, 72, true)};
        auto a = sentinels(1100), b = a;
        (void)success(system, 1024, a, notes, 2);
        known_reference(expected, 1024, b, intended);
        same_audio(a, b);
        same_engine(system.engine, expected);
        CHECK(system.owners.owner_count() == 4);
        CHECK(system.engine.active_key_count(Manual::Upper) == 2);
        std::size_t count = 999;
        CHECK(system.owners.owner_count(Manual::Upper, 69, count) && count == 3);

        // Retiring bus0/channel0 releases its C but leaves two A owners intact.
        const std::array release{channel_off(0, 0, 0)};
        const std::array intended_release{physical(0, Manual::Upper, 72, false)};
        (void)success(system, 300, a, release, 1);
        known_reference(expected, 300, b, intended_release);
        same_audio(a, b);
        same_engine(system.engine, expected);
        CHECK(system.engine.key_down(Manual::Upper, 69));
        CHECK(!system.engine.key_down(Manual::Upper, 72));
        CHECK(system.owners.owner_count() == 2);

        // An existing identified owner keeps Upper after bus1 is remapped.
        CHECK(system.owners.set_bus_route(1, Manual::Lower));
        const std::array mapped{on(0, 1, 0, 69, 1), on(0, 1, 0, 69, 7),
                                off(30, 1, 0, 69, 1), off(60, 0, 1, 69, 1)};
        const std::array intended_mapped{physical(0, Manual::Lower, 69, true),
                                         physical(60, Manual::Upper, 69, false)};
        (void)success(system, 700, a, mapped, 2);
        known_reference(expected, 700, b, intended_mapped);
        same_audio(a, b);
        same_engine(system.engine, expected);
        CHECK(!system.engine.key_down(Manual::Upper, 69));
        CHECK(system.engine.key_down(Manual::Lower, 69));
        CHECK(system.owners.owner_count() == 1);
        NoteOwnerSnapshot owner;
        CHECK(system.owners.owner_snapshot(0, owner));
        CHECK((owner == NoteOwnerSnapshot{1, 0, 69, 7, Manual::Lower}));
        const std::array last{channel_off(0, 1, 0)};
        const std::array intended_last{physical(0, Manual::Lower, 69, false)};
        (void)success(system, 800, a, last, 1);
        known_reference(expected, 800, b, intended_last);
        same_audio(a, b);
        same_engine(system.engine, expected);
        CHECK(system.owners.owner_count() == 0);
        CHECK(system.engine.active_key_count() == 0);
    }
}

void test_anonymous_fifo_cross_routes(const RuntimeProfile& profile) {
    for (const auto mode : {ContactMode::Ideal, ContactMode::LinearTravel}) {
        auto system = prepared(profile, mode, 48000.0);
        auto expected = system.engine;
        const std::array first{on(0, 0, 2, 60, -1, 1)};
        const std::array first_expected{physical(0, Manual::Upper, 60, true, 1.0)};
        (void)success(system, 64, {}, first, 1);
        known_reference(expected, 64, {}, first_expected);
        CHECK(system.owners.set_bus_route(0, Manual::Lower));
        const std::array second{on(0, 0, 2, 60, -1, 127), on(0, 0, 2, 60, 9)};
        const std::array second_expected{physical(0, Manual::Lower, 60, true, 127.0)};
        (void)success(system, 64, {}, second, 1);
        known_reference(expected, 64, {}, second_expected);
        const std::array fifo{off(0, 0, 2, 60, -1), on(10, 0, 2, 60, -1, 0),
                              off(20, 0, 2, 60, -1), off(30, 0, 2, 60, 9)};
        const std::array fifo_expected{physical(0, Manual::Upper, 60, false),
                                       physical(30, Manual::Lower, 60, false)};
        auto a = sentinels(1100), b = a;
        (void)success(system, 1024, a, fifo, 2);
        known_reference(expected, 1024, b, fifo_expected);
        same_audio(a, b);
        same_engine(system.engine, expected);
        CHECK(system.owners.owner_count() == 0);
    }
}

void test_zero_time_and_disconnected_output(const RuntimeProfile& profile) {
    for (const auto mode : {ContactMode::Ideal, ContactMode::LinearTravel}) {
        for (const auto rate : {44100.0, 48000.0, 96000.0}) {
            auto audible = prepared(profile, mode, rate);
            auto disconnected = audible;
            const std::array note{on(0, 0, 0, 69, 100)};
            auto output = sentinels(2200);
            (void)success(audible, 2048, output, note, 1);
            (void)success(disconnected, 2048, {}, note, 1);
            same_system(audible, disconnected);
            CHECK(std::any_of(output.begin(), output.begin() + 2048,
                              [](float x) { return x != 0.0F; }));
            CHECK(audible.engine.percussion_diagnostics().routed_detector);
            const auto before = audible;
            const auto charge = audible.engine.percussion_diagnostics().readiness;
            const std::array no_ops{on(0, 0, 0, 69, 100, 12), off(0, 1, 3, 80, 99)};
            (void)success(audible, 0, output, no_ops, 0);
            same_system(audible, before);
            const std::array restart{off(0, 0, 0, 69, 100), on(0, 0, 0, 69, 100)};
            (void)success(audible, 0, output, restart, 2);
            same_system(audible, before);
            CHECK(audible.engine.percussion_diagnostics().readiness == charge);
            auto a = sentinels(100), b = a;
            // A same-offset off/on at the next positive sample is equivalent to
            // keeping a fully depressed key held; exactly one elapsed step occurs.
            (void)success(audible, 1, a, restart, 2);
            (void)success(disconnected, 1, b, {}, 0);
            same_audio(a, b);
            same_system(audible, disconnected);
            const auto tau = make_nominal_percussion_profile().fast_decay_seconds;
            CHECK_NEAR(audible.engine.percussion_diagnostics().readiness,
                       charge * std::exp(-1.0 / (rate * tau)), 2e-15);
            (void)success(audible, 64, a, {}, 0);
            (void)success(disconnected, 64, b, {}, 0);
            same_audio(a, b);
            same_system(audible, disconnected);
        }
    }
}

struct Trace {
    System system;
    std::vector<float> samples;
    std::uint64_t host_count{0};
    std::uint64_t physical_count{0};
};

// A manually authored expected physical timeline. It is not obtained by calling
// translate(), reproducing ownership search, or reading the implementation.
const std::array kHostTimeline{
    on(0, 0, 0, 69, 10), on(0, 0, 1, 69, 10, 1), on(19, 1, 0, 60, 20),
    on(53, 0, 0, 72, 11), on(121, 0, 0, 69, 10, 127), off(122, 0, 0, 69, 10),
    on(191, 0, 2, 76, -1), on(191, 0, 2, 76, -1), off(192, 0, 2, 76, -1),
    channel_off(511, 0, 1), off(512, 0, 0, 72, 11), on(512, 0, 0, 72, 11),
    on(769, 1, 1, 60, 21), channel_off(1023, 1, 0), channel_off(1024, 0, 2),
    off(1301, 0, 0, 72, 11), on(1500, 0, 0, 67, -1), on(1500, 0, 0, 67, -1),
    on(1750, 0, 0, 67, -1, 0), channel_off(2000, 0, 0), channel_off(2000, 1, 1)};
const std::array kPhysicalTimeline{
    physical(0, Manual::Upper, 69, true), physical(19, Manual::Lower, 60, true),
    physical(53, Manual::Upper, 72, true), physical(191, Manual::Upper, 76, true),
    physical(511, Manual::Upper, 69, false), physical(512, Manual::Upper, 72, false),
    physical(512, Manual::Upper, 72, true), physical(1024, Manual::Upper, 76, false),
    physical(1301, Manual::Upper, 72, false), physical(1500, Manual::Upper, 67, true),
    physical(2000, Manual::Upper, 67, false), physical(2000, Manual::Lower, 60, false)};

Trace partitioned(const RuntimeProfile& profile, ContactMode mode, double rate,
                  std::uint32_t block_size, bool boundary_flushes) {
    constexpr std::uint32_t total = 3072;
    Trace trace{prepared(profile, mode, rate), std::vector<float>(total), 0, 0};
    auto reference = trace.system.engine;
    std::vector<float> expected(total);
    std::size_t next_host = 0, next_physical = 0;
    for (std::uint32_t start = 0; start < total;) {
        const auto frames = std::min(block_size, total - start);
        std::vector<HostNoteEvent> host;
        std::vector<Event> physical_events;
        if (boundary_flushes) {
            while (next_host < kHostTimeline.size() && kHostTimeline[next_host].offset == start) {
                auto e = kHostTimeline[next_host++]; e.offset = 0; host.push_back(e);
            }
            while (next_physical < kPhysicalTimeline.size() &&
                   kPhysicalTimeline[next_physical].offset == start) {
                auto e = kPhysicalTimeline[next_physical++]; e.offset = 0; physical_events.push_back(e);
            }
            auto guard = sentinels(8);
            const auto result = success(trace.system, 0, guard, host,
                                        static_cast<std::uint32_t>(physical_events.size()));
            trace.host_count += result.host_events_consumed;
            trace.physical_count += result.physical_events_consumed;
            known_reference(reference, 0, {}, physical_events);
            host.clear(); physical_events.clear();
        }
        while (next_host < kHostTimeline.size() && kHostTimeline[next_host].offset < start + frames) {
            auto e = kHostTimeline[next_host++]; e.offset -= start; host.push_back(e);
        }
        while (next_physical < kPhysicalTimeline.size() &&
               kPhysicalTimeline[next_physical].offset < start + frames) {
            auto e = kPhysicalTimeline[next_physical++]; e.offset -= start; physical_events.push_back(e);
        }
        const auto result = success(trace.system, frames,
                                    std::span<float>(trace.samples).subspan(start, frames), host,
                                    static_cast<std::uint32_t>(physical_events.size()));
        trace.host_count += result.host_events_consumed;
        trace.physical_count += result.physical_events_consumed;
        known_reference(reference, frames, std::span<float>(expected).subspan(start, frames),
                         physical_events);
        start += frames;
    }
    CHECK(next_host == kHostTimeline.size());
    CHECK(next_physical == kPhysicalTimeline.size());
    CHECK(trace.host_count == kHostTimeline.size());
    CHECK(trace.physical_count == kPhysicalTimeline.size());
    CHECK(trace.system.owners.owner_count() == 0);
    CHECK(trace.system.engine.active_key_count() == 0);
    same_audio(trace.samples, expected);
    same_engine(trace.system.engine, reference);
    ++partition_variants;
    return trace;
}

void test_partitioned_end_to_end(const RuntimeProfile& profile) {
    for (const auto mode : {ContactMode::Ideal, ContactMode::LinearTravel}) {
        for (const auto rate : {44100.0, 48000.0, 96000.0}) {
            const auto baseline = partitioned(profile, mode, rate, 3072, false);
            for (const auto block : {1U, 7U, 64U, 127U, 1024U}) {
                for (const bool flush : {false, true}) {
                    const auto actual = partitioned(profile, mode, rate, block, flush);
                    same_audio(actual.samples, baseline.samples);
                    same_system(actual.system, baseline.system);
                }
            }
            CHECK(std::any_of(baseline.samples.begin(), baseline.samples.end(),
                              [](float x) { return x != 0.0F; }));
        }
    }
}

void test_control_edits_keep_ownership(const RuntimeProfile& profile) {
    auto system = prepared(profile, ContactMode::LinearTravel, 48000.0);
    const std::array held{on(0, 0, 0, 69, 10), on(0, 0, 1, 69, 20)};
    (void)success(system, 1024, {}, held, 1);
    const auto owners = system.owners;
    const auto charge = system.engine.percussion_diagnostics().readiness;
    const auto clock = system.engine.frame_clock();
    const std::array controls{Event{0, EventType::Cancel, Manual::Upper, 0, 0.0},
                              Event{0, EventType::BankDrawbar, Manual::Upper, 11, 4.0},
                              Event{0, EventType::Percussion, Manual::Upper, 1, 1.0}};
    known_reference(system.engine, 0, {}, controls);
    CHECK(system.owners == owners);
    CHECK(system.engine.frame_clock() == clock);
    CHECK(system.engine.percussion_diagnostics().readiness == charge);
    const std::array release_one{off(0, 0, 0, 69, 10)};
    auto silent = sentinels(512);
    (void)success(system, 512, silent, release_one, 0);
    CHECK(std::all_of(silent.begin(), silent.end(), [](float x) { return x == 0.0F; }));
    CHECK(system.engine.key_down(Manual::Upper, 69));
    CHECK(system.owners.owner_count() == 1);
    const std::array reselect{Event{0, EventType::SelectBank, Manual::Upper, 0, 1.0}};
    known_reference(system.engine, 0, {}, reselect);
    (void)success(system, 512, silent, {}, 0);
    CHECK(std::any_of(silent.begin(), silent.end(), [](float x) { return x != 0.0F; }));
    const std::array release_last{channel_off(0, 0, 1)};
    (void)success(system, 1024, {}, release_last, 1);
    CHECK(system.owners.owner_count() == 0);
    CHECK(system.engine.active_key_count() == 0);
}
} // namespace

int main() {
    const auto profile = load_test_profile();
    test_engine_admission_rollback(profile);
    test_translation_rollback(profile);
    test_physical_ownership_and_remapping(profile);
    test_anonymous_fifo_cross_routes(profile);
    test_zero_time_and_disconnected_output(profile);
    test_partitioned_end_to_end(profile);
    test_control_edits_keep_ownership(profile);
    std::cout << "input processor: " << wrapper_calls << " calls; "
              << rejected_calls << " atomic rejections; " << future_probes
              << " future probes; " << compared_systems << " complete state comparisons; "
              << reference_events << " hand-authored reference events; "
              << partition_variants << " partition variants; " << compared_samples
              << " bit-exact sample comparisons\n";
}
