#include "TestSupport.h"
#include "hammond/InputProcessor.h"

#include <algorithm>
#include <array>
#include <bit>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <memory>
#include <span>
#include <vector>

namespace {
using namespace hammond;

std::uint64_t compared_samples = 0;
std::uint64_t state_comparisons = 0;
std::uint64_t rate_boundaries = 0;
std::uint64_t rejected_rates = 0;
std::uint64_t rejected_blocks = 0;
std::uint64_t future_probes = 0;
std::uint64_t partition_runs = 0;

struct System {
    Engine engine;
    NoteOwnership owners;
    std::uint32_t maximum{257};
};

struct State {
    std::uint64_t clock{};
    double rate{};
    ContactMode mode{};
    ControlSnapshot controls{};
    PercussionRoutingDiagnostics percussion{};
    std::array<double, kToneSourceCount> phases{};
    std::array<std::array<ContactKeySnapshot, kManualKeyCount>, kManualCount> contacts{};
    std::array<std::array<bool, kManualKeyCount>, kManualCount> held{};
    std::size_t active{};

    bool operator==(const State&) const = default;
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

Event key(std::uint32_t frame, Manual manual, std::uint8_t note, bool down) {
    return {frame, down ? EventType::NoteOn : EventType::NoteOff,
            manual, note, down ? 100.0 : 0.0};
}

void same_double(double actual, double expected) {
    CHECK(std::bit_cast<std::uint64_t>(actual) ==
          std::bit_cast<std::uint64_t>(expected));
}

void same_audio(std::span<const float> actual, std::span<const float> expected) {
    CHECK(actual.size() == expected.size());
    for (std::size_t i = 0; i < actual.size(); ++i) {
        CHECK(std::isfinite(actual[i]));
        CHECK(std::bit_cast<std::uint32_t>(actual[i]) ==
              std::bit_cast<std::uint32_t>(expected[i]));
    }
    compared_samples += actual.size();
}

State state(const Engine& engine) {
    CHECK(engine.prepared());
    State result;
    result.clock = engine.frame_clock();
    result.rate = engine.sample_rate();
    result.mode = engine.contact_mode();
    result.controls = engine.controls_snapshot();
    result.percussion = engine.percussion_diagnostics();
    result.active = engine.active_key_count();
    for (std::size_t i = 0; i < kToneSourceCount; ++i) {
        CHECK(engine.source_phase_turns(static_cast<ToneId>(i + 1), result.phases[i]));
    }
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        std::size_t active = 0;
        for (std::size_t i = 0; i < kManualKeyCount; ++i) {
            const auto note = static_cast<std::uint32_t>(i + kMinManualMidiNote);
            result.held[manual][i] = engine.key_down(static_cast<Manual>(manual), note);
            active += result.held[manual][i] ? 1U : 0U;
            CHECK(engine.contact_snapshot(static_cast<Manual>(manual), note,
                                          result.contacts[manual][i]));
        }
        CHECK(engine.active_key_count(static_cast<Manual>(manual)) == active);
    }
    return result;
}

void same_state(const State& actual, const State& expected) {
    CHECK(actual == expected);
    same_double(actual.percussion.readiness, expected.percussion.readiness);
    same_double(actual.controls.expression, expected.controls.expression);
    for (std::size_t i = 0; i < kToneSourceCount; ++i) {
        same_double(actual.phases[i], expected.phases[i]);
    }
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        for (std::size_t i = 0; i < kManualKeyCount; ++i) {
            same_double(actual.contacts[manual][i].position,
                        expected.contacts[manual][i].position);
            same_double(actual.contacts[manual][i].target,
                        expected.contacts[manual][i].target);
        }
    }
    ++state_comparisons;
}

// Changes to routing/settings may change eligibility and gain, but cannot move
// any physical key, source phase, readiness or frame clock without samples.
void same_history(const State& actual, const State& expected) {
    auto normalized = actual;
    normalized.controls = expected.controls;
    normalized.percussion = expected.percussion;
    same_double(actual.percussion.readiness, expected.percussion.readiness);
    same_state(normalized, expected);
}

std::unique_ptr<System> prepared(const RuntimeProfile& profile, ContactMode mode,
                                 double rate, std::uint32_t maximum = 257,
                                 std::uint64_t origin = 73) {
    auto result = std::make_unique<System>();
    result->maximum = maximum;
    const auto model = mode == ContactMode::Ideal ? make_legacy_console_model()
                                                 : make_nominal_console_model();
    CHECK(result->engine.prepare(profile, {rate, maximum, 130132151, origin}, model) ==
          Status::Ok);
    auto controls = result->engine.controls_snapshot();
    controls.drawbars[0][1][2] = 8;
    controls.drawbars[0][1][8] = 5;
    controls.drawbars[0][0][0] = 6;
    controls.drawbars[1][1][2] = 7;
    controls.drawbars[1][1][4] = 3;
    controls.drawbars[1][0][2] = 5;
    controls.expression = 0.375;
    controls.percussion = {true, PercussionHarmonic::Second,
                           PercussionVolume::Normal, PercussionDecay::Fast};
    CHECK(result->engine.restore_controls(controls));
    return result;
}

InputProcessResult accept(System& system, std::uint32_t frames,
                          std::span<float> output,
                          std::span<const HostNoteEvent> input,
                          std::uint32_t physical_count) {
    const auto clock = system.engine.frame_clock();
    const auto result = process_owned_notes(system.engine, system.owners,
                                            frames, output, input);
    CHECK(result.status == Status::Ok);
    CHECK(result.host_events_consumed == input.size());
    CHECK(result.physical_events_consumed == physical_count);
    CHECK(system.engine.frame_clock() == clock + frames);
    return result;
}

void check_owner_keys(const System& system,
                      std::span<const NoteOwnerSnapshot> expected) {
    CHECK(system.owners.owner_count() == expected.size());
    for (std::size_t i = 0; i < expected.size(); ++i) {
        NoteOwnerSnapshot actual;
        CHECK(system.owners.owner_snapshot(i, actual));
        CHECK(actual == expected[i]);
    }
    std::size_t total = 0;
    for (const Manual manual : {Manual::Upper, Manual::Lower}) {
        for (std::uint32_t note = 36; note <= 96; ++note) {
            const auto count = static_cast<std::size_t>(std::count_if(
                expected.begin(), expected.end(), [manual, note](const auto& owner) {
                    return owner.manual == manual && owner.midi_note == note;
                }));
            std::size_t actual = kMaxNoteOwners + 1;
            CHECK(system.owners.owner_count(manual, note, actual));
            CHECK(actual == count);
            CHECK(system.engine.key_down(manual, note) == (count != 0));
            total += actual;
        }
    }
    CHECK(total == expected.size());
}

void change_rate(System& system, double rate) {
    auto before = state(system.engine);
    const auto owners = system.owners;
    CHECK(system.engine.reconfigure_sample_rate(rate) == Status::Ok);
    before.rate = rate;
    same_state(state(system.engine), before);
    CHECK(system.owners == owners);
    // A repeated rate must not introduce a trajectory rebase or hidden sample.
    CHECK(system.engine.reconfigure_sample_rate(rate) == Status::Ok);
    same_state(state(system.engine), before);
    CHECK(system.owners == owners);
    ++rate_boundaries;
}

void zero_flush(System& system) {
    const auto before = state(system.engine);
    const auto owners = system.owners;
    std::array<float, 2> output{-0.0F, 0.75F};
    const auto untouched = output;
    accept(system, 0, output, {}, 0);
    CHECK(system.engine.restore_controls(system.engine.controls_snapshot()));
    same_state(state(system.engine), before);
    CHECK(system.owners == owners);
    same_audio(output, untouched);
}

void control(System& system, Event event) {
    const auto before = state(system.engine);
    const auto owners = system.owners;
    const std::array events{event};
    const auto result = system.engine.process(0, {}, events);
    CHECK(result.status == Status::Ok && result.events_consumed == 1);
    same_history(state(system.engine), before);
    CHECK(system.owners == owners);
}

void restore(System& system, const ControlSnapshot& controls) {
    const auto before = state(system.engine);
    const auto owners = system.owners;
    CHECK(system.engine.restore_controls(controls));
    CHECK(system.engine.controls_snapshot() == controls);
    same_history(state(system.engine), before);
    CHECK(system.owners == owners);
}

struct Segment {
    double rate;
    std::uint32_t frames;
    std::vector<HostNoteEvent> host;
    std::vector<Event> physical;
    std::vector<NoteOwnerSnapshot> owners_after;
};

std::vector<Segment> schedule() {
    // This physical timeline and the surviving owner table were written by hand.
    // Neither is generated by NoteOwnership or by observing its output.
    using M = Manual;
    return {
        {48000.0, 601,
         {on(0, 0, 0, 60, 101), on(37, 0, 1, 60, 102), on(101, 1, 2, 67, 201),
          on(559, 0, 0, 64, -1), on(583, 0, 0, 64, -1), off(600, 0, 1, 60, 102)},
         {key(0, M::Upper, 60, true), key(101, M::Lower, 67, true),
          key(559, M::Upper, 64, true)},
         {{0, 0, 60, 101, M::Upper}, {1, 2, 67, 201, M::Lower},
          {0, 0, 64, -1, M::Upper}, {0, 0, 64, -1, M::Upper}}},
        // Before this segment both bus destinations swap and Upper is cancelled.
        {96000.0, 379,
         {on(0, 0, 0, 60, 101), on(1, 0, 0, 60, 103), off(17, 0, 0, 64, -1),
          on(66, 1, 2, 72, 202), off(197, 1, 2, 67, 201), on(378, 0, 0, 64, -1)},
         {key(1, M::Lower, 60, true), key(66, M::Upper, 72, true),
          key(197, M::Lower, 67, false), key(378, M::Lower, 64, true)},
         {{0, 0, 60, 101, M::Upper}, {0, 0, 64, -1, M::Upper},
          {0, 0, 60, 103, M::Lower}, {1, 2, 72, 202, M::Upper},
          {0, 0, 64, -1, M::Lower}}},
        {44100.0, 487,
         {off(0, 0, 0, 60, 101), off(13, 0, 0, 64, -1), on(29, 1, 3, 72, 203),
          channel_off(50, 0, 0), off(51, 0, 0, 90, 909), off(133, 1, 2, 72, 202),
          on(486, 1, 3, 76, 204)},
         {key(0, M::Upper, 60, false), key(13, M::Upper, 64, false),
          key(50, M::Lower, 60, false), key(50, M::Lower, 64, false),
          key(486, M::Upper, 76, true)},
         {{1, 3, 72, 203, M::Upper}, {1, 3, 76, 204, M::Upper}}},
        {48000.0, 29,
         {off(0, 1, 3, 72, 203), on(7, 0, 4, 55, 301), off(28, 1, 3, 76, 204)},
         {key(0, M::Upper, 72, false), key(7, M::Lower, 55, true),
          key(28, M::Upper, 76, false)},
         {{0, 4, 55, 301, M::Lower}}},
        {96000.0, 1081,
         {on(0, 1, 5, 65, 401), on(123, 0, 4, 55, 301, 0),
          off(377, 1, 5, 65, 401), channel_off(1079, 1, 3),
          on(1080, 0, 6, 69, 501)},
         {key(0, M::Upper, 65, true), key(123, M::Lower, 55, false),
          key(377, M::Upper, 65, false), key(1080, M::Lower, 69, true)},
         {{0, 6, 69, 501, M::Lower}}},
        {44100.0, 1237,
         {on(0, 0, 6, 69, 502), channel_off(5, 0, 6), on(47, 1, 7, 62, 601),
          channel_off(400, 1, 7), off(636, 1, 7, 62, 601)},
         {key(5, M::Lower, 69, false), key(47, M::Upper, 62, true),
          key(400, M::Upper, 62, false)},
         {}}
    };
}

void segment_boundary(System& system, std::size_t index, double rate,
                       const ControlSnapshot& original) {
    change_rate(system, rate);
    zero_flush(system);
    if (index == 1) {
        CHECK(system.owners.set_routes({Manual::Lower, Manual::Upper}));
        control(system, {0, EventType::Cancel, Manual::Upper, 0, 0.0});
        CHECK(!system.engine.percussion_diagnostics().eligible);
    } else if (index == 2 || index == 4) {
        control(system, {0, EventType::SelectBank, Manual::Upper, 0, 1.0});
        CHECK(system.engine.percussion_diagnostics().eligible);
        if (index == 2) {
            auto changed = system.engine.controls_snapshot();
            changed.expression = 0.625;
            changed.selected_banks[1] = DrawbarBank::A;
            changed.percussion.harmonic = PercussionHarmonic::Third;
            changed.percussion.volume = PercussionVolume::Soft;
            restore(system, changed);
        }
    } else if (index == 3) {
        control(system, {0, EventType::SelectBank, Manual::Upper, 0, 0.0});
        CHECK(!system.engine.percussion_diagnostics().eligible);
    } else if (index == 5) {
        restore(system, original);
        CHECK(system.engine.percussion_diagnostics().eligible);
    }
}

struct Run {
    std::vector<float> audio;
    std::vector<State> boundaries;
};

Run mixed_run(const RuntimeProfile& profile, ContactMode mode,
              const std::vector<Segment>& segments, std::uint32_t partition) {
    auto actual = prepared(profile, mode, segments.front().rate);
    auto direct = prepared(profile, mode, segments.front().rate);
    const auto original = actual->engine.controls_snapshot();
    Run result;
    std::uint64_t rendered = 0;
    for (std::size_t index = 0; index < segments.size(); ++index) {
        const auto& segment = segments[index];
        segment_boundary(*actual, index, segment.rate, original);
        segment_boundary(*direct, index, segment.rate, original);
        // The direct engine intentionally has no NoteOwnership input. Only its
        // hand-authored physical commands may depress/release its playing keys.
        same_state(state(actual->engine), state(direct->engine));
        const double start_q = actual->engine.percussion_diagnostics().readiness;
        std::uint32_t cursor = 0;
        std::size_t next_host = 0;
        std::size_t next_physical = 0;
        while (cursor < segment.frames) {
            const auto request = partition == 0
                ? std::array<std::uint32_t, 5>{3, 127, 1, 257, 19}[(cursor + index) % 5]
                : partition;
            const auto frames = std::min(request, segment.frames - cursor);
            std::array<HostNoteEvent, 16> host{};
            std::array<Event, 16> physical{};
            std::size_t host_count = 0;
            std::size_t physical_count = 0;
            while (next_host < segment.host.size() &&
                   segment.host[next_host].offset < cursor + frames) {
                auto event = segment.host[next_host++];
                CHECK(event.offset >= cursor && host_count < host.size());
                event.offset -= cursor;
                host[host_count++] = event;
            }
            while (next_physical < segment.physical.size() &&
                   segment.physical[next_physical].offset < cursor + frames) {
                auto event = segment.physical[next_physical++];
                CHECK(event.offset >= cursor && physical_count < physical.size());
                event.offset -= cursor;
                physical[physical_count++] = event;
            }
            std::array<float, 259> actual_audio{}, direct_audio{};
            actual_audio.fill(-0.0F);
            direct_audio.fill(-0.0F);
            actual_audio.back() = direct_audio.back() = 0.875F;
            accept(*actual, frames, actual_audio, {host.data(), host_count},
                   static_cast<std::uint32_t>(physical_count));
            const auto direct_result = direct->engine.process(
                frames, direct_audio, {physical.data(), physical_count});
            CHECK(direct_result.status == Status::Ok);
            CHECK(direct_result.events_consumed == physical_count);
            same_audio(actual_audio, direct_audio);
            for (std::size_t tail = frames; tail < actual_audio.size(); ++tail) {
                CHECK(std::bit_cast<std::uint32_t>(actual_audio[tail]) ==
                      std::bit_cast<std::uint32_t>(tail + 1 == actual_audio.size()
                                                     ? 0.875F : -0.0F));
            }
            result.audio.insert(result.audio.end(), actual_audio.begin(),
                                actual_audio.begin() + frames);
            same_state(state(actual->engine), state(direct->engine));
            cursor += frames;
        }
        CHECK(next_host == segment.host.size());
        CHECK(next_physical == segment.physical.size());
        check_owner_keys(*actual, segment.owners_after);
        rendered += segment.frames;
        CHECK(actual->engine.frame_clock() == 73 + rendered);
        const auto end = state(actual->engine);
        if (index == 0) {
            CHECK(end.percussion.readiness < 1.0);
            if (mode == ContactMode::LinearTravel) {
                CHECK(end.contacts[0][64 - 36].position > 0.0);
                CHECK(end.contacts[0][64 - 36].position < 1.0);
            }
        } else if (index == 1 || index == 3) {
            CHECK(end.percussion.readiness > start_q);
        }
        if (index == 3 && mode == ContactMode::LinearTravel) {
            CHECK(!end.held[0][72 - 36]);
            CHECK(end.contacts[0][72 - 36].closed[8]);
            CHECK(end.contacts[0][72 - 36].position < 1.0);
        }
        result.boundaries.push_back(end);
    }
    CHECK(actual->owners.owner_count() == 0);
    CHECK(actual->engine.active_key_count() == 0);
    for (const auto& manual : result.boundaries.back().contacts) {
        for (const auto& contact : manual) {
            CHECK(contact.position == 0.0 && contact.target == 0.0);
            CHECK(std::none_of(contact.closed.begin(), contact.closed.end(),
                               [](bool closed) { return closed; }));
        }
    }
    CHECK(result.audio.size() == 3814);
    CHECK(std::any_of(result.audio.begin(), result.audio.end(),
                      [](float sample) { return std::fabs(sample) > 1.0e-6F; }));
    ++partition_runs;
    return result;
}

void test_mixed_timeline(const RuntimeProfile& profile) {
    const auto segments = schedule();
    for (const auto mode : {ContactMode::Ideal, ContactMode::LinearTravel}) {
        const auto baseline = mixed_run(profile, mode, segments, 257);
        for (const std::uint32_t partition : {1U, 7U, 31U, 127U, 0U}) {
            const auto actual = mixed_run(profile, mode, segments, partition);
            same_audio(actual.audio, baseline.audio);
            CHECK(actual.boundaries.size() == baseline.boundaries.size());
            for (std::size_t i = 0; i < actual.boundaries.size(); ++i) {
                same_state(actual.boundaries[i], baseline.boundaries[i]);
            }
        }
    }
}

void future_equal(const System& actual, const System& expected) {
    auto left = std::make_unique<System>(actual);
    auto right = std::make_unique<System>(expected);
    const auto frames = std::min<std::uint32_t>(17, left->maximum);
    CHECK(frames >= 2);
    const std::array events{on(0, 0, 9, 77, 9000),
                            off(frames - 1, 0, 9, 77, 9000)};
    for (std::uint32_t block = 0; block < 3; ++block) {
        std::array<float, 17> a{}, b{};
        accept(*left, frames, a, events, 2);
        accept(*right, frames, b, events, 2);
        same_audio(a, b);
        same_state(state(left->engine), state(right->engine));
        CHECK(left->owners == right->owners);
    }
    ++future_probes;
}

std::unique_ptr<System> warm(const RuntimeProfile& profile, ContactMode mode,
                            double rate) {
    auto system = prepared(profile, mode, rate, 64);
    const std::array held{on(0, 0, 0, 60, 10), on(1, 0, 1, 60, 11),
                          on(12, 1, 2, 64, 20)};
    accept(*system, 64, {}, held, 2);
    for (std::uint32_t block = 0; block < 16; ++block) {
        accept(*system, 64, {}, {}, 0);
    }
    const std::array moving{on(0, 0, 0, 67, -1)};
    accept(*system, 23, {}, moving, 1);
    CHECK(system->owners.set_routes({Manual::Lower, Manual::Upper}));
    CHECK(system->owners.owner_count() == 4);
    CHECK(system->engine.percussion_diagnostics().readiness < 1.0);
    return system;
}

void rejected_rate(const System& baseline, double rate, Status expected) {
    auto actual = std::make_unique<System>(baseline);
    CHECK(actual->engine.reconfigure_sample_rate(rate) == expected);
    same_state(state(actual->engine), state(baseline.engine));
    CHECK(actual->owners == baseline.owners);
    future_equal(*actual, baseline);
    ++rejected_rates;
}

void test_rate_rollback(const RuntimeProfile& profile) {
    for (const auto mode : {ContactMode::Ideal, ContactMode::LinearTravel}) {
        auto ordinary = warm(profile, mode, 48000.0);
        change_rate(*ordinary, 96000.0);
        for (const double rate : {0.0, -48000.0, 32000.0,
                                  std::numeric_limits<double>::infinity(),
                                  std::numeric_limits<double>::quiet_NaN()}) {
            rejected_rate(*ordinary, rate, Status::InvalidSpec);
        }
        auto restricted = profile;
        restricted.sources.back().frequency_hz = 30000.0;
        auto high = warm(restricted, mode, 96000.0);
        rejected_rate(*high, 44100.0, Status::InvalidProfile);
        rejected_rate(*high, 48000.0, Status::InvalidProfile);
    }
}

void reject_block(const System& baseline, std::uint32_t frames,
                  std::span<const HostNoteEvent> input, Status expected,
                  std::size_t output_size, bool probe_future = true) {
    auto actual = std::make_unique<System>(baseline);
    std::vector<float> output(output_size, 0.625F);
    if (!output.empty()) {
        output.front() = -0.0F;
    }
    const auto untouched = output;
    const auto result = process_owned_notes(actual->engine, actual->owners,
                                            frames, output, input);
    CHECK(result.status == expected);
    CHECK(result.host_events_consumed == 0 && result.physical_events_consumed == 0);
    same_audio(output, untouched);
    same_state(state(actual->engine), state(baseline.engine));
    CHECK(actual->owners == baseline.owners);
    if (probe_future) {
        future_equal(*actual, baseline);
    }
    ++rejected_blocks;
}

void test_retained_block_limit(const RuntimeProfile& profile) {
    for (const auto mode : {ContactMode::Ideal, ContactMode::LinearTravel}) {
        auto system = prepared(profile, mode, 44100.0, 17);
        const std::array held{on(0, 0, 0, 60, 1), on(1, 0, 1, 60, 2)};
        accept(*system, 17, {}, held, 1);
        CHECK(system->owners.set_bus_route(0, Manual::Lower));
        for (const double rate : {96000.0, 48000.0, 44100.0}) {
            change_rate(*system, rate);
            const std::array new_owner{on(0, 1, 3, 70, 3)};
            reject_block(*system, 18, new_owner, Status::BlockTooLarge, 18);
            reject_block(*system, 17, new_owner, Status::InvalidBuffer, 16);
            const std::array bad_offset{on(17, 1, 3, 70, 3)};
            reject_block(*system, 17, bad_offset, Status::InvalidEvent, 17);
            const std::array conflict{on(0, 1, 3, 70, 3), on(1, 0, 0, 61, 1)};
            reject_block(*system, 17, conflict, Status::InvalidEvent, 17);
            reject_block(*system, kHardMaxBlockFrames + 1, new_owner,
                         Status::BlockTooLarge, 0);
            std::vector<HostNoteEvent> too_many(kMaxEventsPerBlock + 1,
                                               off(0, 1, 15, 96, 999));
            reject_block(*system, 17, too_many, Status::TooManyEvents, 17);
            // Maximum-sized success still releases the original Upper owner,
            // despite the bus remap, and leaves the second channel holding it.
            auto success = std::make_unique<System>(*system);
            const std::array input{off(0, 0, 0, 60, 1), on(16, 0, 3, 70, 3)};
            std::array<float, 19> audio{};
            audio[17] = -0.0F;
            audio[18] = 0.875F;
            accept(*success, 17, audio, input, 1);
            CHECK(success->engine.key_down(Manual::Upper, 60));
            CHECK(!success->engine.key_down(Manual::Lower, 60));
            CHECK(success->engine.key_down(Manual::Lower, 70));
            CHECK(std::bit_cast<std::uint32_t>(audio[17]) ==
                  std::bit_cast<std::uint32_t>(-0.0F));
            CHECK(audio[18] == 0.875F);
            zero_flush(*success);
        }
    }
}

void same_clock_phase_readiness(const State& actual, const State& expected) {
    CHECK(actual.clock == expected.clock);
    CHECK(actual.rate == expected.rate);
    same_double(actual.percussion.readiness, expected.percussion.readiness);
    for (std::size_t i = 0; i < kToneSourceCount; ++i) {
        same_double(actual.phases[i], expected.phases[i]);
    }
}

void test_clock_overflow(const RuntimeProfile& profile) {
    const auto maximum = std::numeric_limits<std::uint64_t>::max();
    for (const auto mode : {ContactMode::Ideal, ContactMode::LinearTravel}) {
        auto system = prepared(profile, mode, 48000.0, 17, maximum - 5);
        const std::array held{on(0, 0, 0, 60, 1), on(1, 0, 1, 60, 2)};
        accept(*system, 3, {}, held, 1);
        change_rate(*system, 96000.0);
        const std::array first_channel{channel_off(0, 0, 0)};
        reject_block(*system, 3, first_channel, Status::TimelineOverflow, 3, false);
        CHECK(system->owners.set_bus_route(0, Manual::Lower));
        accept(*system, 2, {}, first_channel, 0);
        CHECK(system->engine.frame_clock() == maximum);
        CHECK(system->owners.owner_count() == 1);
        CHECK(system->engine.key_down(Manual::Upper, 60));
        change_rate(*system, 44100.0);
        const auto before_release = state(system->engine);
        const std::array final_channel{channel_off(0, 0, 1)};
        std::array<float, 2> output{-0.0F, 0.75F};
        const auto untouched = output;
        accept(*system, 0, output, final_channel, 1);
        const auto released = state(system->engine);
        same_clock_phase_readiness(released, before_release);
        if (mode == ContactMode::LinearTravel) {
            same_double(released.contacts[0][60 - 36].position,
                        before_release.contacts[0][60 - 36].position);
        }
        CHECK(released.contacts[0][60 - 36].target == 0.0);
        CHECK(system->owners.owner_count() == 0);
        CHECK(system->engine.active_key_count() == 0);
        same_audio(output, untouched);
        const std::array new_owner{on(0, 0, 2, 65, 3)};
        reject_block(*system, 1, new_owner, Status::TimelineOverflow, 1, false);
        reject_block(*system, 18, new_owner, Status::BlockTooLarge, 18, false);
        // At UINT64_MAX, zero-time ownership changes are still admissible. A
        // same-offset press/release grants no source or percussion advancement.
        const auto before_pair = state(system->engine);
        const std::array pair{on(0, 0, 2, 65, 3), off(0, 0, 2, 65, 3)};
        accept(*system, 0, output, pair, 2);
        same_state(state(system->engine), before_pair);
        CHECK(system->owners.owner_count() == 0);
        same_audio(output, untouched);
    }
}
} // namespace

int main() {
    const auto profile = load_test_profile();
    test_mixed_timeline(profile);
    test_rate_rollback(profile);
    test_retained_block_limit(profile);
    test_clock_overflow(profile);
    std::cout << "owned lifecycle: " << partition_runs << " mixed-rate runs, "
              << rate_boundaries << " preserved rate boundaries, "
              << rejected_rates << " rejected rates, " << rejected_blocks
              << " rejected input blocks, " << future_probes << " future probes, "
              << state_comparisons << " exact state comparisons, "
              << compared_samples << " exact sample comparisons\n";
    return EXIT_SUCCESS;
}
