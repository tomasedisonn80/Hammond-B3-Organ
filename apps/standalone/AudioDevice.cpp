#include "AudioDevice.h"

#include <SDL.h>

#include <cmath>
#include <cstring>
#include <limits>
#include <utility>

namespace hammond::standalone {
namespace {

static_assert(sizeof(float) == 4 && std::numeric_limits<float>::is_iec559);
static_assert(std::atomic<std::uint64_t>::is_always_lock_free,
              "SDL callback diagnostics require lock-free 64-bit atomics");
static_assert(std::atomic<SessionStatus>::is_always_lock_free,
              "SDL callback diagnostics require lock-free status atomics");
constexpr std::size_t kChannels = 2;
constexpr std::size_t kFrameBytes = sizeof(float) * kChannels;

[[nodiscard]] bool supported_buffer(std::uint16_t frames) noexcept {
    return frames == 128 || frames == 256 || frames == 512 ||
           frames == 1024 || frames == 2048;
}

[[nodiscard]] const char* session_status_name(SessionStatus status) noexcept {
    switch (status) {
    case SessionStatus::Ok: return "ok";
    case SessionStatus::NotPrepared: return "not_prepared";
    case SessionStatus::AlreadyRunning: return "already_running";
    case SessionStatus::NotRunning: return "not_running";
    case SessionStatus::InvalidSpec: return "invalid_spec";
    case SessionStatus::InvalidProfile: return "invalid_profile";
    case SessionStatus::InvalidBuffer: return "invalid_buffer";
    case SessionStatus::BlockTooLarge: return "block_too_large";
    case SessionStatus::TimelineOverflow: return "timeline_overflow";
    case SessionStatus::InvalidCommand: return "invalid_command";
    case SessionStatus::QueueFull: return "queue_full";
    case SessionStatus::RecoveryPending: return "recovery_pending";
    case SessionStatus::SequenceExhausted: return "sequence_exhausted";
    case SessionStatus::CoreFailure: return "core_failure";
    }
    return "unknown";
}

// Each counter has exactly one serialized callback writer, and no resetter.
// A bounded load/store suffices; readers never contend on a compare/exchange.
void add_saturating(std::atomic<std::uint64_t>& counter,
                    std::uint64_t amount = 1) noexcept {
    const auto old = counter.load(std::memory_order_relaxed);
    constexpr auto maximum = std::numeric_limits<std::uint64_t>::max();
    counter.store(amount > maximum - old ? maximum : old + amount,
                  std::memory_order_relaxed);
}

void silence(Uint8* stream, int byte_count) noexcept {
    // SDL supplies the actual writable byte extent. Clear even a rejected
    // non-frame-aligned/oversized buffer without forming a float span.
    if (stream != nullptr && byte_count > 0) {
        std::memset(stream, 0, static_cast<std::size_t>(byte_count));
    }
}

struct PendingOutput {
    SDL_AudioDeviceID id{0};
    ~PendingOutput() {
        if (id != 0) {
            SDL_CloseAudioDevice(id);
        }
    }
};

} // namespace

AudioDevice::~AudioDevice() {
    close();
}

bool AudioDevice::enumerate_output_devices(std::vector<std::string>& destination,
                                            std::string& error) {
    if ((SDL_WasInit(SDL_INIT_AUDIO) & SDL_INIT_AUDIO) == 0) {
        error = "SDL audio is not initialized by the application";
        return false;
    }
    const int count = SDL_GetNumAudioDevices(0);
    if (count < 0) {
        error = std::string("Cannot enumerate output devices: ") + SDL_GetError();
        return false;
    }
    std::vector<std::string> names;
    names.reserve(static_cast<std::size_t>(count));
    for (int index = 0; index < count; ++index) {
        const char* name = SDL_GetAudioDeviceName(index, 0);
        if (name == nullptr) {
            error = std::string("Cannot read an output device name: ") + SDL_GetError();
            return false;
        }
        names.emplace_back(name);
    }
    destination.swap(names);
    error.clear();
    return true;
}

bool AudioDevice::open(Session& session, const RuntimeProfile& profile,
                       const AudioDeviceConfig& config, std::string& error) {
    if (is_open()) {
        error = "Audio output is already open; close it before reopening";
        return false;
    }
    if ((SDL_WasInit(SDL_INIT_AUDIO) & SDL_INIT_AUDIO) == 0) {
        error = "SDL audio is not initialized by the application";
        return false;
    }
    if (!is_supported_sample_rate(static_cast<double>(config.sample_rate)) ||
        !supported_buffer(config.buffer_frames)) {
        error = "Audio requires 44100/48000/96000 Hz and 128/256/512/1024/2048 frames";
        return false;
    }
    if (config.device_name.find('\0') != std::string::npos) {
        error = "An audio device name cannot contain a null byte";
        return false;
    }

    AudioDeviceInfo candidate;
    candidate.device_name = config.device_name.empty() ? "Default output" : config.device_name;
    if (const char* driver = SDL_GetCurrentAudioDriver()) {
        candidate.driver = driver;
    }
    SDL_AudioSpec desired{};
    desired.freq = config.sample_rate;
    desired.format = AUDIO_F32SYS;
    desired.channels = static_cast<Uint8>(kChannels);
    desired.samples = config.buffer_frames;
    desired.callback = &AudioDevice::audio_callback;
    desired.userdata = this;
    SDL_AudioSpec obtained{};
    PendingOutput pending{SDL_OpenAudioDevice(
        config.device_name.empty() ? nullptr : config.device_name.c_str(), 0,
        &desired, &obtained, SDL_AUDIO_ALLOW_ANY_CHANGE)};
    if (pending.id == 0) {
        error = std::string("Cannot open audio output: ") + SDL_GetError();
        return false;
    }
    // OpenAudioDevice starts paused. Admit its actual callback format instead
    // of requesting hidden SDL format/rate conversions to a preferred spec.
    if (obtained.format != AUDIO_F32SYS || obtained.channels != kChannels ||
        !is_supported_sample_rate(static_cast<double>(obtained.freq)) ||
        !supported_buffer(obtained.samples) || obtained.silence != 0 ||
        obtained.size != static_cast<std::size_t>(obtained.samples) * kFrameBytes) {
        error = "Obtained audio must be native float32 stereo at a supported rate and buffer size";
        return false;
    }

    const ProcessSpec spec{static_cast<double>(obtained.freq), obtained.samples,
                           config.seed, config.initial_frame};
    const auto status = session.prepare(profile, spec);
    last_lifecycle_status_.store(status, std::memory_order_relaxed);
    if (status != SessionStatus::Ok) {
        error = std::string("Cannot prepare audio Session: ") + session_status_name(status);
        return false;
    }

    candidate.sample_rate = obtained.freq;
    candidate.buffer_frames = obtained.samples;
    candidate.channels = obtained.channels;
    candidate.sample_format = obtained.format;
    candidate.buffer_bytes = obtained.size;
    info_ = std::move(candidate);
    session_ = &session;
    callback_frame_bound_ = obtained.samples;
    callback_byte_bound_ = obtained.size;
    running_ = false;
    device_id_ = std::exchange(pending.id, 0);
    error.clear();
    return true;
}

bool AudioDevice::start(std::string& error) {
    if (!is_open() || session_ == nullptr) {
        error = "Audio output is not open";
        return false;
    }
    if (running_) {
        error = "Audio output is already running";
        return false;
    }
    const auto status = session_->start();
    last_lifecycle_status_.store(status, std::memory_order_relaxed);
    if (status != SessionStatus::Ok) {
        error = std::string("Cannot start audio Session: ") + session_status_name(status);
        return false;
    }
    running_ = true;
    SDL_PauseAudioDevice(device_id_, 0);
    error.clear();
    return true;
}

SessionStatus AudioDevice::stop() noexcept {
    if (!is_open() || session_ == nullptr) {
        return SessionStatus::NotPrepared;
    }
    SDL_PauseAudioDevice(device_id_, 1);
    // SDL's lock waits for any in-flight callback; the paused device cannot
    // begin another one after unlock. Neither lock is taken by our callback.
    SDL_LockAudioDevice(device_id_);
    SDL_UnlockAudioDevice(device_id_);
    running_ = false;
    const auto status = session_->stop();
    last_lifecycle_status_.store(status, std::memory_order_relaxed);
    return status;
}

void AudioDevice::close() noexcept {
    if (device_id_ == 0) {
        return;
    }
    // Closing waits for and joins actual callbacks before touching Session.
    SDL_CloseAudioDevice(device_id_);
    device_id_ = 0;
    running_ = false;
    if (session_ != nullptr) {
        last_lifecycle_status_.store(session_->stop(), std::memory_order_relaxed);
    }
    session_ = nullptr;
    callback_frame_bound_ = 0;
    callback_byte_bound_ = 0;
}

AudioDeviceInfo AudioDevice::info() const {
    auto result = info_;
    result.open = is_open();
    result.running = running_;
    return result;
}

AudioDeviceDiagnostics AudioDevice::diagnostics() const noexcept {
    return {callback_count_.load(std::memory_order_relaxed),
            rendered_frames_.load(std::memory_order_relaxed),
            render_failures_.load(std::memory_order_relaxed),
            format_failures_.load(std::memory_order_relaxed),
            overrange_failures_.load(std::memory_order_relaxed),
            overrange_samples_.load(std::memory_order_relaxed),
            nonfinite_failures_.load(std::memory_order_relaxed),
            nonfinite_samples_.load(std::memory_order_relaxed),
            last_render_status_.load(std::memory_order_relaxed),
            last_lifecycle_status_.load(std::memory_order_relaxed)};
}

void SDLCALL AudioDevice::audio_callback(void* userdata, Uint8* stream,
                                        int byte_count) noexcept {
    if (userdata == nullptr) {
        silence(stream, byte_count);
        return;
    }
    static_cast<AudioDevice*>(userdata)->render_callback(stream, byte_count);
}

void AudioDevice::render_callback(Uint8* stream, int byte_count) noexcept {
    add_saturating(callback_count_);
    if (session_ == nullptr || stream == nullptr || byte_count <= 0 ||
        reinterpret_cast<std::uintptr_t>(stream) % alignof(float) != 0 ||
        static_cast<std::size_t>(byte_count) % kFrameBytes != 0 ||
        static_cast<std::uint64_t>(byte_count) > callback_byte_bound_) {
        add_saturating(format_failures_);
        silence(stream, byte_count);
        return;
    }
    const auto frames = static_cast<std::uint32_t>(
        static_cast<std::size_t>(byte_count) / kFrameBytes);
    if (frames > callback_frame_bound_) {
        add_saturating(format_failures_);
        silence(stream, byte_count);
        return;
    }
    auto output = std::span<float>{reinterpret_cast<float*>(stream),
                                   static_cast<std::size_t>(frames) * kChannels};
    const auto result = session_->render(frames, output);
    if (!result.ok() || result.frames_rendered != frames) {
        add_saturating(render_failures_);
        last_render_status_.store(result.ok() ? SessionStatus::CoreFailure : result.status,
                                   std::memory_order_relaxed);
        silence(stream, byte_count);
        return;
    }
    add_saturating(rendered_frames_, frames);
    std::uint64_t overrange = 0;
    std::uint64_t nonfinite = 0;
    for (auto& sample : output) {
        if (!std::isfinite(sample)) {
            ++nonfinite;
        } else if (sample > 1.0F) {
            sample = 1.0F;
            ++overrange;
        } else if (sample < -1.0F) {
            sample = -1.0F;
            ++overrange;
        }
    }
    if (overrange != 0) {
        add_saturating(overrange_failures_);
        add_saturating(overrange_samples_, overrange);
    }
    if (nonfinite != 0) {
        add_saturating(nonfinite_failures_);
        add_saturating(nonfinite_samples_, nonfinite);
        silence(stream, byte_count);
    }
}

} // namespace hammond::standalone
