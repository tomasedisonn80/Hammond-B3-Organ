#pragma once

#include "hammond/HostTimeline.h"
#include "hammond/StateExchange.h"
#include "public.sdk/source/vst/vstaudioeffect.h"

#include <array>
#include <cstddef>
#include <cstdint>
#include <string_view>

namespace hammond::vst3 {

inline constexpr std::string_view kNativeProcessorModelId =
    "nominal-vst3-processor-v1";
inline constexpr std::string_view kNativePedalMappingId =
    "vst3-pedal-midi36-v1";
inline constexpr std::string_view kNativeEventFilterId =
    "vst3-valid-unsupported-and-pitch-filter-v1";
inline constexpr std::uint64_t kNativeInitialSeed = 0;

// Last successful callback only. A rejected callback preserves this report.
// These copied diagnostics and timeline_for_testing() belong to the sole audio
// owner or a genuinely quiescent test; neither is a concurrent UI interface.
struct NativeProcessDiagnostics {
    std::uint32_t frames{0};
    std::uint32_t raw_parameter_points{0};
    std::uint32_t raw_events{0};
    std::uint32_t translated_notes{0};
    std::uint32_t filtered_unsupported_events{0};
    std::uint32_t filtered_pitch_events{0};
    std::uint32_t ignored_note_tuning{0};
    bool connected_output{false};
    bool rendered_silence{true};
    HostTimelineResult timeline{};
};

// Native SDK boundary only: all instrument DSP, ownership and curve semantics
// remain in the SDK-independent core. Construct/destroy this large fixed-storage
// object outside audio. The host must serialize lifecycle changes and establish
// actual processing quiescence; the lifecycle Booleans are not synchronization.
class Processor final : public Steinberg::Vst::AudioEffect {
public:
    Processor();
    static Steinberg::FUnknown* createInstance(void* context);

    Steinberg::tresult PLUGIN_API initialize(Steinberg::FUnknown* context) override;
    Steinberg::tresult PLUGIN_API terminate() override;
    Steinberg::tresult PLUGIN_API setActive(Steinberg::TBool state) override;
    Steinberg::tresult PLUGIN_API activateBus(
        Steinberg::Vst::MediaType type, Steinberg::Vst::BusDirection direction,
        Steinberg::int32 index, Steinberg::TBool state) override;
    Steinberg::tresult PLUGIN_API getRoutingInfo(
        Steinberg::Vst::RoutingInfo& input,
        Steinberg::Vst::RoutingInfo& output) override;
    Steinberg::tresult PLUGIN_API setBusArrangements(
        Steinberg::Vst::SpeakerArrangement* inputs, Steinberg::int32 input_count,
        Steinberg::Vst::SpeakerArrangement* outputs,
        Steinberg::int32 output_count) override;
    Steinberg::tresult PLUGIN_API canProcessSampleSize(
        Steinberg::int32 symbolic_sample_size) override;
    Steinberg::tresult PLUGIN_API setupProcessing(
        Steinberg::Vst::ProcessSetup& setup) override;
    Steinberg::tresult PLUGIN_API setProcessing(Steinberg::TBool state) override;
    Steinberg::tresult PLUGIN_API process(Steinberg::Vst::ProcessData& data) override;
    Steinberg::uint32 PLUGIN_API getTailSamples() override;

    // Serialized host UI/main thread, including while process() is active.
    // Parsing/serialization uses copied state and never accesses live Engine.
    Steinberg::tresult PLUGIN_API setState(Steinberg::IBStream* state) override;
    Steinberg::tresult PLUGIN_API getState(Steinberg::IBStream* state) override;

    [[nodiscard]] NativeProcessDiagnostics last_process_diagnostics() const noexcept {
        return last_process_;
    }
    [[nodiscard]] const HostTimeline& timeline_for_testing() const noexcept {
        return timeline_;
    }

private:
    struct OutputView {
        Steinberg::Vst::AudioBusBuffers* bus{nullptr};
        float* left{nullptr};
        float* right{nullptr};
        bool write_samples{false};
        bool write_flags{false};
    };

    [[nodiscard]] bool admit_output(Steinberg::Vst::ProcessData& data,
                                    OutputView& output) noexcept;
    [[nodiscard]] bool admit_input(Steinberg::Vst::ProcessData& data,
                                   NativeProcessDiagnostics& report,
                                   std::size_t& queue_count,
                                   std::size_t& musical_count) noexcept;

    RuntimeProfile profile_{};
    HostTimeline timeline_{};
    StateExchange state_exchange_{};
    std::array<HostParameterPoint, kMaxEventsPerBlock> points_{};
    std::array<HostParameterQueue, kParameterCount> queues_{};
    std::array<HostMusicalEvent, kMaxEventsPerBlock> musical_{};
    std::array<float, kHardMaxBlockFrames> mono_{};
    NativeProcessDiagnostics last_process_{};
    bool initialized_{false};
    bool profile_loaded_{false};
    bool prepared_{false};
    bool active_{false};
    bool processing_{false};
};

} // namespace hammond::vst3
