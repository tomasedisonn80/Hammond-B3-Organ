#include "Processor.h"

#include "EmbeddedProfile.h"
#include "PluginIds.h"
#include "StateStream.h"
#include "hammond/ConsoleModel.h"
#include "hammond/Profile.h"
#include "pluginterfaces/vst/ivstevents.h"
#include "pluginterfaces/vst/ivstparameterchanges.h"

#include <algorithm>
#include <cmath>
#include <limits>
#include <new>
#include <sstream>
#include <string>

namespace hammond::vst3 {
namespace {

namespace sv = Steinberg::Vst;
using Steinberg::int32;
using Steinberg::tresult;

[[nodiscard]] bool valid_boolean(Steinberg::TBool value) noexcept {
    return value == 0 || value == 1;
}

[[nodiscard]] bool valid_mode(int32 value) noexcept {
    return value == sv::kRealtime || value == sv::kPrefetch || value == sv::kOffline;
}

[[nodiscard]] bool valid_channel(Steinberg::int16 value) noexcept {
    return value >= 0 && value < 16;
}

[[nodiscard]] bool valid_pitch(Steinberg::int16 value) noexcept {
    return value >= 0 && value <= 127;
}

[[nodiscard]] bool normalized(double value) noexcept {
    return std::isfinite(value) && value >= 0.0 && value <= 1.0;
}

// No external data/text pointer is dereferenced or retained for an unsupported
// event. Validate its declared scalar domain and necessary pointer/count shape.
// Unsupported custom expression type IDs have no advertised semantics here.
[[nodiscard]] bool valid_unsupported_event(const sv::Event& event) noexcept {
    switch (event.type) {
    case sv::Event::kDataEvent:
        return event.data.type == sv::DataEvent::kMidiSysEx &&
            (event.data.size == 0 || event.data.bytes != nullptr);
    case sv::Event::kPolyPressureEvent:
        return valid_channel(event.polyPressure.channel) &&
            valid_pitch(event.polyPressure.pitch) &&
            normalized(event.polyPressure.pressure) && event.polyPressure.noteId >= -1;
    case sv::Event::kNoteExpressionValueEvent:
        return event.noteExpressionValue.noteId >= 0 &&
            normalized(event.noteExpressionValue.value);
    case sv::Event::kNoteExpressionIntValueEvent:
        return event.noteExpressionIntValue.noteId >= 0;
    case sv::Event::kNoteExpressionTextEvent:
        return event.noteExpressionText.noteId >= 0 &&
            (event.noteExpressionText.textLen == 0 || event.noteExpressionText.text != nullptr);
    case sv::Event::kChordEvent:
        return valid_pitch(event.chord.root) && valid_pitch(event.chord.bassNote) &&
            (event.chord.textLen == 0 || event.chord.text != nullptr);
    case sv::Event::kScaleEvent:
        return valid_pitch(event.scale.root) &&
            (event.scale.textLen == 0 || event.scale.text != nullptr);
    default:
        // Unknown types and output-only LegacyMIDICCOut are not valid input.
        return false;
    }
}

// Positive velocity is a Boolean press in this organ. Retain a bounded 7-bit
// value without allowing a tiny positive native velocity to round to release.
[[nodiscard]] std::uint8_t note_velocity(float velocity) noexcept {
    if (velocity == 0.0F) {
        return 0;
    }
    const double rounded = std::floor(static_cast<double>(velocity) * 127.0 + 0.5);
    return static_cast<std::uint8_t>(std::max(1.0, rounded));
}

[[nodiscard]] bool valid_sample_range(float* address, std::size_t frames,
                                      std::uintptr_t& begin,
                                      std::uintptr_t& end) noexcept {
    if (address == nullptr || frames > std::numeric_limits<std::size_t>::max() / sizeof(float)) {
        return false;
    }
    const auto bytes = frames * sizeof(float);
    begin = reinterpret_cast<std::uintptr_t>(address);
    if (begin % alignof(float) != 0 ||
        bytes > std::numeric_limits<std::uintptr_t>::max() - begin) {
        return false;
    }
    end = begin + bytes;
    return true;
}

} // namespace

Processor::Processor() {
    setControllerClass(kControllerClassId);
}

Steinberg::FUnknown* Processor::createInstance(void* /*context*/) {
    try {
        return static_cast<sv::IAudioProcessor*>(new Processor());
    } catch (...) {
        return nullptr;
    }
}

tresult PLUGIN_API Processor::initialize(Steinberg::FUnknown* context) {
    if (initialized_) {
        return Steinberg::kResultFalse;
    }
    // Parsing and all SDK bus construction happen before audio can start.
    try {
        if (!profile_loaded_) {
            if (kEmbeddedProfileText.empty() || kEmbeddedProfileText.size() > kMaxCompiledProfileBytes) {
                return Steinberg::kResultFalse;
            }
            std::istringstream input{std::string{kEmbeddedProfileText}};
            std::string error;
            RuntimeProfile candidate{};
            if (!load_runtime_profile(input, candidate, error)) {
                return Steinberg::kResultFalse;
            }
            profile_ = candidate;
            profile_loaded_ = true;
        }
        const auto result = AudioEffect::initialize(context);
        if (result != Steinberg::kResultOk) {
            return result;
        }
        addAudioOutput(STR16("Dry stereo"), sv::SpeakerArr::kStereo);
        addEventInput(STR16("Upper"), 16);
        addEventInput(STR16("Lower"), 16, sv::kAux);
        addEventInput(STR16("Pedals"), 16, sv::kAux);
        initialized_ = true;
        return Steinberg::kResultOk;
    } catch (...) {
        // A partially constructed bus set is never published as initialized.
        (void)AudioEffect::terminate();
        return Steinberg::kOutOfMemory;
    }
}

tresult PLUGIN_API Processor::terminate() {
    if (!initialized_ || active_ || processing_) {
        return Steinberg::kResultFalse;
    }
    const auto result = AudioEffect::terminate();
    if (result == Steinberg::kResultOk) {
        initialized_ = false;
    }
    // A host reinitializing this same object does not reset its musical epoch
    // or accepted state queue. Object destruction/construction creates a new one.
    return result;
}

tresult PLUGIN_API Processor::setActive(Steinberg::TBool state) {
    if (!valid_boolean(state)) {
        return Steinberg::kInvalidArgument;
    }
    if (!initialized_ || processing_ || active_ == (state != 0) ||
        (state != 0 && !prepared_)) {
        return Steinberg::kResultFalse;
    }
    active_ = state != 0;
    return Steinberg::kResultOk;
}

tresult PLUGIN_API Processor::activateBus(
    sv::MediaType type, sv::BusDirection direction, int32 index, Steinberg::TBool state) {
    if (!valid_boolean(state) || index < 0 ||
        (direction != sv::kInput && direction != sv::kOutput) ||
        (type != sv::kAudio && type != sv::kEvent)) {
        return Steinberg::kInvalidArgument;
    }
    if (!initialized_ || processing_) {
        return Steinberg::kResultFalse;
    }
    return AudioEffect::activateBus(type, direction, index, state);
}

tresult PLUGIN_API Processor::getRoutingInfo(sv::RoutingInfo& input, sv::RoutingInfo& output) {
    if (!initialized_ || input.mediaType != sv::kEvent || input.busIndex < 0 ||
        input.busIndex >= 3 || input.channel < -1 || input.channel >= 16) {
        return Steinberg::kInvalidArgument;
    }
    output = {sv::kAudio, 0, -1};
    return Steinberg::kResultOk;
}

tresult PLUGIN_API Processor::setBusArrangements(
    sv::SpeakerArrangement* /*inputs*/, int32 input_count,
    sv::SpeakerArrangement* outputs, int32 output_count) {
    if (input_count < 0 || output_count < 0 || (output_count > 0 && outputs == nullptr)) {
        return Steinberg::kInvalidArgument;
    }
    if (!initialized_ || processing_ || input_count != 0 || output_count != 1) {
        return Steinberg::kResultFalse;
    }
    return outputs[0] == sv::SpeakerArr::kStereo ? Steinberg::kResultOk : Steinberg::kResultFalse;
}

tresult PLUGIN_API Processor::canProcessSampleSize(int32 symbolic_sample_size) {
    return symbolic_sample_size == sv::kSample32 ? Steinberg::kResultTrue : Steinberg::kResultFalse;
}

tresult PLUGIN_API Processor::setupProcessing(sv::ProcessSetup& setup) {
    if (!initialized_ || active_ || processing_) {
        return Steinberg::kResultFalse;
    }
    if (!valid_mode(setup.processMode) || setup.symbolicSampleSize != sv::kSample32 ||
        setup.maxSamplesPerBlock < 1 ||
        setup.maxSamplesPerBlock > static_cast<int32>(kHardMaxBlockFrames) ||
        !is_supported_sample_rate(setup.sampleRate)) {
        return Steinberg::kInvalidArgument;
    }
    const auto maximum = static_cast<std::uint32_t>(setup.maxSamplesPerBlock);
    const auto result = prepared_ ? timeline_.reconfigure(setup.sampleRate, maximum) :
        timeline_.prepare(profile_, ProcessSpec{setup.sampleRate, maximum, kNativeInitialSeed, 0},
                          make_nominal_console_model());
    if (result != Status::Ok) {
        return Steinberg::kResultFalse;
    }
    processSetup = setup;
    prepared_ = true;
    return Steinberg::kResultOk;
}

tresult PLUGIN_API Processor::setProcessing(Steinberg::TBool state) {
    if (!valid_boolean(state)) {
        return Steinberg::kInvalidArgument;
    }
    if (!initialized_ || !prepared_ || !active_) {
        return Steinberg::kResultFalse;
    }
    processing_ = state != 0;
    return Steinberg::kResultOk;
}

Steinberg::uint32 PLUGIN_API Processor::getTailSamples() {
    // Held notes and the shared generator are not suspended by a silence hint.
    // This conservative declaration is not a delay/reverb or device guarantee.
    return sv::kInfiniteTail;
}

bool Processor::admit_output(sv::ProcessData& data, OutputView& output) noexcept {
    if (data.numInputs != 0 || data.numOutputs < 0 || data.numOutputs > 1) {
        return false;
    }
    if (data.numOutputs == 0) {
        return true;
    }
    if (data.outputs == nullptr) {
        return false;
    }
    auto& bus = data.outputs[0];
    if (bus.numChannels == 0 && data.numSamples == 0) {
        output = {&bus, nullptr, nullptr, false, true};
        return true;
    }
    if (bus.numChannels != 2 || bus.channelBuffers32 == nullptr) {
        return false;
    }
    const auto* configured = getAudioOutput(0);
    if (configured == nullptr) {
        return false;
    }
    if (!configured->isActive()) {
        // Inactive buses have a channel array but may have null sample pointers.
        // Neither their samples nor their existing flags are written.
        output = {&bus, nullptr, nullptr, false, false};
        return true;
    }
    auto* const left = bus.channelBuffers32[0];
    auto* const right = bus.channelBuffers32[1];
    if (data.numSamples > 0) {
        std::uintptr_t left_begin = 0;
        std::uintptr_t left_end = 0;
        std::uintptr_t right_begin = 0;
        std::uintptr_t right_end = 0;
        const auto frames = static_cast<std::size_t>(data.numSamples);
        if (!valid_sample_range(left, frames, left_begin, left_end) ||
            !valid_sample_range(right, frames, right_begin, right_end)) {
            return false;
        }
        if (left_begin != right_begin && left_begin < right_end && right_begin < left_end) {
            return false;
        }
    }
    output = {&bus, left, right, data.numSamples > 0, true};
    return true;
}

bool Processor::admit_input(sv::ProcessData& data, NativeProcessDiagnostics& report,
                            std::size_t& queue_count, std::size_t& musical_count) noexcept {
    const auto event_count = data.inputEvents == nullptr ? 0 : data.inputEvents->getEventCount();
    const auto parameter_count = data.inputParameterChanges == nullptr ? 0 :
        data.inputParameterChanges->getParameterCount();
    if (event_count < 0 || event_count > static_cast<int32>(kMaxEventsPerBlock) ||
        parameter_count < 0 || parameter_count > static_cast<int32>(kParameterCount)) {
        return false;
    }
    auto raw_count = static_cast<std::size_t>(event_count) + timeline_.carry_count();
    if (raw_count > kMaxEventsPerBlock) {
        return false;
    }
    report.raw_events = static_cast<std::uint32_t>(event_count);
    std::size_t point_count = 0;
    for (int32 queue_index = 0; queue_index < parameter_count; ++queue_index) {
        auto* const source = data.inputParameterChanges->getParameterData(queue_index);
        if (source == nullptr) {
            return false;
        }
        const auto id = source->getParameterId();
        ParameterDescriptor descriptor{};
        if (!parameter_descriptor(id, descriptor)) {
            return false;
        }
        for (std::size_t previous = 0; previous < queue_count; ++previous) {
            if (queues_[previous].parameter_id == id) {
                return false;
            }
        }
        const auto count = source->getPointCount();
        if (count < 0 || static_cast<std::size_t>(count) > kMaxEventsPerBlock - raw_count) {
            return false;
        }
        const auto start = point_count;
        int32 previous_offset = -1;
        for (int32 point_index = 0; point_index < count; ++point_index) {
            int32 offset = -1;
            double value = 0.0;
            if (source->getPoint(point_index, offset, value) != Steinberg::kResultOk ||
                offset < 0 || offset > data.numSamples || offset < previous_offset ||
                !normalized(value)) {
                return false;
            }
            points_[point_count++] = {offset, value};
            previous_offset = offset;
        }
        const auto size = static_cast<std::size_t>(count);
        queues_[queue_count++] = {id, {points_.data() + start, size}};
        raw_count += size;
    }
    report.raw_parameter_points = static_cast<std::uint32_t>(point_count);

    int32 previous_offset = -1;
    for (int32 event_index = 0; event_index < event_count; ++event_index) {
        sv::Event event{};
        if (data.inputEvents->getEvent(event_index, event) != Steinberg::kResultOk ||
            event.busIndex < 0 || event.busIndex >= 3 ||
            event.sampleOffset < 0 || event.sampleOffset > data.numSamples ||
            event.sampleOffset < previous_offset || !std::isfinite(event.ppqPosition)) {
            return false;
        }
        previous_offset = event.sampleOffset;
        const bool on = event.type == sv::Event::kNoteOnEvent;
        if (!on && event.type != sv::Event::kNoteOffEvent) {
            if (!valid_unsupported_event(event)) {
                return false;
            }
            ++report.filtered_unsupported_events;
            continue;
        }
        const auto channel = on ? event.noteOn.channel : event.noteOff.channel;
        const auto pitch = on ? event.noteOn.pitch : event.noteOff.pitch;
        const auto velocity = on ? event.noteOn.velocity : event.noteOff.velocity;
        const auto note_id = on ? event.noteOn.noteId : event.noteOff.noteId;
        const auto tuning = on ? event.noteOn.tuning : event.noteOff.tuning;
        if (!valid_channel(channel) || !valid_pitch(pitch) || !normalized(velocity) ||
            note_id < -1 || !std::isfinite(tuning)) {
            return false;
        }
        // The nominal profile fixes all source frequencies. The optional native
        // tuning and length fields do not add per-note oscillators or auto-off.
        if (tuning != 0.0F) {
            ++report.ignored_note_tuning;
        }
        const int32 maximum_pitch = event.busIndex == 2 ? 60 : kMaxManualMidiNote;
        if (pitch < kMinManualMidiNote || pitch > maximum_pitch) {
            ++report.filtered_pitch_events;
            continue;
        }
        const auto* const bus = getEventInput(event.busIndex);
        if (bus == nullptr || !bus->isActive()) {
            // Reject a supported note sent to an inactive bus. In particular,
            // a release is never silently filtered because of bus activation.
            return false;
        }
        const auto offset = static_cast<std::uint32_t>(event.sampleOffset);
        const auto native_channel = static_cast<std::uint8_t>(channel);
        const auto native_velocity = on ? note_velocity(velocity) : std::uint8_t{0};
        if (event.busIndex == 2) {
            musical_[musical_count++] = PedalNoteEvent{
                offset, on ? PedalNoteKind::On : PedalNoteKind::Off, 0, native_channel,
                PedalId{static_cast<std::uint8_t>(pitch - 35)}, native_velocity, note_id};
        } else {
            musical_[musical_count++] = HostNoteEvent{
                offset, on ? HostNoteKind::On : HostNoteKind::Off,
                static_cast<std::uint8_t>(event.busIndex), native_channel,
                static_cast<std::uint8_t>(pitch), native_velocity, note_id};
        }
    }
    report.translated_notes = static_cast<std::uint32_t>(musical_count);
    return true;
}

tresult PLUGIN_API Processor::process(sv::ProcessData& data) {
    if (!initialized_ || !prepared_ || !active_ || !processing_) {
        return Steinberg::kResultFalse;
    }
    if (data.symbolicSampleSize != sv::kSample32 || !valid_mode(data.processMode) ||
        ((data.processMode == sv::kOffline) != (processSetup.processMode == sv::kOffline)) ||
        data.numSamples < 0 || data.numSamples > processSetup.maxSamplesPerBlock) {
        return Steinberg::kInvalidArgument;
    }
    OutputView output{};
    if (!admit_output(data, output)) {
        return Steinberg::kInvalidArgument;
    }
    NativeProcessDiagnostics report{};
    report.frames = static_cast<std::uint32_t>(data.numSamples);
    std::size_t queue_count = 0;
    std::size_t musical_count = 0;
    if (!admit_input(data, report, queue_count, musical_count)) {
        return Steinberg::kInvalidArgument;
    }
    StateExchangeBatch batch{};
    if (state_exchange_.audio_peek(batch) != StateExchangeStatus::Ok ||
        state_exchange_.audio_can_commit(batch) != StateExchangeStatus::Ok) {
        return Steinberg::kResultFalse;
    }
    const auto frames = static_cast<std::size_t>(data.numSamples);
    report.timeline = timeline_.process(report.frames, {mono_.data(), frames},
        {queues_.data(), queue_count}, {musical_.data(), musical_count}, batch.snapshots());
    if (!report.timeline) {
        return Steinberg::kResultFalse;
    }
    // Nonfailing after the preflight above: this is the sole audio consumer,
    // no intervening commit exists, UI only appends, and Engine owns a valid
    // snapshot. No new capacity/resource decision may follow timeline commit.
    (void)state_exchange_.audio_commit(batch, timeline_.engine().controls_snapshot());

    report.rendered_silence = std::all_of(mono_.begin(), mono_.begin() + data.numSamples,
                                        [](float sample) { return sample == 0.0F; });
    report.connected_output = output.write_samples;
    if (output.write_samples) {
        std::copy_n(mono_.data(), frames, output.left);
        if (output.right != output.left) {
            std::copy_n(mono_.data(), frames, output.right);
        }
    }
    if (output.write_flags) {
        output.bus->silenceFlags = output.bus->numChannels == 0 ? 0U :
            (report.rendered_silence ? 3U : 0U);
    }
    last_process_ = report;
    return Steinberg::kResultOk;
}

tresult PLUGIN_API Processor::setState(Steinberg::IBStream* state) {
    if (!initialized_) {
        return Steinberg::kResultFalse;
    }
    ControlSnapshot controls{};
    const auto result = read_control_state(state, controls);
    if (result != Steinberg::kResultOk) {
        return result;
    }
    return state_exchange_.ui_enqueue(controls) ? Steinberg::kResultOk : Steinberg::kResultFalse;
}

tresult PLUGIN_API Processor::getState(Steinberg::IBStream* state) {
    if (!initialized_ || state == nullptr) {
        return state == nullptr ? Steinberg::kInvalidArgument : Steinberg::kResultFalse;
    }
    ControlSnapshot controls{};
    if (!state_exchange_.ui_snapshot_for_save(controls)) {
        return Steinberg::kResultFalse;
    }
    return write_control_state(state, controls);
}

} // namespace hammond::vst3
