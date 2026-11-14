#include "TestSupport.h"
#include "hammond/Engine.h"
#include "hammond/ParameterBridge.h"

#include <array>
#include <bit>
#include <cfenv>
#include <cstdint>
#include <set>
#include <string_view>

namespace {
using hammond::Event;
using hammond::EventType;
using hammond::Manual;
constexpr auto upper = Manual::Upper;
constexpr auto lower = Manual::Lower;
constexpr auto drawbar = EventType::BankDrawbar;
constexpr auto expression = EventType::Expression;
constexpr auto selector = EventType::SelectBank;
constexpr auto percussion = EventType::Percussion;
constexpr auto pedal_drawbar = EventType::PedalDrawbar;
constexpr auto preset_selector = EventType::SelectPreset;

struct Expected {
    std::uint32_t id;
    EventType type;
    Manual manual;
    std::uint8_t index;
    std::uint8_t steps;
    double initial;
};

// Independent inventory transcribed from the version-4 registry contract.
// It is deliberately not derived from the native descriptor array or lookup.
constexpr std::array<Expected, 47> expected{{
    {4096, drawbar, upper, 0, 8, 0}, {4097, drawbar, upper, 1, 8, 0},
    {4098, drawbar, upper, 2, 8, 0}, {4099, drawbar, upper, 3, 8, 0},
    {4100, drawbar, upper, 4, 8, 0}, {4101, drawbar, upper, 5, 8, 0},
    {4102, drawbar, upper, 6, 8, 0}, {4103, drawbar, upper, 7, 8, 0},
    {4104, drawbar, upper, 8, 8, 0},
    {4112, drawbar, upper, 9, 8, 0}, {4113, drawbar, upper, 10, 8, 0},
    {4114, drawbar, upper, 11, 8, 0}, {4115, drawbar, upper, 12, 8, 0},
    {4116, drawbar, upper, 13, 8, 0}, {4117, drawbar, upper, 14, 8, 0},
    {4118, drawbar, upper, 15, 8, 0}, {4119, drawbar, upper, 16, 8, 0},
    {4120, drawbar, upper, 17, 8, 0},
    {4128, drawbar, lower, 0, 8, 0}, {4129, drawbar, lower, 1, 8, 0},
    {4130, drawbar, lower, 2, 8, 0}, {4131, drawbar, lower, 3, 8, 0},
    {4132, drawbar, lower, 4, 8, 0}, {4133, drawbar, lower, 5, 8, 0},
    {4134, drawbar, lower, 6, 8, 0}, {4135, drawbar, lower, 7, 8, 0},
    {4136, drawbar, lower, 8, 8, 0},
    {4144, drawbar, lower, 9, 8, 0}, {4145, drawbar, lower, 10, 8, 0},
    {4146, drawbar, lower, 11, 8, 0}, {4147, drawbar, lower, 12, 8, 0},
    {4148, drawbar, lower, 13, 8, 0}, {4149, drawbar, lower, 14, 8, 0},
    {4150, drawbar, lower, 15, 8, 0}, {4151, drawbar, lower, 16, 8, 0},
    {4152, drawbar, lower, 17, 8, 0},
    {8192, expression, upper, 0, 0, 1},
    {8208, selector, upper, 0, 1, 1}, {8209, selector, lower, 0, 1, 1},
    {12288, percussion, upper, 0, 1, 0}, {12289, percussion, upper, 1, 1, 0},
    {12290, percussion, upper, 2, 1, 0}, {12291, percussion, upper, 3, 1, 0},
    {16384, pedal_drawbar, lower, 0, 8, 0}, {16385, pedal_drawbar, lower, 1, 8, 0},
    {20480, preset_selector, upper, 0, 11, 11}, {20481, preset_selector, lower, 0, 11, 11},
}};

// Independent literal oracle transcribed from the frozen conversion contract.
// Python acceptance separately proves these binary64 choices with exact rationals.
constexpr std::array preset_thresholds{
    0x1.745d1745d1746p-5, 0x1.1745d1745d174p-3, 0x1.d1745d1745d17p-3,
    0x1.45d1745d1745dp-2, 0x1.a2e8ba2e8ba2fp-2, 0x1.0000000000000p-1,
    0x1.2e8ba2e8ba2e9p-1, 0x1.5d1745d1745d1p-1, 0x1.8ba2e8ba2e8bap-1,
    0x1.ba2e8ba2e8ba3p-1, 0x1.e8ba2e8ba2e8cp-1};
constexpr std::array preset_canonical{
    0x0.0p+0, 0x1.745d1745d1746p-4, 0x1.745d1745d1746p-3,
    0x1.1745d1745d174p-2, 0x1.745d1745d1746p-2, 0x1.d1745d1745d17p-2,
    0x1.1745d1745d174p-1, 0x1.45d1745d1745dp-1, 0x1.745d1745d1746p-1,
    0x1.a2e8ba2e8ba2fp-1, 0x1.d1745d1745d17p-1, 0x1.0000000000000p+0};

constexpr double maximum(const Expected& spec) {
    return spec.steps == 0 ? 1.0 : static_cast<double>(spec.steps);
}

std::size_t successful_conversions = 0;
std::size_t rejected_conversions = 0;

bool same_event(const Event& left, const Event& right) {
    return left.offset == right.offset && left.type == right.type &&
           left.manual == right.manual && left.index == right.index &&
           std::bit_cast<std::uint64_t>(left.value) ==
               std::bit_cast<std::uint64_t>(right.value);
}

Event sentinel() {
    return {0xabcdef01U, static_cast<EventType>(255), static_cast<Manual>(255),
            253, std::bit_cast<double>(0x7ff800000000babeULL)};
}

void converted(const Expected& spec, double normalized, double plain,
               std::uint32_t offset = 7919) {
    Event actual = sentinel();
    CHECK(hammond::normalized_to_event(spec.id, normalized, offset, actual));
    const Event oracle{offset, spec.type, spec.manual, spec.index, plain};
    CHECK(same_event(actual, oracle));
    ++successful_conversions;
}

void rejected(std::uint32_t id, double normalized) {
    Event actual = sentinel();
    const auto original = actual;
    CHECK(!hammond::normalized_to_event(id, normalized, 7, actual));
    CHECK(same_event(actual, original));
    ++rejected_conversions;
}

void plain_rejected(std::uint32_t id, double plain) {
    double destination = std::bit_cast<double>(0x7ff800000000cafeULL);
    const auto original = std::bit_cast<std::uint64_t>(destination);
    CHECK(!hammond::plain_to_normalized(id, plain, destination));
    CHECK(std::bit_cast<std::uint64_t>(destination) == original);
    ++rejected_conversions;
}

void test_inventory() {
    CHECK(hammond::kParameterCount == 47);
    CHECK(hammond::kParameterRegistrySchemaVersion == 4);
    CHECK(hammond::kParameterRegistryModel == "exclusive-fixed-percussion-pedal-console-v4");
    CHECK(static_cast<std::uint8_t>(pedal_drawbar) == 12);
    CHECK(static_cast<std::uint8_t>(preset_selector) == 14);
    const auto actual = hammond::parameter_descriptors();
    CHECK(actual.size() == expected.size());
    CHECK(actual.data() == hammond::parameter_descriptors().data());
    std::set<std::string_view> paths;
    std::size_t discrete_count = 0;
    for (std::size_t i = 0; i < expected.size(); ++i) {
        const auto& spec = expected[i];
        const auto& descriptor = actual[i];
        CHECK(descriptor.id == spec.id);
        CHECK(descriptor.event_type == spec.type);
        CHECK(descriptor.manual == spec.manual);
        CHECK(descriptor.index == spec.index);
        CHECK(descriptor.step_count == spec.steps);
        CHECK(descriptor.maximum == maximum(spec));
        CHECK(descriptor.default_plain == spec.initial);
        CHECK(!descriptor.path.empty() && !descriptor.kind.empty() && !descriptor.unit.empty());
        CHECK(paths.insert(descriptor.path).second);
        hammond::ParameterDescriptor copied;
        CHECK(hammond::parameter_descriptor(spec.id, copied));
        CHECK(copied == descriptor);
        double normalized = -5.0;
        CHECK(hammond::plain_to_normalized(spec.id, spec.initial, normalized));
        converted(spec, normalized, spec.initial);
        discrete_count += spec.steps != 0 ? 1U : 0U;
    }
    CHECK(discrete_count == 46);
}

void test_id_holes_and_atomic_rejection() {
    const auto base_descriptor = hammond::parameter_descriptors().back();
    auto unknown = [&](std::uint32_t id) {
        auto descriptor = base_descriptor;
        CHECK(!hammond::parameter_descriptor(id, descriptor));
        CHECK(descriptor == base_descriptor);
        rejected(id, 0.5);
        plain_rejected(id, 0.0);
    };
    for (std::uint32_t id = 0; id <= 20482; ++id) {
        bool known = false;
        for (const auto& spec : expected) known = known || spec.id == id;
        if (!known) unknown(id);
    }
    for (const auto id : {0x7fffffffU, 0x80000000U, 0xfffffffeU, 0xffffffffU}) unknown(id);

    const std::array invalid{
        -std::numeric_limits<double>::denorm_min(), -1.0,
        std::nextafter(1.0, 2.0), 2.0, std::numeric_limits<double>::max(),
        std::numeric_limits<double>::infinity(), -std::numeric_limits<double>::infinity(),
        std::bit_cast<double>(0x7ff8000000001234ULL)};
    for (const auto& spec : expected) {
        for (const auto value : invalid) rejected(spec.id, value);
        for (const auto value : {-1.0, std::numeric_limits<double>::infinity(),
                                 -std::numeric_limits<double>::infinity(),
                                 std::numeric_limits<double>::quiet_NaN()}) {
            plain_rejected(spec.id, value);
        }
        const double bound = maximum(spec);
        plain_rejected(spec.id, std::nextafter(bound, bound * 2));
        plain_rejected(spec.id, -std::numeric_limits<double>::denorm_min());
        if (spec.steps != 0) {
            for (const auto value : {std::numeric_limits<double>::denorm_min(),
                                     0.25, 0.5, std::nextafter(1.0, 0.0)}) {
                plain_rejected(spec.id, value);
            }
        }
    }
}

void test_thresholds_and_rounding_modes() {
    const int original_rounding = std::fegetround();
    CHECK(original_rounding != -1);
    constexpr std::array thresholds{0.0625, 0.1875, 0.3125, 0.4375,
                                    0.5625, 0.6875, 0.8125, 0.9375};
    for (const int mode : {FE_TONEAREST, FE_DOWNWARD, FE_UPWARD, FE_TOWARDZERO}) {
        CHECK(std::fesetround(mode) == 0);
        for (const auto& spec : expected) {
            converted(spec, 0.0, 0.0, 0);
            converted(spec, -0.0, spec.steps == 0 ? -0.0 : 0.0);
            converted(spec, 1.0, maximum(spec),
                      std::numeric_limits<std::uint32_t>::max());
            const double small = std::numeric_limits<double>::denorm_min();
            converted(spec, small, spec.steps == 0 ? small : 0.0);
            if (spec.steps == 11) {
                for (std::size_t index = 0; index < preset_thresholds.size(); ++index) {
                    converted(spec, std::nextafter(preset_thresholds[index], 0.0),
                              static_cast<double>(index));
                    converted(spec, preset_thresholds[index], static_cast<double>(index + 1));
                    converted(spec, std::nextafter(preset_thresholds[index], 1.0),
                              static_cast<double>(index + 1));
                }
            } else if (spec.steps == 8) {
                for (std::size_t index = 0; index < thresholds.size(); ++index) {
                    const double before = static_cast<double>(index);
                    const double after = static_cast<double>(index + 1);
                    converted(spec, std::nextafter(thresholds[index], 0.0), before);
                    converted(spec, thresholds[index], after);
                    converted(spec, std::nextafter(thresholds[index], 1.0), after);
                }
            } else if (spec.steps == 1) {
                converted(spec, std::nextafter(0.5, 0.0), 0.0);
                converted(spec, 0.5, 1.0);
                converted(spec, std::nextafter(0.5, 1.0), 1.0);
            } else {
                for (const auto value : {small, std::numeric_limits<double>::min(),
                                         0.12345678901234567, std::nextafter(0.5, 0.0),
                                         0.5, std::nextafter(0.5, 1.0),
                                         std::nextafter(1.0, 0.0), -0.0}) {
                    converted(spec, value, value);
                    double normalized = -999.0;
                    CHECK(hammond::plain_to_normalized(spec.id, value, normalized));
                    CHECK(std::bit_cast<std::uint64_t>(normalized) ==
                          std::bit_cast<std::uint64_t>(value));
                }
            }
            if (spec.steps != 0) {
                for (std::uint8_t plain = 0; plain <= spec.steps; ++plain) {
                    double normalized = -999.0;
                    CHECK(hammond::plain_to_normalized(spec.id, plain, normalized));
                    const double canonical = spec.steps == 11 ? preset_canonical[plain] :
                        (spec.steps == 8 ? static_cast<double>(plain) * 0.125 :
                         static_cast<double>(plain));
                    CHECK(std::bit_cast<std::uint64_t>(normalized) ==
                          std::bit_cast<std::uint64_t>(canonical));
                    converted(spec, normalized, static_cast<double>(plain));
                }
            }
            double negative_zero = 1.0;
            CHECK(hammond::plain_to_normalized(spec.id, -0.0, negative_zero));
            CHECK(std::bit_cast<std::uint64_t>(negative_zero) ==
                  std::bit_cast<std::uint64_t>(spec.steps == 11 ? 0.0 : -0.0));
            rejected(spec.id, std::nextafter(1.0, 2.0));
            rejected(spec.id, std::numeric_limits<double>::quiet_NaN());
            plain_rejected(spec.id, std::numeric_limits<double>::infinity());
            plain_rejected(spec.id, std::numeric_limits<double>::quiet_NaN());
            if (spec.steps != 0) plain_rejected(spec.id, 0.5);
            CHECK(std::fegetround() == mode);
        }
        rejected(8192, std::numeric_limits<double>::quiet_NaN());
        plain_rejected(4096, 0.5);
        CHECK(std::fegetround() == mode);
    }
    CHECK(std::fesetround(original_rounding) == 0);
}

void test_native_events_reach_their_retained_engine_targets() {
    hammond::Engine engine;
    CHECK(engine.prepare(load_test_profile(), {48000.0, 1024, 53, 777},
                         hammond::make_nominal_console_model()) == hammond::Status::Ok);
    const auto initial = engine.controls_snapshot();
    for (const auto& spec : expected) {
        Event event;
        double normalized = -1.0;
        CHECK(hammond::plain_to_normalized(spec.id, spec.initial, normalized));
        CHECK(hammond::normalized_to_event(spec.id, normalized, 0, event));
        CHECK(engine.process(0, {}, std::span<const Event>(&event, 1)));
    }
    CHECK(engine.controls_snapshot() == initial);
    const std::array held{Event{0, EventType::NoteOn, upper, 60, 100},
                          Event{0, EventType::NoteOn, lower, 67, 100},
                          Event{0, EventType::Percussion, upper, 0, 1}};
    CHECK(engine.process(512, {}, held));
    const auto clock = engine.frame_clock();
    const auto readiness = engine.percussion_diagnostics().readiness;
    CHECK(readiness > 0 && readiness < 1);
    hammond::ContactKeySnapshot key_before;
    CHECK(engine.contact_snapshot(upper, 60, key_before));
    std::array<double, hammond::kToneSourceCount> phases{};
    for (std::size_t i = 0; i < phases.size(); ++i) {
        CHECK(engine.source_phase_turns(static_cast<hammond::ToneId>(i + 1), phases[i]));
    }
    auto controls = engine.controls_snapshot();
    for (const auto& spec : expected) {
        Event event;
        CHECK(hammond::normalized_to_event(spec.id, 1.0, 0, event));
        CHECK(engine.process(0, {}, std::span<const Event>(&event, 1)));
        const auto manual = static_cast<std::size_t>(spec.manual);
        if (spec.type == drawbar) {
            controls.drawbars[manual][spec.index / 9][spec.index % 9] = 8;
        } else if (spec.type == selector || spec.type == preset_selector) {
            controls.selected_banks[manual] = hammond::DrawbarBank::B;
            controls.fixed_registrations[manual] = hammond::FixedRegistration::None;
            controls.route_enabled[manual] = true;
        } else if (spec.type == expression) {
            controls.expression = 1;
        } else if (spec.type == pedal_drawbar) {
            controls.pedal_drawbars[spec.index] = 8;
        } else {
            switch (spec.index) {
            case 0: controls.percussion.enabled = true; break;
            case 1: controls.percussion.harmonic = hammond::PercussionHarmonic::Third; break;
            case 2: controls.percussion.volume = hammond::PercussionVolume::Soft; break;
            case 3: controls.percussion.decay = hammond::PercussionDecay::Fast; break;
            default: CHECK(false); break;
            }
        }
        CHECK(engine.controls_snapshot() == controls);
        CHECK(engine.frame_clock() == clock);
        CHECK(engine.percussion_diagnostics().readiness == readiness);
    }
    const Event cancel{0, EventType::Cancel, upper, 0, 0};
    CHECK(engine.process(0, {}, std::span<const Event>(&cancel, 1)));
    Event hidden;
    CHECK(hammond::normalized_to_event(4096, 0.25, 0, hidden));
    CHECK(engine.process(0, {}, std::span<const Event>(&hidden, 1)));
    auto snapshot = engine.controls_snapshot();
    CHECK(snapshot.drawbars[0][0][0] == 2 && snapshot.drawbars[0][1][0] == 8);
    CHECK(!snapshot.route_enabled[0]);
    CHECK(snapshot.selected_banks[0] == hammond::DrawbarBank::B);
    Event reselect;
    CHECK(hammond::normalized_to_event(8208, 1.0, 0, reselect));
    CHECK(engine.process(0, {}, std::span<const Event>(&reselect, 1)));
    CHECK(engine.controls_snapshot().route_enabled[0]);
    CHECK(engine.frame_clock() == clock && engine.key_down(upper, 60));
    CHECK(engine.percussion_diagnostics().readiness == readiness);
    hammond::ContactKeySnapshot key_after;
    CHECK(engine.contact_snapshot(upper, 60, key_after));
    CHECK(key_before == key_after);
    for (std::size_t i = 0; i < phases.size(); ++i) {
        double phase = -1;
        CHECK(engine.source_phase_turns(static_cast<hammond::ToneId>(i + 1), phase));
        CHECK(phase == phases[i]);
    }
    Event out_of_block;
    CHECK(hammond::normalized_to_event(8192, 0.375,
                                      std::numeric_limits<std::uint32_t>::max(), out_of_block));
    const auto before_reject = engine.controls_snapshot();
    std::array<float, 1> output{42};
    const auto result = engine.process(1, output, std::span<const Event>(&out_of_block, 1));
    CHECK(result.status == hammond::Status::InvalidEvent && result.events_consumed == 0);
    CHECK(output[0] == 42);
    CHECK(engine.controls_snapshot() == before_reject && engine.frame_clock() == clock);
}

void test_preset_parameters_retain_banks_and_all_other_live_history() {
    hammond::Engine engine;
    CHECK(engine.prepare(load_test_profile(), {48000.0, 1024, 53, 777},
                         hammond::make_nominal_console_model()) == hammond::Status::Ok);
    const std::array held{Event{0, EventType::NoteOn, upper, 60, 100},
                          Event{0, EventType::NoteOn, lower, 67, 100},
                          Event{0, EventType::PedalOn, lower, 1, 100},
                          Event{0, EventType::Percussion, upper, 0, 1},
                          Event{0, EventType::BankDrawbar, upper, 0, 7},
                          Event{0, EventType::BankDrawbar, lower, 9, 6}};
    CHECK(engine.process(128, {}, held));
    auto retained = engine.controls_snapshot();
    const auto clock = engine.frame_clock();
    const auto readiness = engine.percussion_diagnostics().readiness;
    hammond::ContactKeySnapshot upper_contacts{}, lower_contacts{};
    hammond::PedalContactStates pedal_contacts{};
    CHECK(engine.contact_snapshot(upper, 60, upper_contacts));
    CHECK(engine.contact_snapshot(lower, 67, lower_contacts));
    CHECK(engine.pedal_contacts_snapshot(pedal_contacts));
    std::array<double, hammond::kToneSourceCount> phases{};
    for (std::size_t i = 0; i < phases.size(); ++i) {
        CHECK(engine.source_phase_turns(static_cast<hammond::ToneId>(i + 1), phases[i]));
    }
    for (const auto& spec : {expected[45], expected[46]}) {
        const auto manual = static_cast<std::size_t>(spec.manual);
        // Visit fixed modes, Cancel with a retained row, adjustable A and B.
        for (const auto selection : std::array<std::uint8_t, 12>{1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 10, 11}) {
            Event event;
            CHECK(hammond::normalized_to_event(spec.id, preset_canonical[selection], 0, event));
            CHECK(engine.process(0, {}, std::span<const Event>(&event, 1)));
            if (selection == 0) {
                retained.route_enabled[manual] = false;
            } else if (selection < 10) {
                retained.fixed_registrations[manual] = static_cast<hammond::FixedRegistration>(selection);
                retained.route_enabled[manual] = true;
            } else {
                retained.selected_banks[manual] = selection == 10 ?
                    hammond::DrawbarBank::A : hammond::DrawbarBank::B;
                retained.fixed_registrations[manual] = hammond::FixedRegistration::None;
                retained.route_enabled[manual] = true;
            }
            CHECK(engine.controls_snapshot() == retained);
            CHECK(engine.frame_clock() == clock);
            CHECK(engine.percussion_diagnostics().readiness == readiness);
            CHECK(engine.key_down(upper, 60) && engine.key_down(lower, 67));
            CHECK(engine.pedal_down(hammond::PedalId{1}));
            hammond::ContactKeySnapshot current_upper{}, current_lower{};
            hammond::PedalContactStates current_pedals{};
            CHECK(engine.contact_snapshot(upper, 60, current_upper));
            CHECK(engine.contact_snapshot(lower, 67, current_lower));
            CHECK(engine.pedal_contacts_snapshot(current_pedals));
            CHECK(current_upper == upper_contacts && current_lower == lower_contacts);
            CHECK(current_pedals == pedal_contacts);
        }
        // A repeated legacy B command must leave fixed mode even though its
        // remembered bank and enabled route already match the old command.
        Event fixed, reselect;
        CHECK(hammond::normalized_to_event(spec.id, preset_canonical[3], 0, fixed));
        CHECK(hammond::normalized_to_event(manual == 0 ? 8208U : 8209U, 1.0, 0, reselect));
        CHECK(engine.process(0, {}, std::span<const Event>(&fixed, 1)));
        CHECK(engine.process(0, {}, std::span<const Event>(&reselect, 1)));
        CHECK(engine.controls_snapshot() == retained);
    }
    for (std::size_t i = 0; i < phases.size(); ++i) {
        double phase = -1;
        CHECK(engine.source_phase_turns(static_cast<hammond::ToneId>(i + 1), phase));
        CHECK(phase == phases[i]);
    }
}

void test_pedal_parameters_remain_independent_of_manual_routes_and_live_contacts() {
    hammond::Engine engine;
    CHECK(engine.prepare(load_test_profile(), {48000.0, 1024, 53, 777},
                         hammond::make_nominal_console_model()) == hammond::Status::Ok);
    const std::array held{Event{0, EventType::NoteOn, lower, 60, 100},
                          Event{0, EventType::PedalOn, lower, 1, 100}};
    CHECK(engine.process(32, {}, held));
    CHECK(engine.key_down(lower, 60));
    CHECK(engine.pedal_down(hammond::PedalId{1}));
    const auto clock = engine.frame_clock();
    hammond::PedalContactStates contacts{};
    CHECK(engine.pedal_contacts_snapshot(contacts));
    const auto readiness = engine.percussion_diagnostics().readiness;
    std::array<double, hammond::kToneSourceCount> phases{};
    for (std::size_t i = 0; i < phases.size(); ++i) {
        CHECK(engine.source_phase_turns(static_cast<hammond::ToneId>(i + 1), phases[i]));
    }
    for (const auto action : {Event{0, EventType::Cancel, lower, 0, 0},
                              Event{0, EventType::SelectBank, lower, 0, 0},
                              Event{0, EventType::Cancel, lower, 0, 0}}) {
        CHECK(engine.process(0, {}, std::span<const Event>(&action, 1)));
        auto expected_controls = engine.controls_snapshot();
        for (std::uint8_t index = 0; index < 2; ++index) {
            for (std::uint8_t position = 0; position <= 8; ++position) {
                Event event;
                CHECK(hammond::normalized_to_event(16384U + index,
                                                  static_cast<double>(position) * 0.125,
                                                  0, event));
                CHECK(engine.process(0, {}, std::span<const Event>(&event, 1)));
                expected_controls.pedal_drawbars[index] = position;
                CHECK(engine.controls_snapshot() == expected_controls);
                std::uint8_t observed = 255;
                CHECK(engine.pedal_drawbar_position(index, observed) && observed == position);
                hammond::PedalContactStates current_contacts{};
                CHECK(engine.pedal_contacts_snapshot(current_contacts));
                CHECK(current_contacts == contacts);
                CHECK(engine.frame_clock() == clock && engine.key_down(lower, 60));
                CHECK(engine.percussion_diagnostics().readiness == readiness);
            }
        }
    }
    for (std::size_t i = 0; i < phases.size(); ++i) {
        double phase = -1;
        CHECK(engine.source_phase_turns(static_cast<hammond::ToneId>(i + 1), phase));
        CHECK(phase == phases[i]);
    }
}
} // namespace

int main() {
    test_inventory();
    test_id_holes_and_atomic_rejection();
    test_thresholds_and_rounding_modes();
    test_native_events_reach_their_retained_engine_targets();
    test_pedal_parameters_remain_independent_of_manual_routes_and_live_contacts();
    test_preset_parameters_retain_banks_and_all_other_live_history();
    std::cout << "parameter bridge: " << successful_conversions << " independent conversions, "
              << rejected_conversions << " atomic conversion rejections; 47 live Engine targets; "
              << "all four rounding modes passed\n";
    return EXIT_SUCCESS;
}
