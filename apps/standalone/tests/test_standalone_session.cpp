#include "Session.h"
#include "TestSupport.h"

#include <algorithm>
#include <array>
#include <bit>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <initializer_list>
#include <iostream>
#include <limits>
#include <span>
#include <type_traits>
#include <vector>

namespace {

using namespace hammond;
using namespace hammond::standalone;

static_assert(std::is_trivially_copyable_v<SessionCommand>);
static_assert(std::is_trivially_copyable_v<SessionSnapshot>);
static_assert(!std::is_copy_constructible_v<Session>);
static_assert(!std::is_move_constructible_v<Session>);
static_assert(kSessionCommandCapacity == 256);

constexpr float sentinel = -9182.25F;
constexpr auto maximum = std::numeric_limits<std::uint64_t>::max();

struct Counts {
    std::uint64_t renders{};
    std::uint64_t stereo_samples{};
    std::uint64_t partition_samples{};
    std::uint64_t snapshots{};
    std::uint64_t accepted_posts{};
    std::uint64_t rejected_posts{};
    std::uint64_t rejected_renders{};
    std::uint64_t future_probes{};
    std::uint64_t score_runs{};
    std::uint64_t fixed_mode_publications{};
} counts;

[[nodiscard]] Event e(EventType type, Manual manual, std::uint8_t index, double value) {
    return {0, type, manual, index, value};
}

[[nodiscard]] SessionCommand m(HostNoteKind kind, std::uint8_t bus,
                                std::uint8_t channel, std::uint8_t pitch,
                                std::int32_t id, std::uint8_t velocity = 0) {
    return PerformanceInputEvent{HostNoteEvent{0, kind, bus, channel, pitch, velocity, id}};
}

[[nodiscard]] SessionCommand p(PedalNoteKind kind, std::uint8_t bus,
                                std::uint8_t channel, std::uint8_t pedal,
                                std::int32_t id, std::uint8_t velocity = 0) {
    return PerformanceInputEvent{PedalNoteEvent{
        0, kind, bus, channel, PedalId{pedal}, velocity, id}};
}

[[nodiscard]] SessionCommand c(Event event) { return PerformanceInputEvent{event}; }

[[nodiscard]] ControlSnapshot registration(unsigned variant = 0) {
    ControlSnapshot result;
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        for (std::size_t bank = 0; bank < kDrawbarBankCount; ++bank) {
            for (std::size_t drawbar = 0; drawbar < kDrawbarCount; ++drawbar) {
                result.drawbars[manual][bank][drawbar] = static_cast<std::uint8_t>(
                    (manual * 5 + bank * 3 + drawbar + variant) % 9);
            }
        }
    }
    result.selected_banks = variant % 2 == 0
        ? std::array{DrawbarBank::B, DrawbarBank::A}
        : std::array{DrawbarBank::A, DrawbarBank::B};
    result.route_enabled = {true, variant % 3 != 1};
    result.expression = variant % 2 == 0 ? 0.75 : 0.5;
    result.percussion = {true, PercussionHarmonic::Third,
                         PercussionVolume::Soft, PercussionDecay::Fast};
    result.pedal_drawbars = {8, static_cast<std::uint8_t>(variant % 8)};
    CHECK(is_valid_control_snapshot(result));
    return result;
}

[[nodiscard]] SessionSnapshot read(const Session& session) {
    SessionSnapshot result;
    CHECK(session.read_snapshot(result));
    CHECK(result.publication_revision % 2 == 0);
    ++counts.snapshots;
    return result;
}

void same_snapshot(const SessionSnapshot& actual, const SessionSnapshot& expected) {
    CHECK(actual.controls == expected.controls);
    CHECK(actual.held_keys == expected.held_keys);
    CHECK(actual.held_pedals == expected.held_pedals);
    CHECK(actual.frame_clock == expected.frame_clock);
    CHECK(actual.sample_rate == expected.sample_rate);
    CHECK(std::bit_cast<std::uint32_t>(actual.peak) ==
          std::bit_cast<std::uint32_t>(expected.peak));
    CHECK(actual.prepared == expected.prepared);
    CHECK(actual.running == expected.running);
    CHECK(actual.publication_revision == expected.publication_revision);
    CHECK(actual.resolved_sequence == expected.resolved_sequence);
    CHECK(actual.last_applied_sequence == expected.last_applied_sequence);
    CHECK(actual.recovery_count == expected.recovery_count);
    CHECK(actual.queue_overflows == expected.queue_overflows);
    CHECK(actual.rejected_commands == expected.rejected_commands);
    CHECK(actual.discarded_commands == expected.discarded_commands);
    CHECK(actual.fault_flags == expected.fault_flags);
    CHECK(actual.last_core_status == expected.last_core_status);
}

void same_music(const SessionSnapshot& actual, const Engine& expected) {
    CHECK(actual.controls == expected.controls_snapshot());
    CHECK(actual.prepared == expected.prepared());
    CHECK(actual.frame_clock == expected.frame_clock());
    CHECK(actual.sample_rate == expected.sample_rate());
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        for (std::size_t key = 0; key < kManualKeyCount; ++key) {
            CHECK(actual.held_keys[manual][key] == expected.key_down(
                static_cast<Manual>(manual), static_cast<std::uint32_t>(key) + kMinManualMidiNote));
        }
    }
    for (std::size_t pedal = 0; pedal < kPedalCount; ++pedal) {
        CHECK(actual.held_pedals[pedal] == expected.pedal_down(
            PedalId{static_cast<std::uint8_t>(pedal + 1)}));
    }
}

void no_holds(const SessionSnapshot& value) {
    for (const auto& manual : value.held_keys) {
        CHECK(std::none_of(manual.begin(), manual.end(), [](bool held) { return held; }));
    }
    CHECK(std::none_of(value.held_pedals.begin(), value.held_pedals.end(),
                       [](bool held) { return held; }));
}

[[nodiscard]] bool held(const SessionSnapshot& value, Manual manual, std::uint8_t pitch) {
    return value.held_keys[static_cast<std::size_t>(manual)][
        static_cast<std::size_t>(pitch - kMinManualMidiNote)];
}

[[nodiscard]] bool has_fault(const SessionSnapshot& value, SessionFault fault) {
    return (value.fault_flags & static_cast<std::uint32_t>(fault)) != 0;
}

void failed_post(Session& session, const SessionCommand& command, SessionStatus status) {
    const auto result = session.post(command);
    CHECK(result.status == status);
    CHECK(!result);
    CHECK(result.sequence == 0);
    ++counts.rejected_posts;
}

void failed_render(Session& session, std::uint32_t frames, std::size_t output_size,
                   SessionStatus status) {
    const auto before = read(session);
    std::vector<float> output(output_size, sentinel);
    const auto result = session.render(frames, output);
    CHECK(result.status == status);
    CHECK(!result);
    CHECK(result.frames_rendered == 0);
    CHECK(std::all_of(output.begin(), output.end(), [](float sample) { return sample == sentinel; }));
    same_snapshot(read(session), before);
    ++counts.rejected_renders;
}

// The reference owns no Session and no SessionCommand dispatcher. Each test
// supplies its expected physical Engine events explicitly, independently of the
// Session's hidden queue, ownership tables and recovery implementation.
struct Rig {
    Session session;
    Engine reference;
    std::uint64_t last_sequence{};
    float expected_peak{};

    Rig(const RuntimeProfile& profile, ProcessSpec spec = {48000.0, 1024, 27, 19},
        SessionLimits limits = {}, bool start_now = true) : session(limits) {
        CHECK(session.prepare(profile, spec) == SessionStatus::Ok);
        CHECK(reference.prepare(profile, spec) == Status::Ok);
        same_music(read(session), reference);
        CHECK(!read(session).running);
        if (start_now) CHECK(session.start() == SessionStatus::Ok);
    }

    std::uint64_t post(const SessionCommand& command) {
        const auto result = session.post(command);
        CHECK(result.status == SessionStatus::Ok);
        CHECK(result);
        CHECK(result.sequence == last_sequence + 1);
        last_sequence = result.sequence;
        ++counts.accepted_posts;
        return result.sequence;
    }

    void physical(std::initializer_list<Event> events) {
        const auto result = reference.process(0, {}, {events.begin(), events.size()});
        CHECK(result.status == Status::Ok);
        CHECK(result.events_consumed == events.size());
    }

    void control(Event event) {
        post(c(event));
        physical({event});
    }

    void restore(const ControlSnapshot& value) {
        post(value);
        CHECK(reference.restore_controls(value));
    }

    void panic_reference() {
        physical({e(EventType::AllNotesOff, Manual::Upper, 0, 0),
                  e(EventType::AllNotesOff, Manual::Lower, 0, 0),
                  e(EventType::PedalAllNotesOff, Manual::Lower, 0, 0)});
    }

    std::vector<float> render(std::uint32_t frames) {
        const auto before = read(session);
        std::vector<float> actual(static_cast<std::size_t>(frames) * 2 + 2, sentinel);
        std::vector<float> expected(static_cast<std::size_t>(frames) + 2, sentinel);
        const auto result = session.render(frames,
            std::span<float>{actual}.subspan(1, static_cast<std::size_t>(frames) * 2));
        CHECK(result.status == SessionStatus::Ok);
        CHECK(result);
        CHECK(result.frames_rendered == frames);
        CHECK(reference.process(frames, std::span<float>{expected}.subspan(1, frames), {}));
        CHECK(actual.front() == sentinel && actual.back() == sentinel);
        CHECK(expected.front() == sentinel && expected.back() == sentinel);
        if (frames != 0) expected_peak = 0.0F;
        std::vector<float> mono(frames);
        for (std::size_t index = 0; index < frames; ++index) {
            CHECK(std::isfinite(actual[1 + 2 * index]));
            for (std::size_t channel = 0; channel < 2; ++channel) {
                CHECK(std::bit_cast<std::uint32_t>(actual[1 + 2 * index + channel]) ==
                      std::bit_cast<std::uint32_t>(expected[1 + index]));
                ++counts.stereo_samples;
            }
            mono[index] = actual[1 + 2 * index];
            expected_peak = std::max(expected_peak, std::abs(expected[1 + index]));
        }
        const auto after = read(session);
        same_music(after, reference);
        CHECK(after.running);
        CHECK(after.frame_clock == before.frame_clock + frames);
        CHECK(after.publication_revision == before.publication_revision + 2);
        CHECK(std::bit_cast<std::uint32_t>(after.peak) ==
              std::bit_cast<std::uint32_t>(expected_peak));
        ++counts.renders;
        return mono;
    }

    void future_probe(std::uint32_t frames = 31) {
        render(frames);
        ++counts.future_probes;
    }

    void stop() {
        const auto before = read(session);
        CHECK(session.stop() == SessionStatus::Ok);
        panic_reference();
        expected_peak = 0.0F;
        const auto after = read(session);
        same_music(after, reference);
        CHECK(!after.running);
        CHECK(after.frame_clock == before.frame_clock);
        CHECK(after.peak == 0.0F);
        no_holds(after);
    }
};

void precharge(Rig& rig) {
    rig.restore(registration());
    rig.post(m(HostNoteKind::On, 0, 1, 60, 7, 100));
    rig.post(p(PedalNoteKind::On, 0, 2, 13, 8, 90));
    rig.physical({e(EventType::NoteOn, Manual::Upper, 60, 100),
                  e(EventType::PedalOn, Manual::Lower, 13, 90)});
    rig.render(23);
    CHECK(read(rig.session).peak > 0.0F);
}

void test_initial_and_defaults(const RuntimeProfile& profile) {
    Session fresh;
    const auto initial = read(fresh);
    same_snapshot(initial, SessionSnapshot{});
    Engine unprepared;
    same_music(initial, unprepared);
    CHECK(fresh.start() == SessionStatus::NotPrepared);
    CHECK(fresh.stop() == SessionStatus::NotPrepared);
    failed_post(fresh, Panic{}, SessionStatus::NotPrepared);
    failed_render(fresh, kHardMaxBlockFrames + 1, 3, SessionStatus::NotPrepared);

    for (const auto rate : {44100.0, 48000.0, 96000.0}) {
        Rig rig(profile, {rate, 64, 27, 113}, {}, false);
        const auto prepared = read(rig.session);
        CHECK(prepared.controls == ControlSnapshot{});
        CHECK(prepared.sample_rate == rate);
        CHECK(prepared.frame_clock == 113);
        CHECK(prepared.publication_revision == 2);
        CHECK(prepared.resolved_sequence == 0 && prepared.last_applied_sequence == 0);
        no_holds(prepared);
        CHECK(rig.session.start() == SessionStatus::Ok);
        const auto running = read(rig.session);
        CHECK(rig.session.start() == SessionStatus::AlreadyRunning);
        CHECK(rig.session.prepare(profile, {rate, 64, 0, 0}) == SessionStatus::AlreadyRunning);
        same_snapshot(read(rig.session), running);
        const auto silence = rig.render(31);
        CHECK(std::all_of(silence.begin(), silence.end(), [](float sample) { return sample == 0.0F; }));
        CHECK(read(rig.session).peak == 0.0F);
    }
}

// These boundaries are absolute sample positions, independent of the chosen
// callback partition. The expected note transitions are written out, including
// overlap cases that intentionally emit no additional physical note.
void score_boundary(Rig& rig, std::size_t boundary) {
    switch (boundary) {
    case 0:
        rig.restore(registration());
        rig.post(m(HostNoteKind::On, 0, 0, 60, 100, 100));
        rig.post(m(HostNoteKind::On, 1, 0, 64, 200, 100));
        rig.post(p(PedalNoteKind::On, 0, 0, 13, 300, 100));
        rig.physical({e(EventType::NoteOn, Manual::Upper, 60, 100),
                      e(EventType::NoteOn, Manual::Lower, 64, 100),
                      e(EventType::PedalOn, Manual::Lower, 13, 100)});
        break;
    case 1:
        rig.post(m(HostNoteKind::On, 0, 0, 60, 100, 32));
        rig.post(p(PedalNoteKind::On, 0, 0, 13, 300, 32));
        rig.post(m(HostNoteKind::On, 0, 3, 60, 110, 90));
        rig.post(p(PedalNoteKind::On, 1, 4, 13, 310, 90));
        break;
    case 2:
        rig.restore(registration(1));
        rig.control(e(EventType::Expression, Manual::Upper, 0, 0.625));
        rig.control(e(EventType::BankDrawbar, Manual::Lower, 17, 8));
        rig.control(e(EventType::SelectBank, Manual::Upper, 0, 1));
        break;
    case 3:
        rig.post(ReleaseUiNotes{});
        rig.physical({e(EventType::NoteOff, Manual::Lower, 64, 0)});
        break;
    case 4:
        rig.post(m(HostNoteKind::Off, 0, 3, 60, 110));
        rig.post(p(PedalNoteKind::Off, 1, 4, 13, 310));
        rig.physical({e(EventType::NoteOff, Manual::Upper, 60, 0),
                      e(EventType::PedalOff, Manual::Lower, 13, 0)});
        break;
    case 5:
        rig.post(m(HostNoteKind::On, 0, 0, 67, 400, 100));
        rig.post(m(HostNoteKind::On, 1, 6, 55, 500, 100));
        rig.post(p(PedalNoteKind::On, 1, 0, 25, 600, 100));
        rig.physical({e(EventType::NoteOn, Manual::Upper, 67, 100),
                      e(EventType::NoteOn, Manual::Lower, 55, 100),
                      e(EventType::PedalOn, Manual::Lower, 25, 100)});
        rig.control(e(EventType::Cancel, Manual::Upper, 0, 0));
        break;
    case 6:
        rig.post(Panic{});
        rig.panic_reference();
        rig.post(m(HostNoteKind::On, 0, 0, 72, 700, 100));
        rig.physical({e(EventType::NoteOn, Manual::Upper, 72, 100)});
        break;
    case 7:
        rig.restore(registration(2));
        rig.post(m(HostNoteKind::Off, 0, 0, 72, 700));
        rig.physical({e(EventType::NoteOff, Manual::Upper, 72, 0)});
        break;
    default:
        CHECK(false);
    }
}

[[nodiscard]] std::vector<float> run_score(const RuntimeProfile& profile, double rate,
                                           const std::vector<std::uint32_t>& partitions) {
    constexpr std::array<std::uint32_t, 9> boundaries{0, 37, 113, 257, 401, 509, 701, 887, 1009};
    Rig rig(profile, {rate, 1024, 0x6b381aULL, 97});
    std::vector<float> result;
    std::uint32_t cursor = 0;
    std::size_t boundary = 0;
    std::size_t partition = 0;
    while (cursor < boundaries.back()) {
        if (cursor == boundaries[boundary]) {
            const auto before = read(rig.session);
            score_boundary(rig, boundary);
            same_snapshot(read(rig.session), before); // Accepted is still queued.
            ++boundary;
        }
        const auto frames = std::min(partitions[partition++ % partitions.size()],
                                     boundaries[boundary] - cursor);
        const auto block = rig.render(frames);
        result.insert(result.end(), block.begin(), block.end());
        cursor += frames;
    }
    const auto final = read(rig.session);
    CHECK(final.resolved_sequence == rig.last_sequence);
    CHECK(final.last_applied_sequence == rig.last_sequence);
    CHECK(final.recovery_count == 0 && final.rejected_commands == 0);
    no_holds(final);
    rig.post(m(HostNoteKind::On, 0, 0, 76, 800, 100));
    rig.post(p(PedalNoteKind::On, 1, 0, 1, 801, 100));
    rig.physical({e(EventType::NoteOn, Manual::Upper, 76, 100),
                  e(EventType::PedalOn, Manual::Lower, 1, 100)});
    const auto future = rig.render(63);
    result.insert(result.end(), future.begin(), future.end());
    ++counts.future_probes;
    ++counts.score_runs;
    return result;
}

void test_parity_and_partitions(const RuntimeProfile& profile) {
    for (const auto rate : {44100.0, 48000.0, 96000.0}) {
        const auto whole = run_score(profile, rate, {1024});
        for (const auto& parts : {
                 std::vector<std::uint32_t>{1}, std::vector<std::uint32_t>{7, 13, 64, 127}}) {
            const auto split = run_score(profile, rate, parts);
            CHECK(split.size() == whole.size());
            for (std::size_t index = 0; index < whole.size(); ++index) {
                CHECK(std::bit_cast<std::uint32_t>(split[index]) ==
                      std::bit_cast<std::uint32_t>(whole[index]));
                ++counts.partition_samples;
            }
        }
    }
}

void test_fifo_copy_and_zero_frames(const RuntimeProfile& profile) {
    Rig rig(profile);
    precharge(rig);
    const auto before = read(rig.session);
    auto proposed = registration(2);
    const auto copied = proposed;
    rig.post(proposed);
    proposed = {};
    CHECK(rig.reference.restore_controls(copied));
    auto note = HostNoteEvent{0, HostNoteKind::On, 1, 0, 64, 100, 10};
    rig.post(PerformanceInputEvent{note});
    note.midi_note = 72;
    rig.physical({e(EventType::NoteOn, Manual::Lower, 64, 100)});
    rig.control(e(EventType::Expression, Manual::Upper, 0, 0.3125));
    rig.post(m(HostNoteKind::Off, 0, 1, 60, 7));
    rig.physical({e(EventType::NoteOff, Manual::Upper, 60, 0)});
    rig.post(ReleaseUiNotes{});
    rig.physical({e(EventType::NoteOff, Manual::Lower, 64, 0)});
    rig.post(Panic{});
    rig.panic_reference();
    rig.post(m(HostNoteKind::On, 0, 0, 67, 11, 100));
    rig.post(p(PedalNoteKind::On, 1, 0, 1, 12, 100));
    rig.physical({e(EventType::NoteOn, Manual::Upper, 67, 100),
                  e(EventType::PedalOn, Manual::Lower, 1, 100)});
    same_snapshot(read(rig.session), before);
    rig.render(0);
    const auto flushed = read(rig.session);
    CHECK(flushed.frame_clock == before.frame_clock);
    CHECK(flushed.peak == before.peak);
    CHECK(flushed.controls.expression == 0.3125);
    CHECK(flushed.controls.drawbars == copied.drawbars);
    CHECK(held(flushed, Manual::Upper, 67));
    CHECK(!held(flushed, Manual::Lower, 64) && !held(flushed, Manual::Lower, 72));
    CHECK(flushed.held_pedals[0]);
    CHECK(flushed.last_applied_sequence == rig.last_sequence);
    CHECK(flushed.resolved_sequence == rig.last_sequence);
    CHECK(flushed.recovery_count == 0); // Explicit Panic is not emergency recovery.
    rig.render(0);
    CHECK(read(rig.session).peak == before.peak);
    rig.future_probe(97);
}

void test_scoped_and_overlapping_owners(const RuntimeProfile& profile) {
    Rig rig(profile);
    rig.restore(registration(2));
    rig.post(m(HostNoteKind::On, 0, 0, 60, 10, 100));
    rig.post(m(HostNoteKind::On, 0, 0, 60, 11, 100));
    rig.post(m(HostNoteKind::On, 0, 5, 60, 12, 100));
    rig.post(m(HostNoteKind::On, 1, 0, 64, 20, 100));
    rig.post(m(HostNoteKind::On, 1, 9, 64, 21, 100));
    rig.post(m(HostNoteKind::On, 1, 0, 67, 22, 100));
    rig.post(p(PedalNoteKind::On, 0, 0, 13, 30, 100));
    rig.post(p(PedalNoteKind::On, 1, 0, 13, 31, 100));
    rig.post(p(PedalNoteKind::On, 1, 7, 13, 32, 100));
    rig.post(p(PedalNoteKind::On, 1, 0, 25, 40, 100));
    rig.physical({e(EventType::NoteOn, Manual::Upper, 60, 100),
                  e(EventType::NoteOn, Manual::Lower, 64, 100),
                  e(EventType::NoteOn, Manual::Lower, 67, 100),
                  e(EventType::PedalOn, Manual::Lower, 13, 100),
                  e(EventType::PedalOn, Manual::Lower, 25, 100)});
    rig.render(37);

    // Identified repeats are idempotent. Releasing one UI gesture leaves its
    // overlapping pointer/key and independent-channel owners intact.
    rig.post(m(HostNoteKind::On, 0, 0, 60, 10, 1));
    rig.post(p(PedalNoteKind::On, 0, 0, 13, 30, 1));
    rig.post(m(HostNoteKind::Off, 0, 0, 60, 10));
    rig.post(p(PedalNoteKind::Off, 0, 0, 13, 30));
    rig.control(e(EventType::Cancel, Manual::Upper, 0, 0));
    rig.render(0);
    CHECK(held(read(rig.session), Manual::Upper, 60));
    CHECK(!read(rig.session).controls.route_enabled[0]);

    rig.post(ReleaseUiNotes{});
    rig.physical({e(EventType::NoteOff, Manual::Lower, 67, 0),
                  e(EventType::PedalOff, Manual::Lower, 25, 0)});
    rig.render(0);
    const auto released = read(rig.session);
    CHECK(held(released, Manual::Upper, 60) && held(released, Manual::Lower, 64));
    CHECK(released.held_pedals[12]);
    CHECK(!released.held_pedals[24]);
    rig.post(ReleaseUiNotes{});
    rig.render(0); // Repeated focus loss cannot remove non-UI owners.
    rig.control(e(EventType::SelectBank, Manual::Upper, 0, 1));
    rig.future_probe();

    rig.post(m(HostNoteKind::Off, 0, 5, 60, 12));
    rig.post(m(HostNoteKind::Off, 1, 9, 64, 21));
    rig.post(p(PedalNoteKind::Off, 1, 7, 13, 32));
    rig.physical({e(EventType::NoteOff, Manual::Upper, 60, 0),
                  e(EventType::NoteOff, Manual::Lower, 64, 0),
                  e(EventType::PedalOff, Manual::Lower, 13, 0)});
    rig.render(0);
    no_holds(read(rig.session));

    // Two anonymous owners require two releases; zero-velocity On releases.
    for (unsigned repeat = 0; repeat < 2; ++repeat) {
        rig.post(m(HostNoteKind::On, 0, 4, 60, -1, 100));
        rig.post(p(PedalNoteKind::On, 0, 4, 13, -1, 100));
    }
    rig.physical({e(EventType::NoteOn, Manual::Upper, 60, 100),
                  e(EventType::PedalOn, Manual::Lower, 13, 100)});
    rig.render(0);
    rig.post(m(HostNoteKind::Off, 0, 4, 60, -1));
    rig.post(p(PedalNoteKind::Off, 0, 4, 13, -1));
    rig.render(0);
    CHECK(held(read(rig.session), Manual::Upper, 60));
    CHECK(read(rig.session).held_pedals[12]);
    rig.post(m(HostNoteKind::On, 0, 4, 60, -1));
    rig.post(p(PedalNoteKind::On, 0, 4, 13, -1));
    rig.physical({e(EventType::NoteOff, Manual::Upper, 60, 0),
                  e(EventType::PedalOff, Manual::Lower, 13, 0)});
    rig.render(0);
    no_holds(read(rig.session));
    precharge(rig);
    rig.post(Panic{});
    rig.panic_reference();
    rig.render(0);
    no_holds(read(rig.session));
    CHECK(read(rig.session).recovery_count == 0);
    rig.future_probe();
}

void test_lifecycle_and_failed_prepare(const RuntimeProfile& profile) {
    Rig rig(profile, {48000.0, 1024, 91, 77});
    precharge(rig);
    const auto applied = read(rig.session);
    rig.post(registration(1));
    rig.post(m(HostNoteKind::On, 1, 0, 70, 70, 100));
    rig.stop();
    auto stopped = read(rig.session);
    CHECK(stopped.controls == applied.controls);
    CHECK(stopped.last_applied_sequence == applied.last_applied_sequence);
    CHECK(stopped.resolved_sequence == rig.last_sequence);
    CHECK(stopped.discarded_commands == 2);
    const auto stopped_clock = stopped.frame_clock;
    rig.stop();
    CHECK(read(rig.session).discarded_commands == 2);
    failed_render(rig.session, kHardMaxBlockFrames + 1, 3, SessionStatus::NotRunning);
    CHECK(rig.session.start() == SessionStatus::Ok);
    rig.post(m(HostNoteKind::On, 0, 1, 60, 7, 100));
    rig.physical({e(EventType::NoteOn, Manual::Upper, 60, 100)});
    rig.future_probe(211); // Stop/start preserves phase and percussion readiness.
    CHECK(read(rig.session).frame_clock == stopped_clock + 211);
    rig.stop();

    const std::array invalid_specs{
        ProcessSpec{0.0, 1024, 100, 0}, ProcessSpec{-1.0, 1024, 100, 0},
        ProcessSpec{22050.0, 1024, 100, 0},
        ProcessSpec{std::numeric_limits<double>::quiet_NaN(), 1024, 100, 0},
        ProcessSpec{std::numeric_limits<double>::infinity(), 1024, 100, 0},
        ProcessSpec{-std::numeric_limits<double>::infinity(), 1024, 100, 0},
        ProcessSpec{48000.0, 0, 100, 0},
        ProcessSpec{48000.0, kHardMaxBlockFrames + 1, 100, 0}};
    const auto check_failed_prepare = [&](const RuntimeProfile& candidate,
                                         ProcessSpec spec, SessionStatus status) {
        const auto before = read(rig.session);
        const auto pending = registration(3);
        rig.post(pending);
        rig.post(m(HostNoteKind::On, 0, 0, 72, 99, 100));
        CHECK(rig.session.prepare(candidate, spec) == status);
        same_snapshot(read(rig.session), before);
        CHECK(rig.session.start() == SessionStatus::Ok);
        CHECK(rig.reference.restore_controls(pending));
        rig.physical({e(EventType::NoteOn, Manual::Upper, 72, 100)});
        rig.future_probe(53);
        CHECK(read(rig.session).last_applied_sequence == rig.last_sequence);
        rig.stop();
    };
    for (const auto spec : invalid_specs) {
        check_failed_prepare(profile, spec, SessionStatus::InvalidSpec);
    }
    check_failed_prepare(RuntimeProfile{}, {48000.0, 1024, 100, 0}, SessionStatus::InvalidProfile);
    auto invalid_profile = profile;
    invalid_profile.sources[3].frequency_hz = std::numeric_limits<double>::quiet_NaN();
    check_failed_prepare(invalid_profile, {48000.0, 1024, 100, 0}, SessionStatus::InvalidProfile);
    invalid_profile = profile;
    invalid_profile.manual_map[0][0] = 0;
    check_failed_prepare(invalid_profile, {48000.0, 1024, 100, 0}, SessionStatus::InvalidProfile);

    for (const auto rate : {96000.0, 44100.0, 48000.0}) {
        stopped = read(rig.session);
        rig.post(registration(1));
        rig.post(p(PedalNoteKind::On, 1, 0, 25, 101, 100));
        const ProcessSpec next{rate, 7, 0x9123, 1234};
        CHECK(rig.session.prepare(profile, next) == SessionStatus::Ok);
        CHECK(rig.reference.prepare(profile, next) == Status::Ok);
        rig.expected_peak = 0.0F;
        const auto fresh = read(rig.session);
        same_music(fresh, rig.reference);
        no_holds(fresh);
        CHECK(!fresh.running && fresh.peak == 0.0F);
        CHECK(fresh.controls == ControlSnapshot{});
        CHECK(fresh.discarded_commands == stopped.discarded_commands + 2);
        CHECK(fresh.resolved_sequence == rig.last_sequence);
        CHECK(fresh.last_applied_sequence == stopped.last_applied_sequence);
        CHECK(fresh.publication_revision > stopped.publication_revision);
        CHECK(fresh.fault_flags == stopped.fault_flags);
        CHECK(rig.session.start() == SessionStatus::Ok);
        rig.restore(registration());
        rig.post(m(HostNoteKind::On, 0, 1, 60, 7, 100));
        rig.physical({e(EventType::NoteOn, Manual::Upper, 60, 100)});
        failed_render(rig.session, 8, 16, SessionStatus::BlockTooLarge);
        rig.future_probe(7);
        rig.stop();
    }
}

void test_producer_rejections(const RuntimeProfile& profile) {
    Rig rig(profile);
    precharge(rig);
    const auto before = read(rig.session);
    rig.control(e(EventType::Expression, Manual::Upper, 0, 0.4));
    std::vector<SessionCommand> invalid{
        PerformanceInputEvent{HostNoteEvent{1, HostNoteKind::On, 0, 0, 60, 100, 9}},
        PerformanceInputEvent{PedalNoteEvent{1, PedalNoteKind::On, 0, 0, PedalId{13}, 100, 9}},
        PerformanceInputEvent{Event{1, EventType::Expression, Manual::Upper, 0, 0.4}}};
    for (const auto type : {EventType::NoteOn, EventType::NoteOff, EventType::AllNotesOff,
                            EventType::KeyPosition, EventType::PedalOn, EventType::PedalOff,
                            EventType::PedalAllNotesOff, static_cast<EventType>(255)}) {
        invalid.push_back(c(e(type, Manual::Upper, 60, 0)));
    }
    auto bad = registration();
    bad.drawbars[1][1][8] = 9;
    invalid.emplace_back(bad);
    bad = registration();
    bad.selected_banks[1] = static_cast<DrawbarBank>(2);
    invalid.emplace_back(bad);
    for (const auto expression : {-0.01, 1.01, std::numeric_limits<double>::quiet_NaN(),
                                   std::numeric_limits<double>::infinity()}) {
        bad = registration();
        bad.expression = expression;
        invalid.emplace_back(bad);
    }
    bad = registration();
    bad.percussion.harmonic = static_cast<PercussionHarmonic>(2);
    invalid.emplace_back(bad);
    bad = registration();
    bad.percussion.volume = static_cast<PercussionVolume>(2);
    invalid.emplace_back(bad);
    bad = registration();
    bad.percussion.decay = static_cast<PercussionDecay>(2);
    invalid.emplace_back(bad);
    bad = registration();
    bad.pedal_drawbars[1] = 9;
    invalid.emplace_back(bad);
    invalid.emplace_back(PerformanceInputEvent{Event{1, EventType::SelectPreset, Manual::Upper, 0, 1}});
    for (std::size_t manual = 0; manual < 2; ++manual) {
        for (unsigned value = 10; value <= 255; ++value) {
            bad = registration();
            bad.route_enabled[manual] = false;
            bad.fixed_registrations[manual] = static_cast<FixedRegistration>(value);
            invalid.emplace_back(bad);
        }
    }
    for (const auto& command : invalid) {
        failed_post(rig.session, command, SessionStatus::InvalidCommand);
        same_snapshot(read(rig.session), before);
    }
    rig.control(e(EventType::PedalDrawbar, Manual::Lower, 1, 6));
    rig.render(0);
    const auto after = read(rig.session);
    CHECK(after.rejected_commands == invalid.size());
    CHECK(after.recovery_count == 0 && after.discarded_commands == 0);
    CHECK(after.last_applied_sequence == rig.last_sequence);
    CHECK(after.resolved_sequence == rig.last_sequence);
    CHECK(has_fault(after, SessionFault::RejectedCommand));
    CHECK(after.last_core_status == Status::Ok);
    rig.future_probe();
}

void test_invalid_render_and_timeline(const RuntimeProfile& profile) {
    Rig rig(profile, {48000.0, 64, 37, 19});
    precharge(rig);
    struct BadCall { std::uint32_t frames; std::size_t output; SessionStatus status; };
    const std::array bad_calls{
        BadCall{65, 130, SessionStatus::BlockTooLarge},
        BadCall{65, 0, SessionStatus::BlockTooLarge},
        BadCall{kHardMaxBlockFrames + 1, 0, SessionStatus::BlockTooLarge},
        BadCall{1, 0, SessionStatus::InvalidBuffer},
        BadCall{1, 1, SessionStatus::InvalidBuffer},
        BadCall{1, 3, SessionStatus::InvalidBuffer},
        BadCall{0, 1, SessionStatus::InvalidBuffer}};
    for (const auto bad : bad_calls) {
        const auto before = read(rig.session);
        rig.post(c(e(EventType::Expression, Manual::Upper, 0, 0.25)));
        failed_render(rig.session, bad.frames, bad.output, bad.status);
        same_snapshot(read(rig.session), before);
        rig.physical({e(EventType::Expression, Manual::Upper, 0, 0.25)});
        rig.future_probe(7);
        const auto after = read(rig.session);
        CHECK(has_fault(after, SessionFault::RenderRejected));
        CHECK(after.last_core_status == (bad.status == SessionStatus::InvalidBuffer
            ? Status::InvalidBuffer : Status::BlockTooLarge));
        CHECK(after.last_applied_sequence == rig.last_sequence);
    }
    rig.render(64);

    Rig edge(profile, {96000.0, 64, 37, maximum - 3});
    edge.restore(registration());
    edge.post(m(HostNoteKind::On, 0, 0, 60, 7, 100));
    edge.physical({e(EventType::NoteOn, Manual::Upper, 60, 100)});
    edge.render(2);
    edge.post(c(e(EventType::Expression, Manual::Upper, 0, 0.5)));
    edge.post(p(PedalNoteKind::On, 1, 0, 13, 8, 100));
    failed_render(edge.session, 65, 1, SessionStatus::BlockTooLarge);
    failed_render(edge.session, 2, 3, SessionStatus::InvalidBuffer);
    failed_render(edge.session, 2, 4, SessionStatus::TimelineOverflow);
    edge.physical({e(EventType::Expression, Manual::Upper, 0, 0.5),
                   e(EventType::PedalOn, Manual::Lower, 13, 100)});
    edge.render(0);
    CHECK(read(edge.session).frame_clock == maximum - 1);
    edge.future_probe(1);
    CHECK(read(edge.session).frame_clock == maximum);
    edge.post(m(HostNoteKind::Off, 0, 0, 60, 7));
    failed_render(edge.session, 1, 2, SessionStatus::TimelineOverflow);
    edge.physical({e(EventType::NoteOff, Manual::Upper, 60, 0)});
    edge.render(0);
    CHECK(read(edge.session).frame_clock == maximum);
    CHECK(read(edge.session).last_core_status == Status::TimelineOverflow);
    edge.stop();

    Rig hard_bound(profile, {44100.0, kHardMaxBlockFrames, 18, 0});
    hard_bound.render(kHardMaxBlockFrames);
    CHECK(read(hard_bound.session).frame_clock == kHardMaxBlockFrames);
}

void test_queue_capacity_and_recovery(const RuntimeProfile& profile) {
    const std::array<SessionCommand, 3> failed_commands{
        m(HostNoteKind::Off, 0, 1, 60, 7), SessionCommand{registration(1)}, SessionCommand{Panic{}}};
    for (const auto& failed : failed_commands) {
        Rig rig(profile);
        precharge(rig);
        const auto before = read(rig.session);
        for (std::size_t index = 0; index < kSessionCommandCapacity; ++index) {
            if (index == 0 || index + 1 == kSessionCommandCapacity) {
                rig.post(registration(1));
            } else if (index == 1) {
                rig.post(m(HostNoteKind::Off, 0, 1, 60, 7));
            } else if (index == 2) {
                rig.post(p(PedalNoteKind::Off, 0, 2, 13, 8));
            } else if (index == 3) {
                rig.post(m(HostNoteKind::On, 1, 0, 76, 99, 100));
            } else {
                rig.post(c(e(EventType::Expression, Manual::Upper, 0, 0.125)));
            }
        }
        CHECK(rig.last_sequence == before.last_applied_sequence + 256);
        same_snapshot(read(rig.session), before);
        failed_post(rig.session, failed, SessionStatus::QueueFull);
        failed_post(rig.session, Panic{}, SessionStatus::RecoveryPending);
        failed_render(rig.session, 1, 1, SessionStatus::InvalidBuffer);
        failed_post(rig.session, registration(2), SessionStatus::RecoveryPending);
        rig.panic_reference();
        rig.render(0);
        const auto recovered = read(rig.session);
        no_holds(recovered);
        CHECK(recovered.controls == before.controls);
        CHECK(recovered.last_applied_sequence == before.last_applied_sequence);
        CHECK(recovered.resolved_sequence == rig.last_sequence);
        CHECK(recovered.discarded_commands == 256);
        CHECK(recovered.queue_overflows == 1 && recovered.recovery_count == 1);
        CHECK(recovered.rejected_commands == 0);
        CHECK(has_fault(recovered, SessionFault::QueueOverflow));
        rig.post(m(HostNoteKind::On, 0, 1, 60, 7, 100));
        rig.physical({e(EventType::NoteOn, Manual::Upper, 60, 100)});
        rig.future_probe();
        CHECK(!held(read(rig.session), Manual::Lower, 76));

        // Each ordinary full batch must be usable after recovery, including
        // both laps of the storage cursor. No failed post consumes a sequence.
        for (unsigned lap = 0; lap < 2; ++lap) {
            for (std::size_t index = 0; index < kSessionCommandCapacity; ++index) {
                rig.post(c(e(EventType::Expression, Manual::Upper, 0,
                             static_cast<double>(index % 9) / 8.0)));
            }
            rig.physical({e(EventType::Expression, Manual::Upper, 0, 0.375)});
            rig.render(0);
            const auto drained = read(rig.session);
            CHECK(drained.last_applied_sequence == rig.last_sequence);
            CHECK(drained.resolved_sequence == rig.last_sequence);
            CHECK(drained.discarded_commands == 256);
            CHECK(drained.recovery_count == 1 && drained.queue_overflows == 1);
        }
        rig.future_probe();
    }
}

void verify_consumer_recovery(Rig& rig, const SessionCommand& invalid, Status core_status) {
    const auto before = read(rig.session);
    const auto earlier = rig.post(c(e(EventType::Expression, Manual::Upper, 0, 0.375)));
    rig.physical({e(EventType::Expression, Manual::Upper, 0, 0.375)});
    rig.post(invalid); // Shape admission succeeds; authoritative payload admission is later.
    rig.post(registration(1));
    rig.post(m(HostNoteKind::On, 1, 0, 76, 999, 100));
    rig.post(p(PedalNoteKind::On, 1, 0, 25, 999, 100));
    same_snapshot(read(rig.session), before);
    rig.panic_reference();
    rig.render(17);
    const auto after = read(rig.session);
    no_holds(after);
    auto retained = before.controls;
    retained.expression = 0.375;
    CHECK(after.controls == retained);
    CHECK(after.last_applied_sequence == earlier);
    CHECK(after.resolved_sequence == rig.last_sequence);
    CHECK(after.rejected_commands == before.rejected_commands + 1);
    CHECK(after.discarded_commands == before.discarded_commands + 3);
    CHECK(after.recovery_count == before.recovery_count + 1);
    CHECK(after.queue_overflows == before.queue_overflows);
    CHECK(after.last_core_status == core_status);
    CHECK(has_fault(after, SessionFault::RejectedCommand));
    rig.post(m(HostNoteKind::On, 0, 1, 60, 7, 100));
    rig.post(p(PedalNoteKind::On, 0, 2, 13, 8, 100));
    rig.physical({e(EventType::NoteOn, Manual::Upper, 60, 100),
                  e(EventType::PedalOn, Manual::Lower, 13, 100)});
    rig.future_probe();
    CHECK(!held(read(rig.session), Manual::Lower, 76));
    CHECK(!read(rig.session).held_pedals[24]);
    CHECK(read(rig.session).last_core_status == core_status); // Sticky diagnostic.
}

void test_consumer_rejections(const RuntimeProfile& profile) {
    const std::vector<SessionCommand> invalid{
        c(e(EventType::Expression, Manual::Upper, 0, std::numeric_limits<double>::quiet_NaN())),
        c(e(EventType::Drawbar, Manual::Upper, 2, 2.5)),
        c(e(EventType::PedalDrawbar, Manual::Upper, 0, 8)),
        c(e(EventType::SelectPreset, static_cast<Manual>(2), 0, 1)),
        c(e(EventType::SelectPreset, Manual::Upper, 1, 1)),
        c(e(EventType::SelectPreset, Manual::Upper, 0, -1)),
        c(e(EventType::SelectPreset, Manual::Lower, 0, 12)),
        c(e(EventType::SelectPreset, Manual::Upper, 0, 1.5)),
        c(e(EventType::SelectPreset, Manual::Lower, 0, std::numeric_limits<double>::quiet_NaN())),
        c(e(EventType::SelectPreset, Manual::Upper, 0, std::numeric_limits<double>::infinity())),
        c(e(EventType::SelectPreset, Manual::Lower, 0, -std::numeric_limits<double>::infinity())),
        m(HostNoteKind::On, 2, 0, 60, 9, 100),
        m(HostNoteKind::On, 0, 16, 60, 9, 100),
        m(HostNoteKind::On, 0, 0, 35, 9, 100),
        m(HostNoteKind::On, 0, 0, 60, -2, 100),
        m(HostNoteKind::Off, 0, 1, 60, 7, 1),
        m(HostNoteKind::On, 0, 1, 61, 7, 100), // Reuses an admitted ID at another pitch.
        p(PedalNoteKind::On, 2, 0, 13, 9, 100),
        p(PedalNoteKind::On, 0, 16, 13, 9, 100),
        p(PedalNoteKind::On, 0, 0, 0, 9, 100),
        p(PedalNoteKind::On, 0, 0, 26, 9, 100),
        p(PedalNoteKind::On, 0, 0, 13, 9, 128),
        p(PedalNoteKind::On, 0, 2, 14, 8, 100)};
    for (const auto& command : invalid) {
        Rig rig(profile);
        precharge(rig);
        verify_consumer_recovery(rig, command, Status::InvalidEvent);
    }

    for (const bool overflow_pedals : {false, true}) {
        Rig rig(profile);
        rig.restore(registration());
        rig.render(0);
        // Fill each independent owner namespace in a separately admitted full
        // queue. The next owner, not the 256th command, must trigger rejection.
        for (std::int32_t id = 0; id < 256; ++id) {
            rig.post(m(HostNoteKind::On, 0, 1, 60, id, 100));
        }
        rig.physical({e(EventType::NoteOn, Manual::Upper, 60, 100)});
        rig.render(0);
        for (std::int32_t id = 0; id < 256; ++id) {
            rig.post(p(PedalNoteKind::On, 0, 2, 13, id, 100));
        }
        rig.physical({e(EventType::PedalOn, Manual::Lower, 13, 100)});
        rig.render(29);
        CHECK(read(rig.session).rejected_commands == 0);
        verify_consumer_recovery(rig,
            overflow_pedals ? p(PedalNoteKind::On, 0, 2, 13, 256, 100)
                            : m(HostNoteKind::On, 0, 1, 60, 256, 100),
            Status::TooManyEvents);
    }
}

void test_command_exhaustion(const RuntimeProfile& profile) {
    Rig rig(profile, {48000.0, 64, 37, 11}, {4, 64});
    precharge(rig); // Three accepted and applied commands.
    const auto before = read(rig.session);
    rig.post(registration(1));
    failed_post(rig.session, Panic{}, SessionStatus::SequenceExhausted);
    failed_post(rig.session, ReleaseUiNotes{}, SessionStatus::SequenceExhausted);
    same_snapshot(read(rig.session), before);
    failed_render(rig.session, 1, 0, SessionStatus::InvalidBuffer);
    rig.panic_reference();
    rig.render(0);
    const auto recovered = read(rig.session);
    no_holds(recovered);
    CHECK(recovered.controls == before.controls);
    CHECK(recovered.resolved_sequence == 4 && recovered.last_applied_sequence == 3);
    CHECK(recovered.discarded_commands == 1 && recovered.recovery_count == 1);
    CHECK(has_fault(recovered, SessionFault::SequenceExhausted));
    CHECK(recovered.queue_overflows == 0 && recovered.rejected_commands == 0);
    failed_post(rig.session, Panic{}, SessionStatus::SequenceExhausted);
    rig.future_probe(13);
    rig.stop();
    CHECK(rig.session.prepare(profile, {96000.0, 64, 3, 7}) == SessionStatus::Ok);
    CHECK(rig.reference.prepare(profile, {96000.0, 64, 3, 7}) == Status::Ok);
    rig.expected_peak = 0.0F;
    failed_post(rig.session, Panic{}, SessionStatus::SequenceExhausted);
    CHECK(rig.session.start() == SessionStatus::Ok);
    rig.render(0);
    CHECK(read(rig.session).resolved_sequence == 4);

    Rig stopped(profile, {48000.0, 64, 3, 7}, {2, 32}, false);
    stopped.post(registration());
    stopped.post(m(HostNoteKind::On, 0, 0, 60, 7, 100));
    failed_post(stopped.session, Panic{}, SessionStatus::SequenceExhausted);
    stopped.stop();
    const auto stopped_recovery = read(stopped.session);
    CHECK(stopped_recovery.controls == ControlSnapshot{});
    CHECK(stopped_recovery.resolved_sequence == 2 && stopped_recovery.last_applied_sequence == 0);
    CHECK(stopped_recovery.discarded_commands == 2 && stopped_recovery.recovery_count == 1);
    CHECK(stopped.session.start() == SessionStatus::Ok);
    stopped.future_probe(7);
    failed_post(stopped.session, Panic{}, SessionStatus::SequenceExhausted);

    Rig zero(profile, {48000.0, 64, 3, 7}, {0, 32});
    failed_post(zero.session, Panic{}, SessionStatus::SequenceExhausted);
    zero.stop();
    CHECK(read(zero.session).recovery_count == 1);
    CHECK(read(zero.session).resolved_sequence == 0);
    failed_post(zero.session, Panic{}, SessionStatus::SequenceExhausted);
}

void failed_publication_read(Session& session, const SessionSnapshot& marker) {
    auto destination = marker;
    CHECK(!session.read_snapshot(destination));
    same_snapshot(destination, marker);
}

void test_publication_exhaustion(const RuntimeProfile& profile) {
    Session invalid({maximum, maximum / 2 + 1});
    const auto pristine = read(invalid);
    CHECK(invalid.prepare(profile, {48000.0, 64, 0, 0}) == SessionStatus::InvalidSpec);
    same_snapshot(read(invalid), pristine);
    CHECK(invalid.start() == SessionStatus::NotPrepared);

    Session zero({maximum, 0});
    const auto initial = read(zero);
    CHECK(initial.publication_revision == 0);
    CHECK(zero.prepare(profile, {48000.0, 64, 0, 0}) == SessionStatus::SequenceExhausted);
    failed_publication_read(zero, initial);
    CHECK(zero.prepare(profile, {48000.0, 64, 0, 0}) == SessionStatus::SequenceExhausted);
    CHECK(zero.start() == SessionStatus::NotPrepared);

    Session one({maximum, 1});
    CHECK(one.prepare(profile, {48000.0, 64, 0, 11}) == SessionStatus::Ok);
    const auto prepared = read(one);
    CHECK(prepared.publication_revision == 2);
    CHECK(one.start() == SessionStatus::SequenceExhausted);
    failed_publication_read(one, prepared);
    CHECK(one.prepare(profile, {96000.0, 64, 9, 99}) == SessionStatus::SequenceExhausted);
    failed_post(one, Panic{}, SessionStatus::SequenceExhausted);
    failed_publication_read(one, prepared);

    Rig active(profile, {48000.0, 64, 37, 11}, {maximum, 4});
    precharge(active); // Preparation, start and this render use three publications.
    active.render(0);  // The fourth (last) publication still succeeds.
    const auto last = read(active.session);
    CHECK(last.publication_revision == 8);
    CHECK(held(last, Manual::Upper, 60) && last.held_pedals[12]);
    active.post(registration(1));
    active.post(m(HostNoteKind::On, 1, 0, 76, 99, 100));
    std::array<float, 14> output{};
    output.fill(sentinel);
    const auto exhausted = active.session.render(7, output);
    CHECK(exhausted.status == SessionStatus::SequenceExhausted);
    CHECK(exhausted.frames_rendered == 0);
    CHECK(std::all_of(output.begin(), output.end(), [](float sample) { return sample == sentinel; }));
    failed_publication_read(active.session, last);
    CHECK(active.session.render(0, {}).status == SessionStatus::SequenceExhausted);
    CHECK(active.session.render(1, {}).status == SessionStatus::InvalidBuffer);
    failed_post(active.session, Panic{}, SessionStatus::SequenceExhausted);
    CHECK(active.session.stop() == SessionStatus::SequenceExhausted);
    failed_publication_read(active.session, last);

    Rig stopped(profile, {48000.0, 64, 37, 11}, {maximum, 3});
    stopped.stop();
    const auto stopped_last = read(stopped.session);
    CHECK(stopped_last.publication_revision == 6 && !stopped_last.running);
    CHECK(stopped.session.prepare(profile, {44100.0, 64, 99, 99}) == SessionStatus::SequenceExhausted);
    CHECK(stopped.session.start() == SessionStatus::SequenceExhausted);
    failed_publication_read(stopped.session, stopped_last);
}

void test_unclipped_stereo(const RuntimeProfile& profile) {
    auto loud_profile = profile;
    loud_profile.output_gain = 1.0;
    for (auto& source : loud_profile.sources) {
        source.peak_amplitude = 1.0;
        source.base_phase_turns = 0.25;
    }
    Rig rig(loud_profile, {48000.0, 64, 0, 0});
    auto controls = ControlSnapshot{};
    controls.drawbars[0][1][2] = 8;
    controls.drawbars[1][1][2] = 8;
    rig.restore(controls);
    rig.post(m(HostNoteKind::On, 0, 0, 81, 1, 100));
    rig.post(m(HostNoteKind::On, 1, 0, 81, 2, 100));
    rig.physical({e(EventType::NoteOn, Manual::Upper, 81, 100),
                  e(EventType::NoteOn, Manual::Lower, 81, 100)});
    rig.render(64);
    CHECK(read(rig.session).peak > 1.0F);
}

void test_fixed_mode_publication_and_selection(const RuntimeProfile& profile) {
    Rig rig(profile);
    precharge(rig);
    const auto held_before = read(rig.session);
    for (unsigned upper = 0; upper < 10; ++upper) {
        for (unsigned lower = 0; lower < 10; ++lower) {
            for (unsigned bits = 0; bits < 16; ++bits) {
                auto value = registration(upper * 10 + lower);
                value.fixed_registrations = {static_cast<FixedRegistration>(upper),
                                            static_cast<FixedRegistration>(lower)};
                value.selected_banks = {(bits & 1U) != 0 ? DrawbarBank::B : DrawbarBank::A,
                                        (bits & 2U) != 0 ? DrawbarBank::B : DrawbarBank::A};
                value.route_enabled = {(bits & 4U) != 0, (bits & 8U) != 0};
                value.expression = (bits & 1U) != 0 ? -0.0 : 0.75;
                const auto before = read(rig.session);
                rig.restore(value);
                same_snapshot(read(rig.session), before);
                rig.render(0);
                const auto after = read(rig.session);
                CHECK(after.controls == value);
                CHECK(std::bit_cast<std::uint64_t>(after.controls.expression) ==
                      std::bit_cast<std::uint64_t>(value.expression));
                CHECK(after.held_keys == held_before.held_keys && after.held_pedals == held_before.held_pedals);
                CHECK(after.frame_clock == held_before.frame_clock);
                CHECK(after.resolved_sequence == rig.last_sequence && after.last_applied_sequence == rig.last_sequence);
                ++counts.fixed_mode_publications;
            }
        }
    }
    rig.control(e(EventType::Expression, Manual::Upper, 0, 0.75));
    for (const auto manual : {Manual::Upper, Manual::Lower}) {
        for (unsigned selection = 0; selection < 12; ++selection) {
            rig.control(e(EventType::SelectPreset, manual, 0, selection));
            rig.render(0);
            const auto after = read(rig.session);
            PresetSelection effective{};
            CHECK(control_preset_selection(after.controls, manual, effective));
            CHECK(static_cast<unsigned>(effective) == selection);
            CHECK(after.held_keys == held_before.held_keys && after.held_pedals == held_before.held_pedals);
            CHECK(after.frame_clock == held_before.frame_clock);
        }
    }
    // Stable FIFO is observable across new selectors and the legacy bank alias.
    rig.control(e(EventType::SelectPreset, Manual::Upper, 0, 9));
    rig.control(e(EventType::SelectBank, Manual::Upper, 0, 1));
    rig.render(0);
    CHECK(read(rig.session).controls.fixed_registrations[0] == FixedRegistration::None);
    rig.control(e(EventType::SelectBank, Manual::Upper, 0, 1));
    rig.control(e(EventType::SelectPreset, Manual::Upper, 0, 9));
    rig.control(e(EventType::SelectPreset, Manual::Upper, 0, -0.0));
    rig.render(0);
    CHECK(read(rig.session).controls.fixed_registrations[0] == FixedRegistration::A);
    CHECK(!read(rig.session).controls.route_enabled[0]);
    rig.future_probe();
}

} // namespace

int main() {
    const auto profile = load_test_profile();
    test_initial_and_defaults(profile);
    test_parity_and_partitions(profile);
    test_fifo_copy_and_zero_frames(profile);
    test_scoped_and_overlapping_owners(profile);
    test_lifecycle_and_failed_prepare(profile);
    test_producer_rejections(profile);
    test_invalid_render_and_timeline(profile);
    test_queue_capacity_and_recovery(profile);
    test_consumer_rejections(profile);
    test_command_exhaustion(profile);
    test_publication_exhaustion(profile);
    test_unclipped_stereo(profile);
    test_fixed_mode_publication_and_selection(profile);
    std::cout << "standalone Session acceptance: " << counts.score_runs << " rate/partition scores, "
              << counts.renders << " successful renders, " << counts.stereo_samples
              << " bit-exact stereo samples, " << counts.partition_samples
              << " partition samples, " << counts.snapshots << " coherent snapshots, "
              << counts.accepted_posts << " accepted posts, " << counts.rejected_posts
              << " rejected posts, " << counts.rejected_renders << " rejected renders, "
              << counts.future_probes << " future-output probes, "
              << counts.fixed_mode_publications << " fixed-mode publications\n";
    return 0;
}
