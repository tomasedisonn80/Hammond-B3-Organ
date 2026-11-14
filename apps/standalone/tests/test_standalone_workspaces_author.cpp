#include "TestSupport.h"
#include "UiModel.h"

#include <array>
#include <cmath>
#include <iostream>
#include <limits>
#include <variant>

namespace {
using namespace hammond;
using namespace hammond::standalone;

constexpr UiControlId workspace_id(UiWorkspace workspace) {
    return {UiControlKind::Workspace, Manual::Upper, DrawbarBank::A,
            static_cast<std::uint8_t>(workspace)};
}

constexpr UiControlId upper_key{UiControlKind::ManualKey, Manual::Upper, DrawbarBank::A, 24};
constexpr UiControlId upper_drawbar{UiControlKind::ManualDrawbar, Manual::Upper, DrawbarBank::B, 0};

UiActions tap(UiModel& model, UiKey key, bool shift = false) {
    const auto actions = model.key({key, true, false, shift});
    CHECK(model.key({key, false}).count == 0);
    return actions;
}

UiControlGeometry geometry(const UiModel& model, UiControlId control) {
    for (const auto& item : model.layout().controls) {
        if (item.id == control) return item;
    }
    hammond_test::fail("control geometry exists", __FILE__, __LINE__);
}

UiPoint center(UiRect rectangle) {
    return {rectangle.x + rectangle.width * 0.5F, rectangle.y + rectangle.height * 0.5F};
}

UiPoint playing_point(const UiModel& model) {
    const auto& quad = model.layout().manual_keys[0][24].hit;
    const float fraction = 0.9F;
    const float left = quad.points[0].x + (quad.points[3].x - quad.points[0].x) * fraction;
    const float right = quad.points[1].x + (quad.points[2].x - quad.points[1].x) * fraction;
    return {(left + right) * 0.5F,
            quad.points[0].y + (quad.points[3].y - quad.points[0].y) * fraction};
}

void manual_event(const UiActions& actions, bool down, std::uint8_t bus,
                  std::uint8_t note, std::int32_t owner) {
    CHECK(actions.count == 1);
    CHECK(std::holds_alternative<SessionCommand>(actions.items[0]));
    const auto& command = std::get<SessionCommand>(actions.items[0]);
    CHECK(std::holds_alternative<PerformanceInputEvent>(command));
    const auto& input = std::get<PerformanceInputEvent>(command);
    CHECK(std::holds_alternative<HostNoteEvent>(input));
    const auto& event = std::get<HostNoteEvent>(input);
    CHECK(event.kind == (down ? HostNoteKind::On : HostNoteKind::Off));
    CHECK(event.bus == bus && event.midi_note == note && event.note_id == owner);
}

void inventory_and_invalid_admission() {
    UiModel model;
    CHECK(model.view().workspace == UiWorkspace::Play);
    CHECK(model.view().presentation == UiPresentation::Dimensional);
    CHECK(model.view().focus.kind == UiControlKind::None);
    CHECK(model.layout().control_count == 68);
    for (const auto workspace : {UiWorkspace::Play, UiWorkspace::Rotary, UiWorkspace::Service}) {
        CHECK(model.set_workspace(workspace));
        std::size_t visible = 0;
        for (const auto& item : model.layout().controls) {
            if (ui_control_visible(model.layout(), item.id)) ++visible;
        }
        CHECK(visible == (workspace == UiWorkspace::Play ? 68U : 10U));
        CHECK(ui_control_visible(model.layout(), upper_key) == (workspace == UiWorkspace::Play));
        CHECK(!ui_control_visible(model.layout(), {UiControlKind::SoundingBank}));
        const auto before = model.view();
        std::uint32_t parameter = 123456U;
        CHECK(!ui_parameter_id(workspace_id(workspace), parameter) && parameter == 123456U);
        CHECK(!ui_parameter_id({UiControlKind::Presentation}, parameter) && parameter == 123456U);
        CHECK(!model.set_workspace(static_cast<UiWorkspace>(255)));
        CHECK(!model.set_presentation(static_cast<UiPresentation>(255)));
        CHECK(model.view().workspace == before.workspace && model.view().focus == before.focus);
        CHECK(model.view().controls == before.controls && model.view().workspace_focus == before.workspace_focus);
        for (const auto malformed : {
                UiControlId{UiControlKind::Workspace, Manual::Lower},
                UiControlId{UiControlKind::Workspace, Manual::Upper, DrawbarBank::B},
                UiControlId{UiControlKind::Workspace, Manual::Upper, DrawbarBank::A, 3},
                UiControlId{UiControlKind::Presentation, Manual::Upper, DrawbarBank::A, 1}}) {
            CHECK(!ui_control_visible(model.layout(), malformed));
            CHECK(model.activate(malformed).count == 0 && model.view().focus == before.focus);
        }
        auto destination = model.layout();
        CHECK(!make_ui_layout(1280, 900, model.view().edited_banks, destination,
                              static_cast<UiWorkspace>(3), UiPresentation::Flat));
        CHECK(destination.workspace == workspace && destination.presentation == UiPresentation::Dimensional);
    }
    CHECK(model.set_workspace(UiWorkspace::Play));
    CHECK(model.activate(upper_drawbar).count == 0);
    const auto before = model.view();
    CHECK(model.activate({UiControlKind::ManualDrawbar, Manual::Upper, DrawbarBank::A, 0}).count == 0);
    CHECK(model.view().focus == before.focus && model.view().controls == before.controls);
}

void focus_order_and_memory() {
    for (const auto workspace : {UiWorkspace::Play, UiWorkspace::Rotary, UiWorkspace::Service}) {
        UiModel model;
        CHECK(model.set_workspace(workspace));
        if (workspace == UiWorkspace::Play) CHECK(tap(model, UiKey::Tab).count == 0);
        const auto initial = model.view().focus;
        const std::size_t count = workspace == UiWorkspace::Play ? 71 : 10;
        std::array<UiControlId, 71> seen{};
        for (std::size_t index = 0; index < count; ++index) {
            seen[index] = model.view().focus;
            CHECK(ui_control_visible(model.layout(), seen[index]));
            for (std::size_t previous = 0; previous < index; ++previous) CHECK(!(seen[index] == seen[previous]));
            CHECK(tap(model, UiKey::Tab).count == 0);
        }
        CHECK(model.view().focus == initial);
        for (std::size_t index = count; index > 0; --index) {
            CHECK(tap(model, UiKey::Tab, true).count == 0);
            CHECK(model.view().focus == seen[index - 1]);
        }
    }
    UiModel model;
    CHECK(model.activate(upper_key).count == 0);
    CHECK(tap(model, UiKey::Right).count == 0);
    const auto remembered = model.view().focus;
    const auto rotary_tab = center(geometry(model, workspace_id(UiWorkspace::Rotary)).bounds);
    CHECK(model.pointer({UiPointerKind::Down, rotary_tab}).count == 0);
    CHECK(model.view().workspace == UiWorkspace::Rotary);
    CHECK(model.view().workspace_focus[0] == remembered);
    CHECK(model.pointer({UiPointerKind::Up, {}}).count == 0);
    CHECK(model.activate({UiControlKind::Help}).count == 1);
    CHECK(model.set_workspace(UiWorkspace::Service));
    CHECK(model.set_workspace(UiWorkspace::Play));
    CHECK(model.view().focus == remembered && model.view().roving_manual_keys[0] == remembered.index);
    CHECK(model.activate(workspace_id(UiWorkspace::Play)).count == 0);
    CHECK(model.view().focus == remembered);
    const auto before_flat = model.view().workspace_focus;
    CHECK(model.activate({UiControlKind::Presentation}).count == 0);
    CHECK(model.view().presentation == UiPresentation::Flat);
    CHECK(model.view().focus == remembered && model.view().workspace_focus == before_flat);
    CHECK(model.pointer({UiPointerKind::Down,
                         center(geometry(model, {UiControlKind::Presentation}).bounds)}).count == 0);
    CHECK(model.view().presentation == UiPresentation::Dimensional);
    CHECK(model.view().focus == remembered && model.view().workspace_focus == before_flat);
    CHECK(model.pointer({UiPointerKind::Up, {}}).count == 0);
    CHECK(model.set_workspace(UiWorkspace::Rotary));
    CHECK(model.view().focus.kind == UiControlKind::Help);
    const auto memories = model.view().workspace_focus;
    CHECK(model.set_presentation(UiPresentation::Flat));
    CHECK(model.resize(960, 700));
    CHECK(model.view().focus.kind == UiControlKind::Help && model.view().workspace_focus == memories);
}

void hidden_controls_and_shortcuts() {
    UiModel model;
    const auto body_point = playing_point(model);
    const auto initial_controls = model.view().controls;
    CHECK(tap(model, UiKey::F5).count == 0 && model.view().workspace == UiWorkspace::Rotary);
    for (const auto control : {upper_key, upper_drawbar, UiControlId{UiControlKind::CancelManual},
            UiControlId{UiControlKind::SoundingBank}, UiControlId{UiControlKind::PresetKey},
            UiControlId{UiControlKind::Expression}, UiControlId{UiControlKind::KeyboardTarget}}) {
        const auto focus = model.view().focus;
        CHECK(model.activate(control).count == 0 && model.view().focus == focus);
    }
    CHECK(ui_hit_test(model.layout(), body_point).kind == UiControlKind::None);
    CHECK(model.pointer({UiPointerKind::Down, body_point}).count == 0);
    CHECK(tap(model, UiKey::F4).count == 0);
    CHECK(model.pointer({UiPointerKind::Move, playing_point(model)}).count == 0);
    CHECK(model.pointer({UiPointerKind::Down, playing_point(model)}).count == 0);
    CHECK(model.pointer({UiPointerKind::Up, {}}).count == 0);
    CHECK(tap(model, UiKey::F6, true).count == 0 && model.view().workspace == UiWorkspace::Service);
    CHECK(tap(model, UiKey::F2).count == 0);
    manual_event(model.key({UiKey::A, true}), true, 1, 60, kUiKeyboardOwnerBase);
    CHECK(tap(model, UiKey::F4).count == 0);
    CHECK(tap(model, UiKey::F3).count == 0);
    model.set_text_entry_active(true);
    manual_event(model.key({UiKey::A, false, false, false, true}), false, 1, 60, kUiKeyboardOwnerBase);
    CHECK(tap(model, UiKey::F5).count == 0 && model.view().workspace == UiWorkspace::Play);
    model.set_text_entry_active(false);
    CHECK(model.key({UiKey::F7, true, false, false, true}).count == 0);
    CHECK(model.key({UiKey::F7, true}).count == 0);
    CHECK(model.view().presentation == UiPresentation::Dimensional);
    CHECK(model.key({UiKey::F7, false}).count == 0);
    CHECK(tap(model, UiKey::F7).count == 0 && model.view().presentation == UiPresentation::Flat);
    CHECK(model.view().controls == initial_controls);
    CHECK(!model.view().controls_dirty && !model.view().controls_pending);
}

void held_pointer_and_space_ownership() {
    UiModel model;
    manual_event(model.pointer({UiPointerKind::Down, playing_point(model)}), true, 0, 60, kUiPointerOwnerId);
    CHECK(model.set_workspace(UiWorkspace::Service));
    CHECK(model.view().pointer_captured);
    CHECK(model.pointer({UiPointerKind::Move, {0, 0}}).count == 0);
    CHECK(model.set_workspace(UiWorkspace::Play));
    CHECK(model.set_presentation(UiPresentation::Flat));
    CHECK(model.resize(1400, 900));
    CHECK(model.view().pointer_captured);
    CHECK(model.pointer({UiPointerKind::Move, {0, 0}}).count == 0);
    manual_event(model.pointer({UiPointerKind::Up, {0, 0}}), false, 0, 60, kUiPointerOwnerId);
    CHECK(!model.view().pointer_captured);
    CHECK(model.activate(upper_key).count == 0);
    manual_event(model.key({UiKey::Space, true}), true, 0, 60, kUiAuditionOwnerId);
    CHECK(model.set_workspace(UiWorkspace::Rotary));
    CHECK(tap(model, UiKey::F2).count == 0);
    model.set_text_entry_active(true);
    manual_event(model.key({UiKey::Space, false}), false, 0, 60, kUiAuditionOwnerId);
    model.set_text_entry_active(false);
    CHECK(model.key({UiKey::Space, true}).count == 0);
    CHECK(model.key({UiKey::Space, false}).count == 0);
}

void drag_closure_and_idempotence() {
    for (const int transition : {0, 1, 2}) {
        UiModel model;
        const auto track = geometry(model, upper_drawbar).track;
        (void)model.pointer({UiPointerKind::Down, {track.x + 2.0F, track.y}});
        CHECK(model.view().pointer_captured);
        CHECK(model.set_workspace(UiWorkspace::Play));
        CHECK(model.set_presentation(UiPresentation::Dimensional));
        CHECK(!model.resize(1, 1));
        CHECK(!model.set_workspace(static_cast<UiWorkspace>(17)));
        CHECK(model.pointer({UiPointerKind::Move, {track.x + 2.0F, track.y + track.height}}).count == 1);
        const auto before = model.view();
        if (transition == 0) CHECK(model.set_workspace(UiWorkspace::Service));
        if (transition == 1) CHECK(model.set_presentation(UiPresentation::Flat));
        if (transition == 2) CHECK(model.resize(1400, 900));
        CHECK(model.set_workspace(UiWorkspace::Play));
        CHECK(model.pointer({UiPointerKind::Move, playing_point(model)}).count == 0);
        CHECK(model.pointer({UiPointerKind::Move, {track.x, track.y}}).count == 0);
        CHECK(model.view().controls == before.controls);
        CHECK(model.view().controls_dirty == before.controls_dirty);
        CHECK(model.view().controls_pending == before.controls_pending);
        CHECK(model.pointer({UiPointerKind::Up, {}}).count == 0);
        manual_event(model.pointer({UiPointerKind::Down, playing_point(model)}), true, 0, 60, kUiPointerOwnerId);
        manual_event(model.pointer({UiPointerKind::CaptureLost, {}}), false, 0, 60, kUiPointerOwnerId);
    }
}

void shared_quad_boundaries() {
    UiQuad quad;
    quad.points = {{{2, 3}, {8, 3}, {10, 9}, {0, 9}}};
    CHECK(quad.contains({2, 3}) && quad.contains({5, 6}));
    CHECK(!quad.contains({8, 3}) && !quad.contains({5, 9}));
    CHECK(!quad.contains({0, 3}) && !quad.contains({10, 6}));
    CHECK(!quad.contains({std::numeric_limits<float>::infinity(), 6}));
    auto invalid = quad;
    invalid.points[2].y = 8;
    CHECK(!invalid.contains({5, 6}));
    invalid = quad;
    invalid.points[0].x = std::numeric_limits<float>::quiet_NaN();
    CHECK(!invalid.contains({5, 6}));
    CHECK(!UiQuad{}.contains({0, 0}));
}
} // namespace

int main() {
    inventory_and_invalid_admission();
    focus_order_and_memory();
    hidden_controls_and_shortcuts();
    held_pointer_and_space_ownership();
    drag_closure_and_idempotence();
    shared_quad_boundaries();
    std::cout << "Workspace author checks: 6 behavioral scenarios passed\n";
}
