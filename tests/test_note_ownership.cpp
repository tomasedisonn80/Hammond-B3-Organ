#include "TestSupport.h"
#include "hammond/NoteOwnership.h"

#include <algorithm>
#include <array>
#include <cstdint>
#include <initializer_list>
#include <limits>
#include <span>
#include <vector>

namespace {

using hammond::Event;
using hammond::EventType;
using hammond::HostNoteEvent;
using hammond::HostNoteKind;
using hammond::Manual;
using hammond::NoteOwnerSnapshot;
using hammond::NoteOwnership;
using hammond::Status;

constexpr std::size_t kOutputStorage = 2 * hammond::kMaxEventsPerBlock + 17;
constexpr Event kSentinel{0xc0ffeeU, static_cast<EventType>(255),
                          Manual::Lower, 255, -123.25};
std::size_t accepted_calls = 0;
std::size_t rejected_calls = 0;
std::size_t expected_physical_events = 0;
std::size_t checked_owner_rows = 0;
std::size_t partition_cases = 0;

HostNoteEvent on(std::uint32_t offset, std::uint8_t bus, std::uint8_t channel,
                 std::uint8_t pitch, std::int32_t identity = -1,
                 std::uint8_t velocity = 100) {
    return {offset, HostNoteKind::On, bus, channel, pitch, velocity, identity};
}

HostNoteEvent off(std::uint32_t offset, std::uint8_t bus, std::uint8_t channel,
                  std::uint8_t pitch, std::int32_t identity = -1) {
    return {offset, HostNoteKind::Off, bus, channel, pitch, 0, identity};
}

HostNoteEvent channel_release(std::uint32_t offset, std::uint8_t bus,
                              std::uint8_t channel) {
    return {offset, HostNoteKind::AllNotesOff, bus, channel, 0, 0, -1};
}

Event down(std::uint32_t offset, Manual manual, std::uint8_t pitch,
           std::uint8_t velocity = 100) {
    return {offset, EventType::NoteOn, manual, pitch, static_cast<double>(velocity)};
}

Event up(std::uint32_t offset, Manual manual, std::uint8_t pitch) {
    return {offset, EventType::NoteOff, manual, pitch, 0.0};
}

bool same_event(const Event& left, const Event& right) {
    return left.offset == right.offset && left.type == right.type &&
           left.manual == right.manual && left.index == right.index &&
           left.value == right.value;
}

void events_equal(std::span<const Event> actual, std::span<const Event> expected) {
    CHECK(actual.size() == expected.size());
    for (std::size_t index = 0; index < expected.size(); ++index) {
        if (!same_event(actual[index], expected[index])) {
            std::cerr << "event " << index << ": actual offset/type/manual/index/value="
                      << actual[index].offset << '/'
                      << static_cast<unsigned>(actual[index].type) << '/'
                      << static_cast<unsigned>(actual[index].manual) << '/'
                      << static_cast<unsigned>(actual[index].index) << '/'
                      << actual[index].value << '\n';
        }
        CHECK(same_event(actual[index], expected[index]));
    }
}

void accepted(NoteOwnership& ownership, std::uint32_t frames,
              std::span<const HostNoteEvent> input, std::span<const Event> expected,
              std::size_t capacity = hammond::kMaxEventsPerBlock) {
    CHECK(capacity <= kOutputStorage);
    std::array<Event, kOutputStorage> output;
    output.fill(kSentinel);
    const auto result = ownership.translate(frames, input,
                                            std::span<Event>(output).first(capacity));
    CHECK(result.status == Status::Ok);
    CHECK(result.ok());
    CHECK(static_cast<bool>(result));
    CHECK(result.input_consumed == input.size());
    CHECK(result.output_events == expected.size());
    events_equal(std::span<const Event>(output).first(result.output_events), expected);
    for (std::size_t index = result.output_events; index < output.size(); ++index) {
        CHECK(same_event(output[index], kSentinel));
    }
    for (std::size_t index = 0; index < result.output_events; ++index) {
        CHECK(output[index].type == EventType::NoteOn ||
              output[index].type == EventType::NoteOff);
    }
    ++accepted_calls;
    expected_physical_events += expected.size();
}

void accepted(NoteOwnership& ownership, std::uint32_t frames,
              std::initializer_list<HostNoteEvent> input,
              std::initializer_list<Event> expected,
              std::size_t capacity = hammond::kMaxEventsPerBlock) {
    accepted(ownership, frames, std::span<const HostNoteEvent>(input.begin(), input.size()),
             std::span<const Event>(expected.begin(), expected.size()), capacity);
}

void owners_equal(const NoteOwnership& ownership,
                  std::span<const NoteOwnerSnapshot> expected) {
    CHECK(ownership.owner_count() == expected.size());
    for (std::size_t index = 0; index < expected.size(); ++index) {
        NoteOwnerSnapshot actual{255, 255, 255, -99, static_cast<Manual>(255)};
        CHECK(ownership.owner_snapshot(index, actual));
        CHECK(actual == expected[index]);
        ++checked_owner_rows;
    }
    for (const auto invalid : {expected.size(), std::numeric_limits<std::size_t>::max()}) {
        const NoteOwnerSnapshot sentinel{255, 255, 255, -99, static_cast<Manual>(255)};
        auto actual = sentinel;
        CHECK(!ownership.owner_snapshot(invalid, actual));
        CHECK(actual == sentinel);
    }
    for (const auto manual : {Manual::Upper, Manual::Lower}) {
        for (std::uint32_t pitch = 36; pitch <= 96; ++pitch) {
            const auto count = static_cast<std::size_t>(std::count_if(
                expected.begin(), expected.end(), [manual, pitch](const auto& owner) {
                    return owner.manual == manual && owner.midi_note == pitch;
                }));
            std::size_t actual = 9999;
            CHECK(ownership.owner_count(manual, pitch, actual));
            CHECK(actual == count);
        }
    }
}

void owners_equal(const NoteOwnership& ownership,
                  std::initializer_list<NoteOwnerSnapshot> expected) {
    owners_equal(ownership,
                 std::span<const NoteOwnerSnapshot>(expected.begin(), expected.size()));
}

// This is a future-observation check after rejection, not a second ownership
// algorithm: retire every declared channel, then perform a fresh identified pair.
void unchanged_future(NoteOwnership actual, NoteOwnership expected) {
    std::array<HostNoteEvent, 34> continuation{};
    std::size_t cursor = 0;
    for (std::uint8_t bus = 0; bus < 2; ++bus) {
        for (std::uint8_t channel = 0; channel < 16; ++channel) {
            continuation[cursor++] = channel_release(0, bus, channel);
        }
    }
    continuation[cursor++] = on(0, 0, 0, 36, std::numeric_limits<std::int32_t>::max(), 127);
    continuation[cursor++] = off(0, 0, 0, 36, std::numeric_limits<std::int32_t>::max());
    CHECK(cursor == continuation.size());
    std::array<Event, hammond::kMaxEventsPerBlock> actual_output{};
    std::array<Event, hammond::kMaxEventsPerBlock> expected_output{};
    const auto actual_result = actual.translate(0, continuation, actual_output);
    const auto expected_result = expected.translate(0, continuation, expected_output);
    CHECK(actual_result.ok());
    CHECK(expected_result.ok());
    CHECK(actual_result.input_consumed == continuation.size());
    CHECK(actual_result.output_events == expected_result.output_events);
    events_equal(std::span<const Event>(actual_output).first(actual_result.output_events),
                 std::span<const Event>(expected_output).first(expected_result.output_events));
    CHECK(actual == expected);
    CHECK(actual.owner_count() == 0);
}

void rejected(NoteOwnership& ownership, std::uint32_t frames,
              std::span<const HostNoteEvent> input, Status expected_status,
              std::size_t capacity = hammond::kMaxEventsPerBlock) {
    CHECK(capacity <= kOutputStorage);
    const auto before = ownership;
    std::array<Event, kOutputStorage> output;
    output.fill(kSentinel);
    const auto result = ownership.translate(frames, input,
                                            std::span<Event>(output).first(capacity));
    CHECK(result.status == expected_status);
    CHECK(!result.ok());
    CHECK(!static_cast<bool>(result));
    CHECK(result.input_consumed == 0);
    CHECK(result.output_events == 0);
    CHECK(ownership == before);
    for (const auto& event : output) CHECK(same_event(event, kSentinel));
    unchanged_future(ownership, before);
    ++rejected_calls;
}

void rejected(NoteOwnership& ownership, std::uint32_t frames,
              std::initializer_list<HostNoteEvent> input, Status expected_status,
              std::size_t capacity = hammond::kMaxEventsPerBlock) {
    rejected(ownership, frames,
             std::span<const HostNoteEvent>(input.begin(), input.size()),
             expected_status, capacity);
}

void test_defaults_and_checked_routes() {
    CHECK(hammond::kHostInputBusCount == 2);
    CHECK(hammond::kHostInputChannelCount == 16);
    CHECK(hammond::kMaxNoteOwners == 256);
    CHECK(hammond::kNoteOwnershipModelId == "bounded-fifo-note-ownership-v1");
    NoteOwnership ownership;
    owners_equal(ownership, {});
    Manual route = static_cast<Manual>(255);
    CHECK(ownership.bus_route(0, route)); CHECK(route == Manual::Upper);
    CHECK(ownership.bus_route(1, route)); CHECK(route == Manual::Lower);
    accepted(ownership, 0, {}, {}, 0);
    accepted(ownership, hammond::kHardMaxBlockFrames, {}, {}, 0);
    CHECK(ownership.set_routes({Manual::Lower, Manual::Upper}));
    CHECK(ownership.bus_route(0, route)); CHECK(route == Manual::Lower);
    CHECK(ownership.bus_route(1, route)); CHECK(route == Manual::Upper);

    const auto before = ownership;
    for (const auto bus : {2U, 255U, std::numeric_limits<std::uint32_t>::max()}) {
        route = Manual::Upper;
        CHECK(!ownership.bus_route(bus, route)); CHECK(route == Manual::Upper);
        CHECK(!ownership.set_bus_route(bus, Manual::Lower));
        CHECK(ownership == before);
    }
    for (unsigned value = 2; value <= 255; ++value) {
        const auto invalid = static_cast<Manual>(value);
        CHECK(!ownership.set_bus_route(0, invalid));
        CHECK(!ownership.set_bus_route(1, invalid));
        CHECK(!ownership.set_routes({invalid, Manual::Lower}));
        CHECK(!ownership.set_routes({Manual::Lower, invalid}));
        std::size_t count = 777;
        CHECK(!ownership.owner_count(invalid, 60, count)); CHECK(count == 777);
        CHECK(ownership == before);
    }
    for (const auto pitch : {0U, 35U, 97U, 255U, std::numeric_limits<std::uint32_t>::max()}) {
        for (const auto manual : {Manual::Upper, Manual::Lower}) {
            std::size_t count = 777;
            CHECK(!ownership.owner_count(manual, pitch, count)); CHECK(count == 777);
        }
    }
    CHECK(ownership.set_bus_route(0, Manual::Upper));
    CHECK(ownership.set_bus_route(1, Manual::Lower));
    owners_equal(ownership, {});
}

void test_identified_owners_and_reuse() {
    NoteOwnership ownership;
    accepted(ownership, 0, {on(0, 0, 2, 60, 17, 37)}, {down(0, Manual::Upper, 60, 37)});
    accepted(ownership, 0, {on(0, 0, 2, 60, 17, 127)}, {}, 0);
    accepted(ownership, 0, {on(0, 0, 3, 60, 17, 9)}, {}, 0);
    accepted(ownership, 0, {on(0, 1, 2, 60, 17, 11)}, {down(0, Manual::Lower, 60, 11)});
    accepted(ownership, 0, {on(0, 0, 2, 64, 18, 13)}, {down(0, Manual::Upper, 64, 13)});
    owners_equal(ownership, {{0, 2, 60, 17, Manual::Upper}, {0, 3, 60, 17, Manual::Upper},
                             {1, 2, 60, 17, Manual::Lower}, {0, 2, 64, 18, Manual::Upper}});
    accepted(ownership, 0, {off(0, 0, 2, 69, 999), off(0, 0, 2, 60)}, {}, 0);
    rejected(ownership, 0, {on(0, 0, 2, 61, 17)}, Status::InvalidEvent);
    rejected(ownership, 0, {off(0, 0, 2, 61, 17)}, Status::InvalidEvent);
    rejected(ownership, 0, {on(0, 0, 2, 61, 17, 0)}, Status::InvalidEvent);
    // The valid removal before the dynamic pitch conflict must also roll back.
    rejected(ownership, 0, {off(0, 0, 2, 64, 18), on(0, 0, 2, 61, 17)},
             Status::InvalidEvent);
    accepted(ownership, 0, {on(0, 0, 2, 60, 17, 0)}, {}, 0);
    accepted(ownership, 0, {off(0, 0, 3, 60, 17)}, {up(0, Manual::Upper, 60)});
    accepted(ownership, 0, {off(0, 1, 2, 60, 17)}, {up(0, Manual::Lower, 60)});
    // Proper release permits immediate identity reuse at a different pitch.
    accepted(ownership, 7, {off(6, 0, 2, 64, 18), on(6, 0, 2, 69, 18, 1)},
             {up(6, Manual::Upper, 64), down(6, Manual::Upper, 69, 1)});
    owners_equal(ownership, {{0, 2, 69, 18, Manual::Upper}});
    accepted(ownership, 0, {channel_release(0, 0, 2)}, {up(0, Manual::Upper, 69)});
    owners_equal(ownership, {});
}

void test_fifo_and_original_manual() {
    NoteOwnership ownership;
    accepted(ownership, 0,
             {on(0, 0, 0, 60), on(0, 0, 0, 60), on(0, 0, 0, 60, 42)},
             {down(0, Manual::Upper, 60)});
    CHECK(ownership.set_bus_route(0, Manual::Lower));
    accepted(ownership, 0, {on(0, 0, 0, 60, 42, 99)}, {}, 0);
    accepted(ownership, 0, {on(0, 0, 0, 60, -1, 17)}, {down(0, Manual::Lower, 60, 17)});
    owners_equal(ownership, {{0, 0, 60, -1, Manual::Upper}, {0, 0, 60, -1, Manual::Upper},
                             {0, 0, 60, 42, Manual::Upper}, {0, 0, 60, -1, Manual::Lower}});
    accepted(ownership, 0, {off(0, 0, 0, 60)}, {}, 0);
    owners_equal(ownership, {{0, 0, 60, -1, Manual::Upper}, {0, 0, 60, 42, Manual::Upper},
                             {0, 0, 60, -1, Manual::Lower}});
    accepted(ownership, 0, {off(0, 0, 0, 60)}, {}, 0);
    accepted(ownership, 0, {on(0, 0, 0, 60, -1, 0)}, {up(0, Manual::Lower, 60)});
    // An anonymous release cannot retire the last, identified upper owner.
    accepted(ownership, 0, {off(0, 0, 0, 60)}, {}, 0);
    owners_equal(ownership, {{0, 0, 60, 42, Manual::Upper}});
    accepted(ownership, 0, {off(0, 0, 0, 60, 42)}, {up(0, Manual::Upper, 60)});
    owners_equal(ownership, {});

    // With no identified owner in the way, FIFO explicitly releases the old
    // upper destination before a newer lower owner of the same bus/channel/pitch.
    CHECK(ownership.set_bus_route(0, Manual::Upper));
    accepted(ownership, 0, {on(0, 0, 1, 72)}, {down(0, Manual::Upper, 72)});
    CHECK(ownership.set_bus_route(0, Manual::Lower));
    accepted(ownership, 0, {on(0, 0, 1, 72)}, {down(0, Manual::Lower, 72)});
    accepted(ownership, 0, {off(0, 0, 1, 72)}, {up(0, Manual::Upper, 72)});
    owners_equal(ownership, {{0, 1, 72, -1, Manual::Lower}});
    accepted(ownership, 0, {off(0, 0, 1, 72)}, {up(0, Manual::Lower, 72)});
}

void test_channel_release_scope_and_order() {
    NoteOwnership ownership;
    CHECK(ownership.set_routes({Manual::Upper, Manual::Upper}));
    accepted(ownership, 0,
             {on(0, 0, 3, 60, 1), on(0, 0, 3, 64, 2), on(0, 0, 3, 60, 3),
              on(0, 0, 4, 64, 4), on(0, 1, 3, 67, 5), on(0, 0, 3, 69),
              on(0, 0, 3, 67, 6), on(0, 0, 3, 62, 7)},
             {down(0, Manual::Upper, 60), down(0, Manual::Upper, 64),
              down(0, Manual::Upper, 67), down(0, Manual::Upper, 69),
              down(0, Manual::Upper, 62)});
    CHECK(ownership.set_routes({Manual::Lower, Manual::Lower}));
    // Last-owner retirements follow surviving insertion order: 60, 69, 62.
    // Pitches 64 and 67 remain held by another channel/bus respectively.
    accepted(ownership, 8, {channel_release(7, 0, 3)},
             {up(7, Manual::Upper, 60), up(7, Manual::Upper, 69), up(7, Manual::Upper, 62)});
    owners_equal(ownership, {{0, 4, 64, 4, Manual::Upper}, {1, 3, 67, 5, Manual::Upper}});
    accepted(ownership, 0, {channel_release(0, 0, 3)}, {}, 0);
    accepted(ownership, 0, {channel_release(0, 1, 4)}, {}, 0);
    accepted(ownership, 0, {channel_release(0, 0, 4), on(0, 0, 4, 64, 4, 127)},
             {up(0, Manual::Upper, 64), down(0, Manual::Lower, 64, 127)});
    owners_equal(ownership, {{1, 3, 67, 5, Manual::Upper}, {0, 4, 64, 4, Manual::Lower}});
    accepted(ownership, 0, {channel_release(0, 1, 3), channel_release(0, 0, 4)},
             {up(0, Manual::Upper, 67), up(0, Manual::Lower, 64)});
    owners_equal(ownership, {});
}

void test_anonymous_origin_scoping() {
    NoteOwnership ownership;
    CHECK(ownership.set_routes({Manual::Upper, Manual::Upper}));
    accepted(ownership, 0,
             {on(0, 0, 0, 60), on(0, 0, 1, 60), on(0, 1, 0, 60), on(0, 0, 0, 64)},
             {down(0, Manual::Upper, 60), down(0, Manual::Upper, 64)});
    accepted(ownership, 0, {off(0, 1, 1, 60), off(0, 0, 0, 61)}, {}, 0);
    owners_equal(ownership, {{0, 0, 60, -1, Manual::Upper}, {0, 1, 60, -1, Manual::Upper},
                             {1, 0, 60, -1, Manual::Upper}, {0, 0, 64, -1, Manual::Upper}});
    accepted(ownership, 0, {off(0, 0, 1, 60)}, {}, 0);
    owners_equal(ownership, {{0, 0, 60, -1, Manual::Upper}, {1, 0, 60, -1, Manual::Upper},
                             {0, 0, 64, -1, Manual::Upper}});
    accepted(ownership, 0, {off(0, 1, 0, 60)}, {}, 0);
    accepted(ownership, 0, {on(0, 0, 0, 64, -1, 0)}, {up(0, Manual::Upper, 64)});
    owners_equal(ownership, {{0, 0, 60, -1, Manual::Upper}});
    accepted(ownership, 0, {off(0, 0, 0, 60)}, {up(0, Manual::Upper, 60)});
    owners_equal(ownership, {});
}

void test_every_valid_destination_and_velocity() {
    NoteOwnership ownership;
    for (std::uint8_t bus = 0; bus < 2; ++bus) {
        const auto manual = bus == 0 ? Manual::Upper : Manual::Lower;
        for (std::uint8_t channel = 0; channel < 16; ++channel) {
            const std::int32_t identity = channel % 2 == 0
                ? 0 : std::numeric_limits<std::int32_t>::max();
            for (std::uint8_t pitch = 36; pitch <= 96; ++pitch) {
                accepted(ownership, 2, {on(0, bus, channel, pitch, identity, 127),
                                        off(1, bus, channel, pitch, identity)},
                         {down(0, manual, pitch, 127), up(1, manual, pitch)}, 2);
                CHECK(ownership.owner_count() == 0);
            }
        }
    }
    for (unsigned value = 1; value <= 127; ++value) {
        const auto velocity = static_cast<std::uint8_t>(value);
        accepted(ownership, 0, {on(0, 0, 15, 96, -1, velocity), on(0, 0, 15, 96, -1, 0)},
                 {down(0, Manual::Upper, 96, velocity), up(0, Manual::Upper, 96)}, 2);
    }
    owners_equal(ownership, {});
}

void test_invalid_domains_and_timing() {
    NoteOwnership ownership;
    accepted(ownership, 0, {on(0, 0, 0, 60, 8), on(0, 1, 15, 96)},
             {down(0, Manual::Upper, 60), down(0, Manual::Lower, 96)});
    CHECK(ownership.set_routes({Manual::Lower, Manual::Upper}));
    const auto bad = [&ownership](const HostNoteEvent& invalid) {
        // A valid prefix is also required to remain unapplied on any rejection.
        rejected(ownership, 0, {on(0, 0, 7, 72, 77), invalid}, Status::InvalidEvent);
    };
    for (unsigned value = 3; value <= 255; ++value) {
        auto event = on(0, 0, 0, 60); event.kind = static_cast<HostNoteKind>(value); bad(event);
    }
    for (unsigned value = 2; value <= 255; ++value) {
        auto event = on(0, 0, 0, 60); event.bus = static_cast<std::uint8_t>(value); bad(event);
    }
    for (unsigned value = 16; value <= 255; ++value) {
        auto event = on(0, 0, 0, 60); event.channel = static_cast<std::uint8_t>(value); bad(event);
    }
    for (unsigned value = 0; value <= 255; ++value) {
        if (value >= 36 && value <= 96) continue;
        const auto pitch = static_cast<std::uint8_t>(value);
        bad(on(0, 0, 0, pitch)); bad(off(0, 0, 0, pitch)); bad(on(0, 0, 0, pitch, -1, 0));
    }
    for (unsigned value = 128; value <= 255; ++value) {
        bad(on(0, 0, 0, 60, -1, static_cast<std::uint8_t>(value)));
    }
    for (unsigned value = 1; value <= 255; ++value) {
        auto event = off(0, 0, 0, 60); event.velocity = static_cast<std::uint8_t>(value); bad(event);
        event = channel_release(0, 0, 0); event.velocity = static_cast<std::uint8_t>(value); bad(event);
        event = channel_release(0, 0, 0); event.midi_note = static_cast<std::uint8_t>(value); bad(event);
    }
    for (const auto identity : {-2, -3, std::numeric_limits<std::int32_t>::min()}) {
        bad(on(0, 0, 0, 60, identity)); bad(off(0, 0, 0, 60, identity));
        bad(on(0, 0, 0, 60, identity, 0));
    }
    for (const auto identity : {-2, 0, std::numeric_limits<std::int32_t>::max()}) {
        auto event = channel_release(0, 0, 0); event.note_id = identity; bad(event);
    }
    for (const auto kind : {HostNoteKind::Off, HostNoteKind::AllNotesOff}) {
        auto event = kind == HostNoteKind::Off ? off(0, 0, 0, 60) : channel_release(0, 0, 0);
        event.bus = 2; bad(event); event.bus = 0; event.channel = 16; bad(event);
    }

    rejected(ownership, 0, {on(1, 0, 0, 60)}, Status::InvalidEvent);
    rejected(ownership, 4, {on(3, 0, 0, 61), on(2, 0, 0, 62)}, Status::InvalidEvent);
    for (const auto frames : {1U, 64U, hammond::kHardMaxBlockFrames}) {
        rejected(ownership, frames, {on(frames, 0, 0, 60)}, Status::InvalidEvent);
        rejected(ownership, frames,
                 {on(std::numeric_limits<std::uint32_t>::max(), 0, 0, 60)}, Status::InvalidEvent);
    }
    rejected(ownership, hammond::kHardMaxBlockFrames + 1, {}, Status::BlockTooLarge);
    rejected(ownership, std::numeric_limits<std::uint32_t>::max(), {}, Status::BlockTooLarge);
    accepted(ownership, hammond::kHardMaxBlockFrames,
             {on(hammond::kHardMaxBlockFrames - 1, 0, 9, 70, 22),
              off(hammond::kHardMaxBlockFrames - 1, 0, 9, 70, 22)},
             {down(hammond::kHardMaxBlockFrames - 1, Manual::Lower, 70),
              up(hammond::kHardMaxBlockFrames - 1, Manual::Lower, 70)});
}

void test_owner_capacity_and_transaction() {
    NoteOwnership ownership;
    std::vector<HostNoteEvent> input{on(0, 0, 0, 60, 5, 21)};
    std::vector<NoteOwnerSnapshot> expected{{0, 0, 60, 5, Manual::Upper}};
    for (std::size_t index = 1; index < hammond::kMaxNoteOwners; ++index) {
        input.push_back(on(0, 0, 0, 60));
        expected.push_back({0, 0, 60, -1, Manual::Upper});
    }
    const std::array<Event, 1> physical{down(0, Manual::Upper, 60, 21)};
    accepted(ownership, 0, input, physical, 1);
    owners_equal(ownership, expected);
    std::size_t count = 0;
    CHECK(ownership.owner_count(Manual::Upper, 60, count)); CHECK(count == 256);
    accepted(ownership, 0, {on(0, 0, 0, 60, 5, 99), off(0, 1, 9, 80, 700)}, {}, 0);
    rejected(ownership, 0, {on(0, 0, 0, 60)}, Status::TooManyEvents);
    rejected(ownership, 0, {on(0, 0, 1, 70, 99), off(0, 0, 1, 70, 99)},
             Status::TooManyEvents);
    // A valid earlier release followed by two adds still exceeds simultaneous
    // capacity; the released owner must be restored by whole-call rejection.
    rejected(ownership, 0, {off(0, 0, 0, 60), on(0, 0, 1, 70, 99), on(0, 0, 1, 72, 100)},
             Status::TooManyEvents);
    accepted(ownership, 0, {off(0, 0, 0, 60), on(0, 0, 1, 70, 99)},
             {down(0, Manual::Upper, 70)});
    expected.erase(expected.begin() + 1);
    expected.push_back({0, 1, 70, 99, Manual::Upper});
    owners_equal(ownership, expected);
    rejected(ownership, 0, {channel_release(0, 0, 0), channel_release(0, 0, 1)},
             Status::TooManyEvents, 1);
    accepted(ownership, 0, {channel_release(0, 0, 0), channel_release(0, 0, 1)},
             {up(0, Manual::Upper, 60), up(0, Manual::Upper, 70)}, 2);
    owners_equal(ownership, {});
}

void test_input_output_capacities() {
    NoteOwnership ownership;
    rejected(ownership, 0, {on(0, 0, 0, 60)}, Status::TooManyEvents, 0);
    rejected(ownership, 0, {on(0, 0, 0, 60), off(0, 0, 0, 60)}, Status::TooManyEvents, 1);
    std::vector<HostNoteEvent> no_ops(hammond::kMaxEventsPerBlock, off(0, 0, 0, 60, 999));
    const std::span<const Event> no_physical;
    accepted(ownership, 0, no_ops, no_physical, 0);
    no_ops.push_back(off(0, 0, 0, 60, 999));
    rejected(ownership, 0, no_ops, Status::TooManyEvents);

    std::vector<HostNoteEvent> pairs;
    std::vector<Event> expected;
    for (std::size_t index = 0; index < hammond::kMaxEventsPerBlock / 2; ++index) {
        pairs.push_back(on(0, 0, 0, 60)); pairs.push_back(off(0, 0, 0, 60));
        expected.push_back(down(0, Manual::Upper, 60)); expected.push_back(up(0, Manual::Upper, 60));
    }
    accepted(ownership, 0, pairs, expected, hammond::kMaxEventsPerBlock);
    owners_equal(ownership, {});
    rejected(ownership, 0, pairs, Status::TooManyEvents, hammond::kMaxEventsPerBlock - 1);

    // Each 62-command round has 61 first-owner ons and one channel release that
    // emits 61 offs. Nine rounds would emit 1,098 outputs from only 558 inputs.
    // A span larger than 1,098 proves rejection uses the fixed 1,024 output bound.
    std::vector<HostNoteEvent> expanded;
    for (unsigned round = 0; round < 9; ++round) {
        for (std::uint8_t pitch = 36; pitch <= 96; ++pitch) {
            expanded.push_back(on(0, 0, 0, pitch));
        }
        expanded.push_back(channel_release(0, 0, 0));
    }
    CHECK(expanded.size() == 558);
    CHECK(kOutputStorage > 1098);
    rejected(ownership, 0, expanded, Status::TooManyEvents, kOutputStorage);
    owners_equal(ownership, {});
}

std::vector<Event> partitioned(const std::vector<HostNoteEvent>& absolute,
                               std::uint32_t block_size, bool flush_boundaries,
                               NoteOwnership& ownership) {
    std::vector<Event> result;
    std::size_t next = 0;
    for (std::uint32_t start = 0; start < 32;) {
        const auto frames = std::min(block_size, 32U - start);
        const auto translate = [&](std::uint32_t count, const std::vector<HostNoteEvent>& input) {
            std::array<Event, 32> output;
            output.fill(kSentinel);
            const auto translated = ownership.translate(count, input, output);
            CHECK(translated.ok()); CHECK(translated.input_consumed == input.size());
            for (std::size_t index = 0; index < translated.output_events; ++index) {
                output[index].offset += start;
                result.push_back(output[index]);
            }
            for (std::size_t index = translated.output_events; index < output.size(); ++index) {
                CHECK(same_event(output[index], kSentinel));
            }
        };
        if (flush_boundaries) {
            std::vector<HostNoteEvent> flush;
            while (next < absolute.size() && absolute[next].offset == start) {
                auto event = absolute[next++]; event.offset = 0; flush.push_back(event);
            }
            translate(0, flush);
        }
        std::vector<HostNoteEvent> local;
        while (next < absolute.size() && absolute[next].offset < start + frames) {
            auto event = absolute[next++]; event.offset -= start; local.push_back(event);
        }
        translate(frames, local);
        start += frames;
    }
    CHECK(next == absolute.size());
    return result;
}

void test_partition_and_zero_frame_equivalence() {
    const std::vector<HostNoteEvent> timeline{
        on(0, 0, 0, 60, 1, 13), on(1, 0, 1, 60, 2, 29),
        on(4, 1, 0, 60, 3, 17), off(4, 0, 0, 60, 1),
        on(7, 0, 1, 60, 2, 127), on(7, 0, 0, 64, -1, 19),
        on(8, 0, 0, 64, -1, 23), off(9, 0, 0, 61, 999),
        off(15, 0, 0, 64), channel_release(16, 0, 1),
        on(20, 0, 0, 67, 4, 31), on(21, 0, 0, 64, -1, 0),
        off(22, 1, 0, 60, 3), off(25, 0, 0, 67, 4),
        on(25, 0, 0, 69, 4, 37), channel_release(31, 0, 0)};
    const std::vector<Event> expected{
        down(0, Manual::Upper, 60, 13), down(4, Manual::Lower, 60, 17),
        down(7, Manual::Upper, 64, 19), up(16, Manual::Upper, 60),
        down(20, Manual::Upper, 67, 31), up(21, Manual::Upper, 64),
        up(22, Manual::Lower, 60), up(25, Manual::Upper, 67),
        down(25, Manual::Upper, 69, 37), up(31, Manual::Upper, 69)};
    NoteOwnership baseline;
    const auto all_at_once = partitioned(timeline, 32, false, baseline);
    events_equal(all_at_once, expected);
    owners_equal(baseline, {});
    for (const auto size : {1U, 2U, 3U, 5U, 7U, 16U, 31U, 32U}) {
        for (const bool flush : {false, true}) {
            NoteOwnership ownership;
            const auto output = partitioned(timeline, size, flush, ownership);
            events_equal(output, expected);
            CHECK(ownership == baseline);
            ++partition_cases;
        }
    }
}

void test_owned_copies() {
    NoteOwnership original;
    accepted(original, 0, {on(0, 0, 0, 60, 10)}, {down(0, Manual::Upper, 60)});
    // Invalid route edits must preserve live owners as well as both route slots.
    const auto before = original;
    for (const auto invalid : {static_cast<Manual>(2), static_cast<Manual>(255)}) {
        CHECK(!original.set_bus_route(0, invalid));
        CHECK(!original.set_routes({Manual::Lower, invalid}));
        CHECK(!original.set_routes({invalid, Manual::Upper}));
        CHECK(original == before);
        unchanged_future(original, before);
    }
    CHECK(!original.set_bus_route(2, Manual::Lower));
    CHECK(original == before);
    auto copy = original;
    CHECK(copy == original);
    CHECK(copy.set_routes({Manual::Lower, Manual::Upper}));
    accepted(copy, 0, {off(0, 0, 0, 60, 10), on(0, 0, 0, 60, 11)},
             {up(0, Manual::Upper, 60), down(0, Manual::Lower, 60)});
    owners_equal(original, {{0, 0, 60, 10, Manual::Upper}});
    owners_equal(copy, {{0, 0, 60, 11, Manual::Lower}});
    accepted(original, 0, {off(0, 0, 0, 60, 10)}, {up(0, Manual::Upper, 60)});
    owners_equal(copy, {{0, 0, 60, 11, Manual::Lower}});
}

} // namespace

int main() {
    test_defaults_and_checked_routes();
    test_identified_owners_and_reuse();
    test_fifo_and_original_manual();
    test_channel_release_scope_and_order();
    test_anonymous_origin_scoping();
    test_every_valid_destination_and_velocity();
    test_invalid_domains_and_timing();
    test_owner_capacity_and_transaction();
    test_input_output_capacities();
    test_partition_and_zero_frame_equivalence();
    test_owned_copies();
    std::cout << "note ownership: " << accepted_calls << " accepted calls, "
              << rejected_calls << " atomic rejections with future checks, "
              << expected_physical_events << " expected physical events, "
              << checked_owner_rows << " retained owner rows, "
              << partition_cases << " partition/flush cases\n";
}
