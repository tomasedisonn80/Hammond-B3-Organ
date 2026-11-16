#include "hammond/research/CausalContactGrid.h"

#include <limits>

namespace hammond::research {
namespace {

constexpr std::uint64_t maximumEpochTick =
    std::uint64_t{kContactGridMaxFrames} * kContactGridTicksPerFrame;
static_assert(maximumEpochTick <= std::numeric_limits<std::uint32_t>::max());

[[nodiscard]] bool accepts_motion(ContactGridPhase phase) noexcept {
    return phase == ContactGridPhase::ready || phase == ContactGridPhase::active;
}

[[nodiscard]] bool valid_configuration(const ContactGridConfig& config) noexcept {
    if (config.sampleRateHz != 44100 && config.sampleRateHz != 48000
        && config.sampleRateHz != 96000) return false;
    if (config.keyCount == 0 || config.keyCount > kContactGridMaxKeys) return false;
    for (std::uint32_t keyIndex = 0; keyIndex < config.keyCount; ++keyIndex) {
        const auto& key = config.keys[keyIndex];
        if (key.pressUnitsPerTick == 0 || key.releaseUnitsPerTick == 0) return false;
        for (const auto& contact : key.contacts) {
            if (contact.off >= contact.on || contact.on > kContactGridFullTravel) {
                return false;
            }
        }
    }
    return true;
}

void apply_target(ContactGridSnapshot& state, const ContactGridTarget& target) noexcept {
    auto& key = state.keys[target.keyIndex];
    // A repeated target must not rebase an unfinished or already arrived motion.
    if (key.target == target.position) return;
    key.anchorPosition = key.position;
    key.anchorTick = target.tick;
    key.target = target.position;
}

[[nodiscard]] bool position_at(const ContactGridKeyConfig& config,
                                const ContactGridKeySnapshot& key,
                                std::uint32_t tick,
                                std::uint64_t& position) noexcept {
    if (tick < key.anchorTick || key.anchorPosition > kContactGridFullTravel
        || key.target > kContactGridFullTravel) return false;
    if (key.target == key.anchorPosition) {
        position = key.anchorPosition;
        return true;
    }

    const bool rising = key.target > key.anchorPosition;
    const std::uint32_t speed = rising ? config.pressUnitsPerTick
                                       : config.releaseUnitsPerTick;
    if (speed == 0) return false;
    const std::uint64_t elapsed = tick - key.anchorTick;
    if (elapsed > std::numeric_limits<std::uint64_t>::max() / speed) return false;
    const std::uint64_t displacement = elapsed * std::uint64_t{speed};
    const std::uint64_t distance = rising ? key.target - key.anchorPosition
                                          : key.anchorPosition - key.target;
    const std::uint64_t travelled = displacement < distance ? displacement : distance;
    // Clamp the displacement before either directional position operation.
    if (rising) {
        if (travelled > kContactGridFullTravel - key.anchorPosition) return false;
        position = key.anchorPosition + travelled;
    } else {
        if (travelled > key.anchorPosition) return false;
        position = key.anchorPosition - travelled;
    }
    return true;
}

enum class CrossingResult : std::uint8_t { outside, reached, overflow };

[[nodiscard]] CrossingResult crossing_time(std::uint32_t anchorTick,
                                           std::uint64_t distance,
                                           std::uint32_t speed,
                                           std::uint32_t beginTick,
                                           std::uint32_t endTick,
                                           ContactGridTime& time) noexcept {
    if (speed == 0) return CrossingResult::overflow;
    const std::uint64_t quotient = distance / speed;
    // The remainder is strictly below the uint32_t speed before narrowing.
    const auto remainder = static_cast<std::uint32_t>(distance % speed);
    if (quotient > std::numeric_limits<std::uint64_t>::max() - anchorTick) {
        return CrossingResult::overflow;
    }
    const std::uint64_t wholeTick = std::uint64_t{anchorTick} + quotient;

    // Future roots can exceed UINT32_MAX. Establish (begin,end] eligibility
    // in uint64_t before narrowing or normalizing the fraction.
    if (wholeTick < beginTick || (wholeTick == beginTick && remainder == 0)
        || wholeTick > endTick || (wholeTick == endTick && remainder != 0)) {
        return CrossingResult::outside;
    }
    if (wholeTick > std::numeric_limits<std::uint32_t>::max()) {
        return CrossingResult::overflow;
    }
    if (remainder == 0) {
        time = {static_cast<std::uint32_t>(wholeTick), 0, 1};
        return CrossingResult::reached;
    }

    // Euclid starts with the larger operand. Two remainder steps at least
    // halve it, so a uint32_t pair needs at most 64 steps.
    std::uint32_t larger = speed;
    std::uint32_t smaller = remainder;
    std::uint32_t steps = 0;
    while (smaller != 0) {
        if (steps == 64) return CrossingResult::overflow;
        const std::uint32_t next = larger % smaller;
        larger = smaller;
        smaller = next;
        ++steps;
    }
    time = {static_cast<std::uint32_t>(wholeTick), remainder / larger, speed / larger};
    return CrossingResult::reached;
}

[[nodiscard]] bool edge_before(const ContactGridEdge& left,
                                const ContactGridEdge& right) noexcept {
    if (left.time.tick != right.time.tick) return left.time.tick < right.time.tick;
    // Each product of two uint32_t values fits uint64_t, including products
    // above INT64_MAX. Widen the operand before multiplying.
    const std::uint64_t leftFraction =
        std::uint64_t{left.time.numerator} * right.time.denominator;
    const std::uint64_t rightFraction =
        std::uint64_t{right.time.numerator} * left.time.denominator;
    if (leftFraction != rightFraction) return leftFraction < rightFraction;
    if (left.keyIndex != right.keyIndex) return left.keyIndex < right.keyIndex;
    return left.contactIndex < right.contactIndex;
}

} // namespace

CausalContactGrid::CausalContactGrid() noexcept = default;

ContactGridStatus CausalContactGrid::prepare(const ContactGridConfig& config) noexcept {
    if (state_.phase != ContactGridPhase::unprepared
        && state_.phase != ContactGridPhase::ready
        && state_.phase != ContactGridPhase::closed) return ContactGridStatus::invalid_state;
    if (!valid_configuration(config)) return ContactGridStatus::invalid_configuration;

    staged_ = {};
    staged_.phase = ContactGridPhase::ready;
    staged_.config.sampleRateHz = config.sampleRateHz;
    staged_.config.keyCount = config.keyCount;
    // Never read inactive caller entries; their canonical stored value is zero.
    for (std::uint32_t keyIndex = 0; keyIndex < config.keyCount; ++keyIndex) {
        staged_.config.keys[keyIndex] = config.keys[keyIndex];
    }
    state_ = staged_;
    return ContactGridStatus::ok;
}

ContactGridResult CausalContactGrid::process(
    std::uint32_t frames, std::span<const ContactGridTarget> targets,
    std::span<ContactGridEdge> output) noexcept {
    if (!accepts_motion(state_.phase)) return {ContactGridStatus::invalid_state, 0, 0};
    if (frames > kContactGridMaxFrames - state_.cursorFrames) {
        return {ContactGridStatus::frame_limit, 0, 0};
    }
    if (targets.size() > kContactGridMaxCommands - state_.commandCount) {
        return {ContactGridStatus::command_limit, 0, 0};
    }
    if (frames == 0) {
        if (!targets.empty()) return {ContactGridStatus::invalid_target, 0, 0};
        return {ContactGridStatus::ok, 0, 0};
    }

    // Subtraction admission above bounds these sums/products by 4096 and 2^28.
    const std::uint32_t endFrames = state_.cursorFrames + frames;
    const std::uint32_t beginTick = state_.cursorFrames * kContactGridTicksPerFrame;
    const std::uint32_t endTick = endFrames * kContactGridTicksPerFrame;
    std::uint32_t previousTick = beginTick;
    bool unordered = false;
    for (const auto& target : targets) {
        if (target.keyIndex >= state_.config.keyCount
            || target.position > kContactGridFullTravel
            || target.tick < beginTick || target.tick >= endTick) {
            return {ContactGridStatus::invalid_target, 0, 0};
        }
        // Defer this result until every target domain has passed validation.
        if (target.tick < previousTick) unordered = true;
        previousTick = target.tick;
    }
    if (unordered) return {ContactGridStatus::unordered_targets, 0, 0};

    staged_ = state_;
    std::uint32_t callEdges = 0;
    std::uint32_t intervalBegin = beginTick;
    for (const auto& target : targets) {
        if (target.tick != intervalBegin) {
            if (!advance_interval(intervalBegin, target.tick, callEdges)) {
                return {ContactGridStatus::arithmetic_overflow, 0, 0};
            }
            intervalBegin = target.tick;
        }
        // No travel between tied commands: preserve their complete caller order.
        apply_target(staged_, target);
    }
    if (!advance_interval(intervalBegin, endTick, callEdges)) {
        return {ContactGridStatus::arithmetic_overflow, 0, 0};
    }
    if (callEdges > kContactGridMaxEdges - state_.edgeCount) {
        return {ContactGridStatus::arithmetic_overflow, 0, 0};
    }
    if (output.size() < callEdges) {
        return {ContactGridStatus::output_too_small, 0, callEdges};
    }

    staged_.cursorFrames = endFrames;
    staged_.commandCount += static_cast<std::uint32_t>(targets.size());
    staged_.edgeCount += callEdges;
    staged_.phase = ContactGridPhase::active;
    // All validation, arithmetic and actual-capacity checks precede any write.
    for (std::uint32_t index = 0; index < callEdges; ++index) {
        output[index] = stagedEdges_[index];
    }
    state_ = staged_;
    return {ContactGridStatus::ok, callEdges, callEdges};
}

bool CausalContactGrid::advance_interval(std::uint32_t beginTick,
                                         std::uint32_t endTick,
                                         std::uint32_t& callEdges) noexcept {
    if (beginTick >= endTick) return false;
    std::uint32_t intervalCount = 0;
    for (std::uint32_t keyIndex = 0; keyIndex < staged_.config.keyCount; ++keyIndex) {
        const auto& config = staged_.config.keys[keyIndex];
        auto& key = staged_.keys[keyIndex];
        std::uint64_t position = 0;
        if (!position_at(config, key, endTick, position)) return false;
        const bool rising = key.target > key.anchorPosition;
        const bool falling = key.target < key.anchorPosition;
        if (!rising && !falling) {
            key.position = position;
            continue;
        }
        const std::uint32_t speed = rising ? config.pressUnitsPerTick
                                           : config.releaseUnitsPerTick;
        for (std::uint32_t contactIndex = 0;
             contactIndex < kContactGridContactsPerKey; ++contactIndex) {
            const auto& contact = config.contacts[contactIndex];
            std::uint64_t distance = 0;
            if (rising) {
                if (key.closed[contactIndex] || contact.on < key.anchorPosition
                    || contact.on > key.target || contact.on > position) continue;
                distance = contact.on - key.anchorPosition;
            } else {
                if (!key.closed[contactIndex] || contact.off > key.anchorPosition
                    || contact.off < key.target || contact.off < position) continue;
                distance = key.anchorPosition - contact.off;
            }

            ContactGridTime time{};
            const CrossingResult crossing = crossing_time(
                key.anchorTick, distance, speed, beginTick, endTick, time);
            if (crossing == CrossingResult::overflow) return false;
            if (crossing == CrossingResult::outside) continue;
            if (intervalCount >= intervalEdges_.size()) return false;
            intervalEdges_[intervalCount] = {time, keyIndex, contactIndex, rising};
            ++intervalCount;
            key.closed[contactIndex] = rising;
        }
        // Ordinary processing never changes the original command anchor.
        key.position = position;
    }

    if (callEdges > kContactGridMaxEdges
        || intervalCount > kContactGridMaxEdges - callEdges) return false;
    // At most 36 edges per interval. Sort these batches, never the whole call.
    for (std::uint32_t index = 1; index < intervalCount; ++index) {
        const ContactGridEdge edge = intervalEdges_[index];
        std::uint32_t insertion = index;
        while (insertion != 0 && edge_before(edge, intervalEdges_[insertion - 1])) {
            intervalEdges_[insertion] = intervalEdges_[insertion - 1];
            --insertion;
        }
        intervalEdges_[insertion] = edge;
    }
    for (std::uint32_t index = 0; index < intervalCount; ++index) {
        stagedEdges_[callEdges] = intervalEdges_[index];
        ++callEdges;
    }
    return true;
}

ContactGridStatus CausalContactGrid::close_observation(
    std::span<const ContactGridTarget> endpointTargets) noexcept {
    if (!accepts_motion(state_.phase)) return ContactGridStatus::invalid_state;
    if (endpointTargets.size() > kContactGridMaxCommands - state_.commandCount) {
        return ContactGridStatus::command_limit;
    }
    const std::uint32_t endpointTick = state_.cursorFrames * kContactGridTicksPerFrame;
    for (const auto& target : endpointTargets) {
        if (target.keyIndex >= state_.config.keyCount
            || target.position > kContactGridFullTravel || target.tick != endpointTick) {
            return ContactGridStatus::invalid_target;
        }
    }
    staged_ = state_;
    for (const auto& target : endpointTargets) apply_target(staged_, target);
    staged_.commandCount += static_cast<std::uint32_t>(endpointTargets.size());
    staged_.phase = ContactGridPhase::closed;
    state_ = staged_;
    return ContactGridStatus::ok;
}

ContactGridStatus CausalContactGrid::reset() noexcept {
    if (state_.phase != ContactGridPhase::closed) return ContactGridStatus::invalid_state;
    staged_ = {};
    staged_.config = state_.config;
    staged_.phase = ContactGridPhase::ready;
    state_ = staged_;
    return ContactGridStatus::ok;
}

ContactGridSnapshot CausalContactGrid::snapshot() const noexcept {
    return state_;
}

} // namespace hammond::research
