#include "TestSupport.h"
#include "UiModel.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <limits>
#include <set>
#include <span>
#include <variant>

namespace {
using namespace hammond;
using namespace hammond::standalone;

static_assert(static_cast<std::uint8_t>(UiControlKind::PedalKey) == 17);
static_assert(static_cast<std::uint8_t>(UiControlKind::MidiSettings) == 18);
static_assert(static_cast<std::uint8_t>(UiControlKind::PresetKey) == 19);
static_assert(static_cast<std::uint8_t>(UiAppRequest::Help) == 3);
static_assert(static_cast<std::uint8_t>(UiAppRequest::MidiSettings) == 4);

constexpr UiControlId manual_key(Manual manual, std::uint8_t midi) {
    return {UiControlKind::ManualKey, manual, DrawbarBank::A,
            static_cast<std::uint8_t>(midi - 36)};
}

constexpr UiControlId pedal_key(std::uint8_t pedal) {
    return {UiControlKind::PedalKey, Manual::Upper, DrawbarBank::A,
            static_cast<std::uint8_t>(pedal - 1)};
}

constexpr UiControlId preset_key(Manual manual, std::uint8_t index) {
    return {UiControlKind::PresetKey, manual, DrawbarBank::A, index};
}

UiActions tap(UiModel& model, UiKey key, bool shift = false) {
    const auto actions = model.key({key, true, false, shift});
    CHECK(model.key({key, false}).count == 0);
    return actions;
}

const SessionCommand& command(const UiActions& actions, std::size_t index = 0) {
    CHECK(actions.count <= actions.items.size());
    CHECK(index < actions.count);
    CHECK(std::holds_alternative<SessionCommand>(actions.items[index]));
    return std::get<SessionCommand>(actions.items[index]);
}

const ControlSnapshot& controls(const UiActions& actions) {
    CHECK(actions.count == 1);
    CHECK(std::holds_alternative<ControlSnapshot>(command(actions)));
    return std::get<ControlSnapshot>(command(actions));
}

void manual_event(const UiActions& actions, std::size_t index, bool down,
                  std::uint8_t bus, std::uint8_t midi, std::int32_t owner) {
    const auto& input = std::get<PerformanceInputEvent>(command(actions, index));
    CHECK(std::holds_alternative<HostNoteEvent>(input));
    const auto& event = std::get<HostNoteEvent>(input);
    CHECK(event.offset == 0 && event.channel == 0);
    CHECK(event.kind == (down ? HostNoteKind::On : HostNoteKind::Off));
    CHECK(event.bus == bus && event.midi_note == midi && event.note_id == owner);
    CHECK(event.velocity == (down ? 127 : 0));
}

void pedal_event(const UiActions& actions, std::size_t index, bool down,
                 std::uint8_t pedal, std::int32_t owner) {
    const auto& input = std::get<PerformanceInputEvent>(command(actions, index));
    CHECK(std::holds_alternative<PedalNoteEvent>(input));
    const auto& event = std::get<PedalNoteEvent>(input);
    CHECK(event.offset == 0 && event.bus == 0 && event.channel == 0);
    CHECK(event.kind == (down ? PedalNoteKind::On : PedalNoteKind::Off));
    CHECK(event.pedal.value == pedal && event.note_id == owner);
    CHECK(event.velocity == (down ? 127 : 0));
}

UiPoint key_point(const UiModel& model, UiControlId id) {
    const auto& key = id.kind == UiControlKind::PedalKey ?
        model.layout().pedal_keys[id.index] :
        model.layout().manual_keys[static_cast<std::size_t>(id.manual)][id.index];
    return {key.bounds.x + key.bounds.width * 0.5F,
            key.bounds.y + key.bounds.height * (key.accidental ? 0.5F : 0.9F)};
}

UiControlGeometry geometry(const UiLayout& layout, UiControlId id) {
    for (std::size_t index = 0; index < layout.control_count; ++index) {
        if (layout.controls[index].id == id) return layout.controls[index];
    }
    hammond_test::fail("visible control exists", __FILE__, __LINE__);
}

UiControlGeometry geometry(const UiModel& model, UiControlId id) {
    return geometry(model.layout(), id);
}

// Real Session/Engine processing qualifies physical ownership, not only the
// shape of emitted variants. Zero-frame boundaries isolate input semantics.
struct Rig {
    Session session;
    UiModel model;

    Rig() {
        CHECK(session.prepare(load_test_profile(), {48000.0, 64, 17, 0}) == SessionStatus::Ok);
        CHECK(session.start() == SessionStatus::Ok);
        observe();
    }

    void dispatch(const UiActions& actions) {
        for (std::size_t index = 0; index < actions.count; ++index) {
            const auto& item = command(actions, index);
            const auto result = session.post(item);
            CHECK(result.ok());
            CHECK(model.submitted(item, result).count == 0);
        }
    }

    SessionSnapshot snapshot() {
        SessionSnapshot state;
        CHECK(session.read_snapshot(state));
        return state;
    }

    void observe() { model.observe(snapshot()); }

    void flush() {
        CHECK(session.render(0, {}).ok());
        observe();
    }
};

void registry_and_retained_banks() {
    // Literal published IDs, deliberately not the implementation's ID formula
    // or iteration over parameter_descriptors(). The holes remain visible.
    constexpr std::array<std::array<std::uint32_t, 9>, 4> bank_ids{{
        {4096, 4097, 4098, 4099, 4100, 4101, 4102, 4103, 4104},
        {4112, 4113, 4114, 4115, 4116, 4117, 4118, 4119, 4120},
        {4128, 4129, 4130, 4131, 4132, 4133, 4134, 4135, 4136},
        {4144, 4145, 4146, 4147, 4148, 4149, 4150, 4151, 4152}}};
    constexpr std::array<UiControlId, 4> banks{{
        {UiControlKind::ManualDrawbar, Manual::Upper, DrawbarBank::A},
        {UiControlKind::ManualDrawbar, Manual::Upper, DrawbarBank::B},
        {UiControlKind::ManualDrawbar, Manual::Lower, DrawbarBank::A},
        {UiControlKind::ManualDrawbar, Manual::Lower, DrawbarBank::B}}};
    std::set<std::uint32_t> seen;
    for (std::size_t bank = 0; bank < banks.size(); ++bank) {
        for (std::size_t index = 0; index < 9; ++index) {
            auto id = banks[bank];
            id.index = static_cast<std::uint8_t>(index);
            std::uint32_t actual = 0;
            CHECK(ui_parameter_id(id, actual));
            CHECK(actual == bank_ids[bank][index]);
            CHECK(seen.insert(actual).second);
        }
    }
    struct ParameterCase { UiControlId control; std::uint32_t id; };
    constexpr std::array<ParameterCase, 11> remaining{{
        {{UiControlKind::Expression}, 8192},
        {{UiControlKind::SoundingBank, Manual::Upper, DrawbarBank::A}, 8208},
        {{UiControlKind::SoundingBank, Manual::Lower, DrawbarBank::B}, 8209},
        {{UiControlKind::Percussion, Manual::Upper, DrawbarBank::A, 0}, 12288},
        {{UiControlKind::Percussion, Manual::Upper, DrawbarBank::A, 1}, 12289},
        {{UiControlKind::Percussion, Manual::Upper, DrawbarBank::A, 2}, 12290},
        {{UiControlKind::Percussion, Manual::Upper, DrawbarBank::A, 3}, 12291},
        {{UiControlKind::PedalDrawbar, Manual::Upper, DrawbarBank::A, 0}, 16384},
        {{UiControlKind::PedalDrawbar, Manual::Upper, DrawbarBank::A, 1}, 16385},
        {preset_key(Manual::Upper, 0), 20480},
        {preset_key(Manual::Lower, 11), 20481}}};
    for (const auto& entry : remaining) {
        std::uint32_t actual = 0;
        CHECK(ui_parameter_id(entry.control, actual) && actual == entry.id);
        CHECK(seen.insert(actual).second);
    }
    CHECK(seen.size() == 47 && parameter_descriptors().size() == 47);
    for (const auto& descriptor : parameter_descriptors()) CHECK(seen.contains(descriptor.id));
    for (const auto kind : {UiControlKind::EditBank, UiControlKind::CancelManual,
                           UiControlKind::Panic, UiControlKind::SaveControls,
                           UiControlKind::ManualKey, UiControlKind::PedalKey,
                           UiControlKind::MidiSettings}) {
        std::uint32_t unchanged = 999;
        CHECK(!ui_parameter_id({kind}, unchanged) && unchanged == 999);
    }

    UiModel model;
    for (std::size_t bank = 0; bank < banks.size(); ++bank) {
        const auto id = banks[bank];
        CHECK(model.activate({UiControlKind::EditBank, id.manual, id.bank}).count == 0);
        CHECK(model.activate(id).count == 0);
        for (std::size_t step = 0; step <= bank; ++step) CHECK(tap(model, UiKey::Up).count == 1);
    }
    const auto retained = model.view().controls;
    CHECK(retained.drawbars[0][0][0] == 1 && retained.drawbars[0][1][0] == 2);
    CHECK(retained.drawbars[1][0][0] == 3 && retained.drawbars[1][1][0] == 4);
    CHECK((retained.selected_banks == std::array{DrawbarBank::B, DrawbarBank::B}));
    CHECK(retained.route_enabled[0] && retained.route_enabled[1]);
    const auto cancelled = controls(model.activate({UiControlKind::CancelManual, Manual::Upper}));
    CHECK(!cancelled.route_enabled[0] && cancelled.route_enabled[1]);
    CHECK(cancelled.drawbars == retained.drawbars && cancelled.selected_banks == retained.selected_banks);
    const auto reconnected = controls(model.activate({UiControlKind::SoundingBank, Manual::Upper, DrawbarBank::B}));
    CHECK(reconnected.route_enabled[0] && reconnected.drawbars == retained.drawbars);
    CHECK(model.view().edited_banks[0] == DrawbarBank::B);
    const auto lower_a = controls(model.activate({UiControlKind::SoundingBank, Manual::Lower, DrawbarBank::A}));
    CHECK(lower_a.selected_banks[1] == DrawbarBank::A && model.view().edited_banks[1] == DrawbarBank::B);

    const auto before = model.view().controls;
    const auto focus_before = model.view().focus;
    constexpr std::array<UiControlId, 9> malformed{{
        {UiControlKind::ManualDrawbar, static_cast<Manual>(9)},
        {UiControlKind::ManualDrawbar, Manual::Upper, static_cast<DrawbarBank>(9)},
        {UiControlKind::ManualDrawbar, Manual::Upper, DrawbarBank::A, 9},
        {UiControlKind::PedalDrawbar, Manual::Upper, DrawbarBank::A, 2},
        {UiControlKind::Expression, Manual::Lower},
        {UiControlKind::PresetKey, static_cast<Manual>(2)},
        {UiControlKind::PresetKey, Manual::Upper, DrawbarBank::B, 1},
        {UiControlKind::PresetKey, Manual::Lower, DrawbarBank::A, 12},
        {static_cast<UiControlKind>(255)}}};
    for (const auto id : malformed) {
        std::uint32_t unchanged = 999;
        CHECK(!ui_parameter_id(id, unchanged) && unchanged == 999);
        CHECK(model.activate(id).count == 0 && model.view().controls == before);
        CHECK(model.view().focus == focus_before);
    }
}

void physical_keys_and_release_identity() {
    struct KeyCase { UiKey key; std::uint8_t midi; std::uint8_t pedal; std::int32_t owner; };
    constexpr std::array<KeyCase, 17> keys{{
        {UiKey::A, 60, 1, 1}, {UiKey::W, 61, 2, 2}, {UiKey::S, 62, 3, 3},
        {UiKey::E, 63, 4, 4}, {UiKey::D, 64, 5, 5}, {UiKey::F, 65, 6, 6},
        {UiKey::T, 66, 7, 7}, {UiKey::G, 67, 8, 8}, {UiKey::Y, 68, 9, 9},
        {UiKey::H, 69, 10, 10}, {UiKey::U, 70, 11, 11}, {UiKey::J, 71, 12, 12},
        {UiKey::K, 72, 13, 13}, {UiKey::O, 73, 14, 14}, {UiKey::L, 74, 15, 15},
        {UiKey::P, 75, 16, 16}, {UiKey::Semicolon, 76, 17, 17}}};
    UiModel mapping;
    for (const auto target : {UiKey::F1, UiKey::F2, UiKey::F3}) {
        CHECK(tap(mapping, target).count == 0);
        for (const auto& entry : keys) {
            const auto on = mapping.key({entry.key, true});
            const auto off = mapping.key({entry.key, false});
            CHECK(on.count == 1 && off.count == 1);
            if (target == UiKey::F3) {
                pedal_event(on, 0, true, entry.pedal, entry.owner);
                pedal_event(off, 0, false, entry.pedal, entry.owner);
            } else {
                const std::uint8_t bus = target == UiKey::F1 ? 0 : 1;
                manual_event(on, 0, true, bus, entry.midi, entry.owner);
                manual_event(off, 0, false, bus, entry.midi, entry.owner);
            }
        }
    }
    Rig rig;
    rig.dispatch(rig.model.key({UiKey::A, true}));
    CHECK(rig.model.key({UiKey::A, true}).count == 0);
    CHECK(rig.model.key({UiKey::A, true, true}).count == 0);
    CHECK(tap(rig.model, UiKey::F2).count == 0);
    CHECK(tap(rig.model, UiKey::RightBracket).count == 0);
    CHECK(rig.model.activate(manual_key(Manual::Lower, 96)).count == 0);
    rig.dispatch(rig.model.key({UiKey::S, true}));
    rig.flush();
    CHECK(rig.model.view().applied.held_keys[0][24]); // Original Upper C4.
    CHECK(rig.model.view().applied.held_keys[1][38]); // New Lower D5.
    rig.model.set_text_entry_active(true);
    const auto off = rig.model.key({UiKey::A, false, false, false, true, true, true});
    CHECK(off.count == 1);
    manual_event(off, 0, false, 0, 60, 1);
    rig.dispatch(off);
    CHECK(rig.model.key({UiKey::A, false}).count == 0);
    rig.dispatch(rig.model.key({UiKey::S, false}));
    CHECK(rig.model.key({UiKey::D, true}).count == 0);
    rig.model.set_text_entry_active(false);
    CHECK(rig.model.key({UiKey::D, true}).count == 0);
    CHECK(rig.model.key({UiKey::D, false}).count == 0);
    rig.flush();
    CHECK(!rig.model.view().applied.held_keys[0][24] && !rig.model.view().applied.held_keys[1][38]);
    for (const UiKeyInput chord : {UiKeyInput{UiKey::A, true, false, false, true},
                                  UiKeyInput{UiKey::A, true, false, false, false, true},
                                  UiKeyInput{UiKey::A, true, false, false, false, false, true}}) {
        CHECK(rig.model.key(chord).count == 0);
        CHECK(rig.model.key({UiKey::A, false}).count == 0);
    }
    CHECK(rig.model.key({UiKey::A, true, true}).count == 0); // Orphan repeat.
    CHECK(rig.model.key({UiKey::A, true}).count == 0);
    CHECK(rig.model.key({UiKey::A, false}).count == 0);

    CHECK(tap(mapping, UiKey::F1).count == 0);
    for (int n = 0; n < 5; ++n) CHECK(tap(mapping, UiKey::RightBracket).count == 0);
    CHECK(mapping.view().manual_base_midi == 84);
    manual_event(mapping.key({UiKey::K, true}), 0, true, 0, 96, 13);
    CHECK(mapping.key({UiKey::O, true}).count == 0); // 97 must not clamp to 96.
    CHECK(mapping.key({UiKey::O, false}).count == 0);
    CHECK(mapping.key({UiKey::K, false}).count == 1);
    for (int n = 0; n < 6; ++n) CHECK(tap(mapping, UiKey::LeftBracket).count == 0);
    CHECK(mapping.view().manual_base_midi == 36);
    manual_event(mapping.key({UiKey::A, true}), 0, true, 0, 36, 1);
    CHECK(mapping.key({UiKey::A, false}).count == 1);
    CHECK(tap(mapping, UiKey::F3).count == 0);
    for (int n = 0; n < 4; ++n) CHECK(tap(mapping, UiKey::RightBracket).count == 0);
    CHECK(mapping.view().pedal_octave == 2);
    pedal_event(mapping.key({UiKey::A, true}), 0, true, 25, 1);
    CHECK(mapping.key({UiKey::W, true}).count == 0);
    CHECK(tap(mapping, UiKey::F1).count == 0);
    pedal_event(mapping.key({UiKey::A, false}), 0, false, 25, 1);
    CHECK(mapping.key({UiKey::W, false}).count == 0);
}

void pointer_audition_and_scoped_release() {
    Rig rig;
    const auto upper = manual_key(Manual::Upper, 60);
    const auto lower = manual_key(Manual::Lower, 64);
    rig.dispatch(rig.model.key({UiKey::A, true}));
    rig.dispatch(rig.model.pointer({UiPointerKind::Down, key_point(rig.model, upper)}));
    rig.flush();
    const auto capture = rig.model.pointer({UiPointerKind::CaptureLost, {}});
    CHECK(capture.count == 1 && !rig.model.view().pointer_captured);
    manual_event(capture, 0, false, 0, 60, 100);
    rig.dispatch(capture);
    rig.flush();
    CHECK(rig.model.view().applied.held_keys[0][24]); // Keyboard owner survives.
    CHECK(rig.model.pointer({UiPointerKind::Move, key_point(rig.model, lower)}).count == 0);
    rig.dispatch(rig.model.pointer({UiPointerKind::Down, key_point(rig.model, upper)}));
    const auto cross_manual = rig.model.pointer({UiPointerKind::Move, key_point(rig.model, lower)});
    CHECK(cross_manual.count == 2);
    manual_event(cross_manual, 0, false, 0, 60, 100);
    manual_event(cross_manual, 1, true, 1, 64, 100);
    rig.dispatch(cross_manual);
    const auto cross_pedal = rig.model.pointer({UiPointerKind::Move, key_point(rig.model, pedal_key(13))});
    CHECK(cross_pedal.count == 2);
    manual_event(cross_pedal, 0, false, 1, 64, 100);
    pedal_event(cross_pedal, 1, true, 13, 100);
    rig.dispatch(cross_pedal);
    rig.dispatch(rig.model.activate({UiControlKind::CancelManual, Manual::Upper}));
    rig.flush();
    CHECK(rig.model.view().applied.held_keys[0][24] && rig.model.view().applied.held_pedals[12]);
    CHECK(!rig.model.view().applied.controls.route_enabled[0]);
    rig.dispatch(rig.model.activate({UiControlKind::SoundingBank, Manual::Upper, DrawbarBank::B}));
    const auto from_pedal = rig.model.pointer({UiPointerKind::Move,
        key_point(rig.model, manual_key(Manual::Upper, 67))});
    CHECK(from_pedal.count == 2);
    pedal_event(from_pedal, 0, false, 13, 100);
    manual_event(from_pedal, 1, true, 0, 67, 100);
    rig.dispatch(from_pedal);
    const auto outside = rig.model.pointer({UiPointerKind::Move, {-100.0F, -100.0F}});
    CHECK(outside.count == 1 && rig.model.view().pointer_captured);
    manual_event(outside, 0, false, 0, 67, 100);
    rig.dispatch(outside);
    const auto save_button = geometry(rig.model, {UiControlKind::SaveControls});
    CHECK(rig.model.pointer({UiPointerKind::Move, {save_button.bounds.x + 1, save_button.bounds.y + 1}}).count == 0);
    rig.dispatch(rig.model.pointer({UiPointerKind::Move, key_point(rig.model, lower)}));
    CHECK(rig.model.resize(960.0F, 700.0F));
    const auto outside_up = rig.model.pointer({UiPointerKind::Up, {-1.0F, -1.0F}});
    CHECK(outside_up.count == 1);
    manual_event(outside_up, 0, false, 1, 64, 100);
    rig.dispatch(outside_up);
    CHECK(rig.model.pointer({UiPointerKind::Up, {}}).count == 0);

    CHECK(rig.model.activate(lower).count == 0);
    const auto audition = rig.model.key({UiKey::Space, true});
    CHECK(audition.count == 1);
    manual_event(audition, 0, true, 1, 64, 101);
    rig.dispatch(audition);
    CHECK(rig.model.key({UiKey::Space, true, true}).count == 0);
    CHECK(tap(rig.model, UiKey::End).count == 0);
    CHECK(rig.model.view().focus == manual_key(Manual::Lower, 96));
    CHECK(rig.model.activate(pedal_key(25)).count == 0);
    const auto audition_off = rig.model.key({UiKey::Space, false});
    manual_event(audition_off, 0, false, 1, 64, 101);
    rig.dispatch(audition_off);
    rig.dispatch(rig.model.key({UiKey::Space, true}));
    const SessionCommand external = PerformanceInputEvent{HostNoteEvent{0, HostNoteKind::On, 0, 2, 60, 127, 700}};
    CHECK(rig.session.post(external).ok());
    const SessionCommand external_pedal = PerformanceInputEvent{PedalNoteEvent{0, PedalNoteKind::On, 0, 3, PedalId{25}, 127, 701}};
    CHECK(rig.session.post(external_pedal).ok());
    rig.flush();
    const auto release = rig.model.release_ui(UiReleaseReason::FocusLost);
    CHECK(release.count == 1 && std::holds_alternative<ReleaseUiNotes>(command(release)));
    rig.dispatch(release);
    rig.flush();
    CHECK(rig.model.view().applied.held_keys[0][24] && rig.model.view().applied.held_pedals[24]);
    CHECK(!rig.model.view().applied.held_keys[1][28]);
    CHECK(rig.model.key({UiKey::A, true}).count == 0);
    CHECK(rig.model.key({UiKey::Space, true}).count == 0);
    CHECK(rig.model.key({UiKey::A, false}).count == 0);
    CHECK(rig.model.key({UiKey::Space, false}).count == 0);
    const auto before = rig.model.view().controls;
    const auto panic = rig.model.panic();
    CHECK(panic.count == 1 && std::holds_alternative<Panic>(command(panic)));
    rig.dispatch(panic);
    rig.flush();
    CHECK(!rig.model.view().applied.held_keys[0][24] && !rig.model.view().applied.held_pedals[24]);
    CHECK(rig.model.view().controls == before);
}

void drag_identity_and_parameter_laws() {
    UiModel model;
    const UiControlId upper_b{UiControlKind::ManualDrawbar, Manual::Upper, DrawbarBank::B, 2};
    const auto bar = geometry(model, upper_b);
    const UiPoint top{bar.track.x + 1, bar.track.y};
    CHECK(model.pointer({UiPointerKind::Down, top}).count == 0);
    const float half_step = bar.track.y + bar.track.height / 16.0F;
    CHECK(model.pointer({UiPointerKind::Move, {top.x, std::nextafter(half_step, -INFINITY)}}).count == 0);
    CHECK(controls(model.pointer({UiPointerKind::Move, {top.x, half_step}})).drawbars[0][1][2] == 1);
    CHECK(controls(model.pointer({UiPointerKind::Move, {top.x, bar.track.y + bar.track.height}})).drawbars[0][1][2] == 8);
    CHECK(model.activate({UiControlKind::EditBank, Manual::Upper, DrawbarBank::A}).count == 0);
    CHECK(model.pointer({UiPointerKind::Move, top}).count == 0);
    CHECK(model.view().controls.drawbars[0][0][2] == 0 && model.view().controls.drawbars[0][1][2] == 8);
    CHECK(model.pointer({UiPointerKind::Up, top}).count == 0);
    const UiControlId upper_a{UiControlKind::ManualDrawbar, Manual::Upper, DrawbarBank::A, 2};
    const auto next = geometry(model, upper_a);
    CHECK(controls(model.pointer({UiPointerKind::Down, {next.track.x + 1, next.track.y + next.track.height / 2}})).drawbars[0][0][2] == 4);
    CHECK(!model.resize(959, 900)); // Rejected resize must preserve the gesture.
    CHECK(controls(model.pointer({UiPointerKind::Move, {next.track.x, next.track.y + next.track.height}})).drawbars[0][0][2] == 8);
    CHECK(model.resize(1920, 1080));
    CHECK(model.pointer({UiPointerKind::Move, top}).count == 0);
    CHECK(model.pointer({UiPointerKind::CaptureLost, {}}).count == 0);
    CHECK(!model.view().pointer_captured);
    CHECK(model.activate(upper_a).count == 0);
    CHECK(tap(model, UiKey::Up).count == 0); // Saturation, no redundant snapshot.
    CHECK(controls(tap(model, UiKey::Down, true)).drawbars[0][0][2] == 7);
    CHECK(controls(tap(model, UiKey::Home)).drawbars[0][0][2] == 0);
    CHECK(controls(tap(model, UiKey::End)).drawbars[0][0][2] == 8);
    CHECK(model.activate({UiControlKind::Expression}).count == 0);
    CHECK_NEAR(controls(tap(model, UiKey::Left)).expression, 0.95, 1e-14);
    CHECK_NEAR(controls(tap(model, UiKey::Left, true)).expression, 0.94, 1e-14);
    CHECK(controls(tap(model, UiKey::Home)).expression == 0);
    CHECK(tap(model, UiKey::Left).count == 0);
    CHECK(controls(tap(model, UiKey::End)).expression == 1);
    const auto expression = geometry(model, {UiControlKind::Expression});
    CHECK_NEAR(controls(model.pointer({UiPointerKind::Down,
        {expression.track.x + expression.track.width / 2, expression.track.y}})).expression, 0.5, 1e-6);
    CHECK(controls(model.pointer({UiPointerKind::Move, {-100, expression.track.y}})).expression == 0);
    CHECK(model.pointer({UiPointerKind::Move, {INFINITY, expression.track.y}}).count == 0);
    CHECK(model.pointer({UiPointerKind::Up, {}}).count == 0);
    for (std::uint8_t index = 0; index < 2; ++index) {
        CHECK(model.activate({UiControlKind::PedalDrawbar, Manual::Upper, DrawbarBank::A, index}).count == 0);
        CHECK(controls(tap(model, UiKey::End)).pedal_drawbars[index] == 8);
    }
    const auto percussion_before = model.view().controls.percussion;
    for (std::uint8_t index = 0; index < 4; ++index) {
        CHECK(model.activate({UiControlKind::Percussion, Manual::Upper, DrawbarBank::A, index}).count == 1);
    }
    CHECK(model.view().controls.percussion.enabled != percussion_before.enabled);
    CHECK(model.view().controls.percussion.harmonic != percussion_before.harmonic);
    CHECK(model.view().controls.percussion.volume != percussion_before.volume);
    CHECK(model.view().controls.percussion.decay != percussion_before.decay);
}

void pending_saved_and_recovery() {
    Rig rig;
    CHECK(!rig.model.view().controls_pending && !rig.model.view().controls_dirty);
    rig.dispatch(rig.model.activate({UiControlKind::SoundingBank, Manual::Upper, DrawbarBank::A}));
    CHECK(rig.model.view().controls_pending && rig.model.view().controls.selected_banks[0] == DrawbarBank::A);
    CHECK(rig.model.view().applied.controls.selected_banks[0] == DrawbarBank::B);
    CHECK(rig.session.render(0, {}).ok());
    const auto first = rig.snapshot();
    CHECK(rig.model.activate({UiControlKind::ManualDrawbar, Manual::Upper, DrawbarBank::A, 0}).count == 0);
    rig.dispatch(tap(rig.model, UiKey::Up));
    rig.model.observe(first); // Acknowledgment of the earlier edit must not erase this one.
    CHECK(rig.model.view().controls_pending && rig.model.view().controls.drawbars[0][0][0] == 1);
    rig.flush();
    CHECK(!rig.model.view().controls_pending && rig.model.view().applied.controls.drawbars[0][0][0] == 1);
    const auto saved = rig.model.view().controls;
    rig.dispatch(tap(rig.model, UiKey::Up));
    rig.model.mark_saved(saved); // A late disk completion acknowledges its exact copy.
    CHECK(rig.model.view().controls_dirty);
    rig.flush();
    rig.model.observe(first);
    CHECK(rig.model.view().controls.drawbars[0][0][0] == 2);
    rig.model.mark_saved(rig.model.view().controls);
    CHECK(!rig.model.view().controls_dirty);
    CHECK(rig.model.activate({UiControlKind::EditBank, Manual::Upper, DrawbarBank::A}).count == 0);
    CHECK(tap(rig.model, UiKey::F2).count == 0);
    rig.dispatch(rig.model.key({UiKey::A, true}));
    auto loaded = saved;
    loaded.drawbars[0][1][8] = 8;
    loaded.drawbars[1][0][4] = 5;
    loaded.drawbars[1][1][7] = 3;
    loaded.expression = 0.25;
    loaded.route_enabled[0] = false;
    loaded.pedal_drawbars = {6, 7};
    loaded.fixed_registrations = {FixedRegistration::GSharp, FixedRegistration::A};
    rig.dispatch(rig.model.load_controls(loaded));
    CHECK(!rig.model.view().controls_dirty && rig.model.view().controls_pending);
    CHECK(rig.model.view().edited_banks[0] == DrawbarBank::A);
    rig.flush();
    CHECK(rig.model.view().controls == loaded && rig.model.view().applied.held_keys[1][24]);
    auto invalid = loaded;
    invalid.drawbars[1][0][8] = 9;
    CHECK(rig.model.load_controls(invalid).count == 0 && rig.model.view().controls == loaded);
    invalid = loaded;
    invalid.expression = std::numeric_limits<double>::quiet_NaN();
    rig.model.mark_saved(invalid);
    CHECK(!rig.model.view().controls_dirty);
    CHECK(rig.model.load_controls(invalid).count == 0 && rig.model.view().controls == loaded);
    auto bad_observation = rig.snapshot();
    bad_observation.publication_revision += 2;
    bad_observation.controls = invalid;
    rig.model.observe(bad_observation);
    CHECK(rig.model.view().controls == loaded);

    // Actual bounded-transport overflow, followed by its actual published
    // recovery. Do not manufacture a successful SubmitResult or fake Engine.
    rig.dispatch(rig.model.pointer({UiPointerKind::Down, key_point(rig.model, pedal_key(1))}));
    rig.flush();
    for (std::size_t index = 0; index < kSessionCommandCapacity; ++index) CHECK(rig.session.post(loaded).ok());
    CHECK(rig.model.activate({UiControlKind::Expression}).count == 0);
    const auto rejected = tap(rig.model, UiKey::Right);
    const auto result = rig.session.post(command(rejected));
    CHECK(result.status == SessionStatus::QueueFull);
    CHECK(rig.model.submitted(command(rejected), result).count == 0);
    CHECK(rig.model.view().input_recovery && !rig.model.view().controls_pending);
    CHECK(rig.model.view().controls == loaded && !rig.model.view().controls_dirty);
    rig.flush();
    CHECK(rig.model.view().applied.recovery_count == 1);
    CHECK(!rig.model.view().applied.held_keys[1][24] && !rig.model.view().applied.held_pedals[0]);
    CHECK(rig.model.key({UiKey::A, true}).count == 0);
    CHECK(rig.model.pointer({UiPointerKind::Move, key_point(rig.model, pedal_key(2))}).count == 0);
    CHECK(rig.model.pointer({UiPointerKind::Down, key_point(rig.model, pedal_key(2))}).count == 0);
    CHECK(rig.model.key({UiKey::A, false}).count == 0);
    CHECK(rig.model.pointer({UiPointerKind::Up, {}}).count == 0);
    rig.dispatch(rig.model.key({UiKey::A, true}));
    rig.flush();
    CHECK(rig.model.view().applied.held_keys[1][24]);
    const SessionCommand invalid_command = invalid;
    const auto invalid_result = rig.session.post(invalid_command);
    CHECK(invalid_result.status == SessionStatus::InvalidCommand);
    const auto cleanup = rig.model.submitted(invalid_command, invalid_result);
    CHECK(cleanup.count == 1 && std::holds_alternative<ReleaseUiNotes>(command(cleanup)));
    const auto repeated_invalid = rig.session.post(invalid_command);
    CHECK(repeated_invalid.status == SessionStatus::InvalidCommand);
    CHECK(rig.model.submitted(invalid_command, repeated_invalid).count == 0); // One cleanup, no retry loop.
    rig.dispatch(cleanup);
    rig.flush();
    CHECK(!rig.model.view().applied.held_keys[1][24]);
}

bool same_rect(UiRect a, UiRect b) {
    return a.x == b.x && a.y == b.y && a.width == b.width && a.height == b.height;
}

void equal_layout(const UiLayout& a, const UiLayout& b) {
    CHECK(a.width == b.width && a.height == b.height && a.control_count == b.control_count);
    CHECK(a.show_cabinet == b.show_cabinet && a.bank_controls_in_cheeks == b.bank_controls_in_cheeks);
    CHECK(same_rect(a.header, b.header) && same_rect(a.performance_panel, b.performance_panel));
    CHECK(same_rect(a.keyboard_toolbar, b.keyboard_toolbar) && same_rect(a.pedal_panel, b.pedal_panel));
    CHECK(same_rect(a.footer, b.footer));
    CHECK(same_rect(a.cabinet_panel, b.cabinet_panel) && same_rect(a.cabinet_art, b.cabinet_art));
    for (std::size_t manual = 0; manual < 2; ++manual) {
        CHECK(same_rect(a.registration_panels[manual], b.registration_panels[manual]));
        CHECK(same_rect(a.manual_panels[manual], b.manual_panels[manual]));
        CHECK(same_rect(a.manual_rail_panels[manual], b.manual_rail_panels[manual]));
        CHECK(same_rect(a.preset_key_panels[manual], b.preset_key_panels[manual]));
        for (std::size_t key = 0; key < 61; ++key) {
            CHECK(a.manual_keys[manual][key].note == b.manual_keys[manual][key].note);
            CHECK(a.manual_keys[manual][key].accidental == b.manual_keys[manual][key].accidental);
            CHECK(same_rect(a.manual_keys[manual][key].bounds, b.manual_keys[manual][key].bounds));
        }
    }
    for (std::size_t key = 0; key < 25; ++key) {
        CHECK(a.pedal_keys[key].note == b.pedal_keys[key].note);
        CHECK(a.pedal_keys[key].accidental == b.pedal_keys[key].accidental);
        CHECK(same_rect(a.pedal_keys[key].bounds, b.pedal_keys[key].bounds));
    }
    for (std::size_t index = 0; index < a.control_count; ++index) {
        const auto& left = a.controls[index];
        const auto& right = b.controls[index];
        CHECK(left.id == right.id && same_rect(left.bounds, right.bounds));
        CHECK(same_rect(left.label_bounds, right.label_bounds) && same_rect(left.value_bounds, right.value_bounds));
        CHECK(same_rect(left.track, right.track));
    }
}

void check_keyboard(const UiLayout& layout, std::span<const UiKeyGeometry> keys,
                    UiTarget target, UiRect panel, std::span<const int> naturals,
                    std::span<const int> accidentals) {
    const int first = target == UiTarget::Pedals ? 1 : 36;
    const auto id_for = [target](int value) {
        const auto note = static_cast<std::uint8_t>(value);
        return target == UiTarget::Pedals ? pedal_key(note) :
            manual_key(target == UiTarget::Upper ? Manual::Upper : Manual::Lower, note);
    };
    CHECK(keys.size() == naturals.size() + accidentals.size());
    for (const auto pitches : {naturals, accidentals}) {
        for (const int value : pitches) {
            const auto& key = keys[static_cast<std::size_t>(value - first)];
            const auto& box = key.bounds;
            CHECK(key.note.target == target && key.note.value == value);
            CHECK(key.accidental == (pitches.data() == accidentals.data()));
            CHECK(box.width > 0 && box.height > 0 && panel.contains({box.x, box.y}));
            CHECK(box.x + box.width <= panel.x + panel.width && box.y + box.height <= panel.y + panel.height);
            CHECK(box.contains({box.x, box.y}));
            CHECK(!box.contains({box.x + box.width, box.y}));
            CHECK(!box.contains({box.x, box.y + box.height}));
            const float hit_y = box.y + box.height * (key.accidental ? 0.5F : 0.9F);
            CHECK(ui_hit_test(layout, {box.x + box.width / 2, hit_y}) == id_for(value));
            CHECK(ui_hit_test(layout, {box.x, hit_y}) == id_for(value));
            if (key.accidental) {
                const UiPoint overlay{box.x + box.width * 0.75F, hit_y};
                bool overlaps_natural = false;
                for (const int natural : naturals) {
                    overlaps_natural |= keys[static_cast<std::size_t>(natural - first)].bounds.contains(overlay);
                }
                CHECK(overlaps_natural && ui_hit_test(layout, overlay) == id_for(value));
                CHECK(ui_hit_test(layout, {overlay.x, box.y + box.height}) == id_for(value + 1));
                CHECK(ui_hit_test(layout, {box.x + box.width, hit_y}) == id_for(value + 1));
            }
        }
    }
    for (std::size_t index = 1; index < naturals.size(); ++index) {
        const auto& previous = keys[static_cast<std::size_t>(naturals[index - 1] - first)].bounds;
        const auto& next = keys[static_cast<std::size_t>(naturals[index] - first)].bounds;
        CHECK_NEAR(previous.x + previous.width, next.x, 0.0005F);
        const float y = next.y + next.height * 0.9F;
        CHECK(ui_hit_test(layout, {next.x, y}) == id_for(naturals[index]));
        CHECK(ui_hit_test(layout, {std::nextafter(next.x, -INFINITY), y}) == id_for(naturals[index - 1]));
    }
    const auto& first_box = keys.front().bounds;
    const auto& last_box = keys.back().bounds;
    CHECK(ui_hit_test(layout, {first_box.x - 1, first_box.y + 1}).kind == UiControlKind::None);
    CHECK(ui_hit_test(layout, {last_box.x + last_box.width, last_box.y + last_box.height * 0.9F}).kind == UiControlKind::None);
    CHECK(ui_hit_test(layout, {first_box.x, first_box.y + first_box.height}).kind == UiControlKind::None);
}

void near_rect(UiRect actual, UiRect expected) {
    CHECK_NEAR(actual.x, expected.x, 0.001F);
    CHECK_NEAR(actual.y, expected.y, 0.001F);
    CHECK_NEAR(actual.width, expected.width, 0.001F);
    CHECK_NEAR(actual.height, expected.height, 0.001F);
}

bool empty(UiRect box) {
    return box.width == 0 && box.height == 0;
}

bool overlaps(UiRect a, UiRect b) {
    return a.width > 0 && a.height > 0 && b.width > 0 && b.height > 0 &&
           a.x < b.x + b.width && b.x < a.x + a.width &&
           a.y < b.y + b.height && b.y < a.y + a.height;
}

void contained(UiRect inner, UiRect outer) {
    CHECK(inner.width > 0 && inner.height > 0);
    CHECK(inner.x >= outer.x - 0.001F && inner.y >= outer.y - 0.001F);
    CHECK(inner.x + inner.width <= outer.x + outer.width + 0.001F);
    CHECK(inner.y + inner.height <= outer.y + outer.height + 0.001F);
}

// Literal coordinates independently evaluated from the reviewed design table
// and decimal breakpoint calculations. The test does not call a production
// layout helper to build its expected rows, margins, widths or heights.
struct LayoutCase {
    UiPoint size;
    bool cabinet, cheeks;
    float margin, content_width, player_width, rack_width, gap, rail_width;
    float keyboard_x, keyboard_width, cabinet_x, cabinet_width;
    std::array<float, 8> row_top, row_height;
};

constexpr std::array<LayoutCase, 12> kLayoutCases{{
    {{960, 700}, false, false, 16, 928, 928, 460, 8, 156, 180, 764, 0, 0,
     {16, 106, 190, 366, 402, 492, 582, 648}, {82, 76, 168, 28, 82, 82, 58, 36}},
    {{1280, 900}, false, true, 16, 1248, 1248, 620, 8, 168, 192, 1072, 0, 0,
     {16, 106, 214, 438, 474, 620, 766, 848}, {82, 100, 216, 28, 138, 138, 74, 36}},
    {{1672, 941}, true, true, 71.896F, 1528.208F, 1059.7456F, 524.8728F, 10, 158.96184F,
     240.85784F, 890.78376F, 1141.6416F, 458.4624F,
     {16, 116, 230.92F, 466.76F, 504.76F, 653.24F, 801.72F, 889},
     {90, 104.92F, 225.84F, 28, 138.48F, 138.48F, 77.28F, 36}},
    {{1399, 819}, false, false, 16, 1367, 1367, 679.5F, 8, 168, 192, 1191, 0, 0,
     {16, 106, 204.28F, 408.84F, 444.84F, 568.16F, 691.48F, 767},
     {82, 90.28F, 196.56F, 28, 115.32F, 115.32F, 67.52F, 36}},
    {{1400, 819}, true, false, 60.2F, 1279.6F, 887.72F, 439.86F, 8, 156,
     224.2F, 723.72F, 955.92F, 383.88F,
     {16, 106, 204.28F, 408.84F, 444.84F, 568.16F, 691.48F, 767},
     {82, 90.28F, 196.56F, 28, 115.32F, 115.32F, 67.52F, 36}},
    {{1399, 820}, false, true, 16, 1367, 1367, 679.5F, 8, 168, 192, 1191, 0, 0,
     {16, 106, 204.4F, 409.2F, 445.2F, 568.8F, 692.4F, 768},
     {82, 90.4F, 196.8F, 28, 115.6F, 115.6F, 67.6F, 36}},
    {{1400, 820}, true, true, 60.2F, 1279.6F, 885.72F, 437.86F, 10, 156,
     226.2F, 719.72F, 955.92F, 383.88F,
     {16, 116, 216.4F, 423.2F, 461.2F, 575.8F, 690.4F, 768},
     {90, 90.4F, 196.8F, 28, 104.6F, 104.6F, 67.6F, 36}},
    {{1920, 700}, true, false, 72, 1776, 1235.2F, 613.6F, 8, 168,
     248, 1059.2F, 1315.2F, 532.8F,
     {16, 106, 190, 366, 402, 492, 582, 648}, {82, 76, 168, 28, 82, 82, 58, 36}},
    {{1920, 1080}, true, true, 72, 1776, 1233.2F, 611.6F, 10, 168,
     250, 1055.2F, 1315.2F, 532.8F,
     {16, 116, 236, 482, 520, 726, 932, 1028}, {90, 110, 236, 28, 196, 196, 86, 36}},
    {{8192, 700}, true, false, 72, 8048, 5625.6F, 2808.8F, 8, 168,
     248, 5449.6F, 5705.6F, 2414.4F,
     {16, 106, 190, 366, 402, 492, 582, 648}, {82, 76, 168, 28, 82, 82, 58, 36}},
    {{960, 8192}, false, true, 16, 928, 928, 460, 8, 156, 180, 764, 0, 0,
     {16, 106, 224, 468, 504, 4275, 8046, 8140}, {82, 110, 236, 28, 3763, 3763, 86, 36}},
    {{8192, 8192}, true, true, 72, 8048, 5623.6F, 2806.8F, 10, 168,
     250, 5445.6F, 5705.6F, 2414.4F,
     {16, 116, 236, 482, 520, 4282, 8044, 8140}, {90, 110, 236, 28, 3752, 3752, 86, 36}},
}};

void check_reference_regions(const UiLayout& layout, const LayoutCase& expected) {
    CHECK(layout.show_cabinet == expected.cabinet);
    CHECK(layout.bank_controls_in_cheeks == expected.cheeks);
    near_rect(layout.header, {expected.margin, expected.row_top[0], expected.content_width, expected.row_height[0]});
    near_rect(layout.performance_panel,
              {expected.margin, expected.row_top[1], expected.player_width, expected.row_height[1]});
    near_rect(layout.keyboard_toolbar,
              {expected.margin, expected.row_top[3], expected.player_width, expected.row_height[3]});
    near_rect(layout.pedal_panel,
              {expected.margin, expected.row_top[6], expected.player_width, expected.row_height[6]});
    near_rect(layout.footer, {expected.margin, expected.row_top[7], expected.content_width, expected.row_height[7]});
    CHECK_NEAR(layout.footer.y + layout.footer.height, expected.size.y - 16, 0.001F);
    for (std::size_t manual = 0; manual < 2; ++manual) {
        near_rect(layout.registration_panels[manual],
                  {expected.margin + static_cast<float>(manual) * (expected.rack_width + expected.gap),
                   expected.row_top[2], expected.rack_width, expected.row_height[2]});
        near_rect(layout.manual_panels[manual],
                  {expected.keyboard_x, expected.row_top[4 + manual], expected.keyboard_width, expected.row_height[4 + manual]});
        near_rect(layout.manual_rail_panels[manual],
                  {expected.margin, expected.row_top[4 + manual], expected.rail_width, expected.row_height[4 + manual]});
        near_rect(layout.preset_key_panels[manual],
                  {expected.margin + 8, expected.row_top[4 + manual] + (expected.cheeks ? 54 : 22),
                   expected.rail_width - 16, expected.row_height[4 + manual] - (expected.cheeks ? 62 : 30)});
    }
    if (expected.cabinet) {
        near_rect(layout.cabinet_panel,
                  {expected.cabinet_x, expected.row_top[1], expected.cabinet_width,
                   expected.row_top[6] + expected.row_height[6] - expected.row_top[1]});
        contained(layout.cabinet_art, layout.cabinet_panel);
        CHECK_NEAR(layout.cabinet_art.width / layout.cabinet_art.height, 466.0F / 397.0F, 0.00001F);
        CHECK_NEAR(layout.cabinet_art.y, layout.cabinet_panel.y + 38, 0.001F);
        CHECK(layout.cabinet_art.y + layout.cabinet_art.height + 176 <=
              layout.cabinet_panel.y + layout.cabinet_panel.height + 0.001F);
        CHECK(ui_hit_test(layout, {layout.cabinet_art.x + layout.cabinet_art.width / 2,
                                  layout.cabinet_art.y + layout.cabinet_art.height / 2}).kind == UiControlKind::None);
        if (expected.size.x == 1672) {
            near_rect(layout.cabinet_art, {1153.6416F, 154, 434.4624F, 370.13213F});
        }
        if (expected.size.y == 700 && expected.size.x >= 1920) {
            CHECK_NEAR(layout.cabinet_art.height, 320, 0.001F);
            CHECK_NEAR(layout.cabinet_art.width, 375.6171F, 0.001F);
        }
    } else {
        CHECK(same_rect(layout.cabinet_panel, {}) && same_rect(layout.cabinet_art, {}));
    }
}

void check_control_regions(const UiLayout& layout) {
    std::array<std::size_t, 20> kinds{};
    for (std::size_t index = 0; index < layout.control_count; ++index) {
        const auto& entry = layout.controls[index];
        ++kinds[static_cast<std::size_t>(entry.id.kind)];
        UiRect parent;
        switch (entry.id.kind) {
        case UiControlKind::EditBank:
            parent = layout.bank_controls_in_cheeks ?
                layout.manual_rail_panels[static_cast<std::size_t>(entry.id.manual)] :
                layout.registration_panels[static_cast<std::size_t>(entry.id.manual)];
            CHECK(entry.bounds.height == (layout.bank_controls_in_cheeks ? 24 : 26));
            break;
        case UiControlKind::PresetKey:
            parent = layout.preset_key_panels[static_cast<std::size_t>(entry.id.manual)];
            CHECK(entry.id.bank == DrawbarBank::A && entry.id.index < 12);
            CHECK(entry.label_bounds.height == 11);
            CHECK(empty(entry.value_bounds) && empty(entry.track));
            break;
        case UiControlKind::ManualDrawbar:
            parent = layout.registration_panels[static_cast<std::size_t>(entry.id.manual)];
            CHECK(entry.track.width == 4 && entry.track.height >= 28);
            break;
        case UiControlKind::Percussion:
        case UiControlKind::Expression:
        case UiControlKind::PedalDrawbar:
            parent = layout.performance_panel;
            if (entry.id.kind == UiControlKind::Percussion) CHECK(entry.bounds.height == 42);
            if (entry.id.kind == UiControlKind::PedalDrawbar) CHECK(entry.track.width == 4 && entry.track.height >= 24);
            if (entry.id.kind == UiControlKind::Expression) CHECK(entry.track.height == 4 && entry.track.width > 100);
            break;
        case UiControlKind::KeyboardTarget:
        case UiControlKind::OctaveDown:
        case UiControlKind::OctaveUp:
            parent = layout.keyboard_toolbar;
            CHECK(entry.bounds.height == 28);
            break;
        default:
            parent = layout.header;
            CHECK(entry.bounds.height == (layout.show_cabinet ? 42 : 32));
            break;
        }
        contained(entry.bounds, parent);
        contained(entry.label_bounds, entry.bounds);
        if (!empty(entry.value_bounds)) {
            contained(entry.value_bounds, entry.bounds);
            CHECK(!overlaps(entry.label_bounds, entry.value_bounds));
        }
        if (!empty(entry.track)) {
            contained(entry.track, entry.bounds);
            CHECK(!overlaps(entry.label_bounds, entry.track));
            CHECK(!overlaps(entry.value_bounds, entry.track));
        }
        for (std::size_t other = 0; other < index; ++other) {
            CHECK(entry.id != layout.controls[other].id);
            const auto& previous = layout.controls[other];
            if (entry.id.kind != UiControlKind::PresetKey || previous.id.kind != UiControlKind::PresetKey) {
                CHECK(!overlaps(entry.bounds, previous.bounds));
            }
        }
        for (const auto& manual : layout.manual_keys) {
            for (const auto& key : manual) CHECK(!overlaps(entry.bounds, key.bounds));
        }
        for (const auto& key : layout.pedal_keys) CHECK(!overlaps(entry.bounds, key.bounds));
    }
    constexpr std::array<std::size_t, 20> expected_kinds{
        0, 4, 0, 0, 18, 2, 4, 1, 3, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 24};
    CHECK(kinds == expected_kinds);

    for (const auto manual : {Manual::Upper, Manual::Lower}) {
        const auto& source = layout.bank_controls_in_cheeks ?
            layout.manual_rail_panels[static_cast<std::size_t>(manual)] :
            layout.registration_panels[static_cast<std::size_t>(manual)];
        const auto edit_a = geometry(layout, {UiControlKind::EditBank, manual, DrawbarBank::A});
        const auto edit_b = geometry(layout, {UiControlKind::EditBank, manual, DrawbarBank::B});
        if (layout.bank_controls_in_cheeks) {
            CHECK_NEAR(edit_a.bounds.x, source.x + 8, 0.001F);
            CHECK_NEAR(edit_b.bounds.x + edit_b.bounds.width, source.x + source.width - 8, 0.001F);
            CHECK_NEAR(edit_a.bounds.y, source.y + 22, 0.001F);
            CHECK_NEAR(edit_b.bounds.y, source.y + 22, 0.001F);
            CHECK_NEAR(edit_a.bounds.width, (source.width - 20) / 2, 0.001F);
            CHECK_NEAR(edit_b.bounds.x, edit_a.bounds.x + edit_a.bounds.width + 4, 0.001F);
        } else {
            CHECK_NEAR(edit_a.bounds.x, source.x + 12, 0.001F);
            CHECK_NEAR(edit_b.bounds.x, edit_a.bounds.x + edit_a.bounds.width + 4, 0.001F);
            for (const auto& control : {edit_a, edit_b}) {
                CHECK_NEAR(control.bounds.y, source.y + 28, 0.001F);
                CHECK_NEAR(control.bounds.width, 76, 0.001F);
            }
        }
    }
}

void check_preset_keys(const UiLayout& layout) {
    constexpr std::array<std::uint8_t, 7> naturals{0, 2, 4, 5, 7, 9, 11};
    constexpr std::array<std::uint8_t, 5> sharps{1, 3, 6, 8, 10};
    for (const auto manual : {Manual::Upper, Manual::Lower}) {
        const auto division = static_cast<std::size_t>(manual);
        const auto& panel = layout.preset_key_panels[division];
        CHECK(panel.width >= 140 && panel.width <= 152);
        CHECK(panel.height >= 42.59F);
        for (std::uint8_t index = 0; index < 12; ++index) {
            const auto identity = preset_key(manual, index);
            const auto& entry = layout.controls[8 + division * 23 + index];
            CHECK(entry.id == identity); // EDIT A, EDIT B, C..B, drawbars.
            near_rect(entry.label_bounds,
                      {entry.bounds.x + 1, entry.bounds.y + entry.bounds.height - 13,
                       entry.bounds.width - 2, 11});
            std::uint32_t parameter = 0;
            CHECK(ui_parameter_id(identity, parameter));
            CHECK(parameter == (manual == Manual::Upper ? 20480U : 20481U));
        }
        for (std::size_t ordinal = 0; ordinal < naturals.size(); ++ordinal) {
            const auto id = preset_key(manual, naturals[ordinal]);
            const auto box = geometry(layout, id).bounds;
            const float left = panel.x + panel.width * static_cast<float>(ordinal) / 7;
            const float right = panel.x + panel.width * static_cast<float>(ordinal + 1) / 7;
            near_rect(box, {left, panel.y, right - left, panel.height});
            const float y = box.y + box.height * 0.9F;
            CHECK(ui_hit_test(layout, {box.x, y}) == id);
            CHECK(ui_hit_test(layout, {box.x + box.width / 2, y}) == id);
            if (ordinal != 0) {
                CHECK(ui_hit_test(layout, {std::nextafter(box.x, -INFINITY), y}) ==
                      preset_key(manual, naturals[ordinal - 1]));
            }
        }
        for (const auto index : sharps) {
            const auto id = preset_key(manual, index);
            const auto box = geometry(layout, id).bounds;
            CHECK(box.width >= 12 && box.height >= 26.41F);
            const auto next = geometry(layout, preset_key(manual, static_cast<std::uint8_t>(index + 1))).bounds;
            near_rect(box, {next.x - panel.width * 0.30F / 7, panel.y,
                           panel.width * 0.60F / 7, panel.height * 0.62F});
            CHECK(ui_hit_test(layout, {box.x, box.y}) == id);
            CHECK(ui_hit_test(layout, {box.x + box.width / 2, box.y + box.height / 2}) == id);
            CHECK(ui_hit_test(layout, {box.x + box.width, box.y + 1}) ==
                  preset_key(manual, static_cast<std::uint8_t>(index + 1)));
            CHECK(ui_hit_test(layout, {box.x + box.width * 0.75F, box.y + box.height}) ==
                  preset_key(manual, static_cast<std::uint8_t>(index + 1)));
        }
        CHECK(ui_hit_test(layout, {panel.x - 1, panel.y}).kind == UiControlKind::None);
        CHECK(ui_hit_test(layout, {panel.x + panel.width, panel.y + panel.height * 0.9F}).kind == UiControlKind::None);
        CHECK(ui_hit_test(layout, {panel.x, panel.y + panel.height}).kind == UiControlKind::None);
    }
}

void layout_and_hit_boundaries() {
    // Independent complete piano spelling: no call to the production accidental
    // helper, no modulo pitch formula, and no reuse of the playing-key table.
    constexpr std::array<int, 36> manual_naturals{
        36, 38, 40, 41, 43, 45, 47, 48, 50, 52, 53, 55, 57, 59, 60, 62, 64, 65,
        67, 69, 71, 72, 74, 76, 77, 79, 81, 83, 84, 86, 88, 89, 91, 93, 95, 96};
    constexpr std::array<int, 25> manual_accidentals{
        37, 39, 42, 44, 46, 49, 51, 54, 56, 58, 61, 63, 66, 68, 70, 73, 75, 78,
        80, 82, 85, 87, 90, 92, 94};
    constexpr std::array<int, 15> pedal_naturals{1, 3, 5, 6, 8, 10, 12, 13, 15, 17, 18, 20, 22, 24, 25};
    constexpr std::array<int, 10> pedal_accidentals{2, 4, 7, 9, 11, 14, 16, 19, 21, 23};
    for (const auto& expected : kLayoutCases) {
        const auto size = expected.size;
        UiLayout layout;
        CHECK(make_ui_layout(size.x, size.y, {DrawbarBank::A, DrawbarBank::B}, layout));
        CHECK(layout.width == size.x && layout.height == size.y && layout.control_count == 64);
        check_reference_regions(layout, expected);
        check_keyboard(layout, layout.manual_keys[0], UiTarget::Upper, layout.manual_panels[0], manual_naturals, manual_accidentals);
        check_keyboard(layout, layout.manual_keys[1], UiTarget::Lower, layout.manual_panels[1], manual_naturals, manual_accidentals);
        check_keyboard(layout, layout.pedal_keys, UiTarget::Pedals, layout.pedal_panel, pedal_naturals, pedal_accidentals);
        check_control_regions(layout);
        check_preset_keys(layout);
        std::size_t visible_drawbars = 0;
        for (std::size_t index = 0; index < layout.control_count; ++index) {
            const auto& entry = layout.controls[index];
            CHECK(entry.bounds.width > 0 && entry.bounds.height >= 24);
            CHECK(ui_hit_test(layout, {entry.bounds.x + entry.bounds.width / 2,
                                      entry.bounds.y + entry.bounds.height / 2}) == entry.id);
            CHECK(entry.bounds.x >= 0 && entry.bounds.y >= 0);
            CHECK(entry.bounds.x + entry.bounds.width <= size.x && entry.bounds.y + entry.bounds.height <= size.y);
            if (entry.id.kind == UiControlKind::ManualDrawbar) {
                ++visible_drawbars;
                CHECK(entry.id.bank == (entry.id.manual == Manual::Upper ? DrawbarBank::A : DrawbarBank::B));
            }
        }
        CHECK(visible_drawbars == 18);
        if (size.x == 960 && size.y == 700) {
            near_rect(geometry(layout, {UiControlKind::SaveControls}).bounds, {16, 50, 72, 32});
            near_rect(geometry(layout, {UiControlKind::Help}).bounds, {172, 50, 72, 32});
            near_rect(geometry(layout, {UiControlKind::MidiSettings}).bounds, {794, 50, 72, 32});
            near_rect(geometry(layout, {UiControlKind::Panic}).bounds, {872, 50, 72, 32});
            near_rect(layout.manual_keys[0][0].bounds, {188, 424, 20.777778F, 52});
            near_rect(layout.pedal_keys[0].bounds, {24, 604, 60.8F, 28});
            near_rect(geometry(layout, {UiControlKind::Percussion}).bounds, {28, 130, 94.72F, 42});
            const auto drawbar = geometry(layout, {UiControlKind::ManualDrawbar, Manual::Upper, DrawbarBank::A, 0});
            near_rect(drawbar.bounds, {30, 250, 44.444444F, 100});
            near_rect(drawbar.label_bounds, {30, 250, 44.444444F, 24});
            near_rect(drawbar.value_bounds, {30, 334, 44.444444F, 16});
            near_rect(drawbar.track, {50.222222F, 288, 4, 28});
            near_rect(geometry(layout, {UiControlKind::Expression}).track, {474.88F, 146, 184.4352F, 4});
            near_rect(geometry(layout, {UiControlKind::PedalDrawbar}).track, {726.25216F, 142, 4, 24});
        }
        if (size.x == 1280 && size.y == 900) {
            near_rect(geometry(layout, {UiControlKind::AudioSettings}).bounds, {1036, 50, 72, 32});
            near_rect(geometry(layout, {UiControlKind::EditBank, Manual::Upper}).bounds, {24, 496, 74, 24});
            near_rect(geometry(layout, preset_key(Manual::Lower, 0)).bounds, {24, 674, 21.714286F, 76});
            near_rect(layout.manual_keys[0][0].bounds, {200, 496, 29.333333F, 108});
        }
        if (size.x == 1672) {
            near_rect(geometry(layout, {UiControlKind::SaveControls}).bounds, {71.896F, 46, 112, 42});
            near_rect(geometry(layout, {UiControlKind::Help}).bounds, {311.896F, 46, 112, 42});
            near_rect(geometry(layout, {UiControlKind::MidiSettings}).bounds, {1412.104F, 46, 90, 42});
            near_rect(geometry(layout, {UiControlKind::Panic}).bounds, {1510.104F, 46, 90, 42});
        }
    }
    UiLayout layout;
    CHECK(make_ui_layout(1280, 900, {DrawbarBank::A, DrawbarBank::B}, layout));
    const auto before = layout;
    const float nan = std::numeric_limits<float>::quiet_NaN();
    for (const UiPoint invalid : {UiPoint{959, 900}, UiPoint{1280, 699}, UiPoint{8193, 900},
                                 UiPoint{1280, 8193}, UiPoint{0, 0}, UiPoint{-1, 900},
                                 UiPoint{INFINITY, 900}, UiPoint{1280, -INFINITY},
                                 UiPoint{nan, 900}, UiPoint{1280, nan}}) {
        CHECK(!make_ui_layout(invalid.x, invalid.y, {DrawbarBank::B, DrawbarBank::B}, layout));
        equal_layout(layout, before);
    }
    CHECK(!make_ui_layout(1280, 900, {static_cast<DrawbarBank>(2), DrawbarBank::A}, layout));
    equal_layout(layout, before);
    CHECK(ui_hit_test(layout, {nan, 0}).kind == UiControlKind::None);
    CHECK(ui_hit_test(layout, {0, INFINITY}).kind == UiControlKind::None);
    CHECK((!UiRect{0, 0, 0, 10}.contains({0, 0})));
    CHECK((!UiRect{0, 0, 10, -1}.contains({0, 0})));
}

void breakpoint_resize_preserves_performance() {
    Rig rig;
    CHECK(rig.model.resize(1399, 819));
    CHECK(rig.model.activate({UiControlKind::EditBank, Manual::Upper, DrawbarBank::A}).count == 0);
    CHECK(tap(rig.model, UiKey::RightBracket).count == 0);
    CHECK(rig.model.view().manual_base_midi == 72);
    rig.dispatch(rig.model.key({UiKey::A, true}));
    const SessionCommand external_on = PerformanceInputEvent{
        HostNoteEvent{0, HostNoteKind::On, 0, 1, 72, 127, 700}};
    CHECK(rig.session.post(external_on).ok());
    const SessionCommand external_pedal_on = PerformanceInputEvent{
        PedalNoteEvent{0, PedalNoteKind::On, 0, 3, PedalId{25}, 127, 701}};
    CHECK(rig.session.post(external_pedal_on).ok());
    rig.flush();

    const UiControlId drawbar{UiControlKind::ManualDrawbar, Manual::Upper, DrawbarBank::A, 0};
    constexpr std::array<UiPoint, 7> transitions{{
        {1400, 819}, {1400, 820}, {1399, 820}, {1399, 819}, {1672, 941}, {1920, 700}, {960, 700}}};
    std::uint8_t value = 0;
    for (const auto next : transitions) {
        const auto bar = geometry(rig.model, drawbar);
        value = value == 8 ? 0 : 8;
        const UiPoint point{bar.track.x + 1,
                            value == 0 ? bar.track.y : bar.track.y + bar.track.height};
        rig.dispatch(rig.model.pointer({UiPointerKind::Down, point}));
        CHECK(rig.model.view().pointer_captured && rig.model.view().focus == drawbar);
        CHECK(rig.model.view().controls_pending && rig.model.view().controls.drawbars[0][0][0] == value);
        const auto controls_before = rig.model.view().controls;
        const bool dirty_before = rig.model.view().controls_dirty;
        const auto applied_before = rig.model.view().applied;
        CHECK(rig.model.resize(next.x, next.y));
        CHECK(rig.model.view().controls == controls_before);
        CHECK(rig.model.view().controls_pending && rig.model.view().controls_dirty == dirty_before);
        CHECK(rig.model.view().applied.publication_revision == applied_before.publication_revision);
        CHECK(rig.model.view().focus == drawbar && rig.model.view().pointer_captured);
        CHECK(rig.model.view().edited_banks[0] == DrawbarBank::A && rig.model.view().manual_base_midi == 72);
        const auto moved = geometry(rig.model, drawbar);
        CHECK(rig.model.pointer({UiPointerKind::Move,
            {moved.track.x + 1, value == 0 ? moved.track.y + moved.track.height : moved.track.y}}).count == 0);
        CHECK(rig.model.view().controls == controls_before); // A resize closes the captured parameter gesture.
        CHECK(rig.model.pointer({UiPointerKind::Up, {-100, -100}}).count == 0);
        rig.flush();
        CHECK(!rig.model.view().controls_pending && rig.model.view().applied.controls == controls_before);
        CHECK(rig.model.view().applied.held_keys[0][36] && rig.model.view().applied.held_pedals[24]);
        CHECK(rig.model.view().applied.recovery_count == 0);
    }
    const auto original_off = rig.model.key({UiKey::A, false});
    manual_event(original_off, 0, false, 0, 72, 1);
    rig.dispatch(original_off);
    rig.flush();
    CHECK(rig.model.view().applied.held_keys[0][36]); // External ownership survives the original UI release.
    const SessionCommand external_off = PerformanceInputEvent{
        HostNoteEvent{0, HostNoteKind::Off, 0, 1, 72, 0, 700}};
    CHECK(rig.session.post(external_off).ok());
    const SessionCommand external_pedal_off = PerformanceInputEvent{
        PedalNoteEvent{0, PedalNoteKind::Off, 0, 3, PedalId{25}, 0, 701}};
    CHECK(rig.session.post(external_pedal_off).ok());
    rig.flush();
    CHECK(!rig.model.view().applied.held_keys[0][36] && !rig.model.view().applied.held_pedals[24]);
}

void preset_activation_and_navigation() {
    Rig rig;
    auto initial = rig.model.view().controls;
    initial.drawbars[0][0][0] = 2;
    initial.drawbars[0][1][0] = 3;
    initial.drawbars[1][0][0] = 4;
    initial.drawbars[1][1][0] = 5;
    initial.pedal_drawbars = {6, 7};
    initial.percussion.enabled = true;
    rig.dispatch(rig.model.load_controls(initial));
    rig.dispatch(rig.model.key({UiKey::A, true}));
    CHECK(rig.session.post(PerformanceInputEvent{
        HostNoteEvent{0, HostNoteKind::On, 1, 2, 65, 127, 700}}).ok());
    CHECK(rig.session.post(PerformanceInputEvent{
        PedalNoteEvent{0, PedalNoteKind::On, 0, 3, PedalId{13}, 127, 701}}).ok());
    rig.flush();
    const auto held_before = rig.model.view().applied;
    const auto edited_before = rig.model.view().edited_banks;
    const auto roving_before = rig.model.view().roving_manual_keys;
    const auto check_holds = [&rig, &held_before]() {
        CHECK(rig.model.view().applied.held_keys == held_before.held_keys);
        CHECK(rig.model.view().applied.held_pedals == held_before.held_pedals);
        CHECK(rig.model.view().applied.frame_clock == held_before.frame_clock);
        CHECK(rig.model.view().applied.recovery_count == 0);
    };

    for (const auto manual : {Manual::Upper, Manual::Lower}) {
        const auto division = static_cast<std::size_t>(manual);
        for (std::uint8_t index = 0; index < 12; ++index) {
            const auto id = preset_key(manual, index);
            auto expected = rig.model.view().controls;
            if (index == 0) expected.route_enabled[division] = false;
            else if (index <= 9) {
                expected.fixed_registrations[division] = static_cast<FixedRegistration>(index);
                expected.route_enabled[division] = true;
            } else {
                expected.selected_banks[division] = index == 10 ? DrawbarBank::A : DrawbarBank::B;
                expected.fixed_registrations[division] = FixedRegistration::None;
                expected.route_enabled[division] = true;
            }
            const auto box = geometry(rig.model, id).bounds;
            const UiPoint point{box.x + box.width / 2, box.y + box.height * 0.9F};
            const auto applied_before = rig.model.view().applied.controls;
            const auto pressed = rig.model.pointer({UiPointerKind::Down, point});
            CHECK(controls(pressed) == expected);
            CHECK(rig.model.view().focus == id && !rig.model.view().pointer_captured);
            CHECK(rig.model.view().controls_pending && rig.model.view().applied.controls == applied_before);
            CHECK(rig.model.pointer({UiPointerKind::Down, point}).count == 0);
            CHECK(rig.model.pointer({UiPointerKind::Move, key_point(rig.model, manual_key(manual, 60))}).count == 0);
            CHECK(rig.model.pointer({UiPointerKind::Up, point}).count == 0);
            CHECK(rig.model.pointer({UiPointerKind::CaptureLost, point}).count == 0);
            rig.dispatch(pressed);
            rig.flush();
            CHECK(rig.model.view().controls == expected && !rig.model.view().controls_pending);
            check_holds();

            // Every semantic key also activates from the keyboard, even when
            // the explicit selection reasserts the already applied state.
            const auto key = index % 2 == 0 ? UiKey::Space : UiKey::Enter;
            const auto activated = rig.model.key({key, true});
            CHECK(controls(activated) == expected);
            CHECK(rig.model.key({key, true, true}).count == 0);
            CHECK(rig.model.key({key, true}).count == 0);
            CHECK(rig.model.key({key, false}).count == 0);
            rig.dispatch(activated);
            rig.flush();
            check_holds();
            CHECK(rig.model.view().edited_banks == edited_before);
            CHECK(rig.model.view().roving_manual_keys == roving_before);
            CHECK(rig.model.view().keyboard_target == UiTarget::Upper);
        }
    }
    CHECK(!rig.model.view().controls_dirty); // Both returned to the saved B banks.
    const auto before_navigation = rig.model.view().controls;
    CHECK(tap(rig.model, UiKey::Home).count == 0 && rig.model.view().focus == preset_key(Manual::Lower, 0));
    CHECK(tap(rig.model, UiKey::Left).count == 0 && rig.model.view().focus == preset_key(Manual::Lower, 0));
    CHECK(tap(rig.model, UiKey::Right).count == 0 && rig.model.view().focus == preset_key(Manual::Lower, 1));
    CHECK(tap(rig.model, UiKey::Up).count == 0 && rig.model.view().focus == preset_key(Manual::Upper, 1));
    CHECK(tap(rig.model, UiKey::Up).count == 0 && rig.model.view().focus == preset_key(Manual::Upper, 1));
    CHECK(tap(rig.model, UiKey::Down).count == 0 && rig.model.view().focus == preset_key(Manual::Lower, 1));
    CHECK(tap(rig.model, UiKey::Down).count == 0 && rig.model.view().focus == preset_key(Manual::Lower, 1));
    CHECK(tap(rig.model, UiKey::End).count == 0 && rig.model.view().focus == preset_key(Manual::Lower, 11));
    CHECK(tap(rig.model, UiKey::Right).count == 0 && rig.model.view().focus == preset_key(Manual::Lower, 11));
    CHECK(rig.model.view().controls == before_navigation && !rig.model.view().controls_pending);
    for (const UiPoint size : {UiPoint{1399, 819}, UiPoint{1400, 820}, UiPoint{960, 700}}) {
        CHECK(rig.model.resize(size.x, size.y));
        CHECK(rig.model.view().focus == preset_key(Manual::Lower, 11));
        CHECK(rig.model.view().controls == before_navigation);
        check_holds();
    }

    rig.dispatch(rig.model.activate(preset_key(Manual::Upper, 9)));
    rig.flush();
    rig.model.mark_saved(rig.model.view().controls);
    rig.dispatch(rig.model.activate(preset_key(Manual::Upper, 0)));
    rig.flush();
    CHECK(rig.model.view().controls.fixed_registrations[0] == FixedRegistration::A);
    CHECK(!rig.model.view().controls.route_enabled[0] && rig.model.view().controls_dirty);
    check_holds();
    rig.dispatch(rig.model.activate({UiControlKind::SoundingBank, Manual::Upper, DrawbarBank::B}));
    rig.flush();
    CHECK(rig.model.view().controls.fixed_registrations[0] == FixedRegistration::None);
    CHECK(rig.model.view().controls.route_enabled[0]);
    check_holds();
    const auto released = rig.model.key({UiKey::A, false});
    manual_event(released, 0, false, 0, 60, 1);
    rig.dispatch(released);
    rig.flush();
    CHECK(!rig.model.view().applied.held_keys[0][24]);
    CHECK(rig.model.view().applied.held_keys[1][29] && rig.model.view().applied.held_pedals[12]);
}

void focus_and_app_actions() {
    UiModel model;
    CHECK(model.layout().width == 1280 && model.layout().height == 900);
    for (std::size_t index = 0; index < 64; ++index) {
        CHECK(tap(model, UiKey::Tab).count == 0);
        CHECK(model.view().focus == model.layout().controls[index].id);
    }
    CHECK(tap(model, UiKey::Tab).count == 0 && model.view().focus == manual_key(Manual::Upper, 60));
    CHECK(tap(model, UiKey::Home).count == 0 && model.view().focus == manual_key(Manual::Upper, 36));
    CHECK(tap(model, UiKey::Left).count == 0 && model.view().focus == manual_key(Manual::Upper, 36));
    CHECK(tap(model, UiKey::Up).count == 0 && model.view().focus == manual_key(Manual::Upper, 48));
    CHECK(tap(model, UiKey::Right).count == 0 && model.view().focus == manual_key(Manual::Upper, 49));
    CHECK(tap(model, UiKey::Tab).count == 0 && model.view().focus == manual_key(Manual::Lower, 60));
    CHECK(tap(model, UiKey::Tab).count == 0 && model.view().focus == pedal_key(1));
    CHECK(tap(model, UiKey::End).count == 0 && model.view().focus == pedal_key(25));
    CHECK(tap(model, UiKey::Up).count == 0 && model.view().focus == pedal_key(25));
    CHECK(tap(model, UiKey::Tab).count == 0 && model.view().focus.kind == UiControlKind::SaveControls);
    CHECK(tap(model, UiKey::Tab, true).count == 0 && model.view().focus == pedal_key(25));
    CHECK(tap(model, UiKey::Tab, true).count == 0 && model.view().focus == manual_key(Manual::Lower, 60));
    CHECK(tap(model, UiKey::Tab, true).count == 0 && model.view().focus == manual_key(Manual::Upper, 49));
    model.set_text_entry_active(true);
    CHECK(tap(model, UiKey::Right).count == 0 && model.view().focus == manual_key(Manual::Upper, 49));
    model.set_text_entry_active(false);
    struct RequestCase { UiControlKind kind; UiAppRequest request; };
    constexpr std::array<RequestCase, 5> requests{{
        {UiControlKind::SaveControls, UiAppRequest::SaveControls},
        {UiControlKind::LoadControls, UiAppRequest::LoadControls},
        {UiControlKind::AudioSettings, UiAppRequest::AudioSettings},
        {UiControlKind::Help, UiAppRequest::Help},
        {UiControlKind::MidiSettings, UiAppRequest::MidiSettings}}};
    for (const auto& entry : requests) {
        const auto action = model.activate({entry.kind});
        CHECK(action.count == 1 && std::get<UiAppRequest>(action.items[0]) == entry.request);
        const auto keyboard = tap(model, UiKey::Enter);
        CHECK(keyboard.count == 1 && std::get<UiAppRequest>(keyboard.items[0]) == entry.request);
    }
    const auto escape = tap(model, UiKey::Escape);
    CHECK(escape.count == 1 && std::holds_alternative<ReleaseUiNotes>(command(escape)));
    const auto close = model.release_ui(UiReleaseReason::WindowClosing);
    CHECK(close.count == 1 && std::holds_alternative<ReleaseUiNotes>(command(close)));
}
} // namespace

int main() {
    registry_and_retained_banks();
    physical_keys_and_release_identity();
    pointer_audition_and_scoped_release();
    drag_identity_and_parameter_laws();
    pending_saved_and_recovery();
    layout_and_hit_boundaries();
    breakpoint_resize_preserves_performance();
    preset_activation_and_navigation();
    focus_and_app_actions();
    std::cout << "Standalone UI acceptance: 9 behavioral scenarios passed\n";
}
