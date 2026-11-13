#include "AudioDevice.h"
#include "TestSupport.h"

#include <SDL.h>

#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <memory>
#include <string>
#include <string_view>
#include <type_traits>
#include <vector>

namespace {

using namespace hammond;
using namespace hammond::standalone;
using Clock = std::chrono::steady_clock;

static_assert(!std::is_copy_constructible_v<AudioDevice>);
static_assert(!std::is_move_constructible_v<AudioDevice>);

constexpr auto kWaitLimit = std::chrono::milliseconds{1500};
constexpr auto kMaximum = std::numeric_limits<std::uint64_t>::max();
constexpr std::uint8_t kUpperNote = 60;
constexpr std::uint8_t kLowerNote = 67;
constexpr std::size_t kUpperIndex = kUpperNote - kMinManualMidiNote;
constexpr std::size_t kLowerIndex = kLowerNote - kMinManualMidiNote;

struct Totals {
    std::uint64_t combinations{};
    std::uint64_t matrix_callbacks{};
    std::uint64_t matrix_frames{};
    std::uint64_t rejected_opens{};
    std::uint64_t expected_render_failures{};
    std::uint64_t lifetime_cycles{};
} totals;

// All waiting is on this test's main thread. A scheduling deadline is only a
// generous test timeout; callback counts and wall time are not latency claims.
template <typename Predicate>
void wait_for(std::string_view description, Predicate predicate) {
    const auto deadline = Clock::now() + kWaitLimit;
    while (!predicate()) {
        if (Clock::now() >= deadline) {
            hammond_test::fail("bounded SDL callback progress", __FILE__, __LINE__, description);
        }
        SDL_Delay(1);
    }
}

[[nodiscard]] SessionSnapshot read(const Session& session) {
    SessionSnapshot snapshot;
    CHECK(session.read_snapshot(snapshot));
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

void same_music(const SessionSnapshot& actual, const SessionSnapshot& expected) {
    CHECK(actual.controls == expected.controls);
    CHECK(actual.held_keys == expected.held_keys);
    CHECK(actual.held_pedals == expected.held_pedals);
    CHECK(actual.frame_clock == expected.frame_clock);
    CHECK(actual.sample_rate == expected.sample_rate);
    CHECK(actual.peak == expected.peak);
    CHECK(actual.prepared == expected.prepared);
    CHECK(actual.running == expected.running);
    CHECK(actual.publication_revision == expected.publication_revision);
    CHECK(actual.resolved_sequence == expected.resolved_sequence);
    CHECK(actual.last_applied_sequence == expected.last_applied_sequence);
}

[[nodiscard]] std::chrono::milliseconds observation_window(const AudioDeviceInfo& info) {
    const auto milliseconds = (2000U * static_cast<std::uint32_t>(info.buffer_frames) +
                               static_cast<std::uint32_t>(info.sample_rate) - 1U) /
                              static_cast<std::uint32_t>(info.sample_rate);
    return std::chrono::milliseconds{std::max(milliseconds, 5U)};
}

void stays_quiet(const AudioDevice& device, std::chrono::milliseconds duration) {
    const auto before = device.diagnostics();
    const auto deadline = Clock::now() + duration;
    do {
        SDL_Delay(1);
        const auto after = device.diagnostics();
        CHECK(after.callback_count == before.callback_count);
        CHECK(after.rendered_frames == before.rendered_frames);
        CHECK(after.render_failures == before.render_failures);
        CHECK(after.format_failures == before.format_failures);
        CHECK(after.nonfinite_failures == before.nonfinite_failures);
        CHECK(after.overrange_samples == before.overrange_samples);
    } while (Clock::now() < deadline);
}

[[nodiscard]] ControlSnapshot registration() {
    ControlSnapshot controls;
    controls.drawbars[0][0][4] = 3; // Also retain an inactive-bank edit.
    controls.drawbars[0][1][2] = 8;
    controls.drawbars[1][0][2] = 6;
    controls.selected_banks = {DrawbarBank::B, DrawbarBank::A};
    controls.expression = 0.25;
    controls.pedal_drawbars = {6, 0};
    CHECK(is_valid_control_snapshot(controls));
    return controls;
}

[[nodiscard]] SessionCommand manual_note(HostNoteKind kind, std::uint8_t bus,
                                         std::uint8_t note, std::int32_t id) {
    const auto velocity = static_cast<std::uint8_t>(kind == HostNoteKind::On ? 100 : 0);
    return PerformanceInputEvent{HostNoteEvent{0, kind, bus, kUiInputChannel, note, velocity, id}};
}

[[nodiscard]] std::uint64_t post_sound(Session& session, const ControlSnapshot& controls) {
    CHECK(session.post(controls));
    CHECK(session.post(manual_note(HostNoteKind::On, 0, kUpperNote, 11)));
    CHECK(session.post(manual_note(HostNoteKind::On, 1, kLowerNote, 12)));
    const auto pedal = session.post(PerformanceInputEvent{PedalNoteEvent{
        0, PedalNoteKind::On, 0, kUiInputChannel, PedalId{1}, 100, 13}});
    CHECK(pedal);
    return pedal.sequence;
}

void clean_render(const AudioDeviceDiagnostics& diagnostics) {
    CHECK(diagnostics.render_failures == 0);
    CHECK(diagnostics.format_failures == 0);
    CHECK(diagnostics.nonfinite_failures == 0);
    CHECK(diagnostics.nonfinite_samples == 0);
    CHECK(diagnostics.overrange_failures == 0);
    CHECK(diagnostics.overrange_samples == 0);
    CHECK(diagnostics.last_render_status == SessionStatus::Ok);
    CHECK(diagnostics.last_lifecycle_status == SessionStatus::Ok);
}

void obtained_spec(const AudioDeviceInfo& info, const AudioDeviceConfig& requested) {
    CHECK(info.open);
    CHECK(!info.running);
    CHECK(info.driver == "dummy");
    // The pinned dummy backend returns the exact request. Physical backend
    // negotiation may legally choose another value admitted by AudioDevice.
    CHECK(info.sample_rate == requested.sample_rate);
    CHECK(info.buffer_frames == requested.buffer_frames);
    CHECK(info.channels == 2);
    CHECK(info.sample_format == AUDIO_F32SYS);
    CHECK(info.buffer_bytes == static_cast<std::uint32_t>(info.buffer_frames) * 2U * sizeof(float));
    CHECK(info.device_name == (requested.device_name.empty() ? "Default output" : requested.device_name));
}

void refused_open(AudioDevice& device, Session& session, const RuntimeProfile& profile,
                  const AudioDeviceConfig& config) {
    const auto before = read(session);
    const auto callbacks = device.diagnostics().callback_count;
    std::string error;
    CHECK(!device.open(session, profile, config, error));
    CHECK(!error.empty());
    CHECK(!device.is_open());
    CHECK(!device.is_running());
    CHECK(device.diagnostics().callback_count == callbacks);
    same_music(read(session), before);
    ++totals.rejected_opens;
}

void test_uninitialized(const RuntimeProfile& profile) {
    CHECK((SDL_WasInit(SDL_INIT_AUDIO) & SDL_INIT_AUDIO) == 0);
    Session session;
    AudioDevice device;
    std::vector<std::string> names{"preserve this destination"};
    std::string error;
    CHECK(!AudioDevice::enumerate_output_devices(names, error));
    CHECK(names == std::vector<std::string>{"preserve this destination"});
    CHECK(!error.empty());
    CHECK(!device.start(error));
    CHECK(!error.empty());
    CHECK(device.stop() == SessionStatus::NotPrepared);
    refused_open(device, session, profile, {});
    device.close();
    CHECK(!device.info().open);
    CHECK(device.diagnostics().callback_count == 0);
}

class SdlAudio {
public:
    SdlAudio() {
        SDL_SetMainReady();
        CHECK(SDL_Init(SDL_INIT_AUDIO | SDL_INIT_TIMER) == 0);
        const auto* driver = SDL_GetCurrentAudioDriver();
        CHECK(driver != nullptr);
        CHECK(std::string_view{driver} == "dummy");
    }
    ~SdlAudio() { SDL_Quit(); }
    SdlAudio(const SdlAudio&) = delete;
    SdlAudio& operator=(const SdlAudio&) = delete;
};

[[nodiscard]] std::vector<std::string> test_enumeration() {
    std::vector<std::string> names{"replace stale entry"};
    std::string error = "clear on success";
    CHECK(AudioDevice::enumerate_output_devices(names, error));
    CHECK(error.empty());
    const auto count = SDL_GetNumAudioDevices(0);
    CHECK(count > 0);
    CHECK(names.size() == static_cast<std::size_t>(count));
    for (int index = 0; index < count; ++index) {
        const auto* name = SDL_GetAudioDeviceName(index, 0);
        CHECK(name != nullptr);
        CHECK(names[static_cast<std::size_t>(index)] == name);
        CHECK(!names[static_cast<std::size_t>(index)].empty());
    }
    return names;
}

void test_matrix(const RuntimeProfile& profile) {
    for (const auto rate : std::array{44100, 48000, 96000}) {
        for (const auto frames : std::array<std::uint16_t, 5>{128, 256, 512, 1024, 2048}) {
            Session session;
            AudioDevice device; // Destruction precedes Session and SDL shutdown.
            const AudioDeviceConfig config{{}, rate, frames, 731, 12345};
            std::string error = "clear on success";
            CHECK(device.open(session, profile, config, error));
            CHECK(error.empty());
            const auto info = device.info();
            obtained_spec(info, config);
            const auto initial = read(session);
            CHECK(initial.prepared && !initial.running);
            CHECK(initial.sample_rate == static_cast<double>(info.sample_rate));
            CHECK(initial.frame_clock == config.initial_frame);
            CHECK(initial.controls == ControlSnapshot{});
            CHECK(no_holds(initial));
            CHECK(device.diagnostics().callback_count == 0);

            auto controls = registration();
            const auto queued = post_sound(session, controls);
            stays_quiet(device, observation_window(info));
            same_music(read(session), initial); // Queued means not yet applied.
            Session replacement;
            CHECK(!device.open(replacement, profile, config, error));
            CHECK(!error.empty());
            CHECK(!read(replacement).prepared);
            CHECK(device.is_open() && !device.is_running());
            ++totals.rejected_opens;

            CHECK(device.start(error));
            CHECK(error.empty());
            CHECK(device.info().running);
            CHECK(!device.start(error));
            CHECK(!error.empty());
            wait_for("initial controls, manual/pedal notes and positive samples", [&] {
                SessionSnapshot snapshot;
                return session.read_snapshot(snapshot) && snapshot.last_applied_sequence == queued &&
                    snapshot.controls == controls && snapshot.held_keys[0][kUpperIndex] &&
                    snapshot.held_keys[1][kLowerIndex] && snapshot.held_pedals[0] &&
                    snapshot.frame_clock > config.initial_frame && snapshot.running &&
                    std::isfinite(snapshot.peak) && snapshot.peak > 0.0F &&
                    device.diagnostics().callback_count >= 2;
            });

            controls.expression = 0.125;
            CHECK(session.post(controls));
            const auto released = session.post(manual_note(HostNoteKind::Off, 1, kLowerNote, 12));
            CHECK(released);
            wait_for("live control update and independent lower-note release", [&] {
                SessionSnapshot snapshot;
                return session.read_snapshot(snapshot) && snapshot.controls == controls &&
                    snapshot.last_applied_sequence == released.sequence &&
                    snapshot.held_keys[0][kUpperIndex] && !snapshot.held_keys[1][kLowerIndex] &&
                    snapshot.held_pedals[0];
            });

            CHECK(device.stop() == SessionStatus::Ok);
            CHECK(device.is_open() && !device.is_running());
            const auto stopped = read(session);
            const auto before_restart = device.diagnostics();
            CHECK(!stopped.running && no_holds(stopped));
            CHECK(stopped.controls == controls);
            CHECK(stopped.peak == 0.0F);
            CHECK(stopped.fault_flags == 0 && stopped.rejected_commands == 0);
            CHECK(stopped.frame_clock == config.initial_frame + before_restart.rendered_frames);
            stays_quiet(device, observation_window(info));
            same_music(read(session), stopped);

            CHECK(device.start(error));
            wait_for("restart advances the existing clock with released notes", [&] {
                SessionSnapshot snapshot;
                return session.read_snapshot(snapshot) && snapshot.running && no_holds(snapshot) &&
                    snapshot.controls == controls && snapshot.peak == 0.0F &&
                    snapshot.frame_clock > stopped.frame_clock &&
                    device.diagnostics().callback_count >= before_restart.callback_count + 2;
            });
            CHECK(device.stop() == SessionStatus::Ok);
            const auto restarted = read(session);
            const auto final = device.diagnostics(); // Quiescent, coherent count comparison.
            clean_render(final);
            CHECK(final.rendered_frames == final.callback_count * info.buffer_frames);
            CHECK(restarted.frame_clock == config.initial_frame + final.rendered_frames);
            CHECK(restarted.controls == controls && no_holds(restarted));
            device.close();
            CHECK(!device.is_open() && !device.is_running());
            CHECK(!device.info().open);
            CHECK(device.diagnostics().callback_count == final.callback_count);
            ++totals.combinations;
            totals.matrix_callbacks += final.callback_count;
            totals.matrix_frames += final.rendered_frames;
            std::cout << "dummy obtained " << info.sample_rate << " Hz / " << info.buffer_frames
                      << " frames / F32 stereo: " << final.callback_count << " callbacks, "
                      << final.rendered_frames << " rendered frames\n";
        }
    }
}

void test_rejections_and_reopen(const RuntimeProfile& profile, const std::string& name) {
    Session session;
    AudioDevice device;
    for (const auto rate : std::array{-1, 0, 22050, 44101, 192000}) {
        AudioDeviceConfig config;
        config.sample_rate = rate;
        refused_open(device, session, profile, config);
    }
    for (const auto frames : std::array<std::uint16_t, 5>{0, 64, 127, 129, 4096}) {
        AudioDeviceConfig config;
        config.buffer_frames = frames;
        refused_open(device, session, profile, config);
    }
    AudioDeviceConfig config{name, 48000, 128, 19, 77};
    config.device_name = std::string{"bad\0name", 8};
    refused_open(device, session, profile, config);
    config.device_name = "__hammond_acceptance_nonexistent_output__";
    refused_open(device, session, profile, config);

    std::string error;
    const auto controls = registration();
    for (unsigned cycle = 0; cycle < 3; ++cycle) {
        config.device_name = cycle % 2 == 0 ? name : std::string{};
        const auto previous = device.diagnostics();
        CHECK(device.open(session, profile, config, error));
        CHECK(error.empty());
        obtained_spec(device.info(), config);
        CHECK(device.diagnostics().callback_count == previous.callback_count);
        CHECK(device.diagnostics().rendered_frames == previous.rendered_frames);
        CHECK(read(session).frame_clock == config.initial_frame);
        const auto posted = post_sound(session, controls);
        CHECK(device.start(error));
        wait_for("named/default reopen renders retained input", [&] {
            SessionSnapshot snapshot;
            return session.read_snapshot(snapshot) && snapshot.last_applied_sequence == posted &&
                snapshot.peak > 0.0F && snapshot.frame_clock > config.initial_frame;
        });
        device.close(); // Close a running device, without a preceding stop.
        const auto closed = read(session);
        CHECK(!closed.running && no_holds(closed));
        CHECK(closed.controls == controls);
        CHECK(device.diagnostics().callback_count > previous.callback_count);
        const auto after_close = device.diagnostics();
        stays_quiet(device, observation_window(device.info()));
        same_music(read(session), closed);
        CHECK(!device.start(error));
        CHECK(!error.empty());
        CHECK(device.stop() == SessionStatus::NotPrepared);
        device.close(); // Repeated close is harmless.
        CHECK(device.diagnostics().callback_count == after_close.callback_count);

        refused_open(device, session, RuntimeProfile{}, config);
        CHECK(device.diagnostics().last_lifecycle_status == SessionStatus::InvalidProfile);
        // The next successful open proves the failed partial SDL open was freed.
    }
    CHECK(device.open(session, profile, config, error));
    clean_render(device.diagnostics());
    device.close();
}

void test_real_render_failures(const RuntimeProfile& profile) {
    {
        Session session;
        AudioDevice device;
        const AudioDeviceConfig config{{}, 48000, 128, 0, kMaximum - 64};
        std::string error;
        CHECK(device.open(session, profile, config, error));
        CHECK(device.start(error));
        wait_for("real Session timeline-overflow rejection", [&] {
            return device.diagnostics().render_failures > 0;
        });
        CHECK(device.stop() == SessionStatus::Ok);
        const auto diagnostics = device.diagnostics();
        CHECK(diagnostics.render_failures == diagnostics.callback_count);
        CHECK(diagnostics.rendered_frames == 0);
        CHECK(diagnostics.format_failures == 0);
        CHECK(diagnostics.last_render_status == SessionStatus::TimelineOverflow);
        CHECK(read(session).frame_clock == config.initial_frame);
        totals.expected_render_failures += diagnostics.render_failures;
        stays_quiet(device, observation_window(device.info()));
    }
    {
        // Prepare and start consume the two real publication slots. The first
        // actual SDL callback reaches the Session's permanent exhaustion path.
        Session session{SessionLimits{kMaximum, 2}};
        AudioDevice device;
        std::string error;
        CHECK(device.open(session, profile, {{}, 48000, 128}, error));
        CHECK(device.start(error));
        wait_for("real Session publication-exhaustion rejection", [&] {
            return device.diagnostics().render_failures > 0;
        });
        CHECK(device.stop() == SessionStatus::SequenceExhausted);
        CHECK(!device.is_running());
        const auto diagnostics = device.diagnostics();
        CHECK(diagnostics.render_failures == diagnostics.callback_count);
        CHECK(diagnostics.rendered_frames == 0);
        CHECK(diagnostics.format_failures == 0);
        CHECK(diagnostics.last_render_status == SessionStatus::SequenceExhausted);
        CHECK(diagnostics.last_lifecycle_status == SessionStatus::SequenceExhausted);
        SessionSnapshot unavailable;
        CHECK(!session.read_snapshot(unavailable));
        totals.expected_render_failures += diagnostics.render_failures;
        stays_quiet(device, observation_window(device.info()));
    }
    {
        Session session{SessionLimits{kMaximum, 1}};
        AudioDevice device;
        std::string error;
        CHECK(device.open(session, profile, {{}, 48000, 128}, error));
        CHECK(!device.start(error));
        CHECK(!error.empty());
        CHECK(device.is_open() && !device.is_running());
        CHECK(device.diagnostics().last_lifecycle_status == SessionStatus::SequenceExhausted);
        stays_quiet(device, observation_window(device.info()));
        CHECK(device.diagnostics().callback_count == 0);
    }
}

void test_lifetime(const RuntimeProfile& profile) {
    const AudioDeviceConfig config{{}, 48000, 128};
    const auto controls = registration();
    for (unsigned cycle = 0; cycle < 4; ++cycle) {
        AudioDevice device;
        auto session = std::make_unique<Session>();
        std::string error;
        CHECK(device.open(*session, profile, config, error));
        const auto sequence = post_sound(*session, controls);
        CHECK(device.start(error));
        wait_for("callback before explicit close and Session destruction", [&] {
            SessionSnapshot snapshot;
            return session->read_snapshot(snapshot) && snapshot.last_applied_sequence == sequence &&
                snapshot.peak > 0.0F;
        });
        device.close();
        CHECK(!read(*session).running && no_holds(read(*session)));
        session.reset(); // Legal only after actual SDL callback join.
        stays_quiet(device, observation_window(device.info()));
        clean_render(device.diagnostics());
        ++totals.lifetime_cycles;
    }
    for (unsigned cycle = 0; cycle < 4; ++cycle) {
        Session session;
        {
            AudioDevice device;
            std::string error;
            CHECK(device.open(session, profile, config, error));
            const auto sequence = post_sound(session, controls);
            CHECK(device.start(error));
            wait_for("callback before active AudioDevice destruction", [&] {
                SessionSnapshot snapshot;
                return session.read_snapshot(snapshot) && snapshot.last_applied_sequence == sequence &&
                    snapshot.peak > 0.0F;
            });
        } // Actual device destructor must join before touching Session.
        const auto stopped = read(session);
        CHECK(!stopped.running && no_holds(stopped));
        CHECK(stopped.controls == controls);
        const auto deadline = Clock::now() + std::chrono::milliseconds{6};
        do {
            SDL_Delay(1);
            same_music(read(session), stopped);
        } while (Clock::now() < deadline);
        ++totals.lifetime_cycles;
    }
}

} // namespace

int main() {
    // Driver selection is an explicit fixture/CTest setting, never production
    // fallback or a hidden environment mutation in this test executable.
    const auto* selected = std::getenv("SDL_AUDIODRIVER");
    CHECK(selected != nullptr);
    CHECK(std::string_view{selected} == "dummy");
    RuntimeProfile profile;
    std::string error;
    CHECK(load_runtime_profile_file(HAMMOND_TEST_PROFILE, profile, error));
    test_uninitialized(profile);
    {
        const SdlAudio sdl;
        SDL_version version;
        SDL_GetVersion(&version);
        const auto names = test_enumeration();
        std::cout << "SDL " << static_cast<unsigned>(version.major) << '.'
                  << static_cast<unsigned>(version.minor) << '.'
                  << static_cast<unsigned>(version.patch) << ", driver=dummy, "
                  << names.size() << " copied output name(s)\n";
        test_matrix(profile);
        test_rejections_and_reopen(profile, names.front());
        test_real_render_failures(profile);
        test_lifetime(profile);
    } // All devices and Sessions are already destroyed before global quit.
    CHECK((SDL_WasInit(SDL_INIT_AUDIO) & SDL_INIT_AUDIO) == 0);
    CHECK(totals.combinations == 15);
    std::cout << "standalone actual-device acceptance: " << totals.combinations
              << " rate/buffer combinations, " << totals.matrix_callbacks << " matrix callbacks, "
              << totals.matrix_frames << " matrix frames (" << totals.matrix_frames * 2
              << " stereo samples), " << totals.rejected_opens << " rejected opens, "
              << totals.expected_render_failures << " expected real render faults, "
              << totals.lifetime_cycles << " close/destruction cycles\n";
    return 0;
}
