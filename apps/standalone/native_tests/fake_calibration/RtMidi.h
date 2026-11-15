#pragma once

// A deliberately small, test-only RtMidi dependency. Production MidiDevice.cpp
// is compiled unchanged against this header for the native calibration gate.
// Discovery and the live client share one mutex-protected bounded event log;
// callback delivery occurs synchronously at native API boundaries. This is not
// a model of an operating-system MIDI driver or callback scheduling.

#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <memory>
#include <mutex>
#include <stdexcept>
#include <string>
#include <string_view>
#include <thread>
#include <vector>

class RtMidiError : public std::runtime_error {
public:
    enum Type { WARNING, UNSPECIFIED, DRIVER_ERROR };
    explicit RtMidiError(const std::string& message, Type type = UNSPECIFIED)
        : std::runtime_error(message), type_(type) {}
    [[nodiscard]] Type getType() const noexcept { return type_; }
private:
    Type type_;
};

using RtMidiCallback = void (*)(double, std::vector<unsigned char>*, void*);
using RtMidiErrorCallback = void (*)(RtMidiError::Type, const std::string&, void*);

class RtMidi {
public:
    enum Api {
        UNSPECIFIED, MACOSX_CORE, LINUX_ALSA, UNIX_JACK, WINDOWS_MM,
        RTMIDI_DUMMY, WEB_MIDI_API, NUM_APIS
    };
    static void getCompiledApi(std::vector<Api>& apis);
};

namespace hammond_calibration_fixture {

#if defined(_WIN32)
inline constexpr auto platform_api = RtMidi::WINDOWS_MM;
#elif defined(__APPLE__)
inline constexpr auto platform_api = RtMidi::MACOSX_CORE;
#else
inline constexpr auto platform_api = RtMidi::LINUX_ALSA;
#endif

enum class Scenario { Identical, Calibration, Route, Port, NoInput, FailedReopen, FaultRetry };
enum class Operation : std::size_t {
    CompiledApi, Construct, ErrorCallback, Api, PortCount, PortName, Ignore,
    Buffer, Callback, Open, IsOpen, Message, Error, Close, Closed, Cancel, Destroy
};
inline constexpr std::array<std::string_view, 17> operation_names{
    "compiled-api", "construct", "error-callback", "api", "port-count", "port-name",
    "ignore", "buffer", "callback", "open", "is-open", "message", "error", "close",
    "closed", "cancel", "destroy"};
inline constexpr std::array<std::string_view, 2> port_names{"Controller", "Alternate"};

struct Event {
    Operation operation{};
    std::uint32_t client{0}, open_attempt{0}, poll{0}, port{0};
    bool transport{false}, registered{false};
    std::array<unsigned int, 3> bytes{};
    bool worker{false};
};

struct State {
    explicit State(Scenario value) : scenario(value) {}
    std::mutex mutex;
    const std::thread::id main_thread{std::this_thread::get_id()};
    Scenario scenario;
    std::array<Event, 4096> events{};
    std::size_t event_count{0}, dropped_events{0};
    std::uint32_t clients{0}, constructions{0}, destructions{0};
    std::uint32_t opens{0}, closes{0}, cancellations{0};
    std::uint32_t offered_messages{0}, delivered_messages{0}, errors{0};
    std::uint32_t cancelled_while_open{0}, destroyed_while_open{0};
    std::uint32_t destroyed_with_input_callback{0}, invalid_callbacks{0};
    void append(const Event& event) noexcept {
        if (event_count == events.size()) { ++dropped_events; return; }
        events[event_count] = event;
        events[event_count].worker = std::this_thread::get_id() != main_thread;
        ++event_count;
    }
};

// Installed once before real application startup, reset after its discovery
// worker and audio callback have joined. Concurrent clients only read this ptr.
inline std::shared_ptr<State> installed;
inline std::shared_ptr<State> install(Scenario scenario) {
    auto result = std::make_shared<State>(scenario);
    installed = result;
    return result;
}

} // namespace hammond_calibration_fixture

inline void RtMidi::getCompiledApi(std::vector<Api>& apis) {
    const auto state = hammond_calibration_fixture::installed;
    if (!state) throw std::logic_error("calibration fixture was not installed");
    const std::lock_guard lock(state->mutex);
    state->append({hammond_calibration_fixture::Operation::CompiledApi});
    apis = {hammond_calibration_fixture::platform_api};
}

class RtMidiIn : public RtMidi {
public:
    explicit RtMidiIn(Api api = UNSPECIFIED,
                      const std::string& client_name = "RtMidi Input Client",
                      unsigned int queue_size_limit = 100)
        : state_(hammond_calibration_fixture::installed), api_(api),
          transport_(client_name == "Hammond B-3 MIDI input") {
        if (!state_) throw std::logic_error("calibration fixture was not installed");
        if (queue_size_limit != 0) throw std::logic_error("unexpected native queue configuration");
        const std::lock_guard lock(state_->mutex);
        client_ = ++state_->clients;
        ++state_->constructions;
        record(hammond_calibration_fixture::Operation::Construct);
    }

    ~RtMidiIn() noexcept {
        const std::lock_guard lock(state_->mutex);
        if (open_) ++state_->destroyed_while_open;
        if (callback_ != nullptr) ++state_->destroyed_with_input_callback;
        ++state_->destructions;
        record(hammond_calibration_fixture::Operation::Destroy);
    }

    RtMidiIn(const RtMidiIn&) = delete;
    RtMidiIn& operator=(const RtMidiIn&) = delete;

    void setErrorCallback(RtMidiErrorCallback callback, void* context) {
        const std::lock_guard lock(state_->mutex);
        error_callback_ = callback;
        error_context_ = context;
        record(hammond_calibration_fixture::Operation::ErrorCallback);
    }
    [[nodiscard]] Api getCurrentApi() {
        const std::lock_guard lock(state_->mutex);
        record(hammond_calibration_fixture::Operation::Api);
        return api_;
    }
    [[nodiscard]] unsigned int getPortCount() {
        const std::lock_guard lock(state_->mutex);
        record(hammond_calibration_fixture::Operation::PortCount);
        return static_cast<unsigned int>(hammond_calibration_fixture::port_names.size());
    }
    [[nodiscard]] std::string getPortName(unsigned int index = 0) {
        const std::lock_guard lock(state_->mutex);
        record(hammond_calibration_fixture::Operation::PortName);
        if (index >= hammond_calibration_fixture::port_names.size())
            throw RtMidiError("fixture port index outside declared inventory");
        return std::string{hammond_calibration_fixture::port_names[index]};
    }
    void ignoreTypes(bool sysex = true, bool time = true, bool sense = true) {
        const std::lock_guard lock(state_->mutex);
        if (!sysex || !time || !sense) throw std::logic_error("unexpected native filters");
        record(hammond_calibration_fixture::Operation::Ignore);
    }
    void setBufferSize(unsigned int size, unsigned int count) {
        const std::lock_guard lock(state_->mutex);
        if (size != 1024 || count != 0) throw std::logic_error("unexpected native buffer configuration");
        record(hammond_calibration_fixture::Operation::Buffer);
    }
    void setCallback(RtMidiCallback callback, void* context) {
        const std::lock_guard lock(state_->mutex);
        callback_ = callback;
        context_ = context;
        record(hammond_calibration_fixture::Operation::Callback);
    }
    void openPort(unsigned int index = 0, const std::string& name = "RtMidi Input") {
        (void)name;
        const std::lock_guard lock(state_->mutex);
        if (!transport_ || open_ || index >= hammond_calibration_fixture::port_names.size())
            throw std::logic_error("invalid fixture activation");
        port_ = index;
        open_ = true;
        attempt_ = ++state_->opens;
        record(hammond_calibration_fixture::Operation::Open);
        if (attempt_ == 1) {
            emit(0xB0, 11, 35);
            emit(0x90, 60, 100);
            emit(0x91, 64, 100);
            emit(0x92, 38, 100); // Existing pedal 3 (wire note 36 is pedal 1).
        } else if (state_->scenario == hammond_calibration_fixture::Scenario::FailedReopen && attempt_ == 2) {
            // A backend may deliver an admitted prefix and then fail activation.
            // These bytes must never reach the musical decoder after failure.
            emit(0xB0, 11, 110);
            emit(0x90, 72, 100);
            emit(0x91, 65, 100);
            report_error();
        }
    }
    [[nodiscard]] bool isPortOpen() {
        const std::lock_guard lock(state_->mutex);
        if (open_) ++polls_;
        record(hammond_calibration_fixture::Operation::IsOpen);
        // The first two queries belong to real MidiDevice activation. A later
        // periodic native poll supplies a separate, observable next-CC11 turn.
        if (open_ && polls_ >= 3 && !post_open_sent_) {
            post_open_sent_ = true;
            using Scenario = hammond_calibration_fixture::Scenario;
            if (attempt_ == 1 && state_->scenario == Scenario::FaultRetry) {
                emit(0xB0, 11, 110);
                emit(0x90, 72, 100);
                report_error();
            } else if (attempt_ > 1) {
                if (state_->scenario == Scenario::Route) {
                    emit(0xB0, 11, 110); // Retired wire route must be ignored.
                    emit(0x90, 74, 100);
                    emit(0xB3, 11, 60); // New wire channel 4.
                    emit(0x93, 67, 100);
                } else {
                    const unsigned int raw = state_->scenario == Scenario::Port ? 60U : 35U;
                    emit(0xB0, 11, raw);
                    emit(0x90, 67, 100);
                }
            }
        }
        return open_;
    }
    void closePort() {
        const std::lock_guard lock(state_->mutex);
        ++state_->closes;
        record(hammond_calibration_fixture::Operation::Close);
        if (open_) {
            // MidiDevice must close admission before calling into the backend.
            // Both packets are observable offers, not assumed admitted packets.
            emit(0xB0, 11, 127);
            emit(0x90, 75, 100);
        }
        open_ = false;
        record(hammond_calibration_fixture::Operation::Closed);
    }
    void cancelCallback() {
        const std::lock_guard lock(state_->mutex);
        if (open_) ++state_->cancelled_while_open;
        ++state_->cancellations;
        record(hammond_calibration_fixture::Operation::Cancel);
        callback_ = nullptr;
        context_ = nullptr;
    }

private:
    void record(hammond_calibration_fixture::Operation operation,
                std::array<unsigned int, 3> bytes = {}) noexcept {
        state_->append({operation, client_, attempt_, polls_, port_, transport_, callback_ != nullptr, bytes});
    }
    void emit(unsigned int status, unsigned int data1, unsigned int data2) {
        ++state_->offered_messages;
        record(hammond_calibration_fixture::Operation::Message, {status, data1, data2});
        if (callback_ == nullptr) { ++state_->invalid_callbacks; return; }
        std::vector<unsigned char> bytes{static_cast<unsigned char>(status),
            static_cast<unsigned char>(data1), static_cast<unsigned char>(data2)};
        callback_(0.0, &bytes, context_);
        ++state_->delivered_messages;
    }
    void report_error() {
        ++state_->errors;
        record(hammond_calibration_fixture::Operation::Error);
        if (error_callback_ == nullptr) { ++state_->invalid_callbacks; return; }
        error_callback_(RtMidiError::DRIVER_ERROR, "injected calibration fixture backend error", error_context_);
    }

    std::shared_ptr<hammond_calibration_fixture::State> state_;
    Api api_;
    std::uint32_t client_{0}, attempt_{0}, polls_{0};
    unsigned int port_{0};
    bool transport_{false}, open_{false}, post_open_sent_{false};
    RtMidiCallback callback_{nullptr};
    void* context_{nullptr};
    RtMidiErrorCallback error_callback_{nullptr};
    void* error_context_{nullptr};
};
