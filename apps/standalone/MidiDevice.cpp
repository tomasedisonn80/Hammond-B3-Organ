#include "MidiDevice.h"
#include "MidiInput.h"

#include <algorithm>
#include <atomic>
#include <chrono>
#include <cmath>
#include <exception>
#include <limits>
#include <span>
#include <thread>
#include <utility>

#if defined(HAMMOND_HAS_RTMIDI) && HAMMOND_HAS_RTMIDI == 1 && \
    (defined(_WIN32) || defined(__APPLE__) || \
     (defined(__linux__) && !defined(__ANDROID__)))
#define HAMMOND_MIDI_NATIVE 1
#include <RtMidi.h>
#else
#define HAMMOND_MIDI_NATIVE 0
#endif

namespace hammond::standalone {
namespace {

constexpr auto maximum_counter = std::numeric_limits<std::uint64_t>::max();

// Counters shared by input/error callbacks use lock-free atomic updates. These
// retries do not acquire a producer lock or wait for another callback to leave.
[[maybe_unused]] void increment(std::atomic<std::uint64_t>& counter) noexcept {
    auto value = counter.load(std::memory_order_relaxed);
    while (value != maximum_counter &&
           !counter.compare_exchange_weak(value, value + 1,
                                          std::memory_order_relaxed)) {}
}

[[nodiscard]] bool valid_port_name(std::string_view name) noexcept {
    return !name.empty() && name.size() <= kMidiMaximumPortNameBytes &&
           name.find('\0') == std::string_view::npos;
}

#if HAMMOND_MIDI_NATIVE
static_assert(std::atomic<bool>::is_always_lock_free,
              "MIDI callback admission requires lock-free Boolean atomics");
#if defined(_WIN32)
constexpr auto selected_api = RtMidi::WINDOWS_MM;
constexpr std::string_view selected_backend = "WinMM";
#elif defined(__APPLE__)
constexpr auto selected_api = RtMidi::MACOSX_CORE;
constexpr std::string_view selected_backend = "CoreMIDI";
#else
constexpr auto selected_api = RtMidi::LINUX_ALSA;
constexpr std::string_view selected_backend = "ALSA";
#endif

[[nodiscard]] bool compiled_api_present(std::string& error) {
    std::vector<RtMidi::Api> apis;
    RtMidi::getCompiledApi(apis);
    if (std::find(apis.begin(), apis.end(), selected_api) == apis.end()) {
        error = "The selected MIDI API is absent from the compiled RtMidi dependency";
        return false;
    }
    return true;
}

// This query is also used on the live client by the main-thread poll. It never
// mutates callback registration, selects a replacement port or truncates names.
[[nodiscard]] bool read_ports(RtMidiIn& input,
                              const std::atomic<bool>& backend_fault,
                              std::vector<std::string>& result,
                              std::string& error) {
    const auto count = input.getPortCount();
    if (backend_fault.load(std::memory_order_acquire)) {
        error = "MIDI backend reported an error while enumerating input ports";
        return false;
    }
    if (count > kMidiMaximumPorts) {
        error = "MIDI input enumeration exceeds the 256-port limit";
        return false;
    }
    std::vector<std::string> names;
    names.reserve(count);
    for (unsigned int index = 0; index < count; ++index) {
        auto name = input.getPortName(index);
        if (backend_fault.load(std::memory_order_acquire)) {
            error = "MIDI backend reported an error while reading an input port name";
            return false;
        }
        if (!valid_port_name(name)) {
            error = "MIDI backend returned an empty, overlong or NUL-containing port name";
            return false;
        }
        names.push_back(std::move(name));
    }
    result.swap(names);
    return true;
}

[[nodiscard]] bool arrival_time(std::uint64_t& nanoseconds) noexcept {
    // Check before converting to an unsigned integer. Using an exclusive 2^64
    // bound is safe even where long double has only double's precision.
    const auto elapsed = std::chrono::steady_clock::now().time_since_epoch();
    const auto value = std::chrono::duration<long double, std::nano>(elapsed).count();
    constexpr long double exclusive_limit = 18446744073709551616.0L;
    if (!std::isfinite(value) || value < 0 || value >= exclusive_limit) return false;
    nanoseconds = static_cast<std::uint64_t>(value);
    return true;
}

struct EnteredCallback {
    explicit EnteredCallback(std::atomic<std::uint32_t>& count) noexcept
        : count_(count) {
        count_.fetch_add(1, std::memory_order_acq_rel);
    }
    ~EnteredCallback() { count_.fetch_sub(1, std::memory_order_release); }
    std::atomic<std::uint32_t>& count_;
};

void enumeration_error(RtMidiError::Type, const std::string&, void* context) noexcept {
    static_cast<std::atomic<bool>*>(context)->store(true, std::memory_order_release);
}
#endif

} // namespace

class MidiDevice::Impl {
public:
    Impl() {
        info_.backend = MidiDevice::backend_name();
        info_.state = MidiDevice::backend_available() ? MidiDeviceState::Closed
                                                     : MidiDeviceState::Unavailable;
    }

    MidiDeviceInfo info_{};
    std::atomic<std::uint64_t> callback_messages_{0};
    std::atomic<std::uint64_t> forwarded_messages_{0};
    std::atomic<std::uint64_t> filtered_messages_{0};
    std::atomic<std::uint64_t> admission_failures_{0};
    std::atomic<std::uint64_t> backend_errors_{0};
    std::atomic<std::uint64_t> callback_contentions_{0};
    std::atomic<std::uint64_t> disconnects_{0};
    std::atomic<std::uint64_t> close_errors_{0};
    std::atomic<std::uint64_t> last_arrival_ns_{0};

#if HAMMOND_MIDI_NATIVE
    // This entire Impl is the stable callback context. Only main changes inbox_
    // and only before activation or after native closure and callback retirement.
    MidiInbox* inbox_{nullptr};
    std::atomic<bool> admission_{false};
    std::atomic<bool> backend_fault_{false};
    std::atomic<bool> closing_{false};
    std::atomic<bool> close_fault_{false};
    std::atomic<std::uint32_t> entered_{0};
    std::atomic_flag producer_ = ATOMIC_FLAG_INIT;
    bool callback_registered_{false};
    bool poisoned_{false};
    std::unique_ptr<RtMidiIn> input_{};

    void signal_backend_fault() noexcept {
        admission_.store(false, std::memory_order_release);
        backend_fault_.store(true, std::memory_order_release);
        if (inbox_ != nullptr) inbox_->signal_fault(MidiInboxFault::Backend);
    }

    static void input_callback(double, std::vector<unsigned char>* message,
                               void* context) noexcept {
        auto& self = *static_cast<Impl*>(context);
        EnteredCallback entered(self.entered_);
        increment(self.callback_messages_);
        if (!self.admission_.load(std::memory_order_acquire)) {
            increment(self.admission_failures_);
            return;
        }
        if (self.producer_.test_and_set(std::memory_order_acquire)) {
            increment(self.callback_contentions_);
            increment(self.admission_failures_);
            self.signal_backend_fault();
            return;
        }
        struct ProducerExit {
            std::atomic_flag& flag;
            ~ProducerExit() { flag.clear(std::memory_order_release); }
        } producer_exit{self.producer_};

        // Admission may have closed between the first check and producer entry.
        if (!self.admission_.load(std::memory_order_acquire)) {
            increment(self.admission_failures_);
            return;
        }
        std::uint64_t timestamp = 0;
        if (!arrival_time(timestamp)) {
            increment(self.admission_failures_);
            self.signal_backend_fault();
            return;
        }
        self.last_arrival_ns_.store(timestamp, std::memory_order_relaxed);
        if (message == nullptr || message->empty() || message->size() > 3) {
            increment(self.filtered_messages_);
            return;
        }
        const auto bytes = std::span<const std::uint8_t>(message->data(), message->size());
        const auto result = self.inbox_->push(bytes, timestamp);
        if (result == MidiPushResult::Accepted) {
            increment(self.forwarded_messages_);
        } else if (result == MidiPushResult::InvalidSize) {
            increment(self.filtered_messages_);
        } else {
            increment(self.admission_failures_);
            self.admission_.store(false, std::memory_order_release);
        }
    }

    static void error_callback(RtMidiError::Type, const std::string&,
                               void* context) noexcept {
        auto& self = *static_cast<Impl*>(context);
        EnteredCallback entered(self.entered_);
        increment(self.backend_errors_);
        if (self.closing_.load(std::memory_order_acquire)) {
            self.close_fault_.store(true, std::memory_order_release);
        }
        self.signal_backend_fault();
    }

    void poison_close() noexcept {
        if (!poisoned_) increment(close_errors_);
        poisoned_ = true;
        info_.state = MidiDeviceState::Faulted;
        signal_backend_fault();
    }

    void close_transport(MidiDeviceState final_state) noexcept {
        if (poisoned_) return;
        admission_.store(false, std::memory_order_release);
        if (inbox_ != nullptr) inbox_->signal_fault(MidiInboxFault::Disconnected);
        if (input_ == nullptr) {
            info_.state = final_state;
            return;
        }

        close_fault_.store(false, std::memory_order_release);
        closing_.store(true, std::memory_order_release);
        try {
            // Even a partially failed open must close with its context alive.
            input_->closePort();
            if (input_->isPortOpen()) close_fault_.store(true, std::memory_order_release);
        } catch (...) {
            increment(backend_errors_);
            close_fault_.store(true, std::memory_order_release);
        }

        // The OS call above has no portable timeout. This bound begins only
        // after it returns, and is never used on the audio or MIDI callback.
        const auto started = std::chrono::steady_clock::now();
        while (entered_.load(std::memory_order_acquire) != 0) {
            if (std::chrono::steady_clock::now() - started >=
                std::chrono::milliseconds(kMidiCloseGuardWaitMilliseconds)) {
                poison_close();
                return;
            }
            std::this_thread::yield();
        }
        if (close_fault_.load(std::memory_order_acquire)) {
            poison_close();
            return;
        }

        try {
            // RtMidi rewrites ordinary callback fields here. Native closure
            // and the guard must precede cancellation, including on failures.
            if (callback_registered_) input_->cancelCallback();
        } catch (...) {
            increment(backend_errors_);
            close_fault_.store(true, std::memory_order_release);
        }
        if (close_fault_.load(std::memory_order_acquire)) {
            poison_close();
            return;
        }
        callback_registered_ = false;
        // Keep error context and inbox alive through the dependency destructor.
        input_.reset();
        if (close_fault_.load(std::memory_order_acquire) ||
            entered_.load(std::memory_order_acquire) != 0) {
            poison_close();
            return;
        }
        inbox_ = nullptr;
        closing_.store(false, std::memory_order_release);
        info_.state = final_state;
    }
#endif
};

MidiDevice::MidiDevice() : impl_(std::make_unique<Impl>()) {}

MidiDevice::~MidiDevice() {
    close();
    if (!is_quiescent()) {
        // One exceptional quarantine, not the ordinary resource lifetime. The
        // caller must retain the inbox too and require process restart.
        (void)impl_.release();
    }
}

bool MidiDevice::backend_available() noexcept {
    return HAMMOND_MIDI_NATIVE != 0;
}

std::string_view MidiDevice::backend_name() noexcept {
#if HAMMOND_MIDI_NATIVE
    return selected_backend;
#else
    return "unavailable";
#endif
}

bool MidiDevice::enumerate_input_ports(std::vector<std::string>& destination,
                                       std::string& error) {
#if HAMMOND_MIDI_NATIVE
    try {
        if (!compiled_api_present(error)) return false;
        // Declared first so it also outlives error reporting during destruction.
        std::atomic<bool> backend_fault{false};
        auto input = std::make_unique<RtMidiIn>(selected_api, "Hammond B-3 enumeration", 0);
        input->setErrorCallback(enumeration_error, &backend_fault);
        if (input->getCurrentApi() != selected_api) {
            error = "RtMidi selected an unexpected MIDI API; fallback is refused";
            return false;
        }
        std::vector<std::string> names;
        const bool success = read_ports(*input, backend_fault, names, error);
        input.reset();
        if (backend_fault.load(std::memory_order_acquire)) {
            error = "MIDI backend reported an error during input enumeration or cleanup";
            return false;
        }
        if (!success) return false;
        destination.swap(names);
        error.clear();
        return true;
    } catch (const std::exception& exception) {
        error = std::string("MIDI input enumeration failed: ") + exception.what();
    } catch (...) {
        error = "MIDI input enumeration failed with an unknown backend exception";
    }
#else
    (void)destination;
    error = "MIDI backend is unavailable in this build";
#endif
    return false;
}

bool MidiDevice::open(MidiInbox& inbox, std::string_view exact_port_name,
                       std::string& error) {
    if (!backend_available()) {
        error = "MIDI backend is unavailable in this build";
        return false;
    }
    if (!valid_port_name(exact_port_name)) {
        error = "Select one exact MIDI input name of 1..1024 bytes without embedded NUL";
        return false;
    }
#if HAMMOND_MIDI_NATIVE
    auto& self = *impl_;
    if (self.poisoned_) {
        error = "MIDI shutdown previously failed; restart the process before reopening";
        return false;
    }
    if (self.input_ != nullptr || self.info_.state == MidiDeviceState::Open) {
        error = "MIDI input is already open";
        return false;
    }
    if (self.info_.generation == maximum_counter) {
        error = "MIDI connection generation is exhausted";
        return false;
    }
    if (inbox.faults() != 0 || inbox.pending() != 0) {
        error = "MIDI input requires an empty, fault-free, quiescent inbox";
        return false;
    }

    const auto previous_state = self.info_.state;
    bool activation_attempted = false;
    const auto reject = [&](std::string_view reason, MidiDeviceState state) {
        error = reason;
        if (activation_attempted) self.signal_backend_fault();
        self.close_transport(state);
        if (self.poisoned_) error += "; MIDI shutdown failed and process restart is required";
        return false;
    };
    try {
        std::string selected_name(exact_port_name);
        if (!compiled_api_present(error)) return false;
        self.backend_fault_.store(false, std::memory_order_release);
        self.input_ = std::make_unique<RtMidiIn>(selected_api, "Hammond B-3 MIDI input", 0);
        self.input_->setErrorCallback(Impl::error_callback, &self);
        if (self.input_->getCurrentApi() != selected_api) {
            return reject("RtMidi selected an unexpected MIDI API; fallback is refused",
                          MidiDeviceState::Faulted);
        }
        std::vector<std::string> names;
        if (!read_ports(*self.input_, self.backend_fault_, names, error)) {
            return reject(error, MidiDeviceState::Faulted);
        }
        if (std::count(names.begin(), names.end(), selected_name) != 1) {
            return reject("The exact MIDI input name is missing or ambiguous", previous_state);
        }
        const auto found = std::find(names.begin(), names.end(), selected_name);
        const auto index = static_cast<unsigned int>(found - names.begin());
        self.input_->ignoreTypes(true, true, true);
#if defined(_WIN32)
        self.input_->setBufferSize(1024, 0);
#endif
        self.input_->setCallback(Impl::input_callback, &self);
        self.callback_registered_ = true;
        if (self.backend_fault_.load(std::memory_order_acquire)) {
            return reject("MIDI backend failed while configuring input callbacks",
                          MidiDeviceState::Faulted);
        }
        if (self.input_->getPortName(index) != selected_name ||
            self.backend_fault_.load(std::memory_order_acquire)) {
            return reject("The selected MIDI input changed before opening", previous_state);
        }

        self.inbox_ = &inbox;
        activation_attempted = true;
        self.admission_.store(true, std::memory_order_release);
        self.input_->openPort(index, "Hammond B-3 MIDI input");
        if (self.input_->getCurrentApi() != selected_api || !self.input_->isPortOpen() ||
            self.backend_fault_.load(std::memory_order_acquire) || inbox.faults() != 0) {
            return reject("MIDI input activation failed or reported a backend/inbox fault",
                          MidiDeviceState::Faulted);
        }
        if (!read_ports(*self.input_, self.backend_fault_, names, error)) {
            return reject(error, MidiDeviceState::Faulted);
        }
        if (index >= names.size() || names[index] != selected_name ||
            std::count(names.begin(), names.end(), selected_name) != 1) {
            return reject("The selected MIDI input changed during opening",
                          MidiDeviceState::Faulted);
        }
        if (self.backend_fault_.load(std::memory_order_acquire) || inbox.faults() != 0 ||
            self.input_->getCurrentApi() != selected_api || !self.input_->isPortOpen()) {
            return reject("MIDI input faulted during activation", MidiDeviceState::Faulted);
        }
        self.info_.port_name.swap(selected_name);
        self.info_.opened_port_index = index;
        ++self.info_.generation;
        self.info_.state = MidiDeviceState::Open;
        error.clear();
        return true;
    } catch (const std::exception& exception) {
        increment(self.backend_errors_);
        return reject(std::string("MIDI input open failed: ") + exception.what(),
                      MidiDeviceState::Faulted);
    } catch (...) {
        increment(self.backend_errors_);
        return reject("MIDI input open failed with an unknown backend exception",
                      MidiDeviceState::Faulted);
    }
#else
    (void)inbox;
    return false;
#endif
}

bool MidiDevice::poll_connection(std::string& error) {
#if HAMMOND_MIDI_NATIVE
    auto& self = *impl_;
    if (!is_open()) {
        error = self.poisoned_ ? "MIDI shutdown failed; process restart is required"
                               : "MIDI input is not open";
        return false;
    }
    const auto fail = [&](std::string_view reason, MidiDeviceState state) {
        error = reason;
        if (state == MidiDeviceState::Disconnected) increment(self.disconnects_);
        else self.signal_backend_fault();
        self.close_transport(state);
        if (self.poisoned_) error += "; MIDI shutdown failed and process restart is required";
        return false;
    };
    try {
        if (self.backend_fault_.load(std::memory_order_acquire) ||
            (self.inbox_ != nullptr && self.inbox_->faults() != 0)) {
            return fail("MIDI input epoch has a latched backend or inbox fault",
                        MidiDeviceState::Faulted);
        }
        if (self.input_->getCurrentApi() != selected_api) {
            return fail("MIDI input no longer reports the selected API", MidiDeviceState::Faulted);
        }
        if (!self.input_->isPortOpen()) {
            return fail("MIDI native input port is closed", MidiDeviceState::Disconnected);
        }
        std::vector<std::string> names;
        if (!read_ports(*self.input_, self.backend_fault_, names, error)) {
            return fail(error, MidiDeviceState::Faulted);
        }
        if (std::count(names.begin(), names.end(), self.info_.port_name) != 1) {
            return fail("The selected MIDI input disappeared or became ambiguous",
                        MidiDeviceState::Disconnected);
        }
        if (self.backend_fault_.load(std::memory_order_acquire) ||
            (self.inbox_ != nullptr && self.inbox_->faults() != 0)) {
            return fail("MIDI input faulted during the connection check", MidiDeviceState::Faulted);
        }
        error.clear();
        return true;
    } catch (const std::exception& exception) {
        increment(self.backend_errors_);
        return fail(std::string("MIDI connection check failed: ") + exception.what(),
                    MidiDeviceState::Faulted);
    } catch (...) {
        increment(self.backend_errors_);
        return fail("MIDI connection check failed with an unknown backend exception",
                    MidiDeviceState::Faulted);
    }
#else
    error = "MIDI backend is unavailable in this build";
    return false;
#endif
}

void MidiDevice::close() noexcept {
#if HAMMOND_MIDI_NATIVE
    const auto state = impl_->info_.state == MidiDeviceState::Open
                           ? MidiDeviceState::Closed : impl_->info_.state;
    impl_->close_transport(state);
#endif
}

bool MidiDevice::is_open() const noexcept {
    return impl_->info_.state == MidiDeviceState::Open;
}

bool MidiDevice::is_quiescent() const noexcept {
#if HAMMOND_MIDI_NATIVE
    return !impl_->poisoned_ && impl_->input_ == nullptr &&
           impl_->entered_.load(std::memory_order_acquire) == 0;
#else
    return true;
#endif
}

MidiDeviceInfo MidiDevice::info() const {
    return impl_->info_;
}

MidiDeviceDiagnostics MidiDevice::diagnostics() const noexcept {
    return {impl_->callback_messages_.load(std::memory_order_relaxed),
            impl_->forwarded_messages_.load(std::memory_order_relaxed),
            impl_->filtered_messages_.load(std::memory_order_relaxed),
            impl_->admission_failures_.load(std::memory_order_relaxed),
            impl_->backend_errors_.load(std::memory_order_relaxed),
            impl_->callback_contentions_.load(std::memory_order_relaxed),
            impl_->disconnects_.load(std::memory_order_relaxed),
            impl_->close_errors_.load(std::memory_order_relaxed),
            impl_->last_arrival_ns_.load(std::memory_order_relaxed)};
}

} // namespace hammond::standalone
