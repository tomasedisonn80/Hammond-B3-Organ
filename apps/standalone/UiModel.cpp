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

void focus_control(UiViewState& view, UiControlId id) noexcept {
    view.focus = id;
    if (id.kind == UiControlKind::ManualKey) view.roving_manual_keys[manual_index(id.manual)] = id.index;
    if (id.kind == UiControlKind::PedalKey) view.roving_pedal_key = id.index;
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
               UiTarget target, std::size_t natural_count) noexcept {
    const float left = panel.x + 8.0F;
    const float top = panel.y + 22.0F;
    const float width = panel.width - 16.0F;
    const float height = panel.height - 30.0F;
    const float natural_width = width / static_cast<float>(natural_count);
    const float black_width = natural_width * 0.60F;
    std::size_t natural = 0;
    for (std::size_t index = 0; index < Count; ++index) {
        auto& key = keys[index];
        key.note = {target, static_cast<std::uint8_t>(
            target == UiTarget::Pedals ? index + 1 : kMinManualMidiNote + index)};
        key.accidental = accidental(index);
        if (key.accidental) {
            key.bounds = {left + static_cast<float>(natural) * natural_width - black_width / 2.0F,
                          top, black_width, height * 0.62F};
        } else {
            // Derive both edges from their ordinal. The last edge is exactly
            // the keyboard boundary, so accumulated rounding creates no gaps.
            const float start = left + width * static_cast<float>(natural) / static_cast<float>(natural_count);
            const float end = left + width * static_cast<float>(natural + 1) / static_cast<float>(natural_count);
            key.bounds = {start, top, end - start, height};
            ++natural;
        }
    }
}

void add_button(UiLayout& layout, UiControlId id, UiRect bounds) noexcept {
    layout.controls[layout.control_count++] = {
        id, bounds, {bounds.x + 4.0F, bounds.y + 4.0F, bounds.width - 8.0F, bounds.height - 8.0F}, {}, {}};
}

void move_tab_focus(UiViewState& view, const UiLayout& layout, bool backwards) noexcept {
    const std::size_t count = layout.control_count + kManualCount + 1;
    std::array<UiControlId, kUiMaxControls + kManualCount + 1> order{};
    for (std::size_t index = 0; index < layout.control_count; ++index) order[index] = layout.controls[index].id;
    order[layout.control_count] = {UiControlKind::ManualKey, Manual::Upper, DrawbarBank::A, view.roving_manual_keys[0]};
    order[layout.control_count + 1] = {UiControlKind::ManualKey, Manual::Lower, DrawbarBank::A, view.roving_manual_keys[1]};
    order[layout.control_count + 2] = {UiControlKind::PedalKey, Manual::Upper, DrawbarBank::A, view.roving_pedal_key};
    std::size_t current = count;
    for (std::size_t index = 0; index < count; ++index) {
        if (order[index] == view.focus) { current = index; break; }
    }
    const std::size_t next = current == count ? (backwards ? count - 1 : 0) :
        (backwards ? (current + count - 1) % count : (current + 1) % count);
    focus_control(view, order[next]);
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
                    UiLayout& destination) noexcept {
    if (!std::isfinite(width) || !std::isfinite(height) ||
        width < kUiMinimumWidth || height < kUiMinimumHeight ||
        width > kUiMaximumDimension || height > kUiMaximumDimension ||
        !is_valid_drawbar_bank(edited_banks[0]) || !is_valid_drawbar_bank(edited_banks[1])) return false;
    UiLayout layout;
    layout.width = width;
    layout.height = height;
    const float margin = width >= 1120.0F ? 24.0F : 16.0F;
    const float gap = 12.0F;
    const float content_width = width - 2.0F * margin;
    const float rack_height = height >= 820.0F ? 248.0F : 208.0F;
    const float pedal_height = height >= 820.0F ? 112.0F : 88.0F;
    const float performance_width = width >= 1120.0F ? 288.0F : 236.0F;
    const float registration_width = (content_width - performance_width - 2.0F * gap) / 2.0F;
    const float manual_height = (height - 2.0F * margin - 56.0F - rack_height -
                                32.0F - pedal_height - 40.0F - 6.0F * gap) / 2.0F;
    layout.header = {margin, margin, content_width, 56.0F};
    const float rack_top = margin + 56.0F + gap;
    layout.registration_panels[0] = {margin, rack_top, registration_width, rack_height};
    layout.registration_panels[1] = {margin + registration_width + gap, rack_top, registration_width, rack_height};
    layout.performance_panel = {margin + 2.0F * (registration_width + gap), rack_top, performance_width, rack_height};
    layout.keyboard_toolbar = {margin, rack_top + rack_height + gap, content_width, 32.0F};
    const float manual_top = layout.keyboard_toolbar.y + layout.keyboard_toolbar.height + gap;
    layout.manual_panels[0] = {margin, manual_top, content_width, manual_height};
    layout.manual_panels[1] = {margin, manual_top + manual_height + gap, content_width, manual_height};
    layout.pedal_panel = {margin, manual_top + 2.0F * (manual_height + gap), content_width, pedal_height};
    layout.footer = {margin, layout.pedal_panel.y + pedal_height + gap, content_width, 40.0F};

    constexpr std::array<UiControlKind, 5> header_kinds{
        UiControlKind::SaveControls, UiControlKind::LoadControls, UiControlKind::AudioSettings,
        UiControlKind::Help, UiControlKind::Panic};
    constexpr std::array<float, 5> header_widths{72.0F, 72.0F, 88.0F, 64.0F, 80.0F};
    float button_x = margin + content_width - 408.0F;
    for (std::size_t index = 0; index < header_kinds.size(); ++index) {
        add_button(layout, {header_kinds[index]}, {button_x, margin + 10.0F, header_widths[index], 36.0F});
        button_x += header_widths[index] + 8.0F;
    }
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        const auto identity = static_cast<Manual>(manual);
        const auto& panel = layout.registration_panels[manual];
        const float button_width = (panel.width - 36.0F) / 5.0F;
        const std::array<UiControlId, 5> buttons{{
            {UiControlKind::EditBank, identity, DrawbarBank::A},
            {UiControlKind::EditBank, identity, DrawbarBank::B},
            {UiControlKind::SoundingBank, identity, DrawbarBank::A},
            {UiControlKind::SoundingBank, identity, DrawbarBank::B},
            {UiControlKind::CancelManual, identity}}};
        for (std::size_t index = 0; index < buttons.size(); ++index) {
            add_button(layout, buttons[index],
                {panel.x + 10.0F + static_cast<float>(index) * (button_width + 4.0F),
                 panel.y + 28.0F, button_width, 32.0F});
        }
        const float column_width = (panel.width - 20.0F) / static_cast<float>(kDrawbarCount);
        for (std::size_t index = 0; index < kDrawbarCount; ++index) {
            const float x = panel.x + 10.0F + static_cast<float>(index) * column_width;
            layout.controls[layout.control_count++] = {
                {UiControlKind::ManualDrawbar, identity, edited_banks[manual], static_cast<std::uint8_t>(index)},
                {x + 2.0F, panel.y + 82.0F, column_width - 4.0F, panel.height - 92.0F},
                {x + 2.0F, panel.y + 84.0F, column_width - 4.0F, 28.0F},
                {x + 2.0F, panel.y + panel.height - 28.0F, column_width - 4.0F, 18.0F},
                {x + column_width / 2.0F - 2.0F, panel.y + 124.0F, 4.0F, panel.height - 168.0F}};
        }
    }
    const auto& performance = layout.performance_panel;
    const float percussion_width = (performance.width - 32.0F) / 4.0F;
    for (std::size_t index = 0; index < 4; ++index) {
        const float x = performance.x + 10.0F + static_cast<float>(index) * (percussion_width + 4.0F);
        layout.controls[layout.control_count++] = {
            {UiControlKind::Percussion, Manual::Upper, DrawbarBank::A, static_cast<std::uint8_t>(index)},
            {x, performance.y + 28.0F, percussion_width, 40.0F},
            {x + 2.0F, performance.y + 31.0F, percussion_width - 4.0F, 14.0F},
            {x + 2.0F, performance.y + 47.0F, percussion_width - 4.0F, 18.0F}, {}};
    }
    const float lower_column = (performance.width - 20.0F) / 3.0F;
    for (std::size_t index = 0; index < 3; ++index) {
        const float x = performance.x + 10.0F + static_cast<float>(index) * lower_column;
        const bool expression = index == 0;
        layout.controls[layout.control_count++] = {
            {expression ? UiControlKind::Expression : UiControlKind::PedalDrawbar,
             Manual::Upper, DrawbarBank::A, static_cast<std::uint8_t>(expression ? 0 : index - 1)},
            {x + 2.0F, performance.y + 102.0F, lower_column - 4.0F, performance.height - 112.0F},
            {x + 2.0F, performance.y + 104.0F, lower_column - 4.0F, 28.0F},
            {x + 2.0F, performance.y + performance.height - 28.0F, lower_column - 4.0F, 18.0F},
            expression ? UiRect{x + 12.0F, performance.y + (performance.height + 106.0F) / 2.0F,
                                lower_column - 24.0F, 4.0F} :
                         UiRect{x + lower_column / 2.0F - 2.0F, performance.y + 144.0F,
                                4.0F, performance.height - 188.0F}};
    }
    const auto& toolbar = layout.keyboard_toolbar;
    float target_x = toolbar.x + 10.0F;
    for (std::size_t index = 0; index < 3; ++index) {
        add_button(layout, {UiControlKind::KeyboardTarget, Manual::Upper, DrawbarBank::A, static_cast<std::uint8_t>(index)},
                   {target_x, toolbar.y, 82.0F, 32.0F});
        target_x += 88.0F;
    }
    add_button(layout, {UiControlKind::OctaveDown}, {target_x + 12.0F, toolbar.y, 74.0F, 32.0F});
    add_button(layout, {UiControlKind::OctaveUp}, {target_x + 92.0F, toolbar.y, 74.0F, 32.0F});
    make_keys(layout.manual_keys[0], layout.manual_panels[0], UiTarget::Upper, 36);
    make_keys(layout.manual_keys[1], layout.manual_panels[1], UiTarget::Lower, 36);
    make_keys(layout.pedal_keys, layout.pedal_panel, UiTarget::Pedals, 15);
    destination = layout;
    return true;
}

UiControlId ui_hit_test(const UiLayout& layout, UiPoint point) noexcept {
    if (!std::isfinite(point.x) || !std::isfinite(point.y)) return {};
    // Accidentals have visual and hit precedence over their underlying naturals.
    for (const bool black : {true, false}) {
        for (const auto& manual : layout.manual_keys) {
            for (const auto& key : manual) {
                if (key.accidental == black && key.bounds.contains(point)) return note_control(key.note);
            }
        }
        for (const auto& key : layout.pedal_keys) {
            if (key.accidental == black && key.bounds.contains(point)) return note_control(key.note);
        }
    }
    const auto count = std::min(layout.control_count, layout.controls.size());
    for (std::size_t index = 0; index < count; ++index) {
        if (layout.controls[index].bounds.contains(point)) return layout.controls[index].id;
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
    if (!make_ui_layout(width, height, view_.edited_banks, candidate)) return false;
    layout_ = candidate;
    drag_ = {};
    return true;
}

UiActions UiModel::activate(UiControlId control) noexcept {
    if (!valid_control(control)) return {};
    // An explicit activation can focus a playing key but has no implicit
    // note lifetime. Only pointer/Space/physical-key events create owners.
    focus_control(view_, control);
    switch (control.kind) {
    case UiControlKind::EditBank: {
        const auto manual = manual_index(control.manual);
        if (view_.edited_banks[manual] == control.bank) return {};
        drag_ = {};
        view_.edited_banks[manual] = control.bank;
        const bool valid = make_ui_layout(layout_.width, layout_.height, view_.edited_banks, layout_);
        (void)valid;
        return {};
    }
    case UiControlKind::SoundingBank:
    case UiControlKind::Percussion: {
        std::uint32_t parameter = 0;
        double plain = 0.0;
        if (!ui_parameter_id(control, parameter) || !control_plain(view_.controls, control, plain)) return {};
        plain = control.kind == UiControlKind::SoundingBank ?
            static_cast<double>(control.bank) : (plain == 0.0 ? 1.0 : 0.0);
        double normalized = 0.0;
        ControlSnapshot candidate;
        if (!plain_to_normalized(parameter, plain, normalized) ||
            !apply_parameter(view_.controls, parameter, normalized, candidate)) return {};
        return publish_controls(view_, saved_controls_, pending_control_sequence_, candidate);
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
    case UiKey::LeftBracket: move_octave(view_, false); return {};
    case UiKey::RightBracket: move_octave(view_, true); return {};
    case UiKey::Tab: move_tab_focus(view_, layout_, input.shift); return {};
    case UiKey::Space:
        if (valid_control(view_.focus) && is_playing_control(view_.focus)) {
            audition_hold_ = {true, control_note(view_.focus), kUiAuditionOwnerId};
            return one_command(note_command(audition_hold_, true));
        }
        return activate(view_.focus);
    case UiKey::Enter:
        if (!is_playing_control(view_.focus)) return activate(view_.focus);
        return {};
    default: break;
    }
    if (!navigation_key(input.key) || !valid_control(view_.focus)) return {};
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
        focus_control(view_, focus);
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
        focus_control(view_, control);
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
        focus_control(view_, control);
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
