#include "TestSupport.h"
#include "UiModel.h"

#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <limits>
#include <variant>

namespace {
using namespace hammond;
using namespace hammond::standalone;

// Independent acceptance expectations come from the frozen UI contract, not
// control-array order, generated registration data or ControlState mutations.
constexpr std::array<unsigned, 7> natural_pitches{0, 2, 4, 5, 7, 9, 11};
constexpr std::array<unsigned, 5> sharp_pitches{1, 3, 6, 8, 10};
constexpr std::array<unsigned, 5> sharp_boundaries{1, 2, 4, 5, 6};

struct Counts {
    std::size_t layouts{}, sampled_hits{}, transitions{}, keyboard_activations{};
    std::size_t focus_moves{}, invalid_ids{}, acknowledged_controls{};
} counts;

UiControlId preset(unsigned manual, unsigned index) {
    return {UiControlKind::PresetKey, static_cast<Manual>(manual), DrawbarBank::A,
            static_cast<std::uint8_t>(index)};
}

bool is_sharp(unsigned index) {
    for (const auto pitch : sharp_pitches) if (index == pitch) return true;
    return false;
}

const UiControlGeometry& geometry(const UiModel& model, UiControlId id) {
    for (std::size_t i = 0; i < model.layout().control_count; ++i) {
        if (model.layout().controls[i].id == id) return model.layout().controls[i];
    }
    hammond_test::fail("requested visible identity exists", __FILE__, __LINE__);
}

UiPoint exposed_point(const UiModel& model, unsigned manual, unsigned index) {
    const auto bounds = geometry(model, preset(manual, index)).bounds;
    return {bounds.x + bounds.width * 0.5F,
            bounds.y + bounds.height * (is_sharp(index) ? 0.3F : 0.85F)};
}

UiPoint exposed_playing_point(const UiKeyGeometry& key) {
    const float depth = key.accidental ? 0.3F : 0.85F;
    const auto& corners = key.hit.points;
    const float left = corners[0].x + depth * (corners[3].x - corners[0].x);
    const float right = corners[1].x + depth * (corners[2].x - corners[1].x);
    return {(left + right) * 0.5F, corners[0].y + depth * (corners[3].y - corners[0].y)};
}

const SessionCommand& command(const UiActions& actions) {
    CHECK(actions.count == 1);
    CHECK(std::holds_alternative<SessionCommand>(actions.items[0]));
    return std::get<SessionCommand>(actions.items[0]);
}

const ControlSnapshot& controls_command(const UiActions& actions) {
    CHECK(std::holds_alternative<ControlSnapshot>(command(actions)));
    return std::get<ControlSnapshot>(command(actions));
}

void tap_navigation(UiModel& model, UiKey key, bool shift = false) {
    CHECK(model.key({key, true, false, shift}).count == 0);
    CHECK(model.key({key, false}).count == 0);
}

void focus_via_tab(UiModel& model, UiControlId target) {
    for (unsigned i = 0; i < 71 && model.view().focus != target; ++i)
        tap_navigation(model, UiKey::Tab);
    CHECK(model.view().focus == target);
}

ControlSnapshot seed_controls() {
    ControlSnapshot snapshot;
    for (std::size_t manual = 0; manual < 2; ++manual)
        for (std::size_t bank = 0; bank < 2; ++bank)
            for (std::size_t drawbar = 0; drawbar < 9; ++drawbar)
                snapshot.drawbars[manual][bank][drawbar] =
                    static_cast<std::uint8_t>((drawbar + 2 * bank + 3 * manual) % 9);
    snapshot.selected_banks = {DrawbarBank::A, DrawbarBank::B};
    snapshot.fixed_registrations = {FixedRegistration::FSharp, FixedRegistration::DSharp};
    snapshot.route_enabled = {true, false};
    snapshot.expression = 0.375;
    snapshot.pedal_drawbars = {7, 3};
    snapshot.percussion.enabled = true;
    snapshot.percussion.harmonic = PercussionHarmonic::Second;
    snapshot.percussion.volume = PercussionVolume::Soft;
    snapshot.percussion.decay = PercussionDecay::Fast;
    return snapshot;
}

// This deliberately does not call select_preset(), normalized_to_event(), or
// the effective-selection helper whose consumers are under acceptance.
ControlSnapshot expected_selection(ControlSnapshot snapshot, unsigned manual,
                                   unsigned index) {
    if (index == 0) snapshot.route_enabled[manual] = false;
    else {
        snapshot.route_enabled[manual] = true;
        if (index < 10)
            snapshot.fixed_registrations[manual] = static_cast<FixedRegistration>(index);
        else {
            snapshot.fixed_registrations[manual] = FixedRegistration::None;
            snapshot.selected_banks[manual] = index == 10 ? DrawbarBank::A : DrawbarBank::B;
        }
    }
    return snapshot;
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
        const auto result = session.post(item);
        CHECK(result.ok());
        CHECK(model.submitted(item, result).count == 0);
    }

    SessionSnapshot flush(bool observe = true) {
        CHECK(session.render(0, {}).ok());
        const auto result = snapshot();
        if (observe) model.observe(result);
        return result;
    }

    void load(const ControlSnapshot& controls) {
        dispatch(model.load_controls(controls));
        flush();
        CHECK(!model.view().controls_dirty && !model.view().controls_pending);
    }

    void hold_notes() {
        // UI and external owners overlap on Upper C. Lower and pedal owners
        // prove that selector input cannot alter another physical division.
        dispatch(model.key({UiKey::A, true}));
        CHECK(session.post(PerformanceInputEvent{HostNoteEvent{
            0, HostNoteKind::On, 0, 5, 60, 127, 700}}).ok());
        CHECK(session.post(PerformanceInputEvent{HostNoteEvent{
            0, HostNoteKind::On, 1, 6, 55, 127, 701}}).ok());
        CHECK(session.post(PerformanceInputEvent{PedalNoteEvent{
            0, PedalNoteKind::On, 0, 7, PedalId{5}, 127, 702}}).ok());
        flush();
    }
};

void unchanged_holds(const SessionSnapshot& a, const SessionSnapshot& b) {
    CHECK(a.held_keys == b.held_keys);
    CHECK(a.held_pedals == b.held_pedals);
    CHECK(a.frame_clock == b.frame_clock);
    CHECK(a.held_keys[0][24] && a.held_keys[1][19] && a.held_pedals[4]);
}

void geometry_and_occlusion() {
    struct Anchor { float width, height, rail, manual, panel; bool cabinet, cheeks; };
    constexpr std::array<Anchor, 7> anchors{{
        {960, 700, 156, 82, 52, false, false},
        {1280, 900, 168, 138, 76, false, true},
        {1672, 941, 158.9619F, 138.48F, 76.48F, true, true},
        {1399, 819, 168, 115.32F, 85.32F, false, false},
        {1400, 819, 156, 115.32F, 85.32F, true, false},
        {1399, 820, 168, 115.6F, 53.6F, false, true},
        {1400, 820, 156, 104.6F, 42.6F, true, true}}};
    UiModel model;
    for (const auto& anchor : anchors) {
        CHECK(model.resize(anchor.width, anchor.height));
        const auto& layout = model.layout();
        CHECK(layout.control_count == 68);
        CHECK(layout.show_cabinet == anchor.cabinet);
        CHECK(layout.bank_controls_in_cheeks == anchor.cheeks);
        unsigned preset_count = 0;
        for (const auto& control : layout.controls) {
            CHECK(control.id.kind != UiControlKind::SoundingBank);
            CHECK(control.id.kind != UiControlKind::CancelManual);
            if (control.id.kind == UiControlKind::PresetKey) ++preset_count;
        }
        CHECK(preset_count == 24);
        for (unsigned manual = 0; manual < 2; ++manual) {
            const auto panel = layout.preset_key_panels[manual];
            CHECK_NEAR(layout.manual_rail_panels[manual].width, anchor.rail, 0.001F);
            CHECK_NEAR(layout.manual_panels[manual].height, anchor.manual, 0.001F);
            CHECK_NEAR(panel.height, anchor.panel, 0.001F);
            CHECK_NEAR(panel.width, anchor.rail - 16, 0.001F);
            for (unsigned pitch = 0; pitch < 12; ++pitch) {
                const auto& key = geometry(model, preset(manual, pitch));
                CHECK(key.bounds.width >= 11.99F);
                CHECK(key.label_bounds.x >= key.bounds.x);
                CHECK(key.label_bounds.x + key.label_bounds.width <= key.bounds.x + key.bounds.width);
                CHECK(key.label_bounds.height == 11);
                CHECK(ui_hit_test(layout, exposed_point(model, manual, pitch)) == preset(manual, pitch));
                std::uint32_t parameter = 0;
                CHECK(ui_parameter_id(key.id, parameter));
                CHECK(parameter == (manual == 0 ? 20480U : 20481U));
            }
            // A dense subpixel grid independently derives the visible topmost
            // pitch from seven natural divisions and five documented overlaps.
            // Offsets avoid ambiguity from separately rounded float borders.
            for (float y = 0.413F; y < panel.height; y += 0.5F) {
                for (float x = 0.371F; x < panel.width; x += 0.5F) {
                    const float unit = panel.width / 7.0F;
                    const auto ordinal = static_cast<unsigned>(x / unit);
                    CHECK(ordinal < natural_pitches.size());
                    unsigned wanted = natural_pitches[ordinal];
                    if (y < panel.height * 0.62F) {
                        for (std::size_t i = 0; i < sharp_pitches.size(); ++i) {
                            const float center = static_cast<float>(sharp_boundaries[i]) * unit;
                            if (x >= center - 0.3F * unit && x < center + 0.3F * unit)
                                wanted = sharp_pitches[i];
                        }
                    }
                    CHECK(ui_hit_test(layout, {panel.x + x, panel.y + y}) == preset(manual, wanted));
                    ++counts.sampled_hits;
                }
            }
            for (unsigned index = 0; index < 61; ++index) {
                const auto& key = layout.manual_keys[manual][index];
                CHECK(key.note.value == 36 + index);
                const UiPoint point = exposed_playing_point(key);
                const UiControlId wanted{UiControlKind::ManualKey, static_cast<Manual>(manual),
                    DrawbarBank::A, static_cast<std::uint8_t>(index)};
                CHECK(ui_hit_test(layout, point) == wanted);
            }
        }
        for (unsigned index = 0; index < 25; ++index) {
            const auto& key = layout.pedal_keys[index];
            CHECK(key.note.value == index + 1);
            const UiPoint point = exposed_playing_point(key);
            const UiControlId wanted{UiControlKind::PedalKey, Manual::Upper,
                DrawbarBank::A, static_cast<std::uint8_t>(index)};
            CHECK(ui_hit_test(layout, point) == wanted);
        }
        ++counts.layouts;
    }
    for (const auto size : std::array<UiPoint, 5>{{{960, 8192}, {8192, 700},
             {8192, 8192}, {1920, 1080}, {1024, 768}}}) {
        CHECK(model.resize(size.x, size.y));
        CHECK(model.layout().control_count == 68);
        for (unsigned manual = 0; manual < 2; ++manual)
            for (unsigned index = 0; index < 12; ++index)
                CHECK(ui_hit_test(model.layout(), exposed_point(model, manual, index)) == preset(manual, index));
        ++counts.layouts;
    }
}

void tab_order_and_navigation() {
    UiModel model;
    std::array<UiControlId, 71> expected{};
    std::size_t size = 0;
    expected[size++] = {UiControlKind::Workspace, Manual::Upper, DrawbarBank::A, 0};
    expected[size++] = {UiControlKind::Workspace, Manual::Upper, DrawbarBank::A, 1};
    expected[size++] = {UiControlKind::Workspace, Manual::Upper, DrawbarBank::A, 2};
    for (const auto kind : {UiControlKind::SaveControls, UiControlKind::LoadControls,
                           UiControlKind::Help, UiControlKind::AudioSettings,
                           UiControlKind::MidiSettings, UiControlKind::Panic})
        expected[size++] = {kind};
    expected[size++] = {UiControlKind::Presentation};
    for (unsigned manual = 0; manual < 2; ++manual) {
        expected[size++] = {UiControlKind::EditBank, static_cast<Manual>(manual), DrawbarBank::A};
        expected[size++] = {UiControlKind::EditBank, static_cast<Manual>(manual), DrawbarBank::B};
        for (unsigned index = 0; index < 12; ++index) expected[size++] = preset(manual, index);
        for (unsigned index = 0; index < 9; ++index)
            expected[size++] = {UiControlKind::ManualDrawbar, static_cast<Manual>(manual),
                                DrawbarBank::B, static_cast<std::uint8_t>(index)};
    }
    for (unsigned index = 0; index < 4; ++index)
        expected[size++] = {UiControlKind::Percussion, Manual::Upper, DrawbarBank::A,
                            static_cast<std::uint8_t>(index)};
    expected[size++] = {UiControlKind::Expression};
    for (unsigned index = 0; index < 2; ++index)
        expected[size++] = {UiControlKind::PedalDrawbar, Manual::Upper, DrawbarBank::A,
                            static_cast<std::uint8_t>(index)};
    for (unsigned index = 0; index < 3; ++index)
        expected[size++] = {UiControlKind::KeyboardTarget, Manual::Upper, DrawbarBank::A,
                            static_cast<std::uint8_t>(index)};
    expected[size++] = {UiControlKind::OctaveDown};
    expected[size++] = {UiControlKind::OctaveUp};
    expected[size++] = {UiControlKind::ManualKey, Manual::Upper, DrawbarBank::A, 24};
    expected[size++] = {UiControlKind::ManualKey, Manual::Lower, DrawbarBank::A, 24};
    expected[size++] = {UiControlKind::PedalKey};
    CHECK(size == expected.size());
    const auto baseline = model.view().controls;
    for (const auto id : expected) {
        tap_navigation(model, UiKey::Tab);
        CHECK(model.view().focus == id);
    }
    tap_navigation(model, UiKey::Tab);
    CHECK(model.view().focus == expected[0]);
    for (std::size_t i = expected.size(); i > 0; --i) {
        tap_navigation(model, UiKey::Tab, true);
        CHECK(model.view().focus == expected[i - 1]);
    }
    CHECK(model.view().controls == baseline);
    for (unsigned manual = 0; manual < 2; ++manual) {
        for (unsigned index = 0; index < 12; ++index) {
            for (const auto key : {UiKey::Left, UiKey::Right, UiKey::Home,
                                   UiKey::End, UiKey::Up, UiKey::Down}) {
                focus_via_tab(model, preset(manual, index));
                const auto roving_manual = model.view().roving_manual_keys;
                const auto roving_pedal = model.view().roving_pedal_key;
                unsigned wanted_manual = manual;
                unsigned wanted_index = index;
                if (key == UiKey::Left && index > 0) --wanted_index;
                if (key == UiKey::Right && index < 11) ++wanted_index;
                if (key == UiKey::Home) wanted_index = 0;
                if (key == UiKey::End) wanted_index = 11;
                if (key == UiKey::Up) wanted_manual = 0;
                if (key == UiKey::Down) wanted_manual = 1;
                tap_navigation(model, key);
                CHECK(model.view().focus == preset(wanted_manual, wanted_index));
                CHECK(model.view().controls == baseline);
                CHECK(model.view().roving_manual_keys == roving_manual);
                CHECK(model.view().roving_pedal_key == roving_pedal);
                ++counts.focus_moves;
            }
        }
    }
}

void all_transitions_preserve_owners(const RuntimeProfile& profile) {
    for (unsigned manual = 0; manual < 2; ++manual) {
        for (unsigned from = 0; from < 12; ++from) {
            for (unsigned to = 0; to < 12; ++to) {
                Rig rig(profile);
                const auto initial = expected_selection(seed_controls(), manual, from);
                rig.load(initial);
                rig.hold_notes();
                const auto before = rig.snapshot();
                const auto target = exposed_point(rig.model, manual, to);
                const auto wanted = expected_selection(initial, manual, to);
                const auto action = rig.model.pointer({UiPointerKind::Down, target});
                CHECK(controls_command(action) == wanted);
                CHECK(rig.model.view().controls == wanted);
                CHECK(rig.model.view().applied.controls == initial);
                CHECK(rig.model.view().controls_pending);
                CHECK(!rig.model.view().pointer_captured);
                CHECK(rig.model.view().edited_banks == (std::array{DrawbarBank::B, DrawbarBank::B}));
                CHECK(rig.model.view().keyboard_target == UiTarget::Upper);
                rig.dispatch(action);
                rig.model.observe(before);
                CHECK(rig.model.view().controls == wanted && rig.model.view().controls_pending);
                CHECK(rig.model.pointer({UiPointerKind::Down, target}).count == 0);
                const auto playing = rig.model.layout().manual_keys[1][60].bounds;
                CHECK(rig.model.pointer({UiPointerKind::Move, {playing.x + 1, playing.y + 30}}).count == 0);
                CHECK(rig.model.pointer({UiPointerKind::Up, target}).count == 0);
                CHECK(rig.model.pointer({UiPointerKind::CaptureLost, target}).count == 0);
                const auto after = rig.flush();
                CHECK(after.controls == wanted);
                CHECK(!rig.model.view().controls_pending);
                CHECK(rig.model.view().controls_dirty == !(wanted == initial));
                unchanged_holds(before, after);
                CHECK(after.last_applied_sequence == before.last_applied_sequence + 1);
                ++counts.acknowledged_controls;
                // Reflow through both placement thresholds cannot undo the
                // route, lose semantic focus, or release independent owners.
                CHECK(rig.model.resize(1400, 820));
                CHECK(rig.model.resize(1399, 819));
                CHECK(rig.model.resize(960, 700));
                CHECK(rig.model.view().focus == preset(manual, to));
                CHECK(rig.model.view().controls == wanted);
                unchanged_holds(before, rig.flush());
                rig.dispatch(rig.model.key({UiKey::A, false}));
                const auto released_ui = rig.flush();
                // The external Upper C owner survives the UI owner's release.
                unchanged_holds(before, released_ui);
                ++counts.transitions;
            }
        }
    }
}

void keyboard_commands_and_invalid_ids(const RuntimeProfile& profile) {
    Rig rig(profile);
    rig.load(seed_controls());
    rig.hold_notes();
    const auto held = rig.snapshot();
    for (unsigned manual = 0; manual < 2; ++manual) {
        for (unsigned index = 0; index < 12; ++index) {
            for (const auto key : {UiKey::Space, UiKey::Enter}) {
                focus_via_tab(rig.model, preset(manual, index));
                const auto wanted = expected_selection(rig.model.view().controls, manual, index);
                const auto action = rig.model.key({key, true});
                CHECK(controls_command(action) == wanted);
                rig.dispatch(action);
                CHECK(rig.model.key({key, true}).count == 0);
                CHECK(rig.model.key({key, true, true}).count == 0);
                CHECK(rig.model.key({key, false}).count == 0);
                unchanged_holds(held, rig.flush());
                CHECK(rig.model.view().controls == wanted);
                ++counts.keyboard_activations;
            }
        }
    }
    const auto before = rig.model.view();
    for (unsigned field = 0; field < 3; ++field) {
        for (unsigned byte = 0; byte < 256; ++byte) {
            if ((field == 0 && byte < 2) || (field == 1 && byte == 0) ||
                (field == 2 && byte < 12)) continue;
            auto id = preset(1, 9);
            if (field == 0) id.manual = static_cast<Manual>(byte);
            if (field == 1) id.bank = static_cast<DrawbarBank>(byte);
            if (field == 2) id.index = static_cast<std::uint8_t>(byte);
            std::uint32_t parameter = 0xDEADBEEFU;
            CHECK(!ui_parameter_id(id, parameter));
            CHECK(parameter == 0xDEADBEEFU);
            CHECK(rig.model.activate(id).count == 0);
            CHECK(rig.model.view().focus == before.focus);
            CHECK(rig.model.view().controls == before.controls);
            CHECK(rig.model.view().controls_pending == before.controls_pending);
            CHECK(rig.model.view().controls_dirty == before.controls_dirty);
            ++counts.invalid_ids;
        }
    }
    unchanged_holds(held, rig.flush());
    rig.dispatch(rig.model.key({UiKey::A, false}));
    unchanged_holds(held, rig.flush());
}

void delayed_acknowledgment_and_rejection(const RuntimeProfile& profile) {
    Rig rig(profile);
    rig.load(seed_controls());
    rig.hold_notes();
    const auto original = rig.snapshot();
    rig.dispatch(rig.model.activate(preset(0, 1)));
    const auto prefix = rig.flush(false);
    const auto cancel = rig.model.activate(preset(0, 0));
    const auto cancelled = expected_selection(prefix.controls, 0, 0);
    CHECK(controls_command(cancel) == cancelled);
    rig.dispatch(cancel);
    rig.model.observe(prefix);
    CHECK(rig.model.view().applied.controls == prefix.controls);
    CHECK(rig.model.view().controls == cancelled && rig.model.view().controls_pending);
    const auto cancel_ack = rig.flush(false);
    const auto next = rig.model.activate(preset(1, 10));
    const auto wanted = expected_selection(cancelled, 1, 10);
    rig.model.observe(cancel_ack); // A newer desired copy has not been posted yet.
    CHECK(rig.model.view().applied.controls == cancelled);
    CHECK(rig.model.view().controls == wanted && rig.model.view().controls_pending);
    rig.dispatch(next);
    const auto final = rig.flush();
    CHECK(final.controls == wanted && !rig.model.view().controls_pending);
    unchanged_holds(original, final);
    rig.model.observe(prefix); // Older publication cannot erase the latest route.
    CHECK(rig.model.view().applied.controls == wanted);
    CHECK(rig.model.view().controls == wanted);

    for (const auto status : {SessionStatus::InvalidCommand, SessionStatus::QueueFull,
                              SessionStatus::RecoveryPending, SessionStatus::SequenceExhausted}) {
        const auto pending = rig.model.activate(preset(0, 9));
        CHECK(rig.model.view().controls_pending);
        const auto recovery = rig.model.submitted(command(pending), {status, 0});
        CHECK(!rig.model.view().controls_pending);
        CHECK(rig.model.view().controls == wanted);
        CHECK(rig.model.view().input_recovery);
        CHECK(rig.model.view().last_submit_status == status);
        if (status == SessionStatus::InvalidCommand) {
            CHECK(std::holds_alternative<ReleaseUiNotes>(command(recovery)));
            const auto again = rig.model.submitted(command(pending), {status, 0});
            CHECK(again.count == 0);
        } else CHECK(recovery.count == 0);
    }
    // Submission feedback is inspected here without pretending an unposted
    // recovery command has changed the real Session's owners.
    unchanged_holds(original, rig.snapshot());
}
} // namespace

int main() {
    const auto profile = load_test_profile();
    geometry_and_occlusion();
    tab_order_and_navigation();
    all_transitions_preserve_owners(profile);
    keyboard_commands_and_invalid_ids(profile);
    delayed_acknowledgment_and_rejection(profile);
    std::cout << "Independent preset UI acceptance: " << counts.layouts << " layouts, "
              << counts.sampled_hits << " independently classified hit points, "
              << counts.transitions << " route transitions, "
              << counts.keyboard_activations << " keyboard activations, "
              << counts.focus_moves << " focus-only moves, " << counts.invalid_ids
              << " invalid identities, " << counts.acknowledged_controls
              << " exact single-command pointer acknowledgments; passed\n";
}
