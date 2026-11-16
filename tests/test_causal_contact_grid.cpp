#include "TestSupport.h"
#include "hammond/research/CausalContactGrid.h"

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <limits>
#include <memory>
#include <span>
#include <vector>

namespace {

using namespace hammond::research;
using Edges = std::vector<ContactGridEdge>;
constexpr std::array<std::uint32_t, 3> kRates{44100, 48000, 96000};
constexpr std::uint32_t kFrame = 65536;
constexpr std::uint32_t kEnd = 268435456;
constexpr std::uint32_t kSpeed = 4294967295U;
constexpr std::uint64_t kTravel = 281474976710656ULL;

static_assert(kContactGridTicksPerFrame == kFrame);
static_assert(kContactGridFullTravel == kTravel);
static_assert(kContactGridMaxFrames == 4096);
static_assert(kContactGridMaxKeys == 4);
static_assert(kContactGridContactsPerKey == 9);
static_assert(kContactGridMaxCommands == 512);
static_assert(kContactGridMaxEdges == 4608);

// These fixtures were derived from the frozen contract/admission, before reading
// the candidate implementation. There is deliberately no crossing/position solver
// here: small cases have explicit rational answers; the capacity case has the
// independently admitted arithmetic progression.
constexpr ContactGridEdge edge(std::uint32_t tick, std::uint32_t numerator,
                               std::uint32_t denominator, std::uint32_t key,
                               std::uint32_t contact, bool closed) {
    return {{tick, numerator, denominator}, key, contact, closed};
}

ContactGridConfig uniform_config(std::uint32_t rate, std::uint32_t keys,
                                 std::uint32_t press, std::uint32_t release,
                                 std::uint64_t off, std::uint64_t on) {
    ContactGridConfig config{};
    config.sampleRateHz = rate;
    config.keyCount = keys;
    for (std::uint32_t key = 0; key < keys; ++key) {
        config.keys[key].pressUnitsPerTick = press;
        config.keys[key].releaseUnitsPerTick = release;
        config.keys[key].contacts.fill({off, on});
    }
    return config;
}

ContactGridSnapshot initial_snapshot(const ContactGridConfig& config) {
    ContactGridSnapshot state{};
    state.phase = ContactGridPhase::ready;
    state.config = config;
    return state;
}

void check_config(const ContactGridConfig& actual,
                  const ContactGridConfig& expected) {
    CHECK(actual.sampleRateHz == expected.sampleRateHz);
    CHECK(actual.keyCount == expected.keyCount);
    for (std::size_t key = 0; key < 4; ++key) {
        CHECK(actual.keys[key].pressUnitsPerTick == expected.keys[key].pressUnitsPerTick);
        CHECK(actual.keys[key].releaseUnitsPerTick == expected.keys[key].releaseUnitsPerTick);
        for (std::size_t contact = 0; contact < 9; ++contact) {
            CHECK(actual.keys[key].contacts[contact].off ==
                  expected.keys[key].contacts[contact].off);
            CHECK(actual.keys[key].contacts[contact].on ==
                  expected.keys[key].contacts[contact].on);
        }
    }
}

void check_snapshot(const ContactGridSnapshot& actual,
                    const ContactGridSnapshot& expected) {
    CHECK(actual.phase == expected.phase);
    check_config(actual.config, expected.config);
    CHECK(actual.cursorFrames == expected.cursorFrames);
    CHECK(actual.commandCount == expected.commandCount);
    CHECK(actual.edgeCount == expected.edgeCount);
    for (std::size_t key = 0; key < 4; ++key) {
        CHECK(actual.keys[key].position == expected.keys[key].position);
        CHECK(actual.keys[key].target == expected.keys[key].target);
        CHECK(actual.keys[key].anchorPosition == expected.keys[key].anchorPosition);
        CHECK(actual.keys[key].anchorTick == expected.keys[key].anchorTick);
        CHECK(actual.keys[key].closed == expected.keys[key].closed);
    }
}

void check_edges(std::span<const ContactGridEdge> actual,
                 std::span<const ContactGridEdge> expected) {
    CHECK(actual.size() == expected.size());
    for (std::size_t index = 0; index < actual.size(); ++index) {
        const auto& a = actual[index];
        const auto& e = expected[index];
        if (a.time.tick != e.time.tick || a.time.numerator != e.time.numerator ||
            a.time.denominator != e.time.denominator || a.keyIndex != e.keyIndex ||
            a.contactIndex != e.contactIndex || a.closedAfter != e.closedAfter) {
            std::cerr << "edge " << index << ": actual " << a.time.tick << '+'
                      << a.time.numerator << '/' << a.time.denominator << " key "
                      << a.keyIndex << " contact " << a.contactIndex << " closed "
                      << a.closedAfter << "; expected " << e.time.tick << '+'
                      << e.time.numerator << '/' << e.time.denominator << " key "
                      << e.keyIndex << " contact " << e.contactIndex << " closed "
                      << e.closedAfter << '\n';
            CHECK(false);
        }
    }
}

void append_nine(Edges& edges, ContactGridTime time, std::uint32_t key, bool closed) {
    for (std::uint32_t contact = 0; contact < 9; ++contact) {
        edges.push_back({time, key, contact, closed});
    }
}

void check_ok(const ContactGridResult& result, std::uint32_t expectedEdges) {
    CHECK(result.status == ContactGridStatus::ok);
    CHECK(result.edgesWritten == expectedEdges);
    CHECK(result.requiredEdges == expectedEdges);
}

struct Replay {
    Edges edges;
    ContactGridSnapshot beforeClose;
    ContactGridSnapshot afterClose;
};

Replay replay(const ContactGridConfig& config, std::uint32_t totalFrames,
              std::span<const ContactGridTarget> commands,
              std::span<const ContactGridTarget> endpointCommands,
              std::span<const std::uint32_t> blocks, bool insertEmptyCalls = false) {
    // Test setup may allocate. Keep large objects/buffers off the Windows stack;
    // callback allocation instrumentation belongs to the separate resource test.
    auto grid = std::make_unique<CausalContactGrid>();
    Edges output(kContactGridMaxEdges);
    Replay result{};
    CHECK(grid->prepare(config) == ContactGridStatus::ok);
    CHECK(!blocks.empty());
    std::uint32_t cursor = 0;
    std::size_t nextCommand = 0;
    std::size_t blockIndex = 0;
    while (cursor < totalFrames) {
        const auto count = std::min(blocks[blockIndex % blocks.size()], totalFrames - cursor);
        CHECK(count > 0);
        const auto endTick = (cursor + count) * kFrame;
        const auto firstCommand = nextCommand;
        while (nextCommand < commands.size() && commands[nextCommand].tick < endTick) {
            CHECK(commands[nextCommand].tick >= cursor * kFrame);
            ++nextCommand;
        }
        if (insertEmptyCalls) {
            const auto before = grid->snapshot();
            check_ok(grid->process(0, {}, {}), 0);
            check_snapshot(grid->snapshot(), before);
        }
        const auto call = grid->process(count,
            commands.subspan(firstCommand, nextCommand - firstCommand), output);
        CHECK(call.status == ContactGridStatus::ok);
        CHECK(call.edgesWritten == call.requiredEdges);
        CHECK(call.edgesWritten <= output.size());
        result.edges.insert(result.edges.end(), output.begin(),
                            output.begin() + call.edgesWritten);
        cursor += count;
        ++blockIndex;
    }
    CHECK(nextCommand == commands.size());
    result.beforeClose = grid->snapshot();
    CHECK(grid->close_observation(endpointCommands) == ContactGridStatus::ok);
    result.afterClose = grid->snapshot();
    return result;
}

void check_partitions(const ContactGridConfig& config, std::uint32_t frames,
                      std::span<const ContactGridTarget> commands,
                      std::span<const ContactGridTarget> endpointCommands,
                      std::span<const ContactGridEdge> expectedEdges,
                      const ContactGridSnapshot& beforeClose,
                      const ContactGridSnapshot& afterClose) {
    const std::array wholeBlocks{frames};
    const std::array singleBlocks{1U};
    const std::array irregularBlocks{3U, 17U, 1U, 255U, 2U, 1024U, 37U, 511U, 5U};
    const auto whole = replay(config, frames, commands, endpointCommands, wholeBlocks);
    const auto single = replay(config, frames, commands, endpointCommands, singleBlocks, true);
    const auto irregular = replay(config, frames, commands, endpointCommands,
                                  irregularBlocks, true);
    for (const auto* run : {&whole, &single, &irregular}) {
        check_edges(run->edges, expectedEdges);
        check_snapshot(run->beforeClose, beforeClose);
        check_snapshot(run->afterClose, afterClose);
        check_edges(run->edges, whole.edges);
        check_snapshot(run->beforeClose, whole.beforeClose);
        check_snapshot(run->afterClose, whole.afterClose);
    }
}

void canonical_configuration_and_zero_frame_epoch() {
    auto grid = std::make_unique<CausalContactGrid>();
    check_snapshot(grid->snapshot(), ContactGridSnapshot{});
    CHECK(grid->reset() == ContactGridStatus::invalid_state);
    const auto clean = uniform_config(48000, 1, 3, 7, 10, 20);
    auto supplied = clean;
    for (std::size_t key = 1; key < 4; ++key) {
        supplied.keys[key].pressUnitsPerTick = 0;
        supplied.keys[key].releaseUnitsPerTick = kSpeed;
        supplied.keys[key].contacts.fill({std::numeric_limits<std::uint64_t>::max(), 0});
    }
    CHECK(grid->prepare(supplied) == ContactGridStatus::ok);
    const auto initial = initial_snapshot(clean);
    check_snapshot(grid->snapshot(), initial);
    // Caller configuration is copied, including all active contact identities.
    supplied.keys[0].pressUnitsPerTick = 0;
    supplied.keys[0].contacts[0] = {99, 0};
    check_snapshot(grid->snapshot(), initial);
    CHECK(grid->reset() == ContactGridStatus::invalid_state);
    check_ok(grid->process(0, {}, {}), 0);
    check_snapshot(grid->snapshot(), initial);

    const std::array closing{
        ContactGridTarget{0, 0, 17}, ContactGridTarget{0, 0, 17},
        ContactGridTarget{0, 0, 0}, ContactGridTarget{0, 0, 20}};
    CHECK(grid->close_observation(closing) == ContactGridStatus::ok);
    auto closed = initial;
    closed.phase = ContactGridPhase::closed;
    closed.commandCount = 4;
    closed.keys[0].target = 20;
    check_snapshot(grid->snapshot(), closed);
    // N=0 closure never travels, even when the final target equals an on level.
    CHECK(grid->process(0, {}, {}).status == ContactGridStatus::invalid_state);
    CHECK(grid->reset() == ContactGridStatus::ok);
    check_snapshot(grid->snapshot(), initial);

    const auto replacement = uniform_config(96000, 2, 5, 11, 0, 1);
    CHECK(grid->prepare(replacement) == ContactGridStatus::ok); // Ready reprepare.
    check_snapshot(grid->snapshot(), initial_snapshot(replacement));
    CHECK(grid->close_observation({}) == ContactGridStatus::ok);
    CHECK(grid->prepare(clean) == ContactGridStatus::ok); // Closed reprepare.
    check_snapshot(grid->snapshot(), initial);
    CHECK(kCausalContactGridModelId == "causal-contact-grid-v1");
}

void unsorted_repeated_contacts_and_fractional_arrivals() {
    const std::array commands{ContactGridTarget{0, 0, 20}, ContactGridTarget{5, 0, 0}};
    const std::array expected{
        edge(0, 1, 3, 0, 7, true), edge(0, 2, 3, 0, 5, true),
        edge(1, 0, 1, 0, 1, true), edge(1, 2, 3, 0, 0, true),
        edge(1, 2, 3, 0, 2, true), edge(1, 5, 6, 0, 6, true),
        edge(2, 0, 1, 0, 3, true), edge(3, 0, 1, 0, 4, true),
        edge(3, 1, 3, 0, 8, true), // Fractional arrival at target 20.
        edge(7, 0, 1, 0, 8, false), edge(7, 1, 4, 0, 4, false),
        edge(7, 1, 2, 0, 6, false), edge(8, 1, 4, 0, 3, false),
        edge(9, 0, 1, 0, 0, false), edge(9, 0, 1, 0, 2, false),
        edge(9, 1, 4, 0, 5, false), edge(9, 3, 4, 0, 7, false),
        edge(10, 0, 1, 0, 1, false)}; // Exact arrival at zero/off.
    for (const auto rate : kRates) {
        auto config = uniform_config(rate, 1, 6, 4, 0, 1);
        config.keys[0].contacts = {{{4, 10}, {0, 6}, {4, 10}, {7, 12},
                                    {11, 18}, {3, 4}, {10, 11}, {1, 2}, {12, 20}}};
        auto before = initial_snapshot(config);
        before.phase = ContactGridPhase::active;
        before.cursorFrames = 9;
        before.commandCount = 2;
        before.edgeCount = 18;
        before.keys[0].anchorPosition = 20;
        before.keys[0].anchorTick = 5;
        auto after = before;
        after.phase = ContactGridPhase::closed;
        check_partitions(config, 9, commands, {}, expected, before, after);
    }
}

void incoming_ties_are_ordered_by_key_and_contact() {
    for (const auto rate : kRates) {
        auto config = uniform_config(rate, 3, 3, 3, 3, 6);
        config.keys[2].pressUnitsPerTick = 6;
        config.keys[2].releaseUnitsPerTick = 6;
        config.keys[2].contacts.fill({6, 12});
        // Command order is deliberately unrelated to edge identity order.
        const std::array commands{
            ContactGridTarget{0, 2, 12}, ContactGridTarget{0, 1, 6},
            ContactGridTarget{0, 0, 6}, ContactGridTarget{2, 2, 0},
            ContactGridTarget{2, 0, 0}, ContactGridTarget{2, 1, 0}};
        Edges expected;
        for (std::uint32_t key = 0; key < 3; ++key) {
            append_nine(expected, {2, 0, 1}, key, true);
        }
        for (std::uint32_t key = 0; key < 3; ++key) {
            append_nine(expected, {3, 0, 1}, key, false);
        }
        auto before = initial_snapshot(config);
        before.phase = ContactGridPhase::active;
        before.cursorFrames = 7;
        before.commandCount = 6;
        before.edgeCount = 54;
        for (std::uint32_t key = 0; key < 3; ++key) {
            before.keys[key].anchorPosition = key == 2 ? 12 : 6;
            before.keys[key].anchorTick = 2;
        }
        auto after = before;
        after.phase = ContactGridPhase::closed;
        check_partitions(config, 7, commands, {}, expected, before, after);
    }
}

void no_op_and_ordered_tied_target_anchors() {
    const auto config = uniform_config(48000, 1, 1, 1, 25, 50);
    const std::array blocks{1U};
    const std::array noops{
        ContactGridTarget{0, 0, 100}, ContactGridTarget{3, 0, 100},
        ContactGridTarget{100, 0, 100}, ContactGridTarget{200, 0, 100}};
    const std::array changedBack{
        ContactGridTarget{0, 0, 100}, ContactGridTarget{3, 0, 100},
        ContactGridTarget{3, 0, 0}, ContactGridTarget{3, 0, 100}};
    const std::array reversedOrder{
        ContactGridTarget{0, 0, 100}, ContactGridTarget{3, 0, 100},
        ContactGridTarget{3, 0, 100}, ContactGridTarget{3, 0, 0}};
    Edges expectedEdges;
    append_nine(expectedEdges, {50, 0, 1}, 0, true);
    auto expected = initial_snapshot(config);
    expected.phase = ContactGridPhase::closed;
    expected.cursorFrames = 1;
    expected.commandCount = 4;
    expected.edgeCount = 9;
    expected.keys[0].position = 100;
    expected.keys[0].target = 100;
    expected.keys[0].closed.fill(true);
    const auto retained = replay(config, 1, noops, {}, blocks);
    check_edges(retained.edges, expectedEdges);
    check_snapshot(retained.afterClose, expected);
    const auto reanchored = replay(config, 1, changedBack, {}, blocks);
    expected.keys[0].anchorTick = 3;
    expected.keys[0].anchorPosition = 3;
    check_edges(reanchored.edges, expectedEdges);
    check_snapshot(reanchored.afterClose, expected);
    const auto reversed = replay(config, 1, reversedOrder, {}, blocks);
    expected.keys[0].position = 0;
    expected.keys[0].target = 0;
    expected.keys[0].closed.fill(false);
    expected.edgeCount = 0;
    check_edges(reversed.edges, {});
    check_snapshot(reversed.afterClose, expected);
}

void hysteresis_holds_and_closure_without_release() {
    auto grid = std::make_unique<CausalContactGrid>();
    const auto config = uniform_config(44100, 2, 1, 1, 3, 7);
    CHECK(grid->prepare(config) == ContactGridStatus::ok);
    const std::array commands{
        ContactGridTarget{0, 0, 5}, ContactGridTarget{0, 1, 9},
        ContactGridTarget{10, 1, 5}};
    Edges output(18);
    check_ok(grid->process(1, commands, output), 9);
    Edges firstEdges;
    append_nine(firstEdges, {7, 0, 1}, 1, true);
    check_edges(std::span<const ContactGridEdge>(output).first(9), firstEdges);
    auto held = initial_snapshot(config);
    held.phase = ContactGridPhase::active;
    held.cursorFrames = 1;
    held.commandCount = 3;
    held.edgeCount = 9;
    held.keys[0].position = held.keys[0].target = 5;
    held.keys[1].position = held.keys[1].target = 5;
    held.keys[1].anchorTick = 10;
    held.keys[1].anchorPosition = 9;
    held.keys[1].closed.fill(true);
    check_snapshot(grid->snapshot(), held); // Same position, opposite contact histories.
    check_ok(grid->process(3, {}, {}), 0);
    held.cursorFrames = 4;
    check_snapshot(grid->snapshot(), held); // A hold preserves bits and original anchors.
    const std::array equalityTargets{
        ContactGridTarget{4 * kFrame, 1, 3}, ContactGridTarget{4 * kFrame, 0, 7}};
    check_ok(grid->process(1, equalityTargets, output), 18);
    Edges equalityEdges;
    append_nine(equalityEdges, {4 * kFrame + 2, 0, 1}, 0, true);
    append_nine(equalityEdges, {4 * kFrame + 2, 0, 1}, 1, false);
    check_edges(output, equalityEdges);
    held.cursorFrames = 5;
    held.commandCount = 5;
    held.edgeCount = 27;
    for (std::uint32_t key = 0; key < 2; ++key) {
        held.keys[key].position = held.keys[key].target = key == 0 ? 7 : 3;
        held.keys[key].anchorPosition = 5;
        held.keys[key].anchorTick = 4 * kFrame;
        held.keys[key].closed.fill(key == 0);
    }
    check_snapshot(grid->snapshot(), held);
    const std::array closeTargets{
        ContactGridTarget{5 * kFrame, 1, 0}, ContactGridTarget{5 * kFrame, 0, 0}};
    CHECK(grid->close_observation(closeTargets) == ContactGridStatus::ok);
    held.phase = ContactGridPhase::closed;
    held.commandCount = 7;
    for (std::uint32_t key = 0; key < 2; ++key) {
        held.keys[key].target = 0;
        held.keys[key].anchorPosition = key == 0 ? 7 : 3;
        held.keys[key].anchorTick = 5 * kFrame;
    }
    check_snapshot(grid->snapshot(), held); // Closing is not a release trajectory.
    CHECK(grid->reset() == ContactGridStatus::ok);
    check_snapshot(grid->snapshot(), initial_snapshot(config));
}

void frame_endpoint_equality_and_future_causality() {
    const std::array commands{
        ContactGridTarget{0, 0, 2 * kFrame}, ContactGridTarget{kFrame, 0, 0}};
    Edges expectedEdges;
    append_nine(expectedEdges, {kFrame, 0, 1}, 0, true);
    append_nine(expectedEdges, {98304, 0, 1}, 0, false);
    for (const auto rate : kRates) {
        const auto config = uniform_config(rate, 1, 1, 1, 32768, 65536);
        auto before = initial_snapshot(config);
        before.phase = ContactGridPhase::active;
        before.cursorFrames = 9;
        before.commandCount = 2;
        before.edgeCount = 18;
        before.keys[0].anchorTick = kFrame;
        before.keys[0].anchorPosition = kFrame;
        auto after = before;
        after.phase = ContactGridPhase::closed;
        check_partitions(config, 9, commands, {}, expectedEdges, before, after);

        auto prefix = std::make_unique<CausalContactGrid>();
        CHECK(prefix->prepare(config) == ContactGridStatus::ok);
        Edges prefixOutput(9);
        check_ok(prefix->process(1, std::span(commands).first(1), prefixOutput), 9);
        check_edges(prefixOutput, std::span(expectedEdges).first(9));
        auto atBoundary = initial_snapshot(config);
        atBoundary.phase = ContactGridPhase::active;
        atBoundary.cursorFrames = 1;
        atBoundary.commandCount = 1;
        atBoundary.edgeCount = 9;
        atBoundary.keys[0].position = kFrame;
        atBoundary.keys[0].target = 2 * kFrame;
        atBoundary.keys[0].closed.fill(true);
        check_snapshot(prefix->snapshot(), atBoundary);
        // The incoming endpoint edge is already observable before any command
        // at that time. Closing with a reversal cannot erase it or move the key.
        CHECK(prefix->close_observation(std::span(commands).last(1)) == ContactGridStatus::ok);
        atBoundary.phase = ContactGridPhase::closed;
        atBoundary.commandCount = 2;
        atBoundary.keys[0].target = 0;
        atBoundary.keys[0].anchorTick = kFrame;
        atBoundary.keys[0].anchorPosition = kFrame;
        check_snapshot(prefix->snapshot(), atBoundary);

        // An alternative future retains the same incoming edge, with no break.
        const std::array holdFuture{
            ContactGridTarget{0, 0, 2 * kFrame},
            ContactGridTarget{kFrame, 0, 2 * kFrame}};
        const std::array blocks{9U};
        const auto held = replay(config, 9, holdFuture, {}, blocks);
        check_edges(held.edges, std::span(expectedEdges).first(9));
        auto heldExpected = initial_snapshot(config);
        heldExpected.phase = ContactGridPhase::closed;
        heldExpected.cursorFrames = 9;
        heldExpected.commandCount = 2;
        heldExpected.edgeCount = 9;
        heldExpected.keys[0].position = heldExpected.keys[0].target = 2 * kFrame;
        heldExpected.keys[0].closed.fill(true);
        check_snapshot(held.afterClose, heldExpected);

        // The largest representable epoch endpoint is owned exactly once and
        // must retain the canonical integer fraction 0/1.
        const auto endConfig = uniform_config(rate, 1, 1, 1, kEnd - 1, kEnd);
        const std::array endCommand{ContactGridTarget{0, 0, kEnd}};
        const std::array endClose{ContactGridTarget{kEnd, 0, 0}};
        Edges endEdges;
        append_nine(endEdges, {kEnd, 0, 1}, 0, true);
        auto endBefore = initial_snapshot(endConfig);
        endBefore.phase = ContactGridPhase::active;
        endBefore.cursorFrames = 4096;
        endBefore.commandCount = 1;
        endBefore.edgeCount = 9;
        endBefore.keys[0].position = endBefore.keys[0].target = kEnd;
        endBefore.keys[0].closed.fill(true);
        auto endAfter = endBefore;
        endAfter.phase = ContactGridPhase::closed;
        endAfter.commandCount = 2;
        endAfter.keys[0].target = 0;
        endAfter.keys[0].anchorTick = kEnd;
        endAfter.keys[0].anchorPosition = kEnd;
        check_partitions(endConfig, 4096, endCommand, endClose,
                         endEdges, endBefore, endAfter);
    }
}

void distant_speed_one_roots_are_not_narrowed() {
    constexpr std::uint64_t distant = 4294967297ULL;
    for (const auto rate : kRates) {
        auto config = uniform_config(rate, 2, 1, 1, distant - 1, distant);
        config.keys[1].contacts.fill({kTravel - 1, kTravel});
        auto grid = std::make_unique<CausalContactGrid>();
        CHECK(grid->prepare(config) == ContactGridStatus::ok);
        const std::array commands{
            ContactGridTarget{0, 0, distant}, ContactGridTarget{0, 1, kTravel}};
        // Actual E is zero: no conservative output-capacity demand is permitted.
        check_ok(grid->process(1, commands, {}), 0);
        auto expected = initial_snapshot(config);
        expected.phase = ContactGridPhase::active;
        expected.cursorFrames = 1;
        expected.commandCount = 2;
        expected.keys[0].position = expected.keys[1].position = kFrame;
        expected.keys[0].target = distant;
        expected.keys[1].target = kTravel;
        check_snapshot(grid->snapshot(), expected);
        check_ok(grid->process(4095, {}, {}), 0);
        expected.cursorFrames = 4096;
        expected.keys[0].position = expected.keys[1].position = kEnd;
        check_snapshot(grid->snapshot(), expected);
        CHECK(grid->close_observation({}) == ContactGridStatus::ok);
        expected.phase = ContactGridPhase::closed;
        check_snapshot(grid->snapshot(), expected);
    }
}

void full_travel_maximum_speed_and_long_epoch_partitions() {
    const std::array commands{
        ContactGridTarget{0, 0, kTravel}, ContactGridTarget{2 * kFrame, 0, 0}};
    const std::array closing{ContactGridTarget{kEnd, 0, kTravel}};
    Edges expected{
        edge(0, 1, kSpeed, 0, 3, true), edge(1, 0, 1, 0, 2, true),
        edge(32768, 32768, kSpeed, 0, 7, true), edge(65535, 0, 1, 0, 6, true),
        edge(65536, 0, 1, 0, 1, true), edge(65536, 1, kSpeed, 0, 5, true),
        edge(65536, 1, 65537, 0, 4, true),
        edge(65536, 65536, kSpeed, 0, 0, true),
        edge(65536, 65536, kSpeed, 0, 8, true)};
    append_nine(expected, {196608, 65536, kSpeed}, 0, false);
    for (const auto rate : kRates) {
        auto config = uniform_config(rate, 1, kSpeed, kSpeed, 0, kTravel);
        config.keys[0].contacts[1].on = kTravel - 65536;
        config.keys[0].contacts[2].on = kSpeed;
        config.keys[0].contacts[3].on = 1;
        config.keys[0].contacts[4].on = kTravel - 1;
        config.keys[0].contacts[5].on = kTravel - 65535;
        config.keys[0].contacts[6].on = std::uint64_t{kSpeed} * 65535;
        config.keys[0].contacts[7].on = kTravel / 2;
        auto before = initial_snapshot(config);
        before.phase = ContactGridPhase::active;
        before.cursorFrames = 4096;
        before.commandCount = 2;
        before.edgeCount = 18;
        before.keys[0].anchorTick = 2 * kFrame;
        before.keys[0].anchorPosition = kTravel;
        auto after = before;
        after.phase = ContactGridPhase::closed;
        after.commandCount = 3;
        after.keys[0].target = kTravel;
        after.keys[0].anchorTick = kEnd;
        after.keys[0].anchorPosition = 0;
        check_partitions(config, 4096, commands, closing, expected, before, after);
    }
}

void exact_close_roots_and_unsigned_fraction_products() {
    constexpr std::uint32_t anchor = 200000000;
    constexpr std::uint32_t almostHalf = 2147483645;
    constexpr std::uint64_t largeProduct = std::uint64_t{kSpeed - 1} * (kSpeed - 1);
    constexpr std::uint64_t smallProduct = std::uint64_t{almostHalf} * kSpeed;
    static_assert(largeProduct > std::uint64_t{std::numeric_limits<std::int64_t>::max()});
    static_assert(smallProduct < std::uint64_t{std::numeric_limits<std::int64_t>::max()});
    // This only verifies the fixture's display collision. No expected ordering
    // is derived using floating point or a candidate comparison helper.
    CHECK(double(anchor) + 1.0 / double(kSpeed) ==
          double(anchor) + 1.0 / double(kSpeed - 1));
    const std::array commands{
        ContactGridTarget{anchor, 0, kSpeed - 1},
        ContactGridTarget{anchor, 1, almostHalf},
        ContactGridTarget{anchor, 2, 1}, ContactGridTarget{anchor, 3, 1}};
    const std::array closing{
        ContactGridTarget{kEnd, 3, 0}, ContactGridTarget{kEnd, 1, 0},
        ContactGridTarget{kEnd, 0, 0}, ContactGridTarget{kEnd, 2, 0}};
    Edges expected;
    append_nine(expected, {anchor, 1, kSpeed}, 3, true);
    append_nine(expected, {anchor, 1, kSpeed - 1}, 2, true);
    append_nine(expected, {anchor, almostHalf, kSpeed - 1}, 1, true);
    append_nine(expected, {anchor, kSpeed - 1, kSpeed}, 0, true);
    for (const auto rate : kRates) {
        auto config = uniform_config(rate, 4, kSpeed, 1, 0, 1);
        config.keys[0].contacts.fill({0, kSpeed - 1});
        config.keys[1].pressUnitsPerTick = kSpeed - 1;
        config.keys[1].contacts.fill({0, almostHalf});
        config.keys[2].pressUnitsPerTick = kSpeed - 1;
        auto before = initial_snapshot(config);
        before.phase = ContactGridPhase::active;
        before.cursorFrames = 4096;
        before.commandCount = 4;
        before.edgeCount = 36;
        const std::array<std::uint64_t, 4> positions{kSpeed - 1, almostHalf, 1, 1};
        for (std::size_t key = 0; key < 4; ++key) {
            before.keys[key].position = before.keys[key].target = positions[key];
            before.keys[key].anchorTick = anchor;
            before.keys[key].closed.fill(true);
        }
        auto after = before;
        after.phase = ContactGridPhase::closed;
        after.commandCount = 8;
        for (std::size_t key = 0; key < 4; ++key) {
            after.keys[key].target = 0;
            after.keys[key].anchorTick = kEnd;
            after.keys[key].anchorPosition = positions[key];
        }
        check_partitions(config, 4096, commands, closing, expected, before, after);
    }
}

void maximum_512_commands_and_4608_known_edges() {
    // Admission's attainable maximum: 128 traversals, each producing 36 edges.
    // Flattened contact order opposes time order on every traversal.
    for (const auto rate : kRates) {
        auto config = uniform_config(rate, 4, 1, 1, 1, 100);
        for (std::uint32_t index = 0; index < 36; ++index) {
            config.keys[index / 9].contacts[index % 9] = {1 + index, 100 - index};
        }
        std::vector<ContactGridTarget> commands;
        Edges expected;
        commands.reserve(512);
        expected.reserve(4608);
        for (std::uint32_t movement = 0; movement < 128; ++movement) {
            const bool press = movement % 2 == 0;
            for (std::uint32_t key = 0; key < 4; ++key) {
                commands.push_back({128 * movement, key, press ? 128U : 0U});
            }
            for (std::uint32_t remaining = 36; remaining > 0; --remaining) {
                const auto index = remaining - 1;
                const auto tick = 128 * movement + (press ? 100 - index : 127 - index);
                expected.push_back(edge(tick, 0, 1, index / 9, index % 9, press));
            }
        }
        CHECK(commands.size() == 512);
        CHECK(expected.size() == 4608);
        auto before = initial_snapshot(config);
        before.phase = ContactGridPhase::active;
        before.cursorFrames = 4096;
        before.commandCount = 512;
        before.edgeCount = 4608;
        for (auto& key : before.keys) {
            key.anchorTick = 16256;
            key.anchorPosition = 128;
        }
        auto after = before;
        after.phase = ContactGridPhase::closed;
        check_partitions(config, 4096, commands, {}, expected, before, after);
    }
}

} // namespace

int main() {
    canonical_configuration_and_zero_frame_epoch();
    unsorted_repeated_contacts_and_fractional_arrivals();
    incoming_ties_are_ordered_by_key_and_contact();
    no_op_and_ordered_tied_target_anchors();
    hysteresis_holds_and_closure_without_release();
    frame_endpoint_equality_and_future_causality();
    distant_speed_one_roots_are_not_narrowed();
    full_travel_maximum_speed_and_long_epoch_partitions();
    exact_close_roots_and_unsigned_fraction_products();
    maximum_512_commands_and_4608_known_edges();
    std::cout << "causal contact grid: independent native known-answer checks passed\n";
    return 0;
}
