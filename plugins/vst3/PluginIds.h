#pragma once

#include "pluginterfaces/base/funknown.h"

namespace hammond::vst3 {

// Original identities fixed by docs/VST3_SPIKE_CONTRACT.md. FUID handles the
// SDK's platform-specific byte representation; never substitute sample IDs.
inline const Steinberg::FUID kProcessorClassId{
    0x19F9ADC0, 0x533F42B4, 0xB96BD51D, 0x6547E838};
inline const Steinberg::FUID kControllerClassId{
    0x0DEE76AB, 0x26BC475A, 0xBF64F138, 0xC89FB0E0};

inline constexpr char kPluginName[] = "Hammond B3 Nominal";
inline constexpr char kPluginVersion[] = "0.1.0";
inline constexpr char kPluginVendor[] = "Hammond B3 Organ project";
inline constexpr char kPluginUrl[] =
    "https://github.com/tomasedisonn80/Hammond-B3-Organ";

} // namespace hammond::vst3
