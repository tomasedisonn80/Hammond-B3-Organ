#include "LibraryModel.h"
#include "TestSupport.h"
#include "hammond/Engine.h"

#include <algorithm>
#include <array>
#include <bit>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <optional>
#include <span>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

// The model receives only copies returned by real Session::read_snapshot.
// nullopt is used explicitly in one failed-read case. Catalog entries are
// in-memory fixtures: this suite performs no library scan, save or disk write.
// Manual render boundaries need no SDL, device, thread, sleep or race timing.
namespace {
using namespace hammond;
using namespace hammond::standalone;

struct Counts {
    std::size_t assertions{}, snapshots{}, renders{}, accepted_posts{};
    std::size_t paired_stereo_samples{}, phase_checks{}, readiness_checks{};
} counts;
std::string_view current_case;

void require(bool condition, std::string_view expression, int line) {
    ++counts.assertions;
    if (!condition) {
        throw std::runtime_error(std::string(current_case) + ": line " +
            std::to_string(line) + ": " + std::string(expression));
    }
}
#define REQUIRE(expression) require(static_cast<bool>(expression), #expression, __LINE__)

constexpr float kSentinel = -7123.25F;

ControlSnapshot saved_controls() {
    ControlSnapshot result;
    result.drawbars[0][0] = {8, 1, 6, 0, 5, 2, 7, 3, 4};
    result.drawbars[0][1] = {3, 8, 2, 7, 1, 6, 0, 5, 4};
    result.drawbars[1][0] = {4, 0, 7, 2, 8, 1, 6, 3, 5};
    result.drawbars[1][1] = {5, 7, 1, 8, 2, 6, 3, 0, 4};
    result.selected_banks = {DrawbarBank::A, DrawbarBank::B};
    result.route_enabled = {false, true};
    result.fixed_registrations = {FixedRegistration::DSharp, FixedRegistration::GSharp};
    result.pedal_drawbars = {7, 3};
    result.percussion = {true, PercussionHarmonic::Third,
        PercussionVolume::Soft, PercussionDecay::Fast};
    result.expression = 0.125;
    REQUIRE(is_valid_control_snapshot(result));
    return result;
}

ControlSnapshot sounding_controls() {
    ControlSnapshot result;
    result.drawbars[0][0] = {0, 2, 4, 6, 8, 1, 3, 5, 7};
    result.drawbars[0][1] = {8, 0, 8, 0, 4, 0, 2, 0, 1};
    result.drawbars[1][0] = {5, 0, 7, 0, 3, 0, 2, 0, 1};
    result.drawbars[1][1] = {7, 5, 3, 1, 8, 6, 4, 2, 0};
    result.selected_banks = {DrawbarBank::B, DrawbarBank::A};
    result.route_enabled = {true, true};
    result.fixed_registrations = {FixedRegistration::None, FixedRegistration::None};
    result.pedal_drawbars = {6, 4};
    result.percussion = {true, PercussionHarmonic::Second,
        PercussionVolume::Normal, PercussionDecay::Slow};
    result.expression = 0.625;
    REQUIRE(is_valid_control_snapshot(result));
    return result;
}

// Literal field assertions are independent of merge_registration_controls and
// registration_controls_equal. In particular, cancelled fixed memory and the
// inactive banks must survive alongside the expression-only scope difference.
void require_saved_fields(const ControlSnapshot& actual, double expression) {
    REQUIRE((actual.drawbars[0][0] == DrawbarPositions{8, 1, 6, 0, 5, 2, 7, 3, 4}));
    REQUIRE((actual.drawbars[0][1] == DrawbarPositions{3, 8, 2, 7, 1, 6, 0, 5, 4}));
    REQUIRE((actual.drawbars[1][0] == DrawbarPositions{4, 0, 7, 2, 8, 1, 6, 3, 5}));
    REQUIRE((actual.drawbars[1][1] == DrawbarPositions{5, 7, 1, 8, 2, 6, 3, 0, 4}));
    REQUIRE((actual.selected_banks == std::array{DrawbarBank::A, DrawbarBank::B}));
    REQUIRE((actual.route_enabled == std::array{false, true}));
    REQUIRE((actual.fixed_registrations == std::array{
        FixedRegistration::DSharp, FixedRegistration::GSharp}));
    REQUIRE((actual.pedal_drawbars == PedalDrawbarPositions{7, 3}));
    REQUIRE(actual.percussion.enabled);
    REQUIRE(actual.percussion.harmonic == PercussionHarmonic::Third);
    REQUIRE(actual.percussion.volume == PercussionVolume::Soft);
    REQUIRE(actual.percussion.decay == PercussionDecay::Fast);
    REQUIRE(std::bit_cast<std::uint64_t>(actual.expression) ==
        std::bit_cast<std::uint64_t>(expression));
}

void same_controls(const ControlSnapshot& actual, const ControlSnapshot& expected) {
    REQUIRE(actual == expected);
    REQUIRE(std::bit_cast<std::uint64_t>(actual.expression) ==
        std::bit_cast<std::uint64_t>(expected.expression));
}

SessionSnapshot read(const Session& session) {
    SessionSnapshot result;
    REQUIRE(session.read_snapshot(result));
    REQUIRE((result.publication_revision & 1U) == 0);
    ++counts.snapshots;
    return result;
}

LibraryObservation fresh(const Session& session, bool enabled = true) {
    return {read(session), enabled};
}

void same_snapshot(const SessionSnapshot& actual, const SessionSnapshot& expected) {
    same_controls(actual.controls, expected.controls);
    REQUIRE(actual.held_keys == expected.held_keys);
    REQUIRE(actual.held_pedals == expected.held_pedals);
    REQUIRE(actual.frame_clock == expected.frame_clock);
    REQUIRE(actual.sample_rate == expected.sample_rate);
    REQUIRE(std::bit_cast<std::uint32_t>(actual.peak) ==
        std::bit_cast<std::uint32_t>(expected.peak));
    REQUIRE(actual.prepared == expected.prepared);
    REQUIRE(actual.running == expected.running);
    REQUIRE(actual.publication_revision == expected.publication_revision);
    REQUIRE(actual.resolved_sequence == expected.resolved_sequence);
    REQUIRE(actual.last_applied_sequence == expected.last_applied_sequence);
    REQUIRE(actual.recovery_count == expected.recovery_count);
    REQUIRE(actual.queue_overflows == expected.queue_overflows);
    REQUIRE(actual.rejected_commands == expected.rejected_commands);
    REQUIRE(actual.discarded_commands == expected.discarded_commands);
    REQUIRE(actual.fault_flags == expected.fault_flags);
    REQUIRE(actual.last_core_status == expected.last_core_status);
}

bool held(const SessionSnapshot& snapshot, Manual manual, std::uint8_t pitch) {
    return snapshot.held_keys[static_cast<std::size_t>(manual)][
        static_cast<std::size_t>(pitch - kMinManualMidiNote)];
}

void no_holds(const SessionSnapshot& snapshot) {
    for (const auto& manual : snapshot.held_keys) {
        REQUIRE(std::none_of(manual.begin(), manual.end(), [](bool value) { return value; }));
    }
    REQUIRE(std::none_of(snapshot.held_pedals.begin(), snapshot.held_pedals.end(),
        [](bool value) { return value; }));
}

SessionCommand manual_note(HostNoteKind kind, std::uint8_t bus, std::uint8_t channel,
    std::uint8_t pitch, std::int32_t owner, std::uint8_t velocity = 0) {
    return PerformanceInputEvent{HostNoteEvent{0, kind, bus, channel, pitch, velocity, owner}};
}

SessionCommand pedal_note(PedalNoteKind kind, std::uint8_t bus, std::uint8_t channel,
    std::uint8_t pedal, std::int32_t owner, std::uint8_t velocity = 0) {
    return PerformanceInputEvent{PedalNoteEvent{
        0, kind, bus, channel, PedalId{pedal}, velocity, owner}};
}

LibraryEntry entry(std::string name, RegistrationScope scope, const ControlSnapshot& controls) {
    LibraryEntry result;
    result.name = std::move(name);
    result.scope = scope;
    result.key = result.name + (scope == RegistrationScope::Registration ?
        ".b3registration" : ".b3performance");
    result.status = LibraryEntryStatus::Valid;
    result.controls = controls;
    return result;
}

void catalog(LibraryModel& model, std::vector<LibraryEntry> rows) {
    const auto refresh = model.request_refresh();
    REQUIRE(refresh.has_value());
    LibraryCatalog value;
    value.generation = refresh->generation;
    value.status = rows.empty() ? LibraryCatalogStatus::Empty : LibraryCatalogStatus::Ready;
    value.directory_items = rows.size();
    value.candidate_count = rows.size();
    value.entries = std::move(rows); // Call sites supply explicit sorted rows.
    REQUIRE(model.replace_catalog(value));
    REQUIRE(!model.view().catalog_stale);
}

LibraryOperationView operation(const LibraryModel& model) {
    const auto value = model.view();
    REQUIRE(value.operation.has_value());
    return *value.operation;
}

void terminal(const LibraryModel& model, LibraryOutcome expected) {
    const auto value = operation(model);
    REQUIRE(value.phase == LibraryOperationPhase::Finished);
    REQUIRE(value.outcome == expected);
}

std::vector<float> render(Session& session, std::uint32_t frames) {
    const auto before = read(session);
    std::vector<float> samples(static_cast<std::size_t>(frames) * 2 + 2, kSentinel);
    const auto result = session.render(frames,
        std::span<float>{samples}.subspan(1, static_cast<std::size_t>(frames) * 2));
    REQUIRE(result.status == SessionStatus::Ok);
    REQUIRE(result.frames_rendered == frames);
    REQUIRE(samples.front() == kSentinel && samples.back() == kSentinel);
    const auto after = read(session);
    REQUIRE(after.frame_clock == before.frame_clock + frames);
    REQUIRE(after.publication_revision == before.publication_revision + 2);
    ++counts.renders;
    return {samples.begin() + 1, samples.end() - 1};
}

struct Rig {
    Session session;
    LibraryModel model;
    std::uint64_t now{}, sequence{};

    explicit Rig(const RuntimeProfile& profile, bool running = true) {
        REQUIRE(session.prepare(profile, {48000.0, 512, 0x19a19ULL, 417}) == SessionStatus::Ok);
        model.audio_lifecycle_changed(LibraryAudioTransition::Prepare);
        if (running) {
            REQUIRE(session.start() == SessionStatus::Ok);
            model.audio_lifecycle_changed(LibraryAudioTransition::Start);
        }
        catalog(model, {});
        observe(running);
    }

    void observe(bool enabled = true) {
        model.observe(fresh(session, enabled), ++now);
        REQUIRE(model.view().observation_fresh);
    }

    std::uint64_t post(const SessionCommand& command,
        const std::optional<LibraryControlIntent>& token = std::nullopt) {
        const auto submitted = session.post(command);
        REQUIRE(submitted.status == SessionStatus::Ok);
        REQUIRE(submitted.sequence == sequence + 1);
        REQUIRE(model.submitted(submitted, token) == LibraryOutcome::Accepted);
        sequence = submitted.sequence;
        ++counts.accepted_posts;
        return sequence;
    }

    LibraryControlIntent control(const ControlSnapshot& controls) {
        const auto token = model.note_control_intent(controls, fresh(session));
        REQUIRE(token.has_value());
        same_controls(token->expected_controls, controls);
        post(controls, token);
        return *token;
    }

    void prove(const ControlSnapshot& controls) {
        (void)control(controls);
        (void)render(session, 0);
        observe();
        REQUIRE(!model.view().controls_pending);
        same_controls(read(session).controls, controls);
    }

    LibraryRecallIntent recall(const LibraryEntry& target, const ControlSnapshot& desired) {
        REQUIRE(model.select(target.key));
        const auto request = model.request_recall(target, desired, fresh(session), ++now);
        REQUIRE(request.outcome == LibraryOutcome::Accepted);
        REQUIRE(request.recall.has_value());
        REQUIRE(operation(model).phase == LibraryOperationPhase::AwaitingSubmission);
        REQUIRE(operation(model).submitted_sequence == 0);
        return *request.recall;
    }

    std::uint64_t dispatch(const LibraryRecallIntent& recall) {
        const auto accepted = post(recall.control_intent.expected_controls, recall.control_intent);
        REQUIRE(operation(model).phase == LibraryOperationPhase::AwaitingAcknowledgment);
        REQUIRE(operation(model).submitted_sequence == accepted);
        return accepted;
    }

    void refuse_save_without_basis() {
        REQUIRE(model.set_name("Unproved"));
        const auto request = model.request_save_new(fresh(session), ++now);
        REQUIRE(request.outcome == LibraryOutcome::NoAcknowledgedControls);
        REQUIRE(!request.recall);
    }
};

void equal_recall_waits_for_real_render(const RuntimeProfile& profile) {
    Rig rig(profile);
    const auto target = entry("Equal", RegistrationScope::Performance, read(rig.session).controls);
    catalog(rig.model, {target});
    rig.refuse_save_without_basis();
    rig.post(manual_note(HostNoteKind::On, 0, 2, 60, 1, 100));
    (void)render(rig.session, 17);
    rig.observe();
    REQUIRE(read(rig.session).last_applied_sequence != 0);
    rig.refuse_save_without_basis(); // An applied note never supplies a control basis.

    for (unsigned repetition = 0; repetition < 2; ++repetition) {
        const auto before = read(rig.session);
        const auto named = rig.recall(target, before.controls);
        same_controls(named.control_intent.expected_controls, before.controls);
        same_snapshot(read(rig.session), before); // Request itself has no Session effect.
        const auto accepted = rig.dispatch(named);
        REQUIRE(accepted > before.last_applied_sequence);
        same_snapshot(read(rig.session), before); // Accepted still means queued.
        rig.observe(); // This is a new real read of the same coherent publication.
        REQUIRE(operation(rig.model).phase == LibraryOperationPhase::AwaitingAcknowledgment);
        REQUIRE(rig.model.view().controls_pending);
        if (repetition == 0) REQUIRE(!rig.model.view().current_reference);
        (void)render(rig.session, 0);
        const auto after = read(rig.session);
        REQUIRE(after.publication_revision > before.publication_revision);
        REQUIRE(after.frame_clock == before.frame_clock);
        REQUIRE(after.resolved_sequence == accepted && after.last_applied_sequence == accepted);
        REQUIRE(after.held_keys == before.held_keys && after.held_pedals == before.held_pedals);
        rig.observe();
        terminal(rig.model, LibraryOutcome::Applied);
        REQUIRE(!rig.model.view().controls_pending);
        REQUIRE(rig.model.view().current_reference->key == target.key);
        REQUIRE(rig.model.view().current_reference->origin == LibraryReferenceOrigin::Recall);
        REQUIRE(!rig.model.view().current_reference->modified);
    }
}

void literal_scopes_use_pending_desired_expression(const RuntimeProfile& profile) {
    Rig rig(profile);
    auto initial = sounding_controls();
    initial.expression = 0.375;
    rig.prove(initial);
    const auto registration = entry("Registration", RegistrationScope::Registration, saved_controls());
    const auto performance = entry("Performance", RegistrationScope::Performance, saved_controls());
    catalog(rig.model, {performance, registration});

    auto desired = initial;
    desired.expression = 0.875;
    const auto expression_intent = rig.control(desired);
    REQUIRE(read(rig.session).controls.expression == 0.375);
    const auto named = rig.recall(registration, desired);
    REQUIRE(named.control_intent.desired_revision > expression_intent.desired_revision);
    require_saved_fields(named.control_intent.expected_controls, 0.875);
    const auto before = read(rig.session);
    rig.dispatch(named);
    same_snapshot(read(rig.session), before);
    rig.observe();
    REQUIRE(operation(rig.model).phase == LibraryOperationPhase::AwaitingAcknowledgment);
    (void)render(rig.session, 0);
    rig.observe();
    terminal(rig.model, LibraryOutcome::Applied);
    require_saved_fields(read(rig.session).controls, 0.875);

    auto expression_only = read(rig.session).controls;
    expression_only.expression = 0.5;
    (void)rig.control(expression_only);
    REQUIRE(!rig.model.view().current_reference->modified);
    (void)render(rig.session, 0);
    rig.observe();
    REQUIRE(!rig.model.view().current_reference->modified); // Registration scope.

    desired = read(rig.session).controls;
    desired.expression = 0.75;
    (void)rig.control(desired);
    const auto full = rig.recall(performance, desired);
    require_saved_fields(full.control_intent.expected_controls, 0.125);
    rig.dispatch(full);
    REQUIRE(read(rig.session).controls.expression == 0.5);
    (void)render(rig.session, 0);
    rig.observe();
    terminal(rig.model, LibraryOutcome::Applied);
    require_saved_fields(read(rig.session).controls, 0.125);
    expression_only = read(rig.session).controls;
    expression_only.expression = 0.5;
    (void)rig.control(expression_only);
    REQUIRE(!rig.model.view().current_reference->modified);
    (void)render(rig.session, 0);
    rig.observe();
    REQUIRE(rig.model.view().current_reference->modified); // Performance scope.
}

// The control Session receives independently constructed expected snapshots.
// The Engine receives only explicit physical transitions and expected controls,
// never Session's ownership adapter or the library's scope-merge helper. All 91
// phase advances and the nominal percussion recurrence are checked separately.
struct AudioPair {
    Session recalled, direct;
    LibraryModel model;
    Engine oracle;
    const RuntimeProfile& profile;
    ProcessSpec spec;
    std::array<double, kToneSourceCount> phases{}, increments{};
    std::array<std::array<bool, kManualKeyCount>, kManualCount> holds{};
    std::array<bool, kPedalCount> pedals{};
    std::uint64_t sequence{}, now{}, frames{};
    long double readiness{1.0L};

    AudioPair(const RuntimeProfile& input, double rate)
        : profile(input), spec{rate, 512, 0x19b319ULL, 9041} {
        REQUIRE(recalled.prepare(profile, spec) == SessionStatus::Ok);
        REQUIRE(direct.prepare(profile, spec) == SessionStatus::Ok);
        REQUIRE(oracle.prepare(profile, spec) == Status::Ok);
        model.audio_lifecycle_changed(LibraryAudioTransition::Prepare);
        REQUIRE(recalled.start() == SessionStatus::Ok);
        REQUIRE(direct.start() == SessionStatus::Ok);
        model.audio_lifecycle_changed(LibraryAudioTransition::Start);
        model.observe(fresh(recalled), ++now);
        for (std::size_t tone = 0; tone < phases.size(); ++tone) {
            REQUIRE(oracle.source_phase_turns(static_cast<ToneId>(tone + 1), phases[tone]));
            increments[tone] = profile.sources[tone].frequency_hz / rate;
        }
    }

    void post(const SessionCommand& actual, const SessionCommand& expected,
        const std::optional<LibraryControlIntent>& token = std::nullopt) {
        const auto left = recalled.post(actual);
        const auto right = direct.post(expected);
        REQUIRE(left.status == SessionStatus::Ok && right.status == SessionStatus::Ok);
        REQUIRE(left.sequence == sequence + 1 && right.sequence == left.sequence);
        REQUIRE(model.submitted(left, token) == LibraryOutcome::Accepted);
        sequence = left.sequence;
        counts.accepted_posts += 2;
    }

    void check_phases() {
        for (std::size_t tone = 0; tone < phases.size(); ++tone) {
            double actual = -1.0;
            REQUIRE(oracle.source_phase_turns(static_cast<ToneId>(tone + 1), actual));
            REQUIRE(std::bit_cast<std::uint64_t>(actual) ==
                std::bit_cast<std::uint64_t>(phases[tone]));
            ++counts.phase_checks;
        }
    }

    void restore_oracle(const ControlSnapshot& controls) {
        const auto before = oracle.percussion_diagnostics().readiness;
        REQUIRE(oracle.restore_controls(controls));
        REQUIRE(oracle.percussion_diagnostics().readiness == before);
        check_phases();
    }

    void initial(const ControlSnapshot& controls) {
        const auto token = model.note_control_intent(controls, fresh(recalled));
        REQUIRE(token.has_value());
        post(controls, controls, token);
        restore_oracle(controls);
    }

    void recall(const LibraryEntry& target, const ControlSnapshot& desired,
        const ControlSnapshot& expected) {
        REQUIRE(model.select(target.key));
        const auto before = read(recalled);
        const auto request = model.request_recall(target, desired, fresh(recalled), ++now);
        REQUIRE(request.outcome == LibraryOutcome::Accepted && request.recall);
        same_controls(request.recall->control_intent.expected_controls, expected);
        post(request.recall->control_intent.expected_controls, expected,
            request.recall->control_intent);
        same_snapshot(read(recalled), before);
        model.observe(fresh(recalled), ++now);
        REQUIRE(operation(model).phase == LibraryOperationPhase::AwaitingAcknowledgment);
        restore_oracle(expected);
    }

    void note(const SessionCommand& command) { post(command, command); }

    void physical(Manual manual, std::uint8_t pitch, bool down, double velocity = 100.0) {
        const std::array events{Event{0, down ? EventType::NoteOn : EventType::NoteOff,
            manual, pitch, down ? velocity : 0.0}};
        REQUIRE(oracle.process(0, {}, events));
        holds[static_cast<std::size_t>(manual)][static_cast<std::size_t>(pitch - kMinManualMidiNote)] = down;
        check_phases(); // No note transition can restart the shared field.
    }

    void physical_pedal(bool down, double velocity = 100.0) {
        const std::array events{Event{0, down ? EventType::PedalOn : EventType::PedalOff,
            Manual::Lower, 13, down ? velocity : 0.0}};
        REQUIRE(oracle.process(0, {}, events));
        pedals[12] = down;
        check_phases();
    }

    void block(std::uint32_t count, bool audible = true) {
        const auto controls = oracle.controls_snapshot();
        const bool physical_detector = std::any_of(holds[0].begin(), holds[0].end(),
            [](bool value) { return value; });
        const bool eligible = controls.percussion.enabled && controls.route_enabled[0] &&
            controls.selected_banks[0] == DrawbarBank::B &&
            controls.fixed_registrations[0] == FixedRegistration::None;
        const bool detector = eligible && physical_detector;
        const auto percussion = make_nominal_percussion_profile();
        const long double tau = detector ?
            (controls.percussion.decay == PercussionDecay::Slow ?
                percussion.slow_decay_seconds : percussion.fast_decay_seconds) :
            percussion.recovery_seconds;
        const auto actual = render(recalled, count);
        const auto expected = render(direct, count);
        std::vector<float> mono(count);
        REQUIRE(oracle.process(count, mono, {}));
        float peak = 0.0F;
        for (std::size_t frame = 0; frame < count; ++frame) {
            REQUIRE(std::isfinite(mono[frame]));
            peak = std::max(peak, std::abs(mono[frame]));
            for (std::size_t channel = 0; channel < 2; ++channel) {
                const auto index = frame * 2 + channel;
                REQUIRE(std::bit_cast<std::uint32_t>(actual[index]) ==
                    std::bit_cast<std::uint32_t>(expected[index]));
                REQUIRE(std::bit_cast<std::uint32_t>(actual[index]) ==
                    std::bit_cast<std::uint32_t>(mono[frame]));
                ++counts.paired_stereo_samples;
            }
            for (std::size_t tone = 0; tone < phases.size(); ++tone) {
                phases[tone] += increments[tone];
                if (phases[tone] >= 1.0) phases[tone] -= 1.0;
            }
        }
        if (count != 0) REQUIRE(audible ? peak > 1.0e-7F : peak == 0.0F);
        const auto factor = std::exp(-static_cast<long double>(count) /
            (static_cast<long double>(spec.sample_rate) * tau));
        readiness = detector ? readiness * factor : 1.0L - (1.0L - readiness) * factor;
        const auto percussion_state = oracle.percussion_diagnostics();
        REQUIRE(percussion_state.physical_detector == physical_detector);
        REQUIRE(percussion_state.eligible == eligible && percussion_state.routed_detector == detector);
        REQUIRE(std::abs(static_cast<long double>(percussion_state.readiness) - readiness) < 2.0e-11L);
        ++counts.readiness_checks;
        check_phases();
        frames += count;
        const auto after = read(recalled);
        same_snapshot(after, read(direct));
        same_controls(after.controls, controls);
        REQUIRE(after.frame_clock == spec.initial_frame + frames);
        REQUIRE(after.frame_clock == oracle.frame_clock());
        REQUIRE(after.held_keys == holds && after.held_pedals == pedals);
        REQUIRE(after.resolved_sequence == sequence && after.last_applied_sequence == sequence);
        REQUIRE(after.recovery_count == 0 && after.queue_overflows == 0);
        REQUIRE(after.rejected_commands == 0 && after.discarded_commands == 0);
        REQUIRE(after.fault_flags == 0 && after.last_core_status == Status::Ok);
        model.observe(fresh(recalled), ++now);
        REQUIRE(model.view().observation_fresh);
        REQUIRE(!model.view().controls_pending);
    }
};

void paired_recall_preserves_owners_audio_and_running_sources(const RuntimeProfile& profile) {
    for (const auto rate : {44100.0, 48000.0, 96000.0}) {
        AudioPair pair(profile, rate);
        const auto initial = sounding_controls();
        auto changed = saved_controls();
        changed.route_enabled = {true, true};
        changed.fixed_registrations = {FixedRegistration::None, FixedRegistration::None};
        changed.selected_banks = {DrawbarBank::B, DrawbarBank::A};
        const auto echo = entry("Echo", RegistrationScope::Registration, changed);
        auto muted = changed;
        muted.route_enabled = {false, false};
        muted.fixed_registrations = {FixedRegistration::DSharp, FixedRegistration::GSharp};
        muted.pedal_drawbars = {0, 0};
        const auto mute = entry("Mute", RegistrationScope::Performance, muted);
        auto restored = initial;
        restored.expression = 0.25;
        const auto restore = entry("Restore", RegistrationScope::Performance, restored);
        catalog(pair.model, {echo, mute, restore});
        pair.initial(initial);
        pair.block(0);
        pair.block(73, false); // All 91 sources advance before the first note.

        pair.note(manual_note(HostNoteKind::On, 0, 0, 60, 101, 100));
        pair.note(manual_note(HostNoteKind::On, 0, 4, 60, 102, 23));
        pair.note(manual_note(HostNoteKind::On, 1, 0, 55, 201, 100));
        pair.note(manual_note(HostNoteKind::On, 1, 6, 55, 202, 31));
        pair.note(pedal_note(PedalNoteKind::On, 0, 0, 13, 301, 100));
        pair.note(pedal_note(PedalNoteKind::On, 1, 7, 13, 302, 47));
        pair.physical(Manual::Upper, 60, true);
        pair.physical(Manual::Lower, 55, true);
        pair.physical_pedal(true);
        pair.block(0);
        pair.block(257);
        REQUIRE(pair.readiness < 1.0L);

        auto expected_registration = changed;
        expected_registration.expression = 0.625; // Literal latest desired value.
        pair.recall(echo, initial, expected_registration);
        pair.block(0);
        terminal(pair.model, LibraryOutcome::Applied);
        pair.block(89);
        pair.recall(echo, expected_registration, expected_registration); // Equal Recall.
        pair.block(0);
        terminal(pair.model, LibraryOutcome::Applied);
        pair.block(127);

        pair.recall(mute, expected_registration, muted);
        pair.block(0);
        pair.block(113, false); // Held owners stay alive while routes are silent.
        REQUIRE(held(read(pair.recalled), Manual::Upper, 60));
        REQUIRE(held(read(pair.recalled), Manual::Lower, 55));
        REQUIRE(read(pair.recalled).held_pedals[12]);
        pair.recall(restore, muted, restored);
        pair.block(0);
        pair.block(191);

        // Release the exact original UI owners. Independent owners still hold
        // all three physical targets; no synthesized/replaced owner can pass.
        pair.note(manual_note(HostNoteKind::Off, 0, 0, 60, 101));
        pair.note(manual_note(HostNoteKind::Off, 1, 0, 55, 201));
        pair.note(pedal_note(PedalNoteKind::Off, 0, 0, 13, 301));
        pair.block(0);
        pair.block(79);
        pair.note(manual_note(HostNoteKind::Off, 0, 4, 60, 102));
        pair.note(manual_note(HostNoteKind::Off, 1, 6, 55, 202));
        pair.note(pedal_note(PedalNoteKind::Off, 1, 7, 13, 302));
        pair.physical(Manual::Upper, 60, false);
        pair.physical(Manual::Lower, 55, false);
        pair.physical_pedal(false);
        pair.block(0);
        pair.block(37, false);
        no_holds(read(pair.recalled));

        pair.note(manual_note(HostNoteKind::On, 0, 0, 60, 101, 42));
        pair.note(manual_note(HostNoteKind::On, 1, 0, 55, 201, 42));
        pair.note(pedal_note(PedalNoteKind::On, 0, 0, 13, 301, 42));
        pair.physical(Manual::Upper, 60, true, 42.0);
        pair.physical(Manual::Lower, 55, true, 42.0);
        pair.physical_pedal(true, 42.0);
        pair.block(0);
        pair.block(47); // Reattack uses the advanced field, never initial phase.
        pair.note(manual_note(HostNoteKind::Off, 0, 0, 60, 101));
        pair.note(manual_note(HostNoteKind::Off, 1, 0, 55, 201));
        pair.note(pedal_note(PedalNoteKind::Off, 0, 0, 13, 301));
        pair.physical(Manual::Upper, 60, false);
        pair.physical(Manual::Lower, 55, false);
        pair.physical_pedal(false);
        pair.block(0);
        pair.block(29, false);
    }
}

void same_value_intention_supersedes_real_recall(const RuntimeProfile& profile) {
    Rig rig(profile);
    const auto target = entry("Same", RegistrationScope::Performance, saved_controls());
    catalog(rig.model, {target});
    const auto named = rig.recall(target, read(rig.session).controls);
    const auto first = rig.dispatch(named);
    const auto newer = rig.control(named.control_intent.expected_controls);
    REQUIRE(newer.desired_revision > named.control_intent.desired_revision);
    REQUIRE(rig.sequence > first);
    terminal(rig.model, LibraryOutcome::Superseded);
    REQUIRE(rig.model.view().controls_pending && !rig.model.view().current_reference);
    (void)render(rig.session, 0);
    rig.observe();
    terminal(rig.model, LibraryOutcome::Superseded);
    REQUIRE(!rig.model.view().current_reference && !rig.model.view().controls_pending);
    REQUIRE(read(rig.session).last_applied_sequence == rig.sequence);
    require_saved_fields(read(rig.session).controls, 0.125);
    REQUIRE(rig.model.set_name("New acknowledged intent"));
    REQUIRE(rig.model.request_save_new(fresh(rig.session), ++rig.now).outcome == LibraryOutcome::Accepted);
    REQUIRE(operation(rig.model).submitted_sequence == rig.sequence);
    REQUIRE(operation(rig.model).phase == LibraryOperationPhase::ReadyToSave);
}

void queue_overflow_recovers_without_false_receipt(const RuntimeProfile& profile) {
    Rig rig(profile);
    const auto controls = read(rig.session).controls;
    const auto target = entry("Equal overflow", RegistrationScope::Performance, controls);
    catalog(rig.model, {target});
    const auto before = read(rig.session);
    const auto named = rig.recall(target, controls);
    const auto recalled_sequence = rig.dispatch(named);
    const auto harmless = manual_note(HostNoteKind::Off, 0, 3, 60, 81);
    for (std::size_t index = 1; index < kSessionCommandCapacity; ++index) rig.post(harmless);
    const auto overflow = rig.session.post(harmless);
    REQUIRE(overflow.status == SessionStatus::QueueFull && overflow.sequence == 0);
    REQUIRE(rig.model.submitted(overflow) == LibraryOutcome::Rejected);
    terminal(rig.model, LibraryOutcome::Rejected);
    same_snapshot(read(rig.session), before); // Synchronous failure precedes publication.
    const auto recovery_pending = rig.session.post(harmless);
    REQUIRE(recovery_pending.status == SessionStatus::RecoveryPending && recovery_pending.sequence == 0);
    REQUIRE(rig.model.submitted(recovery_pending) == LibraryOutcome::Rejected);
    (void)render(rig.session, 0);
    const auto recovered = read(rig.session);
    REQUIRE(recovered.resolved_sequence == rig.sequence);
    REQUIRE(recovered.last_applied_sequence == 0);
    REQUIRE(recovered.discarded_commands == kSessionCommandCapacity);
    REQUIRE(recovered.queue_overflows == 1 && recovered.recovery_count == 1);
    same_controls(recovered.controls, controls);
    no_holds(recovered);
    rig.observe();
    const auto later = rig.post(manual_note(HostNoteKind::On, 1, 2, 55, 82, 100));
    REQUIRE(later > recalled_sequence);
    (void)render(rig.session, 19);
    rig.observe();
    REQUIRE(read(rig.session).last_applied_sequence == later);
    same_controls(read(rig.session).controls, named.control_intent.expected_controls);
    terminal(rig.model, LibraryOutcome::Rejected);
    REQUIRE(!rig.model.view().current_reference && !rig.model.view().controls_pending);
    rig.refuse_save_without_basis();
    const auto retry = rig.recall(target, read(rig.session).controls);
    REQUIRE(retry.operation_id > named.operation_id);
    rig.dispatch(retry);
    (void)render(rig.session, 0);
    rig.observe();
    terminal(rig.model, LibraryOutcome::Applied); // Explicit new receipt uses new guards.
}

void consumer_discard_cannot_be_recaptured_by_save(const RuntimeProfile& profile) {
    Rig rig(profile);
    const auto before = read(rig.session);
    const auto target = entry("Discarded", RegistrationScope::Performance, before.controls);
    catalog(rig.model, {target});
    // Offset zero passes producer shape admission; bus 2 fails at consumption.
    rig.post(manual_note(HostNoteKind::On, 2, 0, 60, 9, 100));
    const auto named = rig.recall(target, before.controls);
    const auto discarded_sequence = rig.dispatch(named);
    rig.post(manual_note(HostNoteKind::On, 1, 1, 55, 10, 100));
    same_snapshot(read(rig.session), before);
    (void)render(rig.session, 0);
    const auto rejected = read(rig.session);
    REQUIRE(rejected.rejected_commands == 1 && rejected.recovery_count == 1);
    REQUIRE(rejected.discarded_commands == 2 && rejected.last_applied_sequence == 0);
    REQUIRE(rejected.resolved_sequence == rig.sequence);
    no_holds(rejected);
    // Deliberately do not observe the rejection yet. A later unrelated command
    // gives both sequence fields coverage and exactly matching control values.
    const auto later = rig.post(manual_note(HostNoteKind::On, 0, 2, 60, 11, 100));
    REQUIRE(later > discarded_sequence);
    (void)render(rig.session, 23);
    const auto matching_later = read(rig.session);
    REQUIRE(matching_later.last_applied_sequence == later);
    REQUIRE(matching_later.resolved_sequence == later);
    same_controls(matching_later.controls, named.control_intent.expected_controls);
    rig.observe();
    terminal(rig.model, LibraryOutcome::Rejected);
    REQUIRE(!rig.model.view().current_reference && !rig.model.view().controls_pending);
    rig.refuse_save_without_basis(); // Current counters cannot replace original guards.
    (void)render(rig.session, 0);
    rig.observe();
    terminal(rig.model, LibraryOutcome::Rejected);
}

void waiting_save_keeps_original_consumer_failure_guards(const RuntimeProfile& profile) {
    Rig rig(profile);
    const auto equal_controls = read(rig.session).controls;
    rig.post(manual_note(HostNoteKind::On, 2, 0, 60, 19, 100));
    (void)rig.control(equal_controls);
    const auto original_sequence = rig.sequence;
    REQUIRE(rig.model.set_name("Waiting original control"));
    REQUIRE(rig.model.request_save_new(fresh(rig.session), ++rig.now).outcome == LibraryOutcome::Accepted);
    REQUIRE(operation(rig.model).phase == LibraryOperationPhase::AwaitingAcknowledgment);
    REQUIRE(operation(rig.model).submitted_sequence == original_sequence);
    REQUIRE(!rig.model.take_save_intent(fresh(rig.session), ++rig.now));
    (void)render(rig.session, 0);
    const auto rejected = read(rig.session);
    REQUIRE(rejected.rejected_commands == 1 && rejected.discarded_commands == 1);
    REQUIRE(rejected.recovery_count == 1 && rejected.last_applied_sequence == 0);
    const auto later = rig.post(manual_note(HostNoteKind::On, 0, 2, 60, 20, 100));
    (void)render(rig.session, 0);
    REQUIRE(later > original_sequence && read(rig.session).last_applied_sequence == later);
    same_controls(read(rig.session).controls, equal_controls);
    // request_save_new must first reject the old wait, then refuse a new Save;
    // taking current counters cannot rehabilitate the discarded basis.
    REQUIRE(rig.model.request_save_new(fresh(rig.session), ++rig.now).outcome ==
        LibraryOutcome::NoAcknowledgedControls);
    terminal(rig.model, LibraryOutcome::Rejected);
    REQUIRE(!rig.model.take_save_intent(fresh(rig.session), ++rig.now));
    REQUIRE(!rig.model.view().current_reference);
}

void failed_direct_post_cancels_before_publication(const RuntimeProfile& profile) {
    Rig rig(profile);
    const auto target = entry("Pending", RegistrationScope::Performance, saved_controls());
    catalog(rig.model, {target});
    const auto named = rig.recall(target, read(rig.session).controls);
    rig.dispatch(named);
    const auto before = read(rig.session);
    const SessionCommand invalid = PerformanceInputEvent{
        HostNoteEvent{1, HostNoteKind::On, 0, 2, 60, 100, 1}};
    const auto failed = rig.session.post(invalid);
    REQUIRE(failed.status == SessionStatus::InvalidCommand && failed.sequence == 0);
    REQUIRE(rig.model.submitted(failed) == LibraryOutcome::Rejected); // No control token.
    terminal(rig.model, LibraryOutcome::Rejected);
    same_snapshot(read(rig.session), before);
    REQUIRE(!rig.model.view().controls_pending);
    (void)render(rig.session, 0); // Recall really executes despite the later bad post.
    const auto after = read(rig.session);
    REQUIRE(after.last_applied_sequence == rig.sequence);
    REQUIRE(after.rejected_commands == before.rejected_commands + 1);
    REQUIRE(after.recovery_count == before.recovery_count);
    require_saved_fields(after.controls, 0.125);
    rig.observe();
    terminal(rig.model, LibraryOutcome::Rejected);
    REQUIRE(!rig.model.view().current_reference);
    rig.refuse_save_without_basis();
}

void missing_prepost_read_never_creates_acknowledgment(const RuntimeProfile& profile) {
    Rig rig(profile);
    const auto desired = saved_controls();
    const auto token = rig.model.note_control_intent(desired, {std::nullopt, true});
    REQUIRE(token.has_value());
    rig.post(desired, token);
    (void)render(rig.session, 0);
    require_saved_fields(read(rig.session).controls, 0.125);
    rig.observe();
    REQUIRE(!rig.model.view().controls_pending);
    rig.refuse_save_without_basis();
    rig.post(manual_note(HostNoteKind::On, 0, 2, 60, 31, 100));
    (void)render(rig.session, 0);
    rig.observe();
    rig.refuse_save_without_basis();
    rig.prove(desired); // A new explicit equal intent with a real pre-post read works.
    REQUIRE(rig.model.set_name("Freshly proved"));
    REQUIRE(rig.model.request_save_new(fresh(rig.session), ++rig.now).outcome == LibraryOutcome::Accepted);
    REQUIRE(operation(rig.model).phase == LibraryOperationPhase::ReadyToSave);
}

void lifecycle_and_no_audio_cannot_revive_receipts(const RuntimeProfile& profile) {
    Rig stopped(profile, false);
    const auto target = entry("Lifecycle", RegistrationScope::Performance, read(stopped.session).controls);
    catalog(stopped.model, {target});
    REQUIRE(stopped.model.select(target.key));
    const auto before = read(stopped.session);
    const auto refused = stopped.model.request_recall(target, before.controls, fresh(stopped.session, false), ++stopped.now);
    REQUIRE(refused.outcome == LibraryOutcome::NoAudio && !refused.recall);
    REQUIRE(!stopped.model.view().operation && !stopped.model.view().controls_pending);
    same_snapshot(read(stopped.session), before);
    REQUIRE(stopped.session.start() == SessionStatus::Ok);
    stopped.model.audio_lifecycle_changed(LibraryAudioTransition::Start);
    stopped.observe();
    const auto disabled = stopped.model.request_recall(target, before.controls,
        fresh(stopped.session, false), ++stopped.now);
    REQUIRE(disabled.outcome == LibraryOutcome::NoAudio && !disabled.recall);
    (void)render(stopped.session, 0);
    stopped.observe();
    REQUIRE(read(stopped.session).resolved_sequence == 0 && !stopped.model.view().current_reference);

    const auto pending = stopped.recall(target, before.controls);
    stopped.dispatch(pending);
    REQUIRE(stopped.session.stop() == SessionStatus::Ok);
    stopped.model.audio_lifecycle_changed(LibraryAudioTransition::Stop);
    REQUIRE(stopped.session.start() == SessionStatus::Ok);
    stopped.model.audio_lifecycle_changed(LibraryAudioTransition::Start);
    // No stopped snapshot was supplied to the model between these boundaries.
    stopped.post(manual_note(HostNoteKind::On, 0, 2, 60, 41, 100));
    (void)render(stopped.session, 0);
    stopped.observe();
    terminal(stopped.model, LibraryOutcome::Cancelled);
    REQUIRE(read(stopped.session).discarded_commands == 1);
    REQUIRE(!stopped.model.view().current_reference);
    stopped.refuse_save_without_basis();

    Rig prepared(profile);
    const auto defaults = read(prepared.session).controls;
    prepared.prove(defaults);
    const auto original_sequence = prepared.sequence;
    REQUIRE(prepared.session.stop() == SessionStatus::Ok);
    prepared.model.audio_lifecycle_changed(LibraryAudioTransition::Stop);
    // Same rate, later clock, same controls, retained sequence counters: only
    // the mandatory Prepare hook identifies this reset before the next read.
    REQUIRE(prepared.session.prepare(profile, {48000.0, 512, 0x19a19ULL, 8000}) == SessionStatus::Ok);
    prepared.model.audio_lifecycle_changed(LibraryAudioTransition::Prepare);
    REQUIRE(prepared.session.start() == SessionStatus::Ok);
    prepared.model.audio_lifecycle_changed(LibraryAudioTransition::Start);
    prepared.post(manual_note(HostNoteKind::On, 0, 2, 60, 42, 100));
    (void)render(prepared.session, 0);
    prepared.observe();
    REQUIRE(read(prepared.session).last_applied_sequence > original_sequence);
    same_controls(read(prepared.session).controls, defaults);
    prepared.refuse_save_without_basis();
}

void stopped_proved_save_emits_one_effect_without_audio(const RuntimeProfile& profile) {
    Rig rig(profile);
    const auto acknowledged = saved_controls();
    rig.prove(acknowledged);
    rig.post(manual_note(HostNoteKind::On, 0, 2, 60, 51, 100));
    (void)render(rig.session, 31);
    rig.observe();
    REQUIRE(rig.session.stop() == SessionStatus::Ok);
    rig.model.audio_lifecycle_changed(LibraryAudioTransition::Stop);
    rig.observe(false);
    const auto stopped = read(rig.session);
    REQUIRE(stopped.prepared && !stopped.running);
    no_holds(stopped);
    require_saved_fields(stopped.controls, 0.125);
    REQUIRE(rig.model.set_name("Stopped proof"));
    REQUIRE(rig.model.set_save_scope(RegistrationScope::Performance));
    const auto request = rig.model.request_save_new(fresh(rig.session, false), ++rig.now);
    REQUIRE(request.outcome == LibraryOutcome::Accepted && !request.recall);
    REQUIRE(operation(rig.model).phase == LibraryOperationPhase::ReadyToSave);
    const auto effect = rig.model.take_save_intent(fresh(rig.session, false), ++rig.now);
    REQUIRE(effect.has_value());
    REQUIRE(effect->key == "Stopped proof.b3performance" && effect->name == "Stopped proof");
    REQUIRE(effect->scope == RegistrationScope::Performance);
    require_saved_fields(effect->acknowledged_controls, 0.125);
    REQUIRE(operation(rig.model).phase == LibraryOperationPhase::Saving);
    REQUIRE(!rig.model.take_save_intent(fresh(rig.session, false), ++rig.now));
    const auto authorization = rig.model.authorize_save(effect->operation_id,
        fresh(rig.session, false), ++rig.now);
    REQUIRE(authorization.permitted);
    REQUIRE(!rig.model.authorize_save(effect->operation_id,
        fresh(rig.session, false), ++rig.now).permitted);
    REQUIRE(rig.model.request_save_new(fresh(rig.session, false), ++rig.now).outcome == LibraryOutcome::Busy);
    same_snapshot(read(rig.session), stopped);
    REQUIRE(!rig.model.view().current_reference);
    // No storage helper and no invented Saved result: the one copied effect
    // and permission are all this boundary test consumes.
}

void real_deadline_precedes_late_publication(const RuntimeProfile& profile) {
    for (const bool at_deadline : {false, true}) {
        Rig rig(profile);
        const auto target = entry("Deadline", RegistrationScope::Performance, saved_controls());
        catalog(rig.model, {target});
        const auto named = rig.recall(target, read(rig.session).controls);
        const auto started = rig.now;
        rig.dispatch(named);
        rig.model.observe({std::nullopt, true}, started + kLibraryAcknowledgmentWaitMs - 1);
        REQUIRE(!rig.model.view().observation_fresh);
        REQUIRE(operation(rig.model).phase == LibraryOperationPhase::AwaitingAcknowledgment);
        (void)render(rig.session, 0);
        rig.now = started + kLibraryAcknowledgmentWaitMs - (at_deadline ? 0U : 1U);
        rig.model.observe(fresh(rig.session), rig.now);
        terminal(rig.model, at_deadline ? LibraryOutcome::Unconfirmed : LibraryOutcome::Applied);
        require_saved_fields(read(rig.session).controls, 0.125);
        if (at_deadline) {
            REQUIRE(!rig.model.view().current_reference);
            rig.post(manual_note(HostNoteKind::On, 0, 2, 60, 61, 100));
            (void)render(rig.session, 0);
            rig.observe();
            terminal(rig.model, LibraryOutcome::Unconfirmed);
            REQUIRE(!rig.model.view().current_reference);
        }
    }
}

} // namespace

int main() {
    const auto profile = load_test_profile();
    using Test = std::pair<std::string_view, void (*)(const RuntimeProfile&)>;
    const std::array tests{
        Test{"equal Recall waits for real render", equal_recall_waits_for_real_render},
        Test{"literal scopes use pending desired expression", literal_scopes_use_pending_desired_expression},
        Test{"paired audio, owners and running sources", paired_recall_preserves_owners_audio_and_running_sources},
        Test{"same-value intention supersedes real Recall", same_value_intention_supersedes_real_recall},
        Test{"queue overflow cannot fabricate proof", queue_overflow_recovers_without_false_receipt},
        Test{"consumer discard cannot be recaptured by Save", consumer_discard_cannot_be_recaptured_by_save},
        Test{"waiting Save retains original failure guards", waiting_save_keeps_original_consumer_failure_guards},
        Test{"direct post failure precedes publication", failed_direct_post_cancels_before_publication},
        Test{"missing pre-post read cannot become proof", missing_prepost_read_never_creates_acknowledgment},
        Test{"lifecycle and unavailable audio", lifecycle_and_no_audio_cannot_revive_receipts},
        Test{"stopped proved Save emits one effect", stopped_proved_save_emits_one_effect_without_audio},
        Test{"real deadline precedes late publication", real_deadline_precedes_late_publication}
    };
    std::size_t failures = 0;
    for (const auto& [name, test] : tests) {
        current_case = name;
        try { test(profile); }
        catch (const std::exception& error) {
            ++failures;
            std::cerr << error.what() << '\n';
        }
    }
    std::cout << "Real Session LibraryModel boundary: " << tests.size() << " groups, "
        << counts.assertions << " assertions, " << counts.snapshots << " real snapshots, "
        << counts.renders << " renders, " << counts.accepted_posts << " accepted posts, "
        << counts.paired_stereo_samples << " bit-exact paired stereo samples, "
        << counts.phase_checks << " source-phase checks, " << counts.readiness_checks
        << " percussion-history checks, " << failures << " failed groups\n";
    return failures == 0 ? 0 : 1;
}
