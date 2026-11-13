#pragma once

#include "hammond/ControlState.h"

#include <cstddef>
#include <iosfwd>
#include <string>

namespace hammond {

inline constexpr std::size_t kMaxControlStateBytes = 16 * 1024;

// B3CONTROLS3 stores musical controls only, including all hidden banks, route
// bits, retained percussion settings and both pedal mixture positions.
// B3CONTROLS1/2 remain readable and explicitly migrate pedals to [0,0]; version
// 1 also migrates percussion to Off/Second/Normal/Slow. No format stores held
// keys/pedals, owners, contact trajectories, readiness, phase, clock or host data.
// These allocating functions are for stopped/control-thread use only. Obtain a
// safely copied snapshot before calling; neither function accesses an Engine.
// See docs/CONTROL_STATE_FORMAT.md for the exact grammar and ownership contract.

// Validates before serializing canonical B3CONTROLS3 to an owned string; the
// caller owns file policy. There is deliberately no older-version writer.
// Failure preserves destination. Success replaces it and clears error.
// The two strings must be distinct; aliasing returns false without modifying
// their shared value (and therefore cannot provide a separate error message).
[[nodiscard]] bool serialize_controls(const ControlSnapshot& snapshot,
                                      std::string& destination, std::string& error);

// Reads at most kMaxControlStateBytes + 1 bytes to enforce the inclusive limit.
// Malformed/truncated/unsupported input or stream failure preserves destination.
// Success replaces the complete snapshot and clears error. Caller stream locale
// and exception mask are unchanged; input position/status may advance on failure.
[[nodiscard]] bool parse_controls(std::istream& input, ControlSnapshot& destination,
                                  std::string& error);

} // namespace hammond
