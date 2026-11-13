#include "TestSupport.h"
#include "hammond/PedalNoteOwnership.h"

#include <algorithm>
#include <array>
#include <cstdint>
#include <initializer_list>
#include <limits>
#include <span>
#include <type_traits>
#include <vector>

namespace {

using hammond::Event;
using hammond::EventType;
using hammond::Manual;
using hammond::PedalId;
using hammond::PedalNoteEvent;
using hammond::PedalNoteKind;
using hammond::PedalNoteOwnership;
using hammond::PedalOwnerSnapshot;
using hammond::Status;

constexpr std::size_t kStorage = hammond::kMaxEventsPerBlock + 64;
constexpr Event kSentinel{0xabcdefU, static_cast<EventType>(255),
                          Manual::Upper, 255, -123.25};
std::size_t accepted_calls = 0;
std::size_t rejected_calls = 0;
std::size_t compared_events = 0;
std::size_t compared_owners = 0;
std::size_t partition_cases = 0;

PedalNoteEvent on(std::uint32_t offset, std::uint8_t bus, std::uint8_t channel,
                  std::uint8_t pedal, std::int32_t id = -1, std::uint8_t velocity = 100) {
    return {offset, PedalNoteKind::On, bus, channel, PedalId{pedal}, velocity, id};
}

PedalNoteEvent off(std::uint32_t offset, std::uint8_t bus, std::uint8_t channel,
                   std::uint8_t pedal, std::int32_t id = -1) {
    return {offset, PedalNoteKind::Off, bus, channel, PedalId{pedal}, 0, id};
}

PedalNoteEvent panic(std::uint32_t offset, std::uint8_t bus, std::uint8_t channel) {
    return {offset, PedalNoteKind::AllNotesOff, bus, channel, PedalId{0}, 0, -1};
}

Event down(std::uint32_t offset, std::uint8_t pedal, std::uint8_t velocity = 100) {
    return {offset, EventType::PedalOn, Manual::Lower, pedal, static_cast<double>(velocity)};
}

Event up(std::uint32_t offset, std::uint8_t pedal) {
    return {offset, EventType::PedalOff, Manual::Lower, pedal, 0.0};
}

bool same_event(const Event& a, const Event& b) {
    return a.offset == b.offset && a.type == b.type && a.manual == b.manual &&
           a.index == b.index && a.value == b.value;
}

void events_equal(std::span<const Event> actual, std::span<const Event> expected) {
    CHECK(actual.size() == expected.size());
    for (std::size_t i = 0; i < actual.size(); ++i) {
        CHECK(same_event(actual[i], expected[i]));
        ++compared_events;
    }
}

void accepted(PedalNoteOwnership& owners, std::uint32_t frames,
              std::span<const PedalNoteEvent> input, std::span<const Event> expected,
              std::size_t capacity = hammond::kMaxEventsPerBlock) {
    CHECK(capacity <= kStorage);
    std::array<Event, kStorage> output;
    output.fill(kSentinel);
    const auto result = owners.translate(frames, input, std::span<Event>(output).first(capacity));
    CHECK(result.status == Status::Ok);
    CHECK(result.ok());
    CHECK(static_cast<bool>(result));
    CHECK(result.input_consumed == input.size());
    CHECK(result.output_events == expected.size());
    events_equal(std::span<const Event>(output).first(result.output_events), expected);
    for (std::size_t i = result.output_events; i < output.size(); ++i) {
        CHECK(same_event(output[i], kSentinel));
    }
    for (std::size_t i = 0; i < result.output_events; ++i) {
        CHECK(output[i].manual == Manual::Lower);
        CHECK(output[i].type == EventType::PedalOn || output[i].type == EventType::PedalOff);
        CHECK(output[i].index >= 1 && output[i].index <= 25);
    }
    ++accepted_calls;
}

void accepted(PedalNoteOwnership& owners, std::uint32_t frames,
              std::initializer_list<PedalNoteEvent> input, std::initializer_list<Event> expected,
              std::size_t capacity = hammond::kMaxEventsPerBlock) {
    accepted(owners, frames, std::span<const PedalNoteEvent>(input.begin(), input.size()),
             std::span<const Event>(expected.begin(), expected.size()), capacity);
}

void owners_equal(const PedalNoteOwnership& owners,
                  std::span<const PedalOwnerSnapshot> expected) {
    CHECK(owners.owner_count() == expected.size());
    for (std::size_t i = 0; i < expected.size(); ++i) {
        PedalOwnerSnapshot actual{255, 255, PedalId{255}, -99};
        CHECK(owners.owner_snapshot(i, actual));
        CHECK(actual == expected[i]);
        ++compared_owners;
    }
    for (const std::size_t invalid : {expected.size(), std::numeric_limits<std::size_t>::max()}) {
        const PedalOwnerSnapshot sentinel{255, 255, PedalId{255}, -99};
        auto actual = sentinel;
        CHECK(!owners.owner_snapshot(invalid, actual));
        CHECK(actual == sentinel);
    }
    for (std::uint8_t pedal = 1; pedal <= 25; ++pedal) {
        const auto count = static_cast<std::size_t>(std::count_if(
            expected.begin(), expected.end(), [pedal](const auto& owner) {
                return owner.pedal.value == pedal;
            }));
        std::size_t actual = 12345;
        CHECK(owners.owner_count(PedalId{pedal}, actual));
        CHECK(actual == count);
    }
}

void owners_equal(const PedalNoteOwnership& owners,
                  std::initializer_list<PedalOwnerSnapshot> expected) {
    owners_equal(owners, std::span<const PedalOwnerSnapshot>(expected.begin(), expected.size()));
}

// Observe the future after every failed call: remove all origin channels and
// exercise a new maximal identified pair. This also checks surviving counts.
void unchanged_future(PedalNoteOwnership actual, PedalNoteOwnership expected) {
    std::array<PedalNoteEvent, 34> input{};
    std::size_t i = 0;
    for (std::uint8_t bus = 0; bus < 2; ++bus) {
        for (std::uint8_t channel = 0; channel < 16; ++channel) {
            input[i++] = panic(0, bus, channel);
        }
    }
    input[i++] = on(0, 1, 15, 25, std::numeric_limits<std::int32_t>::max(), 127);
    input[i++] = off(0, 1, 15, 25, std::numeric_limits<std::int32_t>::max());
    CHECK(i == input.size());
    std::array<Event, hammond::kMaxEventsPerBlock> a{};
    std::array<Event, hammond::kMaxEventsPerBlock> b{};
    const auto ar = actual.translate(0, input, a);
    const auto br = expected.translate(0, input, b);
    CHECK(ar.ok() && br.ok());
    CHECK(ar.input_consumed == input.size() && br.input_consumed == input.size());
    events_equal(std::span<const Event>(a).first(ar.output_events),
                 std::span<const Event>(b).first(br.output_events));
    CHECK(actual == expected);
    CHECK(actual.owner_count() == 0);
}

void rejected(PedalNoteOwnership& owners, std::uint32_t frames,
              std::span<const PedalNoteEvent> input, Status status,
              std::size_t capacity = hammond::kMaxEventsPerBlock) {
    CHECK(capacity <= kStorage);
    const auto before = owners;
    std::array<Event, kStorage> output;
    output.fill(kSentinel);
    const auto result = owners.translate(frames, input, std::span<Event>(output).first(capacity));
    CHECK(result.status == status);
    CHECK(!result.ok() && !static_cast<bool>(result));
    CHECK(result.input_consumed == 0 && result.output_events == 0);
    CHECK(owners == before);
    for (const auto& item : output) CHECK(same_event(item, kSentinel));
    unchanged_future(owners, before);
    ++rejected_calls;
}

void rejected(PedalNoteOwnership& owners, std::uint32_t frames,
              std::initializer_list<PedalNoteEvent> input, Status status,
              std::size_t capacity = hammond::kMaxEventsPerBlock) {
    rejected(owners, frames, std::span<const PedalNoteEvent>(input.begin(), input.size()),
             status, capacity);
}

void test_defaults_and_queries() {
    static_assert(std::is_trivially_copyable_v<PedalNoteOwnership>);
    static_assert(std::is_nothrow_copy_assignable_v<PedalNoteOwnership>);
    static_assert(noexcept(PedalNoteOwnership{}.translate(0, {}, {})));
    CHECK(hammond::kPedalInputBusCount == 2);
    CHECK(hammond::kPedalInputChannelCount == 16);
    CHECK(hammond::kMaxPedalNoteOwners == 256);
    CHECK(hammond::kPedalNoteOwnershipModelId == "bounded-fifo-pedal-note-ownership-v1");
    PedalNoteOwnership owners;
    owners_equal(owners, {});
    accepted(owners, 0, {}, {}, 0);
    accepted(owners, hammond::kHardMaxBlockFrames, {}, {}, 0);
    for (const std::uint8_t invalid : {std::uint8_t{0}, std::uint8_t{26}, std::uint8_t{255}}) {
        std::size_t destination = 12345;
        CHECK(!owners.owner_count(PedalId{invalid}, destination));
        CHECK(destination == 12345);
    }
    accepted(owners, 0, {off(0, 0, 0, 1), on(0, 1, 15, 25, -1, 0), panic(0, 0, 1)}, {}, 0);
    owners_equal(owners, {});
}

void test_identified_and_fifo() {
    PedalNoteOwnership owners;
    const auto maximum = std::numeric_limits<std::int32_t>::max();
    accepted(owners, 8, {on(0, 0, 0, 1, 0, 1), on(1, 0, 0, 1, 0, 127),
                         on(2, 1, 0, 1, 0), on(3, 0, 1, 1, 0), on(4, 1, 15, 25, maximum)},
                        {down(0, 1, 1), down(4, 25)});
    owners_equal(owners, {{0, 0, {1}, 0}, {1, 0, {1}, 0}, {0, 1, {1}, 0}, {1, 15, {25}, maximum}});
    rejected(owners, 0, {on(0, 0, 0, 2, 0)}, Status::InvalidEvent);
    rejected(owners, 0, {off(0, 1, 15, 24, maximum)}, Status::InvalidEvent);
    rejected(owners, 0, {on(0, 1, 15, 24, maximum, 0)}, Status::InvalidEvent);
    accepted(owners, 0, {off(0, 0, 0, 1, 0), off(0, 1, 0, 1, 0),
                         off(0, 1, 0, 1, 0), on(0, 0, 1, 1, 0, 0)}, {up(0, 1)});
    owners_equal(owners, {{1, 15, {25}, maximum}});
    accepted(owners, 0, {off(0, 1, 15, 25, maximum)}, {up(0, 25)});
    owners_equal(owners, {});

    // Interleave other owners so FIFO order is externally observable in the
    // surviving snapshots; anonymous release must not consume identified ID 7.
    accepted(owners, 0, {on(0, 0, 0, 7), on(0, 0, 0, 9, 7),
                         on(0, 0, 0, 7), on(0, 0, 0, 7, 8)},
                        {down(0, 7), down(0, 9)});
    accepted(owners, 0, {off(0, 0, 0, 7)}, {}, 0);
    owners_equal(owners, {{0, 0, {9}, 7}, {0, 0, {7}, -1}, {0, 0, {7}, 8}});
    accepted(owners, 0, {off(0, 0, 0, 7), off(0, 0, 0, 7)}, {}, 0);
    owners_equal(owners, {{0, 0, {9}, 7}, {0, 0, {7}, 8}});
    accepted(owners, 0, {panic(0, 0, 0)}, {up(0, 9), up(0, 7)});
    owners_equal(owners, {});
}

void test_every_origin_and_pedal() {
    // Independently declare 32 distinct origin owners for each pedal. No
    // physical release is expected until the reverse-order final retirement.
    for (std::uint8_t pedal = 1; pedal <= 25; ++pedal) {
        PedalNoteOwnership owners;
        std::array<PedalNoteEvent, 32> presses{};
        std::array<PedalNoteEvent, 32> releases{};
        std::array<PedalOwnerSnapshot, 32> expected{};
        std::size_t i = 0;
        for (std::uint8_t bus = 0; bus < 2; ++bus) {
            for (std::uint8_t channel = 0; channel < 16; ++channel) {
                const std::int32_t identity = channel % 2 == 0 ? -1 : 0;
                presses[i] = on(static_cast<std::uint32_t>(i), bus, channel, pedal, identity);
                releases[31 - i] = off(static_cast<std::uint32_t>(31 - i), bus, channel, pedal, identity);
                expected[i] = {bus, channel, PedalId{pedal}, identity};
                ++i;
            }
        }
        const std::array<Event, 1> make{down(0, pedal)};
        accepted(owners, 32, presses, make);
        owners_equal(owners, expected);
        const std::array<Event, 1> release{up(31, pedal)};
        accepted(owners, 32, releases, release);
        owners_equal(owners, {});
    }
}

void test_scoped_panic_and_stable_ties() {
    PedalNoteOwnership owners;
    accepted(owners, 1, {on(0, 0, 1, 4), on(0, 0, 1, 2, 1), on(0, 1, 1, 4, 1),
                         on(0, 0, 2, 2), on(0, 0, 1, 7, 2), on(0, 0, 1, 7),
                         panic(0, 0, 1), on(0, 0, 1, 7, 2)},
                        {down(0, 4), down(0, 2), down(0, 7), up(0, 7), down(0, 7)});
    owners_equal(owners, {{1, 1, {4}, 1}, {0, 2, {2}, -1}, {0, 1, {7}, 2}});
    accepted(owners, 0, {panic(0, 0, 1), panic(0, 1, 1), panic(0, 0, 2)},
                        {up(0, 7), up(0, 4), up(0, 2)});
    owners_equal(owners, {});
}

void test_payload_and_timeline_atomicity() {
    PedalNoteOwnership owners;
    accepted(owners, 0, {on(0, 1, 15, 25, 42)}, {down(0, 25)});
    std::vector<PedalNoteEvent> invalid;
    for (const auto kind : {PedalNoteKind::On, PedalNoteKind::Off, PedalNoteKind::AllNotesOff}) {
        auto value = kind == PedalNoteKind::On ? on(1, 0, 0, 1) :
                     kind == PedalNoteKind::Off ? off(1, 0, 0, 1) : panic(1, 0, 0);
        for (const std::uint8_t bus : {std::uint8_t{2}, std::uint8_t{255}}) {
            auto bad = value; bad.bus = bus; invalid.push_back(bad);
        }
        for (const std::uint8_t channel : {std::uint8_t{16}, std::uint8_t{255}}) {
            auto bad = value; bad.channel = channel; invalid.push_back(bad);
        }
        for (const std::int32_t id : {-2, std::numeric_limits<std::int32_t>::min()}) {
            auto bad = value; bad.note_id = id; invalid.push_back(bad);
        }
    }
    for (const std::uint8_t pedal : {std::uint8_t{0}, std::uint8_t{26}, std::uint8_t{36}, std::uint8_t{255}}) {
        invalid.push_back(on(1, 0, 0, pedal)); invalid.push_back(off(1, 0, 0, pedal));
    }
    invalid.push_back(on(1, 0, 0, 1, -1, 128));
    invalid.push_back(on(1, 0, 0, 1, -1, 255));
    for (const std::uint8_t velocity : {std::uint8_t{1}, std::uint8_t{127}, std::uint8_t{255}}) {
        auto bad = off(1, 0, 0, 1); bad.velocity = velocity; invalid.push_back(bad);
        bad = panic(1, 0, 0); bad.velocity = velocity; invalid.push_back(bad);
    }
    for (const std::uint8_t pedal : {std::uint8_t{1}, std::uint8_t{25}, std::uint8_t{255}}) {
        auto bad = panic(1, 0, 0); bad.pedal = PedalId{pedal}; invalid.push_back(bad);
    }
    for (const std::int32_t id : {0, std::numeric_limits<std::int32_t>::max()}) {
        auto bad = panic(1, 0, 0); bad.note_id = id; invalid.push_back(bad);
    }
    for (const std::uint8_t kind : {std::uint8_t{3}, std::uint8_t{255}}) {
        auto bad = on(1, 0, 0, 1); bad.kind = static_cast<PedalNoteKind>(kind); invalid.push_back(bad);
    }
    for (const auto& bad : invalid) {
        rejected(owners, 2, {on(0, 0, 0, 1), bad}, Status::InvalidEvent);
    }
    rejected(owners, 0, {on(1, 0, 0, 1)}, Status::InvalidEvent);
    rejected(owners, 1, {on(1, 0, 0, 1)}, Status::InvalidEvent);
    rejected(owners, 2, {on(1, 0, 0, 1), off(0, 0, 0, 1)}, Status::InvalidEvent);
    rejected(owners, 65536, {on(std::numeric_limits<std::uint32_t>::max(), 0, 0, 1)}, Status::InvalidEvent);
    std::array<PedalNoteEvent, 1025> too_many{};
    rejected(owners, 65537, too_many, Status::BlockTooLarge, 0);
    rejected(owners, 0, too_many, Status::TooManyEvents, 0);
    rejected(owners, 0, {on(0, 0, 0, 1)}, Status::TooManyEvents, 0);
    rejected(owners, 0, {on(0, 0, 0, 1), off(0, 0, 0, 1)}, Status::TooManyEvents, 1);
    // Payload preflight outranks earlier dynamic output overflow.
    rejected(owners, 2, {on(0, 0, 0, 1), on(2, 0, 0, 1)}, Status::InvalidEvent, 0);
}

void test_owner_capacity_and_reuse() {
    PedalNoteOwnership owners;
    std::array<PedalNoteEvent, 256> presses{};
    std::array<PedalOwnerSnapshot, 256> expected{};
    for (std::size_t i = 0; i < presses.size(); ++i) {
        presses[i] = on(0, 0, 0, 13, static_cast<std::int32_t>(i));
        expected[i] = {0, 0, PedalId{13}, static_cast<std::int32_t>(i)};
    }
    const std::array<Event, 1> make{down(0, 13)};
    accepted(owners, 0, presses, make, 1);
    owners_equal(owners, expected);
    accepted(owners, 0, {on(0, 0, 0, 13, 255, 127)}, {}, 0);
    rejected(owners, 0, {on(0, 0, 0, 13, 256)}, Status::TooManyEvents);
    rejected(owners, 0, {on(0, 0, 0, 14, 255)}, Status::InvalidEvent);
    // A retirement in the same batch frees a slot; the physical pedal stays held.
    accepted(owners, 0, {off(0, 0, 0, 13, 0), on(0, 1, 15, 13, 256)}, {}, 0);
    CHECK(owners.owner_count() == 256);
    accepted(owners, 0, {panic(0, 0, 0)}, {}, 0);
    owners_equal(owners, {{1, 15, {13}, 256}});
    accepted(owners, 0, {panic(0, 1, 15)}, {up(0, 13)});

    // Failed late identity reuse restores an earlier successful retirement.
    accepted(owners, 0, {on(0, 0, 0, 1, 7), on(0, 0, 0, 2, 8)}, {down(0, 1), down(0, 2)});
    rejected(owners, 0, {off(0, 0, 0, 1, 7), on(0, 0, 0, 3, 8)}, Status::InvalidEvent);
}

PedalNoteOwnership preload_all_pedals() {
    PedalNoteOwnership owners;
    std::array<PedalNoteEvent, 25> input{};
    std::array<Event, 25> expected{};
    for (std::size_t i = 0; i < input.size(); ++i) {
        const auto pedal = static_cast<std::uint8_t>(i + 1);
        input[i] = on(0, 0, 0, pedal);
        expected[i] = down(0, pedal);
    }
    accepted(owners, 0, input, expected);
    return owners;
}

void test_emitted_capacity() {
    auto owners = preload_all_pedals();
    rejected(owners, 0, {panic(0, 0, 0)}, Status::TooManyEvents, 24);
    std::vector<PedalNoteEvent> input{panic(0, 0, 0)};
    std::vector<Event> expected;
    for (std::uint8_t pedal = 1; pedal <= 25; ++pedal) expected.push_back(up(0, pedal));
    for (std::size_t i = 0; i < 499; ++i) {
        input.push_back(on(0, 0, 0, 1)); input.push_back(off(0, 0, 0, 1));
        expected.push_back(down(0, 1)); expected.push_back(up(0, 1));
    }
    input.push_back(on(0, 0, 0, 1)); expected.push_back(down(0, 1));
    CHECK(input.size() == 1000 && expected.size() == 1024);
    rejected(owners, 0, input, Status::TooManyEvents, 1023);
    auto excessive = input;
    excessive.push_back(off(0, 0, 0, 1));
    CHECK(excessive.size() < hammond::kMaxEventsPerBlock);
    rejected(owners, 0, excessive, Status::TooManyEvents, kStorage);
    accepted(owners, 0, input, expected, kStorage);
    owners_equal(owners, {{0, 0, {1}, -1}});
    accepted(owners, 0, {off(0, 0, 0, 1)}, {up(0, 1)});

    // Exactly 1,024 raw commands can be accepted even with zero physical output.
    std::array<PedalNoteEvent, 1024> unmatched{};
    for (auto& event : unmatched) event = off(0, 0, 0, 25, 77);
    accepted(owners, 0, unmatched, std::span<const Event>{}, 0);
}

void test_partition_invariance() {
    const std::vector<PedalNoteEvent> timeline{
        on(0, 0, 0, 1), on(0, 1, 0, 1, 4), on(1, 0, 1, 25, 9),
        on(3, 0, 0, 1), off(7, 0, 0, 1), off(7, 1, 0, 1, 4),
        on(8, 1, 15, 13), panic(15, 0, 0), off(16, 1, 15, 13),
        on(31, 0, 1, 25, 9), on(32, 1, 1, 25, 9), panic(63, 0, 1),
        off(64, 1, 1, 25, 9), on(65, 0, 0, 7, 0), off(65, 0, 0, 7, 0),
        on(65, 0, 0, 7, 0), on(127, 1, 15, 2)};
    const std::array<Event, 10> expected{{
        down(0, 1), down(1, 25), down(8, 13), up(15, 1), up(16, 13),
        up(64, 25), down(65, 7), up(65, 7), down(65, 7), down(127, 2)}};
    PedalNoteOwnership whole;
    accepted(whole, 128, timeline, expected);
    for (const std::uint32_t block : {1U, 3U, 7U, 16U, 64U, 127U, 128U}) {
        PedalNoteOwnership partitioned;
        std::vector<Event> actual;
        std::size_t cursor = 0;
        for (std::uint32_t start = 0; start < 128;) {
            const std::uint32_t length = std::min(block, 128 - start);
            std::vector<PedalNoteEvent> local;
            while (cursor < timeline.size() && timeline[cursor].offset < start + length) {
                auto event = timeline[cursor++]; event.offset -= start; local.push_back(event);
            }
            std::array<Event, hammond::kMaxEventsPerBlock> output{};
            const auto result = partitioned.translate(length, local, output);
            CHECK(result.ok());
            CHECK(result.input_consumed == local.size());
            for (std::size_t i = 0; i < result.output_events; ++i) {
                output[i].offset += start; actual.push_back(output[i]);
            }
            start += length;
        }
        events_equal(actual, expected);
        CHECK(cursor == timeline.size());
        CHECK(partitioned == whole);
        ++partition_cases;
    }
    owners_equal(whole, {{0, 0, {7}, 0}, {1, 15, {2}, -1}});
}

} // namespace

int main() {
    test_defaults_and_queries();
    test_identified_and_fifo();
    test_every_origin_and_pedal();
    test_scoped_panic_and_stable_ties();
    test_payload_and_timeline_atomicity();
    test_owner_capacity_and_reuse();
    test_emitted_capacity();
    test_partition_invariance();
    std::cout << "pedal ownership: " << accepted_calls << " accepted calls, "
              << rejected_calls << " atomic rejection/future checks, " << compared_events
              << " exact event comparisons, " << compared_owners << " owner rows, "
              << partition_cases << " partitions; sizeof=" << sizeof(PedalNoteOwnership) << '\n';
}
