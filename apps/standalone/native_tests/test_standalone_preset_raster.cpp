#include "InstrumentView.h"

#include <SDL.h>

#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <string_view>
#include <variant>
#include <vector>

namespace {
using namespace hammond;
using namespace hammond::standalone;

std::size_t failures = 0;
std::size_t label_cases = 0;
std::size_t readable_glyph_cases = 0;
std::size_t isolation_cases = 0;
std::size_t state_cases = 0;

void require(bool condition, std::string_view detail) {
    if (!condition) throw std::runtime_error(std::string(detail) + ": " + SDL_GetError());
}

void check(bool condition, std::string_view detail) {
    if (!condition) {
        ++failures;
        std::cerr << "FAIL: " << detail << '\n';
    }
}

UiControlId preset(unsigned manual, unsigned index) {
    return {UiControlKind::PresetKey, static_cast<Manual>(manual), DrawbarBank::A,
            static_cast<std::uint8_t>(index)};
}

void focus(UiModel& model, UiControlId id) {
    for (unsigned i = 0; i < 71 && model.view().focus != id; ++i) {
        require(model.key({UiKey::Tab, true}).count == 0, "focus navigation emits no action");
        require(model.key({UiKey::Tab, false}).count == 0, "Tab release emits no action");
    }
    require(model.view().focus == id, "focus reaches requested identity");
}

const UiControlGeometry& geometry(const UiModel& model, UiControlId id) {
    for (std::size_t i = 0; i < model.layout().control_count; ++i)
        if (model.layout().controls[i].id == id) return model.layout().controls[i];
    throw std::runtime_error("missing preset geometry");
}

struct Frame {
    int width{}, height{};
    std::vector<std::uint8_t> rgba;

    std::size_t index(int x, int y) const {
        require(x >= 0 && y >= 0 && x < width && y < height, "pixel region inside frame");
        return (static_cast<std::size_t>(y) * static_cast<std::size_t>(width) +
                static_cast<std::size_t>(x)) * 4;
    }
};

struct Region { int left{}, top{}, right{}, bottom{}; };

Region interior(UiRect bounds) {
    return {static_cast<int>(std::ceil(bounds.x)), static_cast<int>(std::ceil(bounds.y)),
            static_cast<int>(std::floor(bounds.x + bounds.width)),
            static_cast<int>(std::floor(bounds.y + bounds.height))};
}

std::size_t differences(const Frame& a, const Frame& b, UiRect bounds) {
    require(a.width == b.width && a.height == b.height, "frame dimensions agree");
    const auto area = interior(bounds);
    std::size_t count = 0;
    for (int y = area.top; y < area.bottom; ++y)
        for (int x = area.left; x < area.right; ++x) {
            const auto i = a.index(x, y);
            if (a.rgba[i] != b.rgba[i] || a.rgba[i + 1] != b.rgba[i + 1] ||
                a.rgba[i + 2] != b.rgba[i + 2] || a.rgba[i + 3] != b.rgba[i + 3]) ++count;
        }
    return count;
}

std::size_t color_count(const Frame& frame, UiRect bounds, UiColor color) {
    const auto area = interior(bounds);
    std::size_t count = 0;
    for (int y = area.top; y < area.bottom; ++y)
        for (int x = area.left; x < area.right; ++x) {
            const auto i = frame.index(x, y);
            if (frame.rgba[i] == color.red && frame.rgba[i + 1] == color.green &&
                frame.rgba[i + 2] == color.blue) ++count;
        }
    return count;
}

struct InkComparison { std::size_t pixels{}, changed{}; };

InkComparison compare_pitch_ink(const Frame& before, const Frame& after,
                                UiRect label, bool accidental) {
    const auto area = interior(label);
    InkComparison result;
    for (int y = area.top; y < area.bottom; ++y)
        for (int x = area.left; x < area.right; ++x) {
            const auto i = before.index(x, y);
            // The contract uses light single-letter text on dark naturals and
            // dark pitch text on ivory accidentals. High-contrast ink samples
            // exclude blank label margins, bevels and faint filtered edges.
            const bool ink = accidental ?
                before.rgba[i] < 125 && before.rgba[i + 1] < 115 && before.rgba[i + 2] < 100 :
                before.rgba[i] > 130 && before.rgba[i + 1] > 110;
            if (!ink) continue;
            ++result.pixels;
            if (before.rgba[i] != after.rgba[i] || before.rgba[i + 1] != after.rgba[i + 1] ||
                before.rgba[i + 2] != after.rgba[i + 2]) ++result.changed;
        }
    return result;
}

Frame read_frame(Drawing& drawing, int width, int height) {
    SDL_RenderPresent(drawing.renderer());
    Frame frame{width, height, std::vector<std::uint8_t>(
        static_cast<std::size_t>(width) * static_cast<std::size_t>(height) * 4)};
    require(SDL_RenderReadPixels(drawing.renderer(), nullptr, SDL_PIXELFORMAT_RGBA32,
        frame.rgba.data(), width * 4) == 0, "read actual instrument raster");
    return frame;
}

Frame render(Drawing& drawing, const UiModel& model, int width, int height) {
    InstrumentViewInfo info;
    paint_instrument(drawing, model, info);
    return read_frame(drawing, width, height);
}

UiModel prepared(int width, int height, UiPresentation presentation) {
    UiModel model;
    require(model.resize(static_cast<float>(width), static_cast<float>(height)), "resize model");
    require(model.set_presentation(presentation), "select complete presentation");
    SessionSnapshot snapshot;
    snapshot.publication_revision = 2;
    snapshot.controls.fixed_registrations = {FixedRegistration::CSharp, FixedRegistration::None};
    snapshot.controls.selected_banks = {DrawbarBank::B, DrawbarBank::A};
    snapshot.controls.percussion.enabled = true;
    model.observe(snapshot);
    return model;
}

void readable_accidentals(Drawing& drawing, const UiModel& model, const Frame& actual) {
    constexpr std::array<unsigned, 5> indices{1, 3, 6, 8, 10};
    constexpr std::array<std::string_view, 5> letters{"C", "D", "F", "G", "A"};
    // An independent native glyph template fixes the required size, characters
    // and two row positions. The material is uniform across each interior row,
    // so an unlettered adjacent pixel supplies its actual background. Recompose
    // the expected glyph on that material to check every antialiased sample.
    require(SDL_SetRenderDrawColor(drawing.renderer(), 255, 255, 255, 255) == 0,
            "set glyph template background");
    require(SDL_RenderClear(drawing.renderer()) == 0, "clear glyph template target");
    for (unsigned manual = 0; manual < 2; ++manual) {
        for (std::size_t index = 0; index < indices.size(); ++index) {
            const auto& label = geometry(model, preset(manual, indices[index])).label_bounds;
            for (unsigned row = 0; row < 2; ++row) {
                const auto glyph = row == 0 ? letters[index] : std::string_view{"#"};
                const float advance = drawing.text_width(glyph, 9.0F);
                check(advance <= label.width, "full-size accidental glyph fits without shrinking");
                drawing.text(glyph, label.x + (label.width - advance) / 2.0F,
                    label.y + 0.1F + 9.0F * static_cast<float>(row), 9.0F, {0, 0, 0});
            }
        }
    }
    const auto mask = read_frame(drawing, actual.width, actual.height);
    require(SDL_RenderClear(drawing.renderer()) == 0, "clear material template target");
    for (unsigned manual = 0; manual < 2; ++manual) {
        for (std::size_t index = 0; index < indices.size(); ++index) {
            const auto& key = geometry(model, preset(manual, indices[index]));
            const auto& label = key.label_bounds;
            const int left = static_cast<int>(std::floor(key.bounds.x)) + 2;
            const int right = static_cast<int>(std::floor(key.bounds.x + key.bounds.width)) - 2;
            const int sample_x = right - 1;
            for (int y = static_cast<int>(std::floor(label.y));
                 y < static_cast<int>(std::ceil(label.y + label.height)); ++y) {
                const auto i = actual.index(sample_x, y);
                check(mask.rgba[i] == 255, "material sample is outside the full-size glyph");
                drawing.rect({static_cast<float>(left), static_cast<float>(y),
                              static_cast<float>(right - left), 1.0F},
                             {actual.rgba[i], actual.rgba[i + 1], actual.rgba[i + 2]});
            }
            for (unsigned row = 0; row < 2; ++row) {
                const auto glyph = row == 0 ? letters[index] : std::string_view{"#"};
                const float advance = drawing.text_width(glyph, 9.0F);
                drawing.text(glyph, label.x + (label.width - advance) / 2.0F,
                    label.y + 0.1F + 9.0F * static_cast<float>(row), 9.0F, {37, 29, 20});
            }
        }
    }
    const auto expected = read_frame(drawing, actual.width, actual.height);
    for (unsigned manual = 0; manual < 2; ++manual) {
        for (const auto index : indices) {
            const auto& key = geometry(model, preset(manual, index));
            const auto& label = key.label_bounds;
            for (unsigned row = 0; row < 2; ++row) {
                auto area = interior({label.x, label.y + 9.0F * static_cast<float>(row),
                                      label.width, 9.0F});
                area.left = static_cast<int>(std::floor(key.bounds.x)) + 2;
                area.right = static_cast<int>(std::floor(key.bounds.x + key.bounds.width)) - 2;
                std::size_t ink = 0;
                std::size_t mismatches = 0;
                for (int y = area.top; y < area.bottom; ++y) {
                    for (int x = area.left; x < area.right; ++x) {
                        const auto i = actual.index(x, y);
                        if (mask.rgba[i] < 255) ++ink;
                        if (expected.rgba[i] != actual.rgba[i] ||
                            expected.rgba[i + 1] != actual.rgba[i + 1] ||
                            expected.rgba[i + 2] != actual.rgba[i + 2]) ++mismatches;
                    }
                }
                check(ink > 0 && mismatches == 0,
                      std::to_string(actual.width) + "x" + std::to_string(actual.height) +
                      " manual " + std::to_string(manual) + " accidental " + std::to_string(index) +
                      " row " + std::to_string(row) + " matches independently rendered 9-unit glyph pixels (" +
                      std::to_string(ink) + " ink, " + std::to_string(mismatches) + " mismatches)");
                ++readable_glyph_cases;
            }
        }
    }
}

void focus_labels(Drawing& drawing, int width, int height, UiPresentation presentation) {
    auto model = prepared(width, height, presentation);
    const auto unfocused = render(drawing, model, width, height);
    readable_accidentals(drawing, model, unfocused);
    constexpr std::array<unsigned, 5> sharps{1, 3, 6, 8, 10};
    for (unsigned manual = 0; manual < 2; ++manual) {
        for (unsigned index = 0; index < 12; ++index) {
            focus(model, preset(manual, index));
            const auto focused = render(drawing, model, width, height);
            const auto& key = geometry(model, preset(manual, index));
            const auto description = std::to_string(width) + "x" + std::to_string(height) +
                " manual " + std::to_string(manual) + " pitch " + std::to_string(index);
            bool accidental = false;
            for (const auto sharp : sharps) accidental = accidental || sharp == index;
            const auto ink = compare_pitch_ink(unfocused, focused, key.label_bounds, accidental);
            if (ink.changed != 0)
                std::cerr << "Changed pitch ink " << description << ": " << ink.changed <<
                    '/' << ink.pixels << '\n';
            check(ink.pixels > 0 && ink.changed == 0,
                  description + " preserves independently classified pitch ink under focus");
            check(color_count(focused, key.bounds, kUiFocusCyan) >= 2,
                  description + " has a visible independent focus indicator");
            ++label_cases;
            check(differences(unfocused, focused, model.layout().preset_key_panels[1 - manual]) == 0,
                  description + " focus leaves the other manual untouched");
            ++isolation_cases;
            if (!accidental) {
                for (const auto sharp : sharps) {
                    check(differences(unfocused, focused, geometry(model, preset(manual, sharp)).bounds) == 0,
                          description + " natural focus never crosses an ivory accidental");
                    ++isolation_cases;
                }
            }
        }
    }
}

void acknowledge(UiModel& model, const UiActions& actions, std::uint64_t revision,
                 std::uint64_t sequence) {
    require(actions.count == 1 && std::holds_alternative<SessionCommand>(actions.items[0]),
            "preset emits one musical command");
    const auto& command = std::get<SessionCommand>(actions.items[0]);
    require(std::holds_alternative<ControlSnapshot>(command), "preset command is copied controls");
    require(model.submitted(command, {SessionStatus::Ok, sequence}).count == 0,
            "accepted command requires no recovery");
    SessionSnapshot applied;
    applied.controls = std::get<ControlSnapshot>(command);
    applied.publication_revision = revision;
    applied.resolved_sequence = sequence;
    applied.last_applied_sequence = sequence;
    model.observe(applied);
}

void pending_cancel_rejection(Drawing& drawing, int width, int height, UiPresentation presentation) {
    constexpr UiColor pending_color{235, 169, 73};
    auto model = prepared(width, height, presentation);
    focus(model, {UiControlKind::SaveControls});
    const auto baseline = render(drawing, model, width, height);
    const auto upper = model.layout().preset_key_panels[0];
    const auto lower = model.layout().preset_key_panels[1];
    const auto sharp = geometry(model, preset(0, 1)).bounds;
    const auto f = geometry(model, preset(0, 5)).bounds;
    const auto c = geometry(model, preset(0, 0)).bounds;
    const UiRect c_exposed{c.x, c.y + c.height * 0.62F, c.width, c.height * 0.38F};

    const auto request = model.activate(preset(0, 5));
    focus(model, {UiControlKind::SaveControls});
    const auto pending = render(drawing, model, width, height);
    check(differences(baseline, pending, sharp) == 0, "pending F retains the applied C# face");
    check(differences(baseline, pending, lower) == 0, "Upper pending leaves Lower pixels unchanged");
    check(color_count(pending, f, pending_color) > 0, "desired F has an amber request outline");
    check(color_count(pending, sharp, pending_color) == 0, "applied C# is not the requested target");
    state_cases += 4;
    acknowledge(model, request, 4, 1);
    const auto accepted = render(drawing, model, width, height);
    check(differences(baseline, accepted, sharp) > 0, "acknowledgment releases the old C# face");
    check(differences(pending, accepted, f) > 0, "acknowledgment changes the requested F face");
    check(color_count(accepted, upper, pending_color) == 0, "acknowledgment clears request ink");
    state_cases += 3;

    const auto cancel = model.activate(preset(0, 0));
    focus(model, {UiControlKind::SaveControls});
    const auto cancel_pending = render(drawing, model, width, height);
    check(color_count(cancel_pending, c, pending_color) > 0, "Cancel may show a pending request");
    acknowledge(model, cancel, 6, 2);
    const auto cancelled = render(drawing, model, width, height);
    check(differences(baseline, cancelled, c_exposed) == 0, "acknowledged Cancel leaves C at its original raised face");
    check(color_count(cancelled, upper, pending_color) == 0, "Cancel acknowledgment clears request ink");
    state_cases += 3;

    SessionSnapshot hidden;
    hidden.controls = model.view().applied.controls;
    hidden.controls.fixed_registrations[0] = FixedRegistration::A;
    hidden.controls.selected_banks[0] = DrawbarBank::A;
    hidden.publication_revision = 8;
    hidden.resolved_sequence = 2;
    model.observe(hidden);
    const auto hidden_changed = render(drawing, model, width, height);
    check(differences(cancelled, hidden_changed, upper) == 0,
          "cancelled raw fixed/bank memory cannot paint a latched route");
    ++state_cases;

    const auto reject = model.activate(preset(0, 7));
    const auto& command = std::get<SessionCommand>(reject.items[0]);
    require(model.submitted(command, {SessionStatus::QueueFull, 0}).count == 0,
            "transport rejection uses out-of-band recovery");
    focus(model, {UiControlKind::SaveControls});
    const auto rejected = render(drawing, model, width, height);
    check(differences(hidden_changed, rejected, upper) == 0,
          "rejection clears the request and preserves applied Cancel pixels");
    ++state_cases;
}
} // namespace

int main() {
    SDL_SetMainReady();
    try {
        require(SDL_Init(0) == 0, "initialize SDL without hardware subsystems");
        for (const auto dimensions : std::array<std::array<int, 2>, 4>{{
                 {960, 700}, {1280, 900}, {1672, 941}, {1400, 820}}}) {
            const int width = dimensions[0];
            const int height = dimensions[1];
            const std::unique_ptr<SDL_Surface, decltype(&SDL_FreeSurface)> surface(
                SDL_CreateRGBSurfaceWithFormat(0, width, height, 32, SDL_PIXELFORMAT_RGBA32), SDL_FreeSurface);
            require(surface != nullptr, "create software target");
            const std::unique_ptr<SDL_Renderer, decltype(&SDL_DestroyRenderer)> renderer(
                SDL_CreateSoftwareRenderer(surface.get()), SDL_DestroyRenderer);
            require(renderer != nullptr, "create software renderer");
            Drawing drawing(renderer.get());
            std::string error;
            require(drawing.initialize(error), "initialize native Drawing: " + error);
            for (const auto presentation : {UiPresentation::Dimensional, UiPresentation::Flat}) {
                focus_labels(drawing, width, height, presentation);
                pending_cancel_rejection(drawing, width, height, presentation);
            }
        }
        SDL_Quit();
    } catch (const std::exception& error) {
        std::cerr << "Preset raster setup failed: " << error.what() << '\n';
        SDL_Quit();
        return EXIT_FAILURE;
    }
    std::cout << "Native preset raster: " << label_cases << " preserved label/focus cases, "
              << readable_glyph_cases << " full-size accidental glyph cases, "
              << isolation_cases << " other-manual/accidental isolation cases, "
              << state_cases << " applied/pending/Cancel/rejection checks; failures="
              << failures << "; SDL software surface, no window/audio\n";
    return failures == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
