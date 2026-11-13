#include "Session.h"
#include "TestSupport.h"

#include <algorithm>
#include <array>
#include <atomic>
#include <bit>
#include <chrono>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <functional>
#include <iostream>
#include <limits>
#include <span>
#include <thread>
#include <utility>
#include <vector>

namespace {

using namespace hammond;
using namespace hammond::standalone;

constexpr std::size_t kTransfers = 8192;
constexpr std::size_t kEpochs = 64;
constexpr std::size_t kControlledRecoveryEpochs = 4;
constexpr std::size_t kLatePosts = 96;
constexpr std::size_t kFlights = 16;
constexpr std::size_t kReaders = 2;
constexpr std::uint64_t kInitialFrame = 137;
constexpr std::uint32_t kRecoveryFrames = 64;
constexpr std::uint32_t kFlightFrames = 512;

struct Deadline {
    const std::chrono::steady_clock::time_point end =
        std::chrono::steady_clock::now() + std::chrono::seconds(8);

    void check() const {
        CHECK(std::chrono::steady_clock::now() < end);
    }
};

// The supported Apple standard library does not supply jthread/stop_token.
// Keep the existing cooperative stop-and-join behavior with the same portable
// atomic flag and std::thread ownership pattern as native VST3 acceptance.
class StopToken {
public:
    explicit StopToken(const std::atomic<bool>& requested) noexcept : requested_(requested) {}
    [[nodiscard]] bool stop_requested() const noexcept {
        return requested_.load(std::memory_order_acquire);
    }
private:
    const std::atomic<bool>& requested_;
};

class JoiningThread {
public:
    template<class Function>
    explicit JoiningThread(Function&& function)
        : worker_(std::forward<Function>(function), StopToken{requested_}) {}
    JoiningThread(const JoiningThread&) = delete;
    JoiningThread& operator=(const JoiningThread&) = delete;
    JoiningThread(JoiningThread&&) = delete;
    JoiningThread& operator=(JoiningThread&&) = delete;
    ~JoiningThread() {
        request_stop();
        if (worker_.joinable()) worker_.join();
    }
    void request_stop() noexcept { requested_.store(true, std::memory_order_release); }
private:
    std::atomic<bool> requested_{false}; // Must outlive the thread and its token.
    std::thread worker_;
};

void test_watchdog_unwind_cleanup(const Deadline& deadline) {
    struct UnwindProbe {};
    std::atomic<bool> started{false}, stopped{false}, finished{false};
    bool caught = false;
    try {
        JoiningThread worker([&](StopToken stop) {
            started.store(true, std::memory_order_release);
            while (!stop.stop_requested()) {
                deadline.check();
                std::this_thread::yield();
            }
            stopped.store(stop.stop_requested(), std::memory_order_release);
            finished.store(true, std::memory_order_release);
        });
        while (!started.load(std::memory_order_acquire)) {
            deadline.check();
            std::this_thread::yield();
        }
        throw UnwindProbe{};
    } catch (const UnwindProbe&) {
        caught = true;
    }
    CHECK(caught && stopped.load(std::memory_order_acquire) && finished.load(std::memory_order_acquire));
    std::cout << "Session concurrency cleanup: exception-unwind stop observed, worker joined\n";
}

// Literal complete patterns, independent of Session's packed-word layout.
// Every retained control changes between A and B, including all 36 drawbars.
ControlSnapshot pattern(bool b) {
    ControlSnapshot value;
    if (b) {
        value.drawbars[0][0] = {1, 2, 3, 4, 5, 6, 7, 8, 0};
        value.drawbars[0][1] = {0, 8, 7, 6, 5, 4, 3, 2, 1};
        value.drawbars[1][0] = {3, 5, 7, 0, 2, 4, 6, 8, 1};
        value.drawbars[1][1] = {6, 4, 2, 0, 7, 5, 3, 1, 8};
        value.selected_banks = {DrawbarBank::B, DrawbarBank::A};
        value.route_enabled = {false, true};
        value.percussion = {true, PercussionHarmonic::Third,
                            PercussionVolume::Soft, PercussionDecay::Fast};
        value.pedal_drawbars = {8, 0};
        value.expression = 0.75;
    } else {
        value.drawbars[0][0] = {0, 1, 2, 3, 4, 5, 6, 7, 8};
        value.drawbars[0][1] = {8, 7, 6, 5, 4, 3, 2, 1, 0};
        value.drawbars[1][0] = {2, 4, 6, 8, 1, 3, 5, 7, 0};
        value.drawbars[1][1] = {5, 3, 1, 8, 6, 4, 2, 0, 7};
        value.selected_banks = {DrawbarBank::A, DrawbarBank::B};
        value.route_enabled = {true, false};
        value.percussion = {false, PercussionHarmonic::Second,
                            PercussionVolume::Normal, PercussionDecay::Slow};
        value.pedal_drawbars = {1, 7};
        value.expression = 0.25;
    }
    return value;
}

bool no_holds(const SessionSnapshot& value) {
    for (const auto& manual : value.held_keys) {
        if (std::any_of(manual.begin(), manual.end(), [](bool held) { return held; })) {
            return false;
        }
    }
    return std::none_of(value.held_pedals.begin(), value.held_pedals.end(),
                        [](bool held) { return held; });
}

bool same_snapshot(const SessionSnapshot& a, const SessionSnapshot& b) {
    return a.controls == b.controls && a.held_keys == b.held_keys &&
        a.held_pedals == b.held_pedals && a.frame_clock == b.frame_clock &&
        std::bit_cast<std::uint64_t>(a.sample_rate) ==
            std::bit_cast<std::uint64_t>(b.sample_rate) &&
        std::bit_cast<std::uint32_t>(a.peak) == std::bit_cast<std::uint32_t>(b.peak) &&
        a.prepared == b.prepared && a.running == b.running &&
        a.publication_revision == b.publication_revision &&
        a.resolved_sequence == b.resolved_sequence &&
        a.last_applied_sequence == b.last_applied_sequence &&
        a.recovery_count == b.recovery_count && a.queue_overflows == b.queue_overflows &&
        a.rejected_commands == b.rejected_commands &&
        a.discarded_commands == b.discarded_commands && a.fault_flags == b.fault_flags &&
        a.last_core_status == b.last_core_status;
}

SessionSnapshot read_idle(const Session& session) {
    SessionSnapshot result;
    CHECK(session.read_snapshot(result));
    return result;
}

SessionCommand manual(HostNoteKind kind, std::uint8_t bus, std::uint8_t channel,
                      std::uint8_t note, std::int32_t id) {
    return PerformanceInputEvent{HostNoteEvent{
        0, kind, bus, channel, note, static_cast<std::uint8_t>(kind == HostNoteKind::On ? 100 : 0), id}};
}

SessionCommand pedal(PedalNoteKind kind, std::uint8_t bus, std::uint8_t channel,
                     std::uint8_t note, std::int32_t id) {
    return PerformanceInputEvent{PedalNoteEvent{
        0, kind, bus, channel, PedalId{note},
        static_cast<std::uint8_t>(kind == PedalNoteKind::On ? 100 : 0), id}};
}

struct ReaderStats {
    std::uint64_t successful{};
    std::uint64_t busy{};
    std::uint64_t changes{};
    std::uint64_t active_reads{};
    std::uint64_t initial_revision{};
    std::uint64_t final_revision{};
    const char* failure{};
};

struct Shared {
    // Written before thread creation, then read-only for every observer.
    SessionSnapshot initial_snapshot;
    // Written after the audio join; final_ready publishes it to the readers.
    SessionSnapshot final_snapshot;
    std::atomic<bool> begin{false};
    std::atomic<bool> finish{false};
    std::atomic<bool> final_ready{false};
    std::atomic<bool> audio_active{false};
    std::atomic<bool> audio_failed{false};
    std::atomic<bool> reader_failed{false};
    std::atomic<std::size_t> ready{0};
    std::atomic<std::size_t> initial_readers{0};
    std::atomic<std::size_t> final_readers{0};
};

struct Oracle {
    std::span<const ControlSnapshot> controls;
    bool ordered;
    std::uint32_t frames_per_callback;
    bool coordinated{true};
};

const char* coherent(const SessionSnapshot& value, const SessionSnapshot* previous,
                     const Oracle& oracle) {
    if (!value.prepared || !value.running || value.sample_rate != 48000.0 ||
        !std::isfinite(value.peak) || value.peak < 0.0F ||
        value.publication_revision < 4 || value.publication_revision % 2 != 0 ||
        value.frame_clock != kInitialFrame +
            ((value.publication_revision - 4) / 2) * oracle.frames_per_callback ||
        value.last_applied_sequence > value.resolved_sequence ||
        value.discarded_commands > value.resolved_sequence ||
        !is_valid_control_snapshot(value.controls)) return "invalid cross-field snapshot";
    if (previous != nullptr) {
        if (value.publication_revision < previous->publication_revision ||
            value.frame_clock < previous->frame_clock ||
            value.resolved_sequence < previous->resolved_sequence ||
            value.last_applied_sequence < previous->last_applied_sequence ||
            value.recovery_count < previous->recovery_count ||
            value.queue_overflows < previous->queue_overflows ||
            value.rejected_commands < previous->rejected_commands ||
            value.discarded_commands < previous->discarded_commands) return "regressing snapshot";
        if (value.publication_revision == previous->publication_revision &&
            !same_snapshot(value, *previous)) return "one revision has different payloads";
    }
    if (oracle.ordered) {
        if (value.resolved_sequence > oracle.controls.size() + 1 ||
            value.last_applied_sequence != value.resolved_sequence ||
            value.recovery_count != 0 || value.queue_overflows != 0 ||
            value.rejected_commands != 0 || value.discarded_commands != 0 ||
            value.fault_flags != 0 || value.last_core_status != Status::Ok ||
            value.peak != 0.0F || !no_holds(value)) return "unexpected ordinary state";
        const auto expected = value.resolved_sequence == 0 ? ControlSnapshot{} :
            oracle.controls[static_cast<std::size_t>(std::min<std::uint64_t>(
                value.resolved_sequence, oracle.controls.size())) - 1];
        if (value.controls != expected) return "FIFO sequence or complete control pattern mismatch";
    } else if (!oracle.coordinated) {
        if (value.controls != ControlSnapshot{} && value.controls != oracle.controls[0] &&
            value.controls != oracle.controls[1]) return "hybrid active-overflow controls";
        const auto faults = value.queue_overflows == 0 ? 0U :
            static_cast<std::uint32_t>(SessionFault::QueueOverflow);
        if (value.fault_flags != faults || value.rejected_commands != 0 ||
            value.last_core_status != Status::Ok ||
            value.recovery_count > value.queue_overflows) return "invalid active-overflow diagnostics";
        for (std::size_t m = 0; m < value.held_keys.size(); ++m) {
            for (std::size_t key = 0; key < value.held_keys[m].size(); ++key) {
                const bool permitted = m == 0 ? (key == 24 || key == 25) : key == 36;
                if (value.held_keys[m][key] && !permitted) return "unexpected active-overflow key";
            }
        }
        for (std::size_t p = 0; p < value.held_pedals.size(); ++p) {
            if (value.held_pedals[p] && p != 12 && p != 23 && p != 24) {
                return "unexpected active-overflow pedal";
            }
        }
    } else {
        const auto callback = (value.publication_revision - 4) / 2;
        const auto phase = callback % 4;
        const auto epoch = callback == 0 ? 0 : (callback - 1) / 4;
        const auto recoveries = callback / 4 + (phase >= 2 ? 1U : 0U);
        const auto rejected = (callback + 3) / 4 + recoveries / 2;
        const auto expected = callback == 0 ? ControlSnapshot{} :
            oracle.controls[phase == 1 ? 0 : static_cast<std::size_t>(epoch % 2)];
        if (value.controls != expected || value.recovery_count != recoveries ||
            value.queue_overflows != (recoveries + 1) / 2 ||
            value.rejected_commands != rejected ||
            value.last_core_status != (recoveries >= 2 ? Status::InvalidEvent : Status::Ok)) {
            return "hybrid recovery publication or diagnostics";
        }
        constexpr auto overflow = static_cast<std::uint32_t>(SessionFault::QueueOverflow);
        constexpr auto rejection = static_cast<std::uint32_t>(SessionFault::RejectedCommand);
        if (value.fault_flags != ((value.queue_overflows != 0 ? overflow : 0U) |
                                 (value.rejected_commands != 0 ? rejection : 0U))) {
            return "incoherent recovery fault flags";
        }
        for (std::size_t m = 0; m < value.held_keys.size(); ++m) {
            for (std::size_t key = 0; key < value.held_keys[m].size(); ++key) {
                const bool held = phase == 1 && (m == 0 ? key == 24 : key == 36);
                if (value.held_keys[m][key] != held) return "hybrid manual holds";
            }
        }
        for (std::size_t p = 0; p < value.held_pedals.size(); ++p) {
            const bool held = phase == 1 && (p == 12 || p == 24);
            if (value.held_pedals[p] != held) return "hybrid pedal holds";
        }
    }
    return nullptr;
}

void observe(const Session& session, Shared& shared, const Oracle& oracle, ReaderStats& stats) {
    SessionSnapshot destination;
    destination.controls = pattern(true);
    destination.frame_clock = 999;
    destination.peak = -7.0F;
    destination.publication_revision = 13;
    SessionSnapshot previous;
    bool have_previous = false;
    const auto read_once = [&](bool count_activity) {
        const auto before = destination;
        const bool active = count_activity && shared.audio_active.load(std::memory_order_acquire);
        const bool success = session.read_snapshot(destination);
        // This flag surrounds a public call. Observing it does not establish
        // that this read ran inside render, nor is observing it guaranteed.
        if (count_activity && (active || shared.audio_active.load(std::memory_order_acquire))) {
            ++stats.active_reads;
        }
        if (success) {
            ++stats.successful;
            stats.failure = coherent(destination, have_previous ? &previous : nullptr, oracle);
            if (stats.failure == nullptr) {
                if (!have_previous || destination.publication_revision != previous.publication_revision) {
                    ++stats.changes;
                }
                previous = destination;
                have_previous = true;
            }
        } else {
            ++stats.busy;
            if (!same_snapshot(destination, before)) {
                stats.failure = "failed read changed destination";
            }
        }
        return success;
    };
    const auto checkpoint = [&](const SessionSnapshot& expected, std::uint64_t& revision) {
        // The consumer is quiescent at both checkpoints. A single public read
        // must succeed and match every field, not merely a ready-thread flag.
        const bool success = read_once(false);
        if (stats.failure == nullptr && (!success || !same_snapshot(destination, expected))) {
            stats.failure = "reader checkpoint did not observe the exact stable publication";
        }
        if (stats.failure != nullptr) {
            shared.reader_failed.store(true, std::memory_order_release);
            return false;
        }
        revision = destination.publication_revision;
        return true;
    };
    shared.ready.fetch_add(1, std::memory_order_release);
    if (!checkpoint(shared.initial_snapshot, stats.initial_revision)) return;
    shared.initial_readers.fetch_add(1, std::memory_order_release);
    while (!shared.begin.load(std::memory_order_acquire)) std::this_thread::yield();
    while (!shared.final_ready.load(std::memory_order_acquire)) {
        read_once(true);
        if (stats.failure != nullptr) {
            shared.reader_failed.store(true, std::memory_order_release);
            return;
        }
        if ((stats.successful + stats.busy) % 64 == 0) std::this_thread::yield();
    }
    if (!checkpoint(shared.final_snapshot, stats.final_revision)) return;
    shared.final_readers.fetch_add(1, std::memory_order_release);
}

void begin_workers(Shared& shared, const Deadline& deadline) {
    while (shared.ready.load(std::memory_order_acquire) != kReaders + 1 ||
           shared.initial_readers.load(std::memory_order_acquire) != kReaders) {
        deadline.check();
        CHECK(!shared.reader_failed.load(std::memory_order_acquire));
        std::this_thread::yield();
    }
    shared.begin.store(true, std::memory_order_release);
}

void check_readers(const std::array<ReaderStats, kReaders>& stats, const Shared& shared) {
    for (const auto& reader : stats) {
        if (reader.failure != nullptr) {
            hammond_test::fail("concurrent snapshot oracle", __FILE__, __LINE__, reader.failure);
        }
        CHECK(reader.initial_revision == shared.initial_snapshot.publication_revision);
        CHECK(reader.final_revision == shared.final_snapshot.publication_revision);
        CHECK(reader.final_revision > reader.initial_revision);
        CHECK(reader.successful >= 2 && reader.changes >= 2);
    }
}

void finish_workers(Session& session, Shared& shared, std::thread& audio,
                    std::array<std::thread, kReaders>& readers,
                    const std::array<ReaderStats, kReaders>& stats, const Deadline& deadline) {
    shared.finish.store(true, std::memory_order_release);
    audio.join();
    CHECK(!shared.audio_failed.load(std::memory_order_acquire));
    shared.final_snapshot = read_idle(session);
    CHECK(shared.final_snapshot.publication_revision > shared.initial_snapshot.publication_revision);
    shared.final_ready.store(true, std::memory_order_release);
    while (shared.final_readers.load(std::memory_order_acquire) != kReaders) {
        deadline.check();
        CHECK(!shared.reader_failed.load(std::memory_order_acquire));
        std::this_thread::yield();
    }
    for (auto& reader : readers) reader.join();
    check_readers(stats, shared);
}

struct Counts {
    std::uint64_t ordered_posts{};
    std::uint64_t ordered_callbacks{};
    std::uint64_t overlapping_posts{};
    std::uint64_t recovery_callbacks{};
    std::uint64_t accepted{};
    std::uint64_t applied{};
    std::uint64_t discarded{};
    std::uint64_t consumer_rejected{};
    std::uint64_t producer_rejected{};
    std::uint64_t overflows{};
    std::uint64_t recovery_pending{};
    std::uint64_t before_render_discarded{};
    std::uint64_t before_render_pending{};
    std::uint64_t after_render_accepted{};
    std::uint64_t raced_pending{};
    std::uint64_t raced_discarded{};
    std::uint64_t post_acknowledgment{};
    std::uint64_t active_callbacks{};
    std::uint64_t controlled_deferred_overflows{};
    std::uint64_t active_overflows{};
    std::uint64_t deferred_overflows{};
    std::uint64_t active_accepted{};
    std::uint64_t active_applied{};
    std::uint64_t active_discarded{};
    std::uint64_t preserved_exhausted_reads{};
    std::array<ReaderStats, kReaders> ordered_readers{};
    std::array<ReaderStats, kReaders> recovery_readers{};
    std::array<ReaderStats, kReaders> active_readers{};
};

void quiescent_finish(Session& session, std::uint64_t expected_sequence) {
    const auto panic = session.post(Panic{});
    CHECK(panic.ok() && panic.sequence == expected_sequence + 1);
    CHECK(session.render(0, {}).ok());
    const auto drained = read_idle(session);
    CHECK(drained.resolved_sequence == panic.sequence);
    CHECK(drained.last_applied_sequence == panic.sequence && no_holds(drained));
    CHECK(session.render(0, {}).ok());
    CHECK(no_holds(read_idle(session)));
    CHECK(session.stop() == SessionStatus::Ok);
    const auto stopped = read_idle(session);
    CHECK(!stopped.running && no_holds(stopped));
}

void test_sustained_fifo(const RuntimeProfile& profile, const Deadline& deadline, Counts& counts) {
    std::vector<ControlSnapshot> expected(kTransfers);
    for (std::size_t index = 0; index < expected.size(); ++index) {
        expected[index] = pattern(index % 2 != 0);
        expected[index].expression = 0.25 + static_cast<double>(index + 1) / 65536.0;
        CHECK(is_valid_control_snapshot(expected[index]));
    }
    Session session;
    CHECK(session.prepare(profile, {48000.0, 1, 37, kInitialFrame}) == SessionStatus::Ok);
    CHECK(session.start() == SessionStatus::Ok);
    Shared shared;
    shared.initial_snapshot = read_idle(session);
    const Oracle oracle{expected, true, 1};
    std::array<std::thread, kReaders> readers;
    for (std::size_t index = 0; index < readers.size(); ++index) {
        readers[index] = std::thread(observe, std::cref(session), std::ref(shared),
                                    std::cref(oracle), std::ref(counts.ordered_readers[index]));
    }
    std::thread audio([&] {
        std::array<float, 2> output{};
        shared.ready.fetch_add(1, std::memory_order_release);
        while (!shared.begin.load(std::memory_order_acquire)) std::this_thread::yield();
        while (!shared.finish.load(std::memory_order_acquire)) {
            shared.audio_active.store(true, std::memory_order_release);
            const auto result = session.render(1, output);
            shared.audio_active.store(false, std::memory_order_release);
            ++counts.ordered_callbacks;
            if (!result.ok() || result.frames_rendered != 1 || output[0] != 0.0F || output[1] != 0.0F) {
                shared.audio_failed.store(true, std::memory_order_release);
                return;
            }
        }
    });
    begin_workers(shared, deadline);
    std::uint64_t resolved = 0;
    for (std::size_t index = 0; index < expected.size(); ++index) {
        // A rolling 128-command credit window permits overlap and ring wrap;
        // there is no per-command or per-callback handshake in this phase.
        while (index - resolved >= 128) {
            deadline.check();
            CHECK(!shared.audio_failed.load(std::memory_order_acquire));
            SessionSnapshot snapshot;
            if (session.read_snapshot(snapshot)) resolved = snapshot.resolved_sequence;
            std::this_thread::yield();
        }
        const bool active = shared.audio_active.load(std::memory_order_acquire);
        const auto submitted = session.post(expected[index]);
        if (active || shared.audio_active.load(std::memory_order_acquire)) ++counts.overlapping_posts;
        CHECK(submitted.ok() && submitted.sequence == index + 1);
        ++counts.ordered_posts;
        if (index % 64 == 0) deadline.check();
    }
    const auto panic = session.post(Panic{});
    CHECK(panic.ok() && panic.sequence == kTransfers + 1);
    for (;;) {
        deadline.check();
        CHECK(!shared.audio_failed.load(std::memory_order_acquire));
        SessionSnapshot snapshot;
        if (session.read_snapshot(snapshot) && snapshot.resolved_sequence == panic.sequence) break;
        std::this_thread::yield();
    }
    finish_workers(session, shared, audio, readers, counts.ordered_readers, deadline);
    CHECK(read_idle(session).controls == expected.back());
    quiescent_finish(session, panic.sequence);
}

void test_recovery_epochs(const RuntimeProfile& profile, const Deadline& deadline, Counts& counts) {
    const std::array controls{pattern(false), pattern(true)};
    const std::array held_commands{
        manual(HostNoteKind::On, 0, 1, 60, 100),
        manual(HostNoteKind::On, 1, 2, 72, 101),
        pedal(PedalNoteKind::On, 0, 1, 13, 102),
        pedal(PedalNoteKind::On, 1, 2, 25, 103)};
    const std::array release_commands{
        manual(HostNoteKind::Off, 0, 1, 60, 100),
        pedal(PedalNoteKind::Off, 0, 1, 13, 102),
        manual(HostNoteKind::Off, 1, 2, 72, 101),
        pedal(PedalNoteKind::Off, 1, 2, 25, 103)};
    const std::array late_commands{
        manual(HostNoteKind::On, 0, 3, 61, 300),
        pedal(PedalNoteKind::On, 1, 4, 24, 301)};
    const SessionCommand invalid_payload{PerformanceInputEvent{Event{
        0, EventType::Expression, Manual::Upper, 0, std::numeric_limits<double>::quiet_NaN()}}};
    auto bad_controls = controls[0];
    bad_controls.drawbars[1][1][8] = 9;
    const SessionCommand invalid_shape{bad_controls};
    Session session;
    CHECK(session.prepare(profile, {48000.0, kRecoveryFrames, 37, kInitialFrame}) == SessionStatus::Ok);
    CHECK(session.start() == SessionStatus::Ok);
    Shared shared;
    shared.initial_snapshot = read_idle(session);
    std::atomic<std::uint64_t> requested{0};
    std::atomic<std::uint64_t> entered{0};
    std::atomic<std::uint64_t> permitted{0};
    std::atomic<std::uint64_t> completed{0};
    const Oracle oracle{controls, false, kRecoveryFrames};
    std::array<std::thread, kReaders> readers;
    for (std::size_t index = 0; index < readers.size(); ++index) {
        readers[index] = std::thread(observe, std::cref(session), std::ref(shared),
                                    std::cref(oracle), std::ref(counts.recovery_readers[index]));
    }
    std::thread audio([&] {
        std::array<float, 2 * kRecoveryFrames> output{};
        shared.ready.fetch_add(1, std::memory_order_release);
        while (!shared.begin.load(std::memory_order_acquire)) std::this_thread::yield();
        std::uint64_t done = 0;
        while (!shared.finish.load(std::memory_order_acquire)) {
            const auto ticket = requested.load(std::memory_order_acquire);
            if (ticket == done) {
                std::this_thread::yield();
                continue;
            }
            // Ready does not mean render has captured its queue prefix. The
            // first two recovery epochs deliberately hold this public-call
            // boundary; every other callback is already permitted.
            entered.store(ticket, std::memory_order_release);
            while (permitted.load(std::memory_order_acquire) < ticket) {
                deadline.check();
                std::this_thread::yield();
            }
            shared.audio_active.store(true, std::memory_order_release);
            const auto result = session.render(kRecoveryFrames, output);
            shared.audio_active.store(false, std::memory_order_release);
            ++counts.recovery_callbacks;
            if (!result.ok() || result.frames_rendered != kRecoveryFrames ||
                !std::all_of(output.begin(), output.end(), [](float v) { return std::isfinite(v); })) {
                shared.audio_failed.store(true, std::memory_order_release);
                return;
            }
            done = ticket;
            completed.store(done, std::memory_order_release);
        }
    });
    begin_workers(shared, deadline);
    const auto wait_for = [&](const std::atomic<std::uint64_t>& counter, std::uint64_t ticket) {
        while (counter.load(std::memory_order_acquire) < ticket) {
            deadline.check();
            CHECK(!shared.audio_failed.load(std::memory_order_acquire));
            std::this_thread::yield();
        }
    };
    std::uint64_t ticket = 0;
    const auto render_once = [&] {
        permitted.store(++ticket, std::memory_order_release);
        requested.store(ticket, std::memory_order_release);
        wait_for(completed, ticket);
        return read_idle(session);
    };
    const auto post = [&](const SessionCommand& command) {
        const auto result = session.post(command);
        CHECK(result.ok() && result.sequence == counts.accepted + 1);
        ++counts.accepted;
        return result.sequence;
    };
    for (std::size_t epoch = 0; epoch < kEpochs; ++epoch) {
        deadline.check();
        const auto invalid = session.post(invalid_shape);
        CHECK(invalid.status == SessionStatus::InvalidCommand && invalid.sequence == 0);
        ++counts.producer_rejected;
        post(controls[0]);
        for (const auto& command : held_commands) post(command);
        counts.applied += 5;
        const auto held = render_once();
        CHECK(held.controls == controls[0] && held.resolved_sequence == counts.accepted);
        CHECK(held.held_keys[0][24] && held.held_keys[1][36]); // literal MIDI 60/72
        CHECK(held.held_pedals[12] && held.held_pedals[24]);
        const auto applied_before = counts.applied;
        const auto discarded_before = counts.discarded;
        const auto precharge_sequence = counts.accepted;
        std::uint64_t invalid_sequence = 0;
        const bool overflow = epoch % 2 == 0;
        // Four explicit schedules prove both sides of the recovery boundary.
        // The other sixty epochs retain genuinely concurrent late posting;
        // no particular outcome of that race is a portable requirement.
        if (overflow) {
            for (const auto& command : release_commands) post(command);
            for (const auto& command : late_commands) post(command);
            for (std::size_t index = 6; index < kSessionCommandCapacity; ++index) {
                post(controls[index % 2]);
            }
            const auto full = session.post(release_commands[0]);
            CHECK(full.status == SessionStatus::QueueFull && full.sequence == 0);
            ++counts.overflows;
            const auto blocked = session.post(late_commands[0]);
            CHECK(blocked.status == SessionStatus::RecoveryPending && blocked.sequence == 0);
            ++counts.recovery_pending;
        } else {
            // Existing-ID duplicates exercise real ownership work before the
            // invalid payload, leaving time for admission to race closure.
            for (std::size_t index = 0; index < 95; ++index) post(held_commands[index % 4]);
            post(controls[1]);
            invalid_sequence = post(invalid_payload);
            for (const auto& command : release_commands) post(command);
            for (const auto& command : late_commands) post(command);
            post(controls[0]);
        }
        const auto prefix_end = counts.accepted;
        const bool before_render = epoch < kControlledRecoveryEpochs / 2;
        const bool after_render = !before_render && epoch < kControlledRecoveryEpochs;
        std::array<std::uint64_t, kLatePosts> late_sequences{};
        std::uint64_t late_pending = 0;
        ++ticket;
        if (!before_render) permitted.store(ticket, std::memory_order_release);
        requested.store(ticket, std::memory_order_release);
        wait_for(entered, ticket);
        if (after_render) wait_for(completed, ticket);
        for (std::size_t index = 0; index < kLatePosts; ++index) {
            const auto result = session.post(late_commands[index % 2]);
            if (result.ok()) {
                CHECK(result.sequence == counts.accepted + 1);
                late_sequences[index] = ++counts.accepted;
            } else {
                CHECK(result.status == SessionStatus::RecoveryPending && result.sequence == 0);
                ++counts.recovery_pending;
                ++late_pending;
            }
        }
        if (before_render) permitted.store(ticket, std::memory_order_release);
        wait_for(completed, ticket);
        const auto recovered = read_idle(session);
        CHECK(no_holds(recovered));
        CHECK(recovered.recovery_count == epoch + 1);
        CHECK(recovered.resolved_sequence >= prefix_end && recovered.resolved_sequence <= counts.accepted);
        CHECK(recovered.controls == controls[overflow ? 0 : 1]);
        if (overflow) {
            CHECK(recovered.last_applied_sequence == precharge_sequence);
            CHECK(recovered.resolved_sequence == prefix_end);
            counts.discarded += kSessionCommandCapacity;
        } else {
            CHECK(recovered.last_applied_sequence == invalid_sequence - 1);
            ++counts.consumer_rejected;
            counts.applied += 96;
            counts.discarded += recovered.resolved_sequence - invalid_sequence;
        }
        std::uint64_t after_ack = 0;
        std::uint64_t late_discarded = 0;
        for (const auto sequence : late_sequences) {
            if (sequence == 0) continue;
            if (sequence <= recovered.resolved_sequence) ++late_discarded;
            else ++after_ack;
        }
        CHECK(late_pending + late_discarded + after_ack == kLatePosts);
        if (before_render) {
            CHECK(late_pending == (overflow ? kLatePosts : 0));
            CHECK(late_discarded == (overflow ? 0 : kLatePosts));
            CHECK(after_ack == 0);
            counts.before_render_pending += late_pending;
            counts.before_render_discarded += late_discarded;
        } else if (after_render) {
            CHECK(late_pending == 0 && late_discarded == 0 && after_ack == kLatePosts);
            counts.after_render_accepted += after_ack;
        } else {
            counts.raced_pending += late_pending;
            counts.raced_discarded += late_discarded;
            counts.post_acknowledgment += after_ack;
        }
        CHECK(recovered.discarded_commands == counts.discarded);
        CHECK(recovered.queue_overflows == counts.overflows);
        CHECK(recovered.rejected_commands == counts.consumer_rejected + counts.producer_rejected);
        CHECK(recovered.resolved_sequence == counts.applied + counts.consumer_rejected + counts.discarded);
        CHECK(counts.applied - applied_before == (overflow ? 0 : 96));
        CHECK(counts.discarded > discarded_before);
        // An accepted sequence above the acknowledgment belongs to the new
        // epoch. It is valid input, so drain it with a final FIFO Panic.
        post(Panic{});
        counts.applied += after_ack + 1;
        const auto drained = render_once();
        CHECK(no_holds(drained) && drained.resolved_sequence == counts.accepted);
        CHECK(drained.last_applied_sequence == counts.accepted);
        CHECK(counts.accepted == counts.applied + counts.consumer_rejected + counts.discarded);
        const auto later = render_once();
        CHECK(no_holds(later) && later.controls == recovered.controls);
        CHECK(later.resolved_sequence == drained.resolved_sequence);
        CHECK(later.recovery_count == recovered.recovery_count);
    }
    finish_workers(session, shared, audio, readers, counts.recovery_readers, deadline);
    CHECK(counts.before_render_pending == kLatePosts);
    CHECK(counts.before_render_discarded == kLatePosts);
    CHECK(counts.after_render_accepted == 2 * kLatePosts);
    CHECK(counts.raced_pending + counts.raced_discarded + counts.post_acknowledgment ==
          (kEpochs - kControlledRecoveryEpochs) * kLatePosts);
    CHECK(counts.recovery_pending == kEpochs / 2 + counts.before_render_pending + counts.raced_pending);
    CHECK(read_idle(session).recovery_count == kEpochs);
    quiescent_finish(session, counts.accepted);
}

void test_active_overflow(const RuntimeProfile& profile, const Deadline& deadline, Counts& counts) {
    const std::array controls{pattern(false), pattern(true)};
    const std::array held_commands{
        manual(HostNoteKind::On, 0, 1, 60, 100),
        manual(HostNoteKind::On, 1, 2, 72, 101),
        pedal(PedalNoteKind::On, 0, 1, 13, 102),
        pedal(PedalNoteKind::On, 1, 2, 25, 103)};
    const std::array releases{
        manual(HostNoteKind::Off, 0, 1, 60, 100),
        pedal(PedalNoteKind::Off, 0, 1, 13, 102),
        manual(HostNoteKind::Off, 1, 2, 72, 101),
        pedal(PedalNoteKind::Off, 1, 2, 25, 103)};
    const std::array late_commands{
        manual(HostNoteKind::On, 0, 3, 61, 300),
        pedal(PedalNoteKind::On, 1, 4, 24, 301)};
    std::array<SessionCommand, 2 * kSessionCommandCapacity + 1> burst;
    std::array<ControlSnapshot, burst.size()> expected;
    auto installed = controls[0];
    for (std::size_t index = 0; index < burst.size(); ++index) {
        if (index < releases.size()) burst[index] = releases[index];
        else if (index % 3 == 0) {
            burst[index] = controls[1];
            installed = controls[1];
        } else burst[index] = late_commands[index % 2];
        expected[index] = installed;
    }
    Session session;
    CHECK(session.prepare(profile, {48000.0, kFlightFrames, 37, kInitialFrame}) == SessionStatus::Ok);
    CHECK(session.start() == SessionStatus::Ok);
    Shared shared;
    shared.initial_snapshot = read_idle(session);
    std::atomic<std::uint64_t> requested{0};
    std::atomic<std::uint64_t> entered{0};
    std::atomic<std::uint64_t> completed{0};
    const Oracle oracle{controls, false, kFlightFrames, false};
    std::array<std::thread, kReaders> readers;
    for (std::size_t index = 0; index < readers.size(); ++index) {
        readers[index] = std::thread(observe, std::cref(session), std::ref(shared),
                                    std::cref(oracle), std::ref(counts.active_readers[index]));
    }
    std::thread audio([&] {
        std::array<float, 2 * kFlightFrames> output{};
        shared.ready.fetch_add(1, std::memory_order_release);
        while (!shared.begin.load(std::memory_order_acquire)) std::this_thread::yield();
        std::uint64_t done = 0;
        while (!shared.finish.load(std::memory_order_acquire)) {
            const auto ticket = requested.load(std::memory_order_acquire);
            if (ticket == done) {
                std::this_thread::yield();
                continue;
            }
            shared.audio_active.store(true, std::memory_order_release);
            entered.store(ticket, std::memory_order_release);
            const auto result = session.render(kFlightFrames, output);
            shared.audio_active.store(false, std::memory_order_release);
            ++counts.active_callbacks;
            if (!result.ok() || result.frames_rendered != kFlightFrames ||
                !std::all_of(output.begin(), output.end(), [](float v) { return std::isfinite(v); })) {
                shared.audio_failed.store(true, std::memory_order_release);
                return;
            }
            done = ticket;
            completed.store(done, std::memory_order_release);
        }
    });
    const auto wait_for = [&](const std::atomic<std::uint64_t>& counter, std::uint64_t value) {
        while (counter.load(std::memory_order_acquire) < value) {
            deadline.check();
            CHECK(!shared.audio_failed.load(std::memory_order_acquire));
            std::this_thread::yield();
        }
    };
    begin_workers(shared, deadline);
    std::uint64_t ticket = 0;
    const auto render_once = [&] {
        requested.store(++ticket, std::memory_order_release);
        wait_for(completed, ticket);
        return read_idle(session);
    };
    const auto post = [&](const SessionCommand& command) {
        const auto result = session.post(command);
        CHECK(result.ok() && result.sequence == counts.active_accepted + 1);
        ++counts.active_accepted;
    };
    for (std::size_t epoch = 0; epoch < kFlights; ++epoch) {
        deadline.check();
        post(controls[0]);
        for (const auto& command : held_commands) post(command);
        counts.active_applied += 5;
        const auto precharged = render_once();
        CHECK(precharged.resolved_sequence == counts.active_accepted);
        CHECK(precharged.held_keys[0][24] && precharged.held_keys[1][36]);
        CHECK(precharged.held_pedals[12] && precharged.held_pedals[24]);
        const auto before = counts.active_accepted;
        requested.store(++ticket, std::memory_order_release);
        wait_for(entered, ticket);
        // One public after-call boundary proves pending overflow and recovery
        // on the next callback. The other fifteen rounds retain the race;
        // flag overlap and deferred race observations can both legally be zero.
        const bool after_callback = epoch == 0;
        if (after_callback) wait_for(completed, ticket);
        bool overflowed = false;
        bool active_overflow = false;
        for (const auto& command : burst) {
            const bool active = shared.audio_active.load(std::memory_order_acquire);
            const auto result = session.post(command);
            if (result.ok()) {
                CHECK(result.sequence == counts.active_accepted + 1);
                ++counts.active_accepted;
            } else {
                CHECK(result.status == SessionStatus::QueueFull && result.sequence == 0);
                active_overflow = active && shared.audio_active.load(std::memory_order_acquire);
                counts.active_overflows += active_overflow ? 1U : 0U;
                overflowed = true;
                break;
            }
        }
        CHECK(overflowed); // A single captured prefix cannot consume an unbounded burst.
        wait_for(completed, ticket);
        const auto flight = read_idle(session);
        CHECK(flight.last_applied_sequence >= before && flight.last_applied_sequence <= counts.active_accepted);
        const auto applied = flight.last_applied_sequence - before;
        const auto expected_controls = applied == 0 ? controls[0] : expected[static_cast<std::size_t>(applied - 1)];
        CHECK(flight.controls == expected_controls);
        CHECK(flight.recovery_count == epoch || flight.recovery_count == epoch + 1);
        if (after_callback) {
            CHECK(!active_overflow && applied == 0);
            CHECK(counts.active_accepted - before == kSessionCommandCapacity);
            CHECK(flight.recovery_count == epoch && flight.resolved_sequence == before);
            ++counts.controlled_deferred_overflows;
        }
        if (flight.recovery_count == epoch) {
            CHECK(flight.resolved_sequence < counts.active_accepted);
            if (active_overflow) ++counts.deferred_overflows;
            for (const auto& command : {releases[0], releases[1], late_commands[0], late_commands[1]}) {
                const auto blocked = session.post(command);
                CHECK(blocked.status == SessionStatus::RecoveryPending && blocked.sequence == 0);
            }
        }
        const auto recovered = render_once();
        counts.active_applied += applied;
        counts.active_discarded += counts.active_accepted - before - applied;
        CHECK(no_holds(recovered) && recovered.controls == flight.controls);
        CHECK(recovered.resolved_sequence == counts.active_accepted);
        CHECK(recovered.last_applied_sequence == flight.last_applied_sequence);
        CHECK(recovered.recovery_count == epoch + 1 && recovered.queue_overflows == epoch + 1);
        CHECK(recovered.discarded_commands == counts.active_discarded);
        CHECK(counts.active_accepted == counts.active_applied + counts.active_discarded);
    }
    finish_workers(session, shared, audio, readers, counts.active_readers, deadline);
    CHECK(counts.controlled_deferred_overflows == 1);
    quiescent_finish(session, counts.active_accepted);
}

void test_failed_read_preservation(const RuntimeProfile& profile, Counts& counts) {
    // Deterministic failure evidence supplements schedule-dependent busy reads.
    Session session({std::numeric_limits<std::uint64_t>::max(), 2});
    CHECK(session.prepare(profile, {48000.0, 1, 37, 0}) == SessionStatus::Ok);
    CHECK(session.start() == SessionStatus::Ok);
    const auto marker = read_idle(session);
    CHECK(session.render(0, {}).status == SessionStatus::SequenceExhausted);
    std::array<std::thread, kReaders> readers;
    std::array<std::uint64_t, kReaders> preserved{};
    for (std::size_t index = 0; index < readers.size(); ++index) {
        readers[index] = std::thread([&, index] {
            for (std::size_t attempt = 0; attempt < 128; ++attempt) {
                auto destination = marker;
                if (!session.read_snapshot(destination) && same_snapshot(destination, marker)) {
                    ++preserved[index];
                }
            }
        });
    }
    for (auto& reader : readers) reader.join();
    for (const auto value : preserved) {
        CHECK(value == 128);
        counts.preserved_exhausted_reads += value;
    }
}

} // namespace

int main() {
    const auto profile = load_test_profile();
    const Deadline deadline;
    test_watchdog_unwind_cleanup(deadline);
    // Off-callback watchdog also bounds a failed join, not only producer polls.
    JoiningThread watchdog([&deadline](StopToken stop) {
        while (!stop.stop_requested()) {
            deadline.check();
            std::this_thread::sleep_for(std::chrono::milliseconds(20));
        }
    });
    Counts counts;
    test_sustained_fifo(profile, deadline, counts);
    test_recovery_epochs(profile, deadline, counts);
    test_active_overflow(profile, deadline, counts);
    test_failed_read_preservation(profile, counts);
    watchdog.request_stop();
    std::cout << "Session concurrency: " << counts.ordered_posts << " ordered posts, "
              << counts.ordered_callbacks << " free callbacks, " << counts.overlapping_posts
              << " posts observed the callback activity flag; " << kEpochs << " recovery epochs, "
              << counts.recovery_callbacks << " recovery callbacks, " << counts.accepted
              << " accepted = " << counts.applied << " applied + " << counts.consumer_rejected
              << " rejected + " << counts.discarded << " discarded; " << counts.producer_rejected
              << " immediate rejects, " << counts.overflows << " overflows, "
              << counts.recovery_pending << " recovery-pending posts; "
              << counts.preserved_exhausted_reads << " exhausted reads preserved\n";
    std::cout << "Controlled recovery boundaries: " << kControlledRecoveryEpochs << " epochs, "
              << counts.before_render_pending << " pre-render posts pending, "
              << counts.before_render_discarded << " pre-render admitted posts discarded, "
              << counts.after_render_accepted << " post-render posts accepted after ack\n";
    std::cout << "Concurrent recovery schedules: " << kEpochs - kControlledRecoveryEpochs << " epochs, "
              << counts.raced_pending << " posts pending, " << counts.raced_discarded
              << " admitted posts discarded, " << counts.post_acknowledgment
              << " posts accepted after ack\n";
    std::cout << "Active overflow: " << kFlights << " rounds, " << counts.active_callbacks
              << " callbacks, " << counts.controlled_deferred_overflows
              << " controlled after-callback overflow deferred, " << counts.active_overflows
              << " QueueFull calls observed the activity flag, "
              << counts.deferred_overflows << " flagged recoveries deferred past that callback; "
              << counts.active_accepted << " accepted = " << counts.active_applied << " applied + "
              << counts.active_discarded << " discarded\n";
    for (std::size_t index = 0; index < kReaders; ++index) {
        for (const auto* stats : {&counts.ordered_readers[index], &counts.recovery_readers[index],
                                  &counts.active_readers[index]}) {
            const auto label = stats == &counts.ordered_readers[index] ? "free" :
                stats == &counts.recovery_readers[index] ? "recovery" : "active-overflow";
            std::cout << label
                      << " reader " << index << ": " << stats->successful << " coherent, "
                      << stats->busy << " busy preserved, " << stats->changes
                      << " distinct revisions, " << stats->active_reads << " activity-flag attempts, "
                      << stats->initial_revision << " -> " << stats->final_revision
                      << " exact publication checkpoints\n";
        }
    }
    return 0;
}
