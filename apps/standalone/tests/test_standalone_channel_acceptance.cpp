#include "MidiInput.h"
#include "TestSupport.h"
#include "UiModel.h"

#include <algorithm>
#include <array>
#include <bit>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <limits>
#include <span>
#include <variant>

// Independent channel-mode acceptance at transport boundaries. The physical
// oracle receives explicit Engine events, never a channel-mode/ownership
// translation. The peer used for rejected inputs receives no rejected command.
namespace {
using namespace hammond;
using namespace hammond::standalone;

std::size_t stereo_samples{}, invalid_scopes{}, saturated_batches{}, reset_cases{};

SessionSnapshot read(const Session& session) {
    SessionSnapshot result;
    CHECK(session.read_snapshot(result));
    return result;
}

SessionCommand note(HostNoteKind kind, std::uint8_t bus, std::uint8_t channel,
                    std::uint8_t pitch, std::int32_t id = -1) {
    return PerformanceInputEvent{HostNoteEvent{0, kind, bus, channel, pitch,
        static_cast<std::uint8_t>(kind == HostNoteKind::On ? 100 : 0), id}};
}

SessionCommand pedal(std::uint8_t channel, std::uint8_t key, std::int32_t id) {
    return PerformanceInputEvent{PedalNoteEvent{0, PedalNoteKind::On,
        0, channel, PedalId{key}, 100, id}};
}

ControlSnapshot registration() {
    ControlSnapshot result;
    result.drawbars[0][1][2] = 8;
    result.drawbars[1][1][2] = 5;
    result.drawbars[1][0][4] = 3;
    result.expression = 0.375;
    result.pedal_drawbars = {7, 2};
    result.percussion = {true, PercussionHarmonic::Third,
        PercussionVolume::Soft, PercussionDecay::Fast};
    return result;
}

void require_samples(std::span<const float> actual, std::span<const float> expected) {
    CHECK(actual.size() == expected.size());
    for (std::size_t index = 0; index < actual.size(); ++index) {
        CHECK(std::bit_cast<std::uint32_t>(actual[index]) ==
              std::bit_cast<std::uint32_t>(expected[index]));
        ++stereo_samples;
    }
}

void require_no_holds(const SessionSnapshot& value) {
    for (const auto& manual : value.held_keys) {
        CHECK(std::none_of(manual.begin(), manual.end(), [](bool held) { return held; }));
    }
    CHECK(std::none_of(value.held_pedals.begin(), value.held_pedals.end(),
                      [](bool held) { return held; }));
}

struct PhysicalOracle {
    Session session;
    Engine reference;
    std::uint64_t sequence{};

    explicit PhysicalOracle(const RuntimeProfile& profile) {
        const ProcessSpec spec{48000.0, 128, 91, 37};
        CHECK(session.prepare(profile, spec) == SessionStatus::Ok);
        CHECK(reference.prepare(profile, spec) == Status::Ok);
        CHECK(session.start() == SessionStatus::Ok);
    }

    void post(const SessionCommand& command) {
        const auto result = session.post(command);
        CHECK(result && result.sequence == ++sequence);
    }

    void physical(EventType type, Manual manual, std::uint8_t index,
                  double value = 0.0) {
        const Event event{0, type, manual, index, value};
        CHECK(reference.process(0, {}, {&event, 1}));
    }

    void render(std::uint32_t frames) {
        std::array<float, 256> actual{}, expected{};
        std::array<float, 128> mono{};
        CHECK(session.render(frames, std::span{actual}.first(2 * frames)));
        CHECK(reference.process(frames, std::span{mono}.first(frames), {}));
        for (std::size_t frame = 0; frame < frames; ++frame) {
            expected[2 * frame] = expected[2 * frame + 1] = mono[frame];
        }
        require_samples(std::span{actual}.first(2 * frames),
                        std::span{expected}.first(2 * frames));
        const auto observed = read(session);
        CHECK(observed.controls == reference.controls_snapshot());
        CHECK(observed.frame_clock == reference.frame_clock());
        for (std::size_t manual = 0; manual < kManualCount; ++manual) {
            for (std::size_t key = 0; key < kManualKeyCount; ++key) {
                CHECK(observed.held_keys[manual][key] == reference.key_down(
                    static_cast<Manual>(manual), static_cast<std::uint32_t>(key) + 36));
            }
        }
        for (std::size_t key = 0; key < kPedalCount; ++key) {
            CHECK(observed.held_pedals[key] == reference.pedal_down(
                PedalId{static_cast<std::uint8_t>(key + 1)}));
        }
    }
};

void fifo_capacity_and_global_overflow(const RuntimeProfile& profile) {
    PhysicalOracle rig(profile);
    auto controls = registration();
    rig.post(controls);
    CHECK(rig.reference.restore_controls(controls));
    rig.post(note(HostNoteKind::On, 0, 0, 60, 101));
    rig.post(note(HostNoteKind::On, 0, 1, 60));
    rig.post(note(HostNoteKind::On, 0, 1, 64));
    rig.post(note(HostNoteKind::On, 1, 0, 72, 102));
    rig.post(note(HostNoteKind::On, 1, 2, 67));
    rig.post(pedal(0, 3, 103));
    rig.post(pedal(3, 7, -1));
    rig.physical(EventType::NoteOn, Manual::Upper, 60, 100);
    rig.physical(EventType::NoteOn, Manual::Upper, 64, 100);
    rig.physical(EventType::NoteOn, Manual::Lower, 72, 100);
    rig.physical(EventType::NoteOn, Manual::Lower, 67, 100);
    rig.physical(EventType::PedalOn, Manual::Lower, 3, 100);
    rig.physical(EventType::PedalOn, Manual::Lower, 7, 100);
    rig.render(37);

    // Fill every slot with a mixed transaction. The final new note must survive
    // the preceding sound-off; expression changes must retain their FIFO order.
    const auto first_sequence = rig.sequence;
    for (unsigned iteration = 0; iteration < 84; ++iteration) {
        rig.post(ScopedSoundOff{SoundOffDomain::Manual, 0, 1});
        rig.physical(EventType::NoteOff, Manual::Upper, 64);
        rig.post(note(HostNoteKind::On, 0, 1, 64));
        rig.physical(EventType::NoteOn, Manual::Upper, 64, 100);
        const double expression = iteration % 2 == 0 ? 0.25 : 0.75;
        rig.post(PerformanceInputEvent{Event{0, EventType::Expression,
            Manual::Upper, 0, expression}});
        rig.physical(EventType::Expression, Manual::Upper, 0, expression);
    }
    rig.post(ScopedSoundOff{SoundOffDomain::Manual, 0, 1});
    rig.physical(EventType::NoteOff, Manual::Upper, 64);
    rig.post(note(HostNoteKind::On, 0, 1, 69));
    rig.physical(EventType::NoteOn, Manual::Upper, 69, 100);
    rig.post(ScopedSoundOff{SoundOffDomain::Manual, 1, 2});
    rig.physical(EventType::NoteOff, Manual::Lower, 67);
    controls.expression = 0.625;
    rig.post(controls);
    CHECK(rig.reference.restore_controls(controls));
    CHECK(rig.sequence - first_sequence == kSessionCommandCapacity);
    const auto rejected = rig.session.post(ScopedSoundOff{SoundOffDomain::Pedal, 2, 3});
    CHECK(rejected.status == SessionStatus::InvalidCommand && rejected.sequence == 0);
    rig.render(0);
    const auto full = read(rig.session);
    CHECK(full.resolved_sequence == rig.sequence && full.last_applied_sequence == rig.sequence);
    CHECK(full.rejected_commands == 1 && full.queue_overflows == 0 && full.recovery_count == 0);
    rig.render(61);
    ++saturated_batches;

    // Overflow remains the separately declared GLOBAL recovery. Queued controls
    // must not partially apply; every owner, including UI channel zero, retires.
    auto discarded_controls = controls;
    discarded_controls.expression = 0.125;
    rig.post(discarded_controls);
    for (std::size_t index = 1; index < kSessionCommandCapacity; ++index) {
        rig.post(ScopedSoundOff{SoundOffDomain::Pedal, 1, 15});
    }
    const auto last_applied = full.last_applied_sequence;
    const auto overflow = rig.session.post(ScopedSoundOff{SoundOffDomain::Manual, 0, 1});
    CHECK(overflow.status == SessionStatus::QueueFull && overflow.sequence == 0);
    const auto blocked = rig.session.post(note(HostNoteKind::On, 0, 0, 76, 104));
    CHECK(blocked.status == SessionStatus::RecoveryPending && blocked.sequence == 0);
    rig.physical(EventType::AllNotesOff, Manual::Upper, 0);
    rig.physical(EventType::AllNotesOff, Manual::Lower, 0);
    rig.physical(EventType::PedalAllNotesOff, Manual::Lower, 0);
    rig.render(29);
    const auto recovered = read(rig.session);
    require_no_holds(recovered);
    CHECK(recovered.controls == controls);
    CHECK(recovered.last_applied_sequence == last_applied);
    CHECK(recovered.resolved_sequence == rig.sequence);
    CHECK(recovered.queue_overflows == 1 && recovered.recovery_count == 1);
    CHECK(recovered.discarded_commands == kSessionCommandCapacity);
    ++saturated_batches;

    // An audible fresh press after recovery detects a hidden source-phase reset.
    rig.post(note(HostNoteKind::On, 1, 2, 65));
    rig.physical(EventType::NoteOn, Manual::Lower, 65, 100);
    rig.render(128);
    CHECK(read(rig.session).peak > 0.0F);
}

void rejected_scope_budget_and_continuity(const RuntimeProfile& profile) {
    const SessionLimits limits{4, std::numeric_limits<std::uint64_t>::max() / 2};
    Session actual(limits), peer(limits);
    const ProcessSpec spec{48000.0, 128, 43, 89};
    for (auto* session : {&actual, &peer}) {
        CHECK(session->prepare(profile, spec) == SessionStatus::Ok);
        CHECK(session->start() == SessionStatus::Ok);
        CHECK(session->post(registration()).sequence == 1);
        CHECK(session->post(note(HostNoteKind::On, 0, 0, 60, 1)).sequence == 2);
        CHECK(session->post(note(HostNoteKind::On, 0, 1, 64)).sequence == 3);
    }
    const auto refuse = [&](ScopedSoundOff command) {
        const auto result = actual.post(command);
        CHECK(result.status == SessionStatus::InvalidCommand && result.sequence == 0);
        ++invalid_scopes;
    };
    const auto rejected_domain_ranges = [&] {
        for (unsigned value = 2; value <= 255; ++value) {
            refuse({static_cast<SoundOffDomain>(value), 0, 0});
            for (const auto domain : {SoundOffDomain::Manual, SoundOffDomain::Pedal}) {
                refuse({domain, static_cast<std::uint8_t>(value), 0});
            }
        }
        for (unsigned value = 16; value <= 255; ++value) {
            for (const auto domain : {SoundOffDomain::Manual, SoundOffDomain::Pedal}) {
                for (std::uint8_t bus = 0; bus < 2; ++bus) {
                    refuse({domain, bus, static_cast<std::uint8_t>(value)});
                }
            }
        }
    };
    const auto compare = [&](std::uint32_t frames) {
        std::array<float, 256> actual_audio{}, peer_audio{};
        CHECK(actual.render(frames, std::span{actual_audio}.first(2 * frames)));
        CHECK(peer.render(frames, std::span{peer_audio}.first(2 * frames)));
        require_samples(std::span{actual_audio}.first(2 * frames),
                        std::span{peer_audio}.first(2 * frames));
        const auto a = read(actual), b = read(peer);
        CHECK(a.controls == b.controls && a.held_keys == b.held_keys && a.held_pedals == b.held_pedals);
        CHECK(a.frame_clock == b.frame_clock && a.resolved_sequence == b.resolved_sequence);
        CHECK(a.last_applied_sequence == b.last_applied_sequence);
        CHECK(a.queue_overflows == 0 && b.queue_overflows == 0);
        CHECK(a.recovery_count == b.recovery_count);
    };
    rejected_domain_ranges();
    compare(23);
    CHECK(actual.post(ScopedSoundOff{SoundOffDomain::Manual, 0, 1}).sequence == 4);
    CHECK(peer.post(note(HostNoteKind::Off, 0, 1, 64)).sequence == 4);
    // Invalid shape wins while the finite budget is exactly used but its
    // exhaustion has not been requested. It cannot trigger recovery itself.
    rejected_domain_ranges();
    compare(97);
    const auto before_exhaustion = read(actual);
    CHECK(before_exhaustion.recovery_count == 0);
    CHECK(before_exhaustion.rejected_commands == invalid_scopes);
    CHECK(before_exhaustion.held_keys[0][60 - 36]);
    CHECK(!before_exhaustion.held_keys[0][64 - 36]);
    for (auto* session : {&actual, &peer}) {
        const auto result = session->post(ScopedSoundOff{SoundOffDomain::Manual, 0, 1});
        CHECK(result.status == SessionStatus::SequenceExhausted && result.sequence == 0);
    }
    compare(31);
    const auto exhausted = read(actual);
    require_no_holds(exhausted);
    CHECK(exhausted.recovery_count == 1 && exhausted.discarded_commands == 0);
    CHECK(exhausted.last_applied_sequence == 4 && exhausted.resolved_sequence == 4);
}

void cc121_across_partial_acknowledgments(const RuntimeProfile& profile) {
    for (const auto reset_status : {std::uint8_t{0xBF}, std::uint8_t{0xB3}, std::uint8_t{0xB8}}) {
        Session session;
        UiModel ui;
        MidiInput input;
        CHECK(session.prepare(profile, {48000.0, 128, 0, 0}) == SessionStatus::Ok);
        CHECK(session.start() == SessionStatus::Ok);
        CHECK(input.begin_epoch({16, 4, 9}, {20, 100, true}));
        ui.observe(read(session));
        const auto submit = [&](const UiActions& actions) {
            for (const auto& action : actions.span()) {
                CHECK(std::holds_alternative<SessionCommand>(action));
                const auto& command = std::get<SessionCommand>(action);
                const auto result = session.post(command);
                CHECK(result);
                CHECK(ui.submitted(command, result).count == 0);
            }
        };
        auto expected = registration();
        submit(ui.load_controls(expected));
        CHECK(session.post(note(HostNoteKind::On, 0, 0, 60, 77)));
        CHECK(session.post(note(HostNoteKind::On, 0, 1, 60)));
        CHECK(session.post(note(HostNoteKind::On, 1, 2, 67)));
        CHECK(session.post(pedal(3, 4, -1)));
        CHECK(session.render(0, {}));
        const auto initial = read(session);
        ui.observe(initial);
        submit(ui.external_parameter(4112, 1.0));
        expected.drawbars[0][1][0] = 8;
        CHECK(session.render(0, {}));
        const auto intermediate = read(session); // Deliberately not observed yet.

        submit(ui.external_parameter(4144, 0.5));
        expected.drawbars[1][1][0] = 4;
        const auto reset = input.decode(MidiPacket{{reset_status, 121, 0}, 3, 1});
        CHECK(reset.status == MidiDecodeStatus::Action);
        CHECK(std::holds_alternative<MidiParameterEdit>(reset.action));
        const auto edit = std::get<MidiParameterEdit>(reset.action);
        CHECK(edit.parameter_id == 8192 && edit.normalized == 1.0);
        submit(ui.external_parameter(edit.parameter_id, edit.normalized));
        expected.expression = 1.0;
        submit(ui.external_parameter(16385, 0.75));
        expected.pedal_drawbars[1] = 6;
        CHECK(ui.view().controls == expected && ui.view().controls_pending);
        ui.observe(initial);
        CHECK(ui.view().controls == expected && ui.view().controls_pending);
        ui.observe(intermediate);
        CHECK(ui.view().controls == expected && ui.view().controls_pending);

        // Native MIDI commands bypass UiModel::submitted. A later mode command
        // must neither erase the desired snapshot nor become its control ack.
        const auto silence = input.decode(MidiPacket{{0xBF, 120, 0}, 3, 2});
        CHECK(silence.status == MidiDecodeStatus::Action);
        CHECK(session.post(std::get<SessionCommand>(silence.action)));
        CHECK(ui.view().controls == expected && ui.view().controls_pending);
        CHECK(session.render(0, {}));
        const auto completed = read(session);
        ui.observe(completed);
        CHECK(completed.controls == expected && ui.view().controls == expected);
        CHECK(!ui.view().controls_pending && ui.view().controls_dirty);
        CHECK(completed.held_keys == initial.held_keys && completed.held_pedals == initial.held_pedals);
        CHECK(completed.recovery_count == 0 && completed.rejected_commands == 0);
        CHECK((input.expression_calibration() == MidiExpressionCalibration{20, 100, true}));
        // Older acknowledgments cannot undo the fully acknowledged result.
        ui.observe(intermediate);
        CHECK(ui.view().controls == expected && !ui.view().controls_pending);
        CHECK(ui.external_parameter(edit.parameter_id, edit.normalized).count == 0);
        ++reset_cases;
    }
}
} // namespace

int main() {
    const auto profile = load_test_profile();
    fifo_capacity_and_global_overflow(profile);
    rejected_scope_budget_and_continuity(profile);
    cc121_across_partial_acknowledgments(profile);
    std::cout << "channel acceptance: " << saturated_batches << " saturated batches, "
              << invalid_scopes << " invalid typed scopes, " << reset_cases
              << " partial-ack reset cases, " << stereo_samples
              << " exact stereo sample comparisons passed\n";
}
