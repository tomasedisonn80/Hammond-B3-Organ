#include "AudioDevice.h"
#include "TestSupport.h"

#include <SDL.h>

#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <limits>
#include <string>
#include <string_view>
#include <type_traits>

namespace {

using namespace hammond;
using namespace hammond::standalone;
using Clock = std::chrono::steady_clock;

static_assert(std::is_same_v<decltype(std::declval<const AudioDevice&>().device_id()),
                             SDL_AudioDeviceID>);
static_assert(noexcept(std::declval<const AudioDevice&>().device_id()));
static_assert(noexcept(std::declval<const AudioDevice&>().is_removed_by(
    std::declval<const SDL_AudioDeviceEvent&>())));

constexpr auto kProgressLimit = std::chrono::milliseconds{1500};
constexpr std::uint8_t kUpperNote = 60;
constexpr std::uint8_t kLowerNote = 67;
constexpr std::size_t kUpperIndex = kUpperNote - kMinManualMidiNote;
constexpr std::size_t kLowerIndex = kLowerNote - kMinManualMidiNote;

struct Totals {
    std::uint64_t cycles{};
    std::uint64_t queued_events{};
    std::uint64_t ignored_events{};
    std::uint64_t matching_queries{};
    std::uint64_t matching_closes{};
    std::uint64_t rejected_opens{};
    std::uint64_t id_reuses{};
    std::uint64_t callbacks{};
    std::uint64_t frames{};
} totals;

template <typename Predicate>
void wait_for(std::string_view description, Predicate predicate) {
    const auto deadline = Clock::now() + kProgressLimit;
    while (!predicate()) {
        if (Clock::now() >= deadline) {
            hammond_test::fail("bounded actual SDL callback progress", __FILE__, __LINE__,
                               description);
        }
        SDL_Delay(1);
    }
}

[[nodiscard]] SessionSnapshot read(const Session& session) {
    SessionSnapshot snapshot;
    wait_for("coherent Session observation", [&] { return session.read_snapshot(snapshot); });
    CHECK(snapshot.publication_revision % 2 == 0);
    return snapshot;
}

[[nodiscard]] bool no_holds(const SessionSnapshot& snapshot) {
    for (const auto& manual : snapshot.held_keys) {
        if (std::any_of(manual.begin(), manual.end(), [](bool held) { return held; })) return false;
    }
    return std::none_of(snapshot.held_pedals.begin(), snapshot.held_pedals.end(),
                        [](bool held) { return held; });
}

void clean_session(const SessionSnapshot& snapshot) {
    CHECK(snapshot.queue_overflows == 0);
    CHECK(snapshot.rejected_commands == 0);
    CHECK(snapshot.recovery_count == 0);
    CHECK(snapshot.discarded_commands == 0);
    CHECK(snapshot.fault_flags == 0);
    CHECK(snapshot.last_core_status == Status::Ok);
}

void same_stopped_snapshot(const SessionSnapshot& actual, const SessionSnapshot& expected) {
    CHECK(!actual.running && !expected.running);
    CHECK(actual.controls == expected.controls);
    CHECK(actual.held_keys == expected.held_keys);
    CHECK(actual.held_pedals == expected.held_pedals);
    CHECK(actual.frame_clock == expected.frame_clock);
    CHECK(actual.sample_rate == expected.sample_rate);
    CHECK(actual.peak == expected.peak);
    CHECK(actual.prepared == expected.prepared);
    CHECK(actual.publication_revision == expected.publication_revision);
    CHECK(actual.resolved_sequence == expected.resolved_sequence);
    CHECK(actual.last_applied_sequence == expected.last_applied_sequence);
    clean_session(actual);
    clean_session(expected);
}

void clean_audio(const AudioDeviceDiagnostics& diagnostics) {
    CHECK(diagnostics.render_failures == 0);
    CHECK(diagnostics.format_failures == 0);
    CHECK(diagnostics.overrange_failures == 0);
    CHECK(diagnostics.overrange_samples == 0);
    CHECK(diagnostics.nonfinite_failures == 0);
    CHECK(diagnostics.nonfinite_samples == 0);
    CHECK(diagnostics.last_render_status == SessionStatus::Ok);
    CHECK(diagnostics.last_lifecycle_status == SessionStatus::Ok);
}

void stays_quiet(const AudioDevice& device) {
    const auto before = device.diagnostics();
    const auto info = device.info();
    const auto duration = info.sample_rate > 0 ? std::max(6U,
        (2000U * static_cast<unsigned>(info.buffer_frames) +
         static_cast<unsigned>(info.sample_rate) - 1U) /
            static_cast<unsigned>(info.sample_rate)) : 6U;
    const auto deadline = Clock::now() + std::chrono::milliseconds{duration};
    do {
        SDL_Delay(1);
        const auto after = device.diagnostics();
        CHECK(after.callback_count == before.callback_count);
        CHECK(after.rendered_frames == before.rendered_frames);
        CHECK(after.render_failures == before.render_failures);
        CHECK(after.format_failures == before.format_failures);
        CHECK(after.nonfinite_failures == before.nonfinite_failures);
        CHECK(after.overrange_failures == before.overrange_failures);
    } while (Clock::now() < deadline);
}

[[nodiscard]] SDL_Event event(Uint32 type, SDL_AudioDeviceID id, Uint8 capture = 0) {
    SDL_Event result{};
    result.adevice.type = type;
    result.adevice.which = id;
    result.adevice.iscapture = capture;
    return result;
}

// Events are explicit software fixtures passed through SDL's real public queue.
// Pushing a removal event does not physically disconnect the dummy backend.
[[nodiscard]] SDL_AudioDeviceEvent round_trip(SDL_Event requested) {
    CHECK(SDL_HasEvents(SDL_AUDIODEVICEADDED, SDL_AUDIODEVICEREMOVED) == SDL_FALSE);
    CHECK(SDL_PushEvent(&requested) == 1);
    SDL_Event received{};
    CHECK(SDL_PeepEvents(&received, 1, SDL_GETEVENT, SDL_AUDIODEVICEADDED,
                        SDL_AUDIODEVICEREMOVED) == 1);
    CHECK(received.type == requested.type);
    CHECK(received.adevice.which == requested.adevice.which);
    CHECK(received.adevice.iscapture == requested.adevice.iscapture);
    CHECK(SDL_HasEvents(SDL_AUDIODEVICEADDED, SDL_AUDIODEVICEREMOVED) == SDL_FALSE);
    ++totals.queued_events;
    return received.adevice;
}

// This fixture owns its small routing action; it is not the application handler.
// Literal expected cases below, actual SDL status and retained music are the
// independent oracle. A false match visibly closes the device and fails checks.
void ignore_event(AudioDevice& device, SDL_Event requested) {
    const auto id = device.device_id();
    const bool was_running = device.is_running();
    const auto received = round_trip(requested);
    const bool matched = device.is_removed_by(received);
    if (matched) device.close();
    CHECK(!matched);
    CHECK(device.device_id() == id);
    CHECK(device.is_open() == (id != 0));
    CHECK(device.is_running() == was_running);
    if (id != 0) {
        CHECK(SDL_GetAudioDeviceStatus(id) == (was_running ? SDL_AUDIO_PLAYING : SDL_AUDIO_PAUSED));
    }
    ++totals.ignored_events;
}

void ignore_unrelated_events(AudioDevice& device) {
    const auto id = device.device_id();
    CHECK(id != 0);
    const auto other = id == std::numeric_limits<SDL_AudioDeviceID>::max() ?
        SDL_AudioDeviceID{1} : std::numeric_limits<SDL_AudioDeviceID>::max();
    CHECK(other != id && other != 0);
    // SDL 2.32.10 emits which=0 when an unopened device is removed. ADDED's
    // which is an enumeration index, even if numerically equal to our handle.
    const std::array<SDL_Event, 8> ignored{
        event(SDL_AUDIODEVICEREMOVED, 0),
        event(SDL_AUDIODEVICEREMOVED, other),
        event(SDL_AUDIODEVICEREMOVED, id, 1),
        event(SDL_AUDIODEVICEREMOVED, id, 2),
        event(SDL_AUDIODEVICEREMOVED, id, 255),
        event(SDL_AUDIODEVICEADDED, id),
        event(SDL_AUDIODEVICEADDED, 0),
        event(SDL_AUDIODEVICEADDED, other, 1)};
    for (const auto& requested : ignored) ignore_event(device, requested);
}

void matching_query(const AudioDevice& device) {
    const auto id = device.device_id();
    CHECK(id != 0);
    const bool was_running = device.is_running();
    const auto received = round_trip(event(SDL_AUDIODEVICEREMOVED, id));
    CHECK(device.is_removed_by(received));
    CHECK(device.device_id() == id);
    CHECK(device.is_open() && device.is_running() == was_running);
    CHECK(SDL_GetAudioDeviceStatus(id) == (was_running ? SDL_AUDIO_PLAYING : SDL_AUDIO_PAUSED));
    ++totals.matching_queries;
}

[[nodiscard]] ControlSnapshot registration() {
    ControlSnapshot controls;
    controls.drawbars[0][1][2] = 6;
    controls.drawbars[1][0][2] = 5;
    controls.drawbars[1][1][7] = 3; // Retain an inactive-bank edit through close.
    controls.selected_banks = {DrawbarBank::B, DrawbarBank::A};
    controls.pedal_drawbars = {4, 0};
    controls.expression = 0.25;
    CHECK(is_valid_control_snapshot(controls));
    return controls;
}

[[nodiscard]] std::uint64_t post_music(Session& session, const ControlSnapshot& controls) {
    CHECK(session.post(controls));
    CHECK(session.post(PerformanceInputEvent{HostNoteEvent{
        0, HostNoteKind::On, 0, kUiInputChannel, kUpperNote, 100, 101}}));
    // Different channels ensure ordinary close releases all owners, including
    // owners a UI-only focus release would not affect.
    CHECK(session.post(PerformanceInputEvent{HostNoteEvent{
        0, HostNoteKind::On, 1, 5, kLowerNote, 100, 102}}));
    const auto pedal = session.post(PerformanceInputEvent{PedalNoteEvent{
        0, PedalNoteKind::On, 0, 3, PedalId{7}, 100, 103}});
    CHECK(pedal);
    return pedal.sequence;
}

void has_music(const SessionSnapshot& snapshot, const ControlSnapshot& controls,
               std::uint64_t sequence) {
    CHECK(snapshot.running && snapshot.prepared);
    CHECK(snapshot.controls == controls);
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        for (std::size_t key = 0; key < kManualKeyCount; ++key) {
            const bool expected = manual == 0 ? key == kUpperIndex : key == kLowerIndex;
            CHECK(snapshot.held_keys[manual][key] == expected);
        }
    }
    for (std::size_t pedal = 0; pedal < kPedalCount; ++pedal) {
        CHECK(snapshot.held_pedals[pedal] == (pedal == 6));
    }
    CHECK(snapshot.last_applied_sequence == sequence);
    CHECK(snapshot.resolved_sequence == sequence);
    CHECK(std::isfinite(snapshot.peak) && snapshot.peak > 0.0F && snapshot.peak < 1.0F);
    clean_session(snapshot);
}

void wait_for_music(const Session& session, const ControlSnapshot& controls,
                    std::uint64_t sequence) {
    wait_for("both manuals and independent pedal actually applied", [&] {
        SessionSnapshot snapshot;
        return session.read_snapshot(snapshot) && snapshot.last_applied_sequence == sequence &&
            snapshot.held_keys[0][kUpperIndex] && snapshot.held_keys[1][kLowerIndex] &&
            snapshot.held_pedals[6] && snapshot.peak > 0.0F;
    });
    has_music(read(session), controls, sequence);
}

void test_uninitialized(const RuntimeProfile& profile) {
    CHECK((SDL_WasInit(SDL_INIT_AUDIO) & SDL_INIT_AUDIO) == 0);
    Session session;
    AudioDevice device;
    CHECK(device.device_id() == 0 && !device.is_open() && !device.is_running());
    for (const auto id : std::array<SDL_AudioDeviceID, 3>{0, 1, 0xffffffffU}) {
        CHECK(!device.is_removed_by(event(SDL_AUDIODEVICEREMOVED, id).adevice));
        CHECK(!device.is_removed_by(event(SDL_AUDIODEVICEREMOVED, id, 1).adevice));
        CHECK(!device.is_removed_by(event(SDL_AUDIODEVICEADDED, id).adevice));
    }
    std::string error;
    CHECK(!device.open(session, profile, {}, error));
    CHECK(!error.empty() && device.device_id() == 0);
    ++totals.rejected_opens;
    device.close();
    CHECK(device.device_id() == 0);
}

void test_lifecycles(const RuntimeProfile& profile) {
    Session session;
    AudioDevice device;
    std::string error;
    const auto controls = registration();
    const std::array<AudioDeviceConfig, 3> configurations{
        AudioDeviceConfig{{}, 44100, 128, 11, 77},
        AudioDeviceConfig{{}, 48000, 256, 12, 99},
        AudioDeviceConfig{{}, 96000, 512, 13, 121}};
    SDL_AudioDeviceID previous_id = 0;
    for (const auto& config : configurations) {
        CHECK(device.device_id() == 0);
        const auto before_open = device.diagnostics();
        CHECK(device.open(session, profile, config, error));
        CHECK(error.empty());
        const auto id = device.device_id();
        CHECK(id != 0 && device.is_open() && !device.is_running());
        CHECK(device.info().open && !device.info().running);
        CHECK(device.info().driver == "dummy");
        CHECK(device.info().sample_rate == config.sample_rate);
        CHECK(device.info().buffer_frames == config.buffer_frames);
        CHECK(SDL_GetAudioDeviceStatus(id) == SDL_AUDIO_PAUSED);
        CHECK(device.diagnostics().callback_count == before_open.callback_count);
        SDL_FlushEvents(SDL_AUDIODEVICEADDED, SDL_AUDIODEVICEREMOVED);

        if (previous_id != 0) {
            const auto old_event = round_trip(event(SDL_AUDIODEVICEREMOVED, previous_id));
            // A numerical ID reused by SDL names the current open device. It
            // does not carry a generation or prove the age of a queued event.
            CHECK(device.is_removed_by(old_event) == (previous_id == id));
            if (previous_id == id) ++totals.id_reuses;
        }
        CHECK(!device.open(session, profile, config, error));
        CHECK(!error.empty() && device.device_id() == id);
        CHECK(SDL_GetAudioDeviceStatus(id) == SDL_AUDIO_PAUSED);
        ++totals.rejected_opens;

        const auto sequence = post_music(session, controls);
        const auto prepared = read(session);
        CHECK(prepared.prepared && !prepared.running && no_holds(prepared));
        CHECK(prepared.controls == ControlSnapshot{});
        CHECK(prepared.frame_clock == config.initial_frame);
        ignore_unrelated_events(device);
        matching_query(device);
        stays_quiet(device);
        same_stopped_snapshot(read(session), prepared);

        CHECK(device.start(error));
        CHECK(error.empty() && device.device_id() == id && device.is_running());
        CHECK(SDL_GetAudioDeviceStatus(id) == SDL_AUDIO_PLAYING);
        wait_for_music(session, controls, sequence);
        const auto playing = read(session);
        ignore_unrelated_events(device);
        matching_query(device);
        wait_for("ignored removals preserve callback progress", [&] {
            SessionSnapshot snapshot;
            return session.read_snapshot(snapshot) && snapshot.frame_clock > playing.frame_clock;
        });
        has_music(read(session), controls, sequence);

        CHECK(device.stop() == SessionStatus::Ok);
        CHECK(device.device_id() == id && device.is_open() && !device.is_running());
        CHECK(SDL_GetAudioDeviceStatus(id) == SDL_AUDIO_PAUSED);
        const auto stopped = read(session);
        CHECK(!stopped.running && no_holds(stopped));
        CHECK(stopped.controls == controls && stopped.peak == 0.0F);
        CHECK(stopped.frame_clock >= playing.frame_clock);
        ignore_unrelated_events(device);
        matching_query(device);
        stays_quiet(device);
        same_stopped_snapshot(read(session), stopped);

        CHECK(device.start(error));
        wait_for("restart advances retained clock without restoring notes", [&] {
            SessionSnapshot snapshot;
            return session.read_snapshot(snapshot) && snapshot.frame_clock > stopped.frame_clock;
        });
        const auto resumed = read(session);
        CHECK(resumed.running && no_holds(resumed) && resumed.controls == controls);
        const auto replayed = post_music(session, controls);
        wait_for_music(session, controls, replayed);

        const auto removal = round_trip(event(SDL_AUDIODEVICEREMOVED, id));
        CHECK(device.is_removed_by(removal));
        device.close(); // The actual SDL join precedes Session owner release.
        ++totals.matching_closes;
        CHECK(device.device_id() == 0 && !device.is_open() && !device.is_running());
        CHECK(!device.info().open && !device.info().running);
        CHECK(SDL_GetAudioDeviceStatus(id) == SDL_AUDIO_STOPPED);
        CHECK(!device.is_removed_by(removal));
        ignore_event(device, event(SDL_AUDIODEVICEREMOVED, id));
        ignore_event(device, event(SDL_AUDIODEVICEREMOVED, 0));
        const auto closed = read(session);
        CHECK(!closed.running && no_holds(closed));
        CHECK(closed.controls == controls && closed.peak == 0.0F);
        CHECK(closed.last_applied_sequence == replayed && closed.resolved_sequence == replayed);
        clean_session(closed);
        const auto after_close = device.diagnostics();
        clean_audio(after_close);
        const auto callbacks = after_close.callback_count - before_open.callback_count;
        const auto frames = after_close.rendered_frames - before_open.rendered_frames;
        CHECK(callbacks > 0 && frames == callbacks * config.buffer_frames);
        CHECK(closed.frame_clock == config.initial_frame + frames);
        totals.callbacks += callbacks;
        totals.frames += frames;
        stays_quiet(device);
        same_stopped_snapshot(read(session), closed);
        device.close();
        CHECK(device.device_id() == 0);
        CHECK(!device.start(error));
        CHECK(!error.empty());
        CHECK(device.stop() == SessionStatus::NotPrepared);

        AudioDeviceConfig invalid = config;
        invalid.sample_rate = 12345;
        CHECK(!device.open(session, profile, invalid, error));
        CHECK(!error.empty() && device.device_id() == 0);
        CHECK(!device.is_removed_by(removal));
        same_stopped_snapshot(read(session), closed);
        ++totals.rejected_opens;
        CHECK(!device.open(session, RuntimeProfile{}, config, error));
        CHECK(!error.empty() && device.device_id() == 0);
        CHECK(!device.is_removed_by(removal));
        same_stopped_snapshot(read(session), closed);
        ++totals.rejected_opens;
        previous_id = id;
        ++totals.cycles;
    }
    // Successful final acquisition proves the last failed partial SDL open
    // was released, then closes while paused without requiring a callback.
    CHECK(device.open(session, profile, configurations.front(), error));
    CHECK(device.device_id() != 0);
    CHECK(SDL_GetAudioDeviceStatus(device.device_id()) == SDL_AUDIO_PAUSED);
    matching_query(device);
    const auto pending_id = device.device_id();
    device.close();
    CHECK(device.device_id() == 0 && SDL_GetAudioDeviceStatus(pending_id) == SDL_AUDIO_STOPPED);
    CHECK(!device.is_removed_by(event(SDL_AUDIODEVICEREMOVED, pending_id).adevice));
    CHECK(!read(session).running && no_holds(read(session)));
    clean_audio(device.diagnostics());
}

} // namespace

int main() {
    const auto* selected = SDL_getenv("SDL_AUDIODRIVER");
    CHECK(selected != nullptr && std::string_view{selected} == "dummy");
    const auto profile = load_test_profile();
    test_uninitialized(profile);
    SDL_SetMainReady();
    CHECK(SDL_Init(SDL_INIT_AUDIO | SDL_INIT_EVENTS) == 0);
    CHECK(std::string_view{SDL_GetCurrentAudioDriver()} == "dummy");
    SDL_FlushEvents(SDL_AUDIODEVICEADDED, SDL_AUDIODEVICEREMOVED);
    test_lifecycles(profile);
    CHECK(totals.cycles == 3);
    CHECK(totals.queued_events == 93);
    CHECK(totals.ignored_events == 78);
    CHECK(totals.matching_queries == 10);
    CHECK(totals.matching_closes == 3);
    CHECK(totals.rejected_opens == 10);
    SDL_Quit();
    CHECK(SDL_WasInit(SDL_INIT_AUDIO | SDL_INIT_EVENTS) == 0);
    std::cout << "PASS: " << totals.cycles << " actual SDL lifecycle cycles; "
              << totals.queued_events << " queued events; " << totals.ignored_events
              << " ignored events; " << totals.matching_queries << " matching pure queries; "
              << totals.matching_closes << " matched joined closes; "
              << totals.rejected_opens << " rejected opens; " << totals.id_reuses
              << " observed ID reuses; " << totals.callbacks << " callbacks; "
              << totals.frames << " rendered frames.\n"
              << "Scope: explicit dummy backend and software event injection; "
                 "no physical disconnect or application-handler execution.\n";
}
