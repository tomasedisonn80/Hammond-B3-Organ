#include "TestSupport.h"
#include "UiModel.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <limits>
#include <set>
#include <tuple>
#include <utility>
#include <variant>

// Independent SDK-free acceptance of WHOLE_REFERENCE_LAYOUT_CONTRACT v1.
// Expected rectangles use literal canonical coordinates; projected vertices
// use rational long-double algebra. No production mapping/projection helper,
// returned parent, or returned reference-size layout supplies an oracle.
namespace {
using namespace hammond;
using namespace hammond::standalone;

constexpr long double kTolerance = 0.002L;
constexpr std::array<bool, 12> kSharp{
    false, true, false, true, false, false, true, false, true, false, true, false};
constexpr std::array<UiWorkspace, 3> kWorkspaces{
    UiWorkspace::Play, UiWorkspace::Rotary, UiWorkspace::Service};
constexpr std::array<UiPresentation, 2> kPresentations{
    UiPresentation::Dimensional, UiPresentation::Flat};
constexpr std::array<std::array<DrawbarBank, 2>, 4> kBankPairs{{
    {DrawbarBank::A, DrawbarBank::A}, {DrawbarBank::A, DrawbarBank::B},
    {DrawbarBank::B, DrawbarBank::A}, {DrawbarBank::B, DrawbarBank::B}}};
constexpr std::array<UiPoint, 9> kActiveSizes{{
    {1672, 941}, {1400, 820}, {1920, 1080}, {1400.25F, 820.25F},
    {1672.5F, 941.25F}, {8192, 820}, {1400, 8192}, {8192, 8192},
    {6385.7314453125F, 5674.09375F}}};

struct Counts {
    unsigned active{}, inactive{}, controls{}, keys{}, preset_joins{}, key_joins{},
             pointer_controls{}, keyboard_controls{}, pointer_keys{}, keyboard_keys{};
} counts;

struct Box { long double x{}, y{}, width{}, height{}; };
struct Point { long double x{}, y{}; };
struct Control {
    UiControlId id;
    Box bounds, label, value{}, track{};
};
struct Scale {
    long double x, y;
    explicit Scale(UiPoint size)
        : x(static_cast<long double>(size.x / 1672.0F)),
          y(static_cast<long double>(size.y / 941.0F)) {}
    UiPoint point(Point p) const {
        return {static_cast<float>(p.x * x), static_cast<float>(p.y * y)};
    }
};

void near_rect(UiRect actual, Box expected, Scale scale) {
    CHECK_NEAR(actual.x, expected.x * scale.x, kTolerance);
    CHECK_NEAR(actual.y, expected.y * scale.y, kTolerance);
    CHECK_NEAR(actual.width, expected.width * scale.x, kTolerance);
    CHECK_NEAR(actual.height, expected.height * scale.y, kTolerance);
    CHECK_NEAR(static_cast<long double>(actual.x) + actual.width,
               (expected.x + expected.width) * scale.x, kTolerance);
    CHECK_NEAR(static_cast<long double>(actual.y) + actual.height,
               (expected.y + expected.height) * scale.y, kTolerance);
}

bool empty(UiRect value) {
    return value.x == 0 && value.y == 0 && value.width == 0 && value.height == 0;
}

void positive(UiRect rect) {
    CHECK(std::isfinite(rect.x) && std::isfinite(rect.y));
    CHECK(std::isfinite(rect.width) && std::isfinite(rect.height));
    CHECK(rect.width > 0 && rect.height > 0);
}

void contained(UiRect child, UiRect parent) {
    positive(child);
    positive(parent);
    CHECK(child.x >= parent.x && child.y >= parent.y);
    // This sole ULP allowance is for a recomposed owner's right/bottom.
    // Shared target boundaries below are always compared with exact equality.
    const float infinity = std::numeric_limits<float>::infinity();
    CHECK(child.x + child.width <= std::nextafter(parent.x + parent.width, infinity));
    CHECK(child.y + child.height <= std::nextafter(parent.y + parent.height, infinity));
}

bool overlap(UiRect a, UiRect b) {
    return a.x < b.x + b.width && b.x < a.x + a.width &&
        a.y < b.y + b.height && b.y < a.y + a.height;
}

bool same_point(UiPoint a, UiPoint b) { return a.x == b.x && a.y == b.y; }

const UiControlGeometry& geometry(const UiLayout& layout, UiControlId id) {
    for (std::size_t i = 0; i < layout.control_count; ++i)
        if (layout.controls[i].id == id) return layout.controls[i];
    hammond_test::fail("canonical identity has an actual control", __FILE__, __LINE__);
}

std::array<Control, 68> controls(const std::array<DrawbarBank, 2>& banks) {
    std::array<Control, 68> result{};
    std::size_t count = 0;
    const auto add = [&](UiControlId id, Box bounds, Box label, Box value = {}, Box track = {}) {
        CHECK(count < result.size());
        result[count++] = {id, bounds, label, value, track};
    };
    const auto button = [&](UiControlId id, Box bounds) {
        add(id, bounds, {bounds.x + 4, bounds.y + 4, bounds.width - 8, bounds.height - 8});
    };
    for (std::uint8_t i = 0; i < 3; ++i)
        button({UiControlKind::Workspace, Manual::Upper, DrawbarBank::A, i},
               {100.0L + 140.0L * i, 50, 130, 46});
    constexpr std::array<UiControlKind, 6> tools{
        UiControlKind::SaveControls, UiControlKind::LoadControls, UiControlKind::Help,
        UiControlKind::AudioSettings, UiControlKind::MidiSettings, UiControlKind::Panic};
    for (std::size_t i = 0; i < tools.size(); ++i)
        button({tools[i]}, {1312.0L + 97.0L * (i % 3), 25.0L + 36.0L * (i / 3), 88, 28});
    button({UiControlKind::Presentation}, {1228, 78, 70, 24});

    constexpr std::array<std::array<int, 9>, 2> centers{{
        {158, 206, 254, 302, 351, 400, 449, 498, 548},
        {685, 734, 782, 830, 878, 927, 975, 1024, 1074}}};
    constexpr std::array<Box, 2> presets{{{58, 607, 164, 81}, {42, 777, 172, 83}}};
    constexpr std::array<Box, 4> edits{{
        {58, 579, 80, 22}, {142, 579, 80, 22}, {42, 749, 84, 22}, {130, 749, 84, 22}}};
    for (std::size_t m = 0; m < 2; ++m) {
        const auto manual = static_cast<Manual>(m);
        button({UiControlKind::EditBank, manual, DrawbarBank::A}, edits[2 * m]);
        button({UiControlKind::EditBank, manual, DrawbarBank::B}, edits[2 * m + 1]);
        const auto panel = presets[m];
        unsigned natural = 0;
        for (std::uint8_t note = 0; note < 12; ++note) {
            const bool sharp = kSharp[note];
            // Exact sevenths and tenths, independent of binary32 partition code.
            const long double left = panel.x + panel.width *
                (static_cast<long double>(natural) - (sharp ? 3.0L / 10.0L : 0.0L)) / 7.0L;
            const long double width = panel.width * (sharp ? 3.0L / 5.0L : 1.0L) / 7.0L;
            const long double height = panel.height * (sharp ? 31.0L / 50.0L : 1.0L);
            const long double label_height = sharp ? 20.0L : 11.0L;
            add({UiControlKind::PresetKey, manual, DrawbarBank::A, note},
                {left, panel.y, width, height},
                {left + 1, panel.y + height - label_height - 2, width - 2, label_height});
            if (!sharp) ++natural;
        }
        for (std::uint8_t i = 0; i < 9; ++i) {
            const long double c = centers[m][i];
            add({UiControlKind::ManualDrawbar, manual, banks[m], i},
                {c - 23, 309, 46, 197}, {c - 23, 467, 46, 23},
                {c - 23, 491, 46, 15}, {c - 2, 327, 4, 118});
        }
    }
    constexpr std::array<std::uint8_t, 4> order{0, 2, 3, 1};
    constexpr std::array<long double, 4> left{164, 256, 337, 418};
    for (std::size_t i = 0; i < order.size(); ++i)
        add({UiControlKind::Percussion, Manual::Upper, DrawbarBank::A, order[i]},
            {left[i], 177, 74, 52}, {left[i] - 2, 233, 78, 14}, {left[i] + 5, 183, 64, 38});
    add({UiControlKind::Expression}, {578, 165, 254, 85}, {582, 165, 246, 16},
        {582, 232, 246, 16}, {594, 200, 222, 4});
    add({UiControlKind::PedalDrawbar, Manual::Upper, DrawbarBank::A, 0},
        {850, 165, 112, 85}, {854, 165, 104, 16}, {924, 200, 32, 40}, {891, 193, 4, 43});
    add({UiControlKind::PedalDrawbar, Manual::Upper, DrawbarBank::A, 1},
        {978, 165, 112, 85}, {982, 165, 104, 16}, {1052, 200, 32, 40}, {1019, 193, 4, 43});
    for (std::uint8_t i = 0; i < 3; ++i)
        button({UiControlKind::KeyboardTarget, Manual::Upper, DrawbarBank::A, i},
               {1148.0L + 148.0L * i, 616, 136, 26});
    button({UiControlKind::OctaveDown}, {1148, 648, 84, 26});
    button({UiControlKind::OctaveUp}, {1244, 648, 84, 26});
    CHECK(count == 68);
    return result;
}

Point exposed(const Control& c) {
    const bool natural = c.id.kind == UiControlKind::PresetKey && !kSharp[c.id.index];
    return {c.bounds.x + c.bounds.width / 2,
            c.bounds.y + c.bounds.height * (natural ? 9.0L / 10.0L : 1.0L / 2.0L)};
}

void parents(const UiLayout& layout, Scale scale) {
    const std::array<std::pair<UiRect, Box>, 15> expected{{
        {layout.header, {72, 10, 1528, 102}},
        {layout.performance_panel, {72, 125, 1044, 139}},
        {layout.registration_panels[0], {72, 269, 528, 239}},
        {layout.registration_panels[1], {600, 269, 516, 239}},
        {layout.manual_panels[0], {232, 528, 890, 170}},
        {layout.manual_panels[1], {224, 698, 898, 172}},
        {layout.manual_rail_panels[0], {48, 528, 184, 170}},
        {layout.manual_rail_panels[1], {32, 698, 192, 172}},
        {layout.preset_key_panels[0], {58, 607, 164, 81}},
        {layout.preset_key_panels[1], {42, 777, 172, 83}},
        {layout.cabinet_panel, {1126, 125, 478, 745}},
        {layout.keyboard_toolbar, {1140, 614, 448, 64}},
        {layout.pedal_panel, {1138, 752, 450, 110}},
        {layout.footer, {48, 889, 1556, 36}},
        {layout.workspace_panel, {72, 125, 1528, 745}}}};
    for (const auto& [actual, canonical] : expected) {
        near_rect(actual, canonical, scale);
        contained(actual, {0, 0, layout.width, layout.height});
    }
    CHECK(layout.show_cabinet && layout.bank_controls_in_cheeks && layout.sidebar_pedals);
    CHECK(layout.registration_panels[0].x + layout.registration_panels[0].width ==
          layout.registration_panels[1].x);
    CHECK(layout.manual_panels[0].y + layout.manual_panels[0].height == layout.manual_panels[1].y);
    contained(layout.keyboard_toolbar, layout.cabinet_panel);
    contained(layout.pedal_panel, layout.cabinet_panel);
    const long double f = std::min(scale.x, scale.y);
    const Box art{1132 * scale.x + 233 * (scale.x - f), 174 * scale.y, 466 * f, 397 * f};
    near_rect(layout.cabinet_art, art, Scale({1672, 941}));
    CHECK_NEAR(static_cast<long double>(layout.cabinet_art.width) * 397.0L /
               layout.cabinet_art.height, 466.0L, 0.0002L);
    contained(layout.cabinet_art, layout.cabinet_panel);
}

void control_geometry(const UiLayout& layout, const std::array<DrawbarBank, 2>& banks, Scale scale) {
    CHECK(layout.control_count == 68);
    const auto expected = controls(banks);
    std::set<std::tuple<UiControlKind, Manual, DrawbarBank, std::uint8_t>> ids;
    unsigned preset_count = 0, intersections = 0;
    for (std::size_t i = 0; i < expected.size(); ++i) {
        const auto& e = expected[i];
        const auto& c = layout.controls[i];
        CHECK(c.id == e.id);
        CHECK(ids.emplace(c.id.kind, c.id.manual, c.id.bank, c.id.index).second);
        near_rect(c.bounds, e.bounds, scale);
        near_rect(c.label_bounds, e.label, scale);
        positive(c.bounds);
        if (e.value.width == 0) CHECK(empty(c.value_bounds));
        else { near_rect(c.value_bounds, e.value, scale); contained(c.value_bounds, c.bounds); }
        if (e.track.width == 0) CHECK(empty(c.track));
        else { near_rect(c.track, e.track, scale); contained(c.track, c.bounds); }
        contained(c.label_bounds, c.id.kind == UiControlKind::Percussion ?
            layout.performance_panel : c.bounds);
        CHECK(ui_control_visible(layout, c.id));
        CHECK(ui_hit_test(layout, scale.point(exposed(e))) == e.id);

        UiRect owner = layout.header;
        switch (c.id.kind) {
        case UiControlKind::EditBank: owner = layout.manual_rail_panels[static_cast<std::size_t>(c.id.manual)]; break;
        case UiControlKind::PresetKey: owner = layout.preset_key_panels[static_cast<std::size_t>(c.id.manual)]; ++preset_count; break;
        case UiControlKind::ManualDrawbar: owner = layout.registration_panels[static_cast<std::size_t>(c.id.manual)]; break;
        case UiControlKind::Percussion:
        case UiControlKind::PedalDrawbar:
        case UiControlKind::Expression: owner = layout.performance_panel; break;
        case UiControlKind::KeyboardTarget:
        case UiControlKind::OctaveDown:
        case UiControlKind::OctaveUp: owner = layout.keyboard_toolbar; break;
        default: break;
        }
        contained(c.bounds, owner);
        if (c.id.kind == UiControlKind::ManualDrawbar) {
            const long double cap_half_height = 16 * scale.y;
            CHECK_NEAR(c.track.y - cap_half_height, 311 * scale.y, kTolerance);
            CHECK_NEAR(c.track.y + c.track.height + cap_half_height, 461 * scale.y, kTolerance);
            CHECK(c.track.y + c.track.height + cap_half_height < c.label_bounds.y);
            CHECK_NEAR(c.label_bounds.y, 467 * scale.y, kTolerance);
            CHECK_NEAR(c.value_bounds.y, 491 * scale.y, kTolerance);
            CHECK(34 * scale.x < c.bounds.width);
        } else if (c.id.kind == UiControlKind::PedalDrawbar) {
            CHECK_NEAR(c.track.y - 11 * scale.y, 182 * scale.y, kTolerance);
            CHECK_NEAR(c.track.y + c.track.height + 11 * scale.y, 247 * scale.y, kTolerance);
            CHECK(34 * scale.x < c.bounds.width);
        } else if (c.id.kind == UiControlKind::Percussion) {
            CHECK_NEAR(c.label_bounds.y - (c.bounds.y + c.bounds.height), 4 * scale.y, kTolerance);
            CHECK(ui_hit_test(layout, scale.point({e.label.x + e.label.width / 2,
                                                  e.label.y + e.label.height / 2})).kind == UiControlKind::None);
        }
        for (std::size_t j = i + 1; j < expected.size(); ++j) {
            if (!overlap(c.bounds, layout.controls[j].bounds)) continue;
            const auto other = layout.controls[j].id;
            CHECK(c.id.kind == UiControlKind::PresetKey && other.kind == UiControlKind::PresetKey);
            CHECK(c.id.manual == other.manual && kSharp[c.id.index] != kSharp[other.index]);
            ++intersections;
        }
        ++counts.controls;
    }
    CHECK(ids.size() == 68 && preset_count == 24 && intersections == 20);
    constexpr std::array<std::uint8_t, 7> naturals{0, 2, 4, 5, 7, 9, 11};
    for (const auto manual : {Manual::Upper, Manual::Lower}) {
        for (std::size_t n = 1; n < naturals.size(); ++n) {
            const auto a = geometry(layout, {UiControlKind::PresetKey, manual, DrawbarBank::A, naturals[n - 1]}).bounds;
            const auto b = geometry(layout, {UiControlKind::PresetKey, manual, DrawbarBank::A, naturals[n]}).bounds;
            CHECK(a.x + a.width == b.x);
            const UiPoint boundary{b.x, b.y + b.height * 0.9F};
            CHECK(!a.contains(boundary) && b.contains(boundary));
            CHECK(ui_hit_test(layout, boundary) == (UiControlId{UiControlKind::PresetKey, manual, DrawbarBank::A, naturals[n]}));
            ++counts.preset_joins;
        }
    }
}

struct Keyboard {
    long double x, y, width, height, a, b, naturals;
    Point at(long double u, long double v) const {
        const long double denominator = b - (b - a) * v;
        return {x + width / 2 + width * a * (u - 0.5L) / denominator,
                y + height * a * v / denominator};
    }
    Point at_y(long double u, long double screen_y) const {
        const long double fraction = (screen_y - y) / height;
        return {x + width / 2 + width * (u - 0.5L) * (a + (b - a) * fraction) / b, screen_y};
    }
};
constexpr std::array<Keyboard, 3> kKeyboards{{
    {240, 548, 874, 142, 24, 25, 36},
    {232, 718, 882, 144, 19, 20, 36},
    {1146, 772, 434, 82, 1, 1, 15}}};

UiControlId key_id(unsigned target, std::size_t index) {
    return {target == 2 ? UiControlKind::PedalKey : UiControlKind::ManualKey,
            target == 1 ? Manual::Lower : Manual::Upper, DrawbarBank::A,
            static_cast<std::uint8_t>(index)};
}

Point key_point(unsigned target, std::size_t index) {
    const auto& keyboard = kKeyboards[target];
    unsigned natural = 0;
    for (std::size_t i = 0; i < index; ++i) if (!kSharp[i % 12]) ++natural;
    return keyboard.at((natural + (kSharp[index % 12] ? 0.0L : 0.5L)) / keyboard.naturals,
                       kSharp[index % 12] ? 0.25L : 0.9L);
}

void quad(const UiQuad& actual, const std::array<Point, 4>& expected, Scale scale) {
    for (std::size_t i = 0; i < 4; ++i) {
        CHECK_NEAR(actual.points[i].x, expected[i].x * scale.x, kTolerance);
        CHECK_NEAR(actual.points[i].y, expected[i].y * scale.y, kTolerance);
    }
    const auto& p = actual.points;
    CHECK(p[0].y == p[1].y && p[2].y == p[3].y);
    CHECK(p[0].y < p[3].y && p[0].x < p[1].x && p[3].x < p[2].x);
}

template <std::size_t N>
void keyboard_geometry(const UiLayout& layout, const std::array<UiKeyGeometry, N>& keys,
                       unsigned target, Scale scale) {
    const auto& keyboard = kKeyboards[target];
    std::size_t natural = 0, previous = N;
    for (std::size_t i = 0; i < N; ++i) {
        const auto& key = keys[i];
        const bool sharp = kSharp[i % 12];
        const long double u0 = (natural - (sharp ? 0.3L : 0.0L)) / keyboard.naturals;
        const long double u1 = (natural + (sharp ? 0.3L : 1.0L)) / keyboard.naturals;
        const long double depth = sharp ? 31.0L / 50.0L : 1.0L;
        const std::array<Point, 4> hit{{keyboard.at(u0, 0), keyboard.at(u1, 0),
                                      keyboard.at(u1, depth), keyboard.at(u0, depth)}};
        const long double face = std::clamp((hit[3].y - hit[0].y) * 7.0L / 50.0L, 6.0L, 18.0L);
        const long double split = hit[3].y - face;
        const auto left = keyboard.at_y(u0, split), right = keyboard.at_y(u1, split);
        quad(key.hit, hit, scale);
        quad(key.top, {hit[0], hit[1], right, left}, scale);
        quad(key.front, {left, right, hit[2], hit[3]}, scale);
        CHECK(key.note.target == static_cast<UiTarget>(target));
        CHECK(key.note.value == i + (target == 2 ? 1 : 36));
        CHECK(key.accidental == sharp);
        const auto& p = key.hit.points;
        const float minimum_x = std::min({p[0].x, p[1].x, p[2].x, p[3].x});
        const float maximum_x = std::max({p[0].x, p[1].x, p[2].x, p[3].x});
        CHECK(key.bounds.x == minimum_x && key.bounds.y == p[0].y);
        CHECK(key.bounds.width == maximum_x - minimum_x && key.bounds.height == p[3].y - p[0].y);
        CHECK(same_point(key.top.points[0], p[0]) && same_point(key.top.points[1], p[1]));
        CHECK(same_point(key.top.points[3], key.front.points[0]));
        CHECK(same_point(key.top.points[2], key.front.points[1]));
        CHECK(same_point(key.front.points[2], p[2]) && same_point(key.front.points[3], p[3]));
        CHECK_NEAR(key.front.points[3].y - key.front.points[0].y, face * scale.y, kTolerance);
        const auto point = scale.point(key_point(target, i));
        CHECK(key.hit.contains(point) && ui_hit_test(layout, point) == key_id(target, i));
        const UiPoint split_point{(key.front.points[0].x + key.front.points[1].x) / 2,
                                  key.front.points[0].y};
        CHECK(key.front.contains(split_point) && !key.top.contains(split_point));
        for (const auto& c : layout.controls) CHECK(!overlap(key.bounds, c.bounds));
        if (!sharp) {
            if (previous != N) {
                const auto& a = keys[previous];
                CHECK(same_point(a.hit.points[1], p[0]) && same_point(a.hit.points[2], p[3]));
                CHECK(same_point(a.top.points[1], key.top.points[0]));
                CHECK(same_point(a.top.points[2], key.top.points[3]));
                CHECK(same_point(a.front.points[1], key.front.points[0]));
                CHECK(same_point(a.front.points[2], key.front.points[3]));
                ++counts.key_joins;
            }
            previous = i;
            ++natural;
        }
        ++counts.keys;
    }
    CHECK(natural == static_cast<std::size_t>(keyboard.naturals));
}

void active_geometry(const UiLayout& layout, const std::array<DrawbarBank, 2>& banks) {
    const Scale scale({layout.width, layout.height});
    parents(layout, scale);
    control_geometry(layout, banks, scale);
    keyboard_geometry(layout, layout.manual_keys[0], 0, scale);
    keyboard_geometry(layout, layout.manual_keys[1], 1, scale);
    keyboard_geometry(layout, layout.pedal_keys, 2, scale);
    // Headings, divider, wooden rim, cabinet art/truth/status, toolbar caption
    // and pedal heading are decorative even though they sit inside parents.
    for (const Point point : {Point{110, 146}, Point{556, 200}, Point{110, 517},
                              Point{1250, 400}, Point{1250, 592}, Point{1450, 709},
                              Point{1500, 739}, Point{1160, 760}, Point{1400, 662}})
        CHECK(ui_hit_test(layout, scale.point(point)).kind == UiControlKind::None);
    ++counts.active;
}

void layout_matrix() {
    const auto check = [](UiPoint size, bool dimensions_active) {
        for (const auto& banks : kBankPairs) for (const auto workspace : kWorkspaces)
            for (const auto presentation : kPresentations) {
                UiLayout layout;
                CHECK(make_ui_layout(size.x, size.y, banks, layout, workspace, presentation));
                CHECK(layout.width == size.x && layout.height == size.y);
                CHECK(layout.workspace == workspace && layout.presentation == presentation);
                const bool active = dimensions_active && workspace == UiWorkspace::Play &&
                    presentation == UiPresentation::Dimensional;
                CHECK(reference_composition_active(layout) == active);
                CHECK(layout.control_count == 68);
                if (active) active_geometry(layout, banks);
                else {
                    // Retained inactive literals: common header and y130/150
                    // percussion allocation, independent of the active API.
                    CHECK(layout.header.y == 16.0F);
                    for (const auto& c : layout.controls)
                        if (c.id.kind == UiControlKind::Percussion)
                            CHECK(c.bounds.y == (size.x >= 1400 && size.y >= 820 ? 150.0F : 130.0F));
                    ++counts.inactive;
                }
            }
    };
    for (const auto size : kActiveSizes) check(size, true);
    const std::array<float, 3> widths{std::nextafter(1400.0F, 0.0F), 1400.0F, std::nextafter(1400.0F, 2000.0F)};
    const std::array<float, 3> heights{std::nextafter(820.0F, 0.0F), 820.0F, std::nextafter(820.0F, 1000.0F)};
    for (std::size_t x = 0; x < 3; ++x) for (std::size_t y = 0; y < 3; ++y)
        check({widths[x], heights[y]}, x != 0 && y != 0);
    CHECK(counts.active == 52 && counts.inactive == 380);
    CHECK(counts.controls == counts.active * 68 && counts.keys == counts.active * 147);
    CHECK(counts.preset_joins == counts.active * 12 && counts.key_joins == counts.active * 84);
}

void recomposed_parent_counterexample() {
    UiLayout layout;
    CHECK(make_ui_layout(6385.7314453125F, 5674.09375F, {DrawbarBank::B, DrawbarBank::B}, layout));
    const auto upper = layout.preset_key_panels[0], lower = layout.preset_key_panels[1];
    const auto upper_last = geometry(layout, {UiControlKind::PresetKey, Manual::Upper, DrawbarBank::A, 11}).bounds;
    const auto lower_last = geometry(layout, {UiControlKind::PresetKey, Manual::Lower, DrawbarBank::A, 11}).bounds;
    CHECK(upper.x + upper.width == 847.8663330078125F);
    CHECK(upper_last.x + upper_last.width == 847.86627197265625F);
    CHECK(lower.x + lower.width == 817.3125F);
    CHECK(lower_last.x + lower_last.width == 817.31256103515625F);
    CHECK(lower_last.x + lower_last.width ==
          std::nextafter(lower.x + lower.width, std::numeric_limits<float>::infinity()));
    contained(upper_last, upper);
    contained(lower_last, lower);
    // Every adjacent join was checked exactly for this same size in the matrix.
}

UiActions tap(UiModel& model, UiKey key, bool shift = false) {
    const auto result = model.key({key, true, false, shift});
    CHECK(model.key({key, false}).count == 0);
    return result;
}

const SessionCommand& command(const UiActions& actions) {
    CHECK(actions.count == 1 && std::holds_alternative<SessionCommand>(actions.items[0]));
    return std::get<SessionCommand>(actions.items[0]);
}

void edit(const UiActions& actions, const ControlSnapshot& expected) {
    CHECK(std::holds_alternative<ControlSnapshot>(command(actions)));
    CHECK(std::get<ControlSnapshot>(command(actions)) == expected);
}

ControlSnapshot seeded() {
    ControlSnapshot state;
    for (auto& manual : state.drawbars) for (auto& bank : manual) bank.fill(4);
    state.selected_banks = {DrawbarBank::A, DrawbarBank::B};
    state.fixed_registrations = {FixedRegistration::D, FixedRegistration::G};
    state.expression = 0.375;
    state.pedal_drawbars = {4, 4};
    return state;
}

void prepare(UiModel& model, UiPoint size, const std::array<DrawbarBank, 2>& banks) {
    CHECK(model.resize(size.x, size.y));
    SessionSnapshot copied;
    copied.controls = seeded();
    copied.publication_revision = 1;
    copied.frame_clock = 1234;
    model.observe(copied);
    model.mark_saved(copied.controls);
    for (std::size_t m = 0; m < 2; ++m)
        CHECK(model.activate({UiControlKind::EditBank, static_cast<Manual>(m), banks[m]}).count == 0);
    CHECK(model.view().edited_banks == banks && model.view().controls == copied.controls);
    CHECK(!model.view().controls_pending && !model.view().controls_dirty);
}

void focus(UiModel& model, UiControlId id) {
    for (unsigned i = 0; i < 71 && model.view().focus != id; ++i)
        CHECK(tap(model, UiKey::Tab).count == 0);
    CHECK(model.view().focus == id);
}

void set_value(ControlSnapshot& state, UiControlId id, bool maximum) {
    if (id.kind == UiControlKind::ManualDrawbar)
        state.drawbars[static_cast<std::size_t>(id.manual)][static_cast<std::size_t>(id.bank)][id.index] = maximum ? 8 : 0;
    else if (id.kind == UiControlKind::PedalDrawbar) state.pedal_drawbars[id.index] = maximum ? 8 : 0;
    else { CHECK(id.kind == UiControlKind::Expression); state.expression = maximum ? 1.0 : 0.0; }
}

void button_result(UiModel& model, const UiActions& actions, UiControlId id, ControlSnapshot before) {
    bool musical = false;
    switch (id.kind) {
    case UiControlKind::PresetKey: {
        const auto m = static_cast<std::size_t>(id.manual);
        before.route_enabled[m] = id.index != 0;
        if (id.index > 0 && id.index < 10) before.fixed_registrations[m] = static_cast<FixedRegistration>(id.index);
        if (id.index >= 10) {
            before.fixed_registrations[m] = FixedRegistration::None;
            before.selected_banks[m] = id.index == 10 ? DrawbarBank::A : DrawbarBank::B;
        }
        musical = true;
        break;
    }
    case UiControlKind::Percussion:
        if (id.index == 0) before.percussion.enabled = !before.percussion.enabled;
        if (id.index == 1) before.percussion.harmonic = before.percussion.harmonic == PercussionHarmonic::Second ? PercussionHarmonic::Third : PercussionHarmonic::Second;
        if (id.index == 2) before.percussion.volume = before.percussion.volume == PercussionVolume::Normal ? PercussionVolume::Soft : PercussionVolume::Normal;
        if (id.index == 3) before.percussion.decay = before.percussion.decay == PercussionDecay::Slow ? PercussionDecay::Fast : PercussionDecay::Slow;
        musical = true;
        break;
    case UiControlKind::Workspace:
        CHECK(model.view().workspace == static_cast<UiWorkspace>(id.index));
        break;
    case UiControlKind::Presentation: CHECK(model.view().presentation == UiPresentation::Flat); break;
    case UiControlKind::EditBank: CHECK(model.view().edited_banks[static_cast<std::size_t>(id.manual)] == id.bank); break;
    case UiControlKind::KeyboardTarget: CHECK(model.view().keyboard_target == static_cast<UiTarget>(id.index)); break;
    case UiControlKind::OctaveDown: CHECK(model.view().manual_base_midi == 48); break;
    case UiControlKind::OctaveUp: CHECK(model.view().manual_base_midi == 72); break;
    case UiControlKind::Panic: CHECK(std::holds_alternative<Panic>(command(actions))); break;
    default: {
        UiAppRequest request{};
        switch (id.kind) {
        case UiControlKind::SaveControls: request = UiAppRequest::SaveControls; break;
        case UiControlKind::LoadControls: request = UiAppRequest::LoadControls; break;
        case UiControlKind::Help: request = UiAppRequest::Help; break;
        case UiControlKind::AudioSettings: request = UiAppRequest::AudioSettings; break;
        case UiControlKind::MidiSettings: request = UiAppRequest::MidiSettings; break;
        default: hammond_test::fail("known relocated button", __FILE__, __LINE__);
        }
        CHECK(actions.count == 1 && std::holds_alternative<UiAppRequest>(actions.items[0]));
        CHECK(std::get<UiAppRequest>(actions.items[0]) == request);
        CHECK(model.view().controls == before);
        return;
    }
    }
    if (musical) {
        edit(actions, before);
        CHECK(model.view().controls_pending);
        CHECK(model.view().applied.controls == seeded());
    } else if (id.kind != UiControlKind::Panic) CHECK(actions.count == 0);
    CHECK(model.view().controls == before);
}

void relocated_controls() {
    for (const UiPoint size : {UiPoint{1672, 941}, UiPoint{1400, 820}}) {
        const Scale scale(size);
        for (const auto& banks : kBankPairs) for (const auto& c : controls(banks)) {
            const bool parameter = c.id.kind == UiControlKind::ManualDrawbar ||
                c.id.kind == UiControlKind::PedalDrawbar || c.id.kind == UiControlKind::Expression;
            UiModel pointer;
            prepare(pointer, size, banks);
            auto expected = seeded();
            const Point start = !parameter ? exposed(c) : c.id.kind == UiControlKind::Expression ?
                Point{c.track.x, c.track.y + c.track.height / 2} : Point{c.track.x + c.track.width / 2, c.track.y};
            const auto pressed = pointer.pointer({UiPointerKind::Down, scale.point(start)});
            if (parameter) { set_value(expected, c.id, false); edit(pressed, expected); }
            else button_result(pointer, pressed, c.id, expected);
            CHECK(pointer.pointer({UiPointerKind::Down, scale.point(start)}).count == 0);
            if (parameter) {
                CHECK(pointer.view().pointer_captured && pointer.view().focus == c.id);
                const Point end = c.id.kind == UiControlKind::Expression ?
                    Point{c.track.x + c.track.width + 1, c.track.y} : Point{c.track.x, c.track.y + c.track.height + 1};
                set_value(expected, c.id, true);
                edit(pointer.pointer({UiPointerKind::Move, scale.point(end)}), expected);
                CHECK(pointer.view().controls == expected && pointer.view().applied.controls == seeded());
            }
            CHECK(pointer.pointer({UiPointerKind::Up, {-10, -10}}).count == 0);
            CHECK(!pointer.view().pointer_captured);
            ++counts.pointer_controls;

            UiModel keyboard;
            prepare(keyboard, size, banks);
            focus(keyboard, c.id);
            expected = seeded();
            if (parameter) {
                set_value(expected, c.id, false);
                edit(tap(keyboard, UiKey::Home), expected);
                set_value(expected, c.id, true);
                edit(tap(keyboard, UiKey::End), expected);
                CHECK(keyboard.view().focus == c.id && keyboard.view().controls == expected);
            } else {
                button_result(keyboard, keyboard.key({UiKey::Enter, true}), c.id, expected);
                CHECK(keyboard.key({UiKey::Enter, true}).count == 0);
                CHECK(keyboard.key({UiKey::Enter, true, true}).count == 0);
                CHECK(keyboard.key({UiKey::Enter, false}).count == 0);
            }
            ++counts.keyboard_controls;
        }
    }
    CHECK(counts.pointer_controls == 544 && counts.keyboard_controls == 544);
}

void note_event(const UiActions& actions, UiControlId id, bool down, std::int32_t owner) {
    CHECK(std::holds_alternative<PerformanceInputEvent>(command(actions)));
    const auto& input = std::get<PerformanceInputEvent>(command(actions));
    if (id.kind == UiControlKind::PedalKey) {
        CHECK(std::holds_alternative<PedalNoteEvent>(input));
        const auto& note = std::get<PedalNoteEvent>(input);
        CHECK(note.kind == (down ? PedalNoteKind::On : PedalNoteKind::Off));
        CHECK(note.pedal.value == id.index + 1 && note.bus == 0);
        CHECK(note.channel == 0 && note.note_id == owner && note.offset == 0);
        CHECK(note.velocity == (down ? 127 : 0));
    } else {
        CHECK(std::holds_alternative<HostNoteEvent>(input));
        const auto& note = std::get<HostNoteEvent>(input);
        CHECK(note.kind == (down ? HostNoteKind::On : HostNoteKind::Off));
        CHECK(note.midi_note == id.index + 36 && note.bus == static_cast<std::uint8_t>(id.manual));
        CHECK(note.channel == 0 && note.note_id == owner && note.offset == 0);
        CHECK(note.velocity == (down ? 127 : 0));
    }
}

void relocated_keys() {
    for (const UiPoint size : {UiPoint{1672, 941}, UiPoint{1400, 820}, UiPoint{1672.5F, 941.25F}}) {
        UiModel model;
        prepare(model, size, {DrawbarBank::B, DrawbarBank::A});
        const Scale scale(size);
        for (unsigned target = 0; target < 3; ++target) {
            for (std::size_t i = 0; i < (target == 2 ? 25U : 61U); ++i) {
                const auto id = key_id(target, i);
                const auto point = scale.point(key_point(target, i));
                note_event(model.pointer({UiPointerKind::Down, point}), id, true, kUiPointerOwnerId);
                CHECK(model.view().focus == id && model.view().pointer_captured);
                CHECK(model.pointer({UiPointerKind::Down, point}).count == 0);
                note_event(model.pointer({UiPointerKind::Up, {-100, -100}}), id, false, kUiPointerOwnerId);
                CHECK(!model.view().pointer_captured);
                note_event(model.key({UiKey::Space, true}), id, true, kUiAuditionOwnerId);
                CHECK(model.key({UiKey::Space, true}).count == 0);
                CHECK(model.key({UiKey::Space, true, true}).count == 0);
                note_event(model.key({UiKey::Space, false}), id, false, kUiAuditionOwnerId);
                CHECK(tap(model, UiKey::Enter).count == 0);
                CHECK(model.view().controls == seeded() && !model.view().controls_pending);
                ++counts.pointer_keys;
                ++counts.keyboard_keys;
            }
        }
    }
    CHECK(counts.pointer_keys == 441 && counts.keyboard_keys == 441);
}

template <class T> auto bytes(const T& object) {
    std::array<unsigned char, sizeof(T)> result{};
    std::memcpy(result.data(), &object, sizeof(T));
    return result;
}

void transactional_and_original_releases() {
    UiModel model;
    prepare(model, {1672, 941}, {DrawbarBank::A, DrawbarBank::B});
    const auto a = key_id(0, 24), w = key_id(0, 25), mouse = key_id(1, 29), audition = key_id(2, 12);
    note_event(model.key({UiKey::A, true}), a, true, kUiKeyboardOwnerBase);
    note_event(model.key({UiKey::W, true}), w, true, kUiKeyboardOwnerBase + 1);
    note_event(model.pointer({UiPointerKind::Down, Scale({1672, 941}).point(key_point(1, 29))}), mouse, true, kUiPointerOwnerId);
    CHECK(model.activate(audition).count == 0);
    note_event(model.key({UiKey::Space, true}), audition, true, kUiAuditionOwnerId);
    const auto original = bytes(model);
    const float infinity = std::numeric_limits<float>::infinity();
    const std::array<float, 8> invalid{0, -1, std::nextafter(960.0F, 0.0F),
        std::nextafter(8192.0F, infinity), std::numeric_limits<float>::max(),
        std::numeric_limits<float>::quiet_NaN(), infinity, -infinity};
    for (const float bad : invalid) {
        CHECK(!model.resize(bad, 941) && bytes(model) == original);
        const float bad_height = bad == std::nextafter(960.0F, 0.0F) ? std::nextafter(700.0F, 0.0F) : bad;
        CHECK(!model.resize(1672, bad_height) && bytes(model) == original);
    }
    for (const unsigned value : {2U, 3U, 127U, 255U}) {
        if (value >= 3) CHECK(!model.set_workspace(static_cast<UiWorkspace>(value)) && bytes(model) == original);
        CHECK(!model.set_presentation(static_cast<UiPresentation>(value)) && bytes(model) == original);
    }
    UiLayout destination = model.layout();
    const auto layout_before = bytes(destination);
    for (const auto& banks : {std::array<DrawbarBank, 2>{static_cast<DrawbarBank>(2), DrawbarBank::A},
                              std::array<DrawbarBank, 2>{DrawbarBank::B, static_cast<DrawbarBank>(255)}}) {
        CHECK(!make_ui_layout(1672, 941, banks, destination));
        CHECK(bytes(destination) == layout_before);
    }
    CHECK(tap(model, UiKey::F2).count == 0 && tap(model, UiKey::RightBracket).count == 0);
    for (const auto size : kActiveSizes) {
        CHECK(model.resize(size.x, size.y));
        CHECK(model.view().focus == audition);
        CHECK(model.view().controls == seeded() && !model.view().controls_pending);
        CHECK(model.view().applied.frame_clock == 1234 && model.view().applied.controls == seeded());
        CHECK(model.pointer({UiPointerKind::Move, Scale(size).point(key_point(0, 0))}).count == 0);
        CHECK(model.key({UiKey::A, true}).count == 0 && model.key({UiKey::Space, true}).count == 0);
    }
    for (const auto size : {UiPoint{std::nextafter(1400.0F, 0.0F), 820},
                            UiPoint{1400, std::nextafter(820.0F, 0.0F)}, UiPoint{1400, 820}}) {
        CHECK(model.resize(size.x, size.y) && model.view().focus == audition);
    }
    CHECK(model.set_presentation(UiPresentation::Flat));
    CHECK(model.set_workspace(UiWorkspace::Rotary) && model.set_workspace(UiWorkspace::Service));
    CHECK(model.set_workspace(UiWorkspace::Play) && model.view().focus == audition);
    CHECK(model.set_presentation(UiPresentation::Dimensional));
    CHECK(model.view().controls == seeded() && !model.view().controls_pending);
    CHECK(model.set_workspace(UiWorkspace::Service));
    note_event(model.pointer({UiPointerKind::Up, {-500, -500}}), mouse, false, kUiPointerOwnerId);
    note_event(model.key({UiKey::Space, false}), audition, false, kUiAuditionOwnerId);
    note_event(model.key({UiKey::A, false}), a, false, kUiKeyboardOwnerBase);
    note_event(model.key({UiKey::W, false}), w, false, kUiKeyboardOwnerBase + 1);
    CHECK(model.pointer({UiPointerKind::Up, {}}).count == 0);
    CHECK(model.key({UiKey::A, false}).count == 0 && model.key({UiKey::Space, false}).count == 0);
}

void focus_cycles_and_drag_reflow() {
    for (const auto& banks : kBankPairs) for (const auto workspace : kWorkspaces)
        for (const auto presentation : kPresentations) {
            UiModel model;
            prepare(model, {1672, 941}, banks);
            CHECK(model.set_workspace(workspace) && model.set_presentation(presentation));
            std::set<std::tuple<UiControlKind, Manual, DrawbarBank, std::uint8_t>> seen;
            UiControlId first;
            const unsigned stops = workspace == UiWorkspace::Play ? 71 : 10;
            for (unsigned i = 0; i < stops; ++i) {
                CHECK(tap(model, UiKey::Tab).count == 0);
                const auto id = model.view().focus;
                if (i == 0) first = id;
                CHECK(seen.emplace(id.kind, id.manual, id.bank, id.index).second);
                CHECK(ui_control_visible(model.layout(), id));
            }
            CHECK(tap(model, UiKey::Tab).count == 0 && model.view().focus == first);
            for (unsigned i = 0; i < stops; ++i) CHECK(tap(model, UiKey::Tab, true).count == 0);
            CHECK(model.view().focus == first && model.view().controls == seeded());
        }

    const auto expected_controls = controls({DrawbarBank::B, DrawbarBank::B});
    for (const auto& c : expected_controls) {
        if (c.id.kind != UiControlKind::ManualDrawbar && c.id.kind != UiControlKind::PedalDrawbar &&
            c.id.kind != UiControlKind::Expression) continue;
        UiModel model;
        prepare(model, {1672, 941}, {DrawbarBank::B, DrawbarBank::B});
        const auto point = Scale({1672, 941}).point(c.id.kind == UiControlKind::Expression ?
            Point{c.track.x, c.track.y} : Point{c.track.x + c.track.width / 2, c.track.y});
        auto expected = seeded();
        set_value(expected, c.id, false);
        edit(model.pointer({UiPointerKind::Down, point}), expected);
        const auto before = bytes(model);
        CHECK(!model.resize(8193, 941) && bytes(model) == before);
        const auto last = Scale({1672, 941}).point(c.id.kind == UiControlKind::Expression ?
            Point{c.track.x + c.track.width + 1, c.track.y} : Point{c.track.x, c.track.y + c.track.height + 1});
        set_value(expected, c.id, true);
        edit(model.pointer({UiPointerKind::Move, last}), expected); // Invalid resize kept the drag.
        CHECK(model.resize(1400, 820) && model.view().focus == c.id);
        CHECK(model.pointer({UiPointerKind::Move, point}).count == 0); // Valid reflow closed it.
        CHECK(model.view().controls == expected && model.view().applied.controls == seeded());
        CHECK(model.pointer({UiPointerKind::Up, {}}).count == 0 && !model.view().pointer_captured);
    }
}
} // namespace

int main() {
    CHECK(parameter_descriptors().size() == 47);
    layout_matrix();
    recomposed_parent_counterexample();
    relocated_controls();
    relocated_keys();
    transactional_and_original_releases();
    focus_cycles_and_drag_reflow();
    std::cout << "whole reference: " << counts.active << " canonical layouts, " << counts.inactive
              << " inactive predicate cases, " << counts.controls << " controls, " << counts.keys
              << " key quads, " << counts.preset_joins << " exact preset joins, " << counts.key_joins
              << " exact natural joins; " << counts.pointer_controls << " pointer and "
              << counts.keyboard_controls << " keyboard control journeys, " << counts.pointer_keys
              << " pointer and " << counts.keyboard_keys << " keyboard note journeys; passed\n";
}
