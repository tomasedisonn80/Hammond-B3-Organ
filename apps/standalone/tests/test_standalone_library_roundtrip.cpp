#include "LibraryModel.h"
#include "TestSupport.h"
#include "UiModel.h"

#include <algorithm>
#include <array>
#include <bit>
#include <chrono>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <functional>
#include <iostream>
#include <iterator>
#include <optional>
#include <span>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <variant>
#include <vector>

// This is an SDK-free adapter harness, not main/browser wiring or native input
// qualification. Every non-null LibraryObservation comes from an actual fresh
// Session::read_snapshot, every post result reaches both models, and every disk
// result comes from the real RegistrationLibrary helper. Manual render boundaries
// and bounded disposable files require no SDL, device, thread, sleep or event pump.
namespace {
namespace fs = std::filesystem;
using namespace hammond;
using namespace hammond::standalone;

struct Counts {
    std::size_t checks{}, snapshots{}, renders{}, posts{}, library_reports{}, ui_reports{};
    std::size_t ordinary_intents{}, recall_dispatches{}, storage_calls{}, authorizer_calls{};
} counts;
std::string_view current_case;

void require(bool condition, std::string_view expression, int line) {
    ++counts.checks;
    if (!condition) {
        throw std::runtime_error(std::string(current_case) + ": line " +
            std::to_string(line) + ": " + std::string(expression));
    }
}
#define REQUIRE(expression) require(static_cast<bool>(expression), #expression, __LINE__)

// The fixture documents and field expectations are literal, independent of the
// production serializer, scope merge and scoped equality helpers. Only the
// expressly supplied decimal expression line differs between these documents.
std::string document(std::string_view expression) {
    return std::string{
        "B3CONTROLS4\n"
        "registration_catalog atlas-chapel-nominal-v1 sha256 "
        "c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf\n"
        "expression "} + std::string(expression) +
        "\npercussion enabled 1 harmonic third volume soft decay fast\n"
        "pedal drawbars 7 3\n"
        "manual upper selected A fixed_registration D# route_enabled 0\n"
        "bank A 8 0 3 1 6 2 7 4 5\n"
        "bank B 1 2 3 4 5 6 7 8 0\n"
        "manual lower selected B fixed_registration G# route_enabled 1\n"
        "bank A 2 4 6 8 0 1 3 5 7\n"
        "bank B 7 5 3 1 8 6 4 2 0\n"
        "end\n";
}

ControlSnapshot file_controls(double expression = 0.25) {
    ControlSnapshot value;
    value.drawbars[0][0] = {8, 0, 3, 1, 6, 2, 7, 4, 5};
    value.drawbars[0][1] = {1, 2, 3, 4, 5, 6, 7, 8, 0};
    value.drawbars[1][0] = {2, 4, 6, 8, 0, 1, 3, 5, 7};
    value.drawbars[1][1] = {7, 5, 3, 1, 8, 6, 4, 2, 0};
    value.selected_banks = {DrawbarBank::A, DrawbarBank::B};
    value.route_enabled = {false, true};
    value.fixed_registrations = {FixedRegistration::DSharp, FixedRegistration::GSharp};
    value.pedal_drawbars = {7, 3};
    value.percussion = {true, PercussionHarmonic::Third,
        PercussionVolume::Soft, PercussionDecay::Fast};
    value.expression = expression;
    return value;
}

ControlSnapshot legacy_controls() {
    ControlSnapshot value;
    value.drawbars[0][0] = {0, 2, 4, 6, 8, 1, 3, 5, 7};
    value.drawbars[0][1] = {8, 0, 8, 0, 4, 0, 2, 0, 1};
    value.drawbars[1][0] = {5, 0, 7, 0, 3, 0, 2, 0, 1};
    value.drawbars[1][1] = {6, 4, 2, 0, 7, 5, 3, 1, 8};
    value.selected_banks = {DrawbarBank::B, DrawbarBank::A};
    value.route_enabled = {true, true};
    value.fixed_registrations = {FixedRegistration::None, FixedRegistration::None};
    value.pedal_drawbars = {6, 4};
    value.percussion = {true, PercussionHarmonic::Second,
        PercussionVolume::Normal, PercussionDecay::Slow};
    value.expression = 0.625;
    return value;
}

void same_controls(const ControlSnapshot& actual, const ControlSnapshot& expected) {
    REQUIRE(actual == expected);
    REQUIRE(std::bit_cast<std::uint64_t>(actual.expression) ==
        std::bit_cast<std::uint64_t>(expected.expression));
}

class TemporaryTree {
public:
    TemporaryTree() {
        const auto stamp = std::chrono::steady_clock::now().time_since_epoch().count();
        for (unsigned attempt = 0; attempt < 64; ++attempt) {
            path_ = fs::temp_directory_path() / ("hammond-library-roundtrip-" +
                std::to_string(stamp) + "-" + std::to_string(attempt));
            std::error_code error;
            if (fs::create_directory(path_, error)) return;
            if (error && error != std::errc::file_exists) break;
        }
        throw std::runtime_error("Could not reserve roundtrip fixture directory");
    }
    ~TemporaryTree() {
        std::error_code ignored;
        (void)fs::remove_all(path_, ignored);
    }
    TemporaryTree(const TemporaryTree&) = delete;
    TemporaryTree& operator=(const TemporaryTree&) = delete;
    const fs::path& path() const noexcept { return path_; }
private:
    fs::path path_;
};

void write_fixture(const fs::path& path, std::string_view bytes) {
    REQUIRE(!fs::exists(path));
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    output.write(bytes.data(), static_cast<std::streamsize>(bytes.size()));
    output.close();
    REQUIRE(output);
}

std::string read_bytes(const fs::path& path) {
    std::ifstream input(path, std::ios::binary);
    REQUIRE(input);
    return {std::istreambuf_iterator<char>(input), std::istreambuf_iterator<char>()};
}

std::vector<fs::path> staging(const fs::path& root) {
    std::vector<fs::path> result;
    if (!fs::exists(root)) return result;
    const auto prefix = fs::path(".b3-library-save-").native();
    for (const auto& entry : fs::directory_iterator(root)) {
        if (entry.path().filename().native().starts_with(prefix)) result.push_back(entry.path());
    }
    return result;
}

LibraryOperationView operation(const LibraryModel& model) {
    const auto view = model.view();
    REQUIRE(view.operation.has_value());
    return *view.operation;
}

LibraryCurrentReferenceView reference(const LibraryModel& model) {
    const auto view = model.view();
    REQUIRE(view.current_reference.has_value());
    return *view.current_reference;
}

void terminal(const LibraryModel& model, LibraryOutcome expected) {
    REQUIRE(operation(model).phase == LibraryOperationPhase::Finished);
    REQUIRE(operation(model).outcome == expected);
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

const SessionCommand& one_command(const UiActions& actions) {
    REQUIRE(actions.count == 1);
    REQUIRE(std::holds_alternative<SessionCommand>(actions.items[0]));
    return std::get<SessionCommand>(actions.items[0]);
}

SessionCommand external_note(bool down) {
    return PerformanceInputEvent{HostNoteEvent{0, down ? HostNoteKind::On : HostNoteKind::Off,
        0, 2, 60, static_cast<std::uint8_t>(down ? 73 : 0), 900}};
}

void require_note(const UiActions& actions, bool down, std::uint8_t bus,
    std::uint8_t pitch, std::int32_t owner) {
    const auto& command = one_command(actions);
    REQUIRE(std::holds_alternative<PerformanceInputEvent>(command));
    const auto& event = std::get<PerformanceInputEvent>(command);
    REQUIRE(std::holds_alternative<HostNoteEvent>(event));
    const auto& note = std::get<HostNoteEvent>(event);
    REQUIRE(note.offset == 0 && note.kind == (down ? HostNoteKind::On : HostNoteKind::Off));
    REQUIRE(note.bus == bus && note.channel == kUiInputChannel);
    REQUIRE(note.midi_note == pitch && note.note_id == owner);
    REQUIRE(note.velocity == (down ? kUiNoteVelocity : 0));
}

UiPoint lower_key_point(const UiModel& ui) {
    const auto& quad = ui.layout().manual_keys[1][19].hit.points;
    constexpr float depth = 0.9F; // Lower G3 is natural; below accidental overlap.
    const float left = quad[0].x + (quad[3].x - quad[0].x) * depth;
    const float right = quad[1].x + (quad[2].x - quad[1].x) * depth;
    return {(left + right) * 0.5F, quad[0].y + (quad[3].y - quad[0].y) * depth};
}

struct PostedControls {
    std::uint64_t sequence{};
    LibraryControlIntent intent;
};

struct StorageExecution {
    LibrarySaveResult result;
    std::optional<LibraryCommitAuthorization> authorization;
    std::optional<SessionSnapshot> final_snapshot;
    std::size_t authorizer_calls{}, reads_before{}, reads_after{};
    std::string staged_bytes;
};

class Rig {
public:
    explicit Rig(const RuntimeProfile& profile, bool start_now = true) {
        std::string error;
        REQUIRE(resolve_registration_library_root(tree.path() / "entries", root, error));
        REQUIRE(error.empty() && root.is_absolute() && !fs::exists(root));
        REQUIRE(session.prepare(profile, {48000.0, 128, 0xa28ULL, 613}) == SessionStatus::Ok);
        model.audio_lifecycle_changed(LibraryAudioTransition::Prepare);
        observe();
        if (start_now) start();
        (void)refresh();
    }

    std::uint64_t tick() { return ++now; }

    SessionSnapshot read() {
        SessionSnapshot snapshot;
        REQUIRE(session.read_snapshot(snapshot));
        ++counts.snapshots;
        REQUIRE(snapshot.prepared && snapshot.publication_revision != 0);
        REQUIRE((snapshot.publication_revision & 1U) == 0);
        return snapshot;
    }

    LibraryObservation fresh() {
        auto snapshot = read();
        ui.observe(snapshot);
        return {std::move(snapshot), commands_enabled};
    }

    void observe() {
        model.observe(fresh(), tick());
        REQUIRE(model.view().observation_fresh);
    }

    void start() {
        REQUIRE(session.start() == SessionStatus::Ok);
        model.audio_lifecycle_changed(LibraryAudioTransition::Start);
        commands_enabled = true;
        observe();
    }

    LibraryCatalog refresh() {
        const auto intent = model.request_refresh();
        REQUIRE(intent.has_value());
        const auto catalog = scan_registration_library(root, intent->generation);
        REQUIRE(catalog.complete());
        REQUIRE(model.replace_catalog(catalog));
        REQUIRE(!model.view().catalog_stale);
        return catalog;
    }

    std::uint64_t post(const SessionCommand& command,
        const std::optional<LibraryControlIntent>& token = std::nullopt) {
        REQUIRE(std::holds_alternative<ControlSnapshot>(command) == token.has_value());
        const auto result = session.post(command);
        ++counts.posts;
        // Report the actual result before making success assertions; no post
        // bypasses either receipt path, including the external-owner events.
        const auto reported = model.submitted(result, token);
        ++counts.library_reports;
        const auto recovery = ui.submitted(command, result);
        ++counts.ui_reports;
        REQUIRE(result.status == SessionStatus::Ok && result.sequence == sequence + 1);
        REQUIRE(reported == LibraryOutcome::Accepted && recovery.count == 0);
        sequence = result.sequence;
        return sequence;
    }

    PostedControls control(const UiActions& actions, const ControlSnapshot& expected,
        std::optional<LibraryControlIntent> named_token = std::nullopt) {
        const auto& command = one_command(actions);
        REQUIRE(std::holds_alternative<ControlSnapshot>(command));
        same_controls(std::get<ControlSnapshot>(command), expected);
        same_controls(ui.view().controls, expected);
        REQUIRE(ui.view().controls_pending);
        if (!named_token) {
            named_token = model.note_control_intent(expected, fresh());
            ++counts.ordinary_intents;
        }
        REQUIRE(named_token.has_value());
        same_controls(named_token->expected_controls, expected);
        return {post(command, named_token), *named_token};
    }

    void render(std::uint32_t frames = 0) {
        REQUIRE(frames <= 128);
        const auto before = read();
        constexpr float sentinel = -2817.25F;
        std::array<float, 258> buffer;
        buffer.fill(sentinel);
        auto output = std::span<float>{buffer}.subspan(1, static_cast<std::size_t>(frames) * 2);
        const auto result = session.render(frames, output);
        ++counts.renders;
        REQUIRE(result.status == SessionStatus::Ok && result.frames_rendered == frames);
        REQUIRE(buffer.front() == sentinel && buffer.back() == sentinel);
        REQUIRE(std::all_of(output.begin(), output.end(), [](float sample) { return std::isfinite(sample); }));
        const auto after = read();
        REQUIRE(after.frame_clock == before.frame_clock + frames);
        REQUIRE(after.publication_revision == before.publication_revision + 2);
        REQUIRE(after.resolved_sequence == sequence && after.last_applied_sequence == sequence);
        REQUIRE(after.recovery_count == 0 && after.rejected_commands == 0);
        REQUIRE(after.discarded_commands == 0 && after.queue_overflows == 0 && after.fault_flags == 0);
        observe(); // Another real read, never a synthetic or cached proof copy.
    }

    PostedControls load(const ControlSnapshot& controls) {
        const auto posted = control(ui.load_controls(controls), controls);
        observe();
        REQUIRE(ui.view().controls_pending && model.view().controls_pending);
        render();
        same_controls(read().controls, controls);
        REQUIRE(!ui.view().controls_pending && !model.view().controls_pending);
        REQUIRE(!ui.view().controls_dirty);
        return posted;
    }

    PostedControls expression(double value) {
        std::uint32_t parameter = 0;
        REQUIRE(ui_parameter_id({UiControlKind::Expression}, parameter));
        auto expected = ui.view().controls;
        expected.expression = value;
        return control(ui.external_parameter(parameter, value), expected);
    }

    PostedControls recall(std::string_view key, const ControlSnapshot& expected) {
        REQUIRE(model.select(key));
        const auto target = read_registration_entry(root, key);
        REQUIRE(target.valid());
        const auto desired = ui.view().controls;
        const auto requested = model.request_recall(target, desired, fresh(), tick());
        REQUIRE(requested.outcome == LibraryOutcome::Accepted && requested.recall);
        REQUIRE(operation(model).phase == LibraryOperationPhase::AwaitingSubmission);
        REQUIRE(operation(model).submitted_sequence == 0);
        same_controls(requested.recall->control_intent.expected_controls, expected);
        const auto intents_before = counts.ordinary_intents;
        const auto posts_before = counts.posts;
        const auto posted = control(ui.recall_controls(requested.recall->control_intent.expected_controls),
            expected, requested.recall->control_intent);
        ++counts.recall_dispatches;
        REQUIRE(counts.posts == posts_before + 1 && counts.ordinary_intents == intents_before);
        REQUIRE(operation(model).phase == LibraryOperationPhase::AwaitingAcknowledgment);
        REQUIRE(operation(model).submitted_sequence == posted.sequence);
        observe();
        REQUIRE(operation(model).phase == LibraryOperationPhase::AwaitingAcknowledgment);
        REQUIRE(ui.view().controls_pending && model.view().controls_pending);
        return posted;
    }

    LibrarySaveIntent begin_save(std::string_view name, RegistrationScope scope) {
        REQUIRE(model.set_name(name) && model.set_save_scope(scope));
        const auto requested = model.request_save_new(fresh(), tick());
        REQUIRE(requested.outcome == LibraryOutcome::Accepted && !requested.recall);
        REQUIRE(operation(model).phase == LibraryOperationPhase::ReadyToSave);
        const auto effect = model.take_save_intent(fresh(), tick());
        REQUIRE(effect.has_value() && effect->operation_id != 0);
        REQUIRE(operation(model).phase == LibraryOperationPhase::Saving);
        same_controls(effect->acknowledged_controls, ui.view().controls);
        REQUIRE(!ui.view().controls_pending && !model.view().controls_pending);
        return *effect;
    }

    StorageExecution execute(const LibrarySaveIntent& effect,
        const std::function<void()>& external_creation_before_read = {}) {
        StorageExecution execution;
        const auto posts_before = counts.posts;
        ++counts.storage_calls;
        execution.result = save_registration_entry_new(root, effect.name, effect.scope,
            effect.acknowledged_controls, {}, [&]() {
                ++execution.authorizer_calls;
                ++counts.authorizer_calls;
                const auto owned = staging(root);
                REQUIRE(owned.size() == 1);
                execution.staged_bytes = read_bytes(owned.front() / "controls.tmp");
                // Only the collision journey uses this seam: an external file
                // appears after final storage admission, BEFORE authorization.
                // No event pumping or control intent occurs inside this callback.
                if (external_creation_before_read) external_creation_before_read();
                execution.reads_before = counts.snapshots;
                const auto observation = fresh();
                execution.reads_after = counts.snapshots;
                execution.final_snapshot = observation.snapshot;
                execution.authorization = model.authorize_save(effect.operation_id, observation, tick());
                return *execution.authorization;
            });
        // No action is interposed after true permission and before this result.
        REQUIRE(counts.posts == posts_before);
        REQUIRE(execution.authorizer_calls == 1 && execution.authorization && execution.final_snapshot);
        REQUIRE(execution.reads_after == execution.reads_before + 1);
        REQUIRE(staging(root).empty());
        return execution;
    }

    void stored(const LibrarySaveIntent& effect, const ControlSnapshot& expected) {
        const auto catalog = refresh();
        const auto found = std::find_if(catalog.entries.begin(), catalog.entries.end(),
            [&effect](const LibraryEntry& entry) { return entry.key == effect.key; });
        REQUIRE(found != catalog.entries.end() && found->valid());
        REQUIRE(found->name == effect.name && found->scope == effect.scope);
        same_controls(*found->controls, expected);
        const auto reread = read_registration_entry(root, effect.key);
        REQUIRE(reread.valid() && reread.key == effect.key && reread.name == effect.name);
        REQUIRE(reread.scope == effect.scope);
        same_controls(*reread.controls, expected);
    }

    LibrarySaveIntent save(std::string_view name, RegistrationScope scope,
        const ControlSnapshot& expected) {
        const auto posts_before = counts.posts;
        const bool dirty_before = ui.view().controls_dirty;
        const auto effect = begin_save(name, scope);
        same_controls(effect.acknowledged_controls, expected);
        const auto execution = execute(effect);
        REQUIRE(execution.authorization->permitted);
        REQUIRE(execution.result.status == LibrarySaveStatus::Saved && execution.result.committed());
        REQUIRE(execution.result.committed_entry && execution.result.committed_entry->valid());
        REQUIRE(execution.result.committed_entry->key == effect.key);
        REQUIRE(execution.result.committed_entry->name == effect.name);
        REQUIRE(execution.result.committed_entry->scope == effect.scope);
        same_controls(*execution.result.committed_entry->controls, expected);
        REQUIRE(model.complete_save(effect.operation_id, execution.result) == LibraryOutcome::Saved);
        terminal(model, LibraryOutcome::Saved);
        REQUIRE(reference(model).key == effect.key);
        REQUIRE(reference(model).origin == LibraryReferenceOrigin::AcknowledgedSave);
        REQUIRE(!reference(model).modified && !reference(model).missing);
        REQUIRE(ui.view().controls_dirty == dirty_before && counts.posts == posts_before);
        stored(effect, expected);
        return effect;
    }

    TemporaryTree tree;
    fs::path root;
    Session session;
    UiModel ui;
    LibraryModel model;
    bool commands_enabled{false};
    std::uint64_t now{}, sequence{};
};

void startup_requires_a_new_post_start_receipt(const RuntimeProfile& profile) {
    Rig rig(profile, false);
    const auto expected = file_controls();
    // Model the source-review caveat explicitly: a prepared stopped Session
    // accepts startup restore, while ordinary native command dispatch is off.
    const auto queued = rig.control(rig.ui.load_controls(expected), expected);
    REQUIRE(!rig.read().running && rig.read().last_applied_sequence == 0);
    REQUIRE(rig.model.view().controls_pending);
    rig.start(); // The mandatory hook invalidates that still-unproved basis.
    rig.render(17); // The real queued restore nevertheless applies successfully.
    same_controls(rig.read().controls, expected);
    REQUIRE(rig.read().last_applied_sequence == queued.sequence);
    REQUIRE(!rig.ui.view().controls_pending && !rig.model.view().controls_pending);
    REQUIRE(rig.model.set_name("Unproved startup"));
    REQUIRE(rig.model.request_save_new(rig.fresh(), rig.tick()).outcome ==
        LibraryOutcome::NoAcknowledgedControls);
    REQUIRE(!rig.model.take_save_intent(rig.fresh(), rig.tick()));
    REQUIRE(!fs::exists(rig.root) && !rig.model.view().current_reference);

    // Selecting the already cancelled upper preset is a real same-value UI
    // intention, with its own post-Start observation, revision and sequence.
    const auto newer = rig.control(rig.ui.activate(
        {UiControlKind::PresetKey, Manual::Upper, DrawbarBank::A, 0}), expected);
    REQUIRE(newer.sequence > queued.sequence);
    REQUIRE(newer.intent.desired_revision > queued.intent.desired_revision);
    REQUIRE(rig.model.set_name("Started proof"));
    REQUIRE(rig.model.set_save_scope(RegistrationScope::Performance));
    REQUIRE(rig.model.request_save_new(rig.fresh(), rig.tick()).outcome == LibraryOutcome::Accepted);
    REQUIRE(operation(rig.model).phase == LibraryOperationPhase::AwaitingAcknowledgment);
    REQUIRE(!rig.model.take_save_intent(rig.fresh(), rig.tick()));
    REQUIRE(!fs::exists(rig.root));
    rig.render();
    REQUIRE(operation(rig.model).phase == LibraryOperationPhase::ReadyToSave);
    const auto effect = rig.model.take_save_intent(rig.fresh(), rig.tick());
    REQUIRE(effect.has_value());
    const auto execution = rig.execute(*effect);
    REQUIRE(execution.authorization->permitted && execution.result.status == LibrarySaveStatus::Saved);
    REQUIRE(execution.final_snapshot->last_applied_sequence == newer.sequence);
    REQUIRE(rig.model.complete_save(effect->operation_id, execution.result) == LibraryOutcome::Saved);
    terminal(rig.model, LibraryOutcome::Saved);
    rig.stored(*effect, expected);
    REQUIRE(read_bytes(rig.root / effect->key) == document("0.25"));
    REQUIRE(!rig.ui.view().controls_dirty); // Only the actual legacy Load set this baseline.
}

void scope_recalls_roundtrip_while_original_owners_remain(const RuntimeProfile& profile) {
    Rig rig(profile);
    REQUIRE(fs::create_directory(rig.root));
    write_fixture(rig.root / "Original registration.b3registration", document("0.25"));
    write_fixture(rig.root / "Original performance.b3performance", document("0.25"));
    REQUIRE(rig.refresh().entries.size() == 2);
    const auto legacy = legacy_controls();
    (void)rig.load(legacy);
    const auto legacy_file = rig.save("Legacy clean", RegistrationScope::Performance, legacy);
    REQUIRE(!rig.ui.view().controls_dirty);

    const auto keyboard_on = rig.ui.key({UiKey::A, true});
    require_note(keyboard_on, true, 0, 60, kUiKeyboardOwnerBase);
    rig.post(one_command(keyboard_on));
    const auto pointer_on = rig.ui.pointer({UiPointerKind::Down, lower_key_point(rig.ui)});
    require_note(pointer_on, true, 1, 55, kUiPointerOwnerId);
    rig.post(one_command(pointer_on));
    rig.post(external_note(true)); // An independent owner overlaps upper C4.
    rig.render(29);
    const auto held_before = rig.read();
    REQUIRE(held(held_before, Manual::Upper, 60) && held(held_before, Manual::Lower, 55));
    REQUIRE(rig.ui.key({UiKey::F2, true}).count == 0);
    REQUIRE(rig.ui.key({UiKey::F2, false}).count == 0);
    REQUIRE(rig.ui.key({UiKey::RightBracket, true}).count == 0);
    REQUIRE(rig.ui.key({UiKey::RightBracket, false}).count == 0);
    REQUIRE(rig.ui.view().keyboard_target == UiTarget::Lower && rig.ui.view().manual_base_midi == 72);

    const auto expression_post = rig.expression(0.875); // Still pending at Recall activation.
    REQUIRE(rig.read().controls.expression == 0.625);
    const auto registration = file_controls(0.875);
    const auto registration_post = rig.recall("Original registration.b3registration", registration);
    REQUIRE(registration_post.sequence == expression_post.sequence + 1);
    REQUIRE(reference(rig.model).key == legacy_file.key);
    rig.render();
    terminal(rig.model, LibraryOutcome::Applied);
    same_controls(rig.read().controls, registration);
    REQUIRE(rig.read().frame_clock == held_before.frame_clock);
    REQUIRE(rig.read().held_keys == held_before.held_keys && rig.read().held_pedals == held_before.held_pedals);
    REQUIRE(rig.ui.view().pointer_captured && rig.ui.view().controls_dirty);
    REQUIRE(reference(rig.model).origin == LibraryReferenceOrigin::Recall);
    const auto saved_registration = rig.save("Stored registration", RegistrationScope::Registration, registration);
    REQUIRE(read_bytes(rig.root / saved_registration.key) == document("0.875"));
    REQUIRE(rig.ui.view().controls_dirty);
    rig.render(64);

    (void)rig.expression(0.5);
    rig.render();
    REQUIRE(!reference(rig.model).modified); // Registration ignores only expression.
    (void)rig.expression(0.75); // Again pending when Performance Recall starts.
    REQUIRE(rig.read().controls.expression == 0.5);
    const auto performance = file_controls();
    (void)rig.recall("Original performance.b3performance", performance);
    rig.render();
    terminal(rig.model, LibraryOutcome::Applied);
    same_controls(rig.read().controls, performance);
    REQUIRE(rig.read().held_keys == held_before.held_keys && rig.read().held_pedals == held_before.held_pedals);
    const auto saved_performance = rig.save("Stored performance", RegistrationScope::Performance, performance);
    REQUIRE(read_bytes(rig.root / saved_performance.key) == document("0.25"));
    REQUIRE(rig.ui.view().controls_dirty);
    (void)rig.expression(0.5);
    rig.render();
    REQUIRE(reference(rig.model).modified); // Performance includes expression.

    // Return to the genuine legacy Load baseline through the named path. Named
    // Recall and both successful Save new operations must not have moved it.
    (void)rig.recall(legacy_file.key, legacy);
    rig.render();
    terminal(rig.model, LibraryOutcome::Applied);
    REQUIRE(!rig.ui.view().controls_dirty);
    (void)rig.recall(saved_performance.key, performance);
    rig.render();
    terminal(rig.model, LibraryOutcome::Applied);
    REQUIRE(rig.ui.view().controls_dirty && rig.ui.view().pointer_captured);
    REQUIRE(read_bytes(rig.root / "Original registration.b3registration") == document("0.25"));
    REQUIRE(read_bytes(rig.root / "Original performance.b3performance") == document("0.25"));
    REQUIRE(rig.refresh().entries.size() == 5);

    // Original releases retain their captured bus/pitch/owner despite the new
    // keyboard target/octave, changed controls and cancelled upper route.
    const auto keyboard_off = rig.ui.key({UiKey::A, false});
    require_note(keyboard_off, false, 0, 60, kUiKeyboardOwnerBase);
    rig.post(one_command(keyboard_off));
    const auto pointer_off = rig.ui.pointer({UiPointerKind::Up, {-50.0F, -50.0F}});
    require_note(pointer_off, false, 1, 55, kUiPointerOwnerId);
    rig.post(one_command(pointer_off));
    rig.render();
    REQUIRE(held(rig.read(), Manual::Upper, 60)); // External owner was not released by UI Up.
    REQUIRE(!held(rig.read(), Manual::Lower, 55) && !rig.ui.view().pointer_captured);
    rig.post(external_note(false));
    rig.render();
    no_holds(rig.read());
}

void equal_newer_intent_refuses_old_save_even_after_real_proof(const RuntimeProfile& profile) {
    Rig rig(profile);
    (void)rig.load(file_controls());
    const auto original = rig.expression(0.625);
    rig.render();
    const auto expected = file_controls(0.625);
    const auto held_on = rig.ui.key({UiKey::A, true});
    require_note(held_on, true, 0, 60, kUiKeyboardOwnerBase);
    rig.post(one_command(held_on));
    rig.render();
    const auto effect = rig.begin_save("Superseded snapshot", RegistrationScope::Performance);

    // Repeated Cancel is equal in every control value but is a new real UI
    // intention. It arrives after the effect was issued and before storage.
    const auto newer = rig.control(rig.ui.activate(
        {UiControlKind::PresetKey, Manual::Upper, DrawbarBank::A, 0}), expected);
    REQUIRE(newer.sequence > original.sequence);
    REQUIRE(newer.intent.desired_revision > original.intent.desired_revision);
    terminal(rig.model, LibraryOutcome::Superseded);
    rig.render(); // Even fresh proof of the equal NEW intent cannot repair the old receipt.
    same_controls(rig.read().controls, effect.acknowledged_controls);
    terminal(rig.model, LibraryOutcome::Superseded);
    const auto execution = rig.execute(effect);
    REQUIRE(!execution.authorization->permitted);
    REQUIRE(execution.result.status == LibrarySaveStatus::NotAuthorized && !execution.result.committed());
    REQUIRE(!execution.result.committed_entry && !execution.result.refreshed_catalog);
    REQUIRE(execution.staged_bytes == document("0.625"));
    REQUIRE(execution.final_snapshot->last_applied_sequence == newer.sequence);
    REQUIRE(rig.model.complete_save(effect.operation_id, execution.result) == LibraryOutcome::Superseded);
    terminal(rig.model, LibraryOutcome::Superseded);
    REQUIRE(!fs::exists(rig.root / effect.key));
    REQUIRE(rig.refresh().entries.empty());
    REQUIRE(!rig.model.view().current_reference && rig.model.view().name_draft == effect.name);
    REQUIRE(rig.ui.view().controls_dirty && held(rig.read(), Manual::Upper, 60));

    // A new explicit operation may use the newer proved basis; the cancelled
    // operation is never revived and there is no automatic retry or overwrite.
    const auto saved = rig.save("New same value", RegistrationScope::Performance, expected);
    REQUIRE(saved.operation_id > effect.operation_id);
    REQUIRE(read_bytes(rig.root / saved.key) == document("0.625"));
    REQUIRE(!fs::exists(rig.root / effect.key) && rig.ui.view().controls_dirty);
    const auto held_off = rig.ui.key({UiKey::A, false});
    require_note(held_off, false, 0, 60, kUiKeyboardOwnerBase);
    rig.post(one_command(held_off));
    rig.render();
    no_holds(rig.read());
}

void external_late_creator_wins_without_replacement(const RuntimeProfile& profile) {
    Rig rig(profile);
    (void)rig.load(file_controls());
    (void)rig.expression(0.875);
    rig.render();
    const auto effect = rig.begin_save("External winner", RegistrationScope::Registration);
    REQUIRE(!fs::exists(rig.root));
    const auto execution = rig.execute(effect, [&]() {
        // Deterministic stand-in for an external creator, after the helper's
        // final name/capacity scan. No Session/UI action occurs at this seam.
        write_fixture(rig.root / effect.key, document("0.25"));
    });
    REQUIRE(execution.authorization->permitted); // Real control proof was valid.
    REQUIRE(execution.staged_bytes == document("0.875"));
    same_controls(execution.final_snapshot->controls, file_controls(0.875));
    REQUIRE(execution.result.status == LibrarySaveStatus::NameExists && !execution.result.committed());
    REQUIRE(!execution.result.committed_entry);
    REQUIRE(rig.model.complete_save(effect.operation_id, execution.result) == LibraryOutcome::SaveFailed);
    terminal(rig.model, LibraryOutcome::SaveFailed);
    REQUIRE(!rig.model.view().current_reference && rig.model.view().name_draft == effect.name);
    REQUIRE(rig.ui.view().controls_dirty);
    REQUIRE(read_bytes(rig.root / effect.key) == document("0.25"));
    const auto catalog = rig.refresh();
    REQUIRE(catalog.entries.size() == 1 && catalog.directory_items == 1);
    REQUIRE(catalog.entries[0].key == effect.key && catalog.entries[0].valid());
    same_controls(*catalog.entries[0].controls, file_controls());
    const auto winner = read_registration_entry(rig.root, effect.key);
    REQUIRE(winner.valid() && winner.scope == RegistrationScope::Registration);
    same_controls(*winner.controls, file_controls());
    terminal(rig.model, LibraryOutcome::SaveFailed);
    REQUIRE(staging(rig.root).empty());
}

} // namespace

int main() {
    const auto profile = load_test_profile();
    using Test = std::pair<std::string_view, void (*)(const RuntimeProfile&)>;
    const std::array tests{
        Test{"startup needs post-Start receipt", startup_requires_a_new_post_start_receipt},
        Test{"held scope recall and real storage roundtrip", scope_recalls_roundtrip_while_original_owners_remain},
        Test{"equal newer intent refuses issued Save", equal_newer_intent_refuses_old_save_even_after_real_proof},
        Test{"late external create-only collision", external_late_creator_wins_without_replacement}};
    std::size_t failures = 0;
    for (const auto& [name, test] : tests) {
        current_case = name;
        try { test(profile); }
        catch (const std::exception& error) {
            ++failures;
            std::cerr << error.what() << '\n';
        }
    }
    if (counts.posts != counts.library_reports || counts.posts != counts.ui_reports) ++failures;
    std::cout << "library_roundtrip groups=" << tests.size() << " checks=" << counts.checks
        << " snapshots=" << counts.snapshots << " renders=" << counts.renders
        << " posts=" << counts.posts << " library_reports=" << counts.library_reports
        << " ui_reports=" << counts.ui_reports << " ordinary_intents=" << counts.ordinary_intents
        << " recall_dispatches=" << counts.recall_dispatches << " storage_calls=" << counts.storage_calls
        << " authorizer_calls=" << counts.authorizer_calls << " failures=" << failures
        << " Session=real storage=real native_browser=unqualified\n";
    return failures == 0 ? 0 : 1;
}
