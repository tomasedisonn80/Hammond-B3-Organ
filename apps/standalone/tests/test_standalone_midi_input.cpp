#include "MidiInput.h"
#include "TestSupport.h"

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <limits>
#include <span>
#include <type_traits>
#include <variant>

namespace {

using namespace hammond;
using namespace hammond::standalone;

// This oracle follows docs/MIDI_INPUT.md. Controller identities and owner
// namespaces below are literal contract values, not a decoder-generated table.
static_assert(kMidiInputModelId == "standalone-three-division-midi-v1");
static_assert(kMidiInboxCapacity == 256);
static_assert(kMidiDrainBudget == 32);
static_assert((kMidiOwnerChannels == std::array<std::uint8_t, 3>{1, 2, 3}));
static_assert(kMidiPedalFirstNote == 36 && kMidiPedalLastNote == 60);
static_assert(!std::is_copy_constructible_v<MidiInbox>);
static_assert(!std::is_move_constructible_v<MidiInbox>);

constexpr auto maximum_time = std::numeric_limits<std::uint64_t>::max();

enum class Division { Upper, Lower, Pedals };

struct DivisionCase {
    Division division;
    std::uint8_t note_status;
    std::uint8_t cc_status;
    std::uint8_t last_pitch;
    std::uint32_t first_drawbar_id;
};

constexpr std::array<DivisionCase, 3> divisions{{
    {Division::Upper, 0x90, 0xB0, 96, 4112},
    {Division::Lower, 0x91, 0xB1, 96, 4144},
    {Division::Pedals, 0x92, 0xB2, 60, 16384},
}};

[[nodiscard]] constexpr std::uint8_t byte(unsigned value) noexcept {
    return static_cast<std::uint8_t>(value);
}

[[nodiscard]] constexpr MidiPacket message(std::uint8_t status,
                                           std::uint8_t first,
                                           std::uint8_t second,
                                           std::uint64_t arrival = 0) noexcept {
    return {{status, first, second}, 3, arrival};
}

void same_diagnostics(const MidiInputDiagnostics& actual,
                      const MidiInputDiagnostics& expected) {
    CHECK(actual.packets == expected.packets);
    CHECK(actual.actions == expected.actions);
    CHECK(actual.unsupported == expected.unsupported);
    CHECK(actual.unmapped_channels == expected.unmapped_channels);
    CHECK(actual.out_of_range == expected.out_of_range);
    CHECK(actual.malformed == expected.malformed);
    CHECK(actual.inactive == expected.inactive);
    CHECK(actual.timestamp_regressions == expected.timestamp_regressions);
    CHECK(actual.epochs == expected.epochs);
}

// The caller supplies the disposition and regression oracle. Check every
// counter delta, including counters that must remain unchanged after rejection.
[[nodiscard]] MidiDecoded decode(MidiInput& input, const MidiPacket& packet,
                                 MidiDecodeStatus status,
                                 bool regressed = false) {
    auto expected = input.diagnostics();
    ++expected.packets;
    switch (status) {
    case MidiDecodeStatus::Action: ++expected.actions; break;
    case MidiDecodeStatus::Unsupported: ++expected.unsupported; break;
    case MidiDecodeStatus::UnmappedChannel: ++expected.unmapped_channels; break;
    case MidiDecodeStatus::OutOfRange: ++expected.out_of_range; break;
    case MidiDecodeStatus::Malformed: ++expected.malformed; break;
    case MidiDecodeStatus::Inactive: ++expected.inactive; break;
    }
    if (regressed) ++expected.timestamp_regressions;
    const auto result = input.decode(packet);
    CHECK(result.status == status);
    CHECK(result.timestamp_regressed == regressed);
    if (status != MidiDecodeStatus::Inactive) CHECK(result.arrival_ns == packet.arrival_ns);
    same_diagnostics(input.diagnostics(), expected);
    // Non-Action payloads are deliberately never inspected or dispatched.
    return result;
}

[[nodiscard]] const PerformanceInputEvent& musical_event(const MidiDecoded& decoded) {
    CHECK(decoded.status == MidiDecodeStatus::Action);
    CHECK(std::holds_alternative<SessionCommand>(decoded.action));
    const auto& command = std::get<SessionCommand>(decoded.action);
    CHECK(std::holds_alternative<PerformanceInputEvent>(command));
    return std::get<PerformanceInputEvent>(command);
}

void note(const MidiDecoded& decoded, Division division, bool on,
          std::uint8_t pitch, std::uint8_t velocity) {
    const auto& input = musical_event(decoded);
    if (division == Division::Pedals) {
        CHECK(std::holds_alternative<PedalNoteEvent>(input));
        const auto& event = std::get<PedalNoteEvent>(input);
        CHECK(event.offset == 0);
        CHECK(event.kind == (on ? PedalNoteKind::On : PedalNoteKind::Off));
        CHECK(event.bus == 0 && event.channel == 3);
        CHECK(event.pedal.value == pitch - 35);
        CHECK(event.velocity == velocity && event.note_id == -1);
    } else {
        CHECK(std::holds_alternative<HostNoteEvent>(input));
        const auto& event = std::get<HostNoteEvent>(input);
        CHECK(event.offset == 0);
        CHECK(event.kind == (on ? HostNoteKind::On : HostNoteKind::Off));
        CHECK(event.bus == (division == Division::Upper ? 0 : 1));
        CHECK(event.channel == (division == Division::Upper ? 1 : 2));
        CHECK(event.midi_note == pitch);
        CHECK(event.velocity == velocity && event.note_id == -1);
    }
}

void release(const SessionCommand& command, Division division) {
    // This also excludes Panic, ReleaseUiNotes and a whole control snapshot.
    CHECK(std::holds_alternative<PerformanceInputEvent>(command));
    const auto& input = std::get<PerformanceInputEvent>(command);
    if (division == Division::Pedals) {
        CHECK(std::holds_alternative<PedalNoteEvent>(input));
        const auto& event = std::get<PedalNoteEvent>(input);
        CHECK(event.offset == 0 && event.kind == PedalNoteKind::AllNotesOff);
        CHECK(event.bus == 0 && event.channel == 3);
        CHECK(event.pedal.value == 0 && event.velocity == 0 && event.note_id == -1);
    } else {
        CHECK(std::holds_alternative<HostNoteEvent>(input));
        const auto& event = std::get<HostNoteEvent>(input);
        CHECK(event.offset == 0 && event.kind == HostNoteKind::AllNotesOff);
        CHECK(event.bus == (division == Division::Upper ? 0 : 1));
        CHECK(event.channel == (division == Division::Upper ? 1 : 2));
        CHECK(event.midi_note == 0 && event.velocity == 0 && event.note_id == -1);
    }
}

void release(const MidiDecoded& decoded, Division division) {
    CHECK(decoded.status == MidiDecodeStatus::Action);
    CHECK(std::holds_alternative<SessionCommand>(decoded.action));
    release(std::get<SessionCommand>(decoded.action), division);
}

void parameter(const MidiDecoded& decoded, std::uint32_t id, unsigned value) {
    CHECK(decoded.status == MidiDecodeStatus::Action);
    CHECK(std::holds_alternative<MidiParameterEdit>(decoded.action));
    const auto& edit = std::get<MidiParameterEdit>(decoded.action);
    CHECK(edit.parameter_id == id);
    CHECK(edit.normalized == static_cast<double>(value) / 127.0);
}

void routing_and_epoch_transactions() {
    CHECK(valid_midi_routing({}));
    // Exhaust all in-range combinations, including every duplicate pairing.
    for (unsigned upper = 1; upper <= 16; ++upper) {
        for (unsigned lower = 1; lower <= 16; ++lower) {
            for (unsigned pedals = 1; pedals <= 16; ++pedals) {
                const MidiRouting routing{byte(upper), byte(lower), byte(pedals)};
                CHECK(valid_midi_routing(routing) ==
                      (upper != lower && upper != pedals && lower != pedals));
            }
        }
    }
    // Every representable out-of-range channel rejects in every field.
    for (unsigned channel = 0; channel <= 255; ++channel) {
        if (channel >= 1 && channel <= 16) continue;
        CHECK(!valid_midi_routing({byte(channel), 2, 3}));
        CHECK(!valid_midi_routing({1, byte(channel), 3}));
        CHECK(!valid_midi_routing({1, 2, byte(channel)}));
    }

    constexpr std::array<MidiRouting, 13> invalid{{
        {0, 2, 3}, {1, 0, 3}, {1, 2, 0},
        {17, 2, 3}, {1, 17, 3}, {1, 2, 17},
        {255, 2, 3}, {1, 255, 3}, {1, 2, 255},
        {1, 1, 3}, {1, 2, 1}, {1, 2, 2}, {16, 16, 16},
    }};
    MidiInput input;
    CHECK(!input.active() && input.routing() == MidiRouting{});
    same_diagnostics(input.diagnostics(), {});
    for (const auto& routing : invalid) {
        CHECK(!input.begin_epoch(routing));
        CHECK(!input.active() && input.routing() == MidiRouting{});
        same_diagnostics(input.diagnostics(), {});
    }
    (void)decode(input, message(0x90, 60, 100, maximum_time), MidiDecodeStatus::Inactive);
    (void)decode(input, MidiPacket{{0, 0xFF, 0xFF}, 255, 0}, MidiDecodeStatus::Inactive);
    CHECK(input.begin_epoch({16, 4, 9}));
    CHECK(input.active() && (input.routing() == MidiRouting{16, 4, 9}));
    CHECK(input.diagnostics().epochs == 1);
    note(decode(input, message(0x9F, 60, 70, 100), MidiDecodeStatus::Action),
         Division::Upper, true, 60, 70);
    const auto before_rejection = input.diagnostics();
    for (const auto& routing : invalid) {
        CHECK(!input.begin_epoch(routing));
        CHECK(input.active() && (input.routing() == MidiRouting{16, 4, 9}));
        same_diagnostics(input.diagnostics(), before_rejection);
    }
    CHECK(!input.begin_epoch());
    CHECK(!input.begin_epoch({16, 4, 9}));
    same_diagnostics(input.diagnostics(), before_rejection);
    // Rejection must retain the previous timing observation as well as routing.
    note(decode(input, message(0x8F, 60, 127, 99), MidiDecodeStatus::Action, true),
         Division::Upper, false, 60, 0);
    const auto before_end = input.diagnostics();
    input.end_epoch();
    input.end_epoch();
    CHECK(!input.active() && (input.routing() == MidiRouting{16, 4, 9}));
    same_diagnostics(input.diagnostics(), before_end);
    CHECK(!input.begin_epoch({4, 4, 9}));
    CHECK(!input.active() && (input.routing() == MidiRouting{16, 4, 9}));
    same_diagnostics(input.diagnostics(), before_end);
    (void)decode(input, message(0x9F, 60, 127, maximum_time), MidiDecodeStatus::Inactive);
    const auto before_restart = input.diagnostics();
    CHECK(input.begin_epoch({1, 16, 2}));
    auto restarted = before_restart;
    ++restarted.epochs;
    same_diagnostics(input.diagnostics(), restarted);
    // Neither the previous epoch nor the inactive call supplies this baseline.
    note(decode(input, message(0x9F, 96, 1, 0), MidiDecodeStatus::Action),
         Division::Lower, true, 96, 1);
    (void)decode(input, message(0x98, 60, 100, 0), MidiDecodeStatus::UnmappedChannel);
}

void all_wire_choices_and_note_domains() {
    // Explicit permutations cover every wire choice for each division; the
    // final three rows exercise channel 16 as pedals, lower and upper.
    constexpr std::array<MidiRouting, 16> configurations{{
        {1, 2, 3}, {2, 3, 4}, {3, 4, 5}, {4, 5, 6},
        {5, 6, 7}, {6, 7, 8}, {7, 8, 9}, {8, 9, 10},
        {9, 10, 11}, {10, 11, 12}, {11, 12, 13}, {12, 13, 14},
        {13, 14, 15}, {14, 15, 16}, {15, 16, 1}, {16, 1, 2},
    }};
    for (const auto& routing : configurations) {
        MidiInput input;
        CHECK(input.begin_epoch(routing));
        const std::array<std::uint8_t, 3> wires{
            routing.upper_channel, routing.lower_channel, routing.pedal_channel};
        for (std::size_t index = 0; index < divisions.size(); ++index) {
            const auto& expected = divisions[index];
            const auto status = byte(0x90U + wires[index] - 1U);
            const auto cc = byte(0xB0U + wires[index] - 1U);
            for (const auto pitch : {std::uint8_t{36}, expected.last_pitch}) {
                note(decode(input, message(status, pitch, 127), MidiDecodeStatus::Action),
                     expected.division, true, pitch, 127);
                note(decode(input, message(status, pitch, 0), MidiDecodeStatus::Action),
                     expected.division, false, pitch, 0);
                note(decode(input, message(byte(status - 0x10U), pitch, 1), MidiDecodeStatus::Action),
                     expected.division, false, pitch, 0);
            }
            (void)decode(input, message(status, 35, 100), MidiDecodeStatus::OutOfRange);
            (void)decode(input, message(status, byte(expected.last_pitch + 1U), 100),
                         MidiDecodeStatus::OutOfRange);
            parameter(decode(input, message(cc, 11, 64), MidiDecodeStatus::Action), 8192, 64);
            parameter(decode(input, message(cc, 16, 64), MidiDecodeStatus::Action),
                      expected.first_drawbar_id, 64);
            release(decode(input, message(cc, 123, 127), MidiDecodeStatus::Action),
                    expected.division);
        }
        for (unsigned wire = 1; wire <= 16; ++wire) {
            if (wire == routing.upper_channel || wire == routing.lower_channel ||
                wire == routing.pedal_channel) continue;
            (void)decode(input, message(byte(0x90U + wire - 1U), 60, 100),
                         MidiDecodeStatus::UnmappedChannel);
            (void)decode(input, message(byte(0xB0U + wire - 1U), 11, 127),
                         MidiDecodeStatus::UnmappedChannel);
            (void)decode(input, message(byte(0xB0U + wire - 1U), 123, 0),
                         MidiDecodeStatus::UnmappedChannel);
        }
    }

    MidiInput input;
    CHECK(input.begin_epoch());
    for (const auto& expected : divisions) {
        for (unsigned pitch = 0; pitch <= 127; ++pitch) {
            const bool in_range = pitch >= 36 && pitch <= expected.last_pitch;
            const auto status = in_range ? MidiDecodeStatus::Action : MidiDecodeStatus::OutOfRange;
            const auto on = decode(input, message(expected.note_status, byte(pitch), 100), status);
            const auto zero = decode(input, message(expected.note_status, byte(pitch), 0), status);
            const auto off = decode(input, message(byte(expected.note_status - 0x10U), byte(pitch), 127), status);
            if (in_range) {
                note(on, expected.division, true, byte(pitch), 100);
                note(zero, expected.division, false, byte(pitch), 0);
                note(off, expected.division, false, byte(pitch), 0);
            }
        }
        for (unsigned velocity = 0; velocity <= 127; ++velocity) {
            for (const auto pitch : {std::uint8_t{36}, expected.last_pitch}) {
                note(decode(input, message(expected.note_status, pitch, byte(velocity)), MidiDecodeStatus::Action),
                     expected.division, velocity != 0, pitch, byte(velocity));
                note(decode(input, message(byte(expected.note_status - 0x10U), pitch, byte(velocity)), MidiDecodeStatus::Action),
                     expected.division, false, pitch, 0);
            }
        }
    }
    // Unmapped channels win over pitch-domain decisions, for all 128 pitches.
    for (unsigned wire = 4; wire <= 16; ++wire) {
        for (unsigned pitch = 0; pitch <= 127; ++pitch) {
            for (const unsigned family : {0x80U, 0x90U}) {
                (void)decode(input, message(byte(family + wire - 1U), byte(pitch), 127),
                             MidiDecodeStatus::UnmappedChannel);
            }
        }
    }
}

void repeated_anonymous_notes_and_scoped_releases() {
    MidiInput input;
    CHECK(input.begin_epoch());
    for (const auto& expected : divisions) {
        const auto off_status = byte(expected.note_status - 0x10U);
        // The decoder has no owner ledger: unmatched releases and identical
        // anonymous repetitions all remain distinct successful commands.
        note(decode(input, message(off_status, 48, 64), MidiDecodeStatus::Action),
             expected.division, false, 48, 0);
        for (unsigned repetition = 0; repetition < 3; ++repetition) {
            note(decode(input, message(expected.note_status, 48, 100), MidiDecodeStatus::Action),
                 expected.division, true, 48, 100);
        }
        note(decode(input, message(off_status, 48, 1), MidiDecodeStatus::Action),
             expected.division, false, 48, 0);
        note(decode(input, message(expected.note_status, 48, 0), MidiDecodeStatus::Action),
             expected.division, false, 48, 0);
        note(decode(input, message(off_status, 48, 127), MidiDecodeStatus::Action),
             expected.division, false, 48, 0);
        note(decode(input, message(off_status, 48, 0), MidiDecodeStatus::Action),
             expected.division, false, 48, 0);
    }
    CHECK(input.diagnostics().actions == 24);
    const auto before = input.diagnostics();
    const auto commands = midi_release_commands();
    CHECK(commands.size() == 3);
    release(commands[0], Division::Upper);
    release(commands[1], Division::Lower);
    release(commands[2], Division::Pedals);
    same_diagnostics(input.diagnostics(), before);
    input.end_epoch();
    const auto inactive_commands = midi_release_commands();
    release(inactive_commands[0], Division::Upper);
    release(inactive_commands[1], Division::Lower);
    release(inactive_commands[2], Division::Pedals);
    same_diagnostics(input.diagnostics(), before);
}

void every_supported_controller_value() {
    struct Mapping { std::uint8_t status; std::uint8_t controller; std::uint32_t id; };
    constexpr std::array<Mapping, 23> mappings{{
        {0xB0, 11, 8192}, {0xB1, 11, 8192}, {0xB2, 11, 8192},
        {0xB0, 16, 4112}, {0xB0, 17, 4113}, {0xB0, 18, 4114},
        {0xB0, 19, 4115}, {0xB0, 20, 4116}, {0xB0, 21, 4117},
        {0xB0, 22, 4118}, {0xB0, 23, 4119}, {0xB0, 24, 4120},
        {0xB1, 16, 4144}, {0xB1, 17, 4145}, {0xB1, 18, 4146},
        {0xB1, 19, 4147}, {0xB1, 20, 4148}, {0xB1, 21, 4149},
        {0xB1, 22, 4150}, {0xB1, 23, 4151}, {0xB1, 24, 4152},
        {0xB2, 16, 16384}, {0xB2, 17, 16385},
    }};
    MidiInput input;
    CHECK(input.begin_epoch());
    for (const auto& mapping : mappings) {
        for (unsigned value = 0; value <= 127; ++value) {
            parameter(decode(input, message(mapping.status, mapping.controller, byte(value)),
                             MidiDecodeStatus::Action), mapping.id, value);
        }
    }
    for (const auto& expected : divisions) {
        for (unsigned value = 0; value <= 127; ++value) {
            release(decode(input, message(expected.cc_status, 123, byte(value)), MidiDecodeStatus::Action),
                    expected.division);
        }
        for (unsigned controller = 0; controller <= 127; ++controller) {
            const bool mapped = std::any_of(mappings.begin(), mappings.end(),
                [&](const Mapping& mapping) {
                    return mapping.status == expected.cc_status && mapping.controller == controller;
                });
            if (mapped || controller == 123) continue;
            for (const unsigned value : {0U, 63U, 64U, 127U}) {
                (void)decode(input, message(expected.cc_status, byte(controller), byte(value)),
                             MidiDecodeStatus::Unsupported);
            }
        }
    }
    CHECK(input.diagnostics().actions == 26U * 128U);
    // Controllers on an unselected wire are unmapped even when the family or
    // controller would otherwise be unsupported (including CC120 and CC121).
    for (unsigned channel = 3; channel < 16; ++channel) {
        for (unsigned controller = 0; controller <= 127; ++controller) {
            (void)decode(input, message(byte(0xB0U + channel), byte(controller), 64),
                         MidiDecodeStatus::UnmappedChannel);
        }
    }
}

void complete_message_admission_order() {
    MidiInput input;
    CHECK(input.begin_epoch());
    for (unsigned first = 0; first < 0x80; ++first) {
        for (const std::uint8_t size : {std::uint8_t{1}, std::uint8_t{2}, std::uint8_t{3}}) {
            (void)decode(input, MidiPacket{{byte(first), 60, 100}, size, 0}, MidiDecodeStatus::Malformed);
        }
    }
    for (unsigned status = 0x80; status <= 0xEF; ++status) {
        const unsigned family = status & 0xF0U;
        const std::uint8_t required = (family == 0xC0 || family == 0xD0) ? 2 : 3;
        for (const std::uint8_t size : {std::uint8_t{0}, std::uint8_t{1}, std::uint8_t{2},
                                        std::uint8_t{3}, std::uint8_t{4}, std::uint8_t{255}}) {
            if (size == required) continue;
            (void)decode(input, MidiPacket{{byte(status), 60, 100}, size, 0}, MidiDecodeStatus::Malformed);
        }
        for (const auto high : {std::uint8_t{0x80}, std::uint8_t{0xFF}}) {
            (void)decode(input, MidiPacket{{byte(status), high, 1}, required, 0}, MidiDecodeStatus::Malformed);
            if (required == 3) {
                (void)decode(input, MidiPacket{{byte(status), 60, high}, required, 0}, MidiDecodeStatus::Malformed);
            }
        }
        if (family == 0xA0 || family == 0xC0 || family == 0xD0 || family == 0xE0) {
            const auto expected = (status & 0x0FU) < 3
                ? MidiDecodeStatus::Unsupported : MidiDecodeStatus::UnmappedChannel;
            // An unused third slot must not cause a valid two-byte packet to
            // fail seven-bit data admission.
            const auto last = required == 2 ? std::uint8_t{0xFF} : std::uint8_t{127};
            (void)decode(input, MidiPacket{{byte(status), 127, last}, required, 0}, expected);
            (void)decode(input, MidiPacket{{byte(status), 0, 0}, required, 0}, expected);
        }
    }
    for (unsigned status = 0xF0; status <= 0xFF; ++status) {
        for (const std::uint8_t size : {std::uint8_t{1}, std::uint8_t{2}, std::uint8_t{3}}) {
            (void)decode(input, MidiPacket{{byte(status), 0xFF, 0x80}, size, 0}, MidiDecodeStatus::Unsupported);
        }
        for (const std::uint8_t size : {std::uint8_t{0}, std::uint8_t{4}, std::uint8_t{255}}) {
            (void)decode(input, MidiPacket{{byte(status), 0, 0}, size, 0}, MidiDecodeStatus::Malformed);
        }
    }
    // Consecutive fragments are never assembled into a running-status stream.
    (void)decode(input, MidiPacket{{0x90, 0, 0}, 1, 0}, MidiDecodeStatus::Malformed);
    (void)decode(input, MidiPacket{{60, 100, 0}, 2, 0}, MidiDecodeStatus::Malformed);
    note(decode(input, message(0x90, 60, 100), MidiDecodeStatus::Action), Division::Upper, true, 60, 100);
    // A malformed release does not poison admission of the next complete one.
    (void)decode(input, message(0x80, 60, 0x80), MidiDecodeStatus::Malformed);
    note(decode(input, message(0x80, 60, 127), MidiDecodeStatus::Action), Division::Upper, false, 60, 0);
}

void receipt_order_and_timestamp_history() {
    MidiInput input;
    (void)decode(input, message(0x90, 36, 1, maximum_time), MidiDecodeStatus::Inactive);
    CHECK(input.begin_epoch());
    note(decode(input, message(0x90, 36, 1, 0), MidiDecodeStatus::Action), Division::Upper, true, 36, 1);
    note(decode(input, message(0x90, 96, 127, 0), MidiDecodeStatus::Action), Division::Upper, true, 96, 127);
    (void)decode(input, message(0xB0, 120, 0, 100), MidiDecodeStatus::Unsupported);
    (void)decode(input, message(0x9F, 60, 1, 99), MidiDecodeStatus::UnmappedChannel, true);
    (void)decode(input, MidiPacket{{0x80, 60, 0xFF}, 3, 50}, MidiDecodeStatus::Malformed, true);
    (void)decode(input, message(0x92, 61, 1, 50), MidiDecodeStatus::OutOfRange);
    // Numeric future time emits immediately at offset zero; it is no deadline.
    note(decode(input, message(0x92, 36, 100, maximum_time), MidiDecodeStatus::Action),
         Division::Pedals, true, 36, 100);
    note(decode(input, message(0x82, 36, 127, 7), MidiDecodeStatus::Action, true),
         Division::Pedals, false, 36, 0);
    // Compare with 7, not the earlier maximum: this must not be a regression.
    note(decode(input, message(0x90, 36, 0, 8), MidiDecodeStatus::Action), Division::Upper, false, 36, 0);
    (void)decode(input, MidiPacket{{0xF8, 0, 0}, 1, 0}, MidiDecodeStatus::Unsupported, true);
    (void)decode(input, MidiPacket{{0xFE, 0, 0}, 1, 0}, MidiDecodeStatus::Unsupported);
    same_diagnostics(input.diagnostics(), MidiInputDiagnostics{
        .packets = 12, .actions = 5, .unsupported = 3, .unmapped_channels = 1,
        .out_of_range = 1, .malformed = 1, .inactive = 1,
        .timestamp_regressions = 4, .epochs = 1});
    input.end_epoch();
    CHECK(input.begin_epoch());
    note(decode(input, message(0x80, 96, 0, 0), MidiDecodeStatus::Action), Division::Upper, false, 96, 0);
    CHECK(input.diagnostics().timestamp_regressions == 4 && input.diagnostics().epochs == 2);

    struct Observation { MidiPacket packet; MidiDecodeStatus status; };
    const std::array<Observation, 4> observations{{
        {message(0xB0, 121, 0, 10), MidiDecodeStatus::Unsupported},
        {message(0x9F, 60, 1, 10), MidiDecodeStatus::UnmappedChannel},
        {message(0x92, 61, 1, 10), MidiDecodeStatus::OutOfRange},
        {MidiPacket{{0x80, 60, 0x80}, 3, 10}, MidiDecodeStatus::Malformed},
    }};
    for (const auto& observation : observations) {
        note(decode(input, message(0x91, 60, 1, 1000), MidiDecodeStatus::Action),
             Division::Lower, true, 60, 1);
        (void)decode(input, observation.packet, observation.status, true);
        // Every rejected active packet becomes the new observation, even
        // though it contributes no musical action. This compares against 10.
        note(decode(input, message(0x81, 60, 0, 11), MidiDecodeStatus::Action),
             Division::Lower, false, 60, 0);
    }
    CHECK(input.diagnostics().timestamp_regressions == 8);
}

void same_packet(const MidiPacket& actual, const MidiPacket& expected) {
    CHECK(actual.bytes == expected.bytes);
    CHECK(actual.size == expected.size);
    CHECK(actual.arrival_ns == expected.arrival_ns);
}

void inbox_diagnostics(const MidiInbox& inbox, const MidiInboxDiagnostics& expected) {
    const auto actual = inbox.diagnostics();
    CHECK(actual.received_packets == expected.received_packets);
    CHECK(actual.accepted_packets == expected.accepted_packets);
    CHECK(actual.invalid_size_packets == expected.invalid_size_packets);
    CHECK(actual.faulted_packets == expected.faulted_packets);
    CHECK(actual.overflow_events == expected.overflow_events);
    CHECK(actual.popped_packets == expected.popped_packets);
    CHECK(actual.discarded_packets == expected.discarded_packets);
    CHECK(actual.resets == expected.resets);
    CHECK(actual.faults == expected.faults && inbox.faults() == expected.faults);
    // All observations here are quiescent, so these identities are exact.
    CHECK(actual.received_packets == actual.accepted_packets + actual.invalid_size_packets +
          actual.faulted_packets + actual.overflow_events);
    CHECK(actual.accepted_packets == actual.popped_packets + actual.discarded_packets + inbox.pending());
}

constexpr MidiPacket destination_sentinel{{0xDE, 0xAD, 0xBE}, 253, maximum_time - 17};

void no_pop(MidiInbox& inbox) {
    auto destination = destination_sentinel;
    CHECK(!inbox.pop(destination));
    same_packet(destination, destination_sentinel);
}

void inbox_size_copy_and_timestamp_fifo() {
    MidiInbox inbox;
    CHECK(inbox.pending() == 0);
    inbox_diagnostics(inbox, {});
    no_pop(inbox);
    const std::array<std::uint8_t, 4> four{0x90, 60, 100, 0};
    const std::array<std::uint8_t, 1024> long_message{};
    CHECK(inbox.push({}, 0) == MidiPushResult::InvalidSize);
    CHECK(inbox.push(four, maximum_time) == MidiPushResult::InvalidSize);
    CHECK(inbox.push(long_message, 1) == MidiPushResult::InvalidSize);
    no_pop(inbox);
    inbox_diagnostics(inbox, {.received_packets = 3, .invalid_size_packets = 3});

    std::array<std::uint8_t, 1> first{0xF8};
    std::array<std::uint8_t, 2> second{0xC0, 127};
    std::array<std::uint8_t, 3> third{0x90, 60, 100};
    std::array<std::uint8_t, 3> fourth{0, 0xFF, 16};
    CHECK(inbox.push(first, maximum_time) == MidiPushResult::Accepted);
    first[0] = 0;
    CHECK(inbox.push(second, 0) == MidiPushResult::Accepted);
    second.fill(0);
    CHECK(inbox.push(third, 0) == MidiPushResult::Accepted);
    third.fill(0);
    // The inbox copies complete bytes; it does not do the decoder's parsing.
    CHECK(inbox.push(fourth, 7) == MidiPushResult::Accepted);
    fourth.fill(0);
    CHECK(inbox.pending() == 4);
    constexpr std::array<MidiPacket, 4> expected{{
        {{0xF8, 0, 0}, 1, maximum_time}, {{0xC0, 127, 0}, 2, 0},
        {{0x90, 60, 100}, 3, 0}, {{0, 0xFF, 16}, 3, 7},
    }};
    for (std::size_t index = 0; index < expected.size(); ++index) {
        auto destination = destination_sentinel;
        CHECK(inbox.pop(destination));
        same_packet(destination, expected[index]);
        CHECK(inbox.pending() == expected.size() - index - 1);
    }
    no_pop(inbox);
    inbox_diagnostics(inbox, {
        .received_packets = 7, .accepted_packets = 4,
        .invalid_size_packets = 3, .popped_packets = 4});
    inbox.reset_quiescent();
    inbox_diagnostics(inbox, {
        .received_packets = 7, .accepted_packets = 4,
        .invalid_size_packets = 3, .popped_packets = 4, .resets = 1});
}

[[nodiscard]] MidiPacket numbered_packet(unsigned sequence) {
    return message(0x90, byte(sequence % 128U), byte((sequence / 128U) % 128U),
                   maximum_time - sequence);
}

void inbox_wraps_without_overwrite_or_reordering() {
    MidiInbox inbox;
    unsigned produced = 0;
    unsigned consumed = 0;
    const auto push_count = [&](unsigned count) {
        for (unsigned index = 0; index < count; ++index) {
            const auto packet = numbered_packet(produced);
            CHECK(inbox.push(packet.bytes, packet.arrival_ns) == MidiPushResult::Accepted);
            ++produced;
            CHECK(inbox.pending() == produced - consumed);
        }
    };
    const auto pop_count = [&](unsigned count) {
        for (unsigned index = 0; index < count; ++index) {
            auto destination = destination_sentinel;
            CHECK(inbox.pop(destination));
            same_packet(destination, numbered_packet(consumed));
            ++consumed;
            CHECK(inbox.pending() == produced - consumed);
        }
    };
    for (unsigned round = 0; round < 8; ++round) {
        push_count(240);
        pop_count(137);
        push_count(153);
        CHECK(inbox.pending() == 256);
        pop_count(256);
        no_pop(inbox);
    }
    CHECK(produced == 3144 && consumed == 3144);
    // All storage slots have now held three-byte packets with nonzero tails.
    // Reusing them for shorter packets must explicitly clear those old bytes.
    const std::array<std::uint8_t, 1> short_packet{0xF8};
    const std::array<std::uint8_t, 2> two_bytes{0xC0, 123};
    CHECK(inbox.push(short_packet, 0) == MidiPushResult::Accepted);
    CHECK(inbox.push(two_bytes, 1) == MidiPushResult::Accepted);
    MidiPacket destination;
    CHECK(inbox.pop(destination));
    same_packet(destination, MidiPacket{{0xF8, 0, 0}, 1, 0});
    CHECK(inbox.pop(destination));
    same_packet(destination, MidiPacket{{0xC0, 123, 0}, 2, 1});
    no_pop(inbox);
    inbox_diagnostics(inbox, {
        .received_packets = 3146, .accepted_packets = 3146, .popped_packets = 3146});
}

void exact_capacity_latched_overflow_and_reset() {
    MidiInbox inbox;
    for (unsigned index = 0; index < 256; ++index) {
        const auto packet = numbered_packet(index);
        CHECK(inbox.push(packet.bytes, packet.arrival_ns) == MidiPushResult::Accepted);
        CHECK(inbox.pending() == index + 1);
    }
    inbox_diagnostics(inbox, {.received_packets = 256, .accepted_packets = 256});
    const std::array<std::uint8_t, 3> next{0x80, 60, 0};
    CHECK(inbox.push(next, 0) == MidiPushResult::Overflow);
    CHECK(inbox.pending() == 256);
    inbox_diagnostics(inbox, {
        .received_packets = 257, .accepted_packets = 256, .overflow_events = 1, .faults = 1});
    no_pop(inbox);
    const std::array<std::uint8_t, 4> oversized{0x90, 60, 1, 0};
    CHECK(inbox.push(next, 1) == MidiPushResult::Faulted);
    CHECK(inbox.push({}, 2) == MidiPushResult::Faulted);
    CHECK(inbox.push(oversized, 3) == MidiPushResult::Faulted);
    // Fault admission precedes even the empty/oversized message check.
    inbox_diagnostics(inbox, {
        .received_packets = 260, .accepted_packets = 256,
        .faulted_packets = 3, .overflow_events = 1, .faults = 1});
    inbox.signal_fault(MidiInboxFault::Backend);
    inbox.signal_fault(MidiInboxFault::Disconnected);
    inbox.signal_fault(MidiInboxFault::Backend);
    inbox_diagnostics(inbox, {
        .received_packets = 260, .accepted_packets = 256,
        .faulted_packets = 3, .overflow_events = 1, .faults = 7});
    no_pop(inbox);
    inbox.reset_quiescent();
    CHECK(inbox.pending() == 0);
    no_pop(inbox);
    inbox_diagnostics(inbox, {
        .received_packets = 260, .accepted_packets = 256,
        .faulted_packets = 3, .overflow_events = 1,
        .discarded_packets = 256, .resets = 1});

    const std::array<std::uint8_t, 3> new_on{0x91, 96, 127};
    CHECK(inbox.push(next, 4) == MidiPushResult::Accepted);
    CHECK(inbox.push(new_on, 5) == MidiPushResult::Accepted);
    MidiPacket destination;
    CHECK(inbox.pop(destination));
    same_packet(destination, message(0x80, 60, 0, 4));
    CHECK(inbox.pending() == 1);
    inbox.reset_quiescent();
    inbox.reset_quiescent();
    no_pop(inbox);
    inbox_diagnostics(inbox, {
        .received_packets = 262, .accepted_packets = 258,
        .faulted_packets = 3, .overflow_events = 1, .popped_packets = 1,
        .discarded_packets = 257, .resets = 3});
}

void independent_faults_and_full_size_precedence() {
    struct FaultCase { MidiInboxFault fault; std::uint32_t bits; };
    constexpr std::array<FaultCase, 3> cases{{
        {MidiInboxFault::Overflow, 1}, {MidiInboxFault::Backend, 2},
        {MidiInboxFault::Disconnected, 4},
    }};
    const std::array<std::uint8_t, 3> on{0x90, 60, 100};
    const std::array<std::uint8_t, 3> off{0x80, 60, 0};
    for (const auto& fault_case : cases) {
        MidiInbox inbox;
        CHECK(inbox.push(on, 8) == MidiPushResult::Accepted);
        CHECK(inbox.push(off, 9) == MidiPushResult::Accepted);
        MidiPacket destination;
        CHECK(inbox.pop(destination));
        same_packet(destination, message(0x90, 60, 100, 8));
        inbox.signal_fault(fault_case.fault);
        inbox.signal_fault(fault_case.fault);
        CHECK(inbox.pending() == 1);
        no_pop(inbox);
        CHECK(inbox.push(on, 10) == MidiPushResult::Faulted);
        // signal_fault only ORs bits; even a named Overflow signal does not
        // fabricate a full-ring push or increment overflow_events.
        inbox_diagnostics(inbox, {
            .received_packets = 3, .accepted_packets = 2,
            .faulted_packets = 1, .popped_packets = 1, .faults = fault_case.bits});
        inbox.reset_quiescent();
        no_pop(inbox);
        inbox_diagnostics(inbox, {
            .received_packets = 3, .accepted_packets = 2,
            .faulted_packets = 1, .popped_packets = 1, .discarded_packets = 1, .resets = 1});
        // Empty storage does not suppress a backend/disconnect fault either.
        inbox.signal_fault(fault_case.fault);
        CHECK(inbox.pending() == 0);
        no_pop(inbox);
        CHECK(inbox.push(on, 11) == MidiPushResult::Faulted);
        inbox_diagnostics(inbox, {
            .received_packets = 4, .accepted_packets = 2,
            .faulted_packets = 2, .popped_packets = 1, .discarded_packets = 1,
            .resets = 1, .faults = fault_case.bits});
        inbox.reset_quiescent();
        inbox_diagnostics(inbox, {
            .received_packets = 4, .accepted_packets = 2,
            .faulted_packets = 2, .popped_packets = 1, .discarded_packets = 1, .resets = 2});
    }
    MidiInbox full;
    for (unsigned index = 0; index < 256; ++index) CHECK(full.push(on, index) == MidiPushResult::Accepted);
    const std::array<std::uint8_t, 4> four{0xF0, 0, 0, 0xF7};
    CHECK(full.push({}, 0) == MidiPushResult::InvalidSize);
    CHECK(full.push(four, 0) == MidiPushResult::InvalidSize);
    CHECK(full.pending() == 256);
    inbox_diagnostics(full, {
        .received_packets = 258, .accepted_packets = 256, .invalid_size_packets = 2});
    MidiPacket destination;
    CHECK(full.pop(destination));
    same_packet(destination, message(0x90, 60, 100, 0));
    // The invalid-size attempts did not latch a full-ring fault.
    CHECK(full.push(off, 257) == MidiPushResult::Accepted);
    full.reset_quiescent();
    inbox_diagnostics(full, {
        .received_packets = 259, .accepted_packets = 257, .invalid_size_packets = 2,
        .popped_packets = 1, .discarded_packets = 256, .resets = 1});
}

} // namespace

int main() {
    routing_and_epoch_transactions();
    all_wire_choices_and_note_domains();
    repeated_anonymous_notes_and_scoped_releases();
    every_supported_controller_value();
    complete_message_admission_order();
    receipt_order_and_timestamp_history();
    inbox_size_copy_and_timestamp_fifo();
    inbox_wraps_without_overwrite_or_reordering();
    exact_capacity_latched_overflow_and_reset();
    independent_faults_and_full_size_precedence();
    std::cout << "Standalone MIDI inbox/decoder acceptance: 10 behavioral scenarios passed\n";
}
