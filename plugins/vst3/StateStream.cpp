#include "StateStream.h"

#include "hammond/ControlStateIO.h"

#include <array>
#include <cstddef>
#include <new>
#include <sstream>
#include <string>

namespace hammond::vst3 {

Steinberg::tresult read_control_state(
    Steinberg::IBStream* stream, ControlSnapshot& destination) noexcept {
    if (stream == nullptr) return Steinberg::kInvalidArgument;
    try {
        std::array<char, kMaxControlStateBytes + 1> bytes{};
        std::size_t size = 0;
        for (;;) {
            const auto requested = static_cast<Steinberg::int32>(bytes.size() - size);
            Steinberg::int32 received = 0;
            const auto result = stream->read(bytes.data() + size, requested, &received);
            if (received < 0 || received > requested) return Steinberg::kResultFalse;
            if (result != Steinberg::kResultOk &&
                !(result == Steinberg::kResultFalse && received == 0)) {
                return Steinberg::kResultFalse;
            }
            if (received == 0) break;
            size += static_cast<std::size_t>(received);
            if (size > kMaxControlStateBytes) return Steinberg::kResultFalse;
        }
        std::istringstream input{std::string(bytes.data(), size)};
        std::string error;
        ControlSnapshot candidate{};
        if (!parse_controls(input, candidate, error)) return Steinberg::kResultFalse;
        destination = candidate;
        return Steinberg::kResultOk;
    } catch (const std::bad_alloc&) {
        return Steinberg::kOutOfMemory;
    } catch (...) {
        return Steinberg::kInternalError;
    }
}

Steinberg::tresult write_control_state(
    Steinberg::IBStream* stream, const ControlSnapshot& snapshot) noexcept {
    if (stream == nullptr) return Steinberg::kInvalidArgument;
    try {
        std::string bytes;
        std::string error;
        if (!serialize_controls(snapshot, bytes, error) ||
            bytes.size() > kMaxControlStateBytes) {
            return Steinberg::kResultFalse;
        }
        std::size_t offset = 0;
        while (offset < bytes.size()) {
            const auto requested = static_cast<Steinberg::int32>(bytes.size() - offset);
            Steinberg::int32 written = 0;
            const auto result = stream->write(bytes.data() + offset, requested, &written);
            if (result != Steinberg::kResultOk || written <= 0 || written > requested) {
                return Steinberg::kResultFalse;
            }
            offset += static_cast<std::size_t>(written);
        }
        return Steinberg::kResultOk;
    } catch (const std::bad_alloc&) {
        return Steinberg::kOutOfMemory;
    } catch (...) {
        return Steinberg::kInternalError;
    }
}

} // namespace hammond::vst3
