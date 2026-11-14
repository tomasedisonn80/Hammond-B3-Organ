#include "MidiInput.h"
#include "TestSupport.h"
#include "UiModel.h"

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
#include <variant>
#include <vector>

namespace {

using namespace hammond;
using namespace hammond::standalone;

constexpr std::uint64_t initial_frame = 137;
constexpr std::uint64_t phase_seed = 519;
constexpr float sentinel = -1937.5F;

struct Counts {
    std::size_t scenarios{};
    std::size_t packets{};
    std::size_t commands{};
    std::size_t callbacks{};
    std::size_t stereo_samples{};
    std::size_t reference_samples{};
    std::size_t partition_samples{};
} counts;

[[nodiscard]] ControlSnapshot registration() {
    ControlSnapshot controls;
    controls.drawbars[0][1][2] = 8;
    controls.drawbars[1][1][2] = 6;
    controls.pedal_drawbars = {8, 3};
    controls.expression = 0.75;
    CHECK(is_valid_control_snapshot(controls));
    return controls;
}

// Every observation in this fixture comes from an actual prepared Session.
// MIDI commands go directly to its sole producer; only controller edits enter
// UiModel's complete desired snapshot and submitted/observe protocol.
struct Rig {
    Session session;
    MidiInbox inbox;
    MidiInput midi;
    UiModel ui;
    std::uint64_t last_sequence{};

    explicit Rig(const RuntimeProfile& profile, MidiRouting routing = {},
                 double rate = 48000.0) {
        CHECK(session.prepare(profile, {rate, 1024, phase_seed, initial_frame}) == SessionStatus::Ok);
        CHECK(session.start() == SessionStatus::Ok);
        CHECK(midi.begin_epoch(routing));
        ui.observe(read());
        ++counts.scenarios;
    }

    [[nodiscard]] SessionSnapshot read() const {
        SessionSnapshot snapshot;
        CHECK(session.read_snapshot(snapshot));
        CHECK(snapshot.prepared && snapshot.running);
        CHECK(snapshot.publication_revision % 2 == 0);
        CHECK(snapshot.fault_flags == 0 && snapshot.recovery_count == 0);
        CHECK(snapshot.rejected_commands == 0 && snapshot.discarded_commands == 0);
        CHECK(snapshot.queue_overflows == 0 && snapshot.last_core_status == Status::Ok);
        CHECK(is_valid_control_snapshot(snapshot.controls));
        CHECK(std::isfinite(snapshot.peak));
        return snapshot;
    }

    SubmitResult post(const SessionCommand& command) {
        const auto result = session.post(command);
        CHECK(result.ok());
        CHECK(result.sequence == last_sequence + 1);
        last_sequence = result.sequence;
        ++counts.commands;
        return result;
    }

    void actions(const UiActions& actions) {
        CHECK(actions.count <= kUiMaxActions);
        for (const auto& action : actions.span()) {
            const auto* command = std::get_if<SessionCommand>(&action);
            CHECK(command != nullptr);
            const auto submitted = post(*command);
            CHECK(ui.submitted(*command, submitted).count == 0);
        }
    }

    [[nodiscard]] MidiDecoded send(std::uint8_t status, std::uint8_t data1,
                                   std::uint8_t data2, std::uint64_t arrival_ns = 0) {
        const std::array bytes{status, data1, data2};
        CHECK(inbox.push(bytes, arrival_ns) == MidiPushResult::Accepted);
        MidiPacket packet;
        CHECK(inbox.pop(packet));
        CHECK(packet.arrival_ns == arrival_ns);
        const auto decoded = midi.decode(packet);
        CHECK(decoded.status == MidiDecodeStatus::Action);
        CHECK(decoded.arrival_ns == arrival_ns);
        if (const auto* command = std::get_if<SessionCommand>(&decoded.action)) {
            post(*command);
        } else {
            const auto& edit = std::get<MidiParameterEdit>(decoded.action);
            actions(ui.external_parameter(edit.parameter_id, edit.normalized));
        }
        ++counts.packets;
        return decoded;
    }

    [[nodiscard]] std::uint8_t status(std::uint8_t family, std::size_t division) const {
        const auto& routing = midi.routing();
        const std::array channels{routing.upper_channel, routing.lower_channel, routing.pedal_channel};
        CHECK(division < channels.size());
        return static_cast<std::uint8_t>(family | (channels[division] - 1U));
    }

    void note(std::size_t division, std::uint8_t pitch, bool on,
              std::uint8_t velocity = 127, std::uint64_t arrival_ns = 0) {
        static_cast<void>(send(status(on ? 0x90 : 0x80, division), pitch, velocity, arrival_ns));
    }

    void cc(std::size_t division, std::uint8_t controller, std::uint8_t value,
            std::uint64_t arrival_ns = 0) {
        static_cast<void>(send(status(0xB0, division), controller, value, arrival_ns));
    }

    void ui_note(std::size_t division, bool down) {
        CHECK(division < 3);
        actions(ui.activate({UiControlKind::KeyboardTarget, Manual::Upper,
                             DrawbarBank::A, static_cast<std::uint8_t>(division)}));
        actions(ui.key({UiKey::A, down}));
    }

    [[nodiscard]] std::vector<float> render(std::uint32_t frames, bool observe = true) {
        const auto before = read();
        std::vector<float> output(static_cast<std::size_t>(frames) * 2 + 2, sentinel);
        const auto rendered = session.render(frames, std::span<float>{output}.subspan(
            1, static_cast<std::size_t>(frames) * 2));
        CHECK(rendered.ok() && rendered.frames_rendered == frames);
        CHECK(output.front() == sentinel && output.back() == sentinel);
        std::vector<float> mono(frames);
        float peak = frames == 0 ? before.peak : 0.0F;
        for (std::size_t frame = 0; frame < frames; ++frame) {
            const float left = output[1 + 2 * frame];
            const float right = output[2 + 2 * frame];
            CHECK(std::isfinite(left) && std::isfinite(right));
            CHECK(std::bit_cast<std::uint32_t>(left) == std::bit_cast<std::uint32_t>(right));
            mono[frame] = left;
            peak = std::max(peak, std::abs(left));
            counts.stereo_samples += 2;
        }
        const auto after = read();
        CHECK(after.frame_clock == before.frame_clock + frames);
        CHECK(after.publication_revision == before.publication_revision + 2);
        CHECK(after.resolved_sequence == last_sequence);
        CHECK(after.last_applied_sequence == last_sequence);
        CHECK(after.peak == peak);
        if (observe) ui.observe(after);
        ++counts.callbacks;
        return mono;
    }

    void flush(bool observe = true) { static_cast<void>(render(0, observe)); }

    void load(const ControlSnapshot& controls) {
        actions(ui.load_controls(controls));
        flush();
        CHECK(!ui.view().controls_pending);
        CHECK(!ui.view().controls_dirty);
    }

    // A synthetic already-quiescent device retirement. This deliberately does
    // not claim a physical backend close/join or native application's behavior.
    void retire() {
        midi.end_epoch();
        inbox.reset_quiescent();
        for (const auto& command : midi_release_commands()) post(command);
    }
};

[[nodiscard]] bool held(const SessionSnapshot& snapshot, std::size_t division,
                        std::uint8_t wire_pitch) {
    CHECK(division < 3);
    if (division == 2) return snapshot.held_pedals[wire_pitch - kMidiPedalFirstNote];
    return snapshot.held_keys[division][wire_pitch - kMinManualMidiNote];
}

void no_holds(const SessionSnapshot& snapshot) {
    for (const auto& manual : snapshot.held_keys) {
        CHECK(std::none_of(manual.begin(), manual.end(), [](bool value) { return value; }));
    }
    CHECK(std::none_of(snapshot.held_pedals.begin(), snapshot.held_pedals.end(),
                       [](bool value) { return value; }));
}

void repeated_anonymous_owners(const RuntimeProfile& profile) {
    for (std::size_t division = 0; division < 3; ++division) {
        Rig rig(profile);
        rig.load(registration());
        const std::uint8_t pitch = division == 2 ? 48 : 60;
        rig.note(division, pitch, true, 77, 100);
        rig.note(division, pitch, true, 77, 100);
        // Queuing two identical messages does not mutate the live observation.
        no_holds(rig.read());
        static_cast<void>(rig.render(31));
        CHECK(held(rig.read(), division, pitch));
        CHECK(rig.read().peak > 0.0F);
        rig.note(division, pitch, false, 103, 0);
        rig.flush();
        CHECK(held(rig.read(), division, pitch));
        rig.note(division, pitch, true, 0, std::numeric_limits<std::uint64_t>::max());
        CHECK(held(rig.read(), division, pitch));
        rig.flush();
        no_holds(rig.read());
        // An unmatched ordinary release cannot create a hold or recovery.
        rig.note(division, pitch, false, 127);
        rig.flush();
        no_holds(rig.read());
        CHECK(rig.midi.diagnostics().actions == 5);
        CHECK(rig.midi.diagnostics().timestamp_regressions == 2);
        CHECK(rig.read().frame_clock == initial_frame + 31);
    }
}

void distinct_configured_routes(const RuntimeProfile& profile) {
    Rig rig(profile, {16, 1, 9});
    rig.load(registration());
    for (std::size_t division = 0; division < 3; ++division) rig.note(division, 48, true);
    rig.flush();
    auto snapshot = rig.read();
    CHECK(held(snapshot, 0, 48) && held(snapshot, 1, 48) && held(snapshot, 2, 48));
    CHECK(snapshot.held_pedals[12]); // MIDI 48 maps to PedalId 13, not manual index 12.
    rig.cc(1, 123, 127);
    rig.flush();
    snapshot = rig.read();
    CHECK(held(snapshot, 0, 48) && !held(snapshot, 1, 48) && held(snapshot, 2, 48));
    rig.note(0, 48, false, 64);
    rig.flush();
    snapshot = rig.read();
    CHECK(!held(snapshot, 0, 48) && !held(snapshot, 1, 48) && held(snapshot, 2, 48));
    rig.note(2, 48, false, 45);
    rig.flush();
    no_holds(rig.read());
    CHECK(rig.read().frame_clock == initial_frame);
}

enum class MidiRelease { NoteOff, Controller123, Disconnect };

void overlapping_ui_and_midi(const RuntimeProfile& profile) {
    for (std::size_t division = 0; division < 3; ++division) {
        const std::uint8_t pitch = division == 2 ? 36 : 60;
        for (const auto release : {MidiRelease::NoteOff, MidiRelease::Controller123,
                                   MidiRelease::Disconnect}) {
            Rig rig(profile);
            const auto controls = registration();
            rig.load(controls);
            rig.ui_note(division, true);
            rig.note(division, pitch, true);
            rig.note(division, static_cast<std::uint8_t>(pitch + 1), true);
            static_cast<void>(rig.render(23));
            CHECK(held(rig.read(), division, pitch));
            CHECK(held(rig.read(), division, static_cast<std::uint8_t>(pitch + 1)));

            if (release == MidiRelease::NoteOff) {
                rig.note(division, pitch, false, 112);
                rig.note(division, static_cast<std::uint8_t>(pitch + 1), false, 97);
            } else if (release == MidiRelease::Controller123) {
                rig.cc(division, 123, 55);
            } else {
                // A queued old-epoch On and Off must not replay after retirement.
                const std::array<std::uint8_t, 3> old_on{
                    rig.status(0x90, division), static_cast<std::uint8_t>(pitch + 2), 127};
                const std::array<std::uint8_t, 3> old_off{
                    rig.status(0x80, division), pitch, 0};
                CHECK(rig.inbox.push(old_on, 1000) == MidiPushResult::Accepted);
                CHECK(rig.inbox.push(old_off, 1001) == MidiPushResult::Accepted);
                rig.inbox.signal_fault(MidiInboxFault::Disconnected);
                rig.retire();
                CHECK(!rig.midi.active());
                CHECK(rig.inbox.diagnostics().discarded_packets == 2);
                CHECK(rig.inbox.pending() == 0 && rig.inbox.faults() == 0);
            }
            // Successful post is not the release acknowledgment.
            CHECK(held(rig.read(), division, static_cast<std::uint8_t>(pitch + 1)));
            rig.flush();
            CHECK(held(rig.read(), division, pitch));
            CHECK(!held(rig.read(), division, static_cast<std::uint8_t>(pitch + 1)));
            CHECK(rig.read().controls == controls);
            if (release == MidiRelease::Disconnect) {
                CHECK(rig.midi.begin_epoch()); // Only after the actual Session acknowledgment.
                rig.flush();
                CHECK(!held(rig.read(), division, static_cast<std::uint8_t>(pitch + 2)));
            }
            rig.ui_note(division, false);
            rig.flush();
            no_holds(rig.read());
            CHECK(rig.read().frame_clock == initial_frame + 23);
        }

        Rig rig(profile);
        rig.load(registration());
        rig.note(division, pitch, true);
        rig.ui_note(division, true);
        rig.flush();
        rig.actions(rig.ui.release_ui(UiReleaseReason::FocusLost));
        CHECK(rig.ui.resize(kUiMinimumWidth, kUiMinimumHeight));
        CHECK(rig.ui.activate({UiControlKind::Help}).count == 1);
        CHECK(rig.ui.activate({UiControlKind::AudioSettings}).count == 1);
        rig.actions(rig.ui.activate({UiControlKind::EditBank, Manual::Upper, DrawbarBank::A}));
        rig.actions(rig.ui.load_controls(registration()));
        rig.flush();
        CHECK(rig.midi.active() && held(rig.read(), division, pitch));
        rig.ui_note(division, false); // A late physical UI Up is a harmless no-op.
        rig.flush();
        CHECK(held(rig.read(), division, pitch));
        rig.note(division, pitch, false, 68);
        rig.flush();
        no_holds(rig.read());
    }
}

void shared_controls_during_pending_drag(const RuntimeProfile& profile) {
    Rig rig(profile);
    auto initial = registration();
    initial.selected_banks = {DrawbarBank::A, DrawbarBank::A};
    initial.route_enabled[0] = false;
    initial.drawbars[0][0][2] = 2;
    rig.load(initial);
    rig.ui_note(0, true);
    rig.note(0, 60, true);
    rig.flush();
    const auto before = rig.read();
    rig.actions(rig.ui.activate({UiControlKind::EditBank, Manual::Upper, DrawbarBank::A}));
    const UiControlId drawbar{UiControlKind::ManualDrawbar, Manual::Upper, DrawbarBank::A, 2};
    const auto& layout = rig.ui.layout();
    const auto found = std::find_if(layout.controls.begin(), layout.controls.begin() +
        static_cast<std::ptrdiff_t>(layout.control_count), [&](const auto& control) {
            return control.id == drawbar;
        });
    CHECK(found != layout.controls.begin() + static_cast<std::ptrdiff_t>(layout.control_count));
    const auto track = found->track;
    const UiPoint low{track.x + track.width * 0.5F, track.y + track.height * 0.75F};
    const UiPoint middle{track.x + track.width * 0.5F, track.y + track.height * 0.5F};
    CHECK(ui_hit_test(layout, low) == drawbar);
    rig.actions(rig.ui.pointer({UiPointerKind::Down, low}));
    CHECK(rig.ui.view().pointer_captured && rig.ui.view().controls_pending);
    CHECK(rig.ui.view().controls.drawbars[0][0][2] == 6);
    const auto focus = rig.ui.view().focus;
    const auto edited_banks = rig.ui.view().edited_banks;
    rig.cc(0, 16, 127); // Fixed B-bank target despite edited/sounding A and Cancel.
    rig.cc(1, 24, 64);
    rig.cc(2, 17, 127);
    rig.cc(1, 11, 95);
    CHECK(rig.ui.view().focus == focus && rig.ui.view().edited_banks == edited_banks);
    CHECK(rig.ui.view().pointer_captured);
    rig.actions(rig.ui.pointer({UiPointerKind::Move, middle}));

    auto expected = initial;
    expected.drawbars[0][0][2] = 4;
    expected.drawbars[0][1][0] = 8;
    expected.drawbars[1][1][8] = 4;
    expected.pedal_drawbars[1] = 8;
    expected.expression = 95.0 / 127.0;
    CHECK(rig.ui.view().controls == expected);
    CHECK(rig.ui.view().controls_dirty && rig.ui.view().controls_pending);
    rig.ui.observe(before); // A real old publication cannot overwrite desired edits.
    CHECK(rig.ui.view().controls == expected);
    CHECK(rig.read().controls == initial);
    rig.flush(false);
    const auto first_ack = rig.read();
    CHECK(first_ack.controls == expected && held(first_ack, 0, 60));
    CHECK(first_ack.frame_clock == before.frame_clock);

    // Queue new intent before observing the prior applied acknowledgment.
    rig.cc(0, 11, 32);
    rig.cc(0, 16, 0);
    rig.actions(rig.ui.pointer({UiPointerKind::Move, low}));
    expected.expression = 32.0 / 127.0;
    expected.drawbars[0][1][0] = 0;
    expected.drawbars[0][0][2] = 6;
    rig.ui.observe(first_ack);
    CHECK(rig.ui.view().controls_pending);
    CHECK(rig.ui.view().controls == expected);
    CHECK(rig.ui.view().applied.controls == first_ack.controls);
    rig.actions(rig.ui.pointer({UiPointerKind::Up, low}));
    CHECK(!rig.ui.view().pointer_captured);
    rig.flush();
    CHECK(!rig.ui.view().controls_pending);
    CHECK(rig.ui.view().controls == expected && rig.read().controls == expected);
    CHECK(rig.ui.view().controls_dirty);
    CHECK(held(rig.read(), 0, 60));
    CHECK(rig.read().frame_clock == before.frame_clock);
    rig.ui.mark_saved(expected);
    CHECK(!rig.ui.view().controls_dirty);
    rig.cc(2, 11, 127);
    CHECK(rig.ui.view().controls_dirty);
    rig.flush();
    CHECK(rig.read().controls.expression == 1.0);
}

[[nodiscard]] Event event(EventType type, Manual manual, std::uint8_t index, double value = 0) {
    return {0, type, manual, index, value};
}

void physical(Engine& reference, std::initializer_list<Event> events) {
    const auto result = reference.process(0, {}, {events.begin(), events.size()});
    CHECK(result.ok() && result.events_consumed == events.size());
}

void compare_reference(const SessionSnapshot& actual, const Engine& reference) {
    CHECK(actual.controls == reference.controls_snapshot());
    CHECK(actual.frame_clock == reference.frame_clock());
    CHECK(actual.sample_rate == reference.sample_rate());
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        for (std::size_t key = 0; key < kManualKeyCount; ++key) {
            CHECK(actual.held_keys[manual][key] == reference.key_down(
                static_cast<Manual>(manual), static_cast<std::uint32_t>(key) + kMinManualMidiNote));
        }
    }
    for (std::size_t pedal = 0; pedal < kPedalCount; ++pedal) {
        CHECK(actual.held_pedals[pedal] == reference.pedal_down(
            PedalId{static_cast<std::uint8_t>(pedal + 1)}));
    }
}

// Absolute event boundaries are shared; only subdivision between them varies.
// The reference uses written physical transitions, not the decoder/Session
// dispatcher or copied snapshots. This also tests audible routes and phase
// continuation through silence, mixed ownership and scoped release.
[[nodiscard]] std::vector<float> score(const RuntimeProfile& profile, double rate,
                                       bool fragmented, bool skewed_timestamps,
                                       std::uint8_t velocity) {
    Rig rig(profile, {}, rate);
    Engine reference;
    CHECK(reference.prepare(profile, {rate, 1024, phase_seed, initial_frame}) == Status::Ok);
    auto controls = registration();
    rig.load(controls);
    CHECK(reference.restore_controls(controls));
    constexpr std::array<std::uint64_t, 8> timestamps{
        std::numeric_limits<std::uint64_t>::max(), 0, 0, 91, 91, 3,
        std::numeric_limits<std::uint64_t>::max() - 1, 1};
    std::size_t packet_number = 0;
    const auto time = [&]() {
        const auto index = packet_number++;
        return skewed_timestamps ? timestamps[index % timestamps.size()] :
                                   static_cast<std::uint64_t>(index + 100);
    };
    const auto note = [&](std::size_t division, std::uint8_t pitch, bool on,
                          std::uint8_t value) { rig.note(division, pitch, on, value, time()); };
    const auto cc = [&](std::size_t division, std::uint8_t controller, std::uint8_t value) {
        rig.cc(division, controller, value, time());
    };
    constexpr std::array<std::uint32_t, 7> durations{97, 193, 127, 251, 113, 89, 67};
    constexpr std::array<std::uint32_t, 5> partitions{1, 7, 32, 9, 64};
    std::size_t partition_index = 0;
    std::vector<float> complete;
    for (std::size_t stage = 0; stage < durations.size(); ++stage) {
        switch (stage) {
        case 0:
            note(0, 60, true, velocity);
            note(0, 60, true, velocity);
            rig.ui_note(0, true);
            note(1, 64, true, velocity);
            note(2, 48, true, velocity);
            physical(reference, {event(EventType::NoteOn, Manual::Upper, 60, velocity),
                                 event(EventType::NoteOn, Manual::Lower, 64, velocity),
                                 event(EventType::PedalOn, Manual::Lower, 13, velocity)});
            no_holds(rig.read());
            break;
        case 1:
            note(0, 60, false, 73);
            note(1, 64, false, 103);
            physical(reference, {event(EventType::NoteOff, Manual::Lower, 64)});
            break;
        case 2:
            note(0, 60, true, 0);
            cc(2, 123, 99);
            cc(0, 16, 127);
            cc(2, 11, 96);
            controls.drawbars[0][1][0] = 8;
            controls.expression = 96.0 / 127.0;
            CHECK(reference.restore_controls(controls));
            physical(reference, {event(EventType::PedalOff, Manual::Lower, 13)});
            break;
        case 3:
            rig.ui_note(0, false);
            note(1, 67, true, velocity);
            physical(reference, {event(EventType::NoteOff, Manual::Upper, 60),
                                 event(EventType::NoteOn, Manual::Lower, 67, velocity)});
            break;
        case 4:
            cc(1, 123, 0);
            note(0, 72, true, velocity);
            note(0, 72, false, 127);
            note(0, 72, true, velocity);
            physical(reference, {event(EventType::NoteOff, Manual::Lower, 67),
                                 event(EventType::NoteOn, Manual::Upper, 72, velocity),
                                 event(EventType::NoteOff, Manual::Upper, 72),
                                 event(EventType::NoteOn, Manual::Upper, 72, velocity)});
            break;
        case 5:
            rig.retire();
            physical(reference, {event(EventType::NoteOff, Manual::Upper, 72)});
            break;
        default: break;
        }

        const auto before_flush = rig.read().frame_clock;
        rig.flush();
        CHECK(rig.read().frame_clock == before_flush);
        compare_reference(rig.read(), reference);
        auto remaining = durations[stage];
        while (remaining != 0) {
            const auto frames = fragmented ?
                std::min(remaining, partitions[partition_index++ % partitions.size()]) : remaining;
            auto actual = rig.render(frames);
            std::vector<float> expected(frames);
            CHECK(reference.process(frames, expected, {}).ok());
            for (std::size_t frame = 0; frame < frames; ++frame) {
                CHECK(std::bit_cast<std::uint32_t>(actual[frame]) ==
                      std::bit_cast<std::uint32_t>(expected[frame]));
                ++counts.reference_samples;
            }
            compare_reference(rig.read(), reference);
            complete.insert(complete.end(), actual.begin(), actual.end());
            remaining -= frames;
        }
    }
    CHECK(rig.midi.diagnostics().actions == packet_number);
    CHECK(skewed_timestamps ? rig.midi.diagnostics().timestamp_regressions > 0 :
                            rig.midi.diagnostics().timestamp_regressions == 0);
    CHECK(std::any_of(complete.begin(), complete.end(), [](float value) { return value != 0; }));
    CHECK(std::all_of(complete.end() - durations.back(), complete.end(),
                      [](float value) { return value == 0; }));
    CHECK(rig.read().frame_clock == initial_frame + complete.size());
    no_holds(rig.read());
    return complete;
}

void timestamp_velocity_and_partition_rendering(const RuntimeProfile& profile) {
    for (const auto rate : {44100.0, 48000.0, 96000.0}) {
        const auto baseline = score(profile, rate, false, false, 127);
        const auto fragmented = score(profile, rate, true, true, 127);
        const auto low_velocity = score(profile, rate, false, true, 1);
        CHECK(baseline.size() == fragmented.size() && baseline.size() == low_velocity.size());
        for (std::size_t frame = 0; frame < baseline.size(); ++frame) {
            CHECK(std::bit_cast<std::uint32_t>(baseline[frame]) ==
                  std::bit_cast<std::uint32_t>(fragmented[frame]));
            CHECK(std::bit_cast<std::uint32_t>(baseline[frame]) ==
                  std::bit_cast<std::uint32_t>(low_velocity[frame]));
            counts.partition_samples += 2;
        }
    }
}

} // namespace

int main() {
    const auto profile = load_test_profile();
    repeated_anonymous_owners(profile);
    distinct_configured_routes(profile);
    overlapping_ui_and_midi(profile);
    shared_controls_during_pending_drag(profile);
    timestamp_velocity_and_partition_rendering(profile);
    std::cout << "MIDI/Session/UI acceptance: " << counts.scenarios << " scenarios, "
              << counts.packets << " decoded packets, " << counts.commands << " commands, "
              << counts.callbacks << " callbacks, " << counts.stereo_samples
              << " finite stereo samples, " << counts.reference_samples
              << " physical-reference sample comparisons, " << counts.partition_samples
              << " timestamp/velocity/partition sample comparisons\n";
}
