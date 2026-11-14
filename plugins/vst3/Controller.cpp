#include "Controller.h"

#include "StateStream.h"
#include "hammond/ParameterBridge.h"
#include "hammond/detail/Decimal.h"

#include <array>
#include <cstddef>
#include <iomanip>
#include <limits>
#include <locale>
#include <new>
#include <sstream>
#include <string>
#include <string_view>

namespace hammond::vst3 {
namespace {

using Steinberg::Vst::ParameterInfo;
using Steinberg::Vst::ParamID;
using Steinberg::Vst::ParamValue;
using Steinberg::Vst::String128;
using Steinberg::Vst::TChar;

[[nodiscard]] bool copy_ascii(std::string_view source, String128 destination) noexcept {
    if (source.size() >= 128) return false;
    for (std::size_t index = 0; index < source.size(); ++index) {
        const auto byte = static_cast<unsigned char>(source[index]);
        if (byte >= 128) return false;
        destination[index] = static_cast<TChar>(byte);
    }
    destination[source.size()] = 0;
    return true;
}

[[nodiscard]] bool make_parameter_info(const ParameterDescriptor& descriptor,
                                      ParameterInfo& destination) noexcept {
    ParameterInfo candidate{};
    if (!copy_ascii(descriptor.path, candidate.title) ||
        !copy_ascii(descriptor.path, candidate.shortTitle) ||
        !copy_ascii(descriptor.unit, candidate.units) ||
        !plain_to_normalized(descriptor.id, descriptor.default_plain,
                             candidate.defaultNormalizedValue)) {
        return false;
    }
    candidate.id = descriptor.id;
    candidate.stepCount = static_cast<Steinberg::int32>(descriptor.step_count);
    candidate.flags = ParameterInfo::kCanAutomate;
    candidate.unitId = Steinberg::Vst::kRootUnitId;
    destination = candidate;
    return true;
}

[[nodiscard]] bool format_value(ParamID id, ParamValue normalized,
                                String128 destination) {
    if (destination == nullptr) return false;
    Event event{};
    if (!normalized_to_event(id, normalized, 0, event)) return false;
    std::ostringstream output;
    output.imbue(std::locale::classic());
    {
        const detail::DecimalRounding rounding;
        if (!rounding.ready()) return false;
        output << std::setprecision(std::numeric_limits<double>::max_digits10) << event.value;
    }
    if (!output) return false;
    String128 candidate{};
    if (!copy_ascii(output.str(), candidate)) return false;
    for (std::size_t index = 0; index < 128; ++index) destination[index] = candidate[index];
    return true;
}

[[nodiscard]] bool parse_value(ParamID id, const TChar* text,
                               ParamValue& destination) {
    if (text == nullptr) return false;
    std::array<char, 128> bytes{};
    std::size_t length = 0;
    while (length < bytes.size()) {
        const auto code = static_cast<std::uint32_t>(text[length]);
        if (code == 0) break;
        if (code >= 128) return false;
        bytes[length] = static_cast<char>(code);
        ++length;
    }
    if (length == bytes.size()) return false;
    double plain = 0.0;
    if (detail::parse_decimal({bytes.data(), length}, plain) != detail::DecimalResult::Ok) {
        return false;
    }
    return plain_to_normalized(id, plain, destination);
}

[[nodiscard]] std::size_t parameter_index(ParamID id) noexcept {
    const auto descriptors = parameter_descriptors();
    for (std::size_t index = 0; index < descriptors.size(); ++index) {
        if (descriptors[index].id == id) return index;
    }
    return descriptors.size();
}

[[nodiscard]] bool snapshot_plain(const ControlSnapshot& snapshot,
                                  const ParameterDescriptor& descriptor,
                                  double& destination) noexcept {
    const auto manual = static_cast<std::size_t>(descriptor.manual);
    switch (descriptor.event_type) {
    case EventType::BankDrawbar: {
        const auto index = static_cast<std::size_t>(descriptor.index);
        destination = snapshot.drawbars[manual][index / kDrawbarCount][index % kDrawbarCount];
        return true;
    }
    case EventType::SelectBank:
        destination = static_cast<double>(snapshot.selected_banks[manual]);
        return true;
    case EventType::SelectPreset: {
        PresetSelection selection{};
        if (!control_preset_selection(snapshot, descriptor.manual, selection)) return false;
        destination = static_cast<double>(selection);
        return true;
    }
    case EventType::Expression:
        destination = snapshot.expression;
        return true;
    case EventType::Percussion:
        switch (descriptor.index) {
        case 0: destination = snapshot.percussion.enabled ? 1.0 : 0.0; return true;
        case 1: destination = static_cast<double>(snapshot.percussion.harmonic); return true;
        case 2: destination = static_cast<double>(snapshot.percussion.volume); return true;
        case 3: destination = static_cast<double>(snapshot.percussion.decay); return true;
        default: return false;
        }
    case EventType::PedalDrawbar:
        destination = snapshot.pedal_drawbars[descriptor.index];
        return true;
    default:
        return false;
    }
}

} // namespace

Steinberg::FUnknown* Controller::createInstance(void* context) {
    static_cast<void>(context);
    try {
        return static_cast<Steinberg::Vst::IEditController*>(new Controller);
    } catch (...) {
        return nullptr;
    }
}

Steinberg::tresult PLUGIN_API Controller::initialize(Steinberg::FUnknown* context) {
    if (initialized_) return Steinberg::kResultFalse;
    std::array<double, kParameterCount> defaults{};
    std::size_t index = 0;
    for (const auto& descriptor : parameter_descriptors()) {
        ParameterInfo parameter_info{};
        if (!make_parameter_info(descriptor, parameter_info)) return Steinberg::kInternalError;
        defaults[index++] = parameter_info.defaultNormalizedValue;
    }
    const auto result = EditController::initialize(context);
    if (result != Steinberg::kResultOk) return result;
    values_ = defaults;
    initialized_ = true;
    return Steinberg::kResultOk;
}

Steinberg::tresult PLUGIN_API Controller::terminate() {
    if (!initialized_) return Steinberg::kResultFalse;
    initialized_ = false;
    return EditController::terminate();
}

Steinberg::tresult PLUGIN_API Controller::setComponentState(Steinberg::IBStream* state) {
    if (!initialized_) return Steinberg::kResultFalse;
    ControlSnapshot candidate{};
    const auto result = read_control_state(state, candidate);
    if (result != Steinberg::kResultOk) return result;

    std::array<double, kParameterCount> values{};
    std::size_t index = 0;
    for (const auto& descriptor : parameter_descriptors()) {
        double plain = 0.0;
        if (!snapshot_plain(candidate, descriptor, plain) ||
            !plain_to_normalized(descriptor.id, plain, values[index])) {
            return Steinberg::kInternalError;
        }
        ++index;
    }
    // One fixed value assignment follows complete validation. This generic
    // controller has no custom-view observers; no reentrant partial update or
    // IComponentHandler gesture is emitted. New selector values reflect the
    // effective route, including Cancel; old bank values retain the edit bank.
    // Subsequent host writes continue to cache their accepted raw value.
    values_ = values;
    return Steinberg::kResultOk;
}

Steinberg::int32 PLUGIN_API Controller::getParameterCount() {
    return initialized_ ? static_cast<Steinberg::int32>(kParameterCount) : 0;
}

Steinberg::tresult PLUGIN_API Controller::getParameterInfo(
    Steinberg::int32 index, ParameterInfo& info) {
    if (!initialized_ || index < 0 || static_cast<std::size_t>(index) >= kParameterCount) {
        return Steinberg::kInvalidArgument;
    }
    return make_parameter_info(parameter_descriptors()[static_cast<std::size_t>(index)], info)
        ? Steinberg::kResultOk : Steinberg::kInternalError;
}

ParamValue PLUGIN_API Controller::getParamNormalized(ParamID id) {
    const auto index = parameter_index(id);
    return initialized_ && index < values_.size() ? values_[index] : 0.0;
}

Steinberg::tresult PLUGIN_API Controller::setParamNormalized(ParamID id, ParamValue value) {
    Event event{};
    if (!initialized_ || !normalized_to_event(id, value, 0, event)) {
        return Steinberg::kInvalidArgument;
    }
    const auto index = parameter_index(id);
    if (index == values_.size()) return Steinberg::kResultFalse;
    values_[index] = value;
    return Steinberg::kResultOk;
}

Steinberg::tresult PLUGIN_API Controller::getParamStringByValue(
    ParamID id, ParamValue value, String128 text) {
    if (!initialized_ || text == nullptr) return Steinberg::kInvalidArgument;
    try {
        return format_value(id, value, text) ? Steinberg::kResultOk : Steinberg::kResultFalse;
    } catch (const std::bad_alloc&) {
        return Steinberg::kOutOfMemory;
    } catch (...) {
        return Steinberg::kInternalError;
    }
}

Steinberg::tresult PLUGIN_API Controller::getParamValueByString(
    ParamID id, TChar* text, ParamValue& value) {
    if (!initialized_ || text == nullptr) return Steinberg::kInvalidArgument;
    try {
        return parse_value(id, text, value) ? Steinberg::kResultOk : Steinberg::kResultFalse;
    } catch (const std::bad_alloc&) {
        return Steinberg::kOutOfMemory;
    } catch (...) {
        return Steinberg::kInternalError;
    }
}

ParamValue PLUGIN_API Controller::normalizedParamToPlain(ParamID id, ParamValue value) {
    Event event{};
    return initialized_ && normalized_to_event(id, value, 0, event) ? event.value : 0.0;
}

ParamValue PLUGIN_API Controller::plainParamToNormalized(ParamID id, ParamValue value) {
    double normalized = 0.0;
    return initialized_ && plain_to_normalized(id, value, normalized) ? normalized : 0.0;
}

} // namespace hammond::vst3
