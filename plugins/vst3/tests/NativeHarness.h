#pragma once

#include "hammond/ControlState.h"
#include "pluginterfaces/base/ibstream.h"
#include "pluginterfaces/vst/ivstaudioprocessor.h"
#include "pluginterfaces/vst/ivstcomponent.h"
#include "pluginterfaces/vst/ivsteditcontroller.h"
#include "pluginterfaces/vst/ivstevents.h"
#include "pluginterfaces/vst/ivstparameterchanges.h"
#include "public.sdk/source/vst/hosting/hostclasses.h"
#include "public.sdk/source/vst/hosting/module.h"

#include <array>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <memory>
#include <optional>
#include <string>
#include <string_view>
#include <vector>

// Test-host fixtures. Construction, vector/string mutation, state parsing and
// assertions occur outside measured callbacks. The interface getters copy from
// already-owned storage and do not allocate. Borrowed fixture FUnknown methods
// do not delete stack-owned objects; the test owns their complete lifetime.
namespace hammond::native_test {

namespace sv = Steinberg::Vst;

void require(bool condition, std::string_view message);
void require_ok(Steinberg::tresult result, std::string_view operation);
[[nodiscard]] Steinberg::FUID expected_processor_id();
[[nodiscard]] Steinberg::FUID expected_controller_id();
[[nodiscard]] std::string ascii(const sv::TChar* text, std::size_t capacity = 128);
[[nodiscard]] std::string snapshot_text(const ControlSnapshot& controls);
[[nodiscard]] ControlSnapshot parse_snapshot(std::string_view text);

class MemoryStream final : public Steinberg::IBStream {
public:
    explicit MemoryStream(std::string_view initial = {});

    std::string bytes{};
    std::size_t cursor{0};
    std::size_t read_chunk{static_cast<std::size_t>(std::numeric_limits<Steinberg::int32>::max())};
    std::size_t write_chunk{static_cast<std::size_t>(std::numeric_limits<Steinberg::int32>::max())};
    bool false_at_eof{false};
    std::optional<Steinberg::tresult> read_result_override{};
    std::optional<Steinberg::tresult> write_result_override{};
    std::optional<Steinberg::int32> read_count_override{};
    std::optional<Steinberg::int32> write_count_override{};
    std::uint64_t read_calls{0};
    std::uint64_t write_calls{0};

    Steinberg::tresult PLUGIN_API queryInterface(const Steinberg::TUID requested_id, void** object) override;
    Steinberg::uint32 PLUGIN_API addRef() override { return 1; }
    Steinberg::uint32 PLUGIN_API release() override { return 1; }
    Steinberg::tresult PLUGIN_API read(void* buffer, Steinberg::int32 count,
                                      Steinberg::int32* actual = nullptr) override;
    Steinberg::tresult PLUGIN_API write(void* buffer, Steinberg::int32 count,
                                       Steinberg::int32* actual = nullptr) override;
    Steinberg::tresult PLUGIN_API seek(Steinberg::int64 position, Steinberg::int32 mode,
                                      Steinberg::int64* actual = nullptr) override;
    Steinberg::tresult PLUGIN_API tell(Steinberg::int64* position) override;
};

class EventList final : public sv::IEventList {
public:
    std::vector<sv::Event> events{};
    std::optional<Steinberg::int32> count_override{};
    Steinberg::int32 fail_index{-1};

    Steinberg::tresult PLUGIN_API queryInterface(const Steinberg::TUID requested_id, void** object) override;
    Steinberg::uint32 PLUGIN_API addRef() override { return 1; }
    Steinberg::uint32 PLUGIN_API release() override { return 1; }
    Steinberg::int32 PLUGIN_API getEventCount() override;
    Steinberg::tresult PLUGIN_API getEvent(Steinberg::int32 index, sv::Event& event) override;
    Steinberg::tresult PLUGIN_API addEvent(sv::Event& event) override;
};

struct ParameterPoint {
    Steinberg::int32 offset{0};
    double normalized{0.0};
};

class ParameterQueue final : public sv::IParamValueQueue {
public:
    explicit ParameterQueue(sv::ParamID parameter_id = 0) : id(parameter_id) {}

    sv::ParamID id{0};
    std::vector<ParameterPoint> points{};
    std::optional<Steinberg::int32> count_override{};
    Steinberg::int32 fail_index{-1};

    Steinberg::tresult PLUGIN_API queryInterface(const Steinberg::TUID requested_id, void** object) override;
    Steinberg::uint32 PLUGIN_API addRef() override { return 1; }
    Steinberg::uint32 PLUGIN_API release() override { return 1; }
    sv::ParamID PLUGIN_API getParameterId() override { return id; }
    Steinberg::int32 PLUGIN_API getPointCount() override;
    Steinberg::tresult PLUGIN_API getPoint(Steinberg::int32 index, Steinberg::int32& offset,
                                          sv::ParamValue& value) override;
    Steinberg::tresult PLUGIN_API addPoint(Steinberg::int32 offset, sv::ParamValue value,
                                          Steinberg::int32& index) override;
};

class ParameterChanges final : public sv::IParameterChanges {
public:
    std::vector<std::unique_ptr<ParameterQueue>> queues{};
    std::optional<Steinberg::int32> count_override{};
    Steinberg::int32 null_index{-1};

    // Always appends, deliberately permitting duplicate-ID adversarial cases.
    ParameterQueue& add_queue(sv::ParamID id);
    Steinberg::tresult PLUGIN_API queryInterface(const Steinberg::TUID requested_id, void** object) override;
    Steinberg::uint32 PLUGIN_API addRef() override { return 1; }
    Steinberg::uint32 PLUGIN_API release() override { return 1; }
    Steinberg::int32 PLUGIN_API getParameterCount() override;
    sv::IParamValueQueue* PLUGIN_API getParameterData(Steinberg::int32 index) override;
    sv::IParamValueQueue* PLUGIN_API addParameterData(const sv::ParamID& id,
                                                    Steinberg::int32& index) override;
};

class StereoBlock {
public:
    explicit StereoBlock(std::size_t capacity);
    StereoBlock(const StereoBlock&) = delete;
    StereoBlock& operator=(const StereoBlock&) = delete;
    StereoBlock(StereoBlock&&) = delete;
    StereoBlock& operator=(StereoBlock&&) = delete;

    // These methods are fixture setup, never part of the plugin allocation probe.
    void set_frames(Steinberg::int32 frames);
    void fill(float value);
    std::vector<float> left;
    std::vector<float> right;
    std::array<float*, 2> channels{};
    sv::AudioBusBuffers bus{};
    sv::ProcessData data{};
};

class NativePlugin {
private:
    // Declaration order ensures interfaces are released before their host and
    // native module, even on construction failure. No module is unloaded while
    // an interface implemented in it is still owned.
    VST3::Hosting::Module::Ptr module_{};
    Steinberg::IPtr<sv::HostApplication> host_{};
    bool component_initialized_{false};
    bool controller_initialized_{false};
    bool active_{false};
    bool processing_{false};
    void shutdown() noexcept;

public:
    explicit NativePlugin(const std::string& bundle_path);
    ~NativePlugin();
    NativePlugin(const NativePlugin&) = delete;
    NativePlugin& operator=(const NativePlugin&) = delete;
    NativePlugin(NativePlugin&&) = delete;
    NativePlugin& operator=(NativePlugin&&) = delete;

    Steinberg::IPtr<sv::IComponent> component{};
    Steinberg::IPtr<sv::IAudioProcessor> processor{};
    Steinberg::IPtr<sv::IEditController> controller{};

    [[nodiscard]] const VST3::Hosting::Module& module() const noexcept { return *module_; }
    void configure(double sample_rate, Steinberg::int32 maximum,
                   Steinberg::int32 mode = sv::kRealtime);
    void activate();
    void begin_processing();
    void stop_processing();
    void deactivate();
    void start(double sample_rate, Steinberg::int32 maximum,
               Steinberg::int32 mode = sv::kRealtime);
    [[nodiscard]] Steinberg::tresult load_state(std::string_view bytes);
    [[nodiscard]] Steinberg::tresult save_state(std::string& bytes);
};

[[nodiscard]] sv::Event note_on(Steinberg::int32 bus, Steinberg::int16 pitch,
                                 Steinberg::int32 offset = 0,
                                 Steinberg::int16 channel = 0,
                                 Steinberg::int32 note_id = -1,
                                 float velocity = 1.0F);
[[nodiscard]] sv::Event note_off(Steinberg::int32 bus, Steinberg::int16 pitch,
                                  Steinberg::int32 offset = 0,
                                  Steinberg::int16 channel = 0,
                                  Steinberg::int32 note_id = -1);

} // namespace hammond::native_test
