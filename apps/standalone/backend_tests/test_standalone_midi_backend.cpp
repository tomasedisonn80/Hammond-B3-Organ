#include "MidiDevice.h"
#include "MidiInput.h"
#include <RtMidi.h>

#include <algorithm>
#include <array>
#include <chrono>
#include <condition_variable>
#include <cstddef>
#include <cstdint>
#include <exception>
#include <iostream>
#include <limits>
#include <memory>
#include <mutex>
#include <stdexcept>
#include <string>
#include <string_view>
#include <thread>
#include <utility>
#include <vector>

namespace {

using namespace hammond::standalone;
namespace native = hammond_rtmidi_test;
using Op = native::Operation;

static_assert(kMidiDeviceModelId == "standalone-rtmidi-short-input-v1");
static_assert(kMidiMaximumPorts == 256);
static_assert(kMidiMaximumPortNameBytes == 1024);
static_assert(kMidiCloseGuardWaitMilliseconds == 250);

// Independent public-contract assertions; no private access, replacement
// adapter, source-text pattern matching, or production testing API is used.
void require(bool condition, const char* expression, int line) {
    if (!condition) {
        throw std::runtime_error(std::string("line ") + std::to_string(line) +
                                 ": " + expression);
    }
}

#define REQUIRE(expression) require(static_cast<bool>(expression), #expression, __LINE__)

constexpr auto bit(MidiInboxFault fault) noexcept {
    return static_cast<std::uint32_t>(fault);
}

std::size_t event_position(const native::Scenario& scenario, Op operation,
                           std::size_t ordinal = 1) {
    for (std::size_t index = 0; index < scenario.events.size(); ++index) {
        const auto event = scenario.events[index];
        if (event.operation == operation && event.ordinal == ordinal) return index;
    }
    throw std::runtime_error("required native operation was not observed");
}

void ordinary_balance(const native::Scenario& scenario) {
    REQUIRE(scenario.constructions == scenario.destructions);
    REQUIRE(scenario.latest == nullptr);
    REQUIRE(scenario.cancelled_while_open == 0);
    REQUIRE(scenario.destroyed_while_open == 0);
}

void close_order(const native::Scenario& scenario, bool callback_installed = true) {
    REQUIRE(event_position(scenario, Op::Close) < event_position(scenario, Op::CloseReturned));
    if (callback_installed) {
        REQUIRE(event_position(scenario, Op::CloseReturned) < event_position(scenario, Op::Cancel));
        REQUIRE(event_position(scenario, Op::Cancel) < event_position(scenario, Op::Destroy));
    } else {
        REQUIRE(scenario.count(Op::Cancel) == 0);
        REQUIRE(event_position(scenario, Op::CloseReturned) < event_position(scenario, Op::Destroy));
    }
}

void open_controller(MidiDevice& device, MidiInbox& inbox,
                     const std::shared_ptr<native::Scenario>& scenario) {
    std::string error = "stale diagnostic";
    REQUIRE(device.open(inbox, "Controller", error));
    REQUIRE(error.empty());
    REQUIRE(device.is_open());
    REQUIRE(!device.is_quiescent());
    REQUIRE(device.info().state == MidiDeviceState::Open);
    REQUIRE(device.info().generation == 1);
    REQUIRE(scenario->latest != nullptr);
}

void metadata_does_not_construct() {
    const auto scenario = native::install();
    REQUIRE(MidiDevice::backend_available());
    REQUIRE(MidiDevice::backend_name() == native::platform_name);
    {
        MidiDevice device;
        REQUIRE(device.is_quiescent());
        REQUIRE(!device.is_open());
        REQUIRE(device.info().state == MidiDeviceState::Closed);
        REQUIRE(device.info().backend == native::platform_name);
        REQUIRE(device.info().generation == 0);
        std::string error;
        REQUIRE(!device.poll_connection(error));
        REQUIRE(!error.empty());
        device.close();
        device.close();
        REQUIRE(device.diagnostics().close_errors == 0);
    }
    REQUIRE(scenario->compiled_api_queries == 0);
    REQUIRE(scenario->construction_attempts == 0);
    ordinary_balance(*scenario);
}

void enumeration_exact_boundaries() {
    std::vector<std::vector<std::string>> cases{
        {}, {"same", "same"}, {" z ", "Z", "z", "Clavier \xC3\xA9"},
        {std::string(1024, 'x')}, {""}, {std::string(1025, 'x')},
        {std::string("Controller\0spoof", 16)}};
    std::vector<std::string> maximum;
    for (unsigned int index = 0; index < 256; ++index) {
        maximum.push_back("Input " + std::to_string(index));
    }
    cases.push_back(maximum);
    maximum.push_back("Input 256");
    cases.push_back(maximum);
    const std::array<bool, 9> valid{true, true, true, true, false, false, false, true, false};
    REQUIRE(cases.size() == valid.size());

    for (std::size_t index = 0; index < cases.size(); ++index) {
        const auto scenario = native::install();
        scenario->ports = cases[index];
        const std::vector<std::string> original{"caller-owned", "preserve on failure"};
        auto result = original;
        std::string error = "old error";
        REQUIRE(MidiDevice::enumerate_input_ports(result, error) == valid[index]);
        REQUIRE(result == (valid[index] ? cases[index] : original));
        REQUIRE(error.empty() == valid[index]);
        REQUIRE(scenario->constructions == 1);
        REQUIRE(scenario->count(Op::Open) == 0);
        REQUIRE(scenario->count(Op::Callback) == 0);
        REQUIRE(scenario->requested_apis == std::vector<RtMidi::Api>{native::platform_api});
        REQUIRE(scenario->queue_limits == std::vector<unsigned int>{0});
        ordinary_balance(*scenario);
    }
}

void enumeration_failures_and_no_fallback() {
    // Neither an absent selected API nor a dependency-selected substitute may
    // turn into a successful empty list or a retry with a different backend.
    for (unsigned int mode = 0; mode < 3; ++mode) {
        const auto scenario = native::install();
        if (mode == 0) scenario->compiled_apis = {RtMidi::UNIX_JACK, RtMidi::RTMIDI_DUMMY};
        if (mode == 1) scenario->reported_api = RtMidi::RTMIDI_DUMMY;
        if (mode == 2) scenario->compiled_api_throws = true;
        std::vector<std::string> destination{"keep"};
        std::string error;
        REQUIRE(!MidiDevice::enumerate_input_ports(destination, error));
        REQUIRE(destination == std::vector<std::string>{"keep"});
        REQUIRE(!error.empty());
        REQUIRE(scenario->construction_attempts == (mode == 1 ? 1U : 0U));
        REQUIRE(scenario->count(Op::Open) == 0);
        ordinary_balance(*scenario);
    }

    for (const auto operation : {Op::Construct, Op::PortCount, Op::PortName}) {
        const auto scenario = native::install();
        scenario->on_call = [operation](RtMidiIn&, Op op, std::size_t) {
            if (op == operation) throw RtMidiError("enumeration exception");
        };
        std::vector<std::string> destination{"keep"};
        std::string error;
        REQUIRE(!MidiDevice::enumerate_input_ports(destination, error));
        REQUIRE(destination == std::vector<std::string>{"keep"});
        REQUIRE(!error.empty());
        REQUIRE(scenario->construction_attempts == 1);
        ordinary_balance(*scenario);
    }

    // The real RtMidi error callback often reports and returns instead of
    // throwing, including during ephemeral-client destruction.
    for (const auto operation : {Op::ErrorCallback, Op::PortCount, Op::PortName, Op::Destroy}) {
        const auto scenario = native::install();
        scenario->on_call = [operation](RtMidiIn& input, Op op, std::size_t) {
            if (op == operation) input.captured_callbacks().report_error();
        };
        std::vector<std::string> destination{"keep"};
        std::string error;
        REQUIRE(!MidiDevice::enumerate_input_ports(destination, error));
        REQUIRE(destination == std::vector<std::string>{"keep"});
        REQUIRE(!error.empty());
        ordinary_balance(*scenario);
    }
}

void argument_rejection_preserves_epoch() {
    const auto scenario = native::install();
    {
        MidiInbox inbox;
        MidiDevice device;
        std::string error;
        for (const auto& name : {std::string{}, std::string(1025, 'x'),
                                 std::string("Controller\0", 11)}) {
            REQUIRE(!device.open(inbox, name, error));
            REQUIRE(!error.empty());
            REQUIRE(device.info().state == MidiDeviceState::Closed);
            REQUIRE(device.info().generation == 0);
            REQUIRE(inbox.pending() == 0);
            REQUIRE(inbox.faults() == 0);
        }
        const std::array<std::uint8_t, 3> bytes{0x90, 60, 127};
        REQUIRE(inbox.push(bytes, 123) == MidiPushResult::Accepted);
        REQUIRE(!device.open(inbox, "Controller", error));
        REQUIRE(inbox.pending() == 1);
        REQUIRE(inbox.faults() == 0);
        inbox.reset_quiescent();
        inbox.signal_fault(MidiInboxFault::Overflow);
        REQUIRE(!device.open(inbox, "Controller", error));
        REQUIRE(inbox.faults() == bit(MidiInboxFault::Overflow));
        REQUIRE(scenario->construction_attempts == 0);
        inbox.reset_quiescent();
        open_controller(device, inbox, scenario);
        const auto before = device.info();
        MidiInbox unrelated;
        REQUIRE(!device.open(unrelated, "Controller", error));
        REQUIRE(!device.open(unrelated, "", error));
        REQUIRE(device.is_open());
        REQUIRE(device.info().port_name == before.port_name);
        REQUIRE(device.info().generation == before.generation);
        REQUIRE(inbox.faults() == 0);
        REQUIRE(unrelated.faults() == 0);
        REQUIRE(scenario->construction_attempts == 1);
        device.close();
        REQUIRE(inbox.faults() == bit(MidiInboxFault::Disconnected));
        REQUIRE(unrelated.faults() == 0);
    }
    ordinary_balance(*scenario);
}

void exact_selection_and_generation() {
    const auto scenario = native::install();
    scenario->ports = {"Controller suffix", "Controller", "controller", " Controller"};
    {
        MidiInbox inbox;
        MidiDevice device;
        open_controller(device, inbox, scenario);
        REQUIRE(device.info().opened_port_index == 1);
        REQUIRE(device.info().port_name == "Controller");
        REQUIRE(scenario->opened_indices == std::vector<unsigned int>{1});
        REQUIRE((scenario->ignored_types == std::array<bool, 3>{true, true, true}));
        REQUIRE(event_position(*scenario, Op::ErrorCallback) < event_position(*scenario, Op::Open));
        REQUIRE(event_position(*scenario, Op::Ignore) < event_position(*scenario, Op::Callback));
        REQUIRE(event_position(*scenario, Op::Callback) < event_position(*scenario, Op::Open));
#if defined(_WIN32)
        REQUIRE((scenario->buffer_size == std::array<unsigned int, 2>{1024, 0}));
        REQUIRE(event_position(*scenario, Op::Buffer) < event_position(*scenario, Op::Open));
#else
        REQUIRE(scenario->count(Op::Buffer) == 0);
#endif
        device.close();
        REQUIRE(device.is_quiescent());
        REQUIRE(device.info().state == MidiDeviceState::Closed);
        REQUIRE(device.info().generation == 1);
        REQUIRE(inbox.diagnostics().resets == 0);
        std::string error;
        REQUIRE(!device.open(inbox, "Controller", error));
        REQUIRE(scenario->construction_attempts == 1);
        inbox.reset_quiescent();
        scenario->ports = {"controller", " Controller", "Controller"};
        REQUIRE(device.open(inbox, "Controller", error));
        REQUIRE(device.info().generation == 2);
        REQUIRE(device.info().opened_port_index == 2);
        REQUIRE((scenario->opened_indices == std::vector<unsigned int>{1, 2}));
        device.close();
        const auto closes = scenario->count(Op::Close);
        const auto destroys = scenario->destructions;
        device.close();
        REQUIRE(scenario->count(Op::Close) == closes);
        REQUIRE(scenario->destructions == destroys);
        REQUIRE(device.diagnostics().close_errors == 0);
    }
    REQUIRE(scenario->constructions == 2);
    close_order(*scenario);
    ordinary_balance(*scenario);

    for (const auto& names : {std::vector<std::string>{"controller", "Controller suffix"},
                              std::vector<std::string>{"Controller", "Controller"}}) {
        const auto missing = native::install();
        missing->ports = names;
        {
            MidiInbox inbox;
            MidiDevice device;
            std::string error;
            REQUIRE(!device.open(inbox, "Controller", error));
            REQUIRE(!error.empty());
            REQUIRE(device.is_quiescent());
            REQUIRE(device.info().state == MidiDeviceState::Closed);
            REQUIRE(device.info().generation == 0);
            REQUIRE(inbox.pending() == 0);
            REQUIRE(inbox.faults() == 0);
            REQUIRE(missing->count(Op::Open) == 0);
        }
        close_order(*missing, false);
        ordinary_balance(*missing);
    }
}

void open_caps_and_no_api_fallback() {
    std::vector<std::vector<std::string>> invalid{{"Controller", ""},
        {"Controller", std::string(1025, 'x')},
        {"Controller", std::string("other\0port", 10)}};
    invalid.emplace_back(257, "Controller");
    for (const auto& names : invalid) {
        const auto scenario = native::install();
        scenario->ports = names;
        {
            MidiInbox inbox;
            MidiDevice device;
            std::string error;
            REQUIRE(!device.open(inbox, "Controller", error));
            REQUIRE(!error.empty());
            REQUIRE(device.is_quiescent());
            REQUIRE(inbox.faults() == 0);
            REQUIRE(scenario->count(Op::Open) == 0);
            REQUIRE(device.info().generation == 0);
        }
        ordinary_balance(*scenario);
    }
    for (unsigned int mode = 0; mode < 3; ++mode) {
        const auto scenario = native::install();
        if (mode == 0) scenario->compiled_apis = {RtMidi::RTMIDI_DUMMY};
        if (mode == 1) scenario->reported_api = RtMidi::UNIX_JACK;
        if (mode == 2) {
            scenario->on_call = [](RtMidiIn&, Op operation, std::size_t) {
                if (operation == Op::Construct) throw RtMidiError("construction refused");
            };
        }
        {
            MidiInbox inbox;
            MidiDevice device;
            std::string error;
            REQUIRE(!device.open(inbox, "Controller", error));
            REQUIRE(!error.empty());
            REQUIRE(device.is_quiescent());
            REQUIRE(inbox.faults() == 0);
            REQUIRE(device.info().generation == 0);
            REQUIRE(scenario->count(Op::Open) == 0);
            REQUIRE(scenario->construction_attempts == (mode == 0 ? 0U : 1U));
        }
        ordinary_balance(*scenario);
    }
    const auto maximum = native::install();
    maximum->ports.assign(256, "other");
    maximum->ports[255] = std::string(1024, 'x');
    {
        MidiInbox inbox;
        MidiDevice device;
        std::string error;
        REQUIRE(device.open(inbox, maximum->ports[255], error));
        REQUIRE(device.info().opened_port_index == 255);
        REQUIRE(device.info().port_name.size() == 1024);
    }
    ordinary_balance(*maximum);
}

void topology_changes_around_activation() {
    for (unsigned int mode = 0; mode < 4; ++mode) {
        const auto scenario = native::install();
        scenario->ports = {"other", "Controller"};
        scenario->on_call = [scenario, mode](RtMidiIn& input, Op operation, std::size_t ordinal) {
            if (mode == 0 && operation == Op::PortName && ordinal == 3) {
                scenario->ports = {"Controller", "other"};
            }
            if (mode != 0 && operation == Op::Open) {
                std::vector<unsigned char> prefix{0x90, 60, 100};
                input.captured_callbacks().message(&prefix);
                if (mode == 1) scenario->ports = {"Controller", "other"};
                if (mode == 2) scenario->ports = {"Controller", "Controller"};
                if (mode == 3) scenario->ports = {"other"};
            }
        };
        {
            MidiInbox inbox;
            MidiDevice device;
            std::string error;
            REQUIRE(!device.open(inbox, "Controller", error));
            REQUIRE(!error.empty());
            REQUIRE(device.info().generation == 0);
            REQUIRE(device.is_quiescent());
            REQUIRE(scenario->count(Op::Open) == (mode == 0 ? 0U : 1U));
            REQUIRE(inbox.pending() == (mode == 0 ? 0U : 1U));
            REQUIRE(inbox.faults() == (mode == 0 ? 0U :
                bit(MidiInboxFault::Backend) | bit(MidiInboxFault::Disconnected)));
            REQUIRE(inbox.diagnostics().discarded_packets == 0);
            REQUIRE(inbox.diagnostics().resets == 0);
            REQUIRE(device.diagnostics().forwarded_messages == (mode == 0 ? 0U : 1U));
        }
        scenario->on_call = {}; // Remove the fixture's shared_ptr capture.
        close_order(*scenario);
        ordinary_balance(*scenario);
    }
}

void callbacks_copy_packets_and_filter_sizes() {
    const auto scenario = native::install();
    {
        MidiInbox inbox;
        MidiDevice device;
        open_controller(device, inbox, scenario);
        const auto callbacks = scenario->latest->captured_callbacks();
        const auto before = std::chrono::steady_clock::now();
        std::vector<unsigned char> note{0x90, 60, 127};
        callbacks.message(&note, std::numeric_limits<double>::quiet_NaN());
        note.assign(4096, 0xEE); // Mutate and reallocate borrowed native storage.
        std::vector<unsigned char> program{0xC0, 7};
        callbacks.message(&program, -1000000.0);
        program.clear();
        std::vector<unsigned char> clock{0xF8};
        callbacks.message(&clock, std::numeric_limits<double>::infinity());
        // Content decoding belongs to MidiInput, so even unsupported/malformed
        // complete short payloads are copied without transport interpretation.
        std::vector<unsigned char> malformed{0x00, 0xFF, 0x80};
        callbacks.message(&malformed, 1e100);
        std::vector<unsigned char> empty;
        std::vector<unsigned char> oversize{0xF0, 1, 2, 0xF7};
        callbacks.message(nullptr);
        callbacks.message(&empty);
        callbacks.message(&oversize);
        callbacks.message(&note);
        const auto after = std::chrono::steady_clock::now();
        const auto first_time = static_cast<std::uint64_t>(
            std::chrono::duration_cast<std::chrono::nanoseconds>(before.time_since_epoch()).count());
        const auto final_time = static_cast<std::uint64_t>(
            std::chrono::duration_cast<std::chrono::nanoseconds>(after.time_since_epoch()).count());
        const std::array<std::array<std::uint8_t, 3>, 4> expected{{
            {0x90, 60, 127}, {0xC0, 7, 0}, {0xF8, 0, 0}, {0x00, 0xFF, 0x80}}};
        const std::array<std::uint8_t, 4> lengths{3, 2, 1, 3};
        std::uint64_t previous = first_time;
        for (std::size_t index = 0; index < expected.size(); ++index) {
            MidiPacket packet;
            REQUIRE(inbox.pop(packet));
            REQUIRE(packet.bytes == expected[index]);
            REQUIRE(packet.size == lengths[index]);
            REQUIRE(packet.arrival_ns >= previous);
            REQUIRE(packet.arrival_ns <= final_time);
            previous = packet.arrival_ns;
        }
        MidiPacket destination{{1, 2, 3}, 3, 123};
        REQUIRE(!inbox.pop(destination));
        REQUIRE(destination.arrival_ns == 123);
        const auto diagnostics = device.diagnostics();
        REQUIRE(diagnostics.callback_messages == 8);
        REQUIRE(diagnostics.forwarded_messages == 4);
        REQUIRE(diagnostics.filtered_messages == 4);
        REQUIRE(diagnostics.admission_failures == 0);
        REQUIRE(diagnostics.backend_errors == 0);
        REQUIRE(diagnostics.callback_contentions == 0);
        REQUIRE(diagnostics.last_arrival_ns >= previous);
        REQUIRE(diagnostics.last_arrival_ns <= final_time);
        REQUIRE(inbox.diagnostics().received_packets == 4);
        REQUIRE(inbox.diagnostics().invalid_size_packets == 0);
        REQUIRE(inbox.faults() == 0);
    }
    close_order(*scenario);
    ordinary_balance(*scenario);
}

void callback_queue_overflow_stops_admission() {
    const auto scenario = native::install();
    {
        MidiInbox inbox;
        MidiDevice device;
        open_controller(device, inbox, scenario);
        const auto callbacks = scenario->latest->captured_callbacks();
        std::vector<unsigned char> bytes{0x90, 60, 127};
        for (unsigned int index = 0; index < 256; ++index) callbacks.message(&bytes);
        REQUIRE(inbox.pending() == 256);
        REQUIRE(inbox.faults() == 0);
        callbacks.message(&bytes);
        REQUIRE(inbox.faults() == bit(MidiInboxFault::Overflow));
        callbacks.message(&bytes);
        REQUIRE(device.diagnostics().callback_messages == 258);
        REQUIRE(device.diagnostics().forwarded_messages == 256);
        REQUIRE(device.diagnostics().admission_failures == 2);
        REQUIRE(device.diagnostics().backend_errors == 0);
        REQUIRE(inbox.diagnostics().received_packets == 257);
        REQUIRE(inbox.diagnostics().overflow_events == 1);
        MidiPacket destination{{1, 2, 3}, 3, 999};
        REQUIRE(!inbox.pop(destination));
        REQUIRE(destination.arrival_ns == 999);
        std::string error;
        REQUIRE(!device.poll_connection(error));
        REQUIRE(device.info().state == MidiDeviceState::Faulted);
        REQUIRE(device.is_quiescent());
        REQUIRE(inbox.pending() == 256);
        REQUIRE(inbox.diagnostics().discarded_packets == 0);
        REQUIRE(inbox.diagnostics().resets == 0);
        REQUIRE((inbox.faults() & bit(MidiInboxFault::Disconnected)) != 0);
        REQUIRE(scenario->count(Op::Open) == 1);
    }
    ordinary_balance(*scenario);
}

void backend_error_callback_closes_admission() {
    for (const auto type : {RtMidiError::WARNING, RtMidiError::DRIVER_ERROR}) {
        const auto scenario = native::install();
        {
            MidiInbox inbox;
            MidiDevice device;
            open_controller(device, inbox, scenario);
            const auto callbacks = scenario->latest->captured_callbacks();
            std::vector<unsigned char> bytes{0x90, 60, 100};
            callbacks.message(&bytes);
            std::thread reporter([callbacks, type] { callbacks.report_error(type); });
            reporter.join();
            REQUIRE(inbox.faults() == bit(MidiInboxFault::Backend));
            callbacks.message(&bytes);
            REQUIRE(inbox.pending() == 1);
            REQUIRE(device.diagnostics().backend_errors == 1);
            REQUIRE(device.diagnostics().admission_failures == 1);
            REQUIRE(device.diagnostics().forwarded_messages == 1);
            std::string error;
            REQUIRE(!device.poll_connection(error));
            REQUIRE(device.info().state == MidiDeviceState::Faulted);
            REQUIRE(device.is_quiescent());
            REQUIRE(device.diagnostics().disconnects == 0);
            REQUIRE(inbox.pending() == 1);
            REQUIRE(inbox.diagnostics().resets == 0);
        }
        ordinary_balance(*scenario);
    }
}

void callback_return_failures_during_open() {
    struct Fault {
        Op operation;
        std::size_t ordinal;
        bool activation;
    };
    const std::array<Fault, 7> faults{{
        {Op::ErrorCallback, 1, false}, {Op::PortCount, 1, false},
        {Op::Ignore, 1, false}, {Op::Callback, 1, false},
        {Op::PortName, 2, false}, {Op::Open, 1, true},
        {Op::PortCount, 2, true}}};
    for (const auto fault : faults) {
        const auto scenario = native::install();
        scenario->on_call = [fault](RtMidiIn& input, Op operation, std::size_t ordinal) {
            if (operation == fault.operation && ordinal == fault.ordinal) {
                input.captured_callbacks().report_error();
            }
        };
        {
            MidiInbox inbox;
            MidiDevice device;
            std::string error;
            REQUIRE(!device.open(inbox, "Controller", error));
            REQUIRE(!error.empty());
            REQUIRE(device.info().generation == 0);
            // Before activation, the public contract promises refusal and an
            // untouched inbox, but does not require replacing the prior state.
            REQUIRE(!device.is_open());
            if (fault.activation) REQUIRE(device.info().state == MidiDeviceState::Faulted);
            REQUIRE(device.is_quiescent());
            REQUIRE(device.diagnostics().backend_errors == 1);
            REQUIRE(device.diagnostics().close_errors == 0);
            REQUIRE(inbox.faults() == (fault.activation ?
                bit(MidiInboxFault::Backend) | bit(MidiInboxFault::Disconnected) : 0U));
            REQUIRE(inbox.diagnostics().resets == 0);
        }
        ordinary_balance(*scenario);
    }
}

void partial_open_failure_closes_and_retires_prefix() {
    for (unsigned int mode = 0; mode < 4; ++mode) {
        const auto scenario = native::install();
        scenario->on_call = [mode](RtMidiIn& input, Op operation, std::size_t ordinal) {
            if (operation != Op::Open || ordinal != 1) return;
            std::vector<unsigned char> prefix{0x90, 60, 100};
            input.captured_callbacks().message(&prefix);
            if (mode == 0) throw RtMidiError("partially opened transport");
            if (mode == 1) input.captured_callbacks().report_error();
            if (mode == 2) input.set_native_open(false);
            if (mode == 3) throw 17; // Non-std native exception remains contained.
        };
        {
            MidiInbox inbox;
            MidiDevice device;
            std::string error;
            REQUIRE(!device.open(inbox, "Controller", error));
            REQUIRE(!error.empty());
            REQUIRE(device.is_quiescent());
            REQUIRE(device.info().state == MidiDeviceState::Faulted);
            REQUIRE(device.info().generation == 0);
            REQUIRE(inbox.pending() == 1);
            REQUIRE(inbox.faults() == (bit(MidiInboxFault::Backend) | bit(MidiInboxFault::Disconnected)));
            REQUIRE(device.diagnostics().forwarded_messages == 1);
            REQUIRE(device.diagnostics().backend_errors == (mode == 2 ? 0U : 1U));
            REQUIRE(!device.open(inbox, "Controller", error));
            REQUIRE(scenario->count(Op::Open) == 1);
            MidiPacket packet;
            REQUIRE(!inbox.pop(packet));
            inbox.reset_quiescent();
            REQUIRE(device.open(inbox, "Controller", error));
            REQUIRE(device.info().generation == 1);
            REQUIRE(inbox.pending() == 0);
            REQUIRE(inbox.faults() == 0);
            REQUIRE(inbox.diagnostics().discarded_packets == 1);
            device.close();
        }
        close_order(*scenario);
        ordinary_balance(*scenario);
    }
}

void callback_during_native_close_uses_live_context() {
    const auto scenario = native::install();
    {
        MidiInbox inbox;
        MidiDevice device;
        open_controller(device, inbox, scenario);
        const auto callbacks = scenario->latest->captured_callbacks();
        std::vector<unsigned char> before{0x90, 60, 100};
        callbacks.message(&before);

        std::mutex mutex;
        std::condition_variable changed;
        bool close_entered = false;
        bool callback_completed = false;
        bool worker_timed_out = false;
        bool native_timed_out = false;
        std::thread worker([&] {
            std::unique_lock lock(mutex);
            if (!changed.wait_for(lock, std::chrono::seconds(2), [&] { return close_entered; })) {
                worker_timed_out = true;
                return;
            }
            lock.unlock();
            std::vector<unsigned char> late{0x80, 60, 0};
            callbacks.message(&late);
            lock.lock();
            callback_completed = true;
            changed.notify_all();
        });
        scenario->on_call = [&](RtMidiIn&, Op operation, std::size_t) {
            if (operation != Op::Close) return;
            std::unique_lock lock(mutex);
            close_entered = true;
            changed.notify_all();
            native_timed_out = !changed.wait_for(lock, std::chrono::seconds(2),
                                               [&] { return callback_completed; });
        };
        device.close();
        worker.join();
        scenario->on_call = {};
        REQUIRE(!worker_timed_out);
        REQUIRE(!native_timed_out);
        REQUIRE(callback_completed);
        REQUIRE(device.is_quiescent());
        REQUIRE(device.info().state == MidiDeviceState::Closed);
        REQUIRE(inbox.faults() == bit(MidiInboxFault::Disconnected));
        REQUIRE(inbox.pending() == 1);
        REQUIRE(inbox.diagnostics().resets == 0);
        REQUIRE(device.diagnostics().callback_messages == 2);
        REQUIRE(device.diagnostics().forwarded_messages == 1);
        REQUIRE(device.diagnostics().admission_failures == 1);
        REQUIRE(device.diagnostics().close_errors == 0);
        close_order(*scenario);
    }
    ordinary_balance(*scenario);
}

void polling_preserves_caller_scope_and_never_reconnects() {
    // A surviving exact name may move; its original index remains historical.
    const auto healthy = native::install();
    {
        MidiInbox inbox;
        MidiDevice device;
        open_controller(device, inbox, healthy);
        healthy->ports = {"new unrelated", "Controller"};
        std::string error = "old";
        REQUIRE(device.poll_connection(error));
        REQUIRE(error.empty());
        REQUIRE(device.info().opened_port_index == 0);
        REQUIRE(device.info().generation == 1);
        REQUIRE(healthy->count(Op::Open) == 1);
    }
    ordinary_balance(*healthy);

    for (unsigned int mode = 0; mode < 7; ++mode) {
        const auto scenario = native::install();
        {
            MidiInbox inbox;
            MidiInbox unrelated;
            MidiInput decoder;
            REQUIRE(decoder.begin_epoch());
            MidiDevice device;
            open_controller(device, inbox, scenario);
            auto callbacks = scenario->latest->captured_callbacks();
            std::vector<unsigned char> note{0x90, 60, 100};
            callbacks.message(&note);
            if (mode == 0) scenario->ports = {"other"};
            if (mode == 1) scenario->ports = {"Controller", "Controller"};
            if (mode == 2) scenario->latest->set_native_open(false);
            if (mode == 3) scenario->reported_api = RtMidi::RTMIDI_DUMMY;
            if (mode == 4) {
                scenario->on_call = [](RtMidiIn&, Op operation, std::size_t) {
                    if (operation == Op::PortCount) throw RtMidiError("poll enumeration failed");
                };
            }
            if (mode == 5) {
                scenario->on_call = [](RtMidiIn& input, Op operation, std::size_t) {
                    if (operation == Op::PortCount) input.captured_callbacks().report_error();
                };
            }
            if (mode == 6) scenario->ports = {"Controller", ""};
            std::string error;
            REQUIRE(!device.poll_connection(error));
            REQUIRE(!error.empty());
            REQUIRE(!device.is_open());
            REQUIRE(device.is_quiescent());
            REQUIRE(device.info().state == (mode < 3 ? MidiDeviceState::Disconnected : MidiDeviceState::Faulted));
            REQUIRE(device.diagnostics().disconnects == (mode < 3 ? 1U : 0U));
            REQUIRE(device.info().generation == 1);
            REQUIRE(device.info().port_name == "Controller");
            REQUIRE(inbox.pending() == 1);
            REQUIRE(inbox.diagnostics().discarded_packets == 0);
            REQUIRE(inbox.diagnostics().resets == 0);
            REQUIRE((inbox.faults() & bit(MidiInboxFault::Disconnected)) != 0);
            REQUIRE(unrelated.faults() == 0);
            REQUIRE(unrelated.diagnostics().resets == 0);
            REQUIRE(decoder.active());
            REQUIRE(decoder.diagnostics().packets == 0);
            scenario->ports = {"Controller"};
            scenario->reported_api = native::platform_api;
            scenario->on_call = {};
            REQUIRE(!device.poll_connection(error));
            REQUIRE(scenario->count(Op::Open) == 1);
            REQUIRE(scenario->construction_attempts == 1);
            REQUIRE(scenario->count(Op::Close) == 1);
        }
        ordinary_balance(*scenario);
    }
}

void destruction_releases_ordinary_resources_once() {
    const auto scenario = native::install();
    MidiInbox inbox;
    {
        MidiDevice device;
        open_controller(device, inbox, scenario);
    }
    REQUIRE(scenario->constructions == 1);
    REQUIRE(scenario->destructions == 1);
    REQUIRE(scenario->count(Op::Close) == 1);
    REQUIRE(scenario->count(Op::Cancel) == 1);
    REQUIRE(inbox.faults() == bit(MidiInboxFault::Disconnected));
    REQUIRE(inbox.diagnostics().resets == 0);
    close_order(*scenario);
    ordinary_balance(*scenario);
}

// A poisoned MidiDevice deliberately keeps one callback context alive. Its
// caller-owned inbox must also survive until process exit. This separate mode
// retains those exact test inboxes and never clears their faulted epochs.
std::vector<MidiInbox*> process_lifetime_inboxes;

void poisoned_close_retains_context_and_refuses_reopen() {
    enum class Failure { CloseThrow, CloseReported, StillOpen, CancelThrow,
                         CancelReported, DestructorReported };
    for (const auto failure : {Failure::CloseThrow, Failure::CloseReported,
                               Failure::StillOpen, Failure::CancelThrow,
                               Failure::CancelReported, Failure::DestructorReported}) {
        const auto scenario = native::install();
        auto inbox = std::make_unique<MidiInbox>();
        auto device = std::make_unique<MidiDevice>();
        open_controller(*device, *inbox, scenario);
        const auto callbacks = scenario->latest->captured_callbacks();
        std::vector<unsigned char> note{0x90, 60, 100};
        callbacks.message(&note);
        if (failure == Failure::StillOpen) scenario->close_succeeds = false;
        scenario->on_call = [failure](RtMidiIn& input, Op operation, std::size_t) {
            if (operation == Op::Close && failure == Failure::CloseThrow) {
                throw RtMidiError("native close threw");
            }
            if (operation == Op::Close && failure == Failure::CloseReported) {
                input.captured_callbacks().report_error();
            }
            if (operation == Op::Cancel && failure == Failure::CancelThrow) {
                throw RtMidiError("callback cancellation threw");
            }
            if (operation == Op::Cancel && failure == Failure::CancelReported) {
                input.captured_callbacks().report_error();
            }
            if (operation == Op::Destroy && failure == Failure::DestructorReported) {
                input.captured_callbacks().report_error();
            }
        };
        device->close();
        REQUIRE(!device->is_open());
        REQUIRE(!device->is_quiescent());
        REQUIRE(device->info().state == MidiDeviceState::Faulted);
        REQUIRE(device->diagnostics().close_errors == 1);
        REQUIRE(device->diagnostics().backend_errors == (failure == Failure::StillOpen ? 0U : 1U));
        REQUIRE(inbox->faults() == (bit(MidiInboxFault::Backend) | bit(MidiInboxFault::Disconnected)));
        REQUIRE(inbox->pending() == 1);
        REQUIRE(inbox->diagnostics().resets == 0);
        const auto close_count = scenario->count(Op::Close);
        const auto cancel_count = scenario->count(Op::Cancel);
        const auto destroy_count = scenario->destructions;
        device->close();
        std::string error;
        REQUIRE(!device->open(*inbox, "Controller", error));
        REQUIRE(error.find("restart") != std::string::npos);
        REQUIRE(!device->poll_connection(error));
        REQUIRE(error.find("restart") != std::string::npos);
        REQUIRE(scenario->construction_attempts == 1);
        REQUIRE(scenario->count(Op::Open) == 1);
        REQUIRE(scenario->count(Op::Close) == close_count);
        REQUIRE(scenario->count(Op::Cancel) == cancel_count);
        REQUIRE(scenario->destructions == destroy_count);
        REQUIRE(device->diagnostics().close_errors == 1);
        callbacks.message(&note); // Late native packet cannot enter the queue.
        REQUIRE(device->diagnostics().callback_messages == 2);
        REQUIRE(device->diagnostics().forwarded_messages == 1);
        REQUIRE(device->diagnostics().admission_failures == 1);

        auto* retained_inbox = inbox.release();
        process_lifetime_inboxes.push_back(retained_inbox);
        device.reset();
        REQUIRE(scenario->count(Op::Close) == close_count);
        REQUIRE(scenario->destructions == destroy_count);
        // Deliberately call the saved actual production callback/context after
        // public-device destruction. ASan verifies the exceptional retention;
        // this is not a claim that a successful native close allows late calls.
        std::thread late([callbacks] {
            std::vector<unsigned char> release{0x80, 60, 0};
            callbacks.message(&release);
            callbacks.report_error();
        });
        late.join();
        REQUIRE(retained_inbox->pending() == 1);
        REQUIRE(retained_inbox->diagnostics().resets == 0);
        REQUIRE(retained_inbox->diagnostics().received_packets == 1);
        REQUIRE(scenario->destructions == (failure == Failure::DestructorReported ? 1U : 0U));
        REQUIRE(scenario->constructions == 1);
        REQUIRE(scenario->cancelled_while_open == 0);
        if (failure == Failure::CloseThrow || failure == Failure::CloseReported ||
            failure == Failure::StillOpen) {
            REQUIRE(cancel_count == 0);
        } else {
            REQUIRE(event_position(*scenario, Op::CloseReturned) < event_position(*scenario, Op::Cancel));
        }
    }
    REQUIRE(process_lifetime_inboxes.size() == 6);
}

struct Test {
    const char* name;
    void (*run)();
};

const std::array<Test, 15> ordinary_tests{{
    {"metadata without native construction", metadata_does_not_construct},
    {"exact enumeration and caps", enumeration_exact_boundaries},
    {"enumeration faults and refused fallback", enumeration_failures_and_no_fallback},
    {"argument rejection preserves epoch", argument_rejection_preserves_epoch},
    {"exact selection and successful generations", exact_selection_and_generation},
    {"open caps and refused fallback", open_caps_and_no_api_fallback},
    {"topology changes around activation", topology_changes_around_activation},
    {"actual callback bytes, storage lifetime and sizes", callbacks_copy_packets_and_filter_sizes},
    {"actual callback queue overflow", callback_queue_overflow_stops_admission},
    {"backend error callback admission", backend_error_callback_closes_admission},
    {"open errors that return normally", callback_return_failures_during_open},
    {"partial activation and stale-prefix retirement", partial_open_failure_closes_and_retires_prefix},
    {"bounded worker callback during native close", callback_during_native_close_uses_live_context},
    {"poll scope and no automatic reconnect", polling_preserves_caller_scope_and_never_reconnects},
    {"ordinary destruction exactly once", destruction_releases_ordinary_resources_once},
}};

} // namespace

int main(int argc, char** argv) {
    const std::string_view mode = argc == 2 ? argv[1] : "--all";
    if (argc > 2 || (mode != "--all" && mode != "--ordinary" && mode != "--quarantine")) {
        std::cerr << "usage: test_standalone_midi_backend [--ordinary|--quarantine|--all]\n";
        return 2;
    }
    const char* active_test = "setup";
    try {
        std::size_t passed = 0;
        if (mode != "--quarantine") {
            for (const auto& test : ordinary_tests) {
                active_test = test.name;
                test.run();
                std::cout << "PASS ordinary: " << test.name << '\n';
                ++passed;
            }
        }
        if (mode != "--ordinary") {
            active_test = "poisoned shutdown and late callbacks";
            poisoned_close_retains_context_and_refuses_reopen();
            std::cout << "PASS quarantine: six failure paths retain context/inbox and refuse reopen\n";
            ++passed;
        }
        native::active_scenario.reset();
        std::cout << "PASS " << passed << " backend groups on " << native::platform_name
                  << "; actual MidiDevice.cpp with fake RtMidi API; no native driver claim\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "FAIL " << active_test << ": " << error.what() << '\n';
    } catch (...) {
        std::cerr << "FAIL " << active_test << ": unknown exception\n";
    }
    return 1;
}
