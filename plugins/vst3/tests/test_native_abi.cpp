#include "NativeHarness.h"
#include "NativePresetOracle.h"

#include "hammond/ConsoleModel.h"
#include "hammond/Engine.h"
#include "hammond/ParameterBridge.h"
#include "hammond/Profile.h"
#include "pluginterfaces/gui/iplugview.h"
#include "pluginterfaces/vst/ivstunits.h"

#include <algorithm>
#include <array>
#include <bit>
#include <cmath>
#include <cstring>
#include <filesystem>
#include <iomanip>
#include <iostream>
#include <limits>
#include <string>
#include <vector>

namespace {

using namespace hammond;
using namespace hammond::native_test;
namespace sv = Steinberg::Vst;

struct Counts {
    std::uint64_t assertions{0};
    std::uint64_t instances{0};
    std::uint64_t descriptors{0};
    std::uint64_t conversions{0};
    std::uint64_t accepted_callbacks{0};
    std::uint64_t rejected_calls{0};
    std::uint64_t state_round_trips{0};
    std::uint64_t lifecycle_sequences{0};
    std::uint64_t compared_frames{0};
    std::uint64_t audible_frames{0};
    std::uint64_t float_hash{14695981039346656037ULL};
    double maximum_audio_error{0.0};
} counts;

void check(bool value, std::string_view message) {
    ++counts.assertions;
    require(value, message);
}

void reject(Steinberg::tresult result, std::string_view message) {
    check(result != Steinberg::kResultOk, message);
    ++counts.rejected_calls;
}

void accepted(NativePlugin& plugin, StereoBlock& block) {
    require_ok(plugin.processor->process(block.data), "native process");
    ++counts.accepted_callbacks;
}

void factory_and_parameters(const std::string& bundle) {
    NativePlugin plugin(bundle);
    ++counts.instances;
    const auto& module = plugin.module();
    std::string error;
    check(module.isBundle(), "module loader did not recognize the bundle");
    check(VST3::Hosting::Module::validateBundleStructure(bundle, error),
          "invalid native bundle structure: " + error);
    const auto& factory = module.getFactory();
    check(factory.classCount() == 2, "factory class count differs from the frozen pair");
    const auto classes = factory.classInfos();
    check(classes.size() == 2, "factory metadata class count differs");
    unsigned processors = 0;
    unsigned controllers = 0;
    for (const auto& item : classes) {
        if (std::memcmp(item.ID().data(), expected_processor_id().toTUID(), 16) == 0) {
            ++processors;
            check(item.category() == kVstAudioEffectClass, "processor has wrong native category");
            check(item.name() == "Hammond B3 Nominal", "unexpected processor class name");
            check(item.subCategoriesString() == "Instrument|Synth", "wrong instrument category");
            check(item.classFlags() == sv::kDistributable, "wrong processor class flags");
        } else if (std::memcmp(item.ID().data(), expected_controller_id().toTUID(), 16) == 0) {
            ++controllers;
            check(item.category() == kVstComponentControllerClass, "controller has wrong category");
        } else {
            check(false, "factory exported an unexpected class UUID");
        }
        check(item.version() == "0.1.0", "native class version changed");
        check(item.cardinality() == Steinberg::PClassInfo::kManyInstances,
              "native class cardinality differs");
    }
    check(processors == 1 && controllers == 1, "native class pair is not unique");
    Steinberg::TUID controller_id{};
    require_ok(plugin.component->getControllerClassId(controller_id), "getControllerClassId");
    check(std::memcmp(controller_id, expected_controller_id().toTUID(), 16) == 0,
          "component advertises the wrong controller UUID");
    check(plugin.controller->createView(sv::ViewType::kEditor) == nullptr,
          "the nominal generic controller unexpectedly requires a custom view");
    void* unexpected = nullptr;
    reject(plugin.component->queryInterface(sv::IEditController::iid.toTUID(), &unexpected),
           "processor unexpectedly exports the separate controller interface");
    check(unexpected == nullptr, "failed interface query did not clear output");
    const auto unknown = Steinberg::FUID(0x77777777, 0x22222222, 0x33333333, 0x44444444);
    reject(factory.get()->createInstance(unknown.toTUID(), sv::IComponent::iid.toTUID(), &unexpected),
           "factory accepted an unknown class identity");
    check(unexpected == nullptr, "failed factory creation did not clear output");

    const auto descriptors = parameter_descriptors();
    check(descriptors.size() == 47 && plugin.controller->getParameterCount() == 47,
          "native controller does not export exactly 47 controls");
    for (std::size_t index = 0; index < descriptors.size(); ++index) {
        const auto& expected = descriptors[index];
        sv::ParameterInfo info{};
        require_ok(plugin.controller->getParameterInfo(static_cast<Steinberg::int32>(index), info),
                   "getParameterInfo");
        ++counts.descriptors;
        check(info.id == expected.id, "native parameter identity/order changed");
        check(ascii(info.title) == expected.path && ascii(info.shortTitle) == expected.path,
              "native parameter title differs from the frozen path");
        check(ascii(info.units) == expected.unit, "native parameter units changed");
        check(info.stepCount == static_cast<Steinberg::int32>(expected.step_count),
              "native parameter discrete cardinality changed");
        check(info.flags == sv::ParameterInfo::kCanAutomate && info.unitId == sv::kRootUnitId,
              "native parameter flags/unit changed");
        double default_normalized = -1.0;
        check(plain_to_normalized(expected.id, expected.default_plain, default_normalized),
              "compiled descriptor default is invalid");
        check(info.defaultNormalizedValue == default_normalized &&
              plugin.controller->getParamNormalized(expected.id) == default_normalized,
              "native default differs from the registry");

        const auto steps = expected.step_count;
        if (steps != 0) {
            for (std::uint32_t position = 0; position <= steps; ++position) {
                const double plain = static_cast<double>(position);
                const double normalized = steps == 11 ? preset_oracle::canonical[position]
                    : plain / static_cast<double>(steps);
                check(plugin.controller->plainParamToNormalized(expected.id, plain) == normalized,
                      "native plain-to-normalized conversion changed");
                check(plugin.controller->normalizedParamToPlain(expected.id, normalized) == plain,
                      "native normalized-to-plain conversion changed");
                counts.conversions += 2;
                sv::String128 text{};
                require_ok(plugin.controller->getParamStringByValue(expected.id, normalized, text),
                           "format discrete native value");
                double parsed = -99.0;
                require_ok(plugin.controller->getParamValueByString(expected.id, text, parsed),
                           "parse discrete native value");
                check(parsed == normalized, "native formatted value does not round-trip");
                ++counts.conversions;
            }
            for (std::uint32_t lower = 0; lower < steps; ++lower) {
                const double boundary = steps == 11 ? preset_oracle::thresholds[lower]
                    : (static_cast<double>(lower) + 0.5) / static_cast<double>(steps);
                for (const auto value : {std::nextafter(boundary, 0.0), boundary,
                                         std::nextafter(boundary, 1.0)}) {
                    const double plain = value < boundary ? static_cast<double>(lower)
                        : static_cast<double>(lower + 1);
                    check(plugin.controller->normalizedParamToPlain(expected.id, value) == plain,
                          "native discrete threshold differs at an adjacent binary64 value");
                    ++counts.conversions;
                }
            }
        } else {
            for (const double value : {0.0, 0.125, 0.5, 0.875, 1.0}) {
                check(plugin.controller->normalizedParamToPlain(expected.id, value) == value &&
                      plugin.controller->plainParamToNormalized(expected.id, value) == value,
                      "native expression conversion changed");
                counts.conversions += 2;
            }
        }
        require_ok(plugin.controller->setParamNormalized(expected.id, 0.375), "set native control");
        check(plugin.controller->getParamNormalized(expected.id) == 0.375,
              "native controller lost a supplied normalized value");
        reject(plugin.controller->setParamNormalized(expected.id,
            std::numeric_limits<double>::quiet_NaN()), "native controller accepted NaN");
        check(plugin.controller->getParamNormalized(expected.id) == 0.375,
              "failed native set changed a control");
    }
    sv::ParameterInfo sentinel{};
    sentinel.id = 0xabcdefU;
    reject(plugin.controller->getParameterInfo(-1, sentinel), "negative parameter index accepted");
    reject(plugin.controller->getParameterInfo(47, sentinel), "out-of-range parameter index accepted");
    check(sentinel.id == 0xabcdefU, "failed parameter query changed destination");
    reject(plugin.controller->setParamNormalized(0xffffffffU, 0.5), "unknown parameter accepted");
}

void buses_and_lifecycle(const std::string& bundle) {
    NativePlugin plugin(bundle);
    ++counts.instances;
    check(plugin.component->getBusCount(sv::kAudio, sv::kInput) == 0, "audio input advertised");
    check(plugin.component->getBusCount(sv::kAudio, sv::kOutput) == 1, "wrong audio output count");
    check(plugin.component->getBusCount(sv::kEvent, sv::kInput) == 3, "wrong native event bus count");
    check(plugin.component->getBusCount(sv::kEvent, sv::kOutput) == 0, "event output advertised");
    const std::array<std::string_view, 3> names{"Upper", "Lower", "Pedals"};
    for (Steinberg::int32 index = 0; index < 3; ++index) {
        sv::BusInfo info{};
        require_ok(plugin.component->getBusInfo(sv::kEvent, sv::kInput, index, info), "event bus info");
        check(info.channelCount == 16 && ascii(info.name) == names[static_cast<std::size_t>(index)],
              "native event bus name/channel count changed");
        check(info.busType == (index == 0 ? sv::kMain : sv::kAux) &&
              (info.flags & sv::BusInfo::kDefaultActive) != 0, "native bus role/activation changed");
        for (const Steinberg::int32 channel : {-1, 0, 15}) {
            sv::RoutingInfo input{sv::kEvent, index, channel};
            sv::RoutingInfo output{-5, -5, -5};
            require_ok(plugin.component->getRoutingInfo(input, output), "native routing info");
            check(output.mediaType == sv::kAudio && output.busIndex == 0 && output.channel == -1,
                  "event bus does not route to dry stereo");
        }
    }
    sv::BusInfo output{};
    require_ok(plugin.component->getBusInfo(sv::kAudio, sv::kOutput, 0, output), "audio bus info");
    check(output.channelCount == 2 && ascii(output.name) == "Dry stereo", "wrong stereo output");
    sv::SpeakerArrangement arrangement{};
    require_ok(plugin.processor->getBusArrangement(sv::kOutput, 0, arrangement), "bus arrangement");
    check(arrangement == sv::SpeakerArr::kStereo, "output is not stereo");
    auto mono = sv::SpeakerArr::kMono;
    reject(plugin.processor->setBusArrangements(nullptr, 0, &mono, 1), "mono arrangement accepted");
    auto stereo = sv::SpeakerArr::kStereo;
    require_ok(plugin.processor->setBusArrangements(nullptr, 0, &stereo, 1), "stereo arrangement");
    require_ok(plugin.processor->canProcessSampleSize(sv::kSample32), "float32 support");
    reject(plugin.processor->canProcessSampleSize(sv::kSample64), "float64 advertised");
    reject(plugin.processor->canProcessSampleSize(17), "unknown precision advertised");

    // Separate real factory instances allow explicit, checked termination and
    // reinitialization. Their interfaces are released before the enclosing
    // module/host holder, including after rejected unsupported-format setup.
    for (const double rate : {44100.0, 48000.0, 96000.0}) {
        auto host = Steinberg::owned(new sv::HostApplication());
        auto component = plugin.module().getFactory().createInstance<sv::IComponent>(
            VST3::UID(expected_processor_id().toTUID()));
        check(component.get() != nullptr, "second native instance creation failed");
        ++counts.instances;
        Steinberg::FUnknownPtr<sv::IAudioProcessor> processor(component.get());
        check(processor.get() != nullptr, "second component processor interface missing");
        require_ok(component->initialize(host.get()), "lifecycle initialize");
        sv::ProcessSetup unsupported{sv::kRealtime, sv::kSample64, 512, rate};
        reject(processor->setupProcessing(unsupported), "unsupported setup accepted");
        reject(component->setActive(true), "failed setup left an activatable instance");
        reject(component->setActive(false), "identical inactive state unexpectedly accepted");
        for (unsigned epoch = 0; epoch < 2; ++epoch) {
            sv::ProcessSetup setup{sv::kRealtime, sv::kSample32, 65536, rate};
            require_ok(processor->setupProcessing(setup), "supported lifecycle setup");
            for (Steinberg::int32 bus = 0; bus < 3; ++bus) {
                require_ok(component->activateBus(sv::kEvent, sv::kInput, bus, true), "lifecycle event bus");
            }
            require_ok(component->activateBus(sv::kAudio, sv::kOutput, 0, true), "lifecycle output bus");
            require_ok(component->setActive(true), "lifecycle activate");
            reject(component->setActive(true), "identical active state unexpectedly accepted");
            require_ok(processor->setProcessing(true), "lifecycle processing start");
            require_ok(processor->setProcessing(true), "repeated processing start");
            StereoBlock block(1);
            require_ok(processor->process(block.data), "lifecycle audio block");
            ++counts.accepted_callbacks;
            check(block.left[0] == 0.0F && block.right[0] == 0.0F, "fresh defaults are not muted");
            reject(component->setActive(false), "active processing was deactivated without stopping");
            require_ok(processor->setProcessing(false), "lifecycle processing stop");
            require_ok(component->setActive(false), "lifecycle deactivate");
            require_ok(component->terminate(), "balanced lifecycle terminate");
            reject(component->terminate(), "repeated terminate unexpectedly accepted");
            ++counts.lifecycle_sequences;
            if (epoch == 0) require_ok(component->initialize(host.get()), "same-instance reinitialize");
        }
    }
}

constexpr std::string_view kLegacyManuals =
    "manual upper selected B route_enabled 0\n"
    "bank A 8 0 0 2 0 0 0 0 0\n"
    "bank B 0 1 2 3 4 5 6 7 8\n"
    "manual lower selected A route_enabled 1\n"
    "bank A 8 7 6 5 4 3 2 1 0\n"
    "bank B 0 0 0 0 0 4 0 0 0\n"
    "end\n";

ControlSnapshot expected_state(unsigned version) {
    ControlSnapshot state{};
    state.expression = 0.375;
    state.selected_banks = {DrawbarBank::B, DrawbarBank::A};
    state.route_enabled = {false, true};
    state.drawbars[0][0] = {8, 0, 0, 2, 0, 0, 0, 0, 0};
    state.drawbars[0][1] = {0, 1, 2, 3, 4, 5, 6, 7, 8};
    state.drawbars[1][0] = {8, 7, 6, 5, 4, 3, 2, 1, 0};
    state.drawbars[1][1] = {0, 0, 0, 0, 0, 4, 0, 0, 0};
    if (version >= 2) state.percussion = {true, PercussionHarmonic::Third,
        PercussionVolume::Soft, PercussionDecay::Fast};
    if (version == 3) state.pedal_drawbars = {2, 7};
    return state;
}

std::string old_state(unsigned version) {
    std::string bytes = "B3CONTROLS" + std::to_string(version) + "\nexpression 0.375\n";
    if (version >= 2) bytes += "percussion enabled 1 harmonic third volume soft decay fast\n";
    if (version == 3) bytes += "pedal drawbars 2 7\n";
    bytes += kLegacyManuals;
    return bytes;
}

std::string expected_state4(unsigned version) {
    std::string bytes =
        "B3CONTROLS4\nregistration_catalog atlas-chapel-nominal-v1 sha256 "
        "c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf\n"
        "expression 0.375\n";
    bytes += version == 1 ? "percussion enabled 0 harmonic second volume normal decay slow\n" :
                            "percussion enabled 1 harmonic third volume soft decay fast\n";
    bytes += version < 3 ? "pedal drawbars 0 0\n" : "pedal drawbars 2 7\n";
    bytes +=
        "manual upper selected B fixed_registration none route_enabled 0\n"
        "bank A 8 0 0 2 0 0 0 0 0\nbank B 0 1 2 3 4 5 6 7 8\n"
        "manual lower selected A fixed_registration none route_enabled 1\n"
        "bank A 8 7 6 5 4 3 2 1 0\nbank B 0 0 0 0 0 4 0 0 0\nend\n";
    return bytes;
}

void native_state(const std::string& bundle) {
    NativePlugin plugin(bundle);
    ++counts.instances;
    plugin.start(48000.0, 512);
    StereoBlock block(512);
    block.set_frames(0);
    for (const unsigned version : {1U, 2U, 3U}) {
        const auto bytes = old_state(version);
        const auto expected = expected_state(version);
        MemoryStream input(bytes);
        input.read_chunk = 7;
        input.false_at_eof = true;
        require_ok(plugin.component->setState(&input), "active native legacy state load");
        MemoryStream saved;
        saved.write_chunk = 13;
        require_ok(plugin.component->getState(&saved), "pending native state save");
        check(saved.bytes.starts_with("B3CONTROLS4\n"), "native writer emitted a historical grammar");
        check(saved.bytes == expected_state4(version), "legacy state did not save exact independent state4 bytes");
        check(parse_snapshot(saved.bytes) == expected, "pending state/migration/route bits changed");
        check(input.read_calls > 1 && saved.write_calls > 1, "partial native stream fixture was vacuous");
        ++counts.state_round_trips;
        MemoryStream controller_input(bytes);
        require_ok(plugin.controller->setComponentState(&controller_input), "native controller component state");
        check(plugin.controller->getParamNormalized(0x4000) ==
              static_cast<double>(expected.pedal_drawbars[0]) / 8.0 &&
              plugin.controller->getParamNormalized(0x4001) ==
              static_cast<double>(expected.pedal_drawbars[1]) / 8.0,
              "native controller migration did not reflect pedal values");
        accepted(plugin, block);
        std::string committed;
        require_ok(plugin.save_state(committed), "acknowledged native state save");
        check(parse_snapshot(committed) == expected, "zero-frame acknowledgement changed saved controls");
        check(parse_snapshot(committed).route_enabled == expected.route_enabled,
              "absent parameter queues reconnected a cancelled route");
        check(committed == expected_state4(version), "acknowledged migration changed canonical bytes");
        ++counts.state_round_trips;
        reject(plugin.load_state("B3CONTROLS99\nend\n"), "future state grammar accepted");
        std::string after_invalid;
        require_ok(plugin.save_state(after_invalid), "save after rejected state");
        check(after_invalid == committed, "invalid native state replaced controls");
    }
    // Exercise the native pending and decoded publication paths, including raw
    // fixed memory behind Cancel, for every valid fixed/bank/route combination.
    for (unsigned upper = 0; upper < 10; ++upper) {
        for (unsigned lower = 0; lower < 10; ++lower) {
            for (unsigned mask = 0; mask < 16; ++mask) {
                auto state = expected_state(3);
                state.fixed_registrations = {static_cast<FixedRegistration>(upper),
                                             static_cast<FixedRegistration>(lower)};
                state.selected_banks = {(mask & 1U) != 0 ? DrawbarBank::B : DrawbarBank::A,
                                       (mask & 2U) != 0 ? DrawbarBank::B : DrawbarBank::A};
                state.route_enabled = {(mask & 4U) != 0, (mask & 8U) != 0};
                const auto canonical = snapshot_text(state);
                require_ok(plugin.load_state(canonical), "native state4 fixed-mode load");
                std::string pending;
                require_ok(plugin.save_state(pending), "native state4 pending save");
                check(pending == canonical, "pending fixed memory changed");
                ++counts.state_round_trips;
                accepted(plugin, block);
                std::string acknowledged;
                require_ok(plugin.save_state(acknowledged), "native state4 acknowledged save");
                check(acknowledged == canonical, "decoded fixed publication changed");
                ++counts.state_round_trips;
                MemoryStream controller_input(canonical);
                require_ok(plugin.controller->setComponentState(&controller_input), "native selector restore");
                for (std::size_t manual = 0; manual < 2; ++manual) {
                    const auto fixed = static_cast<std::size_t>(state.fixed_registrations[manual]);
                    const auto selection = !state.route_enabled[manual] ? 0U : fixed != 0 ? fixed :
                        state.selected_banks[manual] == DrawbarBank::A ? 10U : 11U;
                    check(plugin.controller->getParamNormalized(manual == 0 ? 0x5000U : 0x5001U) ==
                              preset_oracle::canonical[selection], "effective native selector restore changed");
                    check(plugin.controller->getParamNormalized(manual == 0 ? 0x2010U : 0x2011U) ==
                              static_cast<double>(state.selected_banks[manual]), "retained native bank changed");
                }
            }
        }
    }
    for (unsigned index = 0; index < 4; ++index) {
        auto state = expected_state(3);
        state.expression = static_cast<double>(index) / 4.0;
        require_ok(plugin.load_state(snapshot_text(state)), "fill native state queue");
    }
    reject(plugin.load_state(snapshot_text(ControlSnapshot{})), "fifth native pending load accepted");
    std::string before;
    require_ok(plugin.save_state(before), "save full pending queue");
    check(parse_snapshot(before).expression == 0.75, "full queue lost newest accepted load");
    accepted(plugin, block);
    std::string after;
    require_ok(plugin.save_state(after), "save retired native queue");
    check(after == before, "native queue acknowledgement altered controls");
    ++counts.state_round_trips;
    reject(plugin.component->getState(nullptr), "null native save stream accepted");
    reject(plugin.component->setState(nullptr), "null native load stream accepted");
    plugin.stop_processing();
    plugin.deactivate();
}

void compare_audio(NativePlugin& plugin, StereoBlock& block, Engine& reference,
                   std::span<const Event> physical, std::vector<float>& expected) {
    const auto frames = static_cast<std::size_t>(block.data.numSamples);
    block.fill(-99.0F);
    accepted(plugin, block);
    require(reference.process(static_cast<std::uint32_t>(frames),
        std::span<float>{expected}.first(frames), physical).ok(), "plain Engine reference rejected");
    bool silent = true;
    for (std::size_t index = 0; index < frames; ++index) {
        const auto actual = block.left[index];
        check(std::isfinite(actual), "native output is nonfinite");
        counts.maximum_audio_error = std::max(counts.maximum_audio_error,
            std::abs(static_cast<double>(actual) - static_cast<double>(expected[index])));
        check(std::bit_cast<std::uint32_t>(actual) == std::bit_cast<std::uint32_t>(expected[index]),
              "native output differs from plain Engine for identical physical events");
        check(std::bit_cast<std::uint32_t>(actual) == std::bit_cast<std::uint32_t>(block.right[index]),
              "native dry stereo channels differ");
        auto bits = std::bit_cast<std::uint32_t>(actual);
        for (unsigned byte = 0; byte < 4; ++byte) {
            counts.float_hash ^= bits & 0xffU;
            counts.float_hash *= 1099511628211ULL;
            bits >>= 8;
        }
        if (actual != 0.0F) {
            silent = false;
            ++counts.audible_frames;
        }
    }
    counts.compared_frames += frames;
    check(block.bus.silenceFlags == (silent ? 3U : 0U), "native silence flags disagree with output");
    if (frames < block.left.size()) {
        check(block.left[frames] == -99.0F && block.right[frames] == -99.0F,
              "native process wrote beyond its actual sample count");
    }
}

void audible_native(const std::string& bundle, const RuntimeProfile& profile) {
    for (const double rate : {44100.0, 48000.0, 96000.0}) {
        NativePlugin plugin(bundle);
        ++counts.instances;
        plugin.start(rate, 65536);
        Engine reference;
        require(reference.prepare(profile, ProcessSpec{rate, 65536, 0, 0},
                                  make_nominal_console_model()) == Status::Ok,
                "plain Engine preparation failed");
        StereoBlock block(65536);
        std::vector<float> expected(65536);
        for (const Steinberg::int32 frames : {0, 1, 127}) {
            block.set_frames(frames);
            compare_audio(plugin, block, reference, {}, expected);
        }
        ControlSnapshot registration{};
        registration.selected_banks = {DrawbarBank::A, DrawbarBank::A};
        registration.drawbars[0][0][2] = 8;
        registration.drawbars[1][0][3] = 6;
        registration.pedal_drawbars = {3, 2};
        registration.expression = 0.625;
        require_ok(plugin.load_state(snapshot_text(registration)), "audible native registration");
        require(reference.restore_controls(registration), "reference registration restore failed");

        // Literal native bus/pitch boundary examples independently specify the
        // expected physical endpoints; no production native translator is used.
        EventList notes;
        notes.events = {note_on(0, 36, 0, 0, 100), note_on(1, 96, 0, 15, 101),
                        note_on(2, 60, 0, 7, 102)};
        const std::array<Event, 3> on{{
            {0, EventType::NoteOn, Manual::Upper, 36, 127.0},
            {0, EventType::NoteOn, Manual::Lower, 96, 127.0},
            {0, EventType::PedalOn, Manual::Lower, 25, 127.0}}};
        block.data.inputEvents = &notes;
        block.set_frames(0);
        compare_audio(plugin, block, reference, on, expected);
        block.data.inputEvents = nullptr;
        for (const Steinberg::int32 frames : {1, 31, 1024, 65536}) {
            block.set_frames(frames);
            compare_audio(plugin, block, reference, {}, expected);
        }
        check(std::any_of(block.left.begin(), block.left.end(), [](float x) { return x != 0.0F; }),
              "native audible fixture was silent");

        notes.events = {note_off(0, 36, 0, 0, 100), note_off(1, 96, 0, 15, 101),
                        note_off(2, 60, 0, 7, 102)};
        const std::array<Event, 3> off{{
            {0, EventType::NoteOff, Manual::Upper, 36, 0.0},
            {0, EventType::NoteOff, Manual::Lower, 96, 0.0},
            {0, EventType::PedalOff, Manual::Lower, 25, 0.0}}};
        block.data.inputEvents = &notes;
        block.set_frames(1024);
        compare_audio(plugin, block, reference, off, expected);
        notes.events.clear();

        // All sixteen channels retain distinct owners on every native input.
        for (Steinberg::int16 channel = 0; channel < 16; ++channel) {
            for (Steinberg::int32 bus = 0; bus < 3; ++bus) {
                notes.events.push_back(note_on(bus, 48, 0, channel, bus * 16 + channel));
            }
        }
        const std::array<Event, 3> owned_on{{
            {0, EventType::NoteOn, Manual::Upper, 48, 127.0},
            {0, EventType::NoteOn, Manual::Lower, 48, 127.0},
            {0, EventType::PedalOn, Manual::Lower, 13, 127.0}}};
        block.set_frames(512);
        compare_audio(plugin, block, reference, owned_on, expected);
        notes.events.clear();
        for (Steinberg::int16 channel = 0; channel < 15; ++channel) {
            for (Steinberg::int32 bus = 0; bus < 3; ++bus) {
                notes.events.push_back(note_off(bus, 48, 0, channel, bus * 16 + channel));
            }
        }
        compare_audio(plugin, block, reference, {}, expected);
        notes.events = {note_off(0, 48, 0, 15, 15), note_off(1, 48, 0, 15, 31),
                        note_off(2, 48, 0, 15, 47)};
        const std::array<Event, 3> owned_off{{
            {0, EventType::NoteOff, Manual::Upper, 48, 0.0},
            {0, EventType::NoteOff, Manual::Lower, 48, 0.0},
            {0, EventType::PedalOff, Manual::Lower, 13, 0.0}}};
        compare_audio(plugin, block, reference, owned_off, expected);
        block.data.inputEvents = nullptr;

        // Independently audible divisions prevent a muted manual registration
        // or an aggregate manual/pedal sum from making routing checks vacuous.
        block.set_frames(1024);
        compare_audio(plugin, block, reference, {}, expected);
        check(std::all_of(block.left.begin() + 768, block.left.begin() + 1024,
                          [](float value) { return value == 0.0F; }),
              "released divisions did not settle before isolated voice probes");
        for (Steinberg::int32 division = 0; division < 3; ++division) {
            notes.events = {note_on(division, 48, 0, 4, 900 + division)};
            block.data.inputEvents = &notes;
            const std::array<Event, 1> isolated_on{{
                {0, division == 2 ? EventType::PedalOn : EventType::NoteOn,
                 division == 0 ? Manual::Upper : Manual::Lower,
                 static_cast<std::uint8_t>(division == 2 ? 13 : 48), 127.0}}};
            compare_audio(plugin, block, reference, isolated_on, expected);
            check(std::any_of(block.left.begin(), block.left.begin() + 1024,
                              [](float value) { return value != 0.0F; }),
                  "an isolated native division was silent");
            notes.events = {note_off(division, 48, 0, 4, 900 + division)};
            const std::array<Event, 1> isolated_off{{
                {0, division == 2 ? EventType::PedalOff : EventType::NoteOff,
                 division == 0 ? Manual::Upper : Manual::Lower,
                 static_cast<std::uint8_t>(division == 2 ? 13 : 48), 0.0}}};
            compare_audio(plugin, block, reference, isolated_off, expected);
        }
        block.data.inputEvents = nullptr;

        // An omitted native output still advances the one shared source clock.
        block.set_frames(127);
        block.data.numOutputs = 0;
        block.data.outputs = nullptr;
        block.fill(-99.0F);
        accepted(plugin, block);
        require(reference.process(127, {}, {}).ok(), "disconnected reference rejected");
        check(block.left[0] == -99.0F && block.right[0] == -99.0F,
              "disconnected native processing touched audio storage");
        block.data.numOutputs = 1;
        block.data.outputs = &block.bus;
        notes.events = {note_on(2, 36, 0, 3, 800)};
        block.data.inputEvents = &notes;
        const std::array<Event, 1> after_disconnect{{
            {0, EventType::PedalOn, Manual::Lower, 1, 127.0}}};
        compare_audio(plugin, block, reference, after_disconnect, expected);
        check(std::any_of(block.left.begin(), block.left.begin() + 127,
                          [](float value) { return value != 0.0F; }),
              "disconnected phase-history probe was silent");
        plugin.stop_processing();
        plugin.deactivate();
    }
}

} // namespace

int main(int argc, char** argv) {
    try {
        require(argc == 3, "usage: test_native_abi BUNDLE COMPILED_PROFILE");
        RuntimeProfile profile{};
        std::string error;
        require(load_runtime_profile_file(std::filesystem::path(argv[2]), profile, error),
                "test profile could not be loaded: " + error);
        const std::string bundle(argv[1]);
        factory_and_parameters(bundle);
        buses_and_lifecycle(bundle);
        native_state(bundle);
        audible_native(bundle, profile);
        check(counts.audible_frames != 0 && counts.compared_frames > 200000,
              "native audio coverage unexpectedly empty");
        std::cout << "{\"suite\":\"native-abi-v1\",\"instances\":" << counts.instances
                  << ",\"assertions\":" << counts.assertions
                  << ",\"descriptors\":" << counts.descriptors
                  << ",\"conversions\":" << counts.conversions
                  << ",\"accepted_callbacks\":" << counts.accepted_callbacks
                  << ",\"rejected_calls\":" << counts.rejected_calls
                  << ",\"state_round_trips\":" << counts.state_round_trips
                  << ",\"lifecycle_sequences\":" << counts.lifecycle_sequences
                  << ",\"compared_frames\":" << counts.compared_frames
                  << ",\"audible_frames\":" << counts.audible_frames
                  << ",\"maximum_audio_error\":" << counts.maximum_audio_error
                  << ",\"float_hash\":\"" << std::hex << std::setw(16) << std::setfill('0')
                  << counts.float_hash << "\"}\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "native ABI acceptance failed: " << error.what() << '\n';
        return 1;
    }
}
