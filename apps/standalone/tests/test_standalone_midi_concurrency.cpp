#include "MidiInput.h"
#include "TestSupport.h"

#include <algorithm>
#include <array>
#include <atomic>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <limits>
#include <memory>
#include <new>
#include <span>
#include <thread>
#include <variant>

// Keep the interposition boundary visible under optimization. GCC otherwise
// diagnoses an inlined malloc-backed new paired with sized delete as mismatched.
#if defined(_MSC_VER)
#define HAMMOND_PROBE_NOINLINE __declspec(noinline)
#elif defined(__GNUC__) || defined(__clang__)
#define HAMMOND_PROBE_NOINLINE __attribute__((noinline))
#else
#define HAMMOND_PROBE_NOINLINE
#endif

// These replacements belong only to this test executable. The probe observes
// this thread's global C++ allocation/deallocation calls, not arbitrary C heap,
// system allocation, other threads, locking, or callback elapsed time.
namespace allocation_probe {

struct Counts {
    std::size_t allocations{};
    std::size_t deallocations{};
};

thread_local bool recording = false;
thread_local Counts counts{};

void allocation() noexcept {
    if (recording) ++counts.allocations;
}

void deallocation(void* pointer) noexcept {
    if (recording && pointer != nullptr) ++counts.deallocations;
}

void begin() noexcept {
    counts = {};
    recording = true;
}

[[nodiscard]] Counts end() noexcept {
    recording = false;
    return counts;
}

[[nodiscard]] void* allocate_bytes(std::size_t size) {
    if (size == 0) size = 1;
    for (;;) {
        if (void* pointer = std::malloc(size)) return pointer;
        const auto handler = std::get_new_handler();
        if (handler == nullptr) throw std::bad_alloc{};
        handler();
    }
}

// Portable aligned storage: retain the malloc base in bytes preceding the
// aligned payload. No dependency on POSIX or MSVC aligned-allocation APIs.
[[nodiscard]] void* allocate_aligned(std::size_t size, std::size_t alignment) {
    if (size == 0) size = 1;
    if (alignment == 0 || (alignment & (alignment - 1)) != 0) throw std::bad_alloc{};
    alignment = std::max(alignment, alignof(void*));
    constexpr auto maximum = std::numeric_limits<std::size_t>::max();
    if (alignment - 1 > maximum - sizeof(void*)) throw std::bad_alloc{};
    const auto overhead = sizeof(void*) + alignment - 1;
    if (size > maximum - overhead) throw std::bad_alloc{};
    void* base = allocate_bytes(size + overhead);
    void* payload = static_cast<unsigned char*>(base) + sizeof(void*);
    auto space = size + alignment - 1;
    if (std::align(alignment, size, payload, space) == nullptr) {
        std::free(base);
        throw std::bad_alloc{};
    }
    std::memcpy(static_cast<unsigned char*>(payload) - sizeof(base), &base, sizeof(base));
    return payload;
}

void free_aligned(void* pointer) noexcept {
    if (pointer == nullptr) return;
    void* base = nullptr;
    std::memcpy(&base, static_cast<unsigned char*>(pointer) - sizeof(base), sizeof(base));
    std::free(base);
}

} // namespace allocation_probe

HAMMOND_PROBE_NOINLINE void* operator new(std::size_t size) {
    allocation_probe::allocation();
    return allocation_probe::allocate_bytes(size);
}
HAMMOND_PROBE_NOINLINE void* operator new[](std::size_t size) { return ::operator new(size); }
HAMMOND_PROBE_NOINLINE void* operator new(std::size_t size, const std::nothrow_t&) noexcept {
    try { return ::operator new(size); } catch (...) { return nullptr; }
}
HAMMOND_PROBE_NOINLINE void* operator new[](std::size_t size, const std::nothrow_t&) noexcept {
    try { return ::operator new[](size); } catch (...) { return nullptr; }
}
HAMMOND_PROBE_NOINLINE void operator delete(void* pointer) noexcept {
    allocation_probe::deallocation(pointer);
    std::free(pointer);
}
HAMMOND_PROBE_NOINLINE void operator delete[](void* pointer) noexcept { ::operator delete(pointer); }
HAMMOND_PROBE_NOINLINE void operator delete(void* pointer, std::size_t) noexcept {
    ::operator delete(pointer);
}
HAMMOND_PROBE_NOINLINE void operator delete[](void* pointer, std::size_t) noexcept {
    ::operator delete[](pointer);
}
HAMMOND_PROBE_NOINLINE void operator delete(void* pointer, const std::nothrow_t&) noexcept {
    ::operator delete(pointer);
}
HAMMOND_PROBE_NOINLINE void operator delete[](void* pointer, const std::nothrow_t&) noexcept {
    ::operator delete[](pointer);
}

HAMMOND_PROBE_NOINLINE void* operator new(std::size_t size, std::align_val_t alignment) {
    allocation_probe::allocation();
    return allocation_probe::allocate_aligned(size, static_cast<std::size_t>(alignment));
}
HAMMOND_PROBE_NOINLINE void* operator new[](std::size_t size, std::align_val_t alignment) {
    return ::operator new(size, alignment);
}
HAMMOND_PROBE_NOINLINE void* operator new(std::size_t size, std::align_val_t alignment,
                   const std::nothrow_t&) noexcept {
    try { return ::operator new(size, alignment); } catch (...) { return nullptr; }
}
HAMMOND_PROBE_NOINLINE void* operator new[](std::size_t size, std::align_val_t alignment,
                     const std::nothrow_t&) noexcept {
    try { return ::operator new[](size, alignment); } catch (...) { return nullptr; }
}
HAMMOND_PROBE_NOINLINE void operator delete(void* pointer, std::align_val_t) noexcept {
    allocation_probe::deallocation(pointer);
    allocation_probe::free_aligned(pointer);
}
HAMMOND_PROBE_NOINLINE void operator delete[](void* pointer, std::align_val_t alignment) noexcept {
    ::operator delete(pointer, alignment);
}
HAMMOND_PROBE_NOINLINE void operator delete(void* pointer, std::size_t,
                                           std::align_val_t alignment) noexcept {
    ::operator delete(pointer, alignment);
}
HAMMOND_PROBE_NOINLINE void operator delete[](void* pointer, std::size_t,
                                             std::align_val_t alignment) noexcept {
    ::operator delete[](pointer, alignment);
}
HAMMOND_PROBE_NOINLINE void operator delete(void* pointer, std::align_val_t alignment,
                                           const std::nothrow_t&) noexcept {
    ::operator delete(pointer, alignment);
}
HAMMOND_PROBE_NOINLINE void operator delete[](void* pointer, std::align_val_t alignment,
                       const std::nothrow_t&) noexcept {
    ::operator delete[](pointer, alignment);
}

#undef HAMMOND_PROBE_NOINLINE

namespace {

using namespace hammond;
using namespace hammond::standalone;

// Explicit calls through volatile function pointers prevent new-expression
// allocation elision from making the instrumentation calibration vacuous.
template <typename Function>
[[nodiscard]] Function opaque(Function function) noexcept {
    Function volatile pointer = function;
    return pointer;
}

void test_probe_overloads() {
    using New = void* (*)(std::size_t);
    using NothrowNew = void* (*)(std::size_t, const std::nothrow_t&) noexcept;
    using AlignedNew = void* (*)(std::size_t, std::align_val_t);
    using AlignedNothrowNew = void* (*)(std::size_t, std::align_val_t,
                                      const std::nothrow_t&) noexcept;
    using Delete = void (*)(void*) noexcept;
    using SizedDelete = void (*)(void*, std::size_t) noexcept;
    using NothrowDelete = void (*)(void*, const std::nothrow_t&) noexcept;
    using AlignedDelete = void (*)(void*, std::align_val_t) noexcept;
    using AlignedSizedDelete = void (*)(void*, std::size_t, std::align_val_t) noexcept;
    using AlignedNothrowDelete = void (*)(void*, std::align_val_t,
                                        const std::nothrow_t&) noexcept;
    constexpr std::align_val_t alignment{64};
    std::array<void*, 12> pointers{};

    // Calibration is deliberately separate from all Engine observations.
    allocation_probe::begin();
    pointers[0] = opaque(static_cast<New>(&::operator new))(0);
    pointers[1] = opaque(static_cast<New>(&::operator new[]))(23);
    pointers[2] = opaque(static_cast<New>(&::operator new))(31);
    pointers[3] = opaque(static_cast<New>(&::operator new[]))(41);
    pointers[4] = opaque(static_cast<NothrowNew>(&::operator new))(51, std::nothrow);
    pointers[5] = opaque(static_cast<NothrowNew>(&::operator new[]))(61, std::nothrow);
    pointers[6] = opaque(static_cast<AlignedNew>(&::operator new))(0, alignment);
    pointers[7] = opaque(static_cast<AlignedNew>(&::operator new[]))(77, alignment);
    pointers[8] = opaque(static_cast<AlignedNew>(&::operator new))(83, alignment);
    pointers[9] = opaque(static_cast<AlignedNew>(&::operator new[]))(89, alignment);
    pointers[10] = opaque(static_cast<AlignedNothrowNew>(&::operator new))(
        97, alignment, std::nothrow);
    pointers[11] = opaque(static_cast<AlignedNothrowNew>(&::operator new[]))(
        101, alignment, std::nothrow);
    const auto allocated = allocation_probe::end();
    CHECK(allocated.allocations == pointers.size());
    CHECK(allocated.deallocations == 0);
    for (std::size_t index = 0; index < pointers.size(); ++index) {
        CHECK(pointers[index] != nullptr);
        if (index >= 6) CHECK(reinterpret_cast<std::uintptr_t>(pointers[index]) % 64 == 0);
    }

    allocation_probe::begin();
    opaque(static_cast<Delete>(&::operator delete))(pointers[0]);
    opaque(static_cast<Delete>(&::operator delete[]))(pointers[1]);
    opaque(static_cast<SizedDelete>(&::operator delete))(pointers[2], 31);
    opaque(static_cast<SizedDelete>(&::operator delete[]))(pointers[3], 41);
    opaque(static_cast<NothrowDelete>(&::operator delete))(pointers[4], std::nothrow);
    opaque(static_cast<NothrowDelete>(&::operator delete[]))(pointers[5], std::nothrow);
    opaque(static_cast<AlignedDelete>(&::operator delete))(pointers[6], alignment);
    opaque(static_cast<AlignedDelete>(&::operator delete[]))(pointers[7], alignment);
    opaque(static_cast<AlignedSizedDelete>(&::operator delete))(pointers[8], 83, alignment);
    opaque(static_cast<AlignedSizedDelete>(&::operator delete[]))(pointers[9], 89, alignment);
    opaque(static_cast<AlignedNothrowDelete>(&::operator delete))(
        pointers[10], alignment, std::nothrow);
    opaque(static_cast<AlignedNothrowDelete>(&::operator delete[]))(
        pointers[11], alignment, std::nothrow);
    const auto freed = allocation_probe::end();
    CHECK(freed.allocations == 0);
    CHECK(freed.deallocations == pointers.size());
}

struct Measurements {
    std::uint64_t pushes{};
    std::uint64_t pops{};
    std::uint64_t decodes{};
    std::uint64_t faults{};

    void add(const Measurements& other) noexcept {
        pushes += other.pushes;
        pops += other.pops;
        decodes += other.decodes;
        faults += other.faults;
    }
};

void quiet(const allocation_probe::Counts& counts) {
    CHECK(counts.allocations == 0);
    CHECK(counts.deallocations == 0);
}

// Fixture preparation, assertions, diagnostics, waiting, thread creation/join
// and logging stay outside each observed region. Each worker owns its tally.
[[nodiscard]] MidiPushResult push(MidiInbox& inbox,
                                  std::span<const std::uint8_t> bytes,
                                  std::uint64_t arrival, Measurements& measured) {
    CHECK(!allocation_probe::recording);
    allocation_probe::begin();
    const auto result = inbox.push(bytes, arrival);
    const auto counts = allocation_probe::end();
    quiet(counts);
    ++measured.pushes;
    return result;
}

[[nodiscard]] bool pop(MidiInbox& inbox, MidiPacket& destination,
                       Measurements& measured) {
    CHECK(!allocation_probe::recording);
    allocation_probe::begin();
    const auto result = inbox.pop(destination);
    const auto counts = allocation_probe::end();
    quiet(counts);
    ++measured.pops;
    return result;
}

[[nodiscard]] MidiDecoded decode(MidiInput& input, const MidiPacket& packet,
                                 Measurements& measured) {
    CHECK(!allocation_probe::recording);
    allocation_probe::begin();
    const auto result = input.decode(packet);
    const auto counts = allocation_probe::end();
    quiet(counts);
    ++measured.decodes;
    return result;
}

void signal(MidiInbox& inbox, MidiInboxFault fault, Measurements& measured) {
    CHECK(!allocation_probe::recording);
    allocation_probe::begin();
    inbox.signal_fault(fault);
    const auto counts = allocation_probe::end();
    quiet(counts);
    ++measured.faults;
}

struct Deadline {
    const std::chrono::steady_clock::time_point end =
        std::chrono::steady_clock::now() + std::chrono::seconds(15);

    void check() const {
        CHECK(std::chrono::steady_clock::now() < end);
    }
};

template<class Predicate>
void await(const Deadline& deadline, Predicate ready) {
    while (!ready()) {
        deadline.check();
        std::this_thread::yield();
    }
}

constexpr auto maximum_time = std::numeric_limits<std::uint64_t>::max();
constexpr MidiPacket sentinel{{0xDE, 0xAD, 0xBE}, 255, maximum_time - 123};
constexpr std::size_t transfer_count = 65536 + 73;
constexpr std::size_t lossless_epochs = 4;
constexpr std::size_t fault_epochs = 8;
constexpr std::size_t outstanding_window = 64;
constexpr std::size_t fault_prefix = 2048;
constexpr std::size_t parked_tail = 64;
constexpr std::size_t racing_attempts = 96;
constexpr std::size_t acknowledged_fault_attempts = 24;
static_assert(kMidiInboxCapacity == 256 && kMidiDrainBudget == 32);
static_assert(outstanding_window < kMidiInboxCapacity);
static_assert(parked_tail + racing_attempts < kMidiInboxCapacity);

void same_packet(const MidiPacket& actual, const MidiPacket& expected) {
    CHECK(actual.bytes == expected.bytes);
    CHECK(actual.size == expected.size);
    CHECK(actual.arrival_ns == expected.arrival_ns);
}

void no_pop(MidiInbox& inbox, Measurements& measured) {
    auto destination = sentinel;
    CHECK(!pop(inbox, destination, measured));
    same_packet(destination, sentinel);
}

// Literal wire fixtures and expected outcomes follow docs/MIDI_INPUT.md,
// independently of the implementation's decoder tables and ring indices.
[[nodiscard]] MidiPacket packet_at(std::size_t sequence, std::size_t epoch) {
    const auto value = static_cast<std::uint8_t>((sequence * 37 + epoch * 29) % 128);
    const auto velocity = static_cast<std::uint8_t>(1 + (sequence + epoch * 3) % 127);
    const auto pitch = static_cast<std::uint8_t>(36 + (sequence + epoch) % 61);
    const auto drawbar = static_cast<std::uint8_t>(16 + (sequence / 16 + epoch) % 9);
    const auto pedal_drawbar = static_cast<std::uint8_t>(16 + (sequence / 16 + epoch) % 2);
    MidiPacket result{};
    result.size = 3;
    switch (sequence % 16) {
    case 0: result.bytes = {0x90, pitch, velocity}; break;
    case 1: result.bytes = {0x81, pitch, value}; break;
    case 2:
        result.bytes = {0x92, static_cast<std::uint8_t>(36 + (sequence + epoch) % 25), velocity};
        break;
    case 3: result.bytes = {0xB0, 11, value}; break;
    case 4: result.bytes = {0xB0, drawbar, value}; break;
    case 5: result.bytes = {0xB1, drawbar, value}; break;
    case 6: result.bytes = {0xB2, pedal_drawbar, value}; break;
    case 7: result.bytes = {0xB2, 123, value}; break;
    case 8: result.bytes = {0xC0, value, 0}; result.size = 2; break;
    case 9: result.bytes = {0xF8, 0, 0}; result.size = 1; break;
    case 10: result.bytes = {0x90, pitch, 0}; result.size = 2; break;
    case 11: result.bytes = {0x40, pitch, value}; break;
    case 12: result.bytes = {0x9F, pitch, velocity}; break;
    case 13: result.bytes = {0x92, 61, velocity}; break;
    case 14: result.bytes = {0x90, 0xFF, value}; break;
    case 15: result.bytes = {0x91, 96, 0}; break;
    }
    const auto base = static_cast<std::uint64_t>(epoch * 1000000 + sequence / 8 * 17);
    switch (sequence % 8) {
    case 0: case 1: result.arrival_ns = base; break;
    case 2: case 7: result.arrival_ns = maximum_time - base; break;
    case 3: case 4: result.arrival_ns = 0; break;
    case 5: result.arrival_ns = base + 9; break;
    case 6: result.arrival_ns = 3; break;
    }
    return result;
}

[[nodiscard]] MidiDecodeStatus expected_status(std::size_t sequence) {
    switch (sequence % 16) {
    case 8: case 9: return MidiDecodeStatus::Unsupported;
    case 10: case 11: case 14: return MidiDecodeStatus::Malformed;
    case 12: return MidiDecodeStatus::UnmappedChannel;
    case 13: return MidiDecodeStatus::OutOfRange;
    default: return MidiDecodeStatus::Action;
    }
}

struct DecoderOracle {
    MidiInputDiagnostics counts{};
    std::uint64_t last{};
    bool have_last{};

    void begin() noexcept {
        ++counts.epochs;
        have_last = false;
    }
    void end() noexcept { have_last = false; }
};

[[nodiscard]] MidiDecoded check_decode(MidiInput& input, const MidiPacket& packet,
                                       MidiDecodeStatus status, DecoderOracle& oracle,
                                       Measurements& measured) {
    const bool regressed = status != MidiDecodeStatus::Inactive &&
                           oracle.have_last && packet.arrival_ns < oracle.last;
    const auto result = decode(input, packet, measured);
    CHECK(result.status == status);
    CHECK(result.timestamp_regressed == regressed);
    CHECK(result.arrival_ns == (status == MidiDecodeStatus::Inactive ? 0 : packet.arrival_ns));
    ++oracle.counts.packets;
    switch (status) {
    case MidiDecodeStatus::Action: ++oracle.counts.actions; break;
    case MidiDecodeStatus::Unsupported: ++oracle.counts.unsupported; break;
    case MidiDecodeStatus::UnmappedChannel: ++oracle.counts.unmapped_channels; break;
    case MidiDecodeStatus::OutOfRange: ++oracle.counts.out_of_range; break;
    case MidiDecodeStatus::Malformed: ++oracle.counts.malformed; break;
    case MidiDecodeStatus::Inactive: ++oracle.counts.inactive; break;
    }
    if (status != MidiDecodeStatus::Inactive) {
        oracle.have_last = true;
        oracle.last = packet.arrival_ns;
    }
    if (regressed) ++oracle.counts.timestamp_regressions;
    return result;
}

void check_decoder_counters(const MidiInput& input, const DecoderOracle& oracle) {
    const auto& actual = input.diagnostics();
    const auto& expected = oracle.counts;
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

void check_sequence(MidiInput& input, const MidiPacket& received,
                    std::size_t sequence, std::size_t epoch,
                    DecoderOracle& oracle, Measurements& measured) {
    const auto expected = packet_at(sequence, epoch);
    same_packet(received, expected); // Includes every tail byte and the full timestamp.
    const auto status = expected_status(sequence);
    const auto decoded = check_decode(input, received, status, oracle, measured);
    if (status != MidiDecodeStatus::Action) return;
    const auto kind = sequence % 16;
    if (kind >= 3 && kind <= 6) {
        CHECK(std::holds_alternative<MidiParameterEdit>(decoded.action));
        const auto& edit = std::get<MidiParameterEdit>(decoded.action);
        const std::uint32_t expected_id = kind == 3 ? 8192U :
            kind == 4 ? 4112U + expected.bytes[1] - 16U :
            kind == 5 ? 4144U + expected.bytes[1] - 16U :
                        16384U + expected.bytes[1] - 16U;
        CHECK(edit.parameter_id == expected_id);
        CHECK(edit.normalized == static_cast<double>(expected.bytes[2]) / 127.0);
        return;
    }
    CHECK(std::holds_alternative<SessionCommand>(decoded.action));
    const auto& command = std::get<SessionCommand>(decoded.action);
    CHECK(std::holds_alternative<PerformanceInputEvent>(command));
    const auto& event = std::get<PerformanceInputEvent>(command);
    if (kind == 2 || kind == 7) {
        CHECK(std::holds_alternative<PedalNoteEvent>(event));
        const auto& pedal = std::get<PedalNoteEvent>(event);
        CHECK(pedal.offset == 0 && pedal.bus == 0 && pedal.channel == 3);
        CHECK(pedal.note_id == -1);
        CHECK(pedal.kind == (kind == 2 ? PedalNoteKind::On : PedalNoteKind::AllNotesOff));
        CHECK(pedal.pedal.value == (kind == 2 ? expected.bytes[1] - 35 : 0));
        CHECK(pedal.velocity == (kind == 2 ? expected.bytes[2] : 0));
    } else {
        CHECK(std::holds_alternative<HostNoteEvent>(event));
        const auto& manual = std::get<HostNoteEvent>(event);
        CHECK(manual.offset == 0 && manual.note_id == -1);
        CHECK(manual.bus == (kind == 0 ? 0 : 1));
        CHECK(manual.channel == (kind == 0 ? 1 : 2));
        CHECK(manual.kind == (kind == 0 ? HostNoteKind::On : HostNoteKind::Off));
        CHECK(manual.midi_note == expected.bytes[1]);
        CHECK(manual.velocity == (kind == 0 ? expected.bytes[2] : 0));
    }
}

// Result counts are written by the sole producer and inspected only after join.
struct Ledger {
    MidiInboxDiagnostics expected{};

    void pushed(MidiPushResult result) noexcept {
        ++expected.received_packets;
        switch (result) {
        case MidiPushResult::Accepted: ++expected.accepted_packets; break;
        case MidiPushResult::InvalidSize: ++expected.invalid_size_packets; break;
        case MidiPushResult::Faulted: ++expected.faulted_packets; break;
        case MidiPushResult::Overflow: ++expected.overflow_events; break;
        }
    }
};

void check_inbox_counters(const MidiInbox& inbox, const Ledger& ledger) {
    const auto actual = inbox.diagnostics();
    const auto& expected = ledger.expected;
    CHECK(actual.received_packets == expected.received_packets);
    CHECK(actual.accepted_packets == expected.accepted_packets);
    CHECK(actual.invalid_size_packets == expected.invalid_size_packets);
    CHECK(actual.faulted_packets == expected.faulted_packets);
    CHECK(actual.overflow_events == expected.overflow_events);
    CHECK(actual.popped_packets == expected.popped_packets);
    CHECK(actual.discarded_packets == expected.discarded_packets);
    CHECK(actual.resets == expected.resets);
    CHECK(actual.faults == expected.faults);
    // These are quiescent equalities, deliberately not live snapshot claims.
    CHECK(actual.received_packets == actual.accepted_packets + actual.invalid_size_packets +
                                    actual.faulted_packets + actual.overflow_events);
    CHECK(actual.accepted_packets == actual.popped_packets + actual.discarded_packets +
                                    inbox.pending());
}

void reset_joined(MidiInbox& inbox, Ledger& ledger) {
    const auto pending = ledger.expected.accepted_packets - ledger.expected.popped_packets -
                         ledger.expected.discarded_packets;
    CHECK(inbox.pending() == pending);
    inbox.reset_quiescent();
    ledger.expected.discarded_packets += pending;
    ++ledger.expected.resets;
    ledger.expected.faults = 0;
    CHECK(inbox.pending() == 0);
    check_inbox_counters(inbox, ledger);
}

[[nodiscard]] MidiPushResult push_sequence(MidiInbox& inbox, std::size_t sequence,
                                           std::size_t epoch, Measurements& measured) {
    auto source = packet_at(sequence, epoch);
    for (std::size_t index = source.size; index < source.bytes.size(); ++index) {
        source.bytes[index] = 0xA5;
    }
    const auto result = push(inbox, {source.bytes.data(), source.size}, source.arrival_ns, measured);
    source.bytes.fill(0xDD); // Source lifetime/mutation cannot change an accepted copy.
    return result;
}

void lossless_wraps(Measurements& total) {
    MidiInbox inbox;
    Ledger ledger;
    for (std::size_t epoch = 0; epoch < lossless_epochs; ++epoch) {
        MidiInput input;
        DecoderOracle oracle;
        CHECK(input.begin_epoch());
        oracle.begin();
        Measurements producer_measured, consumer_measured;
        std::atomic<std::size_t> consumed{0};
        std::atomic<bool> start{false};
        const Deadline deadline;
        std::size_t largest_batch = 0;
        std::thread producer([&] {
            test_probe_overloads();
            await(deadline, [&] { return start.load(std::memory_order_acquire); });
            for (std::size_t sequence = 0; sequence < transfer_count; ++sequence) {
                await(deadline, [&] {
                    const auto retired = consumed.load(std::memory_order_acquire);
                    CHECK(retired <= sequence);
                    return sequence - retired < outstanding_window;
                });
                if (sequence % 257 == 0) {
                    const std::array<std::uint8_t, 4> oversized{0xF0, 0x01, 0x02, 0xF7};
                    const auto invalid = push(inbox, sequence % 514 == 0
                        ? std::span<const std::uint8_t>{} : std::span<const std::uint8_t>{oversized},
                        maximum_time, producer_measured);
                    CHECK(invalid == MidiPushResult::InvalidSize);
                    ledger.pushed(invalid);
                }
                const auto result = push_sequence(inbox, sequence, epoch, producer_measured);
                CHECK(result == MidiPushResult::Accepted);
                ledger.pushed(result);
            }
        });
        std::thread consumer([&] {
            test_probe_overloads();
            await(deadline, [&] { return start.load(std::memory_order_acquire); });
            std::size_t sequence = 0;
            while (sequence < transfer_count) {
                deadline.check();
                std::size_t batch = 0;
                while (batch < kMidiDrainBudget && sequence < transfer_count) {
                    auto destination = sentinel;
                    if (!pop(inbox, destination, consumer_measured)) {
                        same_packet(destination, sentinel);
                        break;
                    }
                    check_sequence(input, destination, sequence, epoch, oracle, consumer_measured);
                    ++sequence;
                    ++batch;
                    consumed.store(sequence, std::memory_order_release);
                    CHECK(inbox.pending() <= kMidiInboxCapacity);
                }
                largest_batch = std::max(largest_batch, batch);
                std::this_thread::yield();
            }
            no_pop(inbox, consumer_measured);
        });
        start.store(true, std::memory_order_release);
        producer.join();
        consumer.join();
        CHECK(consumed.load(std::memory_order_acquire) == transfer_count);
        CHECK(largest_batch > 0 && largest_batch <= 32);
        ledger.expected.popped_packets += transfer_count;
        check_inbox_counters(inbox, ledger);
        check_decoder_counters(input, oracle);
        CHECK(oracle.counts.timestamp_regressions > 0);
        input.end_epoch();
        // There are no remaining producer/consumer threads at this boundary.
        reset_joined(inbox, ledger);
        no_pop(inbox, consumer_measured);
        total.add(producer_measured);
        total.add(consumer_measured);
    }
    CHECK(ledger.expected.accepted_packets == lossless_epochs * transfer_count);
    CHECK(ledger.expected.discarded_packets == 0);
}

void concurrent_fault_retirement(Measurements& total) {
    MidiInbox inbox;
    Ledger ledger;
    MidiInput input;
    DecoderOracle oracle;
    for (std::size_t epoch = 0; epoch < fault_epochs; ++epoch) {
        const std::size_t fixture_epoch = 100 + epoch;
        CHECK(input.begin_epoch());
        oracle.begin();
        Measurements producer_measured, consumer_measured, backend_measured, disconnect_measured;
        std::atomic<std::size_t> consumed{0}, produced{0};
        std::atomic<unsigned> reporters_done{0}, race_ready{0};
        std::atomic<bool> start{false}, race{false};
        const Deadline deadline;
        std::thread producer([&] {
            test_probe_overloads();
            await(deadline, [&] { return start.load(std::memory_order_acquire); });
            for (std::size_t sequence = 0; sequence < fault_prefix + parked_tail; ++sequence) {
                await(deadline, [&] {
                    const auto retired = consumed.load(std::memory_order_acquire);
                    CHECK(retired <= sequence);
                    return sequence - retired < outstanding_window;
                });
                const auto result = push_sequence(inbox, sequence, fixture_epoch, producer_measured);
                CHECK(result == MidiPushResult::Accepted);
                ledger.pushed(result);
                produced.store(sequence + 1, std::memory_order_release);
            }
            race_ready.fetch_add(1, std::memory_order_acq_rel);
            await(deadline, [&] { return race.load(std::memory_order_acquire); });
            std::size_t sequence = fault_prefix + parked_tail;
            const std::array<std::uint8_t, 4> oversized{0xF0, 0x01, 0x02, 0xF7};
            for (std::size_t attempt = 0; attempt < racing_attempts; ++attempt) {
                deadline.check();
                const auto result = attempt % 3 == 0
                    ? push_sequence(inbox, sequence, fixture_epoch, producer_measured)
                    : push(inbox, attempt % 3 == 1 ? std::span<const std::uint8_t>{}
                                                  : std::span<const std::uint8_t>{oversized},
                           0, producer_measured);
                CHECK(result == MidiPushResult::Faulted || result == (attempt % 3 == 0
                    ? MidiPushResult::Accepted : MidiPushResult::InvalidSize));
                if (result == MidiPushResult::Accepted) ++sequence;
                ledger.pushed(result);
            }
            await(deadline, [&] { return reporters_done.load(std::memory_order_acquire) == 2; });
            for (std::size_t attempt = 0; attempt < acknowledged_fault_attempts; ++attempt) {
                const auto result = attempt % 3 == 0
                    ? push_sequence(inbox, sequence, fixture_epoch, producer_measured)
                    : push(inbox, attempt % 3 == 1 ? std::span<const std::uint8_t>{}
                                                  : std::span<const std::uint8_t>{oversized},
                           0, producer_measured);
                CHECK(result == MidiPushResult::Faulted);
                ledger.pushed(result);
            }
        });
        std::thread consumer([&] {
            test_probe_overloads();
            await(deadline, [&] { return start.load(std::memory_order_acquire); });
            std::size_t sequence = 0;
            while (sequence < fault_prefix) {
                deadline.check();
                auto destination = sentinel;
                if (pop(inbox, destination, consumer_measured)) {
                    check_sequence(input, destination, sequence, fixture_epoch, oracle, consumer_measured);
                    consumed.store(++sequence, std::memory_order_release);
                } else {
                    same_packet(destination, sentinel);
                    std::this_thread::yield();
                }
                CHECK(inbox.pending() <= kMidiInboxCapacity);
            }
            race_ready.fetch_add(1, std::memory_order_acq_rel);
            await(deadline, [&] { return race.load(std::memory_order_acquire); });
            auto destination = sentinel;
            if (pop(inbox, destination, consumer_measured)) {
                // One pop may have passed its fault check before publication.
                check_sequence(input, destination, sequence, fixture_epoch, oracle, consumer_measured);
                consumed.store(++sequence, std::memory_order_release);
            } else {
                same_packet(destination, sentinel);
            }
            await(deadline, [&] { return reporters_done.load(std::memory_order_acquire) == 2; });
            CHECK(inbox.faults() == 6);
            for (std::size_t attempt = 0; attempt < 32; ++attempt) no_pop(inbox, consumer_measured);
        });
        std::thread backend([&] {
            test_probe_overloads();
            await(deadline, [&] {
                return produced.load(std::memory_order_acquire) == fault_prefix + parked_tail &&
                       race_ready.load(std::memory_order_acquire) == 3;
            });
            race.store(true, std::memory_order_release);
            for (std::size_t repeat = 0; repeat < 64; ++repeat) {
                signal(inbox, MidiInboxFault::Backend, backend_measured);
            }
            reporters_done.fetch_add(1, std::memory_order_acq_rel);
        });
        std::thread disconnected([&] {
            test_probe_overloads();
            race_ready.fetch_add(1, std::memory_order_acq_rel);
            await(deadline, [&] { return race.load(std::memory_order_acquire); });
            for (std::size_t repeat = 0; repeat < 64; ++repeat) {
                signal(inbox, MidiInboxFault::Disconnected, disconnect_measured);
            }
            reporters_done.fetch_add(1, std::memory_order_acq_rel);
        });
        start.store(true, std::memory_order_release);
        producer.join();
        consumer.join();
        backend.join();
        disconnected.join();
        ledger.expected.popped_packets += consumed.load(std::memory_order_acquire);
        ledger.expected.faults = 6;
        CHECK(consumed.load(std::memory_order_acquire) >= fault_prefix);
        CHECK(consumed.load(std::memory_order_acquire) <= fault_prefix + 1);
        CHECK(inbox.pending() >= parked_tail - 1);
        CHECK(inbox.pending() <= parked_tail + racing_attempts);
        CHECK(ledger.expected.overflow_events == 0);
        check_inbox_counters(inbox, ledger);
        check_decoder_counters(input, oracle);
        input.end_epoch();
        oracle.end();
        // All four threads are joined before the old epoch is discarded.
        reset_joined(inbox, ledger);
        no_pop(inbox, consumer_measured);

        // A distinct next epoch must expose only its own payloads, including
        // short messages whose reused slots previously held three bytes. Its
        // lower initial timestamp must not inherit the retired epoch's history.
        CHECK(input.begin_epoch());
        oracle.begin();
        for (std::size_t sequence = 0; sequence < 32; ++sequence) {
            const auto result = push_sequence(inbox, sequence, 1 + epoch, producer_measured);
            CHECK(result == MidiPushResult::Accepted);
            ledger.pushed(result);
        }
        for (std::size_t sequence = 0; sequence < 32; ++sequence) {
            MidiPacket destination = sentinel;
            CHECK(pop(inbox, destination, consumer_measured));
            check_sequence(input, destination, sequence, 1 + epoch, oracle, consumer_measured);
            ++ledger.expected.popped_packets;
        }
        no_pop(inbox, consumer_measured);
        check_inbox_counters(inbox, ledger);
        check_decoder_counters(input, oracle);
        input.end_epoch();
        oracle.end();
        reset_joined(inbox, ledger);
        total.add(producer_measured);
        total.add(consumer_measured);
        total.add(backend_measured);
        total.add(disconnect_measured);
    }
}

void explicit_overflow_and_rejections(Measurements& measured) {
    MidiInbox inbox;
    Ledger ledger;
    const std::array<std::uint8_t, 4> oversized{0xF0, 1, 2, 0xF7};
    no_pop(inbox, measured);
    for (std::size_t sequence = 0; sequence < 256; ++sequence) {
        const auto result = push_sequence(inbox, sequence, 2000, measured);
        CHECK(result == MidiPushResult::Accepted);
        ledger.pushed(result);
    }
    CHECK(inbox.pending() == 256);
    for (const auto bytes : {std::span<const std::uint8_t>{},
                             std::span<const std::uint8_t>{oversized}}) {
        const auto result = push(inbox, bytes, 0, measured);
        CHECK(result == MidiPushResult::InvalidSize);
        ledger.pushed(result);
    }
    const auto overflow = push_sequence(inbox, 256, 2000, measured);
    CHECK(overflow == MidiPushResult::Overflow);
    ledger.pushed(overflow);
    ledger.expected.faults = 1;
    for (std::size_t attempt = 0; attempt < 24; ++attempt) {
        const auto result = attempt % 3 == 0 ? push_sequence(inbox, 256, 2000, measured)
            : push(inbox, attempt % 3 == 1 ? std::span<const std::uint8_t>{}
                                           : std::span<const std::uint8_t>{oversized}, 0, measured);
        CHECK(result == MidiPushResult::Faulted);
        ledger.pushed(result);
        no_pop(inbox, measured);
    }
    signal(inbox, MidiInboxFault::Backend, measured);
    signal(inbox, MidiInboxFault::Disconnected, measured);
    ledger.expected.faults = 7;
    check_inbox_counters(inbox, ledger);
    reset_joined(inbox, ledger);
    CHECK(ledger.expected.discarded_packets == 256);
    no_pop(inbox, measured);
    reset_joined(inbox, ledger);

    MidiInput input;
    DecoderOracle oracle;
    const auto valid = packet_at(0, 0);
    (void)check_decode(input, valid, MidiDecodeStatus::Inactive, oracle, measured);
    CHECK(input.begin_epoch());
    oracle.begin();
    constexpr std::array<std::uint8_t, 3> malformed_sizes{0, 4, 255};
    for (const auto size : malformed_sizes) {
        auto malformed = valid;
        malformed.size = size;
        (void)check_decode(input, malformed, MidiDecodeStatus::Malformed, oracle, measured);
    }
    for (std::size_t sequence = 0; sequence < 32; ++sequence) {
        const auto result = push_sequence(inbox, sequence, 3000, measured);
        CHECK(result == MidiPushResult::Accepted);
        ledger.pushed(result);
        MidiPacket destination = sentinel;
        CHECK(pop(inbox, destination, measured));
        check_sequence(input, destination, sequence, 3000, oracle, measured);
        ++ledger.expected.popped_packets;
    }
    input.end_epoch();
    oracle.end();
    (void)check_decode(input, valid, MidiDecodeStatus::Inactive, oracle, measured);
    check_decoder_counters(input, oracle);
    no_pop(inbox, measured);
    check_inbox_counters(inbox, ledger);
}

} // namespace

int main() {
    test_probe_overloads();
    Measurements measured;
    lossless_wraps(measured);
    concurrent_fault_retirement(measured);
    explicit_overflow_and_rejections(measured);
    CHECK(!allocation_probe::recording);
    std::printf("Standalone MIDI concurrency: %zu FIFO transfers across %zu epochs; "
                "%zu joined fault races; explicit capacity overflow passed.\n",
                lossless_epochs * transfer_count, lossless_epochs, fault_epochs);
    std::printf("Observed %llu pushes, %llu pops, %llu decodes, %llu fault signals: "
                "zero C++ allocations/deallocations in every measured operation.\n",
                static_cast<unsigned long long>(measured.pushes),
                static_cast<unsigned long long>(measured.pops),
                static_cast<unsigned long long>(measured.decodes),
                static_cast<unsigned long long>(measured.faults));
    std::puts("Calibration separately observed all 12 C++ allocation and deallocation overload paths "
              "on the main thread and each worker; no physical/backend/timing qualification implied.");
}
