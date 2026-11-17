#include "UiModel.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>

namespace hammond::standalone {
namespace {

[[nodiscard]] constexpr bool valid_manual(Manual manual) noexcept {
    return manual == Manual::Upper || manual == Manual::Lower;
}

[[nodiscard]] constexpr bool valid_workspace(UiWorkspace workspace) noexcept {
    return workspace == UiWorkspace::Play || workspace == UiWorkspace::Rotary ||
           workspace == UiWorkspace::Service;
}

[[nodiscard]] constexpr bool valid_presentation(UiPresentation presentation) noexcept {
    return presentation == UiPresentation::Dimensional || presentation == UiPresentation::Flat;
}

[[nodiscard]] constexpr std::size_t manual_index(Manual manual) noexcept {
    return static_cast<std::size_t>(manual);
}

[[nodiscard]] constexpr bool canonical_global(UiControlId id) noexcept {
    return id.manual == Manual::Upper && id.bank == DrawbarBank::A;
}

// Reject malformed semantic IDs before any enum is used as an array index.
[[nodiscard]] bool valid_control(UiControlId id) noexcept {
    switch (id.kind) {
    case UiControlKind::EditBank:
    case UiControlKind::SoundingBank:
        return valid_manual(id.manual) && is_valid_drawbar_bank(id.bank) && id.index == 0;
    case UiControlKind::CancelManual:
        return valid_manual(id.manual) && id.bank == DrawbarBank::A && id.index == 0;
    case UiControlKind::PresetKey:
        return valid_manual(id.manual) && id.bank == DrawbarBank::A && id.index < kPresetSelectionCount;
    case UiControlKind::ManualDrawbar:
        return valid_manual(id.manual) && is_valid_drawbar_bank(id.bank) && id.index < kDrawbarCount;
    case UiControlKind::ManualKey:
        return valid_manual(id.manual) && id.bank == DrawbarBank::A && id.index < kManualKeyCount;
    case UiControlKind::PedalDrawbar:
        return canonical_global(id) && id.index < kPedalDrawbarCount;
    case UiControlKind::Percussion:
        return canonical_global(id) && id.index < 4;
    case UiControlKind::KeyboardTarget:
        return canonical_global(id) && id.index < 3;
    case UiControlKind::Workspace:
        return canonical_global(id) && id.index < kUiWorkspaceCount;
    case UiControlKind::PedalKey:
        return canonical_global(id) && id.index < kPedalCount;
    case UiControlKind::Expression:
    case UiControlKind::OctaveDown:
    case UiControlKind::OctaveUp:
    case UiControlKind::SaveControls:
    case UiControlKind::LoadControls:
    case UiControlKind::AudioSettings:
    case UiControlKind::Help:
    case UiControlKind::Panic:
    case UiControlKind::MidiSettings:
    case UiControlKind::Presentation:
        return canonical_global(id) && id.index == 0;
    case UiControlKind::None:
        return false;
    }
    return false;
}

[[nodiscard]] constexpr bool is_playing_control(UiControlId id) noexcept {
    return id.kind == UiControlKind::ManualKey || id.kind == UiControlKind::PedalKey;
}

[[nodiscard]] constexpr UiControlId note_control(const UiNote& note) noexcept {
    if (note.target == UiTarget::Pedals) {
        return {UiControlKind::PedalKey, Manual::Upper, DrawbarBank::A,
                static_cast<std::uint8_t>(note.value - 1)};
    }
    return {UiControlKind::ManualKey,
            note.target == UiTarget::Upper ? Manual::Upper : Manual::Lower,
            DrawbarBank::A, static_cast<std::uint8_t>(note.value - kMinManualMidiNote)};
}

[[nodiscard]] constexpr UiNote control_note(UiControlId id) noexcept {
    if (id.kind == UiControlKind::PedalKey) {
        return {UiTarget::Pedals, static_cast<std::uint8_t>(id.index + 1)};
    }
    return {id.manual == Manual::Upper ? UiTarget::Upper : UiTarget::Lower,
            static_cast<std::uint8_t>(kMinManualMidiNote + id.index)};
}

void focus_control(UiViewState& view, const UiLayout& layout, UiControlId id) noexcept {
    view.focus = id;
    if (id.kind == UiControlKind::ManualKey) view.roving_manual_keys[manual_index(id.manual)] = id.index;
    if (id.kind == UiControlKind::PedalKey) view.roving_pedal_key = id.index;
    if (id.kind != UiControlKind::Workspace && valid_workspace(view.workspace) &&
        ui_control_visible(layout, id)) {
        view.workspace_focus[static_cast<std::size_t>(view.workspace)] = id;
    }
}

[[nodiscard]] UiActions one_command(const SessionCommand& command) noexcept {
    UiActions actions;
    actions.items[0] = command;
    actions.count = 1;
    return actions;
}

[[nodiscard]] UiActions one_request(UiAppRequest request) noexcept {
    UiActions actions;
    actions.items[0] = request;
    actions.count = 1;
    return actions;
}

[[nodiscard]] SessionCommand note_command(const UiHeldPress& press, bool down) noexcept {
    if (press.note.target == UiTarget::Pedals) {
        return PerformanceInputEvent{PedalNoteEvent{
            0, down ? PedalNoteKind::On : PedalNoteKind::Off, 0, kUiInputChannel,
            PedalId{press.note.value}, static_cast<std::uint8_t>(down ? kUiNoteVelocity : 0),
            press.owner_id}};
    }
    return PerformanceInputEvent{HostNoteEvent{
        0, down ? HostNoteKind::On : HostNoteKind::Off,
        static_cast<std::uint8_t>(press.note.target == UiTarget::Upper ? 0 : 1),
        kUiInputChannel, press.note.value,
        static_cast<std::uint8_t>(down ? kUiNoteVelocity : 0), press.owner_id}};
}

[[nodiscard]] UiActions release_press(UiHeldPress& press) noexcept {
    if (!press.active) return {};
    const auto actions = one_command(note_command(press, false));
    press = {};
    return actions;
}

[[nodiscard]] bool apply_parameter(const ControlSnapshot& source, std::uint32_t parameter,
                                   double normalized, ControlSnapshot& result) noexcept {
    ParameterDescriptor descriptor;
    Event event;
    if (!parameter_descriptor(parameter, descriptor) ||
        !normalized_to_event(parameter, normalized, 0, event)) return false;
    ControlState candidate;
    if (!candidate.restore(source)) return false;
    bool valid = false;
    switch (event.type) {
    case EventType::BankDrawbar:
        valid = candidate.set_bank_drawbar(event.manual,
            event.index < kDrawbarCount ? DrawbarBank::A : DrawbarBank::B,
            event.index % kDrawbarCount, static_cast<std::uint8_t>(event.value));
        break;
    case EventType::SelectBank:
        valid = candidate.select_bank(event.manual,
            event.value == 0.0 ? DrawbarBank::A : DrawbarBank::B);
        break;
    case EventType::SelectPreset:
        valid = candidate.select_preset(event.manual,
            static_cast<PresetSelection>(static_cast<std::uint8_t>(event.value)));
        break;
    case EventType::Expression:
        valid = candidate.set_expression(event.value);
        break;
    case EventType::PedalDrawbar:
        valid = candidate.set_pedal_drawbar(event.index, static_cast<std::uint8_t>(event.value));
        break;
    case EventType::Percussion: {
        auto settings = candidate.percussion_settings();
        switch (event.index) {
        case 0: settings.enabled = event.value != 0.0; break;
        case 1: settings.harmonic = event.value == 0.0 ? PercussionHarmonic::Second : PercussionHarmonic::Third; break;
        case 2: settings.volume = event.value == 0.0 ? PercussionVolume::Normal : PercussionVolume::Soft; break;
        case 3: settings.decay = event.value == 0.0 ? PercussionDecay::Slow : PercussionDecay::Fast; break;
        default: return false;
        }
        valid = candidate.set_percussion_settings(settings);
        break;
    }
    default: return false;
    }
    if (!valid) return false;
    result = candidate.snapshot();
    return true;
}

[[nodiscard]] bool control_plain(const ControlSnapshot& controls, UiControlId id,
                                 double& result) noexcept {
    std::uint32_t parameter = 0;
    if (!ui_parameter_id(id, parameter)) return false;
    switch (id.kind) {
    case UiControlKind::ManualDrawbar:
        result = controls.drawbars[manual_index(id.manual)][static_cast<std::size_t>(id.bank)][id.index];
        return true;
    case UiControlKind::PedalDrawbar: result = controls.pedal_drawbars[id.index]; return true;
    case UiControlKind::Expression: result = controls.expression; return true;
    case UiControlKind::SoundingBank:
        result = static_cast<double>(controls.selected_banks[manual_index(id.manual)]);
        return true;
    case UiControlKind::PresetKey: {
        PresetSelection selection{};
        if (!control_preset_selection(controls, id.manual, selection)) return false;
        result = static_cast<double>(selection);
        return true;
    }
    case UiControlKind::Percussion:
        switch (id.index) {
        case 0: result = controls.percussion.enabled ? 1.0 : 0.0; break;
        case 1: result = static_cast<double>(controls.percussion.harmonic); break;
        case 2: result = static_cast<double>(controls.percussion.volume); break;
        case 3: result = static_cast<double>(controls.percussion.decay); break;
        default: return false;
        }
        return true;
    default: return false;
    }
}

[[nodiscard]] UiActions publish_controls(UiViewState& view, const ControlSnapshot& saved,
                                         std::uint64_t& pending_sequence,
                                         const ControlSnapshot& controls,
                                         bool force = false) noexcept {
    if (!force && controls == view.controls) return {};
    view.controls = controls;
    view.controls_pending = true;
    view.controls_dirty = !(view.controls == saved);
    // A new desired copy is not acknowledged by an older submitted sequence.
    pending_sequence = 0;
    return one_command(SessionCommand{controls});
}

[[nodiscard]] bool parameter_at_point(const UiDrawbarGesture& drag, UiPoint point,
                                     const ControlSnapshot& source,
                                     ControlSnapshot& result) noexcept {
    if (!std::isfinite(point.x) || !std::isfinite(point.y)) return false;
    double normalized = 0.0;
    if (drag.control.kind == UiControlKind::Expression) {
        if (drag.track.width <= 0.0F) return false;
        normalized = (static_cast<double>(point.x) - drag.track.x) / drag.track.width;
    } else {
        if (drag.track.height <= 0.0F) return false;
        normalized = (static_cast<double>(point.y) - drag.track.y) / drag.track.height;
    }
    return apply_parameter(source, drag.parameter_id, std::clamp(normalized, 0.0, 1.0), result);
}

[[nodiscard]] constexpr bool accidental(std::size_t semitone) noexcept {
    const auto pitch = semitone % 12;
    return pitch == 1 || pitch == 3 || pitch == 6 || pitch == 8 || pitch == 10;
}

template <std::size_t Count>
void make_keys(std::array<UiKeyGeometry, Count>& keys, UiRect panel,
               UiTarget target, std::size_t natural_count,
               UiPresentation presentation) noexcept {
    const float left = panel.x + 8.0F;
    const float top = panel.y + 22.0F;
    const float width = panel.width - 16.0F;
    const float height = panel.height - 30.0F;
    const bool dimensional = presentation == UiPresentation::Dimensional;
    const double back = dimensional && target != UiTarget::Pedals ? 0.94 : 1.0;
    const double count = static_cast<double>(natural_count);
    const auto project = [=](double u, double v) noexcept -> UiPoint {
        const double denominator = 1.0 - (1.0 - back) * v;
        return {static_cast<float>(left + static_cast<double>(width) / 2.0 +
                    static_cast<double>(width) * back * (u - 0.5) / denominator),
                static_cast<float>(top + static_cast<double>(height) * back * v / denominator)};
    };
    std::size_t natural = 0;
    for (std::size_t index = 0; index < Count; ++index) {
        auto& key = keys[index];
        key.note = {target, static_cast<std::uint8_t>(
            target == UiTarget::Pedals ? index + 1 : kMinManualMidiNote + index)};
        key.accidental = accidental(index);
        // Each natural edge is derived from its integer ordinal. Adjacent
        // keys therefore use identical projected endpoints, including the
        // last boundary. Neither rendering nor hit testing invents a second
        // keyboard coordinate system.
        const double ordinal = static_cast<double>(natural);
        const double u0 = (ordinal - (key.accidental ? 0.30 : 0.0)) / count;
        const double u1 = (ordinal + (key.accidental ? 0.30 : 1.0)) / count;
        const double depth = key.accidental ? 0.62 : 1.0;
        key.hit.points = {{project(u0, 0.0), project(u1, 0.0),
                           project(u1, depth), project(u0, depth)}};
        if (!key.accidental) ++natural;
        const auto& points = key.hit.points;
        const float minimum_x = std::min({points[0].x, points[1].x, points[2].x, points[3].x});
        const float maximum_x = std::max({points[0].x, points[1].x, points[2].x, points[3].x});
        key.bounds = {minimum_x, points[0].y, maximum_x - minimum_x,
                      points[3].y - points[0].y};
        key.top = key.hit;
        key.front = {};
        if (dimensional) {
            const float front_depth = std::clamp(key.bounds.height * 0.14F, 6.0F, 18.0F);
            const float split_y = points[3].y - front_depth;
            const float fraction = (split_y - points[0].y) / key.bounds.height;
            const UiPoint split_left{points[0].x + (points[3].x - points[0].x) * fraction, split_y};
            const UiPoint split_right{points[1].x + (points[2].x - points[1].x) * fraction, split_y};
            key.top.points[2] = split_right;
            key.top.points[3] = split_left;
            key.front.points = {{split_left, split_right, points[2], points[3]}};
        }
    }
}

[[nodiscard]] UiRect reference_quad_bounds(const UiQuad& quad) noexcept {
    const auto& points = quad.points;
    const float left = std::min({points[0].x, points[1].x, points[2].x, points[3].x});
    const float right = std::max({points[0].x, points[1].x, points[2].x, points[3].x});
    const float top = std::min({points[0].y, points[1].y, points[2].y, points[3].y});
    const float bottom = std::max({points[0].y, points[1].y, points[2].y, points[3].y});
    return {left, top, right - left, bottom - top};
}

template <std::size_t Count>
void make_reference_keys(std::array<UiKeyGeometry, Count>& keys, UiRect panel,
                         UiTarget target, std::size_t natural_count,
                         ReferenceCompositionScale scale) noexcept {
    const float left = panel.x + 8.0F;
    const float top = panel.y + 20.0F;
    const float width = panel.width - 16.0F;
    const float height = panel.height - 28.0F;
    const double back = target == UiTarget::Upper ? 0.96 :
                        target == UiTarget::Lower ? 0.95 : 1.0;
    const double count = static_cast<double>(natural_count);
    const auto project = [=](double u, double v) noexcept -> UiPoint {
        const double denominator = 1.0 - (1.0 - back) * v;
        return {static_cast<float>(left + static_cast<double>(width) / 2.0 +
                    static_cast<double>(width) * back * (u - 0.5) / denominator),
                static_cast<float>(top + static_cast<double>(height) * back * v / denominator)};
    };
    // Construct shared canonical natural boundaries once. Every mapped neighbor
    // then has exactly the same back, split and front vertices.
    std::array<UiPoint, Count + 1> back_edges{};
    std::array<UiPoint, Count + 1> front_edges{};
    for (std::size_t boundary = 0; boundary <= natural_count; ++boundary) {
        const double u = static_cast<double>(boundary) / count;
        back_edges[boundary] = project(u, 0.0);
        front_edges[boundary] = project(u, 1.0);
    }
    std::size_t natural = 0;
    for (std::size_t index = 0; index < Count; ++index) {
        auto& key = keys[index];
        key.note = {target, static_cast<std::uint8_t>(
            target == UiTarget::Pedals ? index + 1 : kMinManualMidiNote + index)};
        key.accidental = accidental(index);
        UiQuad hit;
        if (key.accidental) {
            const double ordinal = static_cast<double>(natural);
            const double u0 = (ordinal - 0.30) / count;
            const double u1 = (ordinal + 0.30) / count;
            hit.points = {{project(u0, 0.0), project(u1, 0.0),
                           project(u1, 0.62), project(u0, 0.62)}};
        } else {
            hit.points = {{back_edges[natural], back_edges[natural + 1],
                           front_edges[natural + 1], front_edges[natural]}};
            ++natural;
        }
        const auto& points = hit.points;
        const float key_height = points[3].y - points[0].y;
        const float front_depth = std::clamp(key_height * 0.14F, 6.0F, 18.0F);
        const float split_y = points[3].y - front_depth;
        const float fraction = (split_y - points[0].y) / key_height;
        const UiPoint split_left{points[0].x + (points[3].x - points[0].x) * fraction, split_y};
        const UiPoint split_right{points[1].x + (points[2].x - points[1].x) * fraction, split_y};
        UiQuad surface = hit;
        surface.points[2] = split_right;
        surface.points[3] = split_left;
        const UiQuad front{{split_left, split_right, points[2], points[3]}};
        // The complete canonical surfaces precede scaling, including the front
        // clamp. A post-scale clamp would give different geometry at each size.
        key.hit = reference_composition_quad(hit, scale);
        key.top = reference_composition_quad(surface, scale);
        key.front = reference_composition_quad(front, scale);
        key.bounds = reference_quad_bounds(key.hit);
    }
}

void add_button(UiLayout& layout, UiControlId id, UiRect bounds) noexcept {
    layout.controls[layout.control_count++] = {
        id, bounds, {bounds.x + 4.0F, bounds.y + 4.0F, bounds.width - 8.0F, bounds.height - 8.0F}, {}, {}};
}

void add_preset_keys(UiLayout& layout, Manual manual, UiRect panel) noexcept {
    constexpr float natural_count = 7.0F;
    const float natural_width = panel.width / natural_count;
    std::size_t natural = 0;
    for (std::size_t index = 0; index < kPresetSelectionCount; ++index) {
        UiRect bounds;
        if (accidental(index)) {
            bounds = {panel.x + static_cast<float>(natural) * natural_width - 0.30F * natural_width,
                      panel.y, 0.60F * natural_width, 0.62F * panel.height};
        } else {
            const float left = panel.x + panel.width * static_cast<float>(natural) / natural_count;
            const float right = panel.x + panel.width * static_cast<float>(natural + 1) / natural_count;
            bounds = {left, panel.y, right - left, panel.height};
            ++natural;
        }
        const float label_height = accidental(index) ? 20.0F : 11.0F;
        layout.controls[layout.control_count++] = {
            {UiControlKind::PresetKey, manual, DrawbarBank::A, static_cast<std::uint8_t>(index)},
            bounds, {bounds.x + 1.0F, bounds.y + bounds.height - label_height - 2.0F,
                     bounds.width - 2.0F, label_height}, {}, {}};
    }
}

constexpr std::array<UiRect, kManualCount> kReferenceManualPanels{{
    {232.0F, 528.0F, 890.0F, 170.0F}, {224.0F, 698.0F, 898.0F, 172.0F}}};
constexpr std::array<UiRect, kManualCount> kReferenceCheekPanels{{
    {48.0F, 528.0F, 184.0F, 170.0F}, {32.0F, 698.0F, 192.0F, 172.0F}}};
constexpr std::array<UiRect, kManualCount> kReferencePresetPanels{{
    {58.0F, 607.0F, 164.0F, 81.0F}, {42.0F, 777.0F, 172.0F, 83.0F}}};
constexpr std::array<std::array<float, kDrawbarCount>, kManualCount> kReferenceDrawbarCenters{{
    {158.0F, 206.0F, 254.0F, 302.0F, 351.0F, 400.0F, 449.0F, 498.0F, 548.0F},
    {685.0F, 734.0F, 782.0F, 830.0F, 878.0F, 927.0F, 975.0F, 1024.0F, 1074.0F}}};
constexpr UiRect kReferencePedalPanel{1138.0F, 752.0F, 450.0F, 110.0F};
constexpr UiRect kReferenceArtEnvelope{1132.0F, 174.0F, 466.0F, 397.0F};

void add_reference_control(UiLayout& layout, ReferenceCompositionScale scale,
                           UiControlId id, UiRect bounds, UiRect label,
                           UiRect value = {}, UiRect track = {}) noexcept {
    layout.controls[layout.control_count++] = {
        id, reference_composition_rect(bounds, scale), reference_composition_rect(label, scale),
        reference_composition_rect(value, scale), reference_composition_rect(track, scale)};
}

void add_reference_button(UiLayout& layout, ReferenceCompositionScale scale,
                          UiControlId id, UiRect bounds) noexcept {
    add_reference_control(layout, scale, id, bounds,
        {bounds.x + 4.0F, bounds.y + 4.0F, bounds.width - 8.0F, bounds.height - 8.0F});
}

void add_reference_presets(UiLayout& layout, ReferenceCompositionScale scale,
                           Manual manual, UiRect panel) noexcept {
    constexpr std::size_t natural_count = 7;
    const float natural_width = panel.width / static_cast<float>(natural_count);
    std::array<float, natural_count + 1> boundaries{};
    for (std::size_t index = 0; index <= natural_count; ++index)
        boundaries[index] = panel.x + panel.width * static_cast<float>(index) /
                                      static_cast<float>(natural_count);
    std::size_t natural = 0;
    for (std::size_t index = 0; index < kPresetSelectionCount; ++index) {
        const bool sharp = accidental(index);
        const float left = sharp ? boundaries[natural] - 0.30F * natural_width : boundaries[natural];
        const float right = sharp ? boundaries[natural] + 0.30F * natural_width : boundaries[natural + 1];
        const float bottom = panel.y + (sharp ? 0.62F * panel.height : panel.height);
        const float label_height = sharp ? 20.0F : 11.0F;
        layout.controls[layout.control_count++] = {
            {UiControlKind::PresetKey, manual, DrawbarBank::A, static_cast<std::uint8_t>(index)},
            reference_composition_edges(left, panel.y, right, bottom, scale),
            reference_composition_edges(left + 1.0F, bottom - label_height - 2.0F,
                                        right - 1.0F, bottom - 2.0F, scale), {}, {}};
        if (!sharp) ++natural;
    }
}

void make_reference_composition(
    UiLayout& layout, const std::array<DrawbarBank, kManualCount>& edited_banks) noexcept {
    const auto scale = reference_composition_scale(layout);
    const auto map = [scale](UiRect rect) noexcept { return reference_composition_rect(rect, scale); };
    layout.show_cabinet = true;
    layout.bank_controls_in_cheeks = true;
    layout.sidebar_pedals = true;
    layout.header = map({72.0F, 10.0F, 1528.0F, 102.0F});
    layout.performance_panel = map({72.0F, 125.0F, 1044.0F, 139.0F});
    layout.registration_panels = {{map({72.0F, 269.0F, 528.0F, 239.0F}),
                                   map({600.0F, 269.0F, 516.0F, 239.0F})}};
    layout.cabinet_panel = map({1126.0F, 125.0F, 478.0F, 745.0F});
    layout.keyboard_toolbar = map({1140.0F, 614.0F, 448.0F, 64.0F});
    layout.pedal_panel = map(kReferencePedalPanel);
    layout.footer = map({48.0F, 889.0F, 1556.0F, 36.0F});
    layout.workspace_panel = map({72.0F, 125.0F, 1528.0F, 745.0F});
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        layout.manual_panels[manual] = map(kReferenceManualPanels[manual]);
        layout.manual_rail_panels[manual] = map(kReferenceCheekPanels[manual]);
        layout.preset_key_panels[manual] = map(kReferencePresetPanels[manual]);
    }
    const UiRect envelope = map(kReferenceArtEnvelope);
    float art_width = envelope.width;
    float art_height = envelope.height;
    if (static_cast<double>(envelope.width) * 397.0 <=
        static_cast<double>(envelope.height) * 466.0)
        art_height = static_cast<float>(static_cast<double>(envelope.width) * 397.0 / 466.0);
    else
        art_width = static_cast<float>(static_cast<double>(envelope.height) * 466.0 / 397.0);
    layout.cabinet_art = {envelope.x + (envelope.width - art_width) / 2.0F,
                          envelope.y, art_width, art_height};

    // Keep the original semantic insertion order: ten common controls, then
    // each manual's edit buttons, presets and drawbars, followed by performance
    // and the five keyboard controls. Tab traversal still has 71 Play stops.
    for (std::size_t index = 0; index < kUiWorkspaceCount; ++index)
        add_reference_button(layout, scale,
            {UiControlKind::Workspace, Manual::Upper, DrawbarBank::A, static_cast<std::uint8_t>(index)},
            {100.0F + 140.0F * static_cast<float>(index), 50.0F, 130.0F, 46.0F});
    constexpr std::array<UiControlKind, 6> tool_kinds{
        UiControlKind::SaveControls, UiControlKind::LoadControls, UiControlKind::Help,
        UiControlKind::AudioSettings, UiControlKind::MidiSettings, UiControlKind::Panic};
    for (std::size_t index = 0; index < tool_kinds.size(); ++index)
        add_reference_button(layout, scale, {tool_kinds[index]},
            {1312.0F + 97.0F * static_cast<float>(index % 3),
             25.0F + 36.0F * static_cast<float>(index / 3), 88.0F, 28.0F});
    add_reference_button(layout, scale, {UiControlKind::Presentation}, {1228.0F, 78.0F, 70.0F, 24.0F});
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        const auto identity = static_cast<Manual>(manual);
        const auto& cheek = kReferenceCheekPanels[manual];
        const float button_width = (cheek.width - 24.0F) / 2.0F;
        for (std::size_t index = 0; index < 2; ++index)
            add_reference_button(layout, scale,
                {UiControlKind::EditBank, identity, static_cast<DrawbarBank>(index)},
                {cheek.x + 10.0F + static_cast<float>(index) * (button_width + 4.0F),
                 cheek.y + 51.0F, button_width, 22.0F});
        add_reference_presets(layout, scale, identity, kReferencePresetPanels[manual]);
        for (std::size_t index = 0; index < kDrawbarCount; ++index) {
            const float center = kReferenceDrawbarCenters[manual][index];
            add_reference_control(layout, scale,
                {UiControlKind::ManualDrawbar, identity, edited_banks[manual], static_cast<std::uint8_t>(index)},
                {center - 23.0F, 309.0F, 46.0F, 197.0F},
                {center - 23.0F, 467.0F, 46.0F, 23.0F},
                {center - 23.0F, 491.0F, 46.0F, 15.0F},
                {center - 2.0F, 327.0F, 4.0F, 118.0F});
        }
    }
    constexpr std::array<std::uint8_t, 4> percussion_order{0, 2, 3, 1};
    constexpr std::array<float, 4> percussion_lefts{164.0F, 256.0F, 337.0F, 418.0F};
    for (std::size_t slot = 0; slot < percussion_order.size(); ++slot) {
        const float left = percussion_lefts[slot];
        add_reference_control(layout, scale,
            {UiControlKind::Percussion, Manual::Upper, DrawbarBank::A, percussion_order[slot]},
            {left, 177.0F, 74.0F, 52.0F}, {left - 2.0F, 233.0F, 78.0F, 14.0F},
            {left + 5.0F, 183.0F, 64.0F, 38.0F});
    }
    add_reference_control(layout, scale, {UiControlKind::Expression},
        {578.0F, 165.0F, 254.0F, 85.0F}, {582.0F, 165.0F, 246.0F, 16.0F},
        {582.0F, 232.0F, 246.0F, 16.0F}, {594.0F, 200.0F, 222.0F, 4.0F});
    for (std::size_t index = 0; index < kPedalDrawbarCount; ++index) {
        const float left = 850.0F + 128.0F * static_cast<float>(index);
        add_reference_control(layout, scale,
            {UiControlKind::PedalDrawbar, Manual::Upper, DrawbarBank::A, static_cast<std::uint8_t>(index)},
            {left, 165.0F, 112.0F, 85.0F}, {left + 4.0F, 165.0F, 104.0F, 16.0F},
            {left + 74.0F, 200.0F, 32.0F, 40.0F}, {left + 41.0F, 193.0F, 4.0F, 43.0F});
    }
    for (std::size_t index = 0; index < 3; ++index)
        add_reference_button(layout, scale,
            {UiControlKind::KeyboardTarget, Manual::Upper, DrawbarBank::A, static_cast<std::uint8_t>(index)},
            {1148.0F + 148.0F * static_cast<float>(index), 616.0F, 136.0F, 26.0F});
    add_reference_button(layout, scale, {UiControlKind::OctaveDown}, {1148.0F, 648.0F, 84.0F, 26.0F});
    add_reference_button(layout, scale, {UiControlKind::OctaveUp}, {1244.0F, 648.0F, 84.0F, 26.0F});
    make_reference_keys(layout.manual_keys[0], kReferenceManualPanels[0], UiTarget::Upper, 36, scale);
    make_reference_keys(layout.manual_keys[1], kReferenceManualPanels[1], UiTarget::Lower, 36, scale);
    make_reference_keys(layout.pedal_keys, kReferencePedalPanel, UiTarget::Pedals, 15, scale);
}

[[nodiscard]] bool valid_layout(const UiLayout& layout) noexcept {
    constexpr std::size_t expected_controls =
        kUiCommonControlCount + kManualCount * (2 + kPresetSelectionCount + kDrawbarCount) +
        4 + 1 + kPedalDrawbarCount + 3 + 2;
    static_assert(expected_controls == kUiMaxControls);
    if (layout.control_count != expected_controls || !valid_workspace(layout.workspace) ||
        !valid_presentation(layout.presentation)) return false;
    const auto visible = [&layout](UiRect bounds) noexcept {
        return std::isfinite(bounds.x) && std::isfinite(bounds.y) &&
               std::isfinite(bounds.width) && std::isfinite(bounds.height) &&
               bounds.x >= 0.0F && bounds.y >= 0.0F &&
               bounds.width > 0.0F && bounds.height > 0.0F &&
               bounds.x + bounds.width <= layout.width &&
               bounds.y + bounds.height <= layout.height;
    };
    if (!visible(layout.workspace_panel)) return false;
    for (const auto& control : layout.controls) {
        if (!valid_control(control.id) || !visible(control.bounds) ||
            !visible(control.label_bounds)) return false;
    }
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        if (!visible(layout.manual_rail_panels[manual]) ||
            !visible(layout.preset_key_panels[manual])) return false;
        for (const auto& key : layout.manual_keys[manual]) {
            if (!visible(key.bounds)) return false;
        }
    }
    for (const auto& key : layout.pedal_keys) {
        if (!visible(key.bounds)) return false;
    }
    return true;
}

[[nodiscard]] bool reference_rect_valid(UiRect rect) noexcept {
    return std::isfinite(rect.x) && std::isfinite(rect.y) &&
           std::isfinite(rect.width) && std::isfinite(rect.height) &&
           std::isfinite(rect.x + rect.width) && std::isfinite(rect.y + rect.height) &&
           rect.width > 0.0F && rect.height > 0.0F;
}

[[nodiscard]] bool reference_parent_edge_matches(float first, float second) noexcept {
    // UiRect stores an extent, so reconstructing a broad parent's endpoint as
    // left + (right - left) can land one ULP from the mapped endpoint. Only
    // parent containment accepts this representation effect; adjacent targets
    // and every shared key vertex below must still join exactly.
    return first == second || first == std::nextafter(second, first);
}

[[nodiscard]] bool reference_rect_contains(UiRect owner, UiRect child) noexcept {
    return reference_rect_valid(owner) && reference_rect_valid(child) &&
           child.x >= owner.x && child.y >= owner.y &&
           (child.x + child.width <= owner.x + owner.width ||
            reference_parent_edge_matches(child.x + child.width, owner.x + owner.width)) &&
           (child.y + child.height <= owner.y + owner.height ||
            reference_parent_edge_matches(child.y + child.height, owner.y + owner.height));
}

[[nodiscard]] bool reference_rect_overlaps(UiRect first, UiRect second) noexcept {
    return first.x < second.x + second.width && second.x < first.x + first.width &&
           first.y < second.y + second.height && second.y < first.y + first.height;
}

[[nodiscard]] bool reference_same_rect(UiRect first, UiRect second) noexcept {
    return first.x == second.x && first.y == second.y &&
           first.width == second.width && first.height == second.height;
}

[[nodiscard]] bool reference_same_point(UiPoint first, UiPoint second) noexcept {
    return first.x == second.x && first.y == second.y;
}

[[nodiscard]] bool valid_reference_quad(const UiQuad& quad, UiRect owner) noexcept {
    for (const auto& point : quad.points) {
        if (!std::isfinite(point.x) || !std::isfinite(point.y) ||
            point.x < owner.x || point.x > owner.x + owner.width ||
            point.y < owner.y || point.y > owner.y + owner.height) return false;
    }
    const auto& points = quad.points;
    // Horizontal, positive-width edges at increasing y form a convex trapezoid
    // of positive area. This also rules out collapsed top/front faces.
    return points[0].y == points[1].y && points[2].y == points[3].y &&
           points[2].y > points[0].y && points[1].x > points[0].x &&
           points[2].x > points[3].x;
}

template <std::size_t Count>
[[nodiscard]] bool valid_reference_keys(const std::array<UiKeyGeometry, Count>& keys,
                                        UiRect panel, UiTarget target,
                                        std::size_t natural_count,
                                        const UiLayout& layout) noexcept {
    const UiKeyGeometry* previous_natural = nullptr;
    std::size_t naturals = 0;
    for (std::size_t index = 0; index < Count; ++index) {
        const auto& key = keys[index];
        const auto note = UiNote{target, static_cast<std::uint8_t>(
            target == UiTarget::Pedals ? index + 1 : kMinManualMidiNote + index)};
        if (!(key.note == note) || key.accidental != accidental(index) ||
            !reference_rect_contains(panel, key.bounds) ||
            !reference_same_rect(key.bounds, reference_quad_bounds(key.hit)) ||
            !valid_reference_quad(key.hit, panel) || !valid_reference_quad(key.top, panel) ||
            !valid_reference_quad(key.front, panel)) return false;
        if (!reference_same_point(key.top.points[0], key.hit.points[0]) ||
            !reference_same_point(key.top.points[1], key.hit.points[1]) ||
            !reference_same_point(key.front.points[2], key.hit.points[2]) ||
            !reference_same_point(key.front.points[3], key.hit.points[3]) ||
            !reference_same_point(key.top.points[2], key.front.points[1]) ||
            !reference_same_point(key.top.points[3], key.front.points[0])) return false;
        if (!key.accidental) {
            if (previous_natural &&
                (!reference_same_point(previous_natural->hit.points[1], key.hit.points[0]) ||
                 !reference_same_point(previous_natural->hit.points[2], key.hit.points[3]) ||
                 !reference_same_point(previous_natural->top.points[2], key.top.points[3]) ||
                 !reference_same_point(previous_natural->front.points[1], key.front.points[0]))) return false;
            previous_natural = &key;
            ++naturals;
        }
        // Perspective keys may overlap each other's AABBs. Ordinary controls
        // never occupy a playing surface, even at the transformed extremes.
        for (const auto& control : layout.controls)
            if (reference_rect_overlaps(key.bounds, control.bounds)) return false;
    }
    return naturals == natural_count;
}

[[nodiscard]] bool valid_reference_presets(const UiLayout& layout, Manual manual) noexcept {
    const auto& panel = layout.preset_key_panels[manual_index(manual)];
    const auto& canonical_panel = kReferencePresetPanels[manual_index(manual)];
    const float expected_right = reference_composition_point(
        {canonical_panel.x + canonical_panel.width, 0.0F}, reference_composition_scale(layout)).x;
    const UiControlGeometry* previous_natural = nullptr;
    std::size_t count = 0;
    std::size_t naturals = 0;
    for (const auto& control : layout.controls) {
        if (control.id.kind != UiControlKind::PresetKey || control.id.manual != manual) continue;
        if (control.id.index != count || !reference_rect_contains(panel, control.bounds) ||
            control.bounds.y != panel.y) return false;
        ++count;
        if (accidental(control.id.index)) continue;
        if (control.bounds.height != panel.height) return false;
        if (previous_natural) {
            if (previous_natural->bounds.x + previous_natural->bounds.width != control.bounds.x) return false;
        } else if (control.bounds.x != panel.x) return false;
        previous_natural = &control;
        ++naturals;
    }
    return count == kPresetSelectionCount && naturals == 7 && previous_natural &&
           previous_natural->bounds.x + previous_natural->bounds.width == expected_right;
}

[[nodiscard]] bool valid_reference_composition(const UiLayout& layout) noexcept {
    if (!reference_composition_active(layout) || !layout.show_cabinet ||
        !layout.bank_controls_in_cheeks || !layout.sidebar_pedals) return false;
    const UiRect viewport{0.0F, 0.0F, layout.width, layout.height};
    for (UiRect parent : {layout.header, layout.performance_panel, layout.keyboard_toolbar,
                          layout.pedal_panel, layout.footer, layout.cabinet_panel,
                          layout.cabinet_art, layout.workspace_panel})
        if (!reference_rect_contains(viewport, parent)) return false;
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        if (!reference_rect_contains(viewport, layout.registration_panels[manual]) ||
            !reference_rect_contains(viewport, layout.manual_panels[manual]) ||
            !reference_rect_contains(viewport, layout.manual_rail_panels[manual]) ||
            !reference_rect_contains(layout.manual_rail_panels[manual], layout.preset_key_panels[manual]) ||
            !valid_reference_presets(layout, static_cast<Manual>(manual))) return false;
    }
    if (!reference_rect_contains(layout.cabinet_panel, layout.keyboard_toolbar) ||
        !reference_rect_contains(layout.cabinet_panel, layout.pedal_panel)) return false;
    const auto scale = reference_composition_scale(layout);
    const auto map = [scale](UiRect rect) noexcept { return reference_composition_rect(rect, scale); };
    const UiRect envelope = map(kReferenceArtEnvelope);
    if (!reference_rect_contains(layout.cabinet_panel, envelope) ||
        !reference_rect_contains(envelope, layout.cabinet_art) ||
        layout.cabinet_art.y != envelope.y) return false;

    std::size_t preset_overlaps = 0;
    for (std::size_t index = 0; index < layout.control_count; ++index) {
        const auto& control = layout.controls[index];
        const auto kind = control.id.kind;
        UiRect owner;
        switch (kind) {
        case UiControlKind::Workspace:
        case UiControlKind::Presentation:
        case UiControlKind::SaveControls:
        case UiControlKind::LoadControls:
        case UiControlKind::Help:
        case UiControlKind::AudioSettings:
        case UiControlKind::MidiSettings:
        case UiControlKind::Panic: owner = layout.header; break;
        case UiControlKind::EditBank: owner = layout.manual_rail_panels[manual_index(control.id.manual)]; break;
        case UiControlKind::PresetKey: owner = layout.preset_key_panels[manual_index(control.id.manual)]; break;
        case UiControlKind::ManualDrawbar: owner = layout.registration_panels[manual_index(control.id.manual)]; break;
        case UiControlKind::Percussion:
        case UiControlKind::PedalDrawbar:
        case UiControlKind::Expression: owner = layout.performance_panel; break;
        case UiControlKind::KeyboardTarget:
        case UiControlKind::OctaveDown:
        case UiControlKind::OctaveUp: owner = layout.keyboard_toolbar; break;
        default: return false;
        }
        const bool value = kind == UiControlKind::ManualDrawbar || kind == UiControlKind::PedalDrawbar ||
                           kind == UiControlKind::Expression || kind == UiControlKind::Percussion;
        const bool track = kind == UiControlKind::ManualDrawbar || kind == UiControlKind::PedalDrawbar ||
                           kind == UiControlKind::Expression;
        if (!reference_rect_contains(owner, control.bounds) ||
            !reference_rect_contains(kind == UiControlKind::Percussion ? owner : control.bounds,
                                     control.label_bounds) ||
            (value ? !reference_rect_contains(control.bounds, control.value_bounds) :
                     !reference_same_rect(control.value_bounds, {})) ||
            (track ? !reference_rect_contains(control.bounds, control.track) :
                     !reference_same_rect(control.track, {}))) return false;
        if (kind == UiControlKind::Percussion) {
            const float cap_bottom = reference_composition_point({0.0F, 229.0F}, scale).y;
            const float legend_top = reference_composition_point({0.0F, 233.0F}, scale).y;
            if (control.bounds.y + control.bounds.height != cap_bottom ||
                control.label_bounds.y != legend_top) return false;
            for (const auto& other : layout.controls)
                if (reference_rect_overlaps(control.label_bounds, other.bounds)) return false;
        } else if (kind == UiControlKind::ManualDrawbar || kind == UiControlKind::PedalDrawbar) {
            const bool manual = kind == UiControlKind::ManualDrawbar;
            const float center = manual ? kReferenceDrawbarCenters[manual_index(control.id.manual)][control.id.index] :
                                          893.0F + 128.0F * static_cast<float>(control.id.index);
            const UiRect slot = map(manual ? UiRect{center - 21.0F, 311.0F, 42.0F, 150.0F} :
                                            UiRect{center - 21.0F, 182.0F, 42.0F, 65.0F});
            const UiRect first_cap = map(manual ? UiRect{center - 17.0F, 311.0F, 34.0F, 32.0F} :
                                                 UiRect{center - 17.0F, 182.0F, 34.0F, 22.0F});
            const UiRect last_cap = map(manual ? UiRect{center - 17.0F, 429.0F, 34.0F, 32.0F} :
                                                UiRect{center - 17.0F, 225.0F, 34.0F, 22.0F});
            const UiRect expected_track = map(manual ? UiRect{center - 2.0F, 327.0F, 4.0F, 118.0F} :
                                                      UiRect{center - 2.0F, 193.0F, 4.0F, 43.0F});
            if (!reference_rect_contains(control.bounds, slot) ||
                !reference_rect_contains(slot, first_cap) || !reference_rect_contains(slot, last_cap) ||
                !reference_same_rect(control.track, expected_track)) return false;
            if (manual) {
                if (slot.y + slot.height > control.label_bounds.y ||
                    control.label_bounds.y + control.label_bounds.height > control.value_bounds.y) return false;
            } else if (control.label_bounds.y + control.label_bounds.height > slot.y ||
                       slot.x + slot.width > control.value_bounds.x) return false;
        }
        for (std::size_t other_index = index + 1; other_index < layout.control_count; ++other_index) {
            const auto& other = layout.controls[other_index];
            if (control.id == other.id) return false;
            if (!reference_rect_overlaps(control.bounds, other.bounds)) continue;
            const int pitch_distance = static_cast<int>(other.id.index) - static_cast<int>(control.id.index);
            if (kind != UiControlKind::PresetKey || other.id.kind != UiControlKind::PresetKey ||
                control.id.manual != other.id.manual ||
                accidental(control.id.index) == accidental(other.id.index) ||
                (pitch_distance != 1 && pitch_distance != -1)) return false;
            ++preset_overlaps;
        }
    }
    return preset_overlaps == 20 &&
           valid_reference_keys(layout.manual_keys[0], layout.manual_panels[0], UiTarget::Upper, 36, layout) &&
           valid_reference_keys(layout.manual_keys[1], layout.manual_panels[1], UiTarget::Lower, 36, layout) &&
           valid_reference_keys(layout.pedal_keys, layout.pedal_panel, UiTarget::Pedals, 15, layout);
}

void move_tab_focus(UiViewState& view, const UiLayout& layout, bool backwards) noexcept {
    std::size_t count = 0;
    std::array<UiControlId, kUiMaxControls + kManualCount + 1> order{};
    for (std::size_t index = 0; index < std::min(layout.control_count, layout.controls.size()); ++index) {
        if (ui_control_visible(layout, layout.controls[index].id)) order[count++] = layout.controls[index].id;
    }
    if (layout.workspace == UiWorkspace::Play) {
        order[count++] = {UiControlKind::ManualKey, Manual::Upper, DrawbarBank::A, view.roving_manual_keys[0]};
        order[count++] = {UiControlKind::ManualKey, Manual::Lower, DrawbarBank::A, view.roving_manual_keys[1]};
        order[count++] = {UiControlKind::PedalKey, Manual::Upper, DrawbarBank::A, view.roving_pedal_key};
    }
    if (count == 0) return;
    std::size_t current = count;
    for (std::size_t index = 0; index < count; ++index) {
        if (order[index] == view.focus) { current = index; break; }
    }
    const std::size_t next = current == count ? (backwards ? count - 1 : 0) :
        (backwards ? (current + count - 1) % count : (current + 1) % count);
    focus_control(view, layout, order[next]);
}

void move_octave(UiViewState& view, bool up) noexcept {
    if (view.keyboard_target == UiTarget::Pedals) {
        const int next = static_cast<int>(view.pedal_octave) + (up ? 1 : -1);
        view.pedal_octave = static_cast<std::uint8_t>(std::clamp(next, 0, 2));
    } else {
        const int next = static_cast<int>(view.manual_base_midi) + (up ? 12 : -12);
        view.manual_base_midi = static_cast<std::uint8_t>(std::clamp(next, 36, 84));
    }
}

[[nodiscard]] bool navigation_key(UiKey key) noexcept {
    return key == UiKey::Left || key == UiKey::Right || key == UiKey::Up ||
           key == UiKey::Down || key == UiKey::Home || key == UiKey::End;
}

} // namespace

bool make_ui_layout(float width, float height,
                    const std::array<DrawbarBank, kManualCount>& edited_banks,
                    UiLayout& destination, UiWorkspace workspace,
                    UiPresentation presentation) noexcept {
    if (!std::isfinite(width) || !std::isfinite(height) ||
        width < kUiMinimumWidth || height < kUiMinimumHeight ||
        width > kUiMaximumDimension || height > kUiMaximumDimension ||
        !is_valid_drawbar_bank(edited_banks[0]) || !is_valid_drawbar_bank(edited_banks[1]) ||
        !valid_workspace(workspace) || !valid_presentation(presentation)) return false;
    UiLayout layout;
    layout.width = width;
    layout.height = height;
    layout.workspace = workspace;
    layout.presentation = presentation;
    if (reference_composition_active(layout)) {
        make_reference_composition(layout, edited_banks);
        if (!valid_layout(layout) || !valid_reference_composition(layout)) return false;
        destination = layout;
        return true;
    }
    layout.show_cabinet = width >= 1400.0F;
    layout.bank_controls_in_cheeks = height >= 820.0F;
    layout.sidebar_pedals = layout.show_cabinet && layout.bank_controls_in_cheeks;
    const bool dense = !layout.bank_controls_in_cheeks;
    const float margin = layout.show_cabinet ? std::clamp(width * 0.043F, 48.0F, 72.0F) : 16.0F;
    const float gap = dense || !layout.show_cabinet ? 8.0F : 10.0F;
    const float content_width = width - 2.0F * margin;
    const float cabinet_width = layout.show_cabinet ?
        content_width * (layout.sidebar_pedals ? 0.311F : 0.30F) : 0.0F;
    const float player_width = layout.show_cabinet ? content_width - cabinet_width - gap : content_width;
    const float header_height = layout.sidebar_pedals ? 100.0F :
        (dense || !layout.show_cabinet ? 82.0F : 90.0F);
    const float performance_height = std::clamp(76.0F + 0.12F * (height - 700.0F), 76.0F, 110.0F);
    const float rack_height = std::clamp(168.0F + 0.24F * (height - 700.0F), 168.0F, 236.0F) +
        (layout.sidebar_pedals ? 6.0F : 0.0F);
    const float pedal_height = layout.sidebar_pedals ?
        std::clamp(86.0F + 0.08F * (height - 700.0F), 86.0F, 114.0F) :
        std::clamp(58.0F + 0.08F * (height - 700.0F), 58.0F, 86.0F);
    constexpr float toolbar_height = 28.0F;
    constexpr float footer_height = 36.0F;
    const float registration_width = (player_width - gap) / 2.0F;
    // Sidebar pedals share the manuals' bottom edge instead of consuming a
    // full player-width row. Preserve the original arithmetic outside this branch.
    const float manual_height = layout.sidebar_pedals ?
        (height - 32.0F - header_height - performance_height - rack_height -
         toolbar_height - footer_height - 6.0F * gap) / 2.0F :
        (height - 32.0F - header_height - performance_height - rack_height -
         toolbar_height - pedal_height - footer_height - 7.0F * gap) / 2.0F;
    layout.header = {margin, 16.0F, content_width, header_height};
    layout.performance_panel = {margin, layout.header.y + header_height + gap, player_width, performance_height};
    const float rack_top = layout.performance_panel.y + performance_height + gap;
    layout.registration_panels[0] = {margin, rack_top, registration_width, rack_height};
    layout.registration_panels[1] = {margin + registration_width + gap, rack_top, registration_width, rack_height};
    layout.keyboard_toolbar = {margin, rack_top + rack_height + gap, player_width, toolbar_height};
    const float manual_top = layout.keyboard_toolbar.y + layout.keyboard_toolbar.height + gap;
    const float rail_width = std::clamp(player_width * 0.15F, 156.0F, 168.0F);
    const float keyboard_x = margin + rail_width + gap;
    const float keyboard_width = player_width - rail_width - gap;
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        const float y = manual_top + static_cast<float>(manual) * (manual_height + gap);
        layout.manual_rail_panels[manual] = {margin, y, rail_width, manual_height};
        layout.manual_panels[manual] = {keyboard_x, y, keyboard_width, manual_height};
        layout.preset_key_panels[manual] = {
            margin + 8.0F, y + (dense ? 22.0F : 54.0F),
            rail_width - 16.0F, manual_height - (dense ? 30.0F : 62.0F)};
    }
    if (layout.sidebar_pedals) {
        layout.footer = {margin, height - 52.0F, content_width, footer_height};
        layout.pedal_panel = {margin + player_width + gap, layout.footer.y - gap - pedal_height,
                              cabinet_width, pedal_height};
    } else {
        layout.pedal_panel = {margin, manual_top + 2.0F * (manual_height + gap), player_width, pedal_height};
        layout.footer = {margin, layout.pedal_panel.y + pedal_height + gap, content_width, footer_height};
    }
    layout.workspace_panel = {margin, layout.performance_panel.y, content_width,
                              layout.footer.y - gap - layout.performance_panel.y};
    if (layout.show_cabinet) {
        const float cabinet_bottom = layout.sidebar_pedals ? layout.pedal_panel.y - gap :
            layout.pedal_panel.y + pedal_height;
        layout.cabinet_panel = {margin + player_width + gap, layout.performance_panel.y, cabinet_width,
                               cabinet_bottom - layout.performance_panel.y};
        const auto& cabinet = layout.cabinet_panel;
        // Keep the reference crop's 466:397 aspect. The sidebar reserve leaves
        // 61 px above the status card, at least 116 px inside it and 14 px below.
        const float art_top = layout.sidebar_pedals ? 48.0F : 38.0F;
        const float art_inset = layout.sidebar_pedals ? 16.0F : 24.0F;
        const float art_reserve = layout.sidebar_pedals ? 191.0F : 176.0F;
        const float art_height = std::min((cabinet.width - art_inset) * 397.0F / 466.0F,
                                          cabinet.height - art_top - art_reserve);
        const float art_width = art_height * 466.0F / 397.0F;
        layout.cabinet_art = {cabinet.x + (cabinet.width - art_width) / 2.0F, cabinet.y + art_top,
                              art_width, art_height};
    }

    constexpr std::array<UiControlKind, 6> tool_kinds{
        UiControlKind::SaveControls, UiControlKind::LoadControls, UiControlKind::Help,
        UiControlKind::AudioSettings, UiControlKind::MidiSettings, UiControlKind::Panic};
    const float header_button_gap = layout.show_cabinet ? 8.0F : 6.0F;
    const float left_button_width = layout.show_cabinet ? 112.0F : 72.0F;
    const float right_button_width = layout.show_cabinet ? 90.0F : 72.0F;
    const float header_button_top = layout.header.y + (layout.show_cabinet ? 30.0F : 34.0F);
    const float header_button_height = layout.show_cabinet ? 42.0F : 32.0F;
    for (std::size_t index = 0; index < kUiWorkspaceCount; ++index) {
        add_button(layout, {UiControlKind::Workspace, Manual::Upper, DrawbarBank::A,
                            static_cast<std::uint8_t>(index)},
                   {margin + static_cast<float>(index) * (left_button_width + header_button_gap),
                    header_button_top, left_button_width, header_button_height});
    }
    const float right_buttons_x = margin + content_width - 3.0F * right_button_width - 2.0F * header_button_gap;
    const float tool_height = layout.show_cabinet ? 30.0F : 28.0F;
    for (std::size_t index = 0; index < tool_kinds.size(); ++index) {
        add_button(layout, {tool_kinds[index]},
                   {right_buttons_x + static_cast<float>(index % 3) * (right_button_width + header_button_gap),
                    layout.header.y + 10.0F + static_cast<float>(index / 3) * (tool_height + 6.0F),
                    right_button_width, tool_height});
    }
    const float title_left = margin + 3.0F * left_button_width + 2.0F * header_button_gap + 12.0F;
    const float title_right = right_buttons_x - 12.0F;
    const float flat_width = layout.show_cabinet ? 70.0F : 60.0F;
    add_button(layout, {UiControlKind::Presentation},
               {title_right - flat_width, layout.header.y + header_height - 30.0F,
                flat_width, 24.0F});
    // The renderer derives its title/caption allowance from the left tabs and
    // right tools. Keep a useful center region at every admitted window width.
    if (title_right - title_left < flat_width + 12.0F) return false;
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        const auto identity = static_cast<Manual>(manual);
        const auto& panel = layout.registration_panels[manual];
        const std::array<UiControlId, 2> buttons{{
            {UiControlKind::EditBank, identity, DrawbarBank::A},
            {UiControlKind::EditBank, identity, DrawbarBank::B}}};
        for (std::size_t index = 0; index < buttons.size(); ++index) {
            if (layout.bank_controls_in_cheeks) {
                const auto& rail = layout.manual_rail_panels[manual];
                const float button_width = (rail.width - 20.0F) / 2.0F;
                add_button(layout, buttons[index],
                    {rail.x + 8.0F + static_cast<float>(index) * (button_width + 4.0F),
                     rail.y + 22.0F, button_width, 24.0F});
            } else {
                const float button_width = std::min(76.0F, (panel.width - 28.0F) / 2.0F);
                add_button(layout, buttons[index],
                    {panel.x + 12.0F + static_cast<float>(index) * (button_width + 4.0F),
                     panel.y + 28.0F, button_width, 26.0F});
            }
        }
        add_preset_keys(layout, identity, layout.preset_key_panels[manual]);
        const float column_width = (panel.width - 24.0F) / static_cast<float>(kDrawbarCount);
        const float label_top = dense ? 60.0F : 32.0F;
        for (std::size_t index = 0; index < kDrawbarCount; ++index) {
            const float x = panel.x + 12.0F + static_cast<float>(index) * column_width;
            layout.controls[layout.control_count++] = {
                {UiControlKind::ManualDrawbar, identity, edited_banks[manual], static_cast<std::uint8_t>(index)},
                {x + 2.0F, panel.y + label_top, column_width - 4.0F, panel.height - label_top - 8.0F},
                {x + 2.0F, panel.y + label_top, column_width - 4.0F, 24.0F},
                {x + 2.0F, panel.y + panel.height - 24.0F, column_width - 4.0F, 16.0F},
                {x + column_width / 2.0F - 2.0F, panel.y + label_top + 38.0F,
                 4.0F, panel.height - label_top - 80.0F}};
        }
    }
    const auto& performance = layout.performance_panel;
    const float percussion_group_width = performance.width * 0.46F;
    const bool reference_percussion = layout.workspace == UiWorkspace::Play &&
        layout.sidebar_pedals && layout.presentation == UiPresentation::Dimensional;
    if (reference_percussion) {
        constexpr std::array<std::uint8_t, 4> order{0, 2, 3, 1};
        constexpr std::array<float, 4> offsets{0.0F, 92.0F, 173.0F, 254.0F};
        const float scale = std::clamp(percussion_group_width / 480.0F, 0.80F, 1.25F);
        const float percussion_width = 74.0F * scale;
        const float percussion_height = std::min(48.0F, performance.height - 43.0F);
        const float percussion_x = performance.x + 0.535F * percussion_group_width - 164.0F * scale;
        const float percussion_y = performance.y + 24.0F;
        for (std::size_t slot = 0; slot < order.size(); ++slot) {
            const float x = percussion_x + offsets[slot] * scale;
            layout.controls[layout.control_count++] = {
                {UiControlKind::Percussion, Manual::Upper, DrawbarBank::A, order[slot]},
                {x, percussion_y, percussion_width, percussion_height},
                {x - 2.0F, percussion_y + percussion_height + 2.0F, percussion_width + 4.0F, 13.0F},
                {x + 5.0F, percussion_y + 5.0F, percussion_width - 10.0F, percussion_height - 12.0F}, {}};
        }
    } else {
        const float percussion_width = (percussion_group_width - 48.0F) / 4.0F;
        for (std::size_t index = 0; index < 4; ++index) {
            const float x = performance.x + 12.0F + static_cast<float>(index) * (percussion_width + 8.0F);
            layout.controls[layout.control_count++] = {
                {UiControlKind::Percussion, Manual::Upper, DrawbarBank::A, static_cast<std::uint8_t>(index)},
                {x, performance.y + 24.0F, percussion_width, 42.0F},
                {x + 4.0F, performance.y + 28.0F, percussion_width - 8.0F, 14.0F},
                {x + 4.0F, performance.y + 44.0F, percussion_width - 8.0F, 18.0F}, {}};
        }
    }
    const float performance_right_x = performance.x + percussion_group_width + 8.0F;
    const float performance_right_width = performance.width - percussion_group_width - 8.0F;
    const float parameter_width = performance_right_width - 24.0F - 16.0F;
    const float expression_width = parameter_width * 0.46F;
    const float mixture_width = (parameter_width - expression_width) / 2.0F;
    float parameter_x = performance_right_x + 12.0F;
    for (std::size_t index = 0; index < 3; ++index) {
        const bool expression = index == 0;
        const float control_width = expression ? expression_width : mixture_width;
        layout.controls[layout.control_count++] = {
            {expression ? UiControlKind::Expression : UiControlKind::PedalDrawbar,
             Manual::Upper, DrawbarBank::A, static_cast<std::uint8_t>(expression ? 0 : index - 1)},
            {parameter_x, performance.y + 6.0F, control_width, performance.height - 10.0F},
            {parameter_x + 4.0F, performance.y + 8.0F, control_width - 8.0F, 16.0F},
            expression ? UiRect{parameter_x + 4.0F, performance.y + performance.height - 22.0F,
                                control_width - 8.0F, 16.0F} :
                         UiRect{parameter_x + control_width * 0.68F, performance.y + 34.0F,
                                control_width * 0.28F, performance.height - 42.0F},
            expression ? UiRect{parameter_x + 12.0F, performance.y + (performance.height + 4.0F) / 2.0F,
                                control_width - 24.0F, 4.0F} :
                         UiRect{parameter_x + control_width * 0.40F - 2.0F, performance.y + 36.0F,
                                4.0F, performance.height - 52.0F}};
        parameter_x += control_width + 8.0F;
    }
    const auto& toolbar = layout.keyboard_toolbar;
    float target_x = toolbar.x + 10.0F;
    for (std::size_t index = 0; index < 3; ++index) {
        add_button(layout, {UiControlKind::KeyboardTarget, Manual::Upper, DrawbarBank::A, static_cast<std::uint8_t>(index)},
                   {target_x, toolbar.y, 82.0F, toolbar.height});
        target_x += 88.0F;
    }
    add_button(layout, {UiControlKind::OctaveDown}, {target_x + 12.0F, toolbar.y, 74.0F, toolbar.height});
    add_button(layout, {UiControlKind::OctaveUp}, {target_x + 92.0F, toolbar.y, 74.0F, toolbar.height});
    make_keys(layout.manual_keys[0], layout.manual_panels[0], UiTarget::Upper, 36, presentation);
    make_keys(layout.manual_keys[1], layout.manual_panels[1], UiTarget::Lower, 36, presentation);
    make_keys(layout.pedal_keys, layout.pedal_panel, UiTarget::Pedals, 15, presentation);
    if (!valid_layout(layout)) return false;
    destination = layout;
    return true;
}

bool ui_control_visible(const UiLayout& layout, UiControlId control) noexcept {
    if (!valid_workspace(layout.workspace) || !valid_presentation(layout.presentation) ||
        !valid_control(control)) return false;
    if (is_playing_control(control)) return layout.workspace == UiWorkspace::Play;
    const bool common = control.kind == UiControlKind::Workspace ||
        control.kind == UiControlKind::Presentation || control.kind == UiControlKind::SaveControls ||
        control.kind == UiControlKind::LoadControls || control.kind == UiControlKind::Help ||
        control.kind == UiControlKind::AudioSettings || control.kind == UiControlKind::MidiSettings ||
        control.kind == UiControlKind::Panic;
    if (!common && layout.workspace != UiWorkspace::Play) return false;
    const auto count = std::min(layout.control_count, layout.controls.size());
    for (std::size_t index = 0; index < count; ++index) {
        if (layout.controls[index].id == control) return true;
    }
    return false;
}

UiControlId ui_hit_test(const UiLayout& layout, UiPoint point) noexcept {
    if (!std::isfinite(point.x) || !std::isfinite(point.y) ||
        !valid_workspace(layout.workspace) || !valid_presentation(layout.presentation)) return {};
    const auto count = std::min(layout.control_count, layout.controls.size());
    // Preset semantic order is pitch order, so explicitly give short ivory
    // accidentals precedence over the overlapping dark natural rectangles.
    for (const bool sharp : {true, false}) {
        for (std::size_t index = 0; index < count; ++index) {
            const auto& control = layout.controls[index];
            if (control.id.kind == UiControlKind::PresetKey && ui_control_visible(layout, control.id) &&
                accidental(control.id.index) == sharp && control.bounds.contains(point)) return control.id;
        }
    }
    // Accidentals have visual and hit precedence over their underlying naturals.
    for (const bool black : {true, false}) {
        if (layout.workspace != UiWorkspace::Play) break;
        for (const auto& manual : layout.manual_keys) {
            for (const auto& key : manual) {
                if (key.accidental == black && key.hit.contains(point)) return note_control(key.note);
            }
        }
        for (const auto& key : layout.pedal_keys) {
            if (key.accidental == black && key.hit.contains(point)) return note_control(key.note);
        }
    }
    for (std::size_t index = 0; index < count; ++index) {
        if (layout.controls[index].id.kind != UiControlKind::PresetKey &&
            ui_control_visible(layout, layout.controls[index].id) &&
            layout.controls[index].bounds.contains(point)) return layout.controls[index].id;
    }
    return {};
}

bool ui_parameter_id(UiControlId control, std::uint32_t& destination) noexcept {
    if (!valid_control(control)) return false;
    std::uint32_t parameter = 0;
    switch (control.kind) {
    case UiControlKind::ManualDrawbar:
        parameter = 4096U + 32U * static_cast<std::uint32_t>(control.manual) +
                    16U * static_cast<std::uint32_t>(control.bank) + control.index;
        break;
    case UiControlKind::SoundingBank: parameter = 8208U + static_cast<std::uint32_t>(control.manual); break;
    case UiControlKind::PresetKey: parameter = 20480U + static_cast<std::uint32_t>(control.manual); break;
    case UiControlKind::Expression: parameter = 8192U; break;
    case UiControlKind::Percussion: parameter = 12288U + control.index; break;
    case UiControlKind::PedalDrawbar: parameter = 16384U + control.index; break;
    default: return false;
    }
    ParameterDescriptor descriptor;
    if (!parameter_descriptor(parameter, descriptor)) return false;
    destination = parameter;
    return true;
}

UiModel::UiModel() noexcept {
    saved_controls_ = view_.controls;
    const bool valid = make_ui_layout(kUiReferenceWidth, kUiReferenceHeight, view_.edited_banks, layout_);
    (void)valid;
}

bool UiModel::resize(float width, float height) noexcept {
    UiLayout candidate;
    if (!make_ui_layout(width, height, view_.edited_banks, candidate,
                        view_.workspace, view_.presentation)) return false;
    layout_ = candidate;
    drag_ = {};
    if (pointer_down_) pointer_suppressed_ = true;
    return true;
}

bool UiModel::set_workspace(UiWorkspace workspace) noexcept {
    if (!valid_workspace(workspace)) return false;
    if (workspace == view_.workspace) return true;
    UiLayout candidate;
    if (!make_ui_layout(layout_.width, layout_.height, view_.edited_banks, candidate,
                        workspace, view_.presentation)) return false;
    const auto remembered = view_.workspace_focus[static_cast<std::size_t>(workspace)];
    const UiControlId focus = ui_control_visible(candidate, remembered) &&
        remembered.kind != UiControlKind::Workspace ? remembered :
        UiControlId{UiControlKind::Workspace, Manual::Upper, DrawbarBank::A,
                    static_cast<std::uint8_t>(workspace)};
    layout_ = candidate;
    view_.workspace = workspace;
    focus_control(view_, layout_, focus);
    drag_ = {};
    if (pointer_down_) pointer_suppressed_ = true;
    return true;
}

bool UiModel::set_presentation(UiPresentation presentation) noexcept {
    if (!valid_presentation(presentation)) return false;
    if (presentation == view_.presentation) return true;
    UiLayout candidate;
    if (!make_ui_layout(layout_.width, layout_.height, view_.edited_banks, candidate,
                        view_.workspace, presentation)) return false;
    layout_ = candidate;
    view_.presentation = presentation;
    drag_ = {};
    if (pointer_down_) pointer_suppressed_ = true;
    return true;
}

UiActions UiModel::activate(UiControlId control) noexcept {
    if (!valid_control(control)) return {};
    const bool compatibility = view_.workspace == UiWorkspace::Play &&
        (control.kind == UiControlKind::SoundingBank || control.kind == UiControlKind::CancelManual);
    if (!compatibility && !ui_control_visible(layout_, control)) return {};
    // Switching first preserves the outgoing body's focus memory. Clicking the
    // currently selected tab is an idempotent operation, not a focus change.
    if (control.kind == UiControlKind::Workspace) {
        const bool valid = set_workspace(static_cast<UiWorkspace>(control.index));
        (void)valid;
        return {};
    }
    if (control.kind == UiControlKind::Presentation) {
        const bool valid = set_presentation(view_.presentation == UiPresentation::Dimensional ?
                                            UiPresentation::Flat : UiPresentation::Dimensional);
        (void)valid;
        return {};
    }
    // An explicit activation can focus a playing key but has no implicit
    // note lifetime. Only pointer/Space/physical-key events create owners.
    focus_control(view_, layout_, control);
    switch (control.kind) {
    case UiControlKind::EditBank: {
        const auto manual = manual_index(control.manual);
        if (view_.edited_banks[manual] == control.bank) return {};
        drag_ = {};
        if (pointer_down_) pointer_suppressed_ = true;
        view_.edited_banks[manual] = control.bank;
        const bool valid = make_ui_layout(layout_.width, layout_.height, view_.edited_banks, layout_,
                                          view_.workspace, view_.presentation);
        (void)valid;
        return {};
    }
    case UiControlKind::SoundingBank:
    case UiControlKind::PresetKey:
    case UiControlKind::Percussion: {
        std::uint32_t parameter = 0;
        double plain = 0.0;
        if (!ui_parameter_id(control, parameter) || !control_plain(view_.controls, control, plain)) return {};
        if (control.kind == UiControlKind::PresetKey) plain = control.index;
        else if (control.kind == UiControlKind::SoundingBank) plain = static_cast<double>(control.bank);
        else plain = plain == 0.0 ? 1.0 : 0.0;
        double normalized = 0.0;
        ControlSnapshot candidate;
        if (!plain_to_normalized(parameter, plain, normalized) ||
            !apply_parameter(view_.controls, parameter, normalized, candidate)) return {};
        return publish_controls(view_, saved_controls_, pending_control_sequence_, candidate,
                                control.kind == UiControlKind::PresetKey);
    }
    case UiControlKind::CancelManual: {
        ControlState candidate;
        if (!candidate.restore(view_.controls) || !candidate.cancel(control.manual)) return {};
        return publish_controls(view_, saved_controls_, pending_control_sequence_, candidate.snapshot());
    }
    case UiControlKind::KeyboardTarget:
        view_.keyboard_target = static_cast<UiTarget>(control.index);
        return {};
    case UiControlKind::OctaveDown: move_octave(view_, false); return {};
    case UiControlKind::OctaveUp: move_octave(view_, true); return {};
    case UiControlKind::SaveControls: return one_request(UiAppRequest::SaveControls);
    case UiControlKind::LoadControls: return one_request(UiAppRequest::LoadControls);
    case UiControlKind::AudioSettings: return one_request(UiAppRequest::AudioSettings);
    case UiControlKind::Help: return one_request(UiAppRequest::Help);
    case UiControlKind::MidiSettings: return one_request(UiAppRequest::MidiSettings);
    case UiControlKind::Panic: return panic();
    default: return {};
    }
}

UiActions UiModel::key(const UiKeyInput& input) noexcept {
    const auto key_index = static_cast<std::size_t>(input.key);
    if (input.key == UiKey::Unknown || key_index >= physical_keys_down_.size()) return {};
    std::size_t playing_slot = kUiPlayingKeys.size();
    for (std::size_t index = 0; index < kUiPlayingKeys.size(); ++index) {
        if (kUiPlayingKeys[index] == input.key) { playing_slot = index; break; }
    }
    // Releases precede every shortcut/text/modifier gate and use only the
    // original captured identity. Space has an independent audition owner.
    if (!input.down) {
        physical_keys_down_[key_index] = false;
        suppressed_keys_[key_index] = false;
        if (playing_slot != kUiPlayingKeys.size()) return release_press(keyboard_holds_[playing_slot]);
        if (input.key == UiKey::Space) return release_press(audition_hold_);
        return {};
    }
    const bool was_down = physical_keys_down_[key_index];
    physical_keys_down_[key_index] = true;
    if (was_down || input.repeat || suppressed_keys_[key_index]) return {};
    if (input.key == UiKey::Escape) return release_ui(UiReleaseReason::Escape);
    if (view_.text_entry_active || input.control || input.alt || input.meta) {
        suppressed_keys_[key_index] = true;
        return {};
    }
    if (playing_slot != kUiPlayingKeys.size()) {
        const int value = view_.keyboard_target == UiTarget::Pedals ?
            1 + 12 * static_cast<int>(view_.pedal_octave) + static_cast<int>(playing_slot) :
            static_cast<int>(view_.manual_base_midi) + static_cast<int>(playing_slot);
        if ((view_.keyboard_target == UiTarget::Pedals && value > static_cast<int>(kPedalCount)) ||
            (view_.keyboard_target != UiTarget::Pedals && value > kMaxManualMidiNote)) return {};
        auto& hold = keyboard_holds_[playing_slot];
        hold = {true, {view_.keyboard_target, static_cast<std::uint8_t>(value)},
                kUiKeyboardOwnerBase + static_cast<std::int32_t>(playing_slot)};
        return one_command(note_command(hold, true));
    }
    switch (input.key) {
    case UiKey::F1: view_.keyboard_target = UiTarget::Upper; return {};
    case UiKey::F2: view_.keyboard_target = UiTarget::Lower; return {};
    case UiKey::F3: view_.keyboard_target = UiTarget::Pedals; return {};
    case UiKey::F4:
    case UiKey::F5:
    case UiKey::F6: {
        const bool valid = set_workspace(input.key == UiKey::F4 ? UiWorkspace::Play :
            input.key == UiKey::F5 ? UiWorkspace::Rotary : UiWorkspace::Service);
        (void)valid;
        return {};
    }
    case UiKey::F7: {
        const bool valid = set_presentation(view_.presentation == UiPresentation::Dimensional ?
                                            UiPresentation::Flat : UiPresentation::Dimensional);
        (void)valid;
        return {};
    }
    case UiKey::LeftBracket: move_octave(view_, false); return {};
    case UiKey::RightBracket: move_octave(view_, true); return {};
    case UiKey::Tab: move_tab_focus(view_, layout_, input.shift); return {};
    case UiKey::Space:
        if (ui_control_visible(layout_, view_.focus) && is_playing_control(view_.focus)) {
            audition_hold_ = {true, control_note(view_.focus), kUiAuditionOwnerId};
            return one_command(note_command(audition_hold_, true));
        }
        return activate(view_.focus);
    case UiKey::Enter:
        if (!is_playing_control(view_.focus)) return activate(view_.focus);
        return {};
    default: break;
    }
    if (!navigation_key(input.key) || !ui_control_visible(layout_, view_.focus)) return {};
    if (view_.focus.kind == UiControlKind::PresetKey) {
        auto focus = view_.focus;
        int next = focus.index;
        switch (input.key) {
        case UiKey::Left: --next; break;
        case UiKey::Right: ++next; break;
        case UiKey::Up: focus.manual = Manual::Upper; break;
        case UiKey::Down: focus.manual = Manual::Lower; break;
        case UiKey::Home: next = 0; break;
        case UiKey::End: next = static_cast<int>(kPresetSelectionCount) - 1; break;
        default: break;
        }
        focus.index = static_cast<std::uint8_t>(std::clamp(next, 0, static_cast<int>(kPresetSelectionCount) - 1));
        focus_control(view_, layout_, focus);
        return {};
    }
    if (is_playing_control(view_.focus)) {
        const int last = view_.focus.kind == UiControlKind::ManualKey ?
            static_cast<int>(kManualKeyCount) - 1 : static_cast<int>(kPedalCount) - 1;
        int next = view_.focus.index;
        switch (input.key) {
        case UiKey::Left: --next; break;
        case UiKey::Right: ++next; break;
        case UiKey::Up: next += 12; break;
        case UiKey::Down: next -= 12; break;
        case UiKey::Home: next = 0; break;
        case UiKey::End: next = last; break;
        default: break;
        }
        auto focus = view_.focus;
        focus.index = static_cast<std::uint8_t>(std::clamp(next, 0, last));
        focus_control(view_, layout_, focus);
        return {};
    }
    const auto kind = view_.focus.kind;
    if (kind != UiControlKind::ManualDrawbar && kind != UiControlKind::PedalDrawbar &&
        kind != UiControlKind::Expression) return {};
    std::uint32_t parameter = 0;
    double plain = 0.0;
    if (!ui_parameter_id(view_.focus, parameter) || !control_plain(view_.controls, view_.focus, plain)) return {};
    ParameterDescriptor descriptor;
    if (!parameter_descriptor(parameter, descriptor)) return {};
    const double step = kind == UiControlKind::Expression ? (input.shift ? 0.01 : 0.05) : 1.0;
    if (input.key == UiKey::Home) plain = 0.0;
    else if (input.key == UiKey::End) plain = descriptor.maximum;
    else plain = std::clamp(plain + (input.key == UiKey::Up || input.key == UiKey::Right ? step : -step),
                            0.0, descriptor.maximum);
    double normalized = 0.0;
    ControlSnapshot candidate;
    if (!plain_to_normalized(parameter, plain, normalized) ||
        !apply_parameter(view_.controls, parameter, normalized, candidate)) return {};
    return publish_controls(view_, saved_controls_, pending_control_sequence_, candidate);
}

UiActions UiModel::pointer(const UiPointerInput& input) noexcept {
    if (input.kind == UiPointerKind::Up || input.kind == UiPointerKind::CaptureLost) {
        auto actions = release_press(pointer_hold_);
        pointer_down_ = false;
        pointer_suppressed_ = input.kind == UiPointerKind::CaptureLost;
        view_.pointer_captured = false;
        drag_ = {};
        return actions;
    }
    if (input.kind == UiPointerKind::Down) {
        if (pointer_down_) return {};
        pointer_down_ = true;
        pointer_suppressed_ = true;
        const auto control = ui_hit_test(layout_, input.point);
        if (!valid_control(control)) return {};
        if (control.kind == UiControlKind::Workspace || control.kind == UiControlKind::Presentation)
            return activate(control);
        focus_control(view_, layout_, control);
        if (is_playing_control(control)) {
            pointer_suppressed_ = false;
            view_.pointer_captured = true;
            pointer_hold_ = {true, control_note(control), kUiPointerOwnerId};
            return one_command(note_command(pointer_hold_, true));
        }
        if (control.kind == UiControlKind::ManualDrawbar || control.kind == UiControlKind::PedalDrawbar ||
            control.kind == UiControlKind::Expression) {
            for (std::size_t index = 0; index < layout_.control_count; ++index) {
                const auto& geometry = layout_.controls[index];
                if (!(geometry.id == control)) continue;
                std::uint32_t parameter = 0;
                if (!ui_parameter_id(control, parameter)) return {};
                drag_ = {true, control, parameter, geometry.track};
                view_.pointer_captured = true;
                ControlSnapshot candidate;
                if (!parameter_at_point(drag_, input.point, view_.controls, candidate)) return {};
                return publish_controls(view_, saved_controls_, pending_control_sequence_, candidate);
            }
            return {};
        }
        return activate(control);
    }
    if (input.kind != UiPointerKind::Move || !pointer_down_ || !view_.pointer_captured) return {};
    if (drag_.active) {
        ControlSnapshot candidate;
        if (!parameter_at_point(drag_, input.point, view_.controls, candidate)) return {};
        return publish_controls(view_, saved_controls_, pending_control_sequence_, candidate);
    }
    if (pointer_suppressed_) return {};
    const auto control = ui_hit_test(layout_, input.point);
    const bool on_key = valid_control(control) && is_playing_control(control);
    const auto note = on_key ? control_note(control) : UiNote{};
    if (pointer_hold_.active && on_key && pointer_hold_.note == note) return {};
    UiActions actions;
    if (pointer_hold_.active) {
        actions.items[actions.count++] = note_command(pointer_hold_, false);
        pointer_hold_ = {};
    }
    if (on_key) {
        pointer_hold_ = {true, note, kUiPointerOwnerId};
        actions.items[actions.count++] = note_command(pointer_hold_, true);
        focus_control(view_, layout_, control);
    }
    return actions;
}

UiActions UiModel::release_ui(UiReleaseReason reason) noexcept {
    (void)reason;
    keyboard_holds_ = {};
    pointer_hold_ = {};
    audition_hold_ = {};
    suppressed_keys_ = physical_keys_down_;
    pointer_suppressed_ = pointer_down_;
    drag_ = {};
    view_.pointer_captured = false;
    return one_command(SessionCommand{ReleaseUiNotes{}});
}

UiActions UiModel::panic() noexcept {
    const auto released = release_ui(UiReleaseReason::Escape);
    (void)released;
    return one_command(SessionCommand{Panic{}});
}

UiActions UiModel::load_controls(const ControlSnapshot& controls) noexcept {
    if (!is_valid_control_snapshot(controls)) return {};
    saved_controls_ = controls;
    return publish_controls(view_, saved_controls_, pending_control_sequence_, controls, true);
}

UiActions UiModel::recall_controls(const ControlSnapshot& controls) noexcept {
    if (!is_valid_control_snapshot(controls)) return {};
    return publish_controls(view_, saved_controls_, pending_control_sequence_, controls, true);
}

UiActions UiModel::external_parameter(std::uint32_t parameter_id,
                                    double normalized) noexcept {
    if (!std::isfinite(normalized) || normalized < 0.0 || normalized > 1.0) return {};
    ControlSnapshot candidate;
    if (!apply_parameter(view_.controls, parameter_id, normalized, candidate)) return {};
    return publish_controls(view_, saved_controls_, pending_control_sequence_, candidate);
}

void UiModel::mark_saved(const ControlSnapshot& saved_controls) noexcept {
    if (!is_valid_control_snapshot(saved_controls)) return;
    saved_controls_ = saved_controls;
    view_.controls_dirty = !(view_.controls == saved_controls_);
}

void UiModel::set_text_entry_active(bool active) noexcept {
    view_.text_entry_active = active;
}

UiActions UiModel::submitted(const SessionCommand& command, const SubmitResult& result) noexcept {
    view_.last_submit_status = result.status;
    if (result.ok()) {
        if (std::holds_alternative<ControlSnapshot>(command)) {
            pending_control_sequence_ = result.sequence;
            view_.controls_pending = true;
        }
        return {};
    }
    // No unaccepted local owner may survive a transport rejection, including
    // the On already staged by a glissando whose preceding Off was rejected.
    const auto released = release_ui(UiReleaseReason::Escape);
    (void)released;
    view_.input_recovery = true;
    pending_control_sequence_ = 0;
    view_.controls_pending = false;
    view_.controls = view_.applied.controls;
    view_.controls_dirty = !(view_.controls == saved_controls_);
    if (result.status == SessionStatus::InvalidCommand && !invalid_release_requested_) {
        invalid_release_requested_ = true;
        if (!std::holds_alternative<ReleaseUiNotes>(command)) {
            return one_command(SessionCommand{ReleaseUiNotes{}});
        }
    }
    // QueueFull/RecoveryPending/SequenceExhausted use Session's out-of-band
    // global recovery. Reposting a command here would only amplify the fault.
    return {};
}

void UiModel::observe(const SessionSnapshot& snapshot) noexcept {
    if (snapshot.publication_revision < view_.applied.publication_revision ||
        !is_valid_control_snapshot(snapshot.controls)) return;
    const bool recovery = snapshot.recovery_count > view_.applied.recovery_count;
    view_.applied = snapshot;
    if (recovery) {
        const auto released = release_ui(UiReleaseReason::Escape);
        (void)released;
        pending_control_sequence_ = 0;
        view_.controls_pending = false;
        view_.input_recovery = true;
        invalid_release_requested_ = false;
    } else if (pending_control_sequence_ != 0 && snapshot.resolved_sequence >= pending_control_sequence_) {
        pending_control_sequence_ = 0;
        view_.controls_pending = false;
    }
    if (!view_.controls_pending) {
        view_.controls = snapshot.controls;
        view_.controls_dirty = !(view_.controls == saved_controls_);
    }
}

} // namespace hammond::standalone
