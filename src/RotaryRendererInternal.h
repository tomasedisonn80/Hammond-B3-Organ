#pragma once

#include "hammond/RotaryRenderer.h"

// Private implementation storage. No shipping test accessor is defined here.
// Dedicated acceptance executables may define the declared friend themselves.
namespace hammond::rotary::detail {

struct RotaryUndoRecord {
    std::size_t slot{0};
    std::array<double, kRotorCount> samples{};
    std::array<MotionSegment, kRotorCount> segments{};
};

struct RotaryRendererStorage {
    Profile original_profile{};
    ProcessSpec spec{0.0, 0};
    std::size_t capacity_frames{0};
    std::uint32_t flush_frames{0};
    std::array<RotaryMotion, kRotorCount> motion{};
    std::array<PreparedStreamingPath, kPathCount> paths{};
    RendererDiagnostics diagnostics{};
    std::array<WaveformHistory, kRotorCount> waveform{};
    std::array<MotionFrameHistory, kRotorCount> motion_history{};
    std::array<std::array<double, kMaxBlockFrames>, kMicrophoneCount> output{};
    std::array<RotaryUndoRecord, kMaxBlockFrames> undo{};
};

} // namespace hammond::rotary::detail
