#pragma once

#include "hammond/ControlState.h"
#include "hammond/ParameterBridge.h"

#include <array>
#include <atomic>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <span>
#include <string_view>

namespace hammond {

inline constexpr std::string_view kStateExchangeModelId =
    "bounded-spsc-control-state-exchange-v1";
inline constexpr std::size_t kStateQueueCapacity = 4;
inline constexpr std::size_t kStateReadAttempts = 8;
inline constexpr std::size_t kStatePublicationCellCount = kParameterCount + 3;

// No counter wraps or resets within an object's lifetime. Smaller limits are
// legitimate finite-lifetime configurations, including zero. A publication
// limit above UINT64_MAX/2 is invalid and makes every operation fail closed.
struct StateExchangeLimits {
    std::uint64_t accepted_states{std::numeric_limits<std::uint64_t>::max()};
    std::uint64_t publications{std::numeric_limits<std::uint64_t>::max() / 2};
};

enum class StateExchangeStatus : std::uint8_t {
    Ok,
    InvalidSnapshot,
    QueueFull,
    SequenceExhausted,
    InvalidBatch,
    InvalidLimits
};

struct StateEnqueueResult {
    StateExchangeStatus status{StateExchangeStatus::Ok};
    std::uint64_t sequence{0}; // Zero on failure; successful loads start at one.

    [[nodiscard]] constexpr bool ok() const noexcept {
        return status == StateExchangeStatus::Ok;
    }
    [[nodiscard]] constexpr explicit operator bool() const noexcept { return ok(); }
};

class StateExchange;

// Value-owned callback input and opaque commit token. Copying is permitted;
// successful commit makes every token for the old publication revision stale.
// Tokens must not outlive their originating StateExchange. There is no mutable
// view of a token's snapshots and no pointer into a queue slot or host stream.
class StateExchangeBatch {
public:
    StateExchangeBatch() noexcept = default;

    [[nodiscard]] std::span<const ControlSnapshot> snapshots() const noexcept {
        return {snapshots_.data(), count_};
    }
    [[nodiscard]] std::size_t size() const noexcept { return count_; }
    [[nodiscard]] std::uint64_t last_sequence() const noexcept { return end_sequence_; }

private:
    friend class StateExchange;
    std::array<ControlSnapshot, kStateQueueCapacity> snapshots_{};
    const StateExchange* origin_{nullptr};
    std::uint64_t base_sequence_{0};
    std::uint64_t end_sequence_{0};
    std::uint64_t publication_revision_{0};
    std::size_t count_{0};
};

struct StatePublishedControls {
    ControlSnapshot controls{};
    std::uint64_t acknowledged_sequence{0};
    std::uint64_t publication_revision{0}; // Always even on a successful read.
};

// Fixed-capacity SPSC state handoff, independent of the host SDK and parser.
//
// One serialized UI/main thread owns ui_enqueue() and ui_snapshot_for_save().
// One audio thread owns audio_peek(), audio_can_commit() and audio_commit().
// read_published() uses atomic storage only and permits additional observers.
// Construction/destruction require quiescence; copying/moving/reset is absent.
// The default coherent snapshot exists before audio activation. All methods
// use bounded fixed storage, perform no allocation, wait, lock, parsing or I/O.
class StateExchange {
public:
    explicit StateExchange(StateExchangeLimits limits = {}) noexcept;
    StateExchange(const StateExchange&) = delete;
    StateExchange& operator=(const StateExchange&) = delete;
    StateExchange(StateExchange&&) = delete;
    StateExchange& operator=(StateExchange&&) = delete;

    // Validate the entire copied value before publishing a slot. Invalid,
    // full or exhausted input changes neither pending records nor UI state.
    [[nodiscard]] StateEnqueueResult ui_enqueue(const ControlSnapshot& snapshot) noexcept;

    // Copy all currently available records (0..4), without consuming any.
    // Failure leaves destination unchanged. A producer append after this call
    // remains pending for a later batch and cannot invalidate this token.
    [[nodiscard]] StateExchangeStatus audio_peek(StateExchangeBatch& destination) noexcept;

    // Preflight BEFORE candidate processing. Covers token ownership/freshness,
    // queued range and publication exhaustion. A successful preflight remains
    // valid until this audio thread commits another batch. Concurrent UI
    // appends cannot invalidate it. The current Engine snapshot must be valid.
    [[nodiscard]] StateExchangeStatus audio_can_commit(
        const StateExchangeBatch& batch) const noexcept;

    // Call only after the whole candidate callback succeeds. Publish controls
    // and acknowledgement coherently, then release queue slots. Every failure
    // is checked before mutation. After successful preflight, sole audio
    // ownership plus a valid Engine snapshot PROVES this call returns Ok;
    // there is no new capacity/resource decision after engine processing.
    // Rejected callbacks simply omit this call, retaining all queued records.
    [[nodiscard]] StateExchangeStatus audio_commit(
        const StateExchangeBatch& batch, const ControlSnapshot& current_controls) noexcept;

    // At most eight attempts; a busy writer or invalid configuration returns
    // false and preserves destination. All payload cells and the odd/even
    // revision are atomic uint64_t, using sequentially consistent ordering.
    [[nodiscard]] bool read_published(StatePublishedControls& destination) const noexcept;

    // UI producer thread only. Return the newest accepted UI snapshot while
    // its sequence is pending; after acknowledgement return coherent audio
    // controls (including subsequent automation). Failure preserves destination.
    [[nodiscard]] bool ui_snapshot_for_save(ControlSnapshot& destination) const noexcept;

private:
    const StateExchangeLimits limits_;
    const bool valid_limits_;

    // Plain queue slots have exclusive ownership established by the two
    // release/acquire cursors. Producer-only and consumer-only fields are
    // never read by the opposite thread.
    std::array<ControlSnapshot, kStateQueueCapacity> slots_{};
    std::atomic<std::uint64_t> queued_sequence_{0};
    std::atomic<std::uint64_t> consumed_sequence_{0};
    std::uint64_t producer_sequence_{0};
    ControlSnapshot latest_accepted_{};
    std::uint64_t consumer_sequence_{0};
    std::uint64_t audio_publication_revision_{0};

    std::atomic<std::uint64_t> published_revision_{0};
    std::array<std::atomic<std::uint64_t>, kStatePublicationCellCount> published_cells_{};
};

static_assert(std::atomic<std::uint64_t>::is_always_lock_free,
              "StateExchange requires always-lock-free 64-bit atomics on its target");

} // namespace hammond
