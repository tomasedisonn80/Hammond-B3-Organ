#include "NativeHarness.h"

#include "hammond/ControlStateIO.h"

#include <algorithm>
#include <cstring>
#include <sstream>
#include <stdexcept>

namespace hammond::native_test {
namespace {

template <class Interface>
Steinberg::tresult query_borrowed(Interface* self, const Steinberg::TUID iid,
                                 void** object) noexcept {
    if (object == nullptr) return Steinberg::kInvalidArgument;
    *object = nullptr;
    if (std::memcmp(iid, Interface::iid.toTUID(), sizeof(Steinberg::TUID)) == 0 ||
        std::memcmp(iid, Steinberg::FUnknown::iid.toTUID(), sizeof(Steinberg::TUID)) == 0) {
        *object = self;
        return Steinberg::kResultOk;
    }
    return Steinberg::kNoInterface;
}

[[nodiscard]] Steinberg::int32 checked_count(std::size_t size) noexcept {
    return size <= static_cast<std::size_t>(std::numeric_limits<Steinberg::int32>::max())
        ? static_cast<Steinberg::int32>(size) : -1;
}

} // namespace

void require(bool condition, std::string_view message) {
    if (!condition) throw std::runtime_error(std::string(message));
}

void require_ok(Steinberg::tresult result, std::string_view operation) {
    if (result != Steinberg::kResultOk) {
        throw std::runtime_error(std::string(operation) + " returned " + std::to_string(result));
    }
}

Steinberg::FUID expected_processor_id() {
    return {0x19F9ADC0, 0x533F42B4, 0xB96BD51D, 0x6547E838};
}

Steinberg::FUID expected_controller_id() {
    return {0x0DEE76AB, 0x26BC475A, 0xBF64F138, 0xC89FB0E0};
}

std::string ascii(const sv::TChar* text, std::size_t capacity) {
    require(text != nullptr, "null native string");
    std::string result;
    for (std::size_t index = 0; index < capacity; ++index) {
        if (text[index] == 0) return result;
        const auto code = static_cast<std::uint32_t>(text[index]);
        require(code < 128, "unexpected non-ASCII native metadata");
        result.push_back(static_cast<char>(code));
    }
    throw std::runtime_error("unterminated native string");
}

std::string snapshot_text(const ControlSnapshot& controls) {
    std::string bytes;
    std::string error;
    require(serialize_controls(controls, bytes, error), "test snapshot serialization failed: " + error);
    return bytes;
}

ControlSnapshot parse_snapshot(std::string_view text) {
    ControlSnapshot snapshot{};
    std::istringstream stream{std::string(text)};
    std::string error;
    require(parse_controls(stream, snapshot, error), "saved native state is invalid: " + error);
    return snapshot;
}

MemoryStream::MemoryStream(std::string_view initial) : bytes(initial) {}

Steinberg::tresult PLUGIN_API MemoryStream::queryInterface(
    const Steinberg::TUID requested_id, void** object) {
    return query_borrowed<Steinberg::IBStream>(this, requested_id, object);
}

Steinberg::tresult PLUGIN_API MemoryStream::read(
    void* buffer, Steinberg::int32 count, Steinberg::int32* actual) {
    ++read_calls;
    if (actual != nullptr) *actual = 0;
    if (count < 0 || (count > 0 && buffer == nullptr) || cursor > bytes.size()) {
        return Steinberg::kInvalidArgument;
    }
    const auto size = std::min({static_cast<std::size_t>(count), read_chunk, bytes.size() - cursor});
    if (size != 0) std::memcpy(buffer, bytes.data() + cursor, size);
    cursor += size;
    if (actual != nullptr) *actual = read_count_override.value_or(static_cast<Steinberg::int32>(size));
    return read_result_override.value_or(size == 0 && false_at_eof
        ? Steinberg::kResultFalse : Steinberg::kResultOk);
}

Steinberg::tresult PLUGIN_API MemoryStream::write(
    void* buffer, Steinberg::int32 count, Steinberg::int32* actual) {
    ++write_calls;
    if (actual != nullptr) *actual = 0;
    if (count < 0 || (count > 0 && buffer == nullptr) || cursor > bytes.size()) {
        return Steinberg::kInvalidArgument;
    }
    const auto size = std::min(static_cast<std::size_t>(count), write_chunk);
    if (size > bytes.max_size() - cursor) return Steinberg::kOutOfMemory;
    if (cursor + size > bytes.size()) bytes.resize(cursor + size);
    if (size != 0) std::memcpy(bytes.data() + cursor, buffer, size);
    cursor += size;
    if (actual != nullptr) *actual = write_count_override.value_or(static_cast<Steinberg::int32>(size));
    return write_result_override.value_or(Steinberg::kResultOk);
}

Steinberg::tresult PLUGIN_API MemoryStream::seek(
    Steinberg::int64 position, Steinberg::int32 mode, Steinberg::int64* actual) {
    const auto maximum = static_cast<std::size_t>(std::numeric_limits<Steinberg::int64>::max());
    if (cursor > maximum || bytes.size() > maximum) return Steinberg::kInvalidArgument;
    Steinberg::int64 base = 0;
    switch (mode) {
    case kIBSeekSet: break;
    case kIBSeekCur: base = static_cast<Steinberg::int64>(cursor); break;
    case kIBSeekEnd: base = static_cast<Steinberg::int64>(bytes.size()); break;
    default: return Steinberg::kInvalidArgument;
    }
    if ((position < 0 && position < -base) ||
        (position > 0 && base > std::numeric_limits<Steinberg::int64>::max() - position)) {
        return Steinberg::kInvalidArgument;
    }
    const auto next = base + position;
    if (static_cast<std::uint64_t>(next) > bytes.size()) return Steinberg::kInvalidArgument;
    cursor = static_cast<std::size_t>(next);
    if (actual != nullptr) *actual = next;
    return Steinberg::kResultOk;
}

Steinberg::tresult PLUGIN_API MemoryStream::tell(Steinberg::int64* position) {
    if (position == nullptr ||
        cursor > static_cast<std::size_t>(std::numeric_limits<Steinberg::int64>::max())) {
        return Steinberg::kInvalidArgument;
    }
    *position = static_cast<Steinberg::int64>(cursor);
    return Steinberg::kResultOk;
}

Steinberg::tresult PLUGIN_API EventList::queryInterface(
    const Steinberg::TUID requested_id, void** object) {
    return query_borrowed<sv::IEventList>(this, requested_id, object);
}

Steinberg::int32 PLUGIN_API EventList::getEventCount() {
    return count_override.value_or(checked_count(events.size()));
}

Steinberg::tresult PLUGIN_API EventList::getEvent(Steinberg::int32 index, sv::Event& event) {
    if (index < 0 || index == fail_index || static_cast<std::size_t>(index) >= events.size()) {
        return Steinberg::kResultFalse;
    }
    event = events[static_cast<std::size_t>(index)];
    return Steinberg::kResultOk;
}

Steinberg::tresult PLUGIN_API EventList::addEvent(sv::Event& event) {
    events.push_back(event);
    return Steinberg::kResultOk;
}

Steinberg::tresult PLUGIN_API ParameterQueue::queryInterface(
    const Steinberg::TUID requested_id, void** object) {
    return query_borrowed<sv::IParamValueQueue>(this, requested_id, object);
}

Steinberg::int32 PLUGIN_API ParameterQueue::getPointCount() {
    return count_override.value_or(checked_count(points.size()));
}

Steinberg::tresult PLUGIN_API ParameterQueue::getPoint(
    Steinberg::int32 index, Steinberg::int32& offset, sv::ParamValue& value) {
    if (index < 0 || index == fail_index || static_cast<std::size_t>(index) >= points.size()) {
        return Steinberg::kResultFalse;
    }
    const auto& point = points[static_cast<std::size_t>(index)];
    offset = point.offset;
    value = point.normalized;
    return Steinberg::kResultOk;
}

Steinberg::tresult PLUGIN_API ParameterQueue::addPoint(
    Steinberg::int32 offset, sv::ParamValue value, Steinberg::int32& index) {
    const auto next = checked_count(points.size());
    if (next < 0) return Steinberg::kResultFalse;
    points.push_back({offset, value});
    index = next;
    return Steinberg::kResultOk;
}

ParameterQueue& ParameterChanges::add_queue(sv::ParamID id) {
    queues.push_back(std::make_unique<ParameterQueue>(id));
    return *queues.back();
}

Steinberg::tresult PLUGIN_API ParameterChanges::queryInterface(
    const Steinberg::TUID requested_id, void** object) {
    return query_borrowed<sv::IParameterChanges>(this, requested_id, object);
}

Steinberg::int32 PLUGIN_API ParameterChanges::getParameterCount() {
    return count_override.value_or(checked_count(queues.size()));
}

sv::IParamValueQueue* PLUGIN_API ParameterChanges::getParameterData(Steinberg::int32 index) {
    if (index < 0 || index == null_index || static_cast<std::size_t>(index) >= queues.size()) {
        return nullptr;
    }
    return queues[static_cast<std::size_t>(index)].get();
}

sv::IParamValueQueue* PLUGIN_API ParameterChanges::addParameterData(
    const sv::ParamID& id, Steinberg::int32& index) {
    for (std::size_t current = 0; current < queues.size(); ++current) {
        if (queues[current] != nullptr && queues[current]->id == id) {
            index = checked_count(current);
            return queues[current].get();
        }
    }
    const auto next = checked_count(queues.size());
    if (next < 0) return nullptr;
    auto& queue = add_queue(id);
    index = next;
    return &queue;
}

StereoBlock::StereoBlock(std::size_t capacity) : left(capacity), right(capacity) {
    require(checked_count(capacity) >= 0, "test audio capacity exceeds signed native count");
    channels = {left.data(), right.data()};
    bus.numChannels = 2;
    bus.channelBuffers32 = channels.data();
    data.processMode = sv::kRealtime;
    data.symbolicSampleSize = sv::kSample32;
    data.numOutputs = 1;
    data.outputs = &bus;
    set_frames(static_cast<Steinberg::int32>(capacity));
}

void StereoBlock::set_frames(Steinberg::int32 frames) {
    require(frames >= 0 && static_cast<std::size_t>(frames) <= left.size(),
            "test block frames exceed preallocated capacity");
    data.numSamples = frames;
}

void StereoBlock::fill(float value) {
    std::fill(left.begin(), left.end(), value);
    std::fill(right.begin(), right.end(), value);
}

NativePlugin::NativePlugin(const std::string& bundle_path) {
    try {
        std::string error;
        module_ = VST3::Hosting::Module::create(bundle_path, error);
        require(module_ != nullptr, "could not load native bundle: " + error);
        host_ = Steinberg::owned(new sv::HostApplication());
        const auto& factory = module_->getFactory();
        factory.setHostContext(host_.get());
        component = factory.createInstance<sv::IComponent>(
            VST3::UID(expected_processor_id().toTUID()));
        require(component.get() != nullptr, "factory did not create expected processor class");
        processor = Steinberg::FUnknownPtr<sv::IAudioProcessor>(component.get());
        require(processor.get() != nullptr, "component has no native audio processor interface");
        require_ok(component->initialize(host_.get()), "component initialize");
        component_initialized_ = true;
        controller = factory.createInstance<sv::IEditController>(
            VST3::UID(expected_controller_id().toTUID()));
        require(controller.get() != nullptr, "factory did not create expected controller class");
        require_ok(controller->initialize(host_.get()), "controller initialize");
        controller_initialized_ = true;
    } catch (...) {
        shutdown();
        throw;
    }
}

NativePlugin::~NativePlugin() { shutdown(); }

void NativePlugin::shutdown() noexcept {
    // Positive test paths explicitly check balanced transitions before this
    // fallback. Cleanup also covers exceptions without destroying live audio.
    try {
        if (processing_ && processor.get() != nullptr) (void)processor->setProcessing(false);
        processing_ = false;
        if (active_ && component.get() != nullptr) (void)component->setActive(false);
        active_ = false;
        if (component_initialized_ && component.get() != nullptr) (void)component->terminate();
        component_initialized_ = false;
        if (controller_initialized_ && controller.get() != nullptr) (void)controller->terminate();
        controller_initialized_ = false;
    } catch (...) {
        // No test continues after a throwing teardown; destructor still releases
        // interfaces before their implementing module is unloaded.
    }
    controller = nullptr;
    processor = nullptr;
    component = nullptr;
    if (module_ != nullptr) module_->getFactory().setHostContext(nullptr);
    module_.reset();
    host_ = nullptr;
}

void NativePlugin::configure(double sample_rate, Steinberg::int32 maximum,
                              Steinberg::int32 mode) {
    require(!active_ && !processing_, "test host configured an active processor");
    sv::ProcessSetup setup{mode, sv::kSample32, maximum, sample_rate};
    require_ok(processor->setupProcessing(setup), "setupProcessing");
}

void NativePlugin::activate() {
    require(!active_, "test host repeated activation");
    require_ok(component->activateBus(sv::kAudio, sv::kOutput, 0, true), "activate output bus");
    for (Steinberg::int32 index = 0; index < 3; ++index) {
        require_ok(component->activateBus(sv::kEvent, sv::kInput, index, true), "activate event bus");
    }
    require_ok(component->setActive(true), "setActive(true)");
    active_ = true;
}

void NativePlugin::begin_processing() {
    require(active_, "test host started inactive processor");
    require_ok(processor->setProcessing(true), "setProcessing(true)");
    processing_ = true;
}

void NativePlugin::stop_processing() {
    require(processing_, "test host stopped a processor that was not processing");
    require_ok(processor->setProcessing(false), "setProcessing(false)");
    processing_ = false;
}

void NativePlugin::deactivate() {
    require(active_ && !processing_, "test host deactivation requires stopped active instance");
    require_ok(component->setActive(false), "setActive(false)");
    active_ = false;
}

void NativePlugin::start(double sample_rate, Steinberg::int32 maximum,
                         Steinberg::int32 mode) {
    configure(sample_rate, maximum, mode);
    activate();
    begin_processing();
}

Steinberg::tresult NativePlugin::load_state(std::string_view bytes) {
    MemoryStream stream(bytes);
    return component->setState(&stream);
}

Steinberg::tresult NativePlugin::save_state(std::string& bytes) {
    MemoryStream stream;
    const auto result = component->getState(&stream);
    if (result == Steinberg::kResultOk) bytes = std::move(stream.bytes);
    return result;
}

sv::Event note_on(Steinberg::int32 bus, Steinberg::int16 pitch,
                   Steinberg::int32 offset, Steinberg::int16 channel,
                   Steinberg::int32 note_id, float velocity) {
    sv::Event event{};
    event.type = sv::Event::kNoteOnEvent;
    event.busIndex = bus;
    event.sampleOffset = offset;
    event.noteOn = {channel, pitch, 0.0F, velocity, 0, note_id};
    return event;
}

sv::Event note_off(Steinberg::int32 bus, Steinberg::int16 pitch,
                    Steinberg::int32 offset, Steinberg::int16 channel,
                    Steinberg::int32 note_id) {
    sv::Event event{};
    event.type = sv::Event::kNoteOffEvent;
    event.busIndex = bus;
    event.sampleOffset = offset;
    event.noteOff = {channel, pitch, 0.0F, note_id, 0.0F};
    return event;
}

} // namespace hammond::native_test
