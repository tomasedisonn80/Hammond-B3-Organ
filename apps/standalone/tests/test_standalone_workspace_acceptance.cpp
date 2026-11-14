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

namespace {
using namespace hammond;
using namespace hammond::standalone;

static_assert(static_cast<unsigned>(UiControlKind::Workspace) == 20);
static_assert(static_cast<unsigned>(UiControlKind::Presentation) == 21);
static_assert(static_cast<unsigned>(UiKey::F1) == 30);
static_assert(static_cast<unsigned>(UiKey::F3) == 32);
static_assert(static_cast<unsigned>(UiKey::F4) == 33);
static_assert(static_cast<unsigned>(UiKey::F7) == 36);
static_assert(kParameterCount == 47);

constexpr std::array<UiWorkspace, 3> workspaces{
    UiWorkspace::Play, UiWorkspace::Rotary, UiWorkspace::Service};
constexpr std::array<UiPresentation, 2> presentations{
    UiPresentation::Dimensional, UiPresentation::Flat};
constexpr std::array<UiPoint, 7> sizes{{
    {960, 700}, {1280, 900}, {1672, 941}, {1399, 819},
    {1400, 819}, {1399, 820}, {1400, 820}}};
constexpr std::array<UiControlId, 10> common{{
    {UiControlKind::Workspace, Manual::Upper, DrawbarBank::A, 0},
    {UiControlKind::Workspace, Manual::Upper, DrawbarBank::A, 1},
    {UiControlKind::Workspace, Manual::Upper, DrawbarBank::A, 2},
    {UiControlKind::SaveControls}, {UiControlKind::LoadControls}, {UiControlKind::Help},
    {UiControlKind::AudioSettings}, {UiControlKind::MidiSettings}, {UiControlKind::Panic},
    {UiControlKind::Presentation}}};

struct Counts {
    std::size_t layouts{}, hidden_ids{}, focus_returns{}, invalid_operations{};
    std::size_t ownership_runs{}, closed_gestures{}, shortcut_gates{};
} counts;

UiControlId workspace_id(UiWorkspace workspace) {
    return {UiControlKind::Workspace, Manual::Upper, DrawbarBank::A,
            static_cast<std::uint8_t>(workspace)};
}

UiControlId manual_key(Manual manual, std::uint8_t midi) {
    return {UiControlKind::ManualKey, manual, DrawbarBank::A,
            static_cast<std::uint8_t>(midi - 36)};
}

UiControlId pedal_key(std::uint8_t pedal) {
    return {UiControlKind::PedalKey, Manual::Upper, DrawbarBank::A,
            static_cast<std::uint8_t>(pedal - 1)};
}

UiActions tap(UiModel& model, UiKey key, bool shift = false) {
    const auto actions = model.key({key, true, false, shift});
    CHECK(model.key({key, false}).count == 0);
    return actions;
}

const UiControlGeometry& geometry(const UiModel& model, UiControlId id) {
    for (const auto& control : model.layout().controls) if (control.id == id) return control;
    hammond_test::fail("retained control exists", __FILE__, __LINE__);
}

UiPoint center(UiRect rectangle) {
    return {rectangle.x + rectangle.width * 0.5F, rectangle.y + rectangle.height * 0.5F};
}

UiPoint playing_point(const UiModel& model, UiControlId id) {
    const auto& key = id.kind == UiControlKind::PedalKey ? model.layout().pedal_keys[id.index] :
        model.layout().manual_keys[static_cast<std::size_t>(id.manual)][id.index];
    const auto& q = key.hit.points;
    const float depth = key.accidental ? 0.3F : 0.9F;
    const float left = q[0].x + (q[3].x - q[0].x) * depth;
    const float right = q[1].x + (q[2].x - q[1].x) * depth;
    return {(left + right) * 0.5F, q[0].y + (q[3].y - q[0].y) * depth};
}

void focus_via_tab(UiModel& model, UiControlId id) {
    for (unsigned attempt = 0; attempt < 71 && model.view().focus != id; ++attempt)
        CHECK(tap(model, UiKey::Tab).count == 0);
    CHECK(model.view().focus == id);
}

void same_snapshot(const SessionSnapshot& a, const SessionSnapshot& b) {
    CHECK(std::tie(a.controls, a.held_keys, a.held_pedals, a.frame_clock, a.sample_rate,
                   a.peak, a.prepared, a.running, a.publication_revision, a.resolved_sequence,
                   a.last_applied_sequence, a.recovery_count, a.queue_overflows,
                   a.rejected_commands, a.discarded_commands, a.fault_flags, a.last_core_status) ==
          std::tie(b.controls, b.held_keys, b.held_pedals, b.frame_clock, b.sample_rate,
                   b.peak, b.prepared, b.running, b.publication_revision, b.resolved_sequence,
                   b.last_applied_sequence, b.recovery_count, b.queue_overflows,
                   b.rejected_commands, b.discarded_commands, b.fault_flags, b.last_core_status));
}

void same_view(const UiViewState& a, const UiViewState& b) {
    same_snapshot(a.applied, b.applied);
    CHECK(std::tie(a.controls, a.edited_banks, a.focus, a.roving_manual_keys, a.roving_pedal_key,
                   a.keyboard_target, a.manual_base_midi, a.pedal_octave, a.controls_pending,
                   a.controls_dirty, a.text_entry_active, a.pointer_captured, a.input_recovery,
                   a.last_submit_status, a.workspace, a.presentation, a.workspace_focus) ==
          std::tie(b.controls, b.edited_banks, b.focus, b.roving_manual_keys, b.roving_pedal_key,
                   b.keyboard_target, b.manual_base_midi, b.pedal_octave, b.controls_pending,
                   b.controls_dirty, b.text_entry_active, b.pointer_captured, b.input_recovery,
                   b.last_submit_status, b.workspace, b.presentation, b.workspace_focus));
}

void same_sound(const UiViewState& a, const UiViewState& b) {
    same_snapshot(a.applied, b.applied);
    CHECK(a.controls == b.controls && a.controls_pending == b.controls_pending);
    CHECK(a.controls_dirty == b.controls_dirty && a.last_submit_status == b.last_submit_status);
    CHECK(a.input_recovery == b.input_recovery);
}

void same_rect(UiRect a, UiRect b) {
    CHECK(std::tie(a.x, a.y, a.width, a.height) == std::tie(b.x, b.y, b.width, b.height));
}

void same_key(const UiKeyGeometry& a, const UiKeyGeometry& b) {
    CHECK(a.note == b.note && a.accidental == b.accidental);
    same_rect(a.bounds, b.bounds);
    for (std::size_t i = 0; i < 4; ++i) {
        CHECK(a.hit.points[i].x == b.hit.points[i].x && a.hit.points[i].y == b.hit.points[i].y);
        CHECK(a.top.points[i].x == b.top.points[i].x && a.top.points[i].y == b.top.points[i].y);
        CHECK(a.front.points[i].x == b.front.points[i].x && a.front.points[i].y == b.front.points[i].y);
    }
}

void same_layout(const UiLayout& a, const UiLayout& b) {
    CHECK(std::tie(a.width, a.height, a.show_cabinet, a.bank_controls_in_cheeks,
                   a.control_count, a.workspace, a.presentation) ==
          std::tie(b.width, b.height, b.show_cabinet, b.bank_controls_in_cheeks,
                   b.control_count, b.workspace, b.presentation));
    same_rect(a.header, b.header);
    same_rect(a.performance_panel, b.performance_panel);
    same_rect(a.keyboard_toolbar, b.keyboard_toolbar);
    same_rect(a.pedal_panel, b.pedal_panel);
    same_rect(a.footer, b.footer);
    same_rect(a.cabinet_panel, b.cabinet_panel);
    same_rect(a.cabinet_art, b.cabinet_art);
    same_rect(a.workspace_panel, b.workspace_panel);
    for (std::size_t manual = 0; manual < 2; ++manual) {
        same_rect(a.registration_panels[manual], b.registration_panels[manual]);
        same_rect(a.manual_panels[manual], b.manual_panels[manual]);
        same_rect(a.manual_rail_panels[manual], b.manual_rail_panels[manual]);
        same_rect(a.preset_key_panels[manual], b.preset_key_panels[manual]);
        for (std::size_t key = 0; key < 61; ++key) same_key(a.manual_keys[manual][key], b.manual_keys[manual][key]);
    }
    for (std::size_t key = 0; key < 25; ++key) same_key(a.pedal_keys[key], b.pedal_keys[key]);
    for (std::size_t control = 0; control < a.controls.size(); ++control) {
        const auto& x = a.controls[control];
        const auto& y = b.controls[control];
        CHECK(x.id == y.id);
        same_rect(x.bounds, y.bounds);
        same_rect(x.label_bounds, y.label_bounds);
        same_rect(x.value_bounds, y.value_bounds);
        same_rect(x.track, y.track);
    }
}

const SessionCommand& command(const UiActions& actions) {
    CHECK(actions.count == 1 && std::holds_alternative<SessionCommand>(actions.items[0]));
    return std::get<SessionCommand>(actions.items[0]);
}

void manual_event(const UiActions& actions, bool down, std::uint8_t bus,
                  std::uint8_t note, std::int32_t owner) {
    const auto& event = std::get<HostNoteEvent>(std::get<PerformanceInputEvent>(command(actions)));
    CHECK(event.kind == (down ? HostNoteKind::On : HostNoteKind::Off));
    CHECK(event.offset == 0 && event.channel == 0 && event.bus == bus);
    CHECK(event.midi_note == note && event.note_id == owner && event.velocity == (down ? 127 : 0));
}

void pedal_event(const UiActions& actions, bool down, std::uint8_t pedal, std::int32_t owner) {
    const auto& event = std::get<PedalNoteEvent>(std::get<PerformanceInputEvent>(command(actions)));
    CHECK(event.kind == (down ? PedalNoteKind::On : PedalNoteKind::Off));
    CHECK(event.offset == 0 && event.channel == 0 && event.bus == 0);
    CHECK(event.pedal.value == pedal && event.note_id == owner && event.velocity == (down ? 127 : 0));
}

void visibility_and_focus_matrix() {
    for (const auto size : sizes) for (const auto presentation : presentations) {
        UiModel model;
        CHECK(model.resize(size.x, size.y) && model.set_presentation(presentation));
        const auto initial = model.view().controls;
        for (const auto workspace : workspaces) {
            CHECK(model.set_workspace(workspace));
            const auto& layout = model.layout();
            CHECK(layout.workspace == workspace && layout.presentation == presentation);
            CHECK(layout.control_count == 68 && layout.manual_keys[0].size() == 61);
            CHECK(layout.manual_keys[1].size() == 61 && layout.pedal_keys.size() == 25);
            CHECK(layout.show_cabinet == (size.x >= 1400));
            CHECK(layout.bank_controls_in_cheeks == (size.y >= 820));
            CHECK(layout.workspace_panel.x == layout.header.x);
            CHECK(layout.workspace_panel.width == layout.header.width);
            CHECK(layout.workspace_panel.y > layout.header.y + layout.header.height);
            CHECK(layout.workspace_panel.y + layout.workspace_panel.height < layout.footer.y);
            for (std::size_t i = 0; i < common.size(); ++i) {
                CHECK(layout.controls[i].id == common[i]);
                CHECK(ui_control_visible(layout, common[i]));
                CHECK(ui_hit_test(layout, center(layout.controls[i].bounds)) == common[i]);
            }
            const auto reject_hidden = [&](UiControlId id, UiPoint point) {
                CHECK(!ui_control_visible(layout, id));
                CHECK(ui_hit_test(layout, point).kind == UiControlKind::None);
                const auto before = model.view();
                CHECK(model.activate(id).count == 0);
                same_view(model.view(), before);
                CHECK(model.pointer({UiPointerKind::Down, point}).count == 0);
                CHECK(model.pointer({UiPointerKind::Move, point}).count == 0);
                CHECK(model.pointer({UiPointerKind::Up, point}).count == 0);
                same_view(model.view(), before);
                ++counts.hidden_ids;
            };
            for (std::size_t i = 10; i < 68; ++i) {
                const auto& control = layout.controls[i];
                CHECK(ui_control_visible(layout, control.id) == (workspace == UiWorkspace::Play));
                if (workspace != UiWorkspace::Play) reject_hidden(control.id, center(control.bounds));
            }
            for (const auto manual : {Manual::Upper, Manual::Lower}) {
                for (std::uint8_t note = 36; note <= 96; ++note) {
                    const auto id = manual_key(manual, note);
                    CHECK(ui_control_visible(layout, id) == (workspace == UiWorkspace::Play));
                    if (workspace != UiWorkspace::Play) reject_hidden(id, playing_point(model, id));
                }
            }
            for (std::uint8_t pedal = 1; pedal <= 25; ++pedal) {
                const auto id = pedal_key(pedal);
                CHECK(ui_control_visible(layout, id) == (workspace == UiWorkspace::Play));
                if (workspace != UiWorkspace::Play) reject_hidden(id, playing_point(model, id));
            }
            if (workspace != UiWorkspace::Play) {
                const auto before = model.view();
                for (const auto kind : {UiControlKind::SoundingBank, UiControlKind::CancelManual}) {
                    CHECK(model.activate({kind}).count == 0);
                    same_view(model.view(), before);
                }
                // The entry tab is the only focus here; arrows and Space cannot
                // recover the remembered Play key or edit its hidden control.
                for (const auto key : {UiKey::Left, UiKey::Right, UiKey::Up, UiKey::Down,
                                       UiKey::Home, UiKey::End, UiKey::Space, UiKey::Enter}) {
                    CHECK(tap(model, key).count == 0);
                    same_view(model.view(), before);
                }
            }
            focus_via_tab(model, common[0]);
            const std::size_t stops = workspace == UiWorkspace::Play ? 71 : 10;
            std::array<UiControlId, 71> observed{};
            for (std::size_t i = 0; i < stops; ++i) {
                observed[i] = model.view().focus;
                CHECK(ui_control_visible(layout, observed[i]));
                if (i < common.size()) CHECK(observed[i] == common[i]);
                for (std::size_t j = 0; j < i; ++j) CHECK(observed[i] != observed[j]);
                CHECK(tap(model, UiKey::Tab).count == 0);
            }
            CHECK(model.view().focus == common[0]);
            for (std::size_t i = stops; i > 0; --i) {
                CHECK(tap(model, UiKey::Tab, true).count == 0);
                CHECK(model.view().focus == observed[i - 1]);
            }
            CHECK(model.view().controls == initial);
            CHECK(!model.view().controls_dirty && !model.view().controls_pending);
            ++counts.layouts;
        }
    }
}

void outgoing_memory_and_return() {
    const std::array<UiControlId, 4> memories{{
        {UiControlKind::ManualDrawbar, Manual::Upper, DrawbarBank::A, 8},
        manual_key(Manual::Lower, 96),
        {UiControlKind::PresetKey, Manual::Lower, DrawbarBank::A, 9},
        {UiControlKind::Expression}}};
    for (const auto size : sizes) for (const auto presentation : presentations) for (const auto remembered : memories) {
        UiModel model;
        CHECK(model.resize(size.x, size.y) && model.set_presentation(presentation));
        CHECK(model.activate({UiControlKind::EditBank, Manual::Upper, DrawbarBank::A}).count == 0);
        if (remembered.kind == UiControlKind::ManualKey) CHECK(model.activate(remembered).count == 0);
        else focus_via_tab(model, remembered);
        const auto play_view = model.view();
        CHECK(model.pointer({UiPointerKind::Down,
            center(geometry(model, workspace_id(UiWorkspace::Rotary)).bounds)}).count == 0);
        CHECK(model.pointer({UiPointerKind::Up, {}}).count == 0);
        CHECK(model.view().workspace_focus[0] == remembered);
        CHECK(model.view().focus == workspace_id(UiWorkspace::Rotary));
        CHECK(model.activate({UiControlKind::SaveControls}).count == 1);
        for (const auto id : {common[2], common[1], common[0]}) {
            CHECK(tap(model, UiKey::Tab, true).count == 0 && model.view().focus == id);
            CHECK(model.view().workspace == UiWorkspace::Rotary);
            CHECK(model.view().workspace_focus[1] == (UiControlId{UiControlKind::SaveControls}));
        }
        CHECK(model.activate(workspace_id(UiWorkspace::Service)).count == 0);
        CHECK(model.activate({UiControlKind::AudioSettings}).count == 1);
        const auto memories_before = model.view().workspace_focus;
        CHECK(memories_before[0] == remembered && memories_before[1] == (UiControlId{UiControlKind::SaveControls}));
        CHECK(memories_before[2] == (UiControlId{UiControlKind::AudioSettings}));
        const auto service_focus = model.view().focus;
        CHECK(model.pointer({UiPointerKind::Down, center(geometry(model, common[9]).bounds)}).count == 0);
        CHECK(model.pointer({UiPointerKind::Up, {}}).count == 0);
        CHECK(model.view().focus == service_focus && model.view().workspace_focus == memories_before);
        CHECK(model.resize(static_cast<float>(size.x < 1400 ? 1400 : 1399),
                           static_cast<float>(size.y < 820 ? 820 : 819)));
        CHECK(model.view().focus == service_focus && model.view().workspace_focus == memories_before);
        CHECK(tap(model, UiKey::F4).count == 0 && model.view().focus == remembered);
        CHECK(model.view().edited_banks == play_view.edited_banks);
        CHECK(model.view().roving_manual_keys == play_view.roving_manual_keys);
        CHECK(model.view().roving_pedal_key == play_view.roving_pedal_key);
        CHECK(tap(model, UiKey::F5).count == 0 && model.view().focus == common[3]);
        CHECK(tap(model, UiKey::F6).count == 0 && model.view().focus == service_focus);
        const auto before_same = model.view();
        CHECK(model.activate(workspace_id(UiWorkspace::Service)).count == 0);
        CHECK(tap(model, UiKey::F6).count == 0);
        CHECK(model.pointer({UiPointerKind::Down, center(geometry(model, common[2]).bounds)}).count == 0);
        CHECK(model.pointer({UiPointerKind::Up, {}}).count == 0);
        same_view(model.view(), before_same);
        focus_via_tab(model, common[9]);
        const auto toggle_memory = model.view().workspace_focus;
        CHECK(tap(model, UiKey::Enter).count == 0);
        CHECK(model.view().focus == common[9] && model.view().workspace_focus == toggle_memory);
        CHECK(model.view().controls == play_view.controls);
        ++counts.focus_returns;
    }
}

void invalid_atomic_rollback() {
    UiModel model;
    CHECK(model.resize(1400, 820));
    const UiControlId bar{UiControlKind::ManualDrawbar, Manual::Upper, DrawbarBank::B, 7};
    const auto track = geometry(model, bar).track;
    CHECK(model.pointer({UiPointerKind::Down, {track.x + 2, track.y}}).count == 0);
    const auto before = model.view();
    const auto layout_before = model.layout();
    const auto unchanged = [&] {
        same_view(model.view(), before);
        same_layout(model.layout(), layout_before);
        ++counts.invalid_operations;
    };
    for (unsigned value = 3; value < 256; ++value) {
        CHECK(!model.set_workspace(static_cast<UiWorkspace>(value)));
        unchanged();
    }
    for (unsigned value = 2; value < 256; ++value) {
        CHECK(!model.set_presentation(static_cast<UiPresentation>(value)));
        unchanged();
    }
    for (const auto kind : {UiControlKind::Workspace, UiControlKind::Presentation}) {
        for (unsigned field = 0; field < 3; ++field) for (unsigned value = 0; value < 256; ++value) {
            if ((field < 2 && value == 0) || (field == 2 && value < (kind == UiControlKind::Workspace ? 3U : 1U))) continue;
            UiControlId malformed{kind};
            if (field == 0) malformed.manual = static_cast<Manual>(value);
            if (field == 1) malformed.bank = static_cast<DrawbarBank>(value);
            if (field == 2) malformed.index = static_cast<std::uint8_t>(value);
            std::uint32_t parameter = 0xDEADBEEFU;
            CHECK(!ui_parameter_id(malformed, parameter) && parameter == 0xDEADBEEFU);
            CHECK(!ui_control_visible(model.layout(), malformed));
            CHECK(model.activate(malformed).count == 0);
            unchanged();
        }
    }
    for (const auto id : common) {
        if (id.kind != UiControlKind::Workspace && id.kind != UiControlKind::Presentation) continue;
        std::uint32_t parameter = 0xDEADBEEFU;
        CHECK(!ui_parameter_id(id, parameter) && parameter == 0xDEADBEEFU);
    }
    const float nan = std::numeric_limits<float>::quiet_NaN();
    for (const UiPoint invalid : {UiPoint{959, 820}, UiPoint{1400, 699}, UiPoint{8193, 820},
                                 UiPoint{1400, 8193}, UiPoint{nan, 820}, UiPoint{1400, INFINITY}}) {
        CHECK(!model.resize(invalid.x, invalid.y));
        unchanged();
    }
    for (const auto workspace : workspaces) for (const auto presentation : presentations) {
        UiLayout destination;
        CHECK(make_ui_layout(1672, 941, {DrawbarBank::A, DrawbarBank::B}, destination, workspace, presentation));
        const auto saved = destination;
        CHECK(!make_ui_layout(1672, 941, {DrawbarBank::A, DrawbarBank::B}, destination,
                              static_cast<UiWorkspace>(3), presentation));
        same_layout(destination, saved);
        CHECK(!make_ui_layout(1672, 941, {DrawbarBank::A, DrawbarBank::B}, destination,
                              workspace, static_cast<UiPresentation>(2)));
        same_layout(destination, saved);
        CHECK(!make_ui_layout(1672, 941, {DrawbarBank::A, static_cast<DrawbarBank>(255)}, destination,
                              workspace, presentation));
        same_layout(destination, saved);
    }
    CHECK(model.set_workspace(UiWorkspace::Play));
    CHECK(model.set_presentation(UiPresentation::Dimensional));
    same_view(model.view(), before);
    same_layout(model.layout(), layout_before);
    // Neither rejected transactions nor idempotent setters closed this drag.
    const auto moved = model.pointer({UiPointerKind::Move, {track.x + 2, track.y + track.height}});
    CHECK(std::get<ControlSnapshot>(command(moved)).drawbars[0][1][7] == 8);
    CHECK(model.pointer({UiPointerKind::Up, {}}).count == 0);
}

struct Rig {
    Session session;
    UiModel model;
    explicit Rig(const RuntimeProfile& profile) {
        CHECK(session.prepare(profile, {48000.0, 64, 17, 0}) == SessionStatus::Ok);
        CHECK(session.start() == SessionStatus::Ok);
        model.observe(snapshot());
    }
    SessionSnapshot snapshot() const {
        SessionSnapshot result;
        CHECK(session.read_snapshot(result));
        return result;
    }
    void dispatch(const UiActions& actions) {
        const auto& item = command(actions);
        const auto submitted = session.post(item);
        CHECK(submitted.ok());
        CHECK(model.submitted(item, submitted).count == 0);
    }
    void flush() {
        CHECK(session.render(0, {}).ok());
        model.observe(snapshot());
    }
};

void pending_and_owner_continuity(const RuntimeProfile& profile) {
    for (std::size_t size_index = 0; size_index < sizes.size(); ++size_index) for (const auto presentation : presentations) {
        Rig rig(profile);
        const auto size = sizes[size_index];
        CHECK(rig.model.resize(size.x, size.y) && rig.model.set_presentation(presentation));
        auto seeded = rig.model.view().controls;
        seeded.drawbars[0][1][2] = 8;
        seeded.drawbars[1][1][2] = 6;
        seeded.pedal_drawbars = {7, 2};
        seeded.percussion.enabled = true;
        rig.dispatch(rig.model.load_controls(seeded));
        rig.flush();
        rig.dispatch(rig.model.key({UiKey::A, true}));
        const auto pointer_id = manual_key(Manual::Lower, 96);
        rig.dispatch(rig.model.pointer({UiPointerKind::Down, playing_point(rig.model, pointer_id)}));
        CHECK(rig.model.activate(pedal_key(25)).count == 0);
        rig.dispatch(rig.model.key({UiKey::Space, true}));
        const std::array<PerformanceInputEvent, 3> external_on{{
            HostNoteEvent{0, HostNoteKind::On, 0, 4, 60, 127, 700},
            HostNoteEvent{0, HostNoteKind::On, 1, 5, 96, 127, 701},
            PedalNoteEvent{0, PedalNoteKind::On, 0, 6, PedalId{25}, 127, 702}}};
        for (const auto& event : external_on) CHECK(rig.session.post(event).ok());
        rig.flush();
        const auto held = rig.snapshot();
        CHECK(held.held_keys[0][24] && held.held_keys[1][60] && held.held_pedals[24]);
        rig.dispatch(rig.model.external_parameter(4096, 0.25));
        CHECK(rig.session.render(0, {}).ok());
        const auto earlier_ack = rig.snapshot();
        rig.dispatch(rig.model.external_parameter(8192, 0.375));
        const auto pending = rig.model.view();
        CHECK(pending.controls_pending && pending.controls_dirty);
        for (const auto workspace : {UiWorkspace::Service, UiWorkspace::Rotary, UiWorkspace::Play}) {
            CHECK(rig.model.set_workspace(workspace));
            CHECK(tap(rig.model, UiKey::F7).count == 0);
            const auto next = sizes[(size_index + 1) % sizes.size()];
            CHECK(rig.model.resize(next.x, next.y));
            same_sound(rig.model.view(), pending);
            CHECK(rig.model.view().pointer_captured);
            CHECK(rig.model.pointer({UiPointerKind::Move, playing_point(rig.model, manual_key(Manual::Upper, 36))}).count == 0);
            CHECK(rig.model.pointer({UiPointerKind::Down, playing_point(rig.model, pedal_key(1))}).count == 0);
            CHECK(rig.model.key({UiKey::Space, true}).count == 0);
            CHECK(rig.model.key({UiKey::A, true}).count == 0);
        }
        rig.model.observe(earlier_ack);
        CHECK(rig.model.view().controls == pending.controls && rig.model.view().controls_pending);
        CHECK(rig.model.view().applied.controls == earlier_ack.controls);
        rig.flush();
        CHECK(!rig.model.view().controls_pending && rig.model.view().applied.controls == pending.controls);
        CHECK(rig.model.view().applied.last_applied_sequence == earlier_ack.last_applied_sequence + 1);
        CHECK(rig.model.view().applied.held_keys == held.held_keys && rig.model.view().applied.held_pedals == held.held_pedals);
        CHECK(rig.model.view().applied.frame_clock == held.frame_clock && rig.model.view().applied.recovery_count == 0);
        CHECK(tap(rig.model, UiKey::F6).count == 0);
        CHECK(tap(rig.model, UiKey::F3).count == 0);
        CHECK(tap(rig.model, UiKey::RightBracket).count == 0);
        auto loaded = pending.controls;
        loaded.fixed_registrations[1] = FixedRegistration::GSharp;
        loaded.expression = 0.625;
        rig.dispatch(rig.model.load_controls(loaded));
        CHECK(!rig.model.view().controls_dirty && rig.model.view().controls_pending);
        rig.flush();
        CHECK(rig.model.view().workspace == UiWorkspace::Service && rig.model.view().controls == loaded);
        rig.model.set_text_entry_active(true);
        const auto keyboard_off = rig.model.key({UiKey::A, false, true, true, true, true, true});
        manual_event(keyboard_off, false, 0, 60, 1);
        rig.dispatch(keyboard_off);
        const auto space_off = rig.model.key({UiKey::Space, false, true, true, true, true, true});
        pedal_event(space_off, false, 25, 101);
        rig.dispatch(space_off);
        const auto pointer_off = rig.model.pointer({UiPointerKind::Up, {INFINITY, -INFINITY}});
        manual_event(pointer_off, false, 1, 96, 100);
        rig.dispatch(pointer_off);
        CHECK(!rig.model.view().pointer_captured);
        CHECK(rig.model.key({UiKey::A, false}).count == 0 && rig.model.key({UiKey::Space, false}).count == 0);
        CHECK(rig.model.pointer({UiPointerKind::Up, {}}).count == 0);
        rig.flush();
        CHECK(rig.model.view().applied.held_keys == held.held_keys && rig.model.view().applied.held_pedals == held.held_pedals);
        const std::array<PerformanceInputEvent, 3> external_off{{
            HostNoteEvent{0, HostNoteKind::Off, 0, 4, 60, 0, 700},
            HostNoteEvent{0, HostNoteKind::Off, 1, 5, 96, 0, 701},
            PedalNoteEvent{0, PedalNoteKind::Off, 0, 6, PedalId{25}, 0, 702}}};
        for (const auto& event : external_off) CHECK(rig.session.post(event).ok());
        rig.flush();
        for (const auto& manual : rig.model.view().applied.held_keys)
            CHECK(std::none_of(manual.begin(), manual.end(), [](bool active) { return active; }));
        CHECK(std::none_of(rig.model.view().applied.held_pedals.begin(), rig.model.view().applied.held_pedals.end(),
                           [](bool active) { return active; }));
        ++counts.ownership_runs;
    }
}

void closed_gestures_require_new_down() {
    const std::array<UiControlId, 3> parameters{{
        {UiControlKind::ManualDrawbar, Manual::Upper, DrawbarBank::A, 8},
        {UiControlKind::PedalDrawbar, Manual::Upper, DrawbarBank::A, 1},
        {UiControlKind::Expression}}};
    for (const auto size : sizes) for (unsigned transition = 0; transition < 3; ++transition) for (const auto parameter : parameters) {
        UiModel model;
        CHECK(model.resize(size.x, size.y));
        CHECK(model.set_presentation(transition == 1 ? UiPresentation::Flat : UiPresentation::Dimensional));
        CHECK(model.activate({UiControlKind::EditBank, Manual::Upper, DrawbarBank::A}).count == 0);
        const auto track = geometry(model, parameter).track;
        const bool horizontal = parameter.kind == UiControlKind::Expression;
        const UiPoint low{track.x + (horizontal ? 0 : 2), track.y + (horizontal ? 2 : 0)};
        const UiPoint high{horizontal ? track.x + track.width : track.x + 2,
                           horizontal ? track.y + 2 : track.y + track.height};
        (void)model.pointer({UiPointerKind::Down, low});
        CHECK(model.pointer({UiPointerKind::Move, high}).count == 1);
        const auto desired = model.view();
        if (transition == 0) CHECK(model.set_workspace(UiWorkspace::Rotary));
        if (transition == 1) CHECK(model.set_presentation(UiPresentation::Dimensional));
        if (transition == 2) CHECK(model.resize(static_cast<float>(size.x < 1400 ? 1400 : 1399),
                                              static_cast<float>(size.y < 820 ? 820 : 819)));
        CHECK(model.set_workspace(UiWorkspace::Play));
        CHECK(model.activate({UiControlKind::EditBank, Manual::Upper, DrawbarBank::B}).count == 0);
        for (const auto point : {low, high, playing_point(model, manual_key(Manual::Lower, 48)),
                                 center(geometry(model, {UiControlKind::Expression}).bounds)}) {
            CHECK(model.pointer({UiPointerKind::Move, point}).count == 0);
            CHECK(model.pointer({UiPointerKind::Down, point}).count == 0);
            same_sound(model.view(), desired);
            CHECK(model.view().pointer_captured);
        }
        CHECK(model.pointer({UiPointerKind::Up, {}}).count == 0 && !model.view().pointer_captured);
        const auto new_note = model.pointer({UiPointerKind::Down, playing_point(model, manual_key(Manual::Lower, 48))});
        manual_event(new_note, true, 1, 48, 100);
        manual_event(model.pointer({UiPointerKind::CaptureLost, {}}), false, 1, 48, 100);
        CHECK(model.pointer({UiPointerKind::Up, {}}).count == 0);
        ++counts.closed_gestures;
    }
    // A press that began in a read-only body stays inert even after both the
    // presentation and workspace expose a keyboard underneath that pointer.
    for (const auto workspace : {UiWorkspace::Rotary, UiWorkspace::Service}) for (const auto presentation : presentations) {
        UiModel model;
        CHECK(model.set_workspace(workspace) && model.set_presentation(presentation));
        CHECK(model.pointer({UiPointerKind::Down, playing_point(model, pedal_key(25))}).count == 0);
        CHECK(model.set_workspace(UiWorkspace::Play));
        CHECK(tap(model, UiKey::F7).count == 0);
        CHECK(model.resize(960, 700));
        CHECK(model.pointer({UiPointerKind::Move, playing_point(model, manual_key(Manual::Upper, 60))}).count == 0);
        CHECK(model.pointer({UiPointerKind::Down, playing_point(model, manual_key(Manual::Upper, 60))}).count == 0);
        CHECK(model.pointer({UiPointerKind::Up, {}}).count == 0);
        manual_event(model.pointer({UiPointerKind::Down, playing_point(model, manual_key(Manual::Upper, 60))}), true, 0, 60, 100);
        manual_event(model.pointer({UiPointerKind::Up, {}}), false, 0, 60, 100);
    }
}

void shortcut_gates_and_global_input() {
    constexpr std::array<UiKey, 4> shortcuts{UiKey::F4, UiKey::F5, UiKey::F6, UiKey::F7};
    for (const auto workspace : workspaces) for (const auto presentation : presentations) {
        for (const auto shortcut : shortcuts) for (unsigned gate = 0; gate < 5; ++gate) {
            UiModel model;
            CHECK(model.set_workspace(workspace) && model.set_presentation(presentation));
            model.set_text_entry_active(gate == 0);
            const auto before = model.view();
            CHECK(model.key({shortcut, true, gate == 4, false, gate == 1, gate == 2, gate == 3}).count == 0);
            same_view(model.view(), before);
            model.set_text_entry_active(false);
            CHECK(model.key({shortcut, true}).count == 0);
            CHECK(model.view().workspace == workspace && model.view().presentation == presentation);
            CHECK(model.key({shortcut, false, true, true, true, true, true}).count == 0);
            CHECK(tap(model, shortcut, true).count == 0);
            if (shortcut == UiKey::F7) {
                CHECK(model.view().workspace == workspace && model.view().presentation != presentation);
            } else {
                const auto wanted = shortcut == UiKey::F4 ? UiWorkspace::Play :
                    shortcut == UiKey::F5 ? UiWorkspace::Rotary : UiWorkspace::Service;
                CHECK(model.view().workspace == wanted && model.view().presentation == presentation);
            }
            ++counts.shortcut_gates;
        }
        UiModel model;
        CHECK(model.set_workspace(workspace) && model.set_presentation(presentation));
        const auto controls = model.view().controls;
        for (const auto target : {UiKey::F1, UiKey::F2, UiKey::F3}) {
            CHECK(tap(model, target).count == 0);
            const auto on = model.key({UiKey::A, true});
            if (target == UiKey::F3) pedal_event(on, true, 1, 1);
            else manual_event(on, true, target == UiKey::F1 ? 0 : 1, 60, 1);
            CHECK(tap(model, UiKey::RightBracket).count == 0);
            model.set_text_entry_active(true);
            const auto off = model.key({UiKey::A, false, false, false, true, true, true});
            if (target == UiKey::F3) pedal_event(off, false, 1, 1);
            else manual_event(off, false, target == UiKey::F1 ? 0 : 1, 60, 1);
            model.set_text_entry_active(false);
            CHECK(tap(model, UiKey::LeftBracket).count == 0);
        }
        struct Request { UiControlKind kind; UiAppRequest request; };
        constexpr std::array<Request, 5> requests{{
            {UiControlKind::SaveControls, UiAppRequest::SaveControls},
            {UiControlKind::LoadControls, UiAppRequest::LoadControls},
            {UiControlKind::Help, UiAppRequest::Help},
            {UiControlKind::AudioSettings, UiAppRequest::AudioSettings},
            {UiControlKind::MidiSettings, UiAppRequest::MidiSettings}}};
        for (const auto request : requests) {
            const auto clicked = model.pointer({UiPointerKind::Down, center(geometry(model, {request.kind}).bounds)});
            CHECK(clicked.count == 1 && std::get<UiAppRequest>(clicked.items[0]) == request.request);
            CHECK(model.pointer({UiPointerKind::Up, {}}).count == 0);
            model.set_text_entry_active(true);
            CHECK(tap(model, UiKey::F7).count == 0);
            CHECK(model.view().workspace == workspace && model.view().presentation == presentation);
            model.set_text_entry_active(false);
            const auto enter = tap(model, UiKey::Enter);
            CHECK(enter.count == 1 && std::get<UiAppRequest>(enter.items[0]) == request.request);
        }
        CHECK(model.view().controls == controls && !model.view().controls_pending && !model.view().controls_dirty);
        CHECK(std::holds_alternative<Panic>(command(model.activate({UiControlKind::Panic}))));
        CHECK(model.view().workspace == workspace && model.view().presentation == presentation);
    }
}
} // namespace

int main() {
    visibility_and_focus_matrix();
    outgoing_memory_and_return();
    invalid_atomic_rollback();
    pending_and_owner_continuity(load_test_profile());
    closed_gestures_require_new_down();
    shortcut_gates_and_global_input();
    std::cout << "Workspace acceptance: " << counts.layouts << " layout/mode/view cases, "
              << counts.hidden_ids << " hidden semantic/pointer rejections, "
              << counts.focus_returns << " focus-memory returns, " << counts.invalid_operations
              << " atomic invalid operations, " << counts.ownership_runs << " real-Session ownership runs, "
              << counts.closed_gestures << " closed parameter gestures, " << counts.shortcut_gates
              << " shortcut suppression cases passed\n";
}
