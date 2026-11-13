#pragma once

#include "hammond/ControlState.h"
#include "pluginterfaces/base/ibstream.h"

namespace hammond::vst3 {

// Serialized UI/control-thread use only. These functions may allocate and use
// the existing strict B3CONTROLS grammar. They never retain a stream pointer,
// access an Engine, seek, or hand parsing work to the processing thread.
//
// Read at most 16 KiB + one overflow-detection byte from the current position.
// Short successful reads continue; zero bytes with kResultOk or kResultFalse
// mark end of stream. Other errors, inconsistent counts and oversized/malformed
// input fail. Destination remains unchanged on every failure. Stream position
// may advance even on failure; IBStream cannot provide a general rollback.
[[nodiscard]] Steinberg::tresult read_control_state(
    Steinberg::IBStream* stream, ControlSnapshot& destination) noexcept;

// Validate/serialize the entire snapshot before the first write. Successful
// short writes continue; errors, zero progress and inconsistent counts fail.
// Invalid snapshots cause no write. An external stream write failure can leave
// a prefix in that stream; no atomic-file or truncation guarantee is implied.
[[nodiscard]] Steinberg::tresult write_control_state(
    Steinberg::IBStream* stream, const ControlSnapshot& snapshot) noexcept;

} // namespace hammond::vst3
