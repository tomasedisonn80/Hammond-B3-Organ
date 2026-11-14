#pragma once

// Original test double for only the RtMidi 6.0.0 API used by MidiDevice.cpp.
// This header neither copies a native backend nor replaces adapter logic.
// The production .cpp is compiled separately with this include directory first.
// Scripted native operations are main-thread-only; captured callback/context
// pairs may be invoked by a test worker after an explicit lifetime barrier.

#include <array>
#include <cstddef>
#include <functional>
#include <memory>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

class RtMidiIn;

class RtMidiError : public std::runtime_error {
public:
    enum Type {
        WARNING, DEBUG_WARNING, UNSPECIFIED, NO_DEVICES_FOUND, INVALID_DEVICE,
        MEMORY_ERROR, INVALID_PARAMETER, INVALID_USE, DRIVER_ERROR, SYSTEM_ERROR,
        THREAD_ERROR
    };

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

namespace hammond_rtmidi_test {

#if defined(_WIN32)
inline constexpr auto platform_api = RtMidi::WINDOWS_MM;
inline constexpr const char* platform_name = "WinMM";
#elif defined(__APPLE__)
inline constexpr auto platform_api = RtMidi::MACOSX_CORE;
inline constexpr const char* platform_name = "CoreMIDI";
#else
inline constexpr auto platform_api = RtMidi::LINUX_ALSA;
inline constexpr const char* platform_name = "ALSA";
#endif

enum class Operation : std::size_t {
    Construct, ErrorCallback, Api, PortCount, PortName, Ignore, Buffer,
    Callback, Open, IsOpen, Close, CloseReturned, Cancel, Destroy, Count
};

struct Event {
    Operation operation;
    std::size_t ordinal;
};

struct Callbacks {
    RtMidiCallback input{nullptr};
    void* input_context{nullptr};
    RtMidiErrorCallback error{nullptr};
    void* error_context{nullptr};

    void message(std::vector<unsigned char>* bytes, double delta = 0.0) const {
        if (input == nullptr) throw std::logic_error("fake input callback not installed");
        input(delta, bytes, input_context);
    }

    void report_error(RtMidiError::Type type = RtMidiError::DRIVER_ERROR) const {
        if (error == nullptr) throw std::logic_error("fake error callback not installed");
        const std::string message = "injected native error (returned normally)";
        error(type, message, error_context);
    }
};

struct Scenario {
    std::vector<RtMidi::Api> compiled_apis{platform_api};
    RtMidi::Api reported_api{platform_api};
    std::vector<std::string> ports{"Controller"};
    std::function<void(RtMidiIn&, Operation, std::size_t)> on_call{};
    bool compiled_api_throws{false};
    bool open_succeeds{true};
    bool close_succeeds{true};
    std::size_t compiled_api_queries{0};
    std::size_t construction_attempts{0};
    std::size_t constructions{0};
    std::size_t destructions{0};
    std::size_t cancelled_while_open{0};
    std::size_t destroyed_while_open{0};
    std::array<std::size_t, static_cast<std::size_t>(Operation::Count)> calls{};
    std::vector<Event> events{};
    std::vector<RtMidi::Api> requested_apis{};
    std::vector<unsigned int> queue_limits{};
    std::vector<unsigned int> opened_indices{};
    std::array<bool, 3> ignored_types{false, false, false};
    std::array<unsigned int, 2> buffer_size{0, 0};
    unsigned int last_name_index{0};
    RtMidiIn* latest{nullptr};

    [[nodiscard]] std::size_t count(Operation operation) const {
        return calls[static_cast<std::size_t>(operation)];
    }
};

inline std::shared_ptr<Scenario> active_scenario{};

inline std::shared_ptr<Scenario> install() {
    auto result = std::make_shared<Scenario>();
    active_scenario = result;
    return result;
}

} // namespace hammond_rtmidi_test

inline void RtMidi::getCompiledApi(std::vector<Api>& apis) {
    auto& scenario = *hammond_rtmidi_test::active_scenario;
    ++scenario.compiled_api_queries;
    if (scenario.compiled_api_throws) throw RtMidiError("compiled API query failed");
    apis = scenario.compiled_apis;
}

class RtMidiIn : public RtMidi {
public:
    explicit RtMidiIn(Api api = UNSPECIFIED,
                      const std::string& client_name = "RtMidi Input Client",
                      unsigned int queue_size_limit = 100)
        : scenario_(hammond_rtmidi_test::active_scenario) {
        (void)client_name;
        ++scenario_->construction_attempts;
        scenario_->requested_apis.push_back(api);
        scenario_->queue_limits.push_back(queue_size_limit);
        step(hammond_rtmidi_test::Operation::Construct);
        ++scenario_->constructions;
        scenario_->latest = this;
    }

    ~RtMidiIn() noexcept {
        step(hammond_rtmidi_test::Operation::Destroy);
        if (open_) ++scenario_->destroyed_while_open;
        ++scenario_->destructions;
        if (scenario_->latest == this) scenario_->latest = nullptr;
    }

    RtMidiIn(const RtMidiIn&) = delete;
    RtMidiIn& operator=(const RtMidiIn&) = delete;

    void setErrorCallback(RtMidiErrorCallback callback, void* context) {
        callbacks_.error = callback;
        callbacks_.error_context = context;
        step(hammond_rtmidi_test::Operation::ErrorCallback);
    }

    [[nodiscard]] Api getCurrentApi() {
        step(hammond_rtmidi_test::Operation::Api);
        return scenario_->reported_api;
    }

    [[nodiscard]] unsigned int getPortCount() {
        step(hammond_rtmidi_test::Operation::PortCount);
        return static_cast<unsigned int>(scenario_->ports.size());
    }

    [[nodiscard]] std::string getPortName(unsigned int index = 0) {
        scenario_->last_name_index = index;
        step(hammond_rtmidi_test::Operation::PortName);
        return index < scenario_->ports.size() ? scenario_->ports[index] : std::string{};
    }

    void ignoreTypes(bool sysex = true, bool time = true, bool sense = true) {
        scenario_->ignored_types = {sysex, time, sense};
        step(hammond_rtmidi_test::Operation::Ignore);
    }

    void setBufferSize(unsigned int size, unsigned int count) {
        scenario_->buffer_size = {size, count};
        step(hammond_rtmidi_test::Operation::Buffer);
    }

    void setCallback(RtMidiCallback callback, void* context) {
        callbacks_.input = callback;
        callbacks_.input_context = context;
        step(hammond_rtmidi_test::Operation::Callback);
    }

    void openPort(unsigned int index = 0,
                  const std::string& port_name = "RtMidi Input") {
        (void)port_name;
        scenario_->opened_indices.push_back(index);
        open_ = scenario_->open_succeeds;
        // A real backend can activate, deliver a prefix, then report failure.
        step(hammond_rtmidi_test::Operation::Open);
    }

    [[nodiscard]] bool isPortOpen() {
        step(hammond_rtmidi_test::Operation::IsOpen);
        return open_;
    }

    void closePort() {
        step(hammond_rtmidi_test::Operation::Close);
        if (scenario_->close_succeeds) open_ = false;
        step(hammond_rtmidi_test::Operation::CloseReturned);
    }

    void cancelCallback() {
        if (open_) ++scenario_->cancelled_while_open;
        step(hammond_rtmidi_test::Operation::Cancel);
        callbacks_.input = nullptr;
        callbacks_.input_context = nullptr;
    }

    // Test-driver controls; these exist solely in the fake dependency header.
    [[nodiscard]] hammond_rtmidi_test::Callbacks captured_callbacks() const {
        return callbacks_;
    }
    void set_native_open(bool value) noexcept { open_ = value; }
    [[nodiscard]] bool native_open() const noexcept { return open_; }

private:
    void step(hammond_rtmidi_test::Operation operation) {
        auto& ordinal = scenario_->calls[static_cast<std::size_t>(operation)];
        ++ordinal;
        scenario_->events.push_back({operation, ordinal});
        if (scenario_->on_call) scenario_->on_call(*this, operation, ordinal);
    }

    std::shared_ptr<hammond_rtmidi_test::Scenario> scenario_;
    hammond_rtmidi_test::Callbacks callbacks_{};
    bool open_{false};
};
