#pragma once

#include "hammond/ControlState.h"
#include "hammond/ParameterBridge.h"
#include "public.sdk/source/vst/vsteditcontroller.h"

#include <array>

namespace hammond::vst3 {

// Generic host controls for the 47 immutable compiled descriptors. All methods
// belong to the host's serialized UI/control thread, never the audio callback.
// No custom editor, processor pointer, stream retention or automation echo.
class Controller final : public Steinberg::Vst::EditController {
public:
    [[nodiscard]] static Steinberg::FUnknown* createInstance(void* context);

    Steinberg::tresult PLUGIN_API initialize(Steinberg::FUnknown* context) override;
    Steinberg::tresult PLUGIN_API terminate() override;
    Steinberg::tresult PLUGIN_API setComponentState(Steinberg::IBStream* state) override;

    Steinberg::int32 PLUGIN_API getParameterCount() override;
    Steinberg::tresult PLUGIN_API getParameterInfo(
        Steinberg::int32 index, Steinberg::Vst::ParameterInfo& info) override;
    Steinberg::Vst::ParamValue PLUGIN_API getParamNormalized(
        Steinberg::Vst::ParamID id) override;

    Steinberg::tresult PLUGIN_API setParamNormalized(
        Steinberg::Vst::ParamID id, Steinberg::Vst::ParamValue value) override;
    Steinberg::tresult PLUGIN_API getParamStringByValue(
        Steinberg::Vst::ParamID id, Steinberg::Vst::ParamValue value,
        Steinberg::Vst::String128 text) override;
    Steinberg::tresult PLUGIN_API getParamValueByString(
        Steinberg::Vst::ParamID id, Steinberg::Vst::TChar* text,
        Steinberg::Vst::ParamValue& value) override;
    Steinberg::Vst::ParamValue PLUGIN_API normalizedParamToPlain(
        Steinberg::Vst::ParamID id, Steinberg::Vst::ParamValue value) override;
    Steinberg::Vst::ParamValue PLUGIN_API plainParamToNormalized(
        Steinberg::Vst::ParamID id, Steinberg::Vst::ParamValue value) override;

private:
    bool initialized_{false};
    std::array<double, kParameterCount> values_{};
};

} // namespace hammond::vst3
