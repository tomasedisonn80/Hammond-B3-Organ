#include "MidiInput.h"
#include "TestSupport.h"
#include "UiModel.h"

#include <array>
#include <bit>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <variant>

namespace {
using namespace hammond;
using namespace hammond::standalone;

static_assert(kMidiExpressionCalibrationModelId == "midi-expression-endpoints-v1");

auto diagnostics(const MidiInput& input) {
    const auto& value = input.diagnostics();
    return std::array{value.packets, value.actions, value.unsupported, value.unmapped_channels,
        value.out_of_range, value.malformed, value.inactive, value.timestamp_regressions, value.epochs};
}

MidiDecoded cc(MidiInput& input, std::uint8_t controller, std::uint8_t raw,
               std::uint64_t time = 0, std::uint8_t status = 0xB0) {
    return input.decode(MidiPacket{{status, controller, raw}, 3, time});
}

MidiParameterEdit edit(const MidiDecoded& decoded) {
    CHECK(decoded.status == MidiDecodeStatus::Action);
    CHECK(std::holds_alternative<MidiParameterEdit>(decoded.action));
    return std::get<MidiParameterEdit>(decoded.action);
}

void mapping_boundaries() {
    // Every representable endpoint pair has one exact admission rule. Rejection
    // preserves even a destination with a nonnumeric bit pattern.
    constexpr std::uint64_t sentinel_bits = 0x7ff8000000000031ULL;
    for (unsigned minimum = 0; minimum < 256; ++minimum) {
        for (unsigned maximum = 0; maximum < 256; ++maximum) {
            const MidiExpressionCalibration calibration{
                static_cast<std::uint8_t>(minimum), static_cast<std::uint8_t>(maximum), false};
            const bool valid = minimum < maximum && maximum <= 127;
            CHECK(valid_midi_expression_calibration(calibration) == valid);
            if (!valid) {
                double destination = std::bit_cast<double>(sentinel_bits);
                CHECK(!map_midi_expression(calibration, 64, destination));
                CHECK(std::bit_cast<std::uint64_t>(destination) == sentinel_bits);
            }
        }
    }
    for (unsigned raw = 0; raw < 256; ++raw) {
        double destination = std::bit_cast<double>(sentinel_bits);
        const bool accepted = map_midi_expression({}, static_cast<std::uint8_t>(raw), destination);
        CHECK(accepted == (raw <= 127));
        if (accepted) {
            CHECK(std::bit_cast<std::uint64_t>(destination) ==
                  std::bit_cast<std::uint64_t>(static_cast<double>(raw) / 127.0));
        } else {
            CHECK(std::bit_cast<std::uint64_t>(destination) == sentinel_bits);
        }
    }
    for (const auto endpoints : {std::array<unsigned, 2>{0, 127}, {20, 100}, {1, 2}, {126, 127}}) {
        for (const bool inverted : {false, true}) {
            const MidiExpressionCalibration calibration{
                static_cast<std::uint8_t>(endpoints[0]),
                static_cast<std::uint8_t>(endpoints[1]), inverted};
            double previous = inverted ? 1.0 : 0.0;
            for (unsigned raw = 0; raw <= 127; ++raw) {
                double result = -1.0;
                CHECK(map_midi_expression(calibration, static_cast<std::uint8_t>(raw), result));
                const double fraction = raw <= endpoints[0] ? 0.0 : raw >= endpoints[1] ? 1.0 :
                    static_cast<double>(raw - endpoints[0]) / (endpoints[1] - endpoints[0]);
                CHECK(result == (inverted ? 1.0 - fraction : fraction));
                CHECK(std::isfinite(result) && result >= 0.0 && result <= 1.0);
                CHECK(inverted ? result <= previous : result >= previous);
                previous = result;
            }
        }
    }
}

void immutable_epochs_and_controller_scope() {
    MidiInput input;
    const MidiExpressionCalibration narrow{20, 100, true};
    const auto empty = diagnostics(input);
    CHECK(!input.begin_epoch({}, {100, 20, false}));
    CHECK(input.expression_calibration() == MidiExpressionCalibration{});
    CHECK(diagnostics(input) == empty && !input.active());
    CHECK(input.begin_epoch({16, 4, 9}, narrow));
    CHECK(edit(cc(input, 11, 80, 100, 0xBF)).normalized == 0.25);
    const auto before = diagnostics(input);
    CHECK(!input.begin_epoch());
    CHECK(!input.begin_epoch({1, 1, 3}, {}));
    CHECK(!input.begin_epoch({1, 2, 3}, {5, 5, false}));
    CHECK(diagnostics(input) == before);
    CHECK((input.routing() == MidiRouting{16, 4, 9}));
    CHECK(input.expression_calibration() == narrow && input.active());
    const auto regressed = cc(input, 11, 20, 99, 0xBF);
    CHECK(regressed.timestamp_regressed && edit(regressed).normalized == 1.0);
    for (const auto status : {std::uint8_t{0xBF}, std::uint8_t{0xB3}, std::uint8_t{0xB8}}) {
        const auto mapped = edit(cc(input, 11, 100, 100, status));
        CHECK(mapped.parameter_id == 8192 && mapped.normalized == 0.0);
        const auto reset = edit(cc(input, 121, 0, 100, status));
        CHECK(reset.parameter_id == 8192 && reset.normalized == 1.0);
        CHECK(input.expression_calibration() == narrow);
        const auto drawbar = edit(cc(input, 16, 80, 100, status));
        CHECK(drawbar.parameter_id == (status == 0xBF ? 4112U : status == 0xB3 ? 4144U : 16384U));
        CHECK(drawbar.normalized == 80.0 / 127.0);
    }
    input.end_epoch();
    const auto retired = diagnostics(input);
    CHECK(!input.begin_epoch({}, {127, 127, false}));
    CHECK(!input.begin_epoch({1, 1, 3}, {}));
    CHECK(!input.active() && input.expression_calibration() == narrow);
    CHECK((input.routing() == MidiRouting{16, 4, 9}));
    CHECK(diagnostics(input) == retired);
    const MidiExpressionCalibration next{10, 20, false};
    CHECK(input.begin_epoch({}, next));
    const auto fresh = cc(input, 11, 15, 1);
    CHECK(!fresh.timestamp_regressed && edit(fresh).normalized == 0.5);
    CHECK(input.expression_calibration() == next && input.diagnostics().epochs == 2);
}

void pending_controls_and_reset(const RuntimeProfile& profile) {
    Session session;
    UiModel ui;
    MidiInput input;
    CHECK(session.prepare(profile, {48000.0, 128, 0, 0}) == SessionStatus::Ok);
    CHECK(session.start() == SessionStatus::Ok);
    CHECK(input.begin_epoch({}, {20, 100, true}));
    const auto observe = [&] {
        SessionSnapshot state;
        CHECK(session.read_snapshot(state));
        ui.observe(state);
        return state;
    };
    const auto submit = [&](const UiActions& actions) {
        for (const auto& action : actions.span()) {
            CHECK(std::holds_alternative<SessionCommand>(action));
            const auto& command = std::get<SessionCommand>(action);
            const auto result = session.post(command);
            CHECK(result);
            CHECK(ui.submitted(command, result).count == 0);
        }
    };
    const auto apply = [&](const MidiDecoded& decoded) {
        const auto value = edit(decoded);
        submit(ui.external_parameter(value.parameter_id, value.normalized));
    };
    (void)observe();
    ControlSnapshot registration;
    registration.percussion.enabled = true;
    registration.pedal_drawbars = {7, 3};
    registration.drawbars[1][0][4] = 5;
    submit(ui.load_controls(registration));
    for (const auto status : {std::uint8_t{0x90}, std::uint8_t{0x91}, std::uint8_t{0x92}}) {
        const auto note = input.decode(MidiPacket{{status, 48, 100}, 3, 0});
        CHECK(note.status == MidiDecodeStatus::Action);
        CHECK(std::holds_alternative<SessionCommand>(note.action));
        CHECK(session.post(std::get<SessionCommand>(note.action)));
    }
    CHECK(session.render(0, {}));
    const auto held = observe();
    apply(cc(input, 11, 80));
    CHECK(ui.view().controls.expression == 0.25 && ui.view().controls_pending);
    submit(ui.external_parameter(4112, 1.0)); // Pending unrelated upper-B edit.
    apply(cc(input, 121, 0, 0, 0xB2));
    CHECK(ui.view().controls.expression == 1.0 && ui.view().controls.drawbars[0][1][0] == 8);
    CHECK(ui.view().controls_pending);
    CHECK(session.render(0, {}));
    const auto applied = observe();
    registration.drawbars[0][1][0] = 8;
    CHECK(applied.controls == registration);
    CHECK(applied.held_keys == held.held_keys && applied.held_pedals == held.held_pedals);
    CHECK(applied.held_keys[0][12] && applied.held_keys[1][12] && applied.held_pedals[12]);
    CHECK(applied.recovery_count == 0 && applied.rejected_commands == 0);
    CHECK(!ui.view().controls_pending);
    CHECK((input.expression_calibration() == MidiExpressionCalibration{20, 100, true}));
    CHECK(ui.external_parameter(8192, edit(cc(input, 121, 0)).normalized).count == 0);
}
} // namespace

int main() {
    mapping_boundaries();
    immutable_epochs_and_controller_scope();
    pending_controls_and_reset(load_test_profile());
    std::cout << "standalone expression calibration: endpoints, immutable epochs and reset pipeline passed\n";
}
