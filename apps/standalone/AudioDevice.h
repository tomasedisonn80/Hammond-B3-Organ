#pragma once

#include "Session.h"

#include <SDL_audio.h>

#include <atomic>
#include <cstdint>
#include <string>
#include <vector>

namespace hammond::standalone {

struct AudioDeviceConfig {
    std::string device_name{}; // Empty selects SDL's default output.
    int sample_rate{48000}; // 44100, 48000 or 96000 Hz.
    std::uint16_t buffer_frames{512}; // 128, 256, 512, 1024 or 2048 frames.
    std::uint64_t seed{0};
    std::uint64_t initial_frame{0};
};

struct AudioDeviceInfo {
    std::string device_name{}; // Requested name, or "Default output".
    std::string driver{};
    int sample_rate{0}; // Obtained callback spec, not a hardware latency claim.
    std::uint16_t buffer_frames{0};
    std::uint8_t channels{0};
    std::uint16_t sample_format{0};
    std::uint32_t buffer_bytes{0};
    bool open{false};
    bool running{false};
};

// Lifetime counters saturate; reopening does not erase earlier faults. Each
// failure count is callbacks; sample counts include both stereo channels.
// Independent atomic reads can span a callback; this is not a coherent Session
// snapshot. rendered_frames counts Session successes, including later silence.
struct AudioDeviceDiagnostics {
    std::uint64_t callback_count{0};
    std::uint64_t rendered_frames{0};
    std::uint64_t render_failures{0};
    std::uint64_t format_failures{0};
    std::uint64_t overrange_failures{0};
    std::uint64_t overrange_samples{0};
    std::uint64_t nonfinite_failures{0};
    std::uint64_t nonfinite_samples{0};
    SessionStatus last_render_status{SessionStatus::Ok}; // Latest render error.
    SessionStatus last_lifecycle_status{SessionStatus::Ok};
};

// Main-thread-owned SDL transport, with one SDL-serialized render callback.
// The application owns SDL_Init/SDL_Quit and must retain audio initialization
// and the Session until this device is closed. It must quiesce snapshot readers
// before lifecycle calls, as required by Session. Only diagnostics() may be
// called concurrently with lifecycle operations. No public call is for use
// from the callback. Destruction closes and joins the actual SDL device first.
class AudioDevice {
public:
    AudioDevice() = default;
    ~AudioDevice();
    AudioDevice(const AudioDevice&) = delete;
    AudioDevice& operator=(const AudioDevice&) = delete;
    AudioDevice(AudioDevice&&) = delete;
    AudioDevice& operator=(AudioDevice&&) = delete;

    // SDL audio must already be initialized. Copies names outside processing;
    // failure preserves destination. There is no implicit dummy-driver retry.
    [[nodiscard]] static bool enumerate_output_devices(
        std::vector<std::string>& destination, std::string& error);

    // Refuses an already-open device. Opens paused, validates the obtained
    // float32-native stereo spec, then prepares Session with that exact rate
    // and frame bound. Failure closes the partial SDL device. The app explicitly
    // posts initial/saved controls between this call and start().
    [[nodiscard]] bool open(Session& session, const RuntimeProfile& profile,
                            const AudioDeviceConfig& config, std::string& error);
    [[nodiscard]] bool start(std::string& error);

    // Pause and wait for callback completion BEFORE Session::stop(). Keeps the
    // device open for start(); releases notes and pending commands through Session.
    [[nodiscard]] SessionStatus stop() noexcept;
    // SDL_CloseAudioDevice joins callbacks BEFORE Session::stop and detachment.
    void close() noexcept;

    [[nodiscard]] bool is_open() const noexcept { return device_id_ != 0; }
    [[nodiscard]] bool is_running() const noexcept { return running_; }
    [[nodiscard]] AudioDeviceInfo info() const;
    [[nodiscard]] AudioDeviceDiagnostics diagnostics() const noexcept;

private:
    static void SDLCALL audio_callback(void* userdata, Uint8* stream,
                                      int byte_count) noexcept;
    void render_callback(Uint8* stream, int byte_count) noexcept;

    SDL_AudioDeviceID device_id_{0};
    Session* session_{nullptr};
    std::uint32_t callback_frame_bound_{0};
    std::uint32_t callback_byte_bound_{0};
    bool running_{false};
    AudioDeviceInfo info_{};

    std::atomic<std::uint64_t> callback_count_{0};
    std::atomic<std::uint64_t> rendered_frames_{0};
    std::atomic<std::uint64_t> render_failures_{0};
    std::atomic<std::uint64_t> format_failures_{0};
    std::atomic<std::uint64_t> overrange_failures_{0};
    std::atomic<std::uint64_t> overrange_samples_{0};
    std::atomic<std::uint64_t> nonfinite_failures_{0};
    std::atomic<std::uint64_t> nonfinite_samples_{0};
    std::atomic<SessionStatus> last_render_status_{SessionStatus::Ok};
    std::atomic<SessionStatus> last_lifecycle_status_{SessionStatus::Ok};
};

} // namespace hammond::standalone
