#include "Session.h"
#include "TestSupport.h"
#include "hammond/ControlStateIO.h"

#include <array>
#include <atomic>
#include <bit>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <exception>
#include <iostream>
#include <span>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <thread>
#include <utility>
#include <vector>

namespace {

using namespace hammond;
using namespace hammond::standalone;

constexpr std::uint64_t kInitialFrame = 529;
constexpr std::uint64_t kInitialSequence = 4;
constexpr std::size_t kControlledRounds = 64;
constexpr std::size_t kBurstRestores = 1024;
constexpr std::size_t kRestores = kControlledRounds + kBurstRestores;
constexpr std::uint32_t kPositiveFrames = 17;

struct Counts {
    std::uint64_t callbacks{};
    std::uint64_t snapshots{};
    std::uint64_t busy_reads{};
    std::uint64_t saves{};
    std::uint64_t pending_checks{};
    std::uint64_t restores{};
    std::uint64_t hidden_fixed_observations{};
    std::uint64_t hidden_none_observations{};
    std::uint64_t queue_recoveries{};
    std::uint64_t discarded_restores{};
    std::uint64_t priming_samples{};
    std::uint64_t future_samples{};
    std::uint64_t audible_samples{};
    std::uint64_t rejections{};
} counts;

void require(bool condition, const char* message) {
    if (!condition) throw std::runtime_error(message);
}

[[nodiscard]] bool same_controls(const ControlSnapshot& left,
                                  const ControlSnapshot& right) {
    return left == right && std::bit_cast<std::uint64_t>(left.expression) ==
        std::bit_cast<std::uint64_t>(right.expression);
}

[[nodiscard]] bool same_snapshot(const SessionSnapshot& left,
                                  const SessionSnapshot& right) {
    return same_controls(left.controls, right.controls) &&
        left.held_keys == right.held_keys && left.held_pedals == right.held_pedals &&
        left.frame_clock == right.frame_clock && left.sample_rate == right.sample_rate &&
        std::bit_cast<std::uint32_t>(left.peak) == std::bit_cast<std::uint32_t>(right.peak) &&
        left.prepared == right.prepared && left.running == right.running &&
        left.publication_revision == right.publication_revision &&
        left.resolved_sequence == right.resolved_sequence &&
        left.last_applied_sequence == right.last_applied_sequence &&
        left.recovery_count == right.recovery_count &&
        left.queue_overflows == right.queue_overflows &&
        left.rejected_commands == right.rejected_commands &&
        left.discarded_commands == right.discarded_commands &&
        left.fault_flags == right.fault_flags && left.last_core_status == right.last_core_status;
}

// An independent sequence stamp changes every control region, including the
// last four drawbar bytes adjacent to the new fixed-mode bytes. Expression is
// a unique exactly representable stamp; no production packer or lookup creates
// any expected snapshot. Raw modes, route bits and remembered banks vary
// independently. The test is not an exhaustive 1,600-state matrix.
[[nodiscard]] ControlSnapshot stamp(std::size_t value) {
    ControlSnapshot result;
    for (std::size_t manual = 0; manual < 2; ++manual) {
        for (std::size_t bank = 0; bank < 2; ++bank) {
            for (std::size_t drawbar = 0; drawbar < 9; ++drawbar) {
                result.drawbars[manual][bank][drawbar] = static_cast<std::uint8_t>(
                    (value * 5 + value / 9 + manual * 4 + bank * 7 + drawbar * 3) % 9);
            }
        }
    }
    result.fixed_registrations = {static_cast<FixedRegistration>(value % 10),
        static_cast<FixedRegistration>((value * 7 + 3) % 10)};
    result.selected_banks = {static_cast<DrawbarBank>((value / 3) % 2),
        static_cast<DrawbarBank>((value / 5) % 2)};
    result.route_enabled = {(value / 2) % 2 == 0, value % 3 != 0};
    result.expression = value == 0 ? -0.0 : static_cast<double>(value) / 4096.0;
    result.percussion = {value % 2 != 0,
        static_cast<PercussionHarmonic>((value / 3) % 2),
        static_cast<PercussionVolume>((value / 5) % 2),
        static_cast<PercussionDecay>((value / 7) % 2)};
    result.pedal_drawbars = {static_cast<std::uint8_t>((value * 2 + 1) % 9),
        static_cast<std::uint8_t>((value * 4 + 7) % 9)};
    require(is_valid_control_snapshot(result), "test stamp is invalid");
    return result;
}

[[nodiscard]] SessionCommand note(std::uint8_t bus, std::uint8_t channel,
                                   std::uint8_t pitch, std::int32_t id) {
    return PerformanceInputEvent{HostNoteEvent{0, HostNoteKind::On,
        bus, channel, pitch, 100, id}};
}

[[nodiscard]] SessionCommand pedal() {
    return PerformanceInputEvent{PedalNoteEvent{0, PedalNoteKind::On,
        1, 3, PedalId{7}, 100, 77}};
}

[[nodiscard]] SessionCommand selector(Manual manual, unsigned value) {
    return PerformanceInputEvent{Event{0, EventType::SelectPreset,
        manual, 0, static_cast<double>(value)}};
}

[[nodiscard]] SessionSnapshot read(const Session& session) {
    SessionSnapshot result;
    require(session.read_snapshot(result), "quiescent snapshot read failed");
    return result;
}

void submit(Session& session, const SessionCommand& command) {
    require(session.post(command).ok(), "expected command admission");
}

void setup(Session& session, const RuntimeProfile& profile,
           double rate, const ControlSnapshot& controls) {
    require(session.prepare(profile, {rate, 64, 123, kInitialFrame}) == SessionStatus::Ok,
        "prepare failed");
    require(session.start() == SessionStatus::Ok, "start failed");
    submit(session, controls);
    submit(session, note(0, 0, 60, 11));
    submit(session, note(1, 2, 67, 22));
    submit(session, pedal());
    require(session.render(0, {}).ok(), "initial zero callback failed");
    require(read(session).last_applied_sequence == kInitialSequence,
        "initial command sequence differs");
}

void check_holds(const SessionSnapshot& snapshot, bool present) {
    for (std::size_t manual = 0; manual < 2; ++manual) {
        for (std::size_t key = 0; key < kManualKeyCount; ++key) {
            const auto expected = present && key == (manual == 0 ? 24U : 31U);
            require(snapshot.held_keys[manual][key] == expected,
                "restore or publication changed a manual owner");
        }
    }
    for (std::size_t key = 0; key < kPedalCount; ++key) {
        require(snapshot.held_pedals[key] == (present && key == 6),
            "restore or publication changed a pedal owner");
    }
}

void check_effective(const ControlSnapshot& controls) {
    for (std::size_t manual = 0; manual < 2; ++manual) {
        const unsigned fixed = static_cast<unsigned>(controls.fixed_registrations[manual]);
        const unsigned wanted = !controls.route_enabled[manual] ? 0U : fixed != 0 ? fixed :
            controls.selected_banks[manual] == DrawbarBank::A ? 10U : 11U;
        auto selection = PresetSelection::Cancel;
        require(control_preset_selection(controls, static_cast<Manual>(manual), selection),
            "copied controls failed effective selection validation");
        require(static_cast<unsigned>(selection) == wanted,
            "raw fixed memory was confused with effective selection");
    }
}

void check_saved_copy(const ControlSnapshot& controls) {
    // Only the independent reader owns this allocating IO. The callback has
    // already published a copied value and remains free to continue rendering.
    constexpr std::array<std::string_view, 10> names{
        "none", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A"};
    std::string text;
    std::string error;
    require(serialize_controls(controls, text, error), "copied controls could not save");
    require(text.starts_with("B3CONTROLS4\nregistration_catalog atlas-chapel-nominal-v1 sha256 "
        "c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf\n"),
        "saved copy omitted the independent state4 catalog identity");
    for (std::size_t manual = 0; manual < 2; ++manual) {
        const std::string expected = std::string("manual ") + (manual == 0 ? "upper" : "lower") +
            " selected " + (controls.selected_banks[manual] == DrawbarBank::A ? "A" : "B") +
            " fixed_registration " + std::string(names[static_cast<std::size_t>(
                controls.fixed_registrations[manual])]) + " route_enabled " +
            (controls.route_enabled[manual] ? "1\n" : "0\n");
        require(text.find(expected) != std::string::npos,
            "saved copy lost hidden fixed mode or remembered bank");
    }
    std::istringstream input(text);
    ControlSnapshot restored;
    require(parse_controls(input, restored, error), "saved copy could not parse");
    require(same_controls(controls, restored), "saved copied controls changed on reload");
}

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
    [[nodiscard]] bool joinable() const noexcept { return worker_.joinable(); }
    void join() { worker_.join(); }
private:
    std::atomic<bool> requested_{false}; // Must outlive the thread and its token.
    std::thread worker_;
};

void concurrent_publication(const RuntimeProfile& profile, double rate) {
    std::vector<ControlSnapshot> expected;
    expected.reserve(kRestores + 1);
    for (std::size_t index = 0; index <= kRestores; ++index) expected.push_back(stamp(index));
    Session session;
    setup(session, profile, rate, expected[0]);
    const auto initial = read(session);
    require(initial.publication_revision == 6, "unexpected initial publication revision");
    std::atomic<bool> stop{false}, failed{false}, reader_ready{false}, free_run{false};
    std::atomic<std::uint64_t> requested{0}, completed{0}, observed{kInitialSequence};
    Counts audio_counts;
    Counts reader_counts;
    std::exception_ptr audio_error, reader_error;

    JoiningThread audio([&](StopToken token) {
        try {
            std::array<float, kPositiveFrames * 2> buffer{};
            while (!stop.load(std::memory_order_acquire) && !token.stop_requested()) {
                const auto ticket = requested.load(std::memory_order_acquire);
                const bool continuous = free_run.load(std::memory_order_acquire);
                if (!continuous && ticket <= completed.load(std::memory_order_relaxed)) {
                    std::this_thread::yield();
                    continue;
                }
                const auto frames = audio_counts.callbacks % 2 == 0 ? kPositiveFrames : 0U;
                const auto result = session.render(frames,
                    {buffer.data(), static_cast<std::size_t>(frames) * 2});
                require(result.ok() && result.frames_rendered == frames,
                    "concurrent audio callback rejected");
                for (std::size_t index = 0; index < frames; ++index) {
                    require(std::isfinite(buffer[index * 2]) &&
                        std::bit_cast<std::uint32_t>(buffer[index * 2]) ==
                        std::bit_cast<std::uint32_t>(buffer[index * 2 + 1]),
                        "concurrent callback output is nonfinite or not dual mono");
                }
                ++audio_counts.callbacks;
                if (!continuous) completed.store(ticket, std::memory_order_release);
            }
        } catch (...) {
            audio_error = std::current_exception();
            failed.store(true, std::memory_order_release);
            stop.store(true, std::memory_order_release);
        }
    });
    JoiningThread reader([&](StopToken token) {
        try {
            SessionSnapshot previous = initial;
            std::uint64_t last_saved = 0;
            while (!stop.load(std::memory_order_acquire) && !token.stop_requested()) {
                auto current = previous;
                if (!session.read_snapshot(current)) {
                    require(same_snapshot(current, previous), "busy read modified destination");
                    ++reader_counts.busy_reads;
                    continue;
                }
                require(current.publication_revision >= previous.publication_revision &&
                    current.publication_revision % 2 == 0,
                    "publication revision regressed or was odd");
                require(current.resolved_sequence >= previous.resolved_sequence &&
                    current.resolved_sequence >= kInitialSequence &&
                    current.resolved_sequence <= kInitialSequence + kRestores &&
                    current.last_applied_sequence == current.resolved_sequence,
                    "snapshot sequence was torn or regressed");
                const auto index = static_cast<std::size_t>(
                    current.resolved_sequence - kInitialSequence);
                require(same_controls(current.controls, expected[index]),
                    "atomic snapshot did not match complete sequence oracle");
                const auto callback_count = current.publication_revision / 2 - 3;
                require(current.frame_clock == kInitialFrame +
                    ((callback_count + 1) / 2) * kPositiveFrames,
                    "frame clock and publication revision were incoherent");
                require(current.sample_rate == rate && current.prepared && current.running &&
                    std::isfinite(current.peak) && current.peak >= 0.0F,
                    "snapshot lifecycle, rate or peak was invalid");
                require(current.recovery_count == 0 && current.queue_overflows == 0 &&
                    current.rejected_commands == 0 && current.discarded_commands == 0 &&
                    current.fault_flags == 0 && current.last_core_status == Status::Ok,
                    "ordinary publication unexpectedly recovered or faulted");
                check_holds(current, true);
                check_effective(current.controls);
                if (current.resolved_sequence != previous.resolved_sequence) {
                    for (std::size_t manual = 0; manual < 2; ++manual) {
                        if (!current.controls.route_enabled[manual]) {
                            if (current.controls.fixed_registrations[manual] == FixedRegistration::None)
                                ++reader_counts.hidden_none_observations;
                            else ++reader_counts.hidden_fixed_observations;
                        }
                    }
                }
                if (index != 0 && index % 16 == 0 && current.resolved_sequence != last_saved) {
                    check_saved_copy(current.controls);
                    last_saved = current.resolved_sequence;
                    ++reader_counts.saves;
                }
                previous = current;
                ++reader_counts.snapshots;
                observed.store(current.resolved_sequence, std::memory_order_release);
                reader_ready.store(true, std::memory_order_release);
            }
        } catch (...) {
            reader_error = std::current_exception();
            failed.store(true, std::memory_order_release);
            stop.store(true, std::memory_order_release);
        }
    });

    const auto deadline = std::chrono::steady_clock::now() + std::chrono::seconds(20);
    const auto wait_until = [&](auto predicate) {
        while (!predicate()) {
            require(!failed.load(std::memory_order_acquire), "publication worker failed");
            require(std::chrono::steady_clock::now() < deadline,
                "concurrency test exceeded its finite process guard");
            std::this_thread::yield();
        }
    };
    const auto join = [&] {
        stop.store(true, std::memory_order_release);
        if (audio.joinable()) audio.join();
        if (reader.joinable()) reader.join();
    };
    try {
        wait_until([&] { return reader_ready.load(std::memory_order_acquire); });
        for (std::size_t index = 1; index <= kControlledRounds; ++index) {
            const auto before = read(session);
            const auto admitted = session.post(expected[index]);
            require(admitted.ok() && admitted.sequence == kInitialSequence + index,
                "controlled restore sequence differs");
            require(same_snapshot(read(session), before),
                "queued restore was presented as applied before callback");
            ++counts.pending_checks;
            requested.store(index, std::memory_order_release);
            wait_until([&] { return completed.load(std::memory_order_acquire) >= index; });
            wait_until([&] { return observed.load(std::memory_order_acquire) >= admitted.sequence; });
            require(same_controls(read(session).controls, expected[index]),
                "acknowledged controlled restore differs");
        }
        free_run.store(true, std::memory_order_release);
        for (std::size_t index = kControlledRounds + 1; index <= kRestores; ++index) {
            // Reader acknowledgment provides a conservative credit bound. The
            // producer never waits inside Session and never violates its one-
            // writer rule; consumer prefix lengths remain scheduler-dependent.
            wait_until([&] { return kInitialSequence + index <=
                observed.load(std::memory_order_acquire) + 192; });
            const auto admitted = session.post(expected[index]);
            require(admitted.ok() && admitted.sequence == kInitialSequence + index,
                "bounded burst restore sequence differs");
        }
        wait_until([&] { return observed.load(std::memory_order_acquire) ==
            kInitialSequence + kRestores; });
        join();
    } catch (...) {
        join();
        if (audio_error) std::rethrow_exception(audio_error);
        if (reader_error) std::rethrow_exception(reader_error);
        throw;
    }
    if (audio_error) std::rethrow_exception(audio_error);
    if (reader_error) std::rethrow_exception(reader_error);
    require(reader_counts.snapshots >= kControlledRounds + 1 && reader_counts.saves >= 4 &&
        reader_counts.hidden_fixed_observations != 0 && reader_counts.hidden_none_observations != 0,
        "concurrency fixture did not observe required copied states");
    const auto final = read(session);
    require(same_controls(final.controls, expected.back()) &&
        final.resolved_sequence == kInitialSequence + kRestores,
        "final burst restore was not acknowledged");
    check_holds(final, true);
    require(session.stop() == SessionStatus::Ok, "quiescent stop failed");
    const auto stopped = read(session);
    require(same_controls(stopped.controls, expected.back()), "stop lost raw fixed controls");
    check_holds(stopped, false);
    counts.callbacks += audio_counts.callbacks;
    counts.snapshots += reader_counts.snapshots;
    counts.busy_reads += reader_counts.busy_reads;
    counts.saves += reader_counts.saves;
    counts.hidden_fixed_observations += reader_counts.hidden_fixed_observations;
    counts.hidden_none_observations += reader_counts.hidden_none_observations;
    counts.restores += kRestores;
}

void compare_audio(Session& actual, Session& reference, std::uint32_t frames,
                   bool priming = false) {
    std::array<float, 128> left{}, right{};
    require(actual.render(frames, {left.data(), static_cast<std::size_t>(frames) * 2}).ok() &&
        reference.render(frames, {right.data(), static_cast<std::size_t>(frames) * 2}).ok(),
        "future comparison render failed");
    for (std::size_t index = 0; index < static_cast<std::size_t>(frames) * 2; ++index) {
        require(std::bit_cast<std::uint32_t>(left[index]) == std::bit_cast<std::uint32_t>(right[index]),
            "rejected or discarded controls changed future audio");
        if (priming) ++counts.priming_samples;
        else ++counts.future_samples;
        if (left[index] != 0.0F) ++counts.audible_samples;
    }
}

void queue_recovery(const RuntimeProfile& profile, double rate, bool hidden_fixed) {
    auto retained = stamp(57);
    retained.route_enabled = {false, false};
    retained.selected_banks = {DrawbarBank::B, DrawbarBank::A};
    retained.fixed_registrations = hidden_fixed
        ? std::array{FixedRegistration::A, FixedRegistration::CSharp}
        : std::array{FixedRegistration::None, FixedRegistration::None};
    retained.expression = 0.75;
    Session actual, reference;
    setup(actual, profile, rate, retained);
    setup(reference, profile, rate, retained);
    compare_audio(actual, reference, 64, true);

    auto before = read(actual);
    auto invalid = retained;
    invalid.fixed_registrations[1] = static_cast<FixedRegistration>(255);
    const auto invalid_result = actual.post(invalid);
    require(invalid_result.status == SessionStatus::InvalidCommand && invalid_result.sequence == 0,
        "invalid hidden fixed snapshot was admitted");
    require(same_snapshot(read(actual), before), "rejected snapshot changed published state");
    ++counts.rejections;
    compare_audio(actual, reference, 17);
    before = read(actual);
    require(same_controls(before.controls, retained), "rejected restore changed live controls");
    check_holds(before, true);
    for (std::size_t index = 0; index < kSessionCommandCapacity; ++index) {
        const auto queued = actual.post(stamp(index + 1));
        require(queued.ok() && queued.sequence == kInitialSequence + index + 1,
            "full ring did not admit its exact capacity");
    }
    const auto overflow = actual.post(selector(Manual::Upper, 11));
    require(overflow.status == SessionStatus::QueueFull && overflow.sequence == 0,
        "full ring did not reject selector");
    const auto pending = actual.post(retained);
    require(pending.status == SessionStatus::RecoveryPending && pending.sequence == 0,
        "full ring allowed restore before recovery acknowledgment");
    counts.rejections += 2;
    require(same_snapshot(read(actual), before), "queued controls leaked into applied snapshot");
    std::array<float, 4> sentinel{7.0F, -3.0F, 9.0F, -11.0F};
    const auto untouched = sentinel;
    require(actual.render(3, sentinel).status == SessionStatus::InvalidBuffer && sentinel == untouched,
        "invalid callback consumed or overwrote output");
    require(same_snapshot(read(actual), before), "invalid callback published pending controls");
    ++counts.rejections;

    require(actual.render(0, {}).ok(), "queue recovery failed");
    submit(reference, Panic{});
    require(reference.render(0, {}).ok(), "reference panic failed");
    const auto recovered = read(actual);
    require(same_controls(recovered.controls, retained), "discarded restore changed hidden memory");
    require(recovered.resolved_sequence == kInitialSequence + kSessionCommandCapacity &&
        recovered.last_applied_sequence == kInitialSequence && recovered.recovery_count == 1 &&
        recovered.queue_overflows == 1 && recovered.discarded_commands == kSessionCommandCapacity &&
        recovered.rejected_commands == 1 && recovered.frame_clock == before.frame_clock,
        "full-ring recovery acknowledgment differs");
    check_holds(recovered, false); // Queue overflow specifies GLOBAL owner recovery.
    check_effective(recovered.controls);
    check_saved_copy(recovered.controls);
    ++counts.queue_recoveries;
    counts.discarded_restores += kSessionCommandCapacity;

    for (auto* session : {&actual, &reference}) {
        submit(*session, selector(Manual::Upper, 11));
        submit(*session, selector(Manual::Lower, 8));
        submit(*session, note(0, 0, 72, 91));
        submit(*session, note(1, 2, 55, 92));
        submit(*session, pedal());
    }
    const auto audible_before_resume = counts.audible_samples;
    for (const auto frames : {1U, 17U, 63U, 0U, 29U}) compare_audio(actual, reference, frames);
    require(counts.audible_samples > audible_before_resume,
        "future comparison after recovery was entirely silent");
    const auto resumed = read(actual);
    require(resumed.controls.fixed_registrations ==
        std::array{FixedRegistration::None, FixedRegistration::GSharp},
        "resumed bank/fixed selection changed identities");
    require(same_controls(resumed.controls, read(reference).controls),
        "resumed controls differ after queue recovery");
    require(actual.stop() == SessionStatus::Ok && reference.stop() == SessionStatus::Ok,
        "queue-case stop failed");
}

} // namespace

int main() {
    try {
        const auto profile = load_test_profile();
        for (const double rate : {44100.0, 48000.0, 96000.0}) {
            concurrent_publication(profile, rate);
            queue_recovery(profile, rate, false);
            queue_recovery(profile, rate, true);
        }
        std::cout << "preset Session concurrency: rates=3 controlled_pending=" << counts.pending_checks
                  << " restored_snapshots=" << counts.restores << " callbacks=" << counts.callbacks
                  << " observer_reads=" << counts.snapshots << " busy_reads=" << counts.busy_reads
                  << " copied_state4_saves=" << counts.saves
                  << " hidden_fixed_observations=" << counts.hidden_fixed_observations
                  << " hidden_none_observations=" << counts.hidden_none_observations
                  << " queue_recoveries=" << counts.queue_recoveries
                  << " discarded_restores=" << counts.discarded_restores
                  << " rejected_calls=" << counts.rejections
                  << " exact_priming_stereo_samples=" << counts.priming_samples
                  << " exact_future_stereo_samples=" << counts.future_samples
                  << " audible_stereo_samples=" << counts.audible_samples << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "preset Session concurrency failed: " << error.what() << '\n';
        return 1;
    }
}
