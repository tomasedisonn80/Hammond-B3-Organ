#include "TestSupport.h"
#include "UiModel.h"

#include <cmath>
#include <iostream>
#include <limits>
#include <variant>

namespace {
using namespace hammond;
using namespace hammond::standalone;

const SessionCommand& command(const UiActions& actions) {
    CHECK(actions.count == 1);
    CHECK(std::holds_alternative<SessionCommand>(actions.items[0]));
    return std::get<SessionCommand>(actions.items[0]);
}

void shared_pending_state() {
    Session session;
    UiModel model;
    CHECK(session.prepare(load_test_profile(), {48000.0, 64, 7, 0}) == SessionStatus::Ok);
    CHECK(session.start() == SessionStatus::Ok);
    SessionSnapshot before;
    CHECK(session.read_snapshot(before));
    model.observe(before);
    const auto post = [&](const UiActions& actions) {
        const auto& item = command(actions);
        const auto result = session.post(item);
        CHECK(result.ok());
        CHECK(model.submitted(item, result).count == 0);
    };

    // Neither a callback nor an observation occurs between these independent
    // controller and on-screen edits. Later snapshots must retain both values.
    post(model.external_parameter(8192, 0.25));
    post(model.external_parameter(4112, 1.0));
    post(model.activate({UiControlKind::Percussion, Manual::Upper, DrawbarBank::A, 0}));
    CHECK(model.view().controls_pending);
    CHECK(model.view().controls.expression == 0.25);
    CHECK(model.view().controls.drawbars[0][1][0] == 8);
    CHECK(model.view().controls.percussion.enabled);

    // An older, still valid applied observation cannot undo queued intent.
    model.observe(before);
    CHECK(model.view().controls.expression == 0.25);
    CHECK(model.view().controls.drawbars[0][1][0] == 8);
    CHECK(session.render(0, {}).ok());
    SessionSnapshot after;
    CHECK(session.read_snapshot(after));
    model.observe(after);
    CHECK(!model.view().controls_pending);
    CHECK(after.controls.expression == 0.25);
    CHECK(after.controls.drawbars[0][1][0] == 8);
    CHECK(after.controls.percussion.enabled);
    CHECK(after.frame_clock == before.frame_clock);
    CHECK(after.held_keys == before.held_keys && after.held_pedals == before.held_pedals);
    CHECK(session.stop() == SessionStatus::Ok);
}

void invalid_and_unchanged_preserve_state() {
    UiModel model;
    const auto edited = model.external_parameter(8192, 0.5);
    CHECK(edited.count == 1);
    const auto controls = model.view().controls;
    const auto focus = model.view().focus;
    const auto banks = model.view().edited_banks;
    CHECK(model.external_parameter(8192, 0.5).count == 0);
    CHECK(model.external_parameter(0xffffffffU, 0.5).count == 0);
    for (const double value : {-0.01, 1.01, std::numeric_limits<double>::infinity(),
                               std::numeric_limits<double>::quiet_NaN()}) {
        CHECK(model.external_parameter(8192, value).count == 0);
    }
    CHECK(model.view().controls == controls);
    CHECK(model.view().focus == focus && model.view().edited_banks == banks);
    CHECK(model.view().controls_pending);
}
} // namespace

int main() {
    shared_pending_state();
    invalid_and_unchanged_preserve_state();
    std::cout << "External controls preserve shared pending UI intent\n";
}
