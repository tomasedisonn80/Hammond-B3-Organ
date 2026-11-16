#include "TestSupport.h"
#include "hammond/research/CausalContactGrid.h"

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <limits>
#include <memory>
#include <span>
#include <type_traits>
#include <vector>

// Independent public-API checks derived from the frozen v1 contract. These do
// not include candidate implementation helpers or the positive-answer suite.
namespace {

using namespace hammond::research;
using Grid = CausalContactGrid;
using Config = ContactGridConfig;
using Target = ContactGridTarget;
using Edge = ContactGridEdge;
using Snapshot = ContactGridSnapshot;
using Phase = ContactGridPhase;
using Status = ContactGridStatus;

constexpr auto ticks = kContactGridTicksPerFrame;
constexpr auto full = kContactGridFullTravel;
constexpr auto u32max = std::numeric_limits<std::uint32_t>::max();
constexpr auto u64max = std::numeric_limits<std::uint64_t>::max();

Config configuration(std::uint32_t keyCount = 1) {
    Config config{};
    config.sampleRateHz = 48000;
    config.keyCount = keyCount;
    for (std::uint32_t key = 0; key < keyCount; ++key) {
        auto& entry = config.keys[key];
        entry.pressUnitsPerTick = 1;
        entry.releaseUnitsPerTick = 1;
        for (std::uint32_t contact = 0; contact < 9; ++contact) {
            entry.contacts[contact] = {50 + 10 * contact, 100 + 10 * contact};
        }
    }
    return config;
}

Config canonical(const Config& source) {
    Config result{};
    result.sampleRateHz = source.sampleRateHz;
    result.keyCount = source.keyCount;
    for (std::uint32_t key = 0; key < source.keyCount; ++key) {
        result.keys[key] = source.keys[key];
    }
    return result;
}

void check_configuration(const Config& actual, const Config& expected) {
    CHECK(actual.sampleRateHz == expected.sampleRateHz);
    CHECK(actual.keyCount == expected.keyCount);
    for (std::size_t key = 0; key < actual.keys.size(); ++key) {
        CHECK(actual.keys[key].pressUnitsPerTick == expected.keys[key].pressUnitsPerTick);
        CHECK(actual.keys[key].releaseUnitsPerTick == expected.keys[key].releaseUnitsPerTick);
        for (std::size_t contact = 0; contact < 9; ++contact) {
            CHECK(actual.keys[key].contacts[contact].off == expected.keys[key].contacts[contact].off);
            CHECK(actual.keys[key].contacts[contact].on == expected.keys[key].contacts[contact].on);
        }
    }
}

void check_snapshot(const Snapshot& actual, const Snapshot& expected) {
    CHECK(actual.phase == expected.phase);
    check_configuration(actual.config, expected.config);
    CHECK(actual.cursorFrames == expected.cursorFrames);
    CHECK(actual.commandCount == expected.commandCount);
    CHECK(actual.edgeCount == expected.edgeCount);
    for (std::size_t key = 0; key < actual.keys.size(); ++key) {
        const auto& a = actual.keys[key];
        const auto& e = expected.keys[key];
        CHECK(a.position == e.position);
        CHECK(a.target == e.target);
        CHECK(a.anchorPosition == e.anchorPosition);
        CHECK(a.anchorTick == e.anchorTick);
        for (std::size_t contact = 0; contact < 9; ++contact) {
            CHECK(a.closed[contact] == e.closed[contact]);
        }
    }
}

void check_clean_epoch(const Grid& grid, const Config& config) {
    Snapshot expected{};
    expected.phase = Phase::ready;
    expected.config = canonical(config);
    check_snapshot(grid.snapshot(), expected);
}

std::unique_ptr<Grid> prepared(const Config& config) {
    auto grid = std::make_unique<Grid>();
    const auto status = grid->prepare(config);
    CHECK(status == Status::ok);
    check_clean_epoch(*grid, config);
    return grid;
}

// Compare semantic snapshot fields above, but the entire caller output object
// representation below. Poison padding too, while leaving bool representations
// valid. The production API may only write the committed prefix on success.
class OutputCanary {
public:
    explicit OutputCanary(std::size_t size = 64, unsigned char pattern = 0xA5)
        : edges_(size), before_(size * sizeof(Edge)) {
        static_assert(std::is_trivially_copyable_v<Edge>);
        auto* bytes = reinterpret_cast<unsigned char*>(edges_.data());
        std::fill_n(bytes, edges_.size() * sizeof(Edge), pattern);
        for (auto& edge : edges_) {
            edge.time.tick = 0x12345678;
            edge.time.numerator = 17;
            edge.time.denominator = 31;
            edge.keyIndex = 0x87654321;
            edge.contactIndex = 0x13579BDF;
            edge.closedAfter = true;
        }
        remember();
    }

    std::span<Edge> span(std::size_t offered) {
        CHECK(offered <= edges_.size());
        return {edges_.data(), offered};
    }

    void remember() {
        std::memcpy(before_.data(), edges_.data(), before_.size());
    }

    void check_tail(std::size_t written) const {
        CHECK(written <= edges_.size());
        const auto offset = written * sizeof(Edge);
        const auto* bytes = reinterpret_cast<const unsigned char*>(edges_.data());
        CHECK(std::memcmp(bytes + offset, before_.data() + offset,
                          before_.size() - offset) == 0);
    }

    void check_prefix(const OutputCanary& other, std::uint32_t count) const {
        CHECK(count <= edges_.size());
        CHECK(count <= other.edges_.size());
        for (std::uint32_t index = 0; index < count; ++index) {
            const auto& a = edges_[index];
            const auto& b = other.edges_[index];
            CHECK(a.time.tick == b.time.tick);
            CHECK(a.time.numerator == b.time.numerator);
            CHECK(a.time.denominator == b.time.denominator);
            CHECK(a.keyIndex == b.keyIndex);
            CHECK(a.contactIndex == b.contactIndex);
            CHECK(a.closedAfter == b.closedAfter);
        }
    }

private:
    std::vector<Edge> edges_;
    std::vector<unsigned char> before_;
};

void rejected_process(Grid& grid, std::uint32_t frames,
                      std::span<const Target> targets, Status status,
                      OutputCanary& output, std::size_t offered = 64,
                      std::uint32_t required = 0) {
    const auto before = grid.snapshot();
    output.remember();
    const auto result = grid.process(frames, targets, output.span(offered));
    CHECK(result.status == status);
    CHECK(result.edgesWritten == 0);
    CHECK(result.requiredEdges == required);
    check_snapshot(grid.snapshot(), before);
    output.check_tail(0);
}

void accepted_process(Grid& grid, std::uint32_t frames,
                      std::span<const Target> targets, OutputCanary& output,
                      std::uint32_t expectedEdges, std::size_t offered = 64) {
    output.remember();
    const auto result = grid.process(frames, targets, output.span(offered));
    CHECK(result.status == Status::ok);
    CHECK(result.edgesWritten == expectedEdges);
    CHECK(result.requiredEdges == expectedEdges);
    output.check_tail(expectedEdges);
}

template <typename Operation>
void rejected_status(Grid& grid, Operation operation, Status expected) {
    const auto before = grid.snapshot();
    CHECK(operation() == expected);
    check_snapshot(grid.snapshot(), before);
}

void zero_identity(Grid& grid, OutputCanary& output) {
    const auto before = grid.snapshot();
    accepted_process(grid, 0, {}, output, 0);
    check_snapshot(grid.snapshot(), before);
    accepted_process(grid, 0, {}, output, 0, 0);
    check_snapshot(grid.snapshot(), before);
}

void test_phase_matrix() {
    auto grid = std::make_unique<Grid>();
    OutputCanary output;
    const Config valid = configuration();
    const Config invalid{};
    const std::array<Target, 1> one{{{0, 0, 0}}};
    const std::vector<Target> excessive(513, Target{u32max, u32max, u64max});
    check_snapshot(grid->snapshot(), Snapshot{});
    check_snapshot(grid->snapshot(), Snapshot{}); // A read is also an identity.

    rejected_process(*grid, 0, {}, Status::invalid_state, output);
    rejected_process(*grid, u32max, excessive, Status::invalid_state, output, 0);
    rejected_status(*grid, [&] { return grid->close_observation({}); }, Status::invalid_state);
    rejected_status(*grid, [&] { return grid->close_observation(excessive); }, Status::invalid_state);
    rejected_status(*grid, [&] { return grid->reset(); }, Status::invalid_state);
    rejected_status(*grid, [&] { return grid->prepare(invalid); }, Status::invalid_configuration);
    CHECK(grid->prepare(valid) == Status::ok);
    check_clean_epoch(*grid, valid);

    zero_identity(*grid, output);
    rejected_process(*grid, 0, one, Status::invalid_target, output);
    rejected_status(*grid, [&] { return grid->reset(); }, Status::invalid_state);
    CHECK(grid->prepare(valid) == Status::ok); // Repreparation is allowed while ready.
    check_clean_epoch(*grid, valid);
    accepted_process(*grid, 1, {}, output, 0, 0);
    CHECK(grid->snapshot().phase == Phase::active);
    CHECK(grid->snapshot().cursorFrames == 1);
    zero_identity(*grid, output);
    rejected_status(*grid, [&] { return grid->prepare(valid); }, Status::invalid_state);
    rejected_status(*grid, [&] { return grid->prepare(invalid); }, Status::invalid_state);
    rejected_status(*grid, [&] { return grid->reset(); }, Status::invalid_state);

    CHECK(grid->close_observation({}) == Status::ok);
    CHECK(grid->snapshot().phase == Phase::closed);
    rejected_process(*grid, 0, {}, Status::invalid_state, output);
    rejected_process(*grid, 1, one, Status::invalid_state, output);
    rejected_process(*grid, u32max, excessive, Status::invalid_state, output);
    rejected_status(*grid, [&] { return grid->close_observation({}); }, Status::invalid_state);
    rejected_status(*grid, [&] { return grid->close_observation(excessive); }, Status::invalid_state);
    rejected_status(*grid, [&] { return grid->prepare(invalid); }, Status::invalid_configuration);
    CHECK(grid->reset() == Status::ok);
    check_clean_epoch(*grid, valid);
    rejected_status(*grid, [&] { return grid->reset(); }, Status::invalid_state);
    CHECK(grid->close_observation({}) == Status::ok); // The empty N=0 epoch is valid.
    CHECK(grid->snapshot().cursorFrames == 0);
    CHECK(grid->reset() == Status::ok);
    check_clean_epoch(*grid, valid);
}

void test_configuration_transactions_and_canonicalization() {
    const auto valid = configuration(4);
    std::vector<Config> invalid;
    for (const auto rate : {0u, 44099u, 44101u, 47999u, 48001u, 95999u, 96001u, u32max}) {
        auto config = valid;
        config.sampleRateHz = rate;
        invalid.push_back(config);
    }
    for (const auto count : {0u, 5u, u32max}) {
        auto config = valid;
        config.keyCount = count;
        invalid.push_back(config);
    }
    for (std::uint32_t key = 0; key < 4; ++key) {
        auto config = valid;
        config.keys[key].pressUnitsPerTick = 0;
        invalid.push_back(config);
        config = valid;
        config.keys[key].releaseUnitsPerTick = 0;
        invalid.push_back(config);
    }
    for (const ContactGridThreshold threshold :
         {ContactGridThreshold{0, 0}, {1, 1}, {2, 1}, {0, full + 1},
          {full, full}, {full + 1, full}, {u64max, u64max}}) {
        auto config = valid;
        config.keys[3].contacts[8] = threshold; // Reject after a fully valid prefix.
        invalid.push_back(config);
    }

    auto grid = std::make_unique<Grid>();
    OutputCanary output;
    for (const auto& config : invalid) {
        rejected_status(*grid, [&] { return grid->prepare(config); }, Status::invalid_configuration);
    }
    CHECK(grid->prepare(valid) == Status::ok);
    for (const auto& config : invalid) {
        rejected_status(*grid, [&] { return grid->prepare(config); }, Status::invalid_configuration);
    }
    const std::array<Target, 1> down{{{0, 3, 1000}}};
    accepted_process(*grid, 1, down, output, 9);
    CHECK(grid->close_observation({}) == Status::ok);
    for (const auto& config : invalid) {
        rejected_status(*grid, [&] { return grid->prepare(config); }, Status::invalid_configuration);
    }

    for (const auto rate : {44100u, 48000u, 96000u}) {
        for (std::uint32_t keyCount = 1; keyCount <= 4; ++keyCount) {
            auto config = configuration(keyCount);
            config.sampleRateHz = rate;
            config.keys[0].pressUnitsPerTick = u32max;
            config.keys[0].releaseUnitsPerTick = u32max;
            config.keys[0].contacts[0] = {0, full};
            for (std::uint32_t key = keyCount; key < 4; ++key) {
                config.keys[key].pressUnitsPerTick = 0;
                config.keys[key].releaseUnitsPerTick = 0;
                for (auto& threshold : config.keys[key].contacts) {
                    threshold = {u64max, 0};
                }
            }
            const auto copied = canonical(config);
            CHECK(grid->prepare(config) == Status::ok);
            check_clean_epoch(*grid, copied);
            config = Config{}; // The API owns its active configuration copy.
            check_clean_epoch(*grid, copied);
        }
    }
}

void test_validation_precedence_and_late_invalid() {
    for (const bool active : {false, true}) {
        auto grid = prepared(configuration(2));
        OutputCanary output;
        if (active) {
            accepted_process(*grid, 1, {}, output, 0);
        }
        const auto begin = grid->snapshot().cursorFrames * ticks;
        const auto end = begin + ticks;
        const std::vector<Target> excessive(513, Target{u32max, u32max, u64max});
        rejected_process(*grid, u32max, excessive, Status::frame_limit, output, 0);
        rejected_process(*grid, 4097, excessive, Status::frame_limit, output);
        rejected_process(*grid, 1, excessive, Status::command_limit, output, 0);
        rejected_process(*grid, 0, excessive, Status::command_limit, output);

        const std::array<Target, 1> noop{{{begin, 0, 0}}};
        rejected_process(*grid, 0, noop, Status::invalid_target, output);
        const std::array<Target, 3> domainBeforeOrder{{
            {begin + 20, 0, 1000}, {begin + 10, 0, 0}, {begin + 30, 2, 1000}}};
        rejected_process(*grid, 1, domainBeforeOrder, Status::invalid_target, output, 0);
        const std::array<Target, 3> unordered{{
            {begin, 0, 1000}, {begin + 2000, 0, 0}, {begin + 1000, 1, 1000}}};
        rejected_process(*grid, 1, unordered, Status::unordered_targets, output, 0);
        rejected_process(*grid, 1, unordered, Status::unordered_targets, output);

        std::vector<Target> lateInvalid{
            {begin, 0, 1000}, {begin + 1500, 0, 0},
            {begin + 3000, 1, 1000}, {begin + 4500, 0, 0}};
        const std::array<Target, 6> badLast{{
            {end, 0, 0}, {u32max, 0, 0}, {begin + 4500, 2, 0},
            {begin + 4500, u32max, 0}, {begin + 4500, 0, full + 1},
            {begin + 4500, 0, u64max}}};
        for (const auto& bad : badLast) {
            lateInvalid.back() = bad;
            rejected_process(*grid, 1, lateInvalid, Status::invalid_target, output);
        }
        if (active) {
            lateInvalid.back() = {begin - 1, 0, 0};
            // The out-of-window domain beats the decreasing final tick.
            rejected_process(*grid, 1, lateInvalid, Status::invalid_target, output);
        }

        // Previous rejections must leave a normal success identical to a fresh
        // call at the same cursor, even after staging valid prefix commands.
        lateInvalid.back() = {begin + 4500, 0, 0};
        auto fresh = prepared(configuration(2));
        OutputCanary freshOutput(64, 0x3C);
        if (active) {
            accepted_process(*fresh, 1, {}, freshOutput, 0);
        }
        accepted_process(*grid, 1, lateInvalid, output, 27);
        accepted_process(*fresh, 1, lateInvalid, freshOutput, 27);
        output.check_prefix(freshOutput, 27);
        check_snapshot(grid->snapshot(), fresh->snapshot());
    }
}

void test_actual_output_capacity_and_retry() {
    // The 36 thresholds are exactly 1..36 across four keys. Moving all four
    // keys to N crosses exactly N contacts; no trajectory helper is needed.
    auto config = configuration(4);
    for (std::uint32_t key = 0; key < 4; ++key) {
        for (std::uint32_t contact = 0; contact < 9; ++contact) {
            config.keys[key].contacts[contact] = {0, 1 + 9 * key + contact};
        }
    }
    for (const auto count : {0u, 1u, 8u, 9u, 10u, 18u, 35u, 36u}) {
        auto grid = prepared(config);
        auto fresh = prepared(config);
        OutputCanary output;
        OutputCanary freshOutput(64, 0x5A);
        std::array<Target, 4> commands{};
        for (std::uint32_t key = 0; key < 4; ++key) {
            commands[key] = {0, key, count};
        }
        if (count != 0) {
            rejected_process(*grid, 1, commands, Status::output_too_small, output, 0, count);
            rejected_process(*grid, 1, commands, Status::output_too_small, output, count - 1, count);
        }
        accepted_process(*grid, 1, commands, output, count, count);
        accepted_process(*fresh, 1, commands, freshOutput, count);
        output.check_prefix(freshOutput, count);
        check_snapshot(grid->snapshot(), fresh->snapshot());
        CHECK(grid->snapshot().commandCount == 4);
        CHECK(grid->snapshot().edgeCount == count);
    }
}

void test_retry_with_existing_history() {
    const auto config = configuration(2);
    auto grid = prepared(config);
    auto fresh = prepared(config);
    OutputCanary output;
    OutputCanary freshOutput(64, 0x6D);
    const std::array<Target, 2> prefix{{{0, 0, 1000}, {0, 1, 1000}}};
    accepted_process(*grid, 1, prefix, output, 18);
    accepted_process(*fresh, 1, prefix, freshOutput, 18);
    const auto previous = grid->snapshot();
    const std::array<Target, 3> next{{
        {ticks, 0, 0}, {ticks, 1, 0}, {ticks + 2000, 0, 1000}}};
    rejected_process(*grid, 1, next, Status::output_too_small, output, 0, 27);
    rejected_process(*grid, 1, next, Status::output_too_small, output, 26, 27);
    zero_identity(*grid, output);
    check_snapshot(grid->snapshot(), previous);
    accepted_process(*grid, 1, next, output, 27, 27);
    accepted_process(*fresh, 1, next, freshOutput, 27);
    output.check_prefix(freshOutput, 27);
    check_snapshot(grid->snapshot(), fresh->snapshot());
    const std::array<Target, 2> endpoint{{{2 * ticks, 1, full}, {2 * ticks, 0, 0}}};
    CHECK(grid->close_observation(endpoint) == Status::ok);
    CHECK(fresh->close_observation(endpoint) == Status::ok);
    check_snapshot(grid->snapshot(), fresh->snapshot());
    CHECK(grid->reset() == Status::ok);
    CHECK(fresh->reset() == Status::ok);
    check_snapshot(grid->snapshot(), fresh->snapshot());
    check_clean_epoch(*grid, config);
}

void test_noop_anchors_and_endpoint_ties() {
    const auto config = configuration(2);
    auto grid = prepared(config);
    OutputCanary output;
    const std::array<Target, 2> down{{{0, 0, full}, {0, 1, 1000}}};
    accepted_process(*grid, 1, down, output, 18);
    const std::array<Target, 4> noops{{
        {ticks, 1, 1000}, {ticks, 0, full},
        {ticks + 17, 0, full}, {2 * ticks - 1, 1, 1000}}};
    accepted_process(*grid, 1, noops, output, 0, 0);
    auto expected = grid->snapshot();
    CHECK(expected.phase == Phase::active);
    CHECK(expected.commandCount == 6);
    CHECK(expected.edgeCount == 18);
    CHECK(expected.keys[0].position == 2 * ticks);
    CHECK(expected.keys[1].position == 1000);
    for (std::size_t key = 0; key < 2; ++key) {
        CHECK(expected.keys[key].anchorPosition == 0);
        CHECK(expected.keys[key].anchorTick == 0);
    }
    zero_identity(*grid, output);
    const std::array<Target, 2> endpointNoops{{{2 * ticks, 1, 1000}, {2 * ticks, 0, full}}};
    CHECK(grid->close_observation(endpointNoops) == Status::ok);
    expected.phase = Phase::closed;
    expected.commandCount += 2;
    check_snapshot(grid->snapshot(), expected);

    // A tied change away and back is not equivalent to a single final no-op.
    CHECK(grid->reset() == Status::ok);
    accepted_process(*grid, 1, down, output, 18);
    expected = grid->snapshot();
    const std::array<Target, 4> ties{{
        {ticks, 0, 0}, {ticks, 1, 1000}, {ticks, 0, full}, {ticks, 0, full}}};
    CHECK(grid->close_observation(ties) == Status::ok);
    expected.phase = Phase::closed;
    expected.commandCount += 4;
    expected.keys[0].anchorPosition = ticks;
    expected.keys[0].anchorTick = ticks;
    check_snapshot(grid->snapshot(), expected);

    CHECK(grid->reset() == Status::ok);
    expected = grid->snapshot();
    const std::array<Target, 5> zeroEndpoint{{
        {0, 1, full}, {0, 0, 1000}, {0, 1, 0}, {0, 0, 0}, {0, 1, full}}};
    CHECK(grid->close_observation(zeroEndpoint) == Status::ok);
    expected.phase = Phase::closed;
    expected.commandCount = 5;
    expected.keys[1].target = full;
    check_snapshot(grid->snapshot(), expected); // No travel or closing edges at N=0.
}

void test_close_rejection_transactions() {
    for (const bool active : {false, true}) {
        const auto config = configuration(2);
        auto grid = prepared(config);
        OutputCanary output;
        if (active) {
            const std::array<Target, 2> down{{{0, 0, full}, {0, 1, 1000}}};
            accepted_process(*grid, 1, down, output, 18);
        }
        const auto tick = grid->snapshot().cursorFrames * ticks;
        const std::vector<Target> excessive(513, Target{tick + 1, u32max, u64max});
        rejected_status(*grid, [&] { return grid->close_observation(excessive); }, Status::command_limit);
        std::array<Target, 3> commands{{{tick, 0, 1000}, {tick, 1, 0}, {tick, 0, 0}}};
        const std::array<Target, 6> badLast{{
            {tick + 1, 0, 0}, {u32max, 0, 0}, {tick, 2, 0},
            {tick, u32max, 0}, {tick, 0, full + 1}, {tick, 0, u64max}}};
        for (const auto& bad : badLast) {
            commands.back() = bad;
            rejected_status(*grid, [&] { return grid->close_observation(commands); }, Status::invalid_target);
        }
        if (active) {
            commands.back() = {tick - 1, 0, 0};
            rejected_status(*grid, [&] { return grid->close_observation(commands); }, Status::invalid_target);
        }
        commands.back() = {tick, 0, 0};
        auto expected = grid->snapshot();
        expected.phase = Phase::closed;
        expected.commandCount += 3;
        for (std::size_t key = 0; key < 2; ++key) {
            expected.keys[key].anchorPosition = expected.keys[key].position;
            expected.keys[key].anchorTick = tick;
            expected.keys[key].target = 0;
        }
        // In the zero-time case key 1 receives only a no-op; its zero anchor
        // already agrees with the expected fields above.
        CHECK(grid->close_observation(commands) == Status::ok);
        check_snapshot(grid->snapshot(), expected);
    }
}

void test_command_capacity_across_calls_and_closure() {
    const auto config = configuration();
    auto grid = prepared(config);
    OutputCanary output;
    std::vector<Target> first(255, Target{0, 0, 0});
    std::vector<Target> second(256, Target{ticks, 0, 0});
    accepted_process(*grid, 1, first, output, 0, 0);
    accepted_process(*grid, 1, second, output, 0, 0);
    CHECK(grid->snapshot().commandCount == 511);
    const std::array<Target, 2> tooMany{{
        {2 * ticks, u32max, u64max}, {2 * ticks - 1, 0, 0}}};
    rejected_process(*grid, 1, tooMany, Status::command_limit, output);
    rejected_process(*grid, 0, tooMany, Status::command_limit, output);
    rejected_status(*grid, [&] { return grid->close_observation(tooMany); }, Status::command_limit);
    const std::array<Target, 1> last{{{2 * ticks, 0, 0}}};
    rejected_process(*grid, 0, last, Status::invalid_target, output);
    zero_identity(*grid, output);
    CHECK(grid->close_observation(last) == Status::ok);
    CHECK(grid->snapshot().commandCount == 512);
    CHECK(grid->snapshot().cursorFrames == 2);
    CHECK(grid->snapshot().edgeCount == 0);
    CHECK(grid->reset() == Status::ok);
    check_clean_epoch(*grid, config);

    first.push_back(Target{0, 0, 0});
    accepted_process(*grid, 1, first, output, 0, 0);
    accepted_process(*grid, 1, second, output, 0, 0);
    CHECK(grid->snapshot().commandCount == 512);
    rejected_process(*grid, 1, last, Status::command_limit, output);
    rejected_process(*grid, 0, last, Status::command_limit, output);
    rejected_status(*grid, [&] { return grid->close_observation(last); }, Status::command_limit);
    accepted_process(*grid, 1, {}, output, 0, 0); // Motion time remains available.
    CHECK(grid->snapshot().commandCount == 512);
    CHECK(grid->snapshot().cursorFrames == 3);
    CHECK(grid->close_observation({}) == Status::ok);
    CHECK(grid->reset() == Status::ok);
    check_clean_epoch(*grid, config);

    const std::vector<Target> endpoint(512, Target{0, 0, 0});
    const std::vector<Target> excessive(513, Target{0, 0, 0});
    rejected_status(*grid, [&] { return grid->close_observation(excessive); }, Status::command_limit);
    rejected_process(*grid, 0, endpoint, Status::invalid_target, output);
    CHECK(grid->close_observation(endpoint) == Status::ok);
    auto expected = Snapshot{};
    expected.phase = Phase::closed;
    expected.config = config;
    expected.commandCount = 512;
    check_snapshot(grid->snapshot(), expected);
}

void test_frame_exhaustion_and_reset_reprepare() {
    auto config = configuration(2);
    auto grid = prepared(config);
    OutputCanary output;
    accepted_process(*grid, 4095, {}, output, 0, 0);
    const std::array<Target, 1> invalid{{{u32max, u32max, u64max}}};
    rejected_process(*grid, 2, invalid, Status::frame_limit, output);
    rejected_process(*grid, u32max, {}, Status::frame_limit, output);
    accepted_process(*grid, 1, {}, output, 0, 0);
    CHECK(grid->snapshot().cursorFrames == 4096);
    rejected_process(*grid, 1, {}, Status::frame_limit, output);
    const std::vector<Target> excessive(513, Target{u32max, u32max, u64max});
    rejected_process(*grid, 1, excessive, Status::frame_limit, output);
    rejected_process(*grid, 0, excessive, Status::command_limit, output);
    rejected_process(*grid, 0, invalid, Status::invalid_target, output);
    zero_identity(*grid, output);
    const std::array<Target, 2> endpoint{{{4096 * ticks, 1, full}, {4096 * ticks, 0, 1000}}};
    auto expected = grid->snapshot();
    CHECK(grid->close_observation(endpoint) == Status::ok);
    expected.phase = Phase::closed;
    expected.commandCount = 2;
    expected.keys[0].target = 1000;
    expected.keys[1].target = full;
    expected.keys[0].anchorTick = 4096 * ticks;
    expected.keys[1].anchorTick = 4096 * ticks;
    check_snapshot(grid->snapshot(), expected);
    rejected_process(*grid, 1, excessive, Status::invalid_state, output);
    CHECK(grid->reset() == Status::ok);
    check_clean_epoch(*grid, config);

    // Reset restores both limits, positions, targets, anchors and contact bits.
    const std::array<Target, 1> down{{{0, 1, 1000}}};
    accepted_process(*grid, 4096, down, output, 9);
    CHECK(grid->close_observation({}) == Status::ok);
    CHECK(grid->reset() == Status::ok);
    check_clean_epoch(*grid, config);
    accepted_process(*grid, 1, down, output, 9);
    CHECK(grid->close_observation({}) == Status::ok);

    // Reprepare from a nonempty closed epoch replaces the copied configuration
    // and canonicalizes the old second key out of both config and history.
    config = configuration();
    config.sampleRateHz = 96000;
    config.keys[0].pressUnitsPerTick = 7;
    config.keys[0].releaseUnitsPerTick = 11;
    config.keys[0].contacts[8] = {full - 1, full};
    config.keys[1].contacts[0] = {u64max, 0};
    CHECK(grid->prepare(config) == Status::ok);
    check_clean_epoch(*grid, config);
    const auto retained = grid->snapshot();
    config = Config{};
    check_snapshot(grid->snapshot(), retained);
    CHECK(grid->close_observation({}) == Status::ok);
    CHECK(grid->reset() == Status::ok);
    check_snapshot(grid->snapshot(), retained);
}

} // namespace

int main() {
    test_phase_matrix();
    test_configuration_transactions_and_canonicalization();
    test_validation_precedence_and_late_invalid();
    test_actual_output_capacity_and_retry();
    test_retry_with_existing_history();
    test_noop_anchors_and_endpoint_ties();
    test_close_rejection_transactions();
    test_command_capacity_across_calls_and_closure();
    test_frame_exhaustion_and_reset_reprepare();
    std::cout << "causal contact grid lifecycle and transaction tests passed\n";
    return 0;
}
