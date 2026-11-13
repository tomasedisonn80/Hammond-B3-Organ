#include "NativeHarness.h"

#include "hammond/ConsoleModel.h"
#include "hammond/Engine.h"
#include "hammond/Profile.h"

#include <array>
#include <atomic>
#include <bit>
#include <chrono>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <exception>
#include <fstream>
#include <iostream>
#include <span>
#include <stdexcept>
#include <stop_token>
#include <string>
#include <thread>
#include <vector>

namespace {

using namespace hammond;
namespace nt = hammond::native_test;
namespace sv = Steinberg::Vst;
using Steinberg::kResultOk;

constexpr std::uint32_t kMaximumFrames = 512;
constexpr std::size_t kCoordinatedRounds = 8;
constexpr std::size_t kAcceptedStressLoads = 1024;
constexpr std::uint64_t kPublicationOnlySaves = 1024;
constexpr std::uint32_t kAudioGenerationCount = 4096;

struct Counters {
    std::uint64_t callbacks{0};
    std::uint64_t rejected_callbacks{0};
    std::uint64_t zero_callbacks{0};
    std::uint64_t compared_frames{0};
    std::uint64_t audible_frames{0};
    std::uint64_t accepted_loads{0};
    std::uint64_t full_loads{0};
    std::uint64_t malformed_loads{0};
    std::uint64_t successful_saves{0};
    std::uint64_t busy_saves{0};
    std::uint64_t pending_saves{0};
    std::uint64_t published_saves{0};
    std::uint64_t future_frames{0};
};

// The pattern and literal IDs below are independent of StateExchange's cell
// encoding and of ParameterBridge/HostTimeline. Every saved field is checked.
ControlSnapshot pattern(std::uint32_t generation, bool audio) {
    ControlSnapshot result{};
    for (std::size_t manual = 0; manual < 2; ++manual) {
        for (std::size_t bank = 0; bank < 2; ++bank) {
            for (std::size_t drawbar = 0; drawbar < 9; ++drawbar) {
                result.drawbars[manual][bank][drawbar] = static_cast<std::uint8_t>(
                    (generation + 3U * manual + 2U * bank + drawbar) % 4U + 1U);
            }
        }
        result.selected_banks[manual] = static_cast<DrawbarBank>((generation + manual) % 2U);
        result.route_enabled[manual] = audio || (generation + manual) % 3U != 0;
    }
    result.expression = audio ? 0.5 + static_cast<double>(generation + 1U) / 32768.0
                              : 0.125 + static_cast<double>(generation + 1U) / 65536.0;
    result.percussion.enabled = (generation & 1U) != 0;
    result.percussion.harmonic = static_cast<PercussionHarmonic>((generation >> 1U) & 1U);
    result.percussion.volume = static_cast<PercussionVolume>((generation >> 2U) & 1U);
    result.percussion.decay = static_cast<PercussionDecay>((generation >> 3U) & 1U);
    result.pedal_drawbars[0] = static_cast<std::uint8_t>(generation % 4U + 1U);
    result.pedal_drawbars[1] = static_cast<std::uint8_t>((generation / 3U) % 4U + 1U);
    return result;
}

bool same_snapshot(const ControlSnapshot& a, const ControlSnapshot& b) {
    return a == b && std::bit_cast<std::uint64_t>(a.expression) ==
                         std::bit_cast<std::uint64_t>(b.expression);
}

std::uint32_t decode_audio_generation(const ControlSnapshot& snapshot) {
    nt::require(snapshot.expression > 0.5 && snapshot.expression <= 0.625,
                "published expression outside independent audio family");
    const double code = (snapshot.expression - 0.5) * 32768.0;
    nt::require(code == std::trunc(code) && code >= 1.0 && code <= kAudioGenerationCount,
                "published expression has no exact generation code");
    const auto generation = static_cast<std::uint32_t>(code) - 1U;
    nt::require(same_snapshot(snapshot, pattern(generation, true)),
                "torn or unexpected complete audio snapshot");
    return generation;
}

void build_queues(nt::ParameterChanges& changes) {
    for (const sv::ParamID base : {4096U, 4112U, 4128U, 4144U}) {
        for (sv::ParamID drawbar = 0; drawbar < 9U; ++drawbar) {
            changes.add_queue(base + drawbar).points.push_back({0, 0.0});
        }
    }
    for (const sv::ParamID id : {8192U, 8208U, 8209U, 12288U, 12289U,
                                  12290U, 12291U, 16384U, 16385U}) {
        changes.add_queue(id).points.push_back({0, 0.0});
    }
    nt::require(changes.queues.size() == 45, "independent all-control queue count");
}

void write_queues(nt::ParameterChanges& changes, const ControlSnapshot& snapshot) {
    std::size_t index = 0;
    const auto put = [&](double value) { changes.queues[index++]->points[0].normalized = value; };
    for (const auto& manual : snapshot.drawbars) {
        for (const auto& bank : manual) {
            for (const auto drawbar : bank) put(static_cast<double>(drawbar) / 8.0);
        }
    }
    put(snapshot.expression);
    put(static_cast<double>(snapshot.selected_banks[0]));
    put(static_cast<double>(snapshot.selected_banks[1]));
    put(snapshot.percussion.enabled ? 1.0 : 0.0);
    put(static_cast<double>(snapshot.percussion.harmonic));
    put(static_cast<double>(snapshot.percussion.volume));
    put(static_cast<double>(snapshot.percussion.decay));
    put(static_cast<double>(snapshot.pedal_drawbars[0]) / 8.0);
    put(static_cast<double>(snapshot.pedal_drawbars[1]) / 8.0);
    nt::require(index == 45, "all independent native queues populated");
}

std::array<Event, 3> physical_notes() {
    return {{{0, EventType::NoteOn, Manual::Upper, 60, 1.0},
             {0, EventType::NoteOn, Manual::Lower, 48, 1.0},
             {0, EventType::PedalOn, Manual::Lower, 1, 1.0}}};
}

void native_notes(nt::EventList& events) {
    events.events = {nt::note_on(0, 60, 0, 0, 100), nt::note_on(1, 48, 0, 1, 101),
                     nt::note_on(2, 36, 0, 2, 102)};
}

void compare(nt::StereoBlock& block, Engine& reference, std::span<const Event> events,
             Counters& counts, bool future = false) {
    std::array<float, kMaximumFrames> expected{};
    const auto frames = static_cast<std::uint32_t>(block.data.numSamples);
    const auto before = reference.frame_clock();
    nt::require(static_cast<bool>(reference.process(frames, {expected.data(), frames}, events)),
                "independent reference callback accepted");
    nt::require(reference.frame_clock() == before + frames, "reference elapsed frame sum");
    for (std::size_t sample = 0; sample < frames; ++sample) {
        nt::require(std::isfinite(block.left[sample]) && std::isfinite(block.right[sample]),
                    "native concurrent output finite");
        nt::require(std::bit_cast<std::uint32_t>(block.left[sample]) ==
                        std::bit_cast<std::uint32_t>(expected[sample]) &&
                    std::bit_cast<std::uint32_t>(block.right[sample]) ==
                        std::bit_cast<std::uint32_t>(expected[sample]),
                    "native concurrent output differs from plain Engine history");
        if (expected[sample] != 0.0F) ++counts.audible_frames;
    }
    ++counts.callbacks;
    if (frames == 0) ++counts.zero_callbacks;
    counts.compared_frames += frames;
    if (future) counts.future_frames += frames;
}

void save_exact(nt::NativePlugin& plugin, const ControlSnapshot& expected, Counters& counts) {
    nt::MemoryStream stream;
    stream.write_chunk = 7;
    nt::require_ok(plugin.component->getState(&stream), "quiescent native save");
    nt::require(same_snapshot(nt::parse_snapshot(stream.bytes), expected),
                "quiescent saved controls are not the expected complete snapshot");
    ++counts.successful_saves;
}

struct WorkerError {
    std::exception_ptr exception{};
    std::atomic<bool> failed{false};

    void capture() noexcept {
        exception = std::current_exception();
        failed.store(true, std::memory_order_release);
    }
    void check() const {
        if (failed.load(std::memory_order_acquire)) std::rethrow_exception(exception);
    }
};

template<class Predicate>
bool wait_for(Predicate predicate, const WorkerError& error, std::stop_token stop = {}) {
    const auto deadline = std::chrono::steady_clock::now() + std::chrono::seconds(60);
    while (!predicate()) {
        error.check();
        if (stop.stop_requested()) return false;
        nt::require(std::chrono::steady_clock::now() < deadline, "test host coordination deadline");
        std::this_thread::yield();
    }
    error.check();
    return true;
}

void add(Counters& result, const Counters& value) {
    result.callbacks += value.callbacks;
    result.rejected_callbacks += value.rejected_callbacks;
    result.zero_callbacks += value.zero_callbacks;
    result.compared_frames += value.compared_frames;
    result.audible_frames += value.audible_frames;
    result.accepted_loads += value.accepted_loads;
    result.full_loads += value.full_loads;
    result.malformed_loads += value.malformed_loads;
    result.successful_saves += value.successful_saves;
    result.busy_saves += value.busy_saves;
    result.pending_saves += value.pending_saves;
    result.published_saves += value.published_saves;
    result.future_frames += value.future_frames;
}

void coordinated(const std::string& bundle, const RuntimeProfile& profile, double rate,
                 Counters& total) {
    nt::NativePlugin plugin(bundle);
    plugin.start(rate, static_cast<Steinberg::int32>(kMaximumFrames));
    Engine reference;
    nt::require(reference.prepare(profile, {rate, kMaximumFrames, 0, 0},
                                   make_nominal_console_model()) == Status::Ok,
                "coordinated reference prepared");
    Counters ui_counts{}, audio_counts{};
    const auto initial = pattern(31, true);
    nt::require_ok(plugin.load_state(nt::snapshot_text(initial)), "initial controlled state");
    ++ui_counts.accepted_loads;
    nt::require(reference.restore_controls(initial), "initial reference controls");

    // Release/acquire commands synchronize only the test host's paused phases.
    // No mutex, wait or test callback is installed in the native processor.
    std::atomic<unsigned> command{0}, completed{0};
    WorkerError error;
    std::jthread audio([&](std::stop_token stop) {
        try {
            nt::StereoBlock block(kMaximumFrames);
            nt::EventList notes;
            native_notes(notes);
            block.set_frames(257);
            block.data.inputEvents = &notes;
            nt::require_ok(plugin.processor->process(block.data), "initial controlled audio");
            const auto on = physical_notes();
            compare(block, reference, on, audio_counts);
            block.data.inputEvents = nullptr;
            completed.store(1, std::memory_order_release);
            for (std::size_t round = 0; round < kCoordinatedRounds; ++round) {
                const auto bad_command = static_cast<unsigned>(round * 2U + 1U);
                if (!wait_for([&] { return command.load(std::memory_order_acquire) >= bad_command; },
                              error, stop)) return;
                nt::ParameterChanges invalid;
                invalid.add_queue(8192U).points = {{0, 0.75}, {18, 0.5}};
                block.set_frames(17);
                block.fill(123.0F);
                block.bus.silenceFlags = 0x12U;
                block.data.inputParameterChanges = &invalid;
                nt::require(plugin.processor->process(block.data) != kResultOk,
                            "invalid audio callback rejected with queued states");
                nt::require(block.bus.silenceFlags == 0x12U, "rejected native flags preserved");
                for (std::size_t index = 0; index < block.left.size(); ++index) {
                    nt::require(block.left[index] == 123.0F && block.right[index] == 123.0F,
                                "rejected native output preserved");
                }
                ++audio_counts.rejected_callbacks;
                completed.store(bad_command + 1U, std::memory_order_release);
                if (!wait_for([&] { return command.load(std::memory_order_acquire) >= bad_command + 1U; },
                              error, stop)) return;

                // Four known UI snapshots precede one sample-zero automation.
                for (std::uint32_t slot = 0; slot < 4; ++slot) {
                    nt::require(reference.restore_controls(pattern(
                        static_cast<std::uint32_t>(round) * 4U + slot, false)),
                        "coordinated reference restore");
                }
                nt::ParameterChanges automation;
                const double expression = 0.25 + static_cast<double>(round + 1U) / 32.0;
                automation.add_queue(8192U).points = {{0, expression}};
                block.data.inputParameterChanges = &automation;
                block.set_frames(round % 3U == 0 ? 0 : static_cast<Steinberg::int32>(37U + round));
                nt::require_ok(plugin.processor->process(block.data), "controlled queued restore/automation");
                const Event expression_event{0, EventType::Expression, Manual::Upper, 0, expression};
                compare(block, reference, {&expression_event, 1}, audio_counts);
                block.data.inputParameterChanges = nullptr;
                block.set_frames(193);
                nt::require_ok(plugin.processor->process(block.data), "controlled future audio");
                compare(block, reference, {}, audio_counts, true);
                completed.store(bad_command + 2U, std::memory_order_release);
            }
        } catch (...) { error.capture(); }
    });
    nt::require(wait_for([&] { return completed.load(std::memory_order_acquire) >= 1U; }, error),
                "initial controlled callback completed");
    for (std::size_t round = 0; round < kCoordinatedRounds; ++round) {
        for (std::uint32_t slot = 0; slot < 4; ++slot) {
            nt::MemoryStream stream(nt::snapshot_text(pattern(
                static_cast<std::uint32_t>(round) * 4U + slot, false)));
            stream.read_chunk = 5;
            nt::require_ok(plugin.component->setState(&stream), "four pending native states");
            ++ui_counts.accepted_loads;
            stream.bytes.assign("caller-owned stream destroyed after accepted load");
        }
        const auto latest = pattern(static_cast<std::uint32_t>(round) * 4U + 3U, false);
        save_exact(plugin, latest, ui_counts);
        ++ui_counts.pending_saves;
        const auto fifth = nt::snapshot_text(pattern(3000U, false));
        nt::require(plugin.load_state(fifth) != kResultOk, "fifth pending state rejected");
        ++ui_counts.full_loads;
        nt::require(plugin.load_state(fifth + " trailing-invalid") != kResultOk,
                    "malformed state does not replace a pending value");
        ++ui_counts.malformed_loads;
        save_exact(plugin, latest, ui_counts);
        command.store(static_cast<unsigned>(round * 2U + 1U), std::memory_order_release);
        nt::require(wait_for([&] { return completed.load(std::memory_order_acquire) >= round * 2U + 2U; }, error),
                    "invalid callback completed");
        nt::require(plugin.load_state(fifth) != kResultOk,
                    "rejected callback did not consume pending state capacity");
        ++ui_counts.full_loads;
        save_exact(plugin, latest, ui_counts);
        command.store(static_cast<unsigned>(round * 2U + 2U), std::memory_order_release);
        nt::require(wait_for([&] { return completed.load(std::memory_order_acquire) >= round * 2U + 3U; }, error),
                    "accepted callback completed");
        auto published = latest;
        published.expression = 0.25 + static_cast<double>(round + 1U) / 32.0;
        save_exact(plugin, published, ui_counts);
        ++ui_counts.published_saves;
    }
    audio.join();
    error.check();
    nt::require(audio_counts.audible_frames > 1000, "controlled held divisions remain audible");
    plugin.stop_processing();
    plugin.deactivate();
    add(total, ui_counts);
    add(total, audio_counts);
}

void stress_save(nt::NativePlugin& plugin, const ControlSnapshot& latest, Counters& counts,
                 bool publication_only = false) {
    nt::MemoryStream stream("untouched");
    stream.write_chunk = 11;
    const auto result = plugin.component->getState(&stream);
    if (result != kResultOk) {
        nt::require(result == Steinberg::kResultFalse && stream.bytes == "untouched" &&
                        stream.write_calls == 0,
                    "busy state save must preserve the actual caller stream");
        ++counts.busy_saves;
        return;
    }
    const auto snapshot = nt::parse_snapshot(stream.bytes);
    ++counts.successful_saves;
    if (snapshot.expression < 0.5) {
        nt::require(!publication_only, "acknowledged state must expose audio publication");
        nt::require(same_snapshot(snapshot, latest), "pending save is not latest accepted UI snapshot");
        ++counts.pending_saves;
    } else {
        static_cast<void>(decode_audio_generation(snapshot));
        ++counts.published_saves;
    }
}

void concurrent_stress(const std::string& bundle, const RuntimeProfile& profile, double rate,
                       Counters& total) {
    nt::NativePlugin plugin(bundle);
    plugin.start(rate, static_cast<Steinberg::int32>(kMaximumFrames));
    Engine reference;
    nt::require(reference.prepare(profile, {rate, kMaximumFrames, 0, 0},
                                   make_nominal_console_model()) == Status::Ok,
                "stress reference prepared");
    ControlSnapshot latest = pattern(0, false);
    nt::require_ok(plugin.load_state(nt::snapshot_text(latest)), "initial stress state");
    Counters ui_counts{}, audio_counts{};
    ++ui_counts.accepted_loads;
    std::atomic<bool> initialized{false}, ui_finished{false};
    std::atomic<std::uint64_t> published_callbacks{0};
    WorkerError error;
    std::uint32_t final_generation = 0;
    std::jthread audio([&](std::stop_token stop) {
        try {
            nt::StereoBlock block(kMaximumFrames);
            nt::ParameterChanges automation;
            build_queues(automation);
            block.data.inputParameterChanges = &automation;
            nt::EventList notes;
            native_notes(notes);
            block.data.inputEvents = &notes;
            unsigned drain = 0;
            std::uint64_t iteration = 0;
            constexpr std::array<Steinberg::int32, 5> sizes{0, 1, 17, 64, 127};
            while (!stop.stop_requested() && drain < 2U) {
                nt::require(iteration < 200000, "stress test host callback budget exhausted");
                const auto generation = static_cast<std::uint32_t>(iteration % kAudioGenerationCount);
                const auto controls = pattern(generation, true);
                write_queues(automation, controls);
                nt::require(reference.restore_controls(controls), "independent complete audio controls");
                block.set_frames(iteration == 0 ? 257 : sizes[iteration % sizes.size()]);
                nt::require_ok(plugin.processor->process(block.data), "concurrent native callback");
                if (iteration == 0) {
                    const auto on = physical_notes();
                    compare(block, reference, on, audio_counts);
                    block.data.inputEvents = nullptr;
                    initialized.store(true, std::memory_order_release);
                } else {
                    compare(block, reference, {}, audio_counts);
                }
                final_generation = generation;
                ++iteration;
                published_callbacks.store(iteration, std::memory_order_release);
                if (ui_finished.load(std::memory_order_acquire)) ++drain;
            }
            if (stop.stop_requested()) return;
            // After the UI release and two boundary publications, no load is
            // pending. A final held-note block exposes any reset/lost history.
            block.data.inputParameterChanges = nullptr;
            block.set_frames(static_cast<Steinberg::int32>(kMaximumFrames));
            nt::require_ok(plugin.processor->process(block.data), "concurrent final future audio");
            compare(block, reference, {}, audio_counts, true);
        } catch (...) { error.capture(); }
    });
    nt::require(wait_for([&] { return initialized.load(std::memory_order_acquire); }, error),
                "initial stress callback completed");
    const auto deadline = std::chrono::steady_clock::now() + std::chrono::seconds(60);
    // No pending load can hide atomic publication behind the UI's private copy
    // in this phase: require 1,024 successful complete audio-family snapshots.
    while (ui_counts.published_saves < kPublicationOnlySaves) {
        error.check();
        nt::require(std::chrono::steady_clock::now() < deadline, "publication reader progress deadline");
        stress_save(plugin, latest, ui_counts, true);
    }
    // A reader owns no slot and must not hold up audio when it stops reading.
    const auto before_pause = published_callbacks.load(std::memory_order_acquire);
    nt::require(wait_for([&] {
        return published_callbacks.load(std::memory_order_acquire) >= before_pause + 32U;
    }, error), "audio progresses while UI performs no state reads");
    for (std::uint32_t generation = 1; generation <= kAcceptedStressLoads;) {
        error.check();
        nt::require(std::chrono::steady_clock::now() < deadline, "stress UI progress deadline");
        const auto candidate = pattern(generation, false);
        nt::MemoryStream input(nt::snapshot_text(candidate));
        input.read_chunk = 13;
        const auto result = plugin.component->setState(&input);
        if (result == kResultOk) {
            latest = candidate;
            ++generation;
            ++ui_counts.accepted_loads;
        } else {
            nt::require(result == Steinberg::kResultFalse, "valid load has only bounded queue-full failure");
            ++ui_counts.full_loads;
        }
        stress_save(plugin, latest, ui_counts);
        if (result == kResultOk && generation % 7U == 0) {
            // This invalid future family member must never become the newest
            // accepted UI snapshot, even while audio is consuming the queue.
            const auto malformed = nt::snapshot_text(pattern(7000U + generation, false)) + " extra";
            nt::require(plugin.load_state(malformed) != kResultOk, "malformed active state rejected");
            ++ui_counts.malformed_loads;
            stress_save(plugin, latest, ui_counts);
        }
        if (result != kResultOk) std::this_thread::yield();
    }
    ui_finished.store(true, std::memory_order_release);
    audio.join();
    error.check();
    save_exact(plugin, pattern(final_generation, true), ui_counts);
    ++ui_counts.published_saves;
    nt::require(ui_counts.successful_saves >= 100, "substantial successful concurrent native saves");
    nt::require(audio_counts.callbacks >= 10 && audio_counts.audible_frames > 1000,
                "substantial actual concurrent processing and audible reference");
    plugin.stop_processing();
    plugin.deactivate();
    add(total, ui_counts);
    add(total, audio_counts);
}

} // namespace

int main(int argc, char** argv) {
    try {
        nt::require(argc == 3, "usage: test_native_concurrency BUNDLE PROFILE");
        std::ifstream input(argv[2], std::ios::binary);
        RuntimeProfile profile{};
        std::string error;
        nt::require(load_runtime_profile(input, profile, error), error);
        Counters total{};
        for (const double rate : {44100.0, 48000.0, 96000.0}) {
            coordinated(argv[1], profile, rate, total);
            concurrent_stress(argv[1], profile, rate, total);
        }
        std::cout << "native-concurrency rates=3 controlled_rounds=" << 3U * kCoordinatedRounds
                  << " stress_accepted_loads=" << 3U * kAcceptedStressLoads
                  << " publication_only_saves=" << 3U * kPublicationOnlySaves
                  << " reader_pause_callbacks=96"
                  << " callbacks=" << total.callbacks << " rejected_callbacks=" << total.rejected_callbacks
                  << " zero_callbacks=" << total.zero_callbacks << " compared_frames=" << total.compared_frames
                  << " audible_frames=" << total.audible_frames << " future_frames=" << total.future_frames
                  << " accepted_loads=" << total.accepted_loads << " full_loads=" << total.full_loads
                  << " malformed_loads=" << total.malformed_loads << " successful_saves=" << total.successful_saves
                  << " busy_saves=" << total.busy_saves << " pending_saves=" << total.pending_saves
                  << " published_saves=" << total.published_saves << " maximum_audio_error=0\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "native-concurrency failure: " << error.what() << '\n';
        return 1;
    }
}
