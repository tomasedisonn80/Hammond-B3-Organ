#include "MidiInput.h"
#include "Session.h"
#include "TestSupport.h"

#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <iostream>
#include <span>
#include <type_traits>
#include <variant>

namespace {
using namespace hammond;
using namespace hammond::standalone;

static_assert(std::is_same_v<std::variant_alternative_t<0, SessionCommand>, PerformanceInputEvent>);
static_assert(std::is_same_v<std::variant_alternative_t<1, SessionCommand>, ControlSnapshot>);
static_assert(std::is_same_v<std::variant_alternative_t<2, SessionCommand>, ReleaseUiNotes>);
static_assert(std::is_same_v<std::variant_alternative_t<3, SessionCommand>, Panic>);
static_assert(std::is_same_v<std::variant_alternative_t<4, SessionCommand>, ScopedSoundOff>);
static_assert(std::is_trivially_copyable_v<SessionCommand>);

SessionSnapshot snapshot(const Session& session) {
    SessionSnapshot result;
    CHECK(session.read_snapshot(result));
    return result;
}

SessionCommand manual(HostNoteKind kind, std::uint8_t bus, std::uint8_t channel,
                      std::uint8_t pitch, std::int32_t id = -1) {
    return PerformanceInputEvent{HostNoteEvent{0, kind, bus, channel, pitch,
        static_cast<std::uint8_t>(kind == HostNoteKind::On ? 100 : 0), id}};
}

SessionCommand pedal(std::uint8_t bus, std::uint8_t channel, std::int32_t id = -1) {
    return PerformanceInputEvent{PedalNoteEvent{0, PedalNoteKind::On,
        bus, channel, PedalId{7}, 100, id}};
}

// The reference receives independently specified physical transitions, never
// ScopedSoundOff or either ownership translator. Full audio equality checks
// continued source/percussion history as well as the copied logical holds.
struct Trace {
    Session session;
    Engine reference;
    MidiInput midi;
    std::uint64_t sequence{};

    explicit Trace(const RuntimeProfile& profile) {
        const ProcessSpec spec{48000.0, 128, 31, 23};
        CHECK(session.prepare(profile, spec) == SessionStatus::Ok);
        CHECK(reference.prepare(profile, spec) == Status::Ok);
        CHECK(reference.contact_mode() == ContactMode::Ideal);
        CHECK(session.start() == SessionStatus::Ok);
        CHECK(midi.begin_epoch());
    }

    void post(const SessionCommand& command) {
        const auto result = session.post(command);
        CHECK(result && result.sequence == ++sequence);
    }

    void sound_off(std::uint8_t status) {
        const auto decoded = midi.decode(MidiPacket{{status, 120, 0}, 3, 0});
        CHECK(decoded.status == MidiDecodeStatus::Action);
        CHECK(std::holds_alternative<SessionCommand>(decoded.action));
        const auto& command = std::get<SessionCommand>(decoded.action);
        CHECK(std::holds_alternative<ScopedSoundOff>(command));
        post(command);
    }

    void physical(EventType type, Manual division, std::uint8_t key) {
        const Event event{0, type, division, key,
            type == EventType::NoteOn || type == EventType::PedalOn ? 100.0 : 0.0};
        CHECK(reference.process(0, {}, {&event, 1}));
    }

    void controls(const ControlSnapshot& controls) {
        post(controls);
        CHECK(reference.restore_controls(controls));
    }

    bool render(std::uint32_t frames) {
        std::array<float, 256> stereo{};
        std::array<float, 128> mono{};
        CHECK(session.render(frames, std::span{stereo}.first(2 * frames)));
        CHECK(reference.process(frames, std::span{mono}.first(frames), {}));
        for (std::uint32_t frame = 0; frame < frames; ++frame) {
            for (std::uint32_t channel = 0; channel < 2; ++channel) {
                CHECK(std::bit_cast<std::uint32_t>(stereo[2 * frame + channel]) ==
                      std::bit_cast<std::uint32_t>(mono[frame]));
            }
        }
        const auto state = snapshot(session);
        CHECK(state.controls == reference.controls_snapshot());
        CHECK(state.frame_clock == reference.frame_clock());
        CHECK(state.resolved_sequence == sequence && state.last_applied_sequence == sequence);
        CHECK(state.recovery_count == 0 && state.rejected_commands == 0 && state.fault_flags == 0);
        for (std::size_t division = 0; division < kManualCount; ++division) {
            for (std::size_t key = 0; key < kManualKeyCount; ++key) {
                CHECK(state.held_keys[division][key] == reference.key_down(
                    static_cast<Manual>(division), static_cast<std::uint32_t>(key) + 36));
            }
        }
        for (std::size_t key = 0; key < kPedalCount; ++key) {
            CHECK(state.held_pedals[key] == reference.pedal_down(
                PedalId{static_cast<std::uint8_t>(key + 1)}));
        }
        return std::any_of(mono.begin(), mono.begin() + frames, [](float value) { return value != 0.0F; });
    }
};

void isolation_and_continuity(const RuntimeProfile& profile) {
    Trace trace(profile);
    ControlSnapshot controls;
    controls.drawbars[0][1][2] = 8;
    controls.drawbars[1][1][2] = 6;
    controls.pedal_drawbars = {8, 5};
    controls.expression = 0.625;
    controls.percussion = {true, PercussionHarmonic::Third, PercussionVolume::Soft, PercussionDecay::Fast};
    trace.controls(controls);
    trace.post(manual(HostNoteKind::On, 0, 1, 60));
    trace.post(manual(HostNoteKind::On, 0, 1, 60)); // Anonymous duplicates retire together.
    trace.post(manual(HostNoteKind::On, 0, 0, 60, 7));
    trace.post(manual(HostNoteKind::On, 0, 1, 64));
    trace.post(manual(HostNoteKind::On, 1, 2, 60));
    trace.post(pedal(0, 3));
    trace.post(pedal(1, 0, 9)); // Second typed pedal origin is valid.
    trace.physical(EventType::NoteOn, Manual::Upper, 60);
    trace.physical(EventType::NoteOn, Manual::Upper, 64);
    trace.physical(EventType::NoteOn, Manual::Lower, 60);
    trace.physical(EventType::PedalOn, Manual::Lower, 7);
    CHECK(trace.render(64));

    trace.sound_off(0xB0);
    trace.physical(EventType::NoteOff, Manual::Upper, 64);
    CHECK(trace.render(31)); // Same-key UI, Lower and pedal owners survive.
    trace.sound_off(0xB0);
    trace.post(manual(HostNoteKind::Off, 0, 1, 64));
    trace.post(manual(HostNoteKind::Off, 0, 1, 60));
    CHECK(trace.render(17)); // Repeats and old unmatched releases are harmless.
    trace.post(manual(HostNoteKind::On, 0, 1, 64));
    trace.physical(EventType::NoteOn, Manual::Upper, 64);
    CHECK(trace.render(47)); // No persistent mute or phase reset.
    trace.sound_off(0xB1);
    trace.physical(EventType::NoteOff, Manual::Lower, 60);
    CHECK(trace.render(23));
    trace.sound_off(0xB2);
    CHECK(trace.render(29)); // Bus-1 pedal owner still holds pedal 7.
    trace.post(ScopedSoundOff{SoundOffDomain::Manual, 0, 0});
    trace.post(ScopedSoundOff{SoundOffDomain::Pedal, 1, 0});
    trace.physical(EventType::NoteOff, Manual::Upper, 60);
    trace.physical(EventType::PedalOff, Manual::Lower, 7);
    CHECK(trace.render(19));
    trace.sound_off(0xB0);
    trace.physical(EventType::NoteOff, Manual::Upper, 64);
    CHECK(!trace.render(1)); // First post-application sample is already zero.
    CHECK(!trace.render(128));
}

void percussion_only(const RuntimeProfile& profile) {
    Trace trace(profile);
    ControlSnapshot controls;
    controls.percussion.enabled = true;
    trace.controls(controls);
    trace.post(manual(HostNoteKind::On, 0, 1, 60));
    trace.physical(EventType::NoteOn, Manual::Upper, 60);
    CHECK(trace.render(64));
    trace.sound_off(0xB0);
    trace.physical(EventType::NoteOff, Manual::Upper, 60);
    CHECK(!trace.render(1));
    CHECK(!trace.render(73));
    trace.post(manual(HostNoteKind::On, 0, 1, 60));
    trace.physical(EventType::NoteOn, Manual::Upper, 60);
    CHECK(trace.render(128)); // Resumption matches unreset shared history.
}

void typed_admission(const RuntimeProfile& profile) {
    Session session;
    CHECK(session.prepare(profile, {48000.0, 128, 0, 0}) == SessionStatus::Ok);
    CHECK(session.start() == SessionStatus::Ok);
    constexpr std::array<ScopedSoundOff, 10> invalid{{
        {static_cast<SoundOffDomain>(2), 0, 0}, {static_cast<SoundOffDomain>(255), 0, 0},
        {SoundOffDomain::Manual, 2, 0}, {SoundOffDomain::Manual, 255, 0},
        {SoundOffDomain::Pedal, 2, 0}, {SoundOffDomain::Pedal, 255, 0},
        {SoundOffDomain::Manual, 0, 16}, {SoundOffDomain::Manual, 0, 255},
        {SoundOffDomain::Pedal, 1, 16}, {SoundOffDomain::Pedal, 1, 255},
    }};
    const auto reject = [&] {
        for (const auto& command : invalid) {
            const auto result = session.post(command);
            CHECK(result.status == SessionStatus::InvalidCommand && result.sequence == 0);
        }
    };
    reject();
    // Exercise all valid scopes, filling the complete queue without rendering.
    // Invalid shapes must still reject before capacity/recovery admission.
    std::uint64_t sequence = 0;
    for (unsigned repeat = 0; repeat < 4; ++repeat) {
        for (const auto domain : {SoundOffDomain::Manual, SoundOffDomain::Pedal}) {
            for (std::uint8_t bus = 0; bus < 2; ++bus) {
                for (std::uint8_t channel = 0; channel < 16; ++channel) {
                    const auto result = session.post(ScopedSoundOff{domain, bus, channel});
                    CHECK(result && result.sequence == ++sequence);
                }
            }
        }
    }
    CHECK(sequence == kSessionCommandCapacity);
    reject();
    CHECK(session.render(0, {}));
    const auto state = snapshot(session);
    CHECK(state.last_applied_sequence == 256 && state.resolved_sequence == 256);
    CHECK(state.rejected_commands == 20 && state.queue_overflows == 0 && state.recovery_count == 0);
    const auto next = session.post(ScopedSoundOff{SoundOffDomain::Pedal, 1, 15});
    CHECK(next && next.sequence == 257);
    CHECK(session.render(0, {}));
}
} // namespace

int main() {
    const auto profile = load_test_profile();
    isolation_and_continuity(profile);
    percussion_only(profile);
    typed_admission(profile);
    std::cout << "standalone channel modes: isolation, ideal silence, continuity and admission passed\n";
}
