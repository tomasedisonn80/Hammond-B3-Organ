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
#include <type_traits>

namespace {
using namespace hammond;
using namespace hammond::standalone;

static_assert(kManualCount == 2 && kManualKeyCount == 61 && kPedalCount == 25);
static_assert(kPresetSelectionCount == 12);
static_assert(2 * kManualKeyCount + kPedalCount == 147);
static_assert(std::is_trivially_copyable_v<UiLayout>);

// Literal pitch classes are deliberately independent of UiModel's helper.
constexpr std::array<bool, 12> kAccidentals{
    false, true, false, true, false, false, true, false, true, false, true, false};
constexpr std::array<UiWorkspace, 3> kWorkspaces{
    UiWorkspace::Play, UiWorkspace::Rotary, UiWorkspace::Service};
constexpr std::array<UiPresentation, 2> kPresentations{
    UiPresentation::Dimensional, UiPresentation::Flat};
constexpr std::array<UiPoint, 12> kSizes{{
    {960.0F, 700.0F}, {1280.0F, 900.0F}, {1672.0F, 941.0F},
    {1399.0F, 819.0F}, {1399.0F, 820.0F},
    {1400.0F, 819.0F}, {1400.0F, 820.0F},
    {1280.0F, 819.0F}, {1280.0F, 820.0F},
    {8192.0F, 8192.0F}, {8192.0F, 700.0F}, {960.0F, 8192.0F}}};

struct ExactPoint {
    long double x{0.0L}, y{0.0L};
};

struct KeyboardOracle {
    long double x, y, width, height;
    bool perspective;

    // Algebraically reduced rational coefficients, evaluated in long double:
    // b = 47/50, d = (50 - 3v)/50. No production projection helper is used.
    [[nodiscard]] ExactPoint at(long double u, long double v) const {
        if (!perspective) return {x + width * u, y + height * v};
        const long double divisor = 50.0L - 3.0L * v;
        return {x + width * (0.5L + 47.0L * (u - 0.5L) / divisor),
                y + height * 47.0L * v / divisor};
    }

    // Independent screen-y form after eliminating v from the homography.
    [[nodiscard]] ExactPoint at_screen_y(long double u, long double screen_y) const {
        const long double s = (screen_y - y) / height;
        const long double scale = perspective ? (47.0L + 3.0L * s) / 50.0L : 1.0L;
        return {x + width * (0.5L + (u - 0.5L) * scale), screen_y};
    }
};

[[nodiscard]] KeyboardOracle oracle(UiRect panel, bool perspective) {
    return {static_cast<long double>(panel.x) + 8.0L,
            static_cast<long double>(panel.y) + 22.0L,
            static_cast<long double>(panel.width) - 16.0L,
            static_cast<long double>(panel.height) - 30.0L, perspective};
}

[[nodiscard]] UiPoint screen(ExactPoint point) {
    return {static_cast<float>(point.x), static_cast<float>(point.y)};
}

[[nodiscard]] bool same_point(UiPoint a, UiPoint b) {
    return a.x == b.x && a.y == b.y;
}

void same_quad(const UiQuad& actual, const UiQuad& expected) {
    for (std::size_t index = 0; index < 4; ++index) {
        CHECK(same_point(actual.points[index], expected.points[index]));
    }
}

void near_point(UiPoint actual, ExactPoint expected, long double tolerance) {
    CHECK_NEAR(actual.x, expected.x, tolerance);
    CHECK_NEAR(actual.y, expected.y, tolerance);
}

[[nodiscard]] UiControlId key_id(UiTarget target, std::size_t index) {
    return {target == UiTarget::Pedals ? UiControlKind::PedalKey : UiControlKind::ManualKey,
            target == UiTarget::Lower ? Manual::Lower : Manual::Upper,
            DrawbarBank::A, static_cast<std::uint8_t>(index)};
}

void check_hit(const UiLayout& layout, UiPoint point, UiControlId expected) {
    CHECK(ui_hit_test(layout, point) ==
          (layout.workspace == UiWorkspace::Play ? expected : UiControlId{}));
}

void check_valid_quad(const UiQuad& quad, UiRect panel, const UiLayout& layout) {
    const auto& p = quad.points;
    CHECK(p[0].y == p[1].y && p[2].y == p[3].y);
    CHECK(p[0].y < p[3].y && p[0].x < p[1].x && p[3].x < p[2].x);
    for (const auto& point : p) {
        CHECK(std::isfinite(point.x) && std::isfinite(point.y));
        CHECK(point.x >= panel.x && point.x <= panel.x + panel.width);
        CHECK(point.y >= panel.y && point.y <= panel.y + panel.height);
        CHECK(point.x >= 0.0F && point.x <= layout.width);
        CHECK(point.y >= 0.0F && point.y <= layout.height);
    }
}

void independent_oracle_landmarks() {
    const KeyboardOracle manual{0.0L, 0.0L, 100.0L, 100.0L, true};
    CHECK_NEAR(manual.at(0.0L, 0.0L).x, 3.0L, 1.0e-12L);
    CHECK_NEAR(manual.at(1.0L, 0.0L).x, 97.0L, 1.0e-12L);
    CHECK_NEAR(manual.at(0.0L, 1.0L).x, 0.0L, 1.0e-12L);
    CHECK_NEAR(manual.at(1.0L, 1.0L).x, 100.0L, 1.0e-12L);
    CHECK_NEAR(manual.at(0.5L, 0.5L).x, 50.0L, 1.0e-12L);
    CHECK_NEAR(manual.at(0.5L, 0.5L).y, 4700.0L / 97.0L, 1.0e-12L);
    CHECK_NEAR(manual.at(1.0L, 0.5L).x - manual.at(0.0L, 0.5L).x,
               9400.0L / 97.0L, 1.0e-12L);
    CHECK_NEAR(manual.at(0.5L, 0.62L).y, 145700.0L / 2407.0L, 1.0e-12L);
    const KeyboardOracle flat{0.0L, 0.0L, 100.0L, 100.0L, false};
    CHECK_NEAR(flat.at(0.3L, 0.62L).x, 30.0L, 1.0e-12L);
    CHECK_NEAR(flat.at(0.3L, 0.62L).y, 62.0L, 1.0e-12L);
}

template <std::size_t Count>
void check_keyboard(const UiLayout& layout, const std::array<UiKeyGeometry, Count>& keys,
                    UiRect panel, UiTarget target, std::size_t natural_count) {
    const bool dimensional = layout.presentation == UiPresentation::Dimensional;
    const auto expected = oracle(panel, dimensional && target != UiTarget::Pedals);
    // Endpoint storage and panel insets round to binary32. Four epsilon-scaled
    // units cover those roundings; face splitting uses additional float ops,
    // so receives eight. Edge identity/ownership checks below use no tolerance.
    const long double scale = std::max(layout.width, layout.height);
    const long double coordinate_tolerance = 4.0L * std::numeric_limits<float>::epsilon() * scale;
    const long double face_tolerance = 2.0L * coordinate_tolerance;
    std::size_t natural = 0;
    std::size_t accidentals = 0;
    std::size_t previous_natural = Count;
    for (std::size_t index = 0; index < Count; ++index) {
        const auto& key = keys[index];
        const bool sharp = kAccidentals[index % 12];
        const auto id = key_id(target, index);
        CHECK(key.note.target == target);
        CHECK(key.note.value == (target == UiTarget::Pedals ? index + 1 : index + 36));
        CHECK(key.accidental == sharp);
        CHECK(ui_control_visible(layout, id) == (layout.workspace == UiWorkspace::Play));
        const long double n = static_cast<long double>(natural);
        const long double count = static_cast<long double>(natural_count);
        const long double u0 = sharp ? (10.0L * n - 3.0L) / (10.0L * count) : n / count;
        const long double u1 = sharp ? (10.0L * n + 3.0L) / (10.0L * count) : (n + 1.0L) / count;
        const long double depth = sharp ? 31.0L / 50.0L : 1.0L;
        const std::array<ExactPoint, 4> corners{{
            expected.at(u0, 0.0L), expected.at(u1, 0.0L),
            expected.at(u1, depth), expected.at(u0, depth)}};
        for (std::size_t corner = 0; corner < 4; ++corner) {
            near_point(key.hit.points[corner], corners[corner], coordinate_tolerance);
        }
        check_valid_quad(key.hit, panel, layout);
        check_valid_quad(key.top, panel, layout);

        // Bounds must be exactly the envelope of the emitted vertices; they
        // are not a substitute hit region.
        const auto& p = key.hit.points;
        const float minimum_x = std::min({p[0].x, p[1].x, p[2].x, p[3].x});
        const float maximum_x = std::max({p[0].x, p[1].x, p[2].x, p[3].x});
        CHECK(key.bounds.x == minimum_x && key.bounds.y == p[0].y);
        CHECK(key.bounds.width == maximum_x - minimum_x);
        CHECK(key.bounds.height == p[3].y - p[0].y);

        if (dimensional) {
            check_valid_quad(key.front, panel, layout);
            const long double height = corners[3].y - corners[0].y;
            const long double face_depth = std::clamp(7.0L * height / 50.0L, 6.0L, 18.0L);
            const long double split_y = corners[3].y - face_depth;
            near_point(key.top.points[2], expected.at_screen_y(u1, split_y), face_tolerance);
            near_point(key.top.points[3], expected.at_screen_y(u0, split_y), face_tolerance);
            CHECK(same_point(key.top.points[0], p[0]));
            CHECK(same_point(key.top.points[1], p[1]));
            CHECK(same_point(key.top.points[2], key.front.points[1]));
            CHECK(same_point(key.top.points[3], key.front.points[0]));
            CHECK(same_point(key.front.points[2], p[2]));
            CHECK(same_point(key.front.points[3], p[3]));
            CHECK_NEAR(key.front.points[3].y - key.front.points[0].y, face_depth, face_tolerance);

            const auto front_point = screen(expected.at_screen_y((u0 + u1) / 2.0L,
                                                                 corners[3].y - face_depth / 2.0L));
            CHECK(key.hit.contains(front_point));
            CHECK(key.front.contains(front_point));
            CHECK(!key.top.contains(front_point));
            check_hit(layout, front_point, id);
            const auto top_point = screen(expected.at_screen_y((u0 + u1) / 2.0L,
                                                               (corners[0].y + split_y) / 2.0L));
            CHECK(key.top.contains(top_point) && key.hit.contains(top_point));
            CHECK(!key.front.contains(top_point));

            // The horizontal split belongs exactly to the front, including
            // under half-open ownership, using a safe interior x coordinate.
            const UiPoint split{static_cast<float>((static_cast<double>(key.front.points[0].x) +
                                                   key.front.points[1].x) / 2.0),
                                key.front.points[0].y};
            CHECK(!key.top.contains(split) && key.front.contains(split) && key.hit.contains(split));
        } else {
            same_quad(key.top, key.hit);
            same_quad(key.front, UiQuad{});
            CHECK(!key.front.contains({0.0F, 0.0F}));
            CHECK(p[0].x == p[3].x && p[1].x == p[2].x);
        }

        if (sharp) {
            ++accidentals;
            // Each half of every accidental overlaps a natural. Test both,
            // well away from their common boundary and all float ambiguity.
            for (const long double offset : {-0.15L, 0.15L}) {
                const auto point = screen(expected.at((n + offset) / count, 0.25L));
                CHECK(key.hit.contains(point));
                std::size_t natural_owners = 0;
                for (const auto& under : keys) {
                    if (!under.accidental && under.hit.contains(point)) ++natural_owners;
                }
                CHECK(natural_owners == 1);
                check_hit(layout, point, id);
            }
        } else {
            const auto exposed = screen(expected.at((n + 0.5L) / count, 0.85L));
            CHECK(key.hit.contains(exposed));
            check_hit(layout, exposed, id);
            if (previous_natural != Count) {
                const auto& previous = keys[previous_natural];
                CHECK(same_point(previous.hit.points[1], p[0]));
                CHECK(same_point(previous.hit.points[2], p[3]));
                CHECK(same_point(previous.top.points[1], key.top.points[0]));
                CHECK(same_point(previous.top.points[2], key.top.points[3]));
                if (dimensional) {
                    CHECK(same_point(previous.front.points[1], key.front.points[0]));
                    CHECK(same_point(previous.front.points[2], key.front.points[3]));
                }
                CHECK(!previous.hit.contains(p[0]) && key.hit.contains(p[0]));
                const auto boundary = expected.at(n / count, 0.85L);
                // At maximum size this 1/32-pixel offset exceeds the numeric
                // tolerance by 8x while remaining far inside adjacent keys.
                check_hit(layout, screen({boundary.x - 1.0L / 32.0L, boundary.y}),
                          key_id(target, previous_natural));
                check_hit(layout, screen({boundary.x + 1.0L / 32.0L, boundary.y}), id);
                if (p[0].x == p[3].x) {
                    const UiPoint vertical_edge{p[0].x, static_cast<float>(boundary.y)};
                    CHECK(!previous.hit.contains(vertical_edge) && key.hit.contains(vertical_edge));
                    check_hit(layout, vertical_edge, id);
                }
            }
            previous_natural = index;
            ++natural;
        }
        // Bottom/right endpoints themselves have no ownership in this quad.
        CHECK(!key.hit.contains(p[1]));
        CHECK(!key.hit.contains(p[2]) && !key.hit.contains(p[3]));
        CHECK(key.hit.contains(p[0]));
    }
    CHECK(natural == natural_count);
    CHECK(accidentals == (Count == 61 ? 25 : 10));
    if (expected.perspective) {
        const long double y = expected.y + expected.height / 10.0L;
        const long double left = expected.at_screen_y(0.0L, y).x;
        const long double right = expected.at_screen_y(1.0L, y).x;
        const UiPoint left_corner = screen({(expected.x + left) / 2.0L, y});
        const UiPoint right_corner = screen({(expected.x + expected.width + right) / 2.0L, y});
        CHECK(keys.front().bounds.contains(left_corner));
        CHECK(keys.back().bounds.contains(right_corner));
        CHECK(!keys.front().hit.contains(left_corner));
        CHECK(!keys.back().hit.contains(right_corner));
        CHECK(ui_hit_test(layout, left_corner).kind == UiControlKind::None);
        CHECK(ui_hit_test(layout, right_corner).kind == UiControlKind::None);
        const long double face_depth = std::clamp(7.0L * expected.height / 50.0L, 6.0L, 18.0L);
        const long double front_y = expected.y + expected.height - face_depth / 2.0L;
        const long double front_left = expected.at_screen_y(0.0L, front_y).x;
        const long double front_right = expected.at_screen_y(1.0L, front_y).x;
        const auto left_front_corner = screen({(expected.x + front_left) / 2.0L, front_y});
        const auto right_front_corner = screen({(expected.x + expected.width + front_right) / 2.0L, front_y});
        CHECK(keys.front().bounds.contains(left_front_corner));
        CHECK(keys.back().bounds.contains(right_front_corner));
        CHECK(!keys.front().hit.contains(left_front_corner));
        CHECK(!keys.front().front.contains(left_front_corner));
        CHECK(!keys.back().hit.contains(right_front_corner));
        CHECK(!keys.back().front.contains(right_front_corner));
        CHECK(ui_hit_test(layout, left_front_corner).kind == UiControlKind::None);
        CHECK(ui_hit_test(layout, right_front_corner).kind == UiControlKind::None);
    }
}

void check_presets(const UiLayout& layout) {
    std::set<std::tuple<UiControlKind, Manual, DrawbarBank, std::uint8_t>> ids;
    std::array<std::size_t, 2> counts{};
    for (std::size_t index = 0; index < layout.control_count; ++index) {
        const auto& control = layout.controls[index];
        CHECK(ids.emplace(control.id.kind, control.id.manual, control.id.bank, control.id.index).second);
        if (control.id.kind != UiControlKind::PresetKey) continue;
        CHECK(control.id.manual == Manual::Upper || control.id.manual == Manual::Lower);
        CHECK(control.id.bank == DrawbarBank::A && control.id.index < 12);
        ++counts[static_cast<std::size_t>(control.id.manual)];
        const bool sharp = kAccidentals[control.id.index];
        const UiPoint point{control.bounds.x + control.bounds.width / 2.0F,
                            control.bounds.y + control.bounds.height * (sharp ? 0.5F : 0.9F)};
        check_hit(layout, point, control.id);
    }
    CHECK(ids.size() == 68 && counts[0] == 12 && counts[1] == 12);
}

void layout_matrix() {
    std::size_t layouts = 0;
    std::size_t key_records = 0;
    for (const auto size : kSizes) {
        for (const auto presentation : kPresentations) {
            for (const auto workspace : kWorkspaces) {
                for (const auto upper : {DrawbarBank::A, DrawbarBank::B}) {
                    for (const auto lower : {DrawbarBank::A, DrawbarBank::B}) {
                        UiLayout layout;
                        CHECK(make_ui_layout(size.x, size.y, {upper, lower}, layout, workspace, presentation));
                        CHECK(layout.width == size.x && layout.height == size.y);
                        CHECK(layout.workspace == workspace && layout.presentation == presentation);
                        CHECK(layout.show_cabinet == (size.x >= 1400.0F));
                        CHECK(layout.bank_controls_in_cheeks == (size.y >= 820.0F));
                        CHECK(layout.control_count == 68);
                        check_keyboard(layout, layout.manual_keys[0], layout.manual_panels[0], UiTarget::Upper, 36);
                        check_keyboard(layout, layout.manual_keys[1], layout.manual_panels[1], UiTarget::Lower, 36);
                        check_keyboard(layout, layout.pedal_keys, layout.pedal_panel, UiTarget::Pedals, 15);
                        check_presets(layout);
                        ++layouts;
                        key_records += 147;
                    }
                }
            }
        }
    }
    CHECK(layouts == 288 && key_records == 42336);
    std::cout << "projection matrix: " << layouts << " layouts, " << key_records
              << " playing-key records, " << layouts * 24 << " preset records\n";
}

void retained_literal_landmarks() {
    UiLayout layout;
    CHECK(make_ui_layout(1280.0F, 900.0F, {DrawbarBank::B, DrawbarBank::B}, layout));
    CHECK(layout.workspace == UiWorkspace::Play && layout.presentation == UiPresentation::Dimensional);
    // Independent literals protect the inset/panel relationship at the default
    // and atlas fixture, in addition to the full per-panel rational oracle.
    near_point(layout.manual_keys[0].front().hit.points[3], {200.0L, 604.0L}, 0.0002L);
    near_point(layout.manual_keys[0].front().hit.points[2], {229.333333333333L, 604.0L}, 0.0002L);
    CHECK(make_ui_layout(1672.0F, 941.0F, {DrawbarBank::B, DrawbarBank::B}, layout));
    near_point(layout.manual_keys[0].front().hit.points[0], {275.1013528L, 526.76L}, 0.0003L);
    near_point(layout.manual_keys[0].front().hit.points[3], {248.85784L, 635.24L}, 0.0003L);
    near_point(layout.manual_keys[0].back().hit.points[2], {1123.6416L, 635.24L}, 0.0003L);
}

void exact_half_open_quads() {
    const UiQuad trapezoid{{{{3.0F, 0.0F}, {97.0F, 0.0F},
                             {100.0F, 100.0F}, {0.0F, 100.0F}}}};
    // These rational edge points are exactly representable in binary32, so
    // nextafter exercises half-open ownership without a rounding ambiguity.
    for (const float y : {0.0F, 25.0F, 50.0F, 75.0F}) {
        const float left = 3.0F - 3.0F * y / 100.0F;
        const float right = 97.0F + 3.0F * y / 100.0F;
        CHECK(trapezoid.contains({left, y}));
        CHECK(!trapezoid.contains({std::nextafter(left, -std::numeric_limits<float>::infinity()), y}));
        CHECK(!trapezoid.contains({right, y}));
        CHECK(trapezoid.contains({std::nextafter(right, -std::numeric_limits<float>::infinity()), y}));
    }
    CHECK(trapezoid.contains({50.0F, 0.0F}));
    CHECK(!trapezoid.contains({50.0F, std::nextafter(0.0F, -1.0F)}));
    CHECK(!trapezoid.contains({50.0F, 100.0F}));
    CHECK(trapezoid.contains({50.0F, std::nextafter(100.0F, 0.0F)}));
    CHECK(!trapezoid.contains({0.0F, 0.0F}));
    CHECK(!trapezoid.contains({100.0F, 0.0F}));

    UiLayout isolated;
    isolated.control_count = 0;
    auto& key = isolated.manual_keys[0][0];
    key.note = {UiTarget::Upper, 36};
    key.hit = trapezoid;
    key.bounds = {0.0F, 0.0F, 100.0F, 100.0F};
    CHECK(key.bounds.contains({1.0F, 25.0F}));
    CHECK(ui_hit_test(isolated, {1.0F, 25.0F}).kind == UiControlKind::None);
    CHECK(ui_hit_test(isolated, {2.25F, 25.0F}) == key_id(UiTarget::Upper, 0));
    CHECK(ui_hit_test(isolated, {99.0F, 75.0F}) == key_id(UiTarget::Upper, 0));
    CHECK(ui_hit_test(isolated, {99.5F, 75.0F}).kind == UiControlKind::None);
}

void malformed_and_huge_quads() {
    const UiQuad valid{{{{3.0F, 0.0F}, {97.0F, 0.0F},
                         {100.0F, 100.0F}, {0.0F, 100.0F}}}};
    CHECK(!UiQuad{}.contains({0.0F, 0.0F}));
    for (const float invalid : {std::numeric_limits<float>::quiet_NaN(),
                               std::numeric_limits<float>::infinity(),
                               -std::numeric_limits<float>::infinity()}) {
        CHECK(!valid.contains({invalid, 50.0F}) && !valid.contains({50.0F, invalid}));
        for (std::size_t vertex = 0; vertex < 4; ++vertex) {
            auto bad = valid;
            bad.points[vertex].x = invalid;
            CHECK(!bad.contains({50.0F, 50.0F}));
            bad = valid;
            bad.points[vertex].y = invalid;
            CHECK(!bad.contains({50.0F, 50.0F}));
        }
    }
    for (const std::size_t edge : {std::size_t{0}, std::size_t{2}}) {
        auto bad = valid;
        bad.points[edge].y = std::nextafter(bad.points[edge].y, 1000.0F);
        CHECK(!bad.contains({50.0F, 50.0F}));
    }
    for (const float bottom : {-100.0F, 0.0F}) {
        auto bad = valid;
        bad.points[2].y = bottom;
        bad.points[3].y = bottom;
        CHECK(!bad.contains({50.0F, 0.0F}));
    }
    for (const bool top : {true, false}) {
        for (const float delta : {0.0F, -1.0F}) {
            auto bad = valid;
            const std::size_t left = top ? 0 : 3;
            const std::size_t right = top ? 1 : 2;
            bad.points[right].x = bad.points[left].x + delta;
            CHECK(!bad.contains({50.0F, 50.0F}));
        }
    }
    const float maximum = std::numeric_limits<float>::max();
    const UiQuad huge_rectangle{{{{-maximum, -maximum}, {maximum, -maximum},
                                  {maximum, maximum}, {-maximum, maximum}}}};
    const UiQuad huge_slant{{{{-maximum, -maximum}, {0.0F, -maximum},
                              {maximum, maximum}, {0.0F, maximum}}}};
    for (std::size_t repeat = 0; repeat < 10000; ++repeat) {
        CHECK(huge_rectangle.contains({0.0F, 0.0F}));
        CHECK(huge_rectangle.contains({-maximum, -maximum}));
        CHECK(!huge_rectangle.contains({maximum, 0.0F}));
        CHECK(!huge_rectangle.contains({0.0F, maximum}));
        CHECK(huge_slant.contains({-maximum / 2.0F, 0.0F}));
        CHECK(huge_slant.contains({0.0F, 0.0F}));
        CHECK(!huge_slant.contains({maximum / 2.0F, 0.0F}));
    }
}

void layout_failure_is_atomic() {
    UiLayout destination;
    CHECK(make_ui_layout(1672.0F, 941.0F, {DrawbarBank::A, DrawbarBank::B}, destination,
                         UiWorkspace::Service, UiPresentation::Flat));
    std::array<unsigned char, sizeof(UiLayout)> before{};
    std::memcpy(before.data(), &destination, sizeof(destination));
    const auto unchanged = [&] {
        CHECK(std::memcmp(before.data(), &destination, sizeof(destination)) == 0);
    };
    for (const float bad : {0.0F, -1.0F, std::nextafter(960.0F, 0.0F),
                            std::nextafter(8192.0F, 9000.0F),
                            std::numeric_limits<float>::max(),
                            std::numeric_limits<float>::quiet_NaN(),
                            std::numeric_limits<float>::infinity(),
                            -std::numeric_limits<float>::infinity()}) {
        CHECK(!make_ui_layout(bad, 941.0F, {DrawbarBank::A, DrawbarBank::B}, destination));
        unchanged();
    }
    for (const float bad : {0.0F, -1.0F, std::nextafter(700.0F, 0.0F),
                            std::nextafter(8192.0F, 9000.0F),
                            std::numeric_limits<float>::max(),
                            std::numeric_limits<float>::quiet_NaN(),
                            std::numeric_limits<float>::infinity(),
                            -std::numeric_limits<float>::infinity()}) {
        CHECK(!make_ui_layout(1672.0F, bad, {DrawbarBank::A, DrawbarBank::B}, destination));
        unchanged();
    }
    for (unsigned int value = 0; value <= 255; ++value) {
        if (value >= 2) {
            const auto bad = static_cast<DrawbarBank>(value);
            CHECK(!make_ui_layout(1672.0F, 941.0F, {bad, DrawbarBank::B}, destination));
            unchanged();
            CHECK(!make_ui_layout(1672.0F, 941.0F, {DrawbarBank::A, bad}, destination));
            unchanged();
            CHECK(!make_ui_layout(1672.0F, 941.0F, {DrawbarBank::A, DrawbarBank::B}, destination,
                                  UiWorkspace::Play, static_cast<UiPresentation>(value)));
            unchanged();
        }
        if (value >= 3) {
            CHECK(!make_ui_layout(1672.0F, 941.0F, {DrawbarBank::A, DrawbarBank::B}, destination,
                                  static_cast<UiWorkspace>(value), UiPresentation::Flat));
            unchanged();
        }
    }
    for (const float bad : {std::numeric_limits<float>::quiet_NaN(),
                            std::numeric_limits<float>::infinity(),
                            -std::numeric_limits<float>::infinity()}) {
        CHECK(ui_hit_test(destination, {bad, 50.0F}).kind == UiControlKind::None);
        CHECK(ui_hit_test(destination, {50.0F, bad}).kind == UiControlKind::None);
    }
}
} // namespace

int main() {
    independent_oracle_landmarks();
    exact_half_open_quads();
    malformed_and_huge_quads();
    layout_failure_is_atomic();
    retained_literal_landmarks();
    layout_matrix();
    std::cout << "independent projection, silhouette, half-open ownership and rollback acceptance passed\n";
}
