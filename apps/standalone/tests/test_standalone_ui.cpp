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

constexpr UiControlId manual_key(Manual manual, std::uint8_t midi) {
    return {UiControlKind::ManualKey, manual, DrawbarBank::A,
            static_cast<std::uint8_t>(midi - 36)};
}

constexpr UiControlId pedal_key(std::uint8_t pedal) {
    return {UiControlKind::PedalKey, Manual::Upper, DrawbarBank::A,
            static_cast<std::uint8_t>(pedal - 1)};
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

UiControlGeometry geometry(const UiModel& model, UiControlId id) {
    for (std::size_t index = 0; index < model.layout().control_count; ++index) {
        if (model.layout().controls[index].id == id) return model.layout().controls[index];
    }
    hammond_test::fail("visible control exists", __FILE__, __LINE__);
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
    constexpr std::array<ParameterCase, 9> remaining{{
        {{UiControlKind::Expression}, 8192},
        {{UiControlKind::SoundingBank, Manual::Upper, DrawbarBank::A}, 8208},
        {{UiControlKind::SoundingBank, Manual::Lower, DrawbarBank::B}, 8209},
        {{UiControlKind::Percussion, Manual::Upper, DrawbarBank::A, 0}, 12288},
        {{UiControlKind::Percussion, Manual::Upper, DrawbarBank::A, 1}, 12289},
        {{UiControlKind::Percussion, Manual::Upper, DrawbarBank::A, 2}, 12290},
        {{UiControlKind::Percussion, Manual::Upper, DrawbarBank::A, 3}, 12291},
        {{UiControlKind::PedalDrawbar, Manual::Upper, DrawbarBank::A, 0}, 16384},
        {{UiControlKind::PedalDrawbar, Manual::Upper, DrawbarBank::A, 1}, 16385}}};
    for (const auto& entry : remaining) {
        std::uint32_t actual = 0;
        CHECK(ui_parameter_id(entry.control, actual) && actual == entry.id);
        CHECK(seen.insert(actual).second);
    }
    CHECK(seen.size() == 45 && parameter_descriptors().size() == 45);
    for (const auto& descriptor : parameter_descriptors()) CHECK(seen.contains(descriptor.id));
    for (const auto kind : {UiControlKind::EditBank, UiControlKind::CancelManual,
                           UiControlKind::Panic, UiControlKind::SaveControls,
                           UiControlKind::ManualKey, UiControlKind::PedalKey}) {
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
    constexpr std::array<UiControlId, 6> malformed{{
        {UiControlKind::ManualDrawbar, static_cast<Manual>(9)},
        {UiControlKind::ManualDrawbar, Manual::Upper, static_cast<DrawbarBank>(9)},
        {UiControlKind::ManualDrawbar, Manual::Upper, DrawbarBank::A, 9},
        {UiControlKind::PedalDrawbar, Manual::Upper, DrawbarBank::A, 2},
        {UiControlKind::Expression, Manual::Lower},
        {static_cast<UiControlKind>(255)}}};
    for (const auto id : malformed) {
        std::uint32_t unchanged = 999;
        CHECK(!ui_parameter_id(id, unchanged) && unchanged == 999);
        CHECK(model.activate(id).count == 0 && model.view().controls == before);
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
    CHECK(same_rect(a.header, b.header) && same_rect(a.performance_panel, b.performance_panel));
    CHECK(same_rect(a.keyboard_toolbar, b.keyboard_toolbar) && same_rect(a.pedal_panel, b.pedal_panel));
    CHECK(same_rect(a.footer, b.footer));
    for (std::size_t manual = 0; manual < 2; ++manual) {
        CHECK(same_rect(a.registration_panels[manual], b.registration_panels[manual]));
        CHECK(same_rect(a.manual_panels[manual], b.manual_panels[manual]));
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
    constexpr std::array<UiPoint, 6> sizes{{{960, 700}, {1280, 900}, {1920, 1080},
                                        {1119, 819}, {1120, 820}, {8192, 8192}}};
    for (const auto size : sizes) {
        UiLayout layout;
        CHECK(make_ui_layout(size.x, size.y, {DrawbarBank::A, DrawbarBank::B}, layout));
        CHECK(layout.width == size.x && layout.height == size.y && layout.control_count == 45);
        check_keyboard(layout, layout.manual_keys[0], UiTarget::Upper, layout.manual_panels[0], manual_naturals, manual_accidentals);
        check_keyboard(layout, layout.manual_keys[1], UiTarget::Lower, layout.manual_panels[1], manual_naturals, manual_accidentals);
        check_keyboard(layout, layout.pedal_keys, UiTarget::Pedals, layout.pedal_panel, pedal_naturals, pedal_accidentals);
        std::size_t visible_drawbars = 0;
        for (std::size_t index = 0; index < layout.control_count; ++index) {
            const auto& entry = layout.controls[index];
            CHECK(entry.bounds.width > 0 && entry.bounds.height >= 32);
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
        if (size.x == 1280) CHECK(layout.manual_panels[0].height == 146);
        if (size.x == 960) CHECK(layout.manual_panels[0].height == 86);
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

void focus_and_app_actions() {
    UiModel model;
    for (std::size_t index = 0; index < 45; ++index) {
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
    constexpr std::array<RequestCase, 4> requests{{
        {UiControlKind::SaveControls, UiAppRequest::SaveControls},
        {UiControlKind::LoadControls, UiAppRequest::LoadControls},
        {UiControlKind::AudioSettings, UiAppRequest::AudioSettings},
        {UiControlKind::Help, UiAppRequest::Help}}};
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
    focus_and_app_actions();
    std::cout << "Standalone UI acceptance: 7 behavioral scenarios passed\n";
}
