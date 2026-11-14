#include "TestSupport.h"
#include "UiModel.h"

#include <array>
#include <bit>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <limits>
#include <set>
#include <string_view>
#include <tuple>
#include <type_traits>

namespace {
using namespace hammond;
using namespace hammond::standalone;

constexpr std::array<UiWorkspace, 3> kWorkspaces{
    UiWorkspace::Play, UiWorkspace::Rotary, UiWorkspace::Service};
constexpr std::array<UiPresentation, 2> kPresentations{
    UiPresentation::Dimensional, UiPresentation::Flat};
constexpr std::array<bool, 12> kSharp{
    false, true, false, true, false, false, true, false, true, false, true, false};

struct Counts {
    unsigned layouts{}, keys{}, controls{}, presets{}, focus{}, gaps{}, old_locations{}, landmarks{};
} counts;

void near_rect(UiRect actual, UiRect expected) {
    // At 8192, 0.002 is just over two binary32 ULPs. No raster tolerance is used.
    CHECK_NEAR(actual.x, expected.x, 0.002F);
    CHECK_NEAR(actual.y, expected.y, 0.002F);
    CHECK_NEAR(actual.width, expected.width, 0.002F);
    CHECK_NEAR(actual.height, expected.height, 0.002F);
}

void contained(UiRect child, UiRect parent) {
    CHECK(std::isfinite(child.x) && std::isfinite(child.y));
    CHECK(std::isfinite(child.width) && std::isfinite(child.height));
    CHECK(child.width > 0 && child.height > 0);
    CHECK(child.x >= parent.x - 0.002F && child.y >= parent.y - 0.002F);
    CHECK(child.x + child.width <= parent.x + parent.width + 0.002F);
    CHECK(child.y + child.height <= parent.y + parent.height + 0.002F);
}

UiPoint exposed(const UiKeyGeometry& key) {
    const auto& p = key.hit.points;
    const float fraction = key.accidental ? 0.5F : 0.9F;
    const float left = p[0].x + fraction * (p[3].x - p[0].x);
    const float right = p[1].x + fraction * (p[2].x - p[1].x);
    return {(left + right) / 2, p[0].y + fraction * (p[3].y - p[0].y)};
}

UiPoint exposed(const UiControlGeometry& control) {
    const float fraction = control.id.kind == UiControlKind::PresetKey &&
        !kSharp[control.id.index] ? 0.9F : 0.5F;
    return {control.bounds.x + control.bounds.width / 2,
            control.bounds.y + control.bounds.height * fraction};
}

bool common(UiControlKind kind) {
    return kind == UiControlKind::Workspace || kind == UiControlKind::Presentation ||
        kind == UiControlKind::SaveControls || kind == UiControlKind::LoadControls ||
        kind == UiControlKind::Help || kind == UiControlKind::AudioSettings ||
        kind == UiControlKind::MidiSettings || kind == UiControlKind::Panic;
}

UiPoint focus_point(const UiLayout& layout, UiControlId id) {
    if (id.kind == UiControlKind::ManualKey)
        return exposed(layout.manual_keys[static_cast<std::size_t>(id.manual)][id.index]);
    if (id.kind == UiControlKind::PedalKey) return exposed(layout.pedal_keys[id.index]);
    for (const auto& control : layout.controls)
        if (control.id == id) return exposed(control);
    hammond_test::fail("focused identity has visible geometry", __FILE__, __LINE__);
}

void verify_layout(UiModel& model) {
    const auto& layout = model.layout();
    const UiRect window{0, 0, layout.width, layout.height};
    CHECK(layout.control_count == 68);
    std::array<unsigned, 2> presets{};
    for (const auto& control : layout.controls) {
        contained(control.bounds, window);
        contained(control.label_bounds, control.bounds);
        if (control.value_bounds.width > 0) contained(control.value_bounds, control.bounds);
        if (control.track.width > 0) contained(control.track, control.bounds);
        if (control.id.kind == UiControlKind::PresetKey) {
            CHECK(control.id.index < 12 && control.id.bank == DrawbarBank::A);
            ++presets[static_cast<std::size_t>(control.id.manual)];
            ++counts.presets;
        }
        const bool visible = layout.workspace == UiWorkspace::Play || common(control.id.kind);
        CHECK(ui_control_visible(layout, control.id) == visible);
        CHECK(ui_hit_test(layout, exposed(control)) == (visible ? control.id : UiControlId{}));
        ++counts.controls;
    }
    CHECK(presets[0] == 12 && presets[1] == 12);

    const auto keyboard = [&](const auto& keys, UiTarget target, UiRect panel) {
        unsigned naturals = 0, sharps = 0;
        for (std::size_t index = 0; index < keys.size(); ++index) {
            const auto& key = keys[index];
            CHECK(key.note.target == target);
            CHECK(key.note.value == index + (target == UiTarget::Pedals ? 1 : 36));
            CHECK(key.accidental == kSharp[index % 12]);
            key.accidental ? ++sharps : ++naturals;
            contained(key.bounds, panel);
            const UiControlId id{target == UiTarget::Pedals ? UiControlKind::PedalKey : UiControlKind::ManualKey,
                target == UiTarget::Lower ? Manual::Lower : Manual::Upper,
                DrawbarBank::A, static_cast<std::uint8_t>(index)};
            CHECK(ui_hit_test(layout, exposed(key)) ==
                  (layout.workspace == UiWorkspace::Play ? id : UiControlId{}));
            ++counts.keys;
        }
        CHECK(naturals == (target == UiTarget::Pedals ? 15U : 36U));
        CHECK(sharps == (target == UiTarget::Pedals ? 10U : 25U));
    };
    keyboard(layout.manual_keys[0], UiTarget::Upper, layout.manual_panels[0]);
    keyboard(layout.manual_keys[1], UiTarget::Lower, layout.manual_panels[1]);
    keyboard(layout.pedal_keys, UiTarget::Pedals, layout.pedal_panel);

    if (layout.sidebar_pedals) {
        CHECK_NEAR(layout.pedal_panel.y - layout.cabinet_panel.y - layout.cabinet_panel.height,
                   10.0F, 0.002F);
        CHECK(layout.cabinet_panel.y + layout.cabinet_panel.height < layout.pedal_panel.y);
        CHECK(layout.manual_panels[0].x + layout.manual_panels[0].width < layout.pedal_panel.x);
        CHECK(layout.manual_panels[1].x + layout.manual_panels[1].width < layout.pedal_panel.x);
        for (const float fraction : {0.01F, 0.5F, 0.99F}) {
            const UiPoint gap{layout.pedal_panel.x + fraction * layout.pedal_panel.width,
                              layout.pedal_panel.y - 5};
            CHECK(ui_hit_test(layout, gap).kind == UiControlKind::None);
            ++counts.gaps;
        }
    }

    // Traverse an entire cycle after reflow, including both hidden workspaces.
    // Cardinality and unique semantic IDs are independent of insertion order.
    const auto controls = model.view().controls;
    const unsigned expected = layout.workspace == UiWorkspace::Play ? 71U : 10U;
    std::set<std::tuple<UiControlKind, Manual, DrawbarBank, std::uint8_t>> focus;
    UiControlId first;
    for (unsigned index = 0; index < expected; ++index) {
        CHECK(model.key({UiKey::Tab, true}).count == 0);
        CHECK(model.key({UiKey::Tab, false}).count == 0);
        const auto id = model.view().focus;
        if (index == 0) first = id;
        CHECK(focus.emplace(id.kind, id.manual, id.bank, id.index).second);
        CHECK(ui_control_visible(layout, id));
        CHECK(ui_hit_test(layout, focus_point(layout, id)) == id);
        ++counts.focus;
    }
    CHECK(model.key({UiKey::Tab, true}).count == 0);
    CHECK(model.key({UiKey::Tab, false}).count == 0);
    CHECK(model.view().focus == first && model.view().controls == controls);
    ++counts.layouts;
}

void closest_breakpoints() {
    const float infinity = std::numeric_limits<float>::infinity();
    const float wm = std::nextafter(1400.0F, -infinity), wp = std::nextafter(1400.0F, infinity);
    const float hm = std::nextafter(820.0F, -infinity), hp = std::nextafter(820.0F, infinity);
    struct Case { float w, h; bool cabinet, cheeks, sidebar; };
    // Explicit truth table: these are the adjacent representable dimensions,
    // not integer-rounded pixels or another copy of the production predicate.
    const std::array<Case, 9> cases{{
        {wm, hm, false, false, false}, {wm, 820, false, true, false},
        {wm, hp, false, true, false}, {1400, hm, true, false, false},
        {1400, 820, true, true, true}, {1400, hp, true, true, true},
        {wp, hm, true, false, false}, {wp, 820, true, true, true},
        {wp, hp, true, true, true}}};
    for (const auto& entry : cases) {
        for (const auto presentation : kPresentations) {
            for (const auto workspace : kWorkspaces) {
                UiModel model;
                CHECK(model.resize(entry.w, entry.h));
                CHECK(model.set_presentation(presentation) && model.set_workspace(workspace));
                const auto& layout = model.layout();
                CHECK(layout.width == entry.w && layout.height == entry.h);
                CHECK(layout.show_cabinet == entry.cabinet);
                CHECK(layout.bank_controls_in_cheeks == entry.cheeks);
                CHECK(layout.sidebar_pedals == entry.sidebar);
                CHECK_NEAR(layout.manual_panels[0].y, entry.sidebar ? 477.2F : 445.2F, 0.001F);
                CHECK_NEAR(layout.manual_panels[0].height, entry.sidebar ? 135.4F : 115.6F, 0.001F);
                CHECK_NEAR(layout.pedal_panel.y, entry.sidebar ? 662.4F : 692.4F, 0.001F);
                verify_layout(model);
            }
        }
    }
}

void literal_landmarks() {
    struct Anchor {
        UiPoint size;
        UiRect manual, lower, pedal, cabinet, art, status;
    };
    // Frozen contract anchors. Art/status dimensions were independently solved
    // with decimal arithmetic and exact 466:397 aspect, including the height-
    // limited 1400x820 and width-limited reference/extreme fixtures. No expected
    // value is derived from a returned parent panel or production helper.
    constexpr std::array<Anchor, 4> anchors{{
        {{1400, 820}, {226.2F, 477.2F, 705.6444F, 135.4F}, {226.2F, 622.6F, 705.6444F, 135.4F},
         {941.8444F, 662.4F, 397.9556F, 95.6F}, {941.8444F, 126, 397.9556F, 526.4F},
         {972.146633249F, 174, 337.351133501F, 287.4F}, {955.8444F, 522.4F, 369.9556F, 116}},
        {{1672, 941}, {238.3362968F, 520.76F, 876.4950152F, 174.12F},
         {238.3362968F, 704.88F, 876.4950152F, 174.12F},
         {1124.831312F, 773.72F, 475.272688F, 105.28F}, {1124.831312F, 126, 475.272688F, 637.72F},
         {1132.831312F, 174, 459.272688F, 391.268792137F},
         {1138.831312F, 626.268792137F, 447.272688F, 123.451207863F}},
        {{1920, 1080}, {250, 536, 1035.664F, 236}, {250, 782, 1035.664F, 236},
         {1295.664F, 904, 552.336F, 114}, {1295.664F, 126, 552.336F, 768},
         {1303.664F, 174, 536.336F, 456.92144206F},
         {1309.664F, 691.92144206F, 524.336F, 188.07855794F}},
        {{8192, 8192}, {250, 536, 5357.072F, 3792}, {250, 4338, 5357.072F, 3792},
         {5617.072F, 8016, 2502.928F, 114}, {5617.072F, 126, 2502.928F, 7880},
         {5625.072F, 174, 2486.928F, 2118.691879828F},
         {5631.072F, 2353.691879828F, 2474.928F, 5638.308120172F}}}};
    for (const auto& anchor : anchors) {
        for (const auto presentation : kPresentations) {
            for (const auto workspace : kWorkspaces) {
                UiModel model;
                CHECK(model.resize(anchor.size.x, anchor.size.y));
                CHECK(model.set_presentation(presentation) && model.set_workspace(workspace));
                const auto& layout = model.layout();
                CHECK(layout.sidebar_pedals);
                near_rect(layout.manual_panels[0], anchor.manual);
                near_rect(layout.manual_panels[1], anchor.lower);
                near_rect(layout.pedal_panel, anchor.pedal);
                near_rect(layout.cabinet_panel, anchor.cabinet);
                near_rect(layout.cabinet_art, anchor.art);
                // The reserved area is a geometry budget, not a raster/text pass.
                near_rect({layout.cabinet_panel.x + 14, layout.cabinet_art.y + layout.cabinet_art.height + 61,
                           layout.cabinet_panel.width - 28, layout.cabinet_panel.y + layout.cabinet_panel.height -
                           layout.cabinet_art.y - layout.cabinet_art.height - 75}, anchor.status);
                if (anchor.size.x == 1672) {
                    for (unsigned manual = 0; manual < 2; ++manual) {
                        const auto& first = layout.manual_keys[manual].front().hit.points;
                        const auto& last = layout.manual_keys[manual].back().hit.points;
                        CHECK_NEAR(first[3].y - first[0].y, 144.12F, 0.0003F);
                        CHECK_NEAR(first[3].x, 246.3362968F, 0.0003F);
                        CHECK_NEAR(last[2].x, 1106.831312F, 0.0003F);
                    }
                }
                verify_layout(model);
                ++counts.landmarks;
            }
        }
    }
}

void relocated_pointer_targets() {
    for (const auto presentation : kPresentations) {
        UiLayout before, after;
        CHECK(make_ui_layout(1400, std::nextafter(820.0F, 0.0F), {DrawbarBank::B, DrawbarBank::B}, before,
                             UiWorkspace::Play, presentation));
        CHECK(make_ui_layout(1400, 820, {DrawbarBank::B, DrawbarBank::B}, after,
                             UiWorkspace::Play, presentation));
        // Fixed screen positions, independent of returned keys: the old pedal
        // row becomes Lower manual ink, and the old cabinet gains live pedals.
        CHECK(ui_hit_test(before, {650, 743}).kind == UiControlKind::PedalKey);
        const auto lower = ui_hit_test(after, {650, 743});
        CHECK(lower.kind == UiControlKind::ManualKey && lower.manual == Manual::Lower);
        CHECK(ui_hit_test(before, {1000, 740}).kind == UiControlKind::None);
        CHECK(ui_hit_test(after, {1000, 740}).kind == UiControlKind::PedalKey);
        counts.old_locations += 4;
    }
}

// Optional cross-revision evidence mode. Compile this same test against the
// unchanged d2972a5 UiModel.cpp and the current source, then compare these bytes.
// Serialize every legacy layout field explicitly; omit padding and the newly
// added sidebar flag (all selected inputs are outside that branch). This is
// deliberately not a platform-specific frozen-float hash in ordinary CTest.
template <class T> void word(T value) {
    std::uint32_t bits;
    if constexpr (std::is_floating_point_v<T>) bits = std::bit_cast<std::uint32_t>(value);
    else bits = static_cast<std::uint32_t>(value);
    for (unsigned shift = 0; shift < 32; shift += 8)
        std::cout.put(static_cast<char>((bits >> shift) & 255U));
}
void write(UiRect rect) { word(rect.x); word(rect.y); word(rect.width); word(rect.height); }
void write(UiControlId id) { word(id.kind); word(id.manual); word(id.bank); word(id.index); }
void write(const UiKeyGeometry& key) {
    word(key.note.target); word(key.note.value); word(key.accidental); write(key.bounds);
    for (const auto& quad : {key.hit, key.top, key.front})
        for (const auto& point : quad.points) { word(point.x); word(point.y); }
}
void legacy_snapshot() {
    const float wm = std::nextafter(1400.0F, 0.0F), wp = std::nextafter(1400.0F, 2000.0F);
    const float hm = std::nextafter(820.0F, 0.0F), hp = std::nextafter(820.0F, 1000.0F);
    const std::array<UiPoint, 13> sizes{{
        {960, 700}, {1280, 900}, {1400, 700}, {1920, 700}, {8192, 700}, {960, 8192},
        {1399.75F, 820.25F}, {1400.25F, 819.75F},
        {wm, hm}, {wm, 820}, {wm, hp}, {1400, hm}, {wp, hm}}};
    for (const auto size : sizes) for (const auto presentation : kPresentations)
        for (const auto workspace : kWorkspaces) {
            UiLayout layout;
            CHECK(make_ui_layout(size.x, size.y, {DrawbarBank::B, DrawbarBank::B}, layout, workspace, presentation));
            word(layout.width); word(layout.height); word(layout.show_cabinet); word(layout.bank_controls_in_cheeks);
            word(layout.workspace); word(layout.presentation); word(layout.control_count);
            for (const auto rect : {layout.header, layout.performance_panel, layout.keyboard_toolbar, layout.pedal_panel,
                                   layout.footer, layout.cabinet_panel, layout.cabinet_art, layout.workspace_panel}) write(rect);
            for (unsigned manual = 0; manual < 2; ++manual) {
                write(layout.registration_panels[manual]); write(layout.manual_panels[manual]);
                write(layout.manual_rail_panels[manual]); write(layout.preset_key_panels[manual]);
                for (const auto& key : layout.manual_keys[manual]) write(key);
            }
            for (const auto& key : layout.pedal_keys) write(key);
            for (const auto& control : layout.controls) {
                write(control.id); write(control.bounds); write(control.label_bounds);
                write(control.value_bounds); write(control.track);
            }
        }
}
} // namespace

int main(int argc, char** argv) {
    if (argc == 2 && std::string_view(argv[1]) == "--legacy-snapshot") {
        legacy_snapshot();
        return 0;
    }
    CHECK(argc == 1);
    closest_breakpoints();
    literal_landmarks();
    relocated_pointer_targets();
    std::cout << "Independent reference layout: " << counts.layouts << " layouts, " << counts.keys
              << " playing-key records, " << counts.controls << " control records including " << counts.presets
              << " presets, " << counts.focus << " unique focus stops, " << counts.gaps << " empty-gap hits, "
              << counts.old_locations << " old-location classifications, " << counts.landmarks
              << " literal landmark layouts; passed\n";
}
