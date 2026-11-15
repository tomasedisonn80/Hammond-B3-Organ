#include "MidiInput.h"
#include "TestSupport.h"
#include "UiModel.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <limits>
#include <tuple>
#include <variant>

// Independent host-free acceptance of retained percussion behavior and the
// admitted whole-reference active allocation. Oracles use contract literals.
// Painting, font/raster containment and physical devices have separate gates.
namespace {
using namespace hammond;
using namespace hammond::standalone;

constexpr std::array<std::uint8_t, 4> kReferenceOrder{0, 2, 3, 1};
constexpr std::array<std::uint8_t, 4> kLegacyOrder{0, 1, 2, 3};
constexpr std::array<std::uint32_t, 4> kParameters{0x3000, 0x3001, 0x3002, 0x3003};
constexpr std::array<DrawbarBank, 2> kBanks{DrawbarBank::B, DrawbarBank::B};

constexpr UiControlId percussion(std::uint8_t index) {
    return {UiControlKind::Percussion, Manual::Upper, DrawbarBank::A, index};
}

constexpr UiControlId preset(std::uint8_t index) {
    return {UiControlKind::PresetKey, Manual::Upper, DrawbarBank::A, index};
}

UiPoint center(UiRect rectangle) {
    return {rectangle.x + rectangle.width * 0.5F, rectangle.y + rectangle.height * 0.5F};
}

const UiControlGeometry& geometry(const UiLayout& layout, UiControlId id) {
    for (std::size_t index = 0; index < layout.control_count; ++index)
        if (layout.controls[index].id == id) return layout.controls[index];
    hammond_test::fail("semantic control has geometry", __FILE__, __LINE__);
}

void same_rect(UiRect actual, UiRect expected) {
    CHECK(std::tie(actual.x, actual.y, actual.width, actual.height) ==
          std::tie(expected.x, expected.y, expected.width, expected.height));
}

void near_rect(UiRect actual, UiRect expected) {
    CHECK_NEAR(actual.x, expected.x, 0.002F);
    CHECK_NEAR(actual.y, expected.y, 0.002F);
    CHECK_NEAR(actual.width, expected.width, 0.002F);
    CHECK_NEAR(actual.height, expected.height, 0.002F);
}

bool overlaps(UiRect a, UiRect b) {
    return a.width > 0 && a.height > 0 && b.width > 0 && b.height > 0 &&
        a.x < b.x + b.width && b.x < a.x + a.width &&
        a.y < b.y + b.height && b.y < a.y + a.height;
}

void contained(UiRect child, UiRect parent) {
    CHECK(std::isfinite(child.x) && std::isfinite(child.y));
    CHECK(std::isfinite(child.width) && std::isfinite(child.height));
    CHECK(child.width > 0 && child.height > 0);
    CHECK(child.x >= parent.x - 0.002F && child.y >= parent.y - 0.002F);
    CHECK(child.x + child.width <= parent.x + parent.width + 0.002F);
    CHECK(child.y + child.height <= parent.y + parent.height + 0.002F);
}

void same_control(const UiControlGeometry& actual, const UiControlGeometry& expected) {
    CHECK(actual.id == expected.id);
    same_rect(actual.bounds, expected.bounds);
    same_rect(actual.label_bounds, expected.label_bounds);
    same_rect(actual.value_bounds, expected.value_bounds);
    same_rect(actual.track, expected.track);
}

void same_layout(const UiLayout& a, const UiLayout& b) {
    CHECK(std::tie(a.width, a.height, a.show_cabinet, a.bank_controls_in_cheeks,
                   a.sidebar_pedals, a.control_count, a.workspace, a.presentation) ==
          std::tie(b.width, b.height, b.show_cabinet, b.bank_controls_in_cheeks,
                   b.sidebar_pedals, b.control_count, b.workspace, b.presentation));
    const std::array<UiRect, 8> a_panels{a.header, a.performance_panel, a.keyboard_toolbar,
        a.pedal_panel, a.footer, a.cabinet_panel, a.cabinet_art, a.workspace_panel};
    const std::array<UiRect, 8> b_panels{b.header, b.performance_panel, b.keyboard_toolbar,
        b.pedal_panel, b.footer, b.cabinet_panel, b.cabinet_art, b.workspace_panel};
    for (std::size_t index = 0; index < a_panels.size(); ++index) same_rect(a_panels[index], b_panels[index]);
    const auto same_key = [](const UiKeyGeometry& x, const UiKeyGeometry& y) {
        CHECK(x.note == y.note && x.accidental == y.accidental);
        same_rect(x.bounds, y.bounds);
        const std::array<UiQuad, 3> x_quads{x.hit, x.top, x.front}, y_quads{y.hit, y.top, y.front};
        for (std::size_t quad = 0; quad < x_quads.size(); ++quad)
            for (std::size_t point = 0; point < 4; ++point) {
                CHECK(x_quads[quad].points[point].x == y_quads[quad].points[point].x);
                CHECK(x_quads[quad].points[point].y == y_quads[quad].points[point].y);
            }
    };
    for (std::size_t manual = 0; manual < 2; ++manual) {
        same_rect(a.registration_panels[manual], b.registration_panels[manual]);
        same_rect(a.manual_panels[manual], b.manual_panels[manual]);
        same_rect(a.manual_rail_panels[manual], b.manual_rail_panels[manual]);
        same_rect(a.preset_key_panels[manual], b.preset_key_panels[manual]);
        for (std::size_t key = 0; key < 61; ++key) same_key(a.manual_keys[manual][key], b.manual_keys[manual][key]);
    }
    for (std::size_t key = 0; key < 25; ++key) same_key(a.pedal_keys[key], b.pedal_keys[key]);
    for (std::size_t control = 0; control < a.controls.size(); ++control)
        same_control(a.controls[control], b.controls[control]);
}

void require_order(const UiLayout& layout, const std::array<std::uint8_t, 4>& expected) {
    std::size_t found = 0;
    for (std::size_t ordinal = 0; ordinal < layout.control_count; ++ordinal) {
        const auto id = layout.controls[ordinal].id;
        if (id.kind != UiControlKind::Percussion) continue;
        CHECK(found < expected.size() && id == percussion(expected[found]));
        std::uint32_t parameter = 0;
        CHECK(ui_parameter_id(id, parameter) && parameter == kParameters[expected[found]]);
        ++found;
    }
    CHECK(found == 4 && layout.control_count == 68);
    CHECK(layout.manual_keys[0].size() + layout.manual_keys[1].size() + layout.pedal_keys.size() == 147);
    CHECK(parameter_descriptors().size() == 47);
}

void targets_and_clearance(const UiLayout& layout, bool exterior) {
    const auto& order = exterior ? kReferenceOrder : kLegacyOrder;
    require_order(layout, order);
    const bool visible = layout.workspace == UiWorkspace::Play;
    for (std::size_t slot = 0; slot < order.size(); ++slot) {
        const auto id = percussion(order[slot]);
        const auto& cap = geometry(layout, id);
        const auto box = cap.bounds;
        const auto middle = center(box);
        CHECK(ui_control_visible(layout, id) == visible);
        contained(box, layout.performance_panel);
        contained(cap.value_bounds, box);
        same_rect(cap.track, {});
        const float last_x = std::nextafter(box.x + box.width, box.x);
        const float last_y = std::nextafter(box.y + box.height, box.y);
        for (const UiPoint hit : {UiPoint{box.x, box.y}, middle,
                                  UiPoint{last_x, box.y}, UiPoint{box.x, last_y}, UiPoint{last_x, last_y}})
            CHECK(ui_hit_test(layout, hit) == (visible ? id : UiControlId{}));
        for (const UiPoint miss : {UiPoint{box.x + box.width, middle.y},
                                   UiPoint{middle.x, box.y + box.height},
                                   UiPoint{std::nextafter(box.x, -1.0F), middle.y},
                                   UiPoint{middle.x, std::nextafter(box.y, -1.0F)}})
            CHECK(ui_hit_test(layout, miss).kind == UiControlKind::None);
        if (exterior) {
            contained(cap.label_bounds, layout.performance_panel);
            const long double sx = static_cast<long double>(layout.width / 1672.0F);
            const long double sy = static_cast<long double>(layout.height / 941.0F);
            CHECK_NEAR(cap.label_bounds.y - (box.y + box.height), 4.0L * sy, 0.002F);
            CHECK_NEAR(cap.label_bounds.height, 14.0L * sy, 0.002F);
            CHECK_NEAR(cap.label_bounds.x - box.x, -2.0L * sx, 0.002F);
            CHECK_NEAR(cap.label_bounds.width - box.width, 4.0L * sx, 0.002F);
            CHECK_NEAR(cap.value_bounds.x - box.x, 5.0L * sx, 0.002F);
            CHECK_NEAR(cap.value_bounds.y - box.y, 6.0L * sy, 0.002F);
            CHECK_NEAR(box.width - cap.value_bounds.width, 10.0L * sx, 0.002F);
            CHECK_NEAR(box.height - cap.value_bounds.height, 14.0L * sy, 0.002F);
            CHECK_NEAR(layout.performance_panel.y + layout.performance_panel.height -
                       cap.label_bounds.y - cap.label_bounds.height, 17.0L * sy, 0.002F);
            for (const UiPoint miss : {center(cap.label_bounds),
                                       UiPoint{cap.label_bounds.x, cap.label_bounds.y},
                                       UiPoint{middle.x, box.y + box.height + 1.0F}})
                CHECK(ui_hit_test(layout, miss).kind == UiControlKind::None);
        } else {
            contained(cap.label_bounds, box);
        }
        for (const auto& neighbor : layout.controls) {
            if (neighbor.id == id) continue;
            CHECK(!overlaps(box, neighbor.bounds));
            if (exterior) CHECK(!overlaps(cap.label_bounds, neighbor.bounds));
        }
        if (slot + 1 < order.size()) {
            const auto& next = geometry(layout, percussion(order[slot + 1]));
            CHECK(box.x + box.width < next.bounds.x);
            CHECK(ui_hit_test(layout, {(box.x + box.width + next.bounds.x) * 0.5F, middle.y}).kind ==
                  UiControlKind::None);
            if (exterior) CHECK(cap.label_bounds.x + cap.label_bounds.width < next.label_bounds.x);
        }
    }
}

void frozen_geometry_and_predicate() {
    // Canonical cap endpoints are independent of the production mapper. Use
    // binary32 scale, then long-double arithmetic for the 0.002-unit oracle.
    constexpr std::array<UiPoint, 8> anchors{{
        {1400, 820}, {1672, 941}, {1920, 1080}, {1400.25F, 820.25F},
        {1672.5F, 941.25F}, {8192, 820}, {1400, 8192}, {8192, 8192}}};
    constexpr std::array<long double, 4> lefts{164, 256, 337, 418};
    for (const auto size : anchors) {
        UiLayout layout;
        CHECK(make_ui_layout(size.x, size.y, kBanks, layout));
        const long double sx = static_cast<long double>(size.x / 1672.0F);
        const long double sy = static_cast<long double>(size.y / 941.0F);
        for (std::size_t slot = 0; slot < kReferenceOrder.size(); ++slot)
            near_rect(geometry(layout, percussion(kReferenceOrder[slot])).bounds,
                      {static_cast<float>(lefts[slot] * sx), static_cast<float>(177 * sy),
                       static_cast<float>(74 * sx), static_cast<float>(52 * sy)});
        targets_and_clearance(layout, true);
    }

    struct Inactive { UiPoint size; UiPresentation presentation; float width, top; std::array<float, 4> left; };
    // Literal old-layout landmarks also detect a broadened active predicate.
    constexpr std::array<Inactive, 4> inactive{{
        {{1399, 820}, UiPresentation::Dimensional, 145.205F, 130, {28, 181.205F, 334.410F, 487.615F}},
        {{1400, 819}, UiPresentation::Dimensional, 90.0878F, 130, {72.2F, 170.2878F, 268.3756F, 366.4634F}},
        {{1280, 900}, UiPresentation::Dimensional, 131.52F, 130, {28, 167.52F, 307.04F, 446.56F}},
        {{1672, 941}, UiPresentation::Flat, 107.937561F, 150, {83.896F, 199.833561F, 315.771122F, 431.708683F}}}};
    for (const auto& entry : inactive) {
        UiLayout layout;
        CHECK(make_ui_layout(entry.size.x, entry.size.y, kBanks, layout, UiWorkspace::Play, entry.presentation));
        for (std::size_t slot = 0; slot < kLegacyOrder.size(); ++slot)
            near_rect(geometry(layout, percussion(kLegacyOrder[slot])).bounds,
                      {entry.left[slot], entry.top, entry.width, 42});
        targets_and_clearance(layout, false);
    }
    const float below_width = std::nextafter(1400.0F, 0.0F);
    const float below_height = std::nextafter(820.0F, 0.0F);
    struct Boundary { UiPoint size; bool active; };
    const std::array<Boundary, 5> boundaries{{
        {{below_width, 820}, false}, {{1400, below_height}, false},
        {{1400.25F, 820.25F}, true}, {{1672.5F, 941.25F}, true}, {{8191.75F, 8191.5F}, true}}};
    for (const auto& entry : boundaries) {
        UiLayout layout;
        CHECK(make_ui_layout(entry.size.x, entry.size.y, kBanks, layout));
        targets_and_clearance(layout, entry.active);
    }

    UiLayout active, flat;
    CHECK(make_ui_layout(1672, 941, kBanks, active));
    CHECK(make_ui_layout(1672, 941, kBanks, flat, UiWorkspace::Play, UiPresentation::Flat));
    // Only the active allocation changes; semantic identity and parameter
    // mapping remain the same across the legacy Flat presentation.
    near_rect(active.performance_panel, {72, 125, 1044, 139});
    near_rect(active.header, {72, 10, 1528, 102});
    near_rect(active.keyboard_toolbar, {1140, 614, 448, 64});
    near_rect(active.pedal_panel, {1138, 752, 450, 110});
    near_rect(active.footer, {48, 889, 1556, 36});
    near_rect(active.cabinet_panel, {1126, 125, 478, 745});
    for (const auto& control : active.controls) {
        const auto& other = geometry(flat, control.id);
        std::uint32_t active_parameter = 0, flat_parameter = 0;
        CHECK(ui_parameter_id(control.id, active_parameter) ==
              ui_parameter_id(other.id, flat_parameter));
        CHECK(active_parameter == flat_parameter);
    }
    CHECK(ui_hit_test(active, {200, 146}).kind == UiControlKind::None); // Heading.
    CHECK(ui_hit_test(active, {200, 255}).kind == UiControlKind::None); // Eligibility.
    for (const auto workspace : {UiWorkspace::Rotary, UiWorkspace::Service}) {
        UiLayout hidden;
        CHECK(make_ui_layout(1672, 941, kBanks, hidden, workspace));
        targets_and_clearance(hidden, false);
        for (const auto index : kLegacyOrder) same_control(geometry(hidden, percussion(index)), geometry(flat, percussion(index)));
    }
}

void invalid_layout_is_transactional() {
    UiLayout layout;
    CHECK(make_ui_layout(1672, 941, kBanks, layout));
    const auto before = layout;
    const float infinity = std::numeric_limits<float>::infinity();
    const float nan = std::numeric_limits<float>::quiet_NaN();
    const std::array<UiPoint, 8> invalid{{{nan, 941}, {1672, nan}, {infinity, 941}, {1672, -infinity},
        {959.75F, 941}, {1672, 699.75F}, {std::nextafter(8192.0F, infinity), 941},
        {1672, std::nextafter(8192.0F, infinity)}}};
    for (const auto size : invalid) {
        CHECK(!make_ui_layout(size.x, size.y, kBanks, layout));
        same_layout(layout, before);
    }
    for (std::size_t manual = 0; manual < 2; ++manual) {
        auto invalid_banks = kBanks;
        invalid_banks[manual] = static_cast<DrawbarBank>(2);
        CHECK(!make_ui_layout(1672, 941, invalid_banks, layout));
        same_layout(layout, before);
    }
    CHECK(!make_ui_layout(1672, 941, kBanks, layout, static_cast<UiWorkspace>(3)));
    same_layout(layout, before);
    CHECK(!make_ui_layout(1672, 941, kBanks, layout, UiWorkspace::Play, static_cast<UiPresentation>(2)));
    same_layout(layout, before);
}

UiActions tap(UiModel& model, UiKey key, bool shift = false) {
    const auto result = model.key({key, true, false, shift});
    CHECK(model.key({key, false}).count == 0);
    return result;
}

void focus(UiModel& model, UiControlId target) {
    for (unsigned attempt = 0; attempt < 71 && model.view().focus != target; ++attempt)
        CHECK(tap(model, UiKey::Tab).count == 0);
    CHECK(model.view().focus == target);
}

const SessionCommand& command(const UiActions& actions) {
    CHECK(actions.count == 1 && std::holds_alternative<SessionCommand>(actions.items[0]));
    return std::get<SessionCommand>(actions.items[0]);
}

void expected_edit(const UiActions& actions, const ControlSnapshot& expected) {
    CHECK(std::holds_alternative<ControlSnapshot>(command(actions)));
    CHECK(std::get<ControlSnapshot>(command(actions)) == expected);
}

ControlSnapshot seeded_controls() {
    ControlSnapshot result;
    result.drawbars[0][0] = {1, 2, 3, 4, 5, 6, 7, 8, 0};
    result.drawbars[0][1] = {8, 7, 6, 5, 4, 3, 2, 1, 0};
    result.drawbars[1][0] = {2, 0, 4, 0, 6, 0, 8, 0, 1};
    result.drawbars[1][1] = {0, 7, 0, 5, 0, 3, 0, 1, 0};
    result.expression = 0.375;
    result.pedal_drawbars = {3, 7};
    result.fixed_registrations[1] = FixedRegistration::G;
    return result;
}

ControlSnapshot toggled(ControlSnapshot expected, std::uint8_t semantic_index) {
    switch (semantic_index) {
    case 0: expected.percussion.enabled = !expected.percussion.enabled; break;
    case 1: expected.percussion.harmonic = expected.percussion.harmonic == PercussionHarmonic::Second ?
        PercussionHarmonic::Third : PercussionHarmonic::Second; break;
    case 2: expected.percussion.volume = expected.percussion.volume == PercussionVolume::Normal ?
        PercussionVolume::Soft : PercussionVolume::Normal; break;
    case 3: expected.percussion.decay = expected.percussion.decay == PercussionDecay::Slow ?
        PercussionDecay::Fast : PercussionDecay::Slow; break;
    default: hammond_test::fail("known percussion semantic index", __FILE__, __LINE__);
    }
    return expected;
}

void pointer_keyboard_domains_and_repeats() {
    UiModel model;
    CHECK(model.resize(1672, 941));
    const auto seeded = seeded_controls();
    expected_edit(model.load_controls(seeded), seeded);
    const auto applied_before = model.view().applied.controls;
    for (const auto index : kReferenceOrder) {
        const auto id = percussion(index);
        const auto& cap = geometry(model.layout(), id);
        for (unsigned direction = 0; direction < 2; ++direction) {
            const auto expected = toggled(model.view().controls, index);
            expected_edit(model.pointer({UiPointerKind::Down, center(cap.bounds)}), expected);
            CHECK(model.view().controls == expected && model.view().focus == id);
            CHECK(model.view().controls_pending && model.view().applied.controls == applied_before);
            CHECK(!model.view().pointer_captured);
            CHECK(model.pointer({UiPointerKind::Down, center(cap.bounds)}).count == 0);
            CHECK(model.pointer({UiPointerKind::Down, center(geometry(model.layout(), percussion(0)).bounds)}).count == 0);
            CHECK(model.pointer({UiPointerKind::Move, center(cap.label_bounds)}).count == 0);
            CHECK(model.pointer({UiPointerKind::Up, {-100, -100}}).count == 0);
            CHECK(model.view().controls == expected);
        }
        for (const auto key : {UiKey::Space, UiKey::Enter}) {
            for (unsigned direction = 0; direction < 2; ++direction) {
                const auto expected = toggled(model.view().controls, index);
                expected_edit(model.key({key, true}), expected);
                CHECK(model.key({key, true, true}).count == 0);
                CHECK(model.key({key, true}).count == 0);
                CHECK(model.key({key, false}).count == 0);
                CHECK(model.view().focus == id && model.view().controls == expected);
            }
            CHECK(model.key({key, true, true}).count == 0); // Orphan repeat is not a press.
            CHECK(model.key({key, false}).count == 0);
        }
        for (const auto key : {UiKey::Left, UiKey::Right, UiKey::Up, UiKey::Down, UiKey::Home, UiKey::End}) {
            CHECK(tap(model, key).count == 0);
            CHECK(model.view().focus == id && model.view().controls == seeded);
        }
        CHECK(model.pointer({UiPointerKind::Down, center(cap.label_bounds)}).count == 0);
        CHECK(model.pointer({UiPointerKind::Up, center(cap.label_bounds)}).count == 0);
        CHECK(model.view().controls == seeded);
    }
}

void tab_cycle_and_semantic_reflow() {
    UiModel model;
    CHECK(model.resize(1672, 941));
    const auto controls = model.view().controls;
    std::array<UiControlId, 71> cycle{};
    for (std::size_t ordinal = 0; ordinal < cycle.size(); ++ordinal) {
        CHECK(tap(model, UiKey::Tab).count == 0);
        cycle[ordinal] = model.view().focus;
        CHECK(std::find(cycle.begin(), cycle.begin() + static_cast<std::ptrdiff_t>(ordinal), cycle[ordinal]) ==
              cycle.begin() + static_cast<std::ptrdiff_t>(ordinal));
        CHECK(ui_control_visible(model.layout(), cycle[ordinal]));
    }
    CHECK(cycle.front() == (UiControlId{UiControlKind::Workspace}));
    CHECK(cycle[55] == (UiControlId{UiControlKind::ManualDrawbar, Manual::Lower, DrawbarBank::B, 8}));
    CHECK(cycle[56] == percussion(0) && cycle[57] == percussion(2));
    CHECK(cycle[58] == percussion(3) && cycle[59] == percussion(1));
    CHECK(cycle[60] == (UiControlId{UiControlKind::Expression}));
    CHECK(cycle[68] == (UiControlId{UiControlKind::ManualKey, Manual::Upper, DrawbarBank::A, 24}));
    CHECK(cycle[69] == (UiControlId{UiControlKind::ManualKey, Manual::Lower, DrawbarBank::A, 24}));
    CHECK(cycle.back() == (UiControlId{UiControlKind::PedalKey}));
    CHECK(tap(model, UiKey::Tab).count == 0 && model.view().focus == cycle.front());
    for (std::size_t ordinal = cycle.size(); ordinal > 0; --ordinal) {
        CHECK(tap(model, UiKey::Tab, true).count == 0);
        CHECK(model.view().focus == cycle[ordinal - 1]);
    }
    CHECK(model.view().controls == controls && !model.view().controls_pending);

    for (const auto index : kReferenceOrder) {
        const auto id = percussion(index);
        focus(model, id);
        for (const UiPoint size : {UiPoint{1399, 820}, UiPoint{1400, 819}, UiPoint{1400, 820}, UiPoint{1672.5F, 941.25F}}) {
            CHECK(model.resize(size.x, size.y));
            CHECK(model.view().focus == id && model.view().controls == controls);
        }
        CHECK(model.set_presentation(UiPresentation::Flat));
        require_order(model.layout(), kLegacyOrder);
        CHECK(model.view().focus == id);
        CHECK(tap(model, UiKey::Tab).count == 0);
        CHECK(model.view().focus == (index == 3 ? UiControlId{UiControlKind::Expression} : percussion(static_cast<std::uint8_t>(index + 1))));
        CHECK(tap(model, UiKey::Tab, true).count == 0 && model.view().focus == id);
        CHECK(model.set_presentation(UiPresentation::Dimensional));
        require_order(model.layout(), kReferenceOrder);
        CHECK(model.view().focus == id);
        for (const auto workspace : {UiWorkspace::Rotary, UiWorkspace::Service}) {
            CHECK(model.set_workspace(workspace));
            const auto hidden_focus = model.view().focus;
            CHECK(!ui_control_visible(model.layout(), id));
            CHECK(model.activate(id).count == 0 && model.view().focus == hidden_focus);
            CHECK(ui_hit_test(model.layout(), center(geometry(model.layout(), id).bounds)).kind == UiControlKind::None);
        }
        CHECK(model.set_workspace(UiWorkspace::Play));
        CHECK(model.view().focus == id && model.view().workspace_focus[0] == id);
        CHECK(model.view().controls == controls && !model.view().controls_pending);
        const auto before = model.layout();
        CHECK(!model.resize(8192.25F, 941));
        CHECK(!model.set_workspace(static_cast<UiWorkspace>(3)));
        CHECK(!model.set_presentation(static_cast<UiPresentation>(2)));
        CHECK(model.view().focus == id && model.view().controls == controls);
        same_layout(model.layout(), before);
    }
}

struct Rig {
    Session session;
    UiModel model;
    MidiInput midi;

    Rig() {
        CHECK(session.prepare(load_test_profile(), {48000.0, 64, 17, 37}) == SessionStatus::Ok);
        CHECK(session.start() == SessionStatus::Ok);
        CHECK(model.resize(1672, 941) && midi.begin_epoch());
        observe();
    }
    SessionSnapshot snapshot() const {
        SessionSnapshot result;
        CHECK(session.read_snapshot(result));
        return result;
    }
    void observe() { model.observe(snapshot()); }
    void dispatch(const UiActions& actions) {
        for (const auto& action : actions.span()) {
            CHECK(std::holds_alternative<SessionCommand>(action));
            const auto& value = std::get<SessionCommand>(action);
            const auto result = session.post(value);
            CHECK(result.ok() && model.submitted(value, result).count == 0);
        }
    }
    void wire(std::array<std::uint8_t, 3> bytes) {
        const auto decoded = midi.decode({bytes, 3, 100});
        CHECK(decoded.status == MidiDecodeStatus::Action);
        CHECK(std::holds_alternative<SessionCommand>(decoded.action));
        CHECK(session.post(std::get<SessionCommand>(decoded.action)).ok());
    }
    void flush() {
        CHECK(session.render(0, {}).ok());
        observe();
        CHECK(model.view().applied.recovery_count == 0 && model.view().applied.fault_flags == 0);
    }
};

void original_release(const UiActions& actions, std::uint8_t bus, std::uint8_t pitch, std::int32_t owner) {
    CHECK(std::holds_alternative<PerformanceInputEvent>(command(actions)));
    const auto& input = std::get<PerformanceInputEvent>(command(actions));
    CHECK(std::holds_alternative<HostNoteEvent>(input));
    const auto& note = std::get<HostNoteEvent>(input);
    CHECK(note.kind == HostNoteKind::Off && note.bus == bus && note.channel == 0);
    CHECK(note.midi_note == pitch && note.note_id == owner && note.offset == 0 && note.velocity == 0);
}

void pending_applied_routes_and_owners() {
    Rig rig;
    auto expected = seeded_controls();
    expected.selected_banks[0] = DrawbarBank::A;
    expected.percussion.enabled = true;
    rig.dispatch(rig.model.load_controls(expected));
    rig.dispatch(rig.model.key({UiKey::A, true})); // UI Upper MIDI 60.
    const auto& key = rig.model.layout().manual_keys[1][29]; // Lower F4, MIDI 65, a natural.
    const auto& q = key.hit.points;
    const UiPoint point{(q[3].x + q[2].x) * 0.5F, q[3].y - 1.0F};
    CHECK(ui_hit_test(rig.model.layout(), point) ==
          (UiControlId{UiControlKind::ManualKey, Manual::Lower, DrawbarBank::A, 29}));
    rig.dispatch(rig.model.pointer({UiPointerKind::Down, point}));
    rig.wire({0x90, 60, 100}); // Independent MIDI owner of the same upper note.
    rig.wire({0x91, 65, 100}); // Independent MIDI owner of the same lower note.
    rig.wire({0x92, 48, 100}); // Pedal ID 13.
    rig.flush();
    const auto held = rig.model.view().applied;
    CHECK(held.held_keys[0][24] && held.held_keys[1][29] && held.held_pedals[12]);
    const auto unchanged_holds = [&]() {
        const auto& state = rig.model.view().applied;
        CHECK(state.held_keys == held.held_keys && state.held_pedals == held.held_pedals);
        CHECK(state.frame_clock == held.frame_clock && state.recovery_count == 0);
    };

    struct Route { std::uint8_t key; DrawbarBank bank; FixedRegistration fixed; bool enabled; };
    constexpr std::array<Route, 5> routes{{
        {11, DrawbarBank::B, FixedRegistration::None, true},
        {2, DrawbarBank::B, FixedRegistration::D, true},
        {0, DrawbarBank::B, FixedRegistration::D, false},
        {10, DrawbarBank::A, FixedRegistration::None, true},
        {11, DrawbarBank::B, FixedRegistration::None, true}}};
    for (const auto& route : routes) {
        const auto applied_before = rig.model.view().applied.controls;
        expected.selected_banks[0] = route.bank;
        expected.fixed_registrations[0] = route.fixed;
        expected.route_enabled[0] = route.enabled;
        const auto action = rig.model.activate(preset(route.key));
        expected_edit(action, expected);
        rig.dispatch(action);
        rig.observe(); // Queued route changes must not become applied eligibility.
        CHECK(rig.model.view().controls_pending && rig.model.view().controls == expected);
        CHECK(rig.model.view().applied.controls == applied_before);
        CHECK(rig.model.view().controls.percussion.enabled);
        focus(rig.model, percussion(1));
        expected = toggled(expected, 1);
        const auto harmonic = tap(rig.model, UiKey::Enter);
        expected_edit(harmonic, expected); // Retains the unacknowledged route edit.
        rig.dispatch(harmonic);
        CHECK(rig.model.resize(1400, 820) && rig.model.set_presentation(UiPresentation::Flat));
        CHECK(rig.model.set_workspace(UiWorkspace::Rotary) && rig.model.set_workspace(UiWorkspace::Service));
        CHECK(rig.model.set_workspace(UiWorkspace::Play) && rig.model.set_presentation(UiPresentation::Dimensional));
        CHECK(rig.model.resize(1672, 941) && rig.model.view().focus == percussion(1));
        CHECK(rig.model.view().controls == expected && rig.model.view().applied.controls == applied_before);
        unchanged_holds();
        rig.flush();
        CHECK(!rig.model.view().controls_pending && rig.model.view().applied.controls == expected);
        // These copied inputs drive eligibility; no assertion about painted text.
        CHECK(rig.model.view().applied.controls.selected_banks[0] == route.bank);
        CHECK(rig.model.view().applied.controls.fixed_registrations[0] == route.fixed);
        CHECK(rig.model.view().applied.controls.route_enabled[0] == route.enabled);
        CHECK(rig.model.view().controls.percussion.enabled); // ON survives every ineligible route.
        unchanged_holds();
    }
    for (const auto index : kReferenceOrder) {
        focus(rig.model, percussion(index));
        for (unsigned direction = 0; direction < 2; ++direction) {
            expected = toggled(expected, index);
            const auto action = tap(rig.model, UiKey::Space);
            expected_edit(action, expected);
            rig.dispatch(action);
            rig.flush();
            unchanged_holds();
        }
    }
    CHECK(tap(rig.model, UiKey::F2).count == 0 && tap(rig.model, UiKey::RightBracket).count == 0);
    CHECK(rig.model.set_workspace(UiWorkspace::Service));
    const auto upper_off = rig.model.key({UiKey::A, false});
    original_release(upper_off, 0, 60, kUiKeyboardOwnerBase);
    rig.dispatch(upper_off);
    const auto lower_off = rig.model.pointer({UiPointerKind::Up, {-100, -100}});
    original_release(lower_off, 1, 65, kUiPointerOwnerId);
    rig.dispatch(lower_off);
    rig.flush();
    unchanged_holds(); // MIDI retains both notes after their original UI owners release.
    rig.wire({0x80, 60, 0});
    rig.flush();
    CHECK(!rig.model.view().applied.held_keys[0][24] && rig.model.view().applied.held_keys[1][29]);
    rig.wire({0x81, 65, 0});
    rig.wire({0x82, 48, 0});
    rig.flush();
    for (const auto& manual : rig.model.view().applied.held_keys)
        CHECK(std::none_of(manual.begin(), manual.end(), [](bool value) { return value; }));
    CHECK(std::none_of(rig.model.view().applied.held_pedals.begin(), rig.model.view().applied.held_pedals.end(),
                       [](bool value) { return value; }));
    CHECK(rig.model.view().controls == expected && rig.model.view().applied.controls == expected);
    CHECK(rig.model.view().applied.frame_clock == held.frame_clock);
}
} // namespace

int main() {
    frozen_geometry_and_predicate();
    invalid_layout_is_transactional();
    pointer_keyboard_domains_and_repeats();
    tab_cycle_and_semantic_reflow();
    pending_applied_routes_and_owners();
    std::cout << "Independent percussion acceptance: frozen geometry, predicate/target boundaries, "
                 "transactional layout rejection, semantic controls/repeats, focus/reflow, "
                 "and pending/applied MIDI/UI ownership passed\n";
}
