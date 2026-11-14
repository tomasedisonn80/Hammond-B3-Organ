#pragma once

#include "MidiDevice.h"

#include <atomic>
#include <cstdint>
#include <exception>
#include <string>
#include <thread>
#include <utility>
#include <vector>

namespace hammond::standalone {

struct MidiDiscoveryResult {
    std::uint64_t generation{0};
    bool success{false};
    bool unexpected_exception{false};
    std::vector<std::string> ports{};
    std::string error{};
};

// One exclusively owned, isolated OS enumeration job. It does not own a live
// MidiDevice, inbox, Session, UI or SDL object. Public operations belong to its
// main-thread owner. The probe/context, when explicitly supplied, must outlive
// this object and its joined worker. No operation is an audio callback API.
//
// poll() never waits for an unfinished native query. The owning application
// decides whether a completed generation still belongs to the open modal.
// Native OS calls have no portable cancellation/deadline; finish()/destruction
// join outside the UI event loop and after audio has stopped. Never detach a
// thread that could outlive the loaded backend or its owned result.
class MidiDiscovery {
public:
    using Probe = bool (*)(void*, std::vector<std::string>&, std::string&);

    explicit MidiDiscovery(Probe probe = native_probe, void* context = nullptr) noexcept
        : probe_(probe), context_(context) {}
    ~MidiDiscovery() { if (worker_.joinable()) worker_.join(); }
    MidiDiscovery(const MidiDiscovery&) = delete;
    MidiDiscovery& operator=(const MidiDiscovery&) = delete;

    [[nodiscard]] bool pending() const noexcept { return worker_.joinable(); }

    // One job only: an unfinished or unconsumed result refuses another start.
    // Reopening the modal queues a new generation in the application; it never
    // creates a second concurrent native query or retries a failed generation.
    [[nodiscard]] bool start(std::uint64_t generation, std::string& error) {
        if (pending() || generation == 0 || probe_ == nullptr) {
            error = "MIDI discovery is pending or its request is invalid";
            return false;
        }
        result_ = {};
        result_.generation = generation;
        completed_.store(false, std::memory_order_relaxed);
        try {
            worker_ = std::thread([this] {
                try {
                    result_.success = probe_(context_, result_.ports, result_.error);
                } catch (...) {
                    // No exception escapes the thread. Main formats the fixed
                    // failure after acquiring the result, not on this worker.
                    result_.success = false;
                    result_.unexpected_exception = true;
                    result_.ports.clear();
                }
                completed_.store(true, std::memory_order_release);
            });
            error.clear();
            return true;
        } catch (const std::exception& exception) {
            error = std::string("Cannot start MIDI discovery: ") + exception.what();
        } catch (...) {
            error = "Cannot start MIDI discovery: unknown thread-creation failure";
        }
        return false;
    }

    // An unavailable result leaves destination untouched. Acquire publication
    // precedes access to every vector/string written by the worker. Joining here
    // only reaps an already completed probe, including native client teardown.
    [[nodiscard]] bool poll(MidiDiscoveryResult& destination) {
        if (!pending() || !completed_.load(std::memory_order_acquire)) return false;
        return finish(destination);
    }

    // Explicit off-loop shutdown, or reaping after poll's acquire. No pending
    // job is cancelled or reported as successfully completed before it returns.
    [[nodiscard]] bool finish(MidiDiscoveryResult& destination) {
        if (!pending()) return false;
        worker_.join();
        if (result_.unexpected_exception) {
            result_.error = "MIDI discovery failed with an unexpected probe exception";
        }
        if (!result_.success) result_.ports.clear();
        destination = std::move(result_);
        completed_.store(false, std::memory_order_relaxed);
        return true;
    }

private:
    [[nodiscard]] static bool native_probe(void*, std::vector<std::string>& ports,
                                            std::string& error) {
        return MidiDevice::enumerate_input_ports(ports, error);
    }

    Probe probe_{};
    void* context_{};
    std::thread worker_{};
    std::atomic<bool> completed_{false};
    MidiDiscoveryResult result_{};
};

} // namespace hammond::standalone
