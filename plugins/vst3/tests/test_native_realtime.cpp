#include "NativeAllocationProbe.h"

#include "hammond/ConsoleModel.h"
#include "hammond/Engine.h"
#include "hammond/Profile.h"

#include <algorithm>
#include <array>
#include <bit>
#include <chrono>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <limits>
#include <span>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

#include <dlfcn.h>

#if !defined(__linux__)
#error This test requires proved Linux ELF interposition; other platforms need a separate probe.
#endif

namespace {

using namespace hammond;
using namespace hammond::native_test;
using Steinberg::int16;
using Steinberg::int32;
constexpr float kSentinel = -1234.5F;
constexpr Steinberg::uint64 kFlags = 0xA5U;
constexpr sv::ParamID kExpression = 0x2000U;
constexpr sv::ParamID kPedalTwo = 0x4001U;
constexpr std::size_t kCapacity = static_cast<std::size_t>(kHardMaxBlockFrames) + 4;
static_assert(std::chrono::steady_clock::is_steady);

enum class Path : std::size_t { Enabled, Dense, Maximum, Carry, OutputShape, Rejected, Lifecycle, Count };
constexpr std::array<const char*, static_cast<std::size_t>(Path::Count)> kNames{
    "enabled", "dense", "maximum", "carry", "output-shape", "rejected", "setProcessing"};
struct Totals {
    std::uint64_t accepted{}, rejected{}, frames{}, fresh_records{}, carried_records{}, restores{};
    std::size_t allocations{}, deallocations{};
    double elapsed_us{}, maximum_us{};
};
struct Statistics {
    std::array<Totals, static_cast<std::size_t>(Path::Count)> paths{};
    std::uint64_t comparisons{}, audible_samples{}, reference_frames{}, state_reads{};
    std::uint64_t rollback_cases{}, future_comparisons{}, moving_contacts{}, full_owner_checks{};
    std::uint64_t checksum{14695981039346656037ULL};
    std::uint64_t assertions{};
} stats;

void check(bool condition, std::string_view message) {
    ++stats.assertions;
    require(condition, message);
}

// Timers surround the probe, but assertions, labels, aggregation, allocation of
// fixtures and reference rendering do not. Only the native virtual call is inside.
template <class Function>
void observe(Path path, bool accepted, std::uint32_t frames, std::uint32_t fresh,
             std::uint32_t carry, std::uint32_t restores, std::string_view label,
             Function&& call) {
    const auto started = std::chrono::steady_clock::now();
    allocation_probe::begin();
    Steinberg::tresult result{};
    try {
        result = call();
    } catch (...) {
        (void)allocation_probe::end();
        throw;
    }
    const auto allocations = allocation_probe::end();
    const auto finished = std::chrono::steady_clock::now();
    const auto elapsed = std::chrono::duration<double, std::micro>(finished - started).count();
    check(std::isfinite(elapsed) && elapsed >= 0.0, "nonfinite or negative measured duration");
    if (allocations.allocations != 0 || allocations.deallocations != 0) {
        throw std::runtime_error(std::string(label) + ": native call allocated " +
            std::to_string(allocations.allocations) + " and freed " +
            std::to_string(allocations.deallocations));
    }
    check((result == Steinberg::kResultOk) == accepted,
          std::string(label) + ": unexpected native result " + std::to_string(result));
    auto& row = stats.paths[static_cast<std::size_t>(path)];
    if (accepted) {
        ++row.accepted;
        row.frames += frames;
        row.fresh_records += fresh;
        row.carried_records += carry;
        row.restores += restores;
    } else {
        ++row.rejected;
    }
    row.allocations += allocations.allocations;
    row.deallocations += allocations.deallocations;
    row.elapsed_us += elapsed;
    row.maximum_us = std::max(row.maximum_us, elapsed);
}

void callback(NativePlugin& plugin, StereoBlock& block, Path path, bool accepted,
              std::string_view label, std::uint32_t fresh = 0,
              std::uint32_t carry = 0, std::uint32_t restores = 0) {
    observe(path, accepted, accepted ? static_cast<std::uint32_t>(block.data.numSamples) : 0,
            fresh, carry, restores, label, [&] { return plugin.processor->process(block.data); });
}

void processing(NativePlugin& plugin, Steinberg::TBool state, bool accepted) {
    observe(Path::Lifecycle, accepted, 0, 0, 0, 0, "setProcessing",
            [&] { return plugin.processor->setProcessing(state); });
}

void check_export_scope() {
    // ELF/Itanium ABI guard against accidentally restoring --export-dynamic.
    // This function is present in the independently linked reference Engine.
    // Exporting it could substitute the host's DSP into the module under test.
    // The intended flags export only _Znw*, _Zna*, _Zdl* and _Zda*.
    check(dlsym(RTLD_DEFAULT,
                "_ZN7hammond6Engine16restore_controlsERKNS_15ControlSnapshotE") == nullptr,
          "reference Engine is dynamically exported; native module isolation is invalid");
}

// Raw module factory and release calls isolate native allocation from loader,
// host, string, and fixture construction. An uninitialized component is valid to
// release. Require a positive net lifetime count, not an assumed DSO override.
template <class Interface>
void calibrate_module_class(Steinberg::IPluginFactory* factory, const Steinberg::FUID& id,
                            const char* label) {
    Interface* object = nullptr;
    allocation_probe::begin();
    const auto result = factory->createInstance(id.toTUID(), Interface::iid,
                                                reinterpret_cast<void**>(&object));
    const auto constructed = allocation_probe::end();
    require_ok(result, "calibration raw module factory create");
    check(object != nullptr, "calibration factory returned null");
    allocation_probe::begin();
    const auto references = object->release();
    const auto destroyed = allocation_probe::end();
    check(references == 0, "calibration module object retained a reference");
    check(constructed.allocations > constructed.deallocations && destroyed.deallocations > 0,
          "module allocation/deallocation interposition was not proved");
    check(constructed.allocations + destroyed.allocations ==
          constructed.deallocations + destroyed.deallocations,
          "calibration module lifetime allocation balance differs");
    std::printf("module calibration %s create new=%zu delete=%zu; release new=%zu delete=%zu refs=%u\n",
                label, constructed.allocations, constructed.deallocations,
                destroyed.allocations, destroyed.deallocations, references);
}

void prove_module_interposition(const std::string& bundle) {
    NativePlugin loaded(bundle);
    auto* factory = loaded.module().getFactory().get().get();
    calibrate_module_class<sv::IComponent>(factory, expected_processor_id(), "processor");
    calibrate_module_class<sv::IEditController>(factory, expected_controller_id(), "controller");
}

ControlSnapshot registration() {
    ControlSnapshot controls{};
    controls.selected_banks = {DrawbarBank::B, DrawbarBank::B};
    controls.drawbars[0][1][2] = 4;
    controls.drawbars[1][1][2] = 3;
    controls.pedal_drawbars = {2, 1};
    controls.expression = 0.625;
    controls.percussion.enabled = true;
    return controls;
}

Event key(Manual manual, std::uint8_t pitch, bool on) {
    return {0, on ? EventType::NoteOn : EventType::NoteOff, manual, pitch, on ? 127.0 : 0.0};
}
Event pedal(std::uint8_t id, bool on) {
    return {0, on ? EventType::PedalOn : EventType::PedalOff, Manual::Lower, id, on ? 127.0 : 0.0};
}
Event expression(double value) { return {0, EventType::Expression, Manual::Upper, 0, value}; }

ControlSnapshot saved(NativePlugin& plugin) {
    std::string bytes;
    require_ok(plugin.save_state(bytes), "save native controls outside probe");
    ++stats.state_reads;
    return parse_snapshot(bytes);
}

void reset(StereoBlock& block, int32 frames, EventList* notes = nullptr,
           ParameterChanges* parameters = nullptr) {
    block.channels = {block.left.data(), block.right.data()};
    block.bus.numChannels = 2;
    block.bus.channelBuffers32 = block.channels.data();
    block.bus.silenceFlags = kFlags;
    block.data = {};
    block.data.processMode = sv::kRealtime;
    block.data.symbolicSampleSize = sv::kSample32;
    block.data.numOutputs = 1;
    block.data.outputs = &block.bus;
    block.data.inputEvents = notes;
    block.data.inputParameterChanges = parameters;
    block.set_frames(frames);
    block.fill(kSentinel);
}

void untouched(const StereoBlock& block) {
    check(std::all_of(block.left.begin(), block.left.end(), [](float f) { return f == kSentinel; }),
          "unwritten left host storage changed");
    check(std::all_of(block.right.begin(), block.right.end(), [](float f) { return f == kSentinel; }),
          "unwritten right host storage changed");
    check(block.bus.silenceFlags == kFlags, "unwritten host silence flags changed");
}

struct Session {
    NativePlugin plugin;
    Engine reference{};
    StereoBlock block{kCapacity};
    std::vector<float> expected = std::vector<float>(kCapacity);

    Session(const std::string& bundle, const RuntimeProfile& profile, double rate) : plugin(bundle) {
        plugin.start(rate, static_cast<int32>(kHardMaxBlockFrames));
        check(reference.prepare(profile, {rate, kHardMaxBlockFrames, 0, 0},
                                make_nominal_console_model()) == Status::Ok,
              "independent Engine prepare failed");
    }

    void restore(const ControlSnapshot& controls) {
        check(reference.restore_controls(controls), "independent reference restore failed");
    }

    void queue(const ControlSnapshot& controls) {
        require_ok(plugin.load_state(snapshot_text(controls)), "native queued controls");
    }

    void four_restores(const ControlSnapshot& final) {
        for (std::size_t index = 0; index < 4; ++index) {
            auto candidate = final;
            candidate.expression = index == 3 ? final.expression : 0.125 * static_cast<double>(index + 1);
            queue(candidate);
        }
        check(plugin.load_state(snapshot_text(final)) != Steinberg::kResultOk,
              "full four-state queue accepted a fifth restore");
        check(saved(plugin) == final, "save did not preserve newest queued state");
    }

    void render_reference(std::uint32_t frames, std::span<const Event> physical = {}) {
        const auto before = reference.frame_clock();
        const auto result = reference.process(frames, {expected.data(), frames}, physical);
        check(result.ok() && result.events_consumed == physical.size(), "plain Engine oracle rejected");
        check(reference.frame_clock() == before + frames, "plain Engine reference clock mismatch");
        stats.reference_frames += frames;
    }

    // A per-sample expression oracle does not use ParameterBridge or HostTimeline.
    // Its specified arithmetic is identical to the public straight-line contract.
    template <class Curve>
    void render_curve(std::uint32_t frames, Curve&& curve) {
        for (std::uint32_t frame = 0; frame < frames; ++frame) {
            const std::array<Event, 1> point{{expression(curve(frame))}};
            const auto result = reference.process(1, {expected.data() + frame, 1}, point);
            check(result.ok() && result.events_consumed == 1, "one-sample expression oracle rejected");
        }
        stats.reference_frames += frames;
    }

    void compare(std::uint32_t frames, bool alias = false, bool future = false) {
        bool silent = true;
        for (std::uint32_t frame = 0; frame < frames; ++frame) {
            const float wanted = expected[frame];
            check(std::isfinite(wanted), "reference sample was nonfinite");
            for (std::size_t channel = 0; channel < 2; ++channel) {
                const float actual = block.channels[channel][frame];
                check(std::isfinite(actual) && std::bit_cast<std::uint32_t>(actual) ==
                      std::bit_cast<std::uint32_t>(wanted), "native/reference sample mismatch");
                ++stats.comparisons;
                if (future) ++stats.future_comparisons;
                if (actual != 0.0F) ++stats.audible_samples;
                stats.checksum ^= std::bit_cast<std::uint32_t>(actual);
                stats.checksum *= 1099511628211ULL;
            }
            silent = silent && wanted == 0.0F;
        }
        check(block.bus.silenceFlags == (silent ? 3U : 0U), "native silence flags mismatch");
        for (std::size_t index = frames; index < kCapacity; ++index) {
            check(block.left[index] == kSentinel && block.right[index] == kSentinel,
                  "callback wrote beyond requested frames");
        }
        if (alias) {
            check(std::all_of(block.right.begin(), block.right.end(),
                             [](float f) { return f == kSentinel; }), "exact alias touched unused right storage");
        }
        check(saved(plugin) == reference.controls_snapshot(), "published native controls differ from reference");
    }

    void process(std::uint32_t frames, Path path, std::span<const Event> physical = {},
                 EventList* notes = nullptr, ParameterChanges* parameters = nullptr,
                 std::uint32_t fresh = 0, std::uint32_t carry = 0,
                 std::uint32_t restores = 0, bool future = false) {
        reset(block, static_cast<int32>(frames), notes, parameters);
        callback(plugin, block, path, true, "accepted native callback", fresh, carry, restores);
        render_reference(frames, physical);
        compare(frames, false, future);
    }
};

void reject_and_resume(Session& session, std::string_view label,
                       const ControlSnapshot* pending = nullptr) {
    const auto controls = saved(session.plugin);
    callback(session.plugin, session.block, Path::Rejected, false, label);
    untouched(session.block);
    check(saved(session.plugin) == controls, "rejected callback changed saved controls");
    ++stats.rollback_cases;
    if (pending != nullptr) {
        check(session.plugin.load_state(snapshot_text(*pending)) != Steinberg::kResultOk,
              "rejection consumed a pending state queue entry");
        session.restore(*pending);
    }
    session.process(257, Path::Enabled, {}, nullptr, nullptr, 0, 0, pending == nullptr ? 0 : 4, true);
    check(std::any_of(session.block.left.begin(), session.block.left.begin() + 257,
                      [](float f) { return f != 0.0F; }), "rollback oracle was silent");
}

void native_rejections(Session& session) {
    EventList notes;
    notes.events = {note_on(0, 72, 0, 4, 50000), note_on(2, 55, 63, 4, 50001)};
    notes.events.back().noteOn.velocity = std::numeric_limits<float>::quiet_NaN();
    reset(session.block, 64, &notes);
    reject_and_resume(session, "late invalid native velocity");
    notes.events.back().noteOn.velocity = 1.0F;
    notes.fail_index = 1;
    reset(session.block, 64, &notes);
    reject_and_resume(session, "late native getEvent failure");

    ParameterChanges changes;
    auto& parameter = changes.add_queue(kExpression);
    parameter.points = {{0, 0.125}, {63, std::numeric_limits<double>::quiet_NaN()}};
    reset(session.block, 64, nullptr, &changes);
    reject_and_resume(session, "late invalid native parameter value");
    parameter.points.back().normalized = 0.875;
    parameter.fail_index = 1;
    reset(session.block, 64, nullptr, &changes);
    reject_and_resume(session, "late native getPoint failure");

    reset(session.block, 64);
    session.block.bus.numChannels = 1;
    reject_and_resume(session, "invalid output channel count");
    reset(session.block, 64);
    session.block.channels[1] = session.block.left.data() + 1;
    reject_and_resume(session, "partial native output overlap");
    reset(session.block, 64);
    session.block.data.outputs = nullptr;
    reject_and_resume(session, "missing declared native output bus");
    reset(session.block, 64);
    session.block.data.symbolicSampleSize = sv::kSample64;
    reject_and_resume(session, "unsupported native precision");
}

void output_shapes(Session& session) {
    reset(session.block, 64);
    session.block.channels[1] = session.block.left.data();
    callback(session.plugin, session.block, Path::OutputShape, true, "exact output alias");
    session.render_reference(64);
    session.compare(64, true);

    reset(session.block, 64);
    session.block.data.numOutputs = 0;
    session.block.data.outputs = nullptr;
    callback(session.plugin, session.block, Path::OutputShape, true, "disconnected output");
    session.render_reference(64);
    untouched(session.block);
    session.process(64, Path::OutputShape, {}, nullptr, nullptr, 0, 0, 0, true);

    session.plugin.stop_processing();
    require_ok(session.plugin.component->activateBus(sv::kAudio, sv::kOutput, 0, false), "deactivate output");
    session.plugin.begin_processing();
    reset(session.block, 64);
    session.block.channels = {nullptr, nullptr};
    callback(session.plugin, session.block, Path::OutputShape, true, "inactive output");
    session.render_reference(64);
    untouched(session.block);
    session.plugin.stop_processing();
    require_ok(session.plugin.component->activateBus(sv::kAudio, sv::kOutput, 0, true), "reactivate output");
    session.plugin.begin_processing();
    session.process(64, Path::OutputShape, {}, nullptr, nullptr, 0, 0, 0, true);

    reset(session.block, 0);
    session.block.bus.numChannels = 0;
    session.block.bus.channelBuffers32 = nullptr;
    callback(session.plugin, session.block, Path::OutputShape, true, "zero channels zero frames");
    check(session.block.bus.silenceFlags == 0, "zero channel flags not cleared");
    session.block.bus.silenceFlags = kFlags;
    untouched(session.block);
    reset(session.block, 0);
    session.block.channels = {nullptr, nullptr};
    callback(session.plugin, session.block, Path::OutputShape, true, "null sample pointers zero frames");
    check(session.block.bus.silenceFlags == 3, "empty stereo did not report silence");
    session.block.bus.silenceFlags = kFlags;
    untouched(session.block);
    session.process(64, Path::OutputShape, {}, nullptr, nullptr, 0, 0, 0, true);
}

void lifecycle(Session& session) {
    processing(session.plugin, 1, true);
    processing(session.plugin, 0, true);
    processing(session.plugin, 0, true);
    processing(session.plugin, 2, false);
    reset(session.block, 64);
    callback(session.plugin, session.block, Path::Rejected, false, "process while stopped");
    untouched(session.block);
    processing(session.plugin, 1, true);
    processing(session.plugin, 1, true);
    session.process(257, Path::Enabled, {}, nullptr, nullptr, 0, 0, 0, true);
}

void enabled_rate(const std::string& bundle, const RuntimeProfile& profile, double rate) {
    Session session(bundle, profile, rate);
    const auto controls = registration();
    session.four_restores(controls);
    session.restore(controls);
    EventList notes;
    notes.events = {note_on(0, 60, 0, 2, 100), note_on(1, 48, 0, 3, 101), note_on(2, 48, 0, 4, 102)};
    const std::array<Event, 3> physical{{key(Manual::Upper, 60, true), key(Manual::Lower, 48, true),
                                        pedal(13, true)}};
    session.process(64, Path::Enabled, physical, &notes, nullptr, 3, 0, 4);
    ContactKeySnapshot contact{};
    check(session.reference.contact_snapshot(Manual::Upper, 60, contact) &&
          contact.position > 0.0 && contact.position < 1.0, "enabled reference contact was not moving");
    ++stats.moving_contacts;
    check(session.reference.active_key_count() == 2 && session.reference.active_pedal_count() == 1,
          "enabled manual/pedal fixture is empty");

    // A second full enqueue proves the first successful callback drained all four.
    session.four_restores(controls);
    session.process(1024, Path::Enabled, {}, nullptr, nullptr, 0, 0, 4);
    check(session.reference.percussion_diagnostics().routed_detector &&
          session.reference.percussion_diagnostics().readiness < 1.0,
          "reference did not exercise enabled routed percussion");

    ParameterChanges flush;
    flush.add_queue(kExpression).points = {{0, 0.75}};
    flush.add_queue(kPedalTwo).points = {{0, 0.5}};
    const std::array<Event, 2> flush_physical{{expression(0.75),
        {0, EventType::PedalDrawbar, Manual::Lower, 1, 4.0}}};
    session.process(0, Path::Carry, flush_physical, nullptr, &flush, 2);

    ParameterChanges dense;
    auto& dense_points = dense.add_queue(kExpression).points;
    dense_points.reserve(1024);
    for (std::size_t index = 0; index < 1024; ++index) {
        dense_points.push_back({0, (index & 1U) != 0 ? 0.75 : 0.25});
    }
    const std::array<Event, 1> dense_physical{{expression(0.75)}};
    session.process(32, Path::Dense, dense_physical, nullptr, &dense, 1024);

    ParameterChanges ramp;
    ramp.add_queue(kExpression).points = {{0, 0.25}, {static_cast<int32>(kHardMaxBlockFrames), 0.75}};
    reset(session.block, static_cast<int32>(kHardMaxBlockFrames), nullptr, &ramp);
    callback(session.plugin, session.block, Path::Maximum, true, "maximum sampled expression callback", 2);
    session.render_curve(kHardMaxBlockFrames, [](std::uint32_t frame) {
        return 0.25 + (static_cast<double>(frame) / static_cast<double>(kHardMaxBlockFrames)) * 0.5;
    });
    session.compare(kHardMaxBlockFrames);
    const std::array<Event, 1> endpoint{{expression(0.75)}};
    session.process(0, Path::Carry, endpoint, nullptr, nullptr, 0, 1);
    session.process(0, Path::Carry);
    output_shapes(session);
    native_rejections(session);
    lifecycle(session);
    std::printf("enabled rate %.0f: manual, pedal, moving contacts, percussion and independent audio verified\n", rate);
}

void full_owners_and_carry(const std::string& bundle, const RuntimeProfile& profile) {
    Session session(bundle, profile, 48000.0);
    const auto controls = registration();
    session.four_restores(controls);
    session.restore(controls);
    EventList owners;
    EventList releases;
    std::vector<Event> physical_on;
    std::vector<Event> physical_off;
    owners.events.reserve(512);
    releases.events.reserve(512);
    physical_on.reserve(147);
    physical_off.reserve(147);
    for (int32 index = 0; index < 256; ++index) {
        const auto bus = index % 2;
        const auto pitch = static_cast<int16>(36 + (index / 2) % 61);
        const auto pedal_pitch = static_cast<int16>(36 + index % 25);
        const auto channel = static_cast<int16>(index % 16);
        owners.events.push_back(note_on(bus, pitch, 0, channel, index));
        owners.events.push_back(note_on(2, pedal_pitch, 0, channel, 1000 + index));
        releases.events.push_back(note_off(bus, pitch, 0, channel, index));
        releases.events.push_back(note_off(2, pedal_pitch, 0, channel, 1000 + index));
        if (index < 122) physical_on.push_back(key(bus == 0 ? Manual::Upper : Manual::Lower,
                                                  static_cast<std::uint8_t>(pitch), true));
        if (index < 25) physical_on.push_back(pedal(static_cast<std::uint8_t>(index + 1), true));
        if (index + 122 >= 256) physical_off.push_back(key(bus == 0 ? Manual::Upper : Manual::Lower,
                                                         static_cast<std::uint8_t>(pitch), false));
        if (index + 25 >= 256) physical_off.push_back(pedal(static_cast<std::uint8_t>(index % 25 + 1), false));
    }
    check(physical_on.size() == 147 && physical_off.size() == 147, "full owner physical oracle size");
    ParameterChanges fill;
    fill.add_queue(kExpression).points.assign(512, {0, 0.625});
    session.process(64, Path::Dense, physical_on, &owners, &fill, 1024, 0, 4);
    check(session.reference.active_key_count() == 122 && session.reference.active_pedal_count() == 25,
          "full owner fixture did not enable every physical note");

    EventList overflow;
    overflow.events = {note_on(0, 60, 0, 0, 99999)};
    auto pending = controls;
    pending.expression = 0.5;
    session.four_restores(pending);
    reset(session.block, 64, &overflow);
    reject_and_resume(session, "manual owner 257 with four pending restores", &pending);
    ++stats.full_owner_checks;
    overflow.events = {note_on(2, 48, 0, 0, 99999)};
    reset(session.block, 64, &overflow);
    reject_and_resume(session, "pedal owner 257");
    ++stats.full_owner_checks;

    ParameterChanges boundary;
    boundary.add_queue(kExpression).points.assign(1024, {32, 0.875});
    const auto anchor = session.reference.expression();
    reset(session.block, 32, nullptr, &boundary);
    callback(session.plugin, session.block, Path::Carry, true, "full boundary carry storage", 1024);
    session.render_curve(32, [anchor](std::uint32_t frame) {
        return anchor + ((static_cast<double>(frame) + 1.0) / 33.0) * (0.875 - anchor);
    });
    session.compare(32);

    // The incoming record is valid by itself; existing 1024 carry records make
    // the complete transaction over budget. Verify no state/time/output advances.
    EventList additional;
    additional.events = {note_off(0, 36, 0, 0, 0)};
    const auto before = saved(session.plugin);
    reset(session.block, 64, &additional);
    callback(session.plugin, session.block, Path::Rejected, false, "full carry plus fresh native record");
    untouched(session.block);
    check(saved(session.plugin) == before, "carry rejection changed controls");
    ++stats.rollback_cases;
    const std::array<Event, 1> endpoint{{expression(0.875)}};
    session.process(0, Path::Carry, endpoint, nullptr, nullptr, 0, 1024);
    session.process(0, Path::Carry);
    // A new full raw budget must now fit. Equal-value controls alone cannot
    // reveal stale duplicate carry, whereas this capacity check can.
    ParameterChanges drained;
    drained.add_queue(kExpression).points.assign(1024, {0, 0.875});
    session.process(0, Path::Carry, endpoint, nullptr, &drained, 1024);
    session.process(257, Path::Enabled, {}, nullptr, nullptr, 0, 0, 0, true);

    session.process(64, Path::Dense, physical_off, &releases, nullptr, 512);
    check(session.reference.active_key_count() == 0 && session.reference.active_pedal_count() == 0,
          "full owner releases did not reach final owners");
    ContactKeySnapshot contact{};
    check(session.reference.contact_snapshot(Manual::Upper, 60, contact) && contact.target == 0.0 &&
          contact.position > 0.0, "full owner release did not exercise moving contacts");
    ++stats.moving_contacts;
    session.process(2048, Path::Enabled);
    check(std::all_of(session.block.left.begin() + 1024, session.block.left.begin() + 2048,
                      [](float f) { return f == 0.0F; }), "released notes retained audible ownership");
}

void unready_lifecycle(const std::string& bundle) {
    NativePlugin plugin(bundle);
    processing(plugin, 1, false);
    processing(plugin, 0, false);
    plugin.configure(48000.0, 64);
    processing(plugin, 1, false);
}

void print_results() {
    std::puts("path accepted rejected frames fresh_raw carried_raw queued_restores new delete total_us max_us");
    std::uint64_t calls = 0;
    for (std::size_t index = 0; index < stats.paths.size(); ++index) {
        const auto& row = stats.paths[index];
        calls += row.accepted + row.rejected;
        std::printf("%s %llu %llu %llu %llu %llu %llu %zu %zu %.3f %.3f\n", kNames[index],
                    static_cast<unsigned long long>(row.accepted), static_cast<unsigned long long>(row.rejected),
                    static_cast<unsigned long long>(row.frames), static_cast<unsigned long long>(row.fresh_records),
                    static_cast<unsigned long long>(row.carried_records), static_cast<unsigned long long>(row.restores),
                    row.allocations, row.deallocations, row.elapsed_us, row.maximum_us);
    }
    std::printf("regions=%llu overload_calibration=12/12 exact_channel_samples=%llu audible_samples=%llu "
                "reference_frames=%llu state_reads=%llu rollback_cases=%llu future_channel_samples=%llu "
                "moving_contact_checks=%llu owner_capacity_checks=%llu assertions=%llu checksum=%016llx\n",
                static_cast<unsigned long long>(calls), static_cast<unsigned long long>(stats.comparisons),
                static_cast<unsigned long long>(stats.audible_samples), static_cast<unsigned long long>(stats.reference_frames),
                static_cast<unsigned long long>(stats.state_reads), static_cast<unsigned long long>(stats.rollback_cases),
                static_cast<unsigned long long>(stats.future_comparisons), static_cast<unsigned long long>(stats.moving_contacts),
                static_cast<unsigned long long>(stats.full_owner_checks), static_cast<unsigned long long>(stats.assertions),
                static_cast<unsigned long long>(stats.checksum));
    std::puts("Scope: Linux calling-thread global C++ new/delete; timings are observations, not device deadlines.");
}

} // namespace

int main(int argc, char* argv[]) {
    try {
        require(argc == 3, "usage: test_native_realtime BUNDLE COMPILED_PROFILE");
        allocation_probe::calibrate_overloads();
        check_export_scope();
        const std::string bundle(argv[1]);
        prove_module_interposition(bundle);
        RuntimeProfile profile{};
        std::string error;
        require(load_runtime_profile_file(argv[2], profile, error), "independent profile load: " + error);
        for (double rate : {44100.0, 48000.0, 96000.0}) enabled_rate(bundle, profile, rate);
        full_owners_and_carry(bundle, profile);
        unready_lifecycle(bundle);
        check(stats.audible_samples > 0 && stats.future_comparisons > 0,
              "native allocation workload lacked audible semantic evidence");
        print_results();
        return 0;
    } catch (const std::exception& error) {
        (void)allocation_probe::end();
        std::fprintf(stderr, "test_native_realtime: %s\n", error.what());
        return 1;
    }
}
