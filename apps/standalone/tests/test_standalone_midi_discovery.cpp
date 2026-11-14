#include "MidiDiscovery.h"

#include <chrono>
#include <condition_variable>
#include <cstdint>
#include <iostream>
#include <mutex>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>

namespace {

using namespace hammond::standalone;
using namespace std::chrono_literals;

void require(bool condition, const char* message) {
    if (!condition) throw std::runtime_error(message);
}

struct ProbeState {
    std::mutex mutex;
    std::condition_variable changed;
    bool entered{false};
    bool released{false};
    bool returns_success{true};
    bool throws{false};
    std::uint64_t calls{0};
    std::thread::id worker_id{};
    std::vector<std::string> ports{"Controller B", "Controller A", "Controller A"};
};

bool blocked_probe(void* context, std::vector<std::string>& ports, std::string& error) {
    auto& state = *static_cast<ProbeState*>(context);
    std::unique_lock lock(state.mutex);
    ++state.calls;
    state.worker_id = std::this_thread::get_id();
    state.entered = true;
    state.changed.notify_all();
    if (!state.changed.wait_for(lock, 5s, [&state] { return state.released; })) {
        throw std::runtime_error("test failed to release its isolated native probe");
    }
    ports = state.ports;
    if (state.throws) throw std::runtime_error("injected discovery exception");
    error = state.returns_success ? "" : "injected native enumeration failure";
    return state.returns_success;
}

struct ReleaseOnExit {
    ProbeState& state;
    void release() {
        std::lock_guard lock(state.mutex);
        state.released = true;
        state.changed.notify_all();
    }
    ~ReleaseOnExit() { release(); }
};

void await_probe(ProbeState& state) {
    std::unique_lock lock(state.mutex);
    require(state.changed.wait_for(lock, 2s, [&state] { return state.entered; }),
            "discovery worker did not enter the supplied probe");
}

void blocked_query_does_not_block_owner() {
    ProbeState state;
    MidiDiscovery discovery(blocked_probe, &state);
    ReleaseOnExit release{state}; // Releases before discovery destruction on any assertion failure.
    std::string error = "stale";
    require(!discovery.pending(), "construction unexpectedly started a query");
    require(!discovery.start(0, error), "zero request identity must be rejected");
    require(discovery.start(7, error) && error.empty(), "valid request must start exactly once");
    await_probe(state);
    require(state.worker_id != std::this_thread::get_id(), "native query ran on its UI owner");
    MidiDiscoveryResult untouched{999, true, false, {"sentinel"}, "retain"};
    for (int turn = 0; turn < 4096; ++turn) {
        require(!discovery.poll(untouched), "unfinished query was reported as complete");
        require(untouched.generation == 999 && untouched.success &&
                    untouched.ports == std::vector<std::string>{"sentinel"} && untouched.error == "retain",
                "nonblocking poll changed its caller's result");
    }
    require(!discovery.start(8, error), "pending query admitted a second worker");
    require(state.calls == 1, "one pending request produced multiple native calls");
    release.release();
    MidiDiscoveryResult result;
    require(discovery.finish(result), "joined query was not returned");
    require(result.generation == 7 && result.success && result.error.empty(),
            "result lost its original request identity or success");
    require(result.ports == state.ports, "exact order and duplicate names were not retained");
    require(!discovery.pending(), "joined query remained pending");
    require(!discovery.poll(untouched) && !discovery.finish(untouched),
            "completed result was delivered more than once");
}

void failure_empty_and_exception_are_distinct() {
    for (int kind = 0; kind < 3; ++kind) {
        ProbeState state;
        state.released = true;
        state.returns_success = kind == 0;
        state.throws = kind == 2;
        if (kind == 0) state.ports.clear();
        MidiDiscovery discovery(blocked_probe, &state);
        std::string error;
        require(discovery.start(static_cast<std::uint64_t>(kind + 1), error), "request could not start");
        MidiDiscoveryResult result;
        require(discovery.finish(result), "shutdown did not retain completed discovery");
        require(result.success == (kind == 0), "empty success and failure were conflated");
        require(result.ports.empty(), "failed discovery leaked partially written port names");
        require(result.unexpected_exception == (kind == 2), "exception disposition was lost");
        if (kind == 0) require(result.error.empty(), "successful zero-port query retained an error");
        if (kind == 1) require(result.error == "injected native enumeration failure", "backend error was hidden");
        if (kind == 2) require(result.error.find("unexpected probe exception") != std::string::npos,
                               "unexpected exception was not surfaced");
    }
}

void completed_results_require_consumption_and_keep_generations() {
    ProbeState state;
    state.released = true;
    MidiDiscovery discovery(blocked_probe, &state);
    std::string error;
    for (std::uint64_t generation = 1; generation <= 32; ++generation) {
        require(discovery.start(generation, error), "sequential discovery could not start");
        require(!discovery.start(generation + 100, error), "unconsumed result admitted another worker");
        MidiDiscoveryResult result;
        require(discovery.finish(result), "result was not joined");
        require(result.generation == generation && result.success, "reused storage changed result identity");
    }
    require(state.calls == 32, "request coalescing fabricated or repeated a probe call");
    MidiDiscovery invalid(nullptr);
    require(!invalid.start(1, error) && !invalid.pending(), "missing probe was admitted");
}

} // namespace

int main() {
    try {
        blocked_query_does_not_block_owner();
        failure_empty_and_exception_are_distinct();
        completed_results_require_consumption_and_keep_generations();
        std::cout << "MIDI discovery: blocked probe permits 4096 owner polls; exact results, failures, exceptions, "
                     "single-worker admission, 32 generations and joined cleanup passed\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
