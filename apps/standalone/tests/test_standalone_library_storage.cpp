#include "LibraryModel.h"

#include <algorithm>
#include <array>
#include <chrono>
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
#include <vector>

// Real RegistrationLibrary filesystem effects connected to LibraryModel's
// mandatory final authorization. The control publication below is explicitly
// synthetic: this suite does not claim Session/runtime or native-browser proof.
// test_standalone_library_session owns the separate real Session boundary.
namespace {
namespace fs = std::filesystem;
using namespace hammond;
using namespace hammond::standalone;

std::size_t checks = 0;
std::string_view current_case;

void check(bool condition, std::string_view expression, int line) {
    ++checks;
    if (!condition) {
        throw std::runtime_error(std::string(current_case) + ": line " +
            std::to_string(line) + ": " + std::string(expression));
    }
}
#define REQUIRE(expression) check(static_cast<bool>(expression), #expression, __LINE__)

// Independent literal bytes and complete field expectations, borrowed from
// the existing storage contract fixtures. The serializer does not construct
// the input document or the canonical-output oracle.
constexpr std::string_view kCanonicalDocument =
    "B3CONTROLS4\n"
    "registration_catalog atlas-chapel-nominal-v1 sha256 "
    "c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf\n"
    "expression 0.25\n"
    "percussion enabled 1 harmonic third volume soft decay fast\n"
    "pedal drawbars 7 3\n"
    "manual upper selected A fixed_registration D# route_enabled 0\n"
    "bank A 8 0 3 1 6 2 7 4 5\n"
    "bank B 1 2 3 4 5 6 7 8 0\n"
    "manual lower selected B fixed_registration G# route_enabled 1\n"
    "bank A 2 4 6 8 0 1 3 5 7\n"
    "bank B 7 5 3 1 8 6 4 2 0\n"
    "end\n";

ControlSnapshot expected_controls() {
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
    value.expression = 0.25;
    return value;
}

class TemporaryTree {
public:
    TemporaryTree() {
        const auto stamp = std::chrono::steady_clock::now().time_since_epoch().count();
        for (int attempt = 0; attempt < 100; ++attempt) {
            path_ = fs::temp_directory_path() / ("hammond-library-model-storage-" +
                std::to_string(stamp) + "-" + std::to_string(attempt));
            std::error_code code;
            if (fs::create_directory(path_, code)) return;
            if (code && code != std::errc::file_exists) break;
        }
        throw std::runtime_error("Could not reserve storage-integration test directory");
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

void write_file(const fs::path& path, std::string_view bytes) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    output.write(bytes.data(), static_cast<std::streamsize>(bytes.size()));
    output.close();
    if (!output) throw std::runtime_error("Fixture write failed");
}

std::string read_bytes(const fs::path& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) throw std::runtime_error("Fixture read failed");
    return {std::istreambuf_iterator<char>(input), std::istreambuf_iterator<char>()};
}

std::vector<fs::path> directory_entries(const fs::path& root) {
    std::vector<fs::path> entries;
    for (const auto& item : fs::directory_iterator(root)) entries.push_back(item.path().filename());
    std::sort(entries.begin(), entries.end());
    return entries;
}

std::vector<fs::path> staging_directories(const fs::path& root) {
    std::vector<fs::path> paths;
    const auto prefix = fs::path(".b3-library-save-").native();
    for (const auto& item : fs::directory_iterator(root)) {
        // Inspect native code units; never narrow a Unicode parent/filename.
        if (item.path().filename().native().starts_with(prefix)) paths.push_back(item.path());
    }
    return paths;
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

void require_terminal(const LibraryModel& model, LibraryOutcome outcome) {
    const auto receipt = operation(model);
    REQUIRE(receipt.phase == LibraryOperationPhase::Finished);
    REQUIRE(receipt.outcome == outcome);
}

// Each read creates an owned, just-requested copy of this synthetic publication;
// it never returns the model's cached display. A failed read returns nullopt
// despite the fixture retaining the previous successful publication. This is
// controlled model input, not an impersonation of Session::read_snapshot.
class SyntheticControlPublication {
public:
    SyntheticControlPublication() {
        actual.prepared = true;
        actual.running = true;
        actual.publication_revision = 2;
        actual.sample_rate = 48000.0;
        actual.frame_clock = 128;
    }

    LibraryObservation fresh_read() {
        ++read_attempts;
        LibraryObservation observation;
        observation.audio_commands_enabled = actual.running;
        if (fail_next_read) fail_next_read = false;
        else observation.snapshot = actual;
        return observation;
    }

    void publish_controls(const ControlSnapshot& controls, std::uint64_t sequence) {
        actual.controls = controls;
        actual.publication_revision += 2;
        actual.resolved_sequence = sequence;
        actual.last_applied_sequence = sequence;
    }

    void stop() {
        actual.running = false;
        actual.publication_revision += 2;
    }

    SessionSnapshot actual;
    std::size_t read_attempts{};
    bool fail_next_read{};
};

struct StorageExecution {
    LibrarySaveResult result;
    std::size_t authorizer_calls{};
    std::size_t reads_before_final{};
    std::size_t reads_after_final{};
    std::vector<fs::path> staging_at_authorization;
    std::string staged_bytes;
    LibraryObservation final_observation;
    std::optional<LibraryCommitAuthorization> authorization;
};

class Harness {
public:
    Harness() {
        std::string error;
        REQUIRE(resolve_registration_library_root(tree.path() / "library", root, error));
        REQUIRE(error.empty() && root.is_absolute());
        REQUIRE(!fs::exists(root));
        (void)refresh();
        model.observe(publication.fresh_read(), tick());
        REQUIRE(model.view().observation_fresh);
        prove_controls(expected_controls());
    }

    std::uint64_t tick() { return ++now; }

    LibraryCatalog refresh() {
        const auto intent = model.request_refresh();
        REQUIRE(intent.has_value());
        const auto catalog = scan_registration_library(root, intent->generation);
        REQUIRE(catalog.complete());
        REQUIRE(model.replace_catalog(catalog));
        REQUIRE(!model.view().catalog_stale);
        return catalog;
    }

    void prove_controls(const ControlSnapshot& controls) {
        const auto intent = model.note_control_intent(controls, publication.fresh_read());
        REQUIRE(intent.has_value());
        REQUIRE(intent->expected_controls == controls);
        ++sequence;
        // Deliberately synthetic successful post/publication pair. The real
        // Session test suite independently qualifies that source of proof.
        REQUIRE(model.submitted({SessionStatus::Ok, sequence}, intent) == LibraryOutcome::Accepted);
        publication.publish_controls(controls, sequence);
        model.observe(publication.fresh_read(), tick());
        REQUIRE(model.view().observation_fresh && !model.view().controls_pending);
    }

    LibrarySaveIntent begin_save(std::string_view name,
        RegistrationScope scope = RegistrationScope::Registration) {
        REQUIRE(model.set_name(name));
        REQUIRE(model.set_save_scope(scope));
        const auto requested = model.request_save_new(publication.fresh_read(), tick());
        REQUIRE(requested.outcome == LibraryOutcome::Accepted && !requested.recall);
        REQUIRE(operation(model).phase == LibraryOperationPhase::ReadyToSave);
        const auto effect = model.take_save_intent(publication.fresh_read(), tick());
        REQUIRE(effect.has_value());
        REQUIRE(effect->operation_id != 0);
        REQUIRE(effect->acknowledged_controls == expected_controls());
        REQUIRE(operation(model).phase == LibraryOperationPhase::Saving);
        return *effect;
    }

    StorageExecution execute(const LibrarySaveIntent& effect,
        const std::function<void()>& before_final_read = {},
        std::span<const fs::path> protected_paths = {}) {
        StorageExecution execution;
        execution.result = save_registration_entry_new(root, effect.name, effect.scope,
            effect.acknowledged_controls, protected_paths, [&]() {
                ++execution.authorizer_calls;
                execution.staging_at_authorization = staging_directories(root);
                if (execution.staging_at_authorization.size() == 1) {
                    execution.staged_bytes = read_bytes(
                        execution.staging_at_authorization.front() / "controls.tmp");
                }
                // Test-only injection simulates a change during staging. It
                // occurs BEFORE the final fresh read and never after a true
                // authorization. No event loop or asynchronous work is used.
                if (before_final_read) before_final_read();
                execution.reads_before_final = publication.read_attempts;
                execution.final_observation = publication.fresh_read();
                execution.reads_after_final = publication.read_attempts;
                execution.authorization = model.authorize_save(effect.operation_id,
                    execution.final_observation, tick());
                return *execution.authorization;
            });
        return execution;
    }

    TemporaryTree tree;
    fs::path root;
    LibraryModel model;
    SyntheticControlPublication publication;
    std::uint64_t now{};
    std::uint64_t sequence{};
};

void require_final_read(const StorageExecution& execution, bool permitted) {
    REQUIRE(execution.authorizer_calls == 1);
    REQUIRE(execution.staging_at_authorization.size() == 1);
    REQUIRE(execution.staged_bytes == kCanonicalDocument);
    REQUIRE(execution.reads_after_final == execution.reads_before_final + 1);
    REQUIRE(execution.authorization.has_value());
    REQUIRE(execution.authorization->permitted == permitted);
}

void require_committed_payload(const Harness& fixture, const LibrarySaveIntent& effect,
    const LibrarySaveResult& result) {
    REQUIRE(result.committed());
    REQUIRE(result.committed_entry && result.committed_entry->valid());
    REQUIRE(result.committed_entry->key == effect.key);
    REQUIRE(result.committed_entry->name == effect.name);
    REQUIRE(result.committed_entry->scope == effect.scope);
    REQUIRE(*result.committed_entry->controls == expected_controls());
    REQUIRE(result.committed_entry->controls->expression == 0.25);
    REQUIRE(read_bytes(fixture.root / effect.key) == kCanonicalDocument);
    const auto reread = read_registration_entry(fixture.root, effect.key);
    REQUIRE(reread.valid() && reread.key == effect.key && reread.name == effect.name);
    REQUIRE(reread.scope == effect.scope && *reread.controls == expected_controls());
    REQUIRE(staging_directories(fixture.root).empty());
}

void copied_catalog_and_selection_leave_disk_untouched() {
    Harness fixture;
    REQUIRE(fixture.model.view().catalog.status == LibraryCatalogStatus::MissingDirectory);
    REQUIRE(!fs::exists(fixture.root));
    REQUIRE(fixture.model.set_name("Draft only"));
    REQUIRE(fixture.model.set_save_scope(RegistrationScope::Performance));
    REQUIRE(!fixture.model.select("Absent.b3performance"));
    (void)fixture.refresh();
    REQUIRE(!fs::exists(fixture.root));
    REQUIRE(!fixture.model.view().operation && !fixture.model.view().current_reference);

    REQUIRE(fs::create_directory(fixture.root));
    write_file(fixture.root / "Alpha.b3registration", kCanonicalDocument);
    write_file(fixture.root / "Omega.b3performance", kCanonicalDocument);
    const auto catalog = fixture.refresh();
    REQUIRE(catalog.entries.size() == 2 && catalog.directory_items == 2);
    REQUIRE(fixture.model.view().selected_key == "Alpha.b3registration");
    const auto before = directory_entries(fixture.root);
    REQUIRE(fixture.model.select("Omega.b3performance"));
    REQUIRE(fixture.model.select_relative(-1));
    REQUIRE(fixture.model.select_relative(1));
    REQUIRE(directory_entries(fixture.root) == before);
    REQUIRE(read_bytes(fixture.root / "Alpha.b3registration") == kCanonicalDocument);
    REQUIRE(read_bytes(fixture.root / "Omega.b3performance") == kCanonicalDocument);

    // Remove only this fixture's inputs. Selection still operates on copied
    // rows, demonstrating that it does not implicitly re-read or recreate them.
    REQUIRE(fs::remove(fixture.root / "Alpha.b3registration"));
    REQUIRE(fs::remove(fixture.root / "Omega.b3performance"));
    REQUIRE(fs::remove(fixture.root));
    REQUIRE(fixture.model.select("Alpha.b3registration"));
    REQUIRE(fixture.model.view().selected_preview->valid());
    REQUIRE(*fixture.model.view().selected_preview->controls == expected_controls());
    REQUIRE(fixture.model.view().catalog.generation == catalog.generation);
    const auto refresh = fixture.model.request_refresh();
    REQUIRE(refresh.has_value() && !fs::exists(fixture.root));
    REQUIRE(fixture.model.view().catalog.entries.size() == 2);
    const auto missing = scan_registration_library(fixture.root, refresh->generation);
    REQUIRE(fixture.model.replace_catalog(missing));
    REQUIRE(!fixture.model.view().selected_key && fixture.model.view().catalog.entries.empty());
    REQUIRE(!fs::exists(fixture.root));
    REQUIRE(!fixture.model.view().operation && !fixture.model.view().current_reference);
}

void both_scope_files_preserve_complete_canonical_snapshot() {
    Harness fixture;
    const auto initial_generation = fixture.model.view().catalog.generation;
    const auto registration = fixture.begin_save("Sunday warm");
    REQUIRE(registration.key == "Sunday warm.b3registration");
    REQUIRE(!fs::exists(fixture.root));
    REQUIRE(!fixture.model.take_save_intent(fixture.publication.fresh_read(), fixture.tick()));
    REQUIRE(fixture.model.set_name("Later draft"));
    REQUIRE(fixture.model.set_save_scope(RegistrationScope::Performance));
    REQUIRE(fixture.model.request_save_new(fixture.publication.fresh_read(), fixture.tick()).outcome ==
        LibraryOutcome::Busy);
    REQUIRE(operation(fixture.model).target_key == registration.key);

    const auto first = fixture.execute(registration);
    require_final_read(first, true);
    REQUIRE(first.result.status == LibrarySaveStatus::Saved);
    require_committed_payload(fixture, registration, first.result);
    REQUIRE(first.result.refreshed_catalog && first.result.refreshed_catalog->generation == 0);
    REQUIRE(!fixture.model.view().current_reference);
    REQUIRE(fixture.model.complete_save(registration.operation_id, first.result) == LibraryOutcome::Saved);
    const auto saved_registration = fixture.model.view();
    REQUIRE(saved_registration.catalog.generation == initial_generation + 1);
    REQUIRE(!saved_registration.catalog_stale && saved_registration.catalog.entries.size() == 1);
    REQUIRE(saved_registration.selected_key == registration.key);
    REQUIRE(saved_registration.selected_preview->scope == RegistrationScope::Registration);
    REQUIRE(saved_registration.name_draft == "Later draft");
    REQUIRE(reference(fixture.model).origin == LibraryReferenceOrigin::AcknowledgedSave);
    REQUIRE(reference(fixture.model).key == registration.key);
    REQUIRE(!reference(fixture.model).modified && !reference(fixture.model).missing);
    REQUIRE(directory_entries(fixture.root) == std::vector<fs::path>{fs::path(registration.key)});
    REQUIRE(!fs::exists(fixture.root / "Later draft.b3performance"));

    const auto performance = fixture.begin_save("Sunday warm", RegistrationScope::Performance);
    REQUIRE(performance.key == "Sunday warm.b3performance");
    REQUIRE(performance.operation_id > registration.operation_id);
    REQUIRE(fixture.model.complete_save(registration.operation_id, first.result) == LibraryOutcome::StaleResult);
    REQUIRE(operation(fixture.model).operation_id == performance.operation_id);
    REQUIRE(operation(fixture.model).phase == LibraryOperationPhase::Saving);
    const auto second = fixture.execute(performance);
    require_final_read(second, true);
    REQUIRE(second.result.status == LibrarySaveStatus::Saved);
    require_committed_payload(fixture, performance, second.result);
    REQUIRE(second.result.refreshed_catalog && second.result.refreshed_catalog->generation == 0);
    REQUIRE(fixture.model.complete_save(performance.operation_id, second.result) == LibraryOutcome::Saved);
    REQUIRE(fixture.model.view().catalog.generation == initial_generation + 2);
    REQUIRE(fixture.model.view().selected_key == performance.key);
    REQUIRE(reference(fixture.model).scope == RegistrationScope::Performance);
    REQUIRE(reference(fixture.model).key == performance.key);
    REQUIRE(reference(fixture.model).origin == LibraryReferenceOrigin::AcknowledgedSave);
    const std::vector<fs::path> expected_files{fs::path(performance.key), fs::path(registration.key)};
    REQUIRE(directory_entries(fixture.root) == expected_files);
    REQUIRE(read_bytes(fixture.root / registration.key) == read_bytes(fixture.root / performance.key));
    REQUIRE(fixture.model.select(registration.key));
    REQUIRE(reference(fixture.model).key == performance.key);
    REQUIRE(operation(fixture.model).target_key == performance.key);
    REQUIRE(fixture.model.complete_save(performance.operation_id, second.result) == LibraryOutcome::StaleResult);
    REQUIRE(fixture.model.view().selected_key == registration.key);
    REQUIRE(reference(fixture.model).key == performance.key);
    require_terminal(fixture.model, LibraryOutcome::Saved);
}

void existing_or_late_created_target_is_never_replaced() {
    {
        Harness fixture;
        REQUIRE(fs::create_directory(fixture.root));
        write_file(fixture.root / "Taken.b3registration", kCanonicalDocument);
        (void)fixture.refresh();
        for (const auto name : {"Taken", "tAkEn"}) {
            REQUIRE(fixture.model.set_name(name));
            const auto request = fixture.model.request_save_new(fixture.publication.fresh_read(), fixture.tick());
            REQUIRE(request.outcome == LibraryOutcome::InvalidInput);
            REQUIRE(!fixture.model.view().operation);
            REQUIRE(fixture.model.view().name_draft == name);
            REQUIRE(read_bytes(fixture.root / "Taken.b3registration") == kCanonicalDocument);
            REQUIRE(staging_directories(fixture.root).empty());
        }
    }
    for (const bool collision_in_authorizer : {false, true}) {
        Harness fixture;
        const auto effect = fixture.begin_save("External winner");
        constexpr std::string_view winner_bytes = "external exact-path winner\n";
        const auto create_winner = [&]() {
            if (!fs::exists(fixture.root)) REQUIRE(fs::create_directory(fixture.root));
            write_file(fixture.root / effect.key, winner_bytes);
        };
        // First run: external creation after the model's preview, before the
        // storage scan. Second: creation after final admission, just before
        // the authorizer's fresh read, exercising native atomic no-replace.
        if (!collision_in_authorizer) create_winner();
        const auto execution = fixture.execute(effect,
            collision_in_authorizer ? std::function<void()>(create_winner) : std::function<void()>{});
        REQUIRE(execution.result.status == LibrarySaveStatus::NameExists && !execution.result.committed());
        REQUIRE(!execution.result.committed_entry);
        if (collision_in_authorizer) require_final_read(execution, true);
        else REQUIRE(execution.authorizer_calls == 0 && !execution.authorization);
        REQUIRE(fixture.model.complete_save(effect.operation_id, execution.result) == LibraryOutcome::SaveFailed);
        require_terminal(fixture.model, LibraryOutcome::SaveFailed);
        REQUIRE(operation(fixture.model).target_key == effect.key);
        REQUIRE(!fixture.model.view().current_reference);
        REQUIRE(fixture.model.view().name_draft == effect.name);
        REQUIRE(read_bytes(fixture.root / effect.key) == winner_bytes);
        REQUIRE(staging_directories(fixture.root).empty());
        REQUIRE(directory_entries(fixture.root) == std::vector<fs::path>{fs::path(effect.key)});
    }
}

enum class Refusal { Lifecycle, NewEqualIntent, FailedFreshRead, FailedPost, Timeout };

void final_authorization_refusals_clean_only_owned_staging() {
    constexpr std::array cases{
        std::pair{Refusal::Lifecycle, LibraryOutcome::Cancelled},
        std::pair{Refusal::NewEqualIntent, LibraryOutcome::Superseded},
        std::pair{Refusal::FailedFreshRead, LibraryOutcome::SnapshotUnavailable},
        std::pair{Refusal::FailedPost, LibraryOutcome::Rejected},
        std::pair{Refusal::Timeout, LibraryOutcome::Unconfirmed}};
    for (const auto& [refusal, expected] : cases) {
        Harness fixture;
        REQUIRE(fs::create_directory(fixture.root));
        write_file(fixture.root / "unrelated.txt", "retain unrelated bytes\n");
        (void)fixture.refresh();
        const auto before = directory_entries(fixture.root);
        const auto effect = fixture.begin_save("Never published");
        const auto execution = fixture.execute(effect, [&]() {
            switch (refusal) {
            case Refusal::Lifecycle:
                fixture.model.audio_lifecycle_changed(LibraryAudioTransition::Stop);
                fixture.publication.stop();
                break;
            case Refusal::NewEqualIntent: {
                // Same values still mean a newer intention. No actual Session
                // submission is simulated after this intentionally pending edit.
                const auto intent = fixture.model.note_control_intent(expected_controls(),
                    fixture.publication.fresh_read());
                REQUIRE(intent.has_value());
                break;
            }
            case Refusal::FailedFreshRead:
                fixture.publication.fail_next_read = true;
                break;
            case Refusal::FailedPost:
                REQUIRE(fixture.model.submitted({SessionStatus::QueueFull, 0}) == LibraryOutcome::Rejected);
                break;
            case Refusal::Timeout:
                fixture.now += kLibraryAcknowledgmentWaitMs;
                break;
            }
        });
        require_final_read(execution, false);
        REQUIRE(execution.result.status == LibrarySaveStatus::NotAuthorized && !execution.result.committed());
        REQUIRE(!execution.result.committed_entry && !execution.result.refreshed_catalog);
        REQUIRE(!execution.result.reason.empty());
        if (refusal == Refusal::FailedFreshRead) {
            REQUIRE(!execution.final_observation.snapshot);
            REQUIRE(fixture.publication.actual.controls == expected_controls());
            REQUIRE(!fixture.model.view().observation_fresh);
        }
        REQUIRE(fixture.model.complete_save(effect.operation_id, execution.result) == expected);
        require_terminal(fixture.model, expected);
        REQUIRE(!fixture.model.view().current_reference);
        REQUIRE(fixture.model.view().name_draft == effect.name);
        REQUIRE(!fs::exists(fixture.root / effect.key));
        REQUIRE(staging_directories(fixture.root).empty());
        REQUIRE(directory_entries(fixture.root) == before);
        REQUIRE(read_bytes(fixture.root / "unrelated.txt") == "retain unrelated bytes\n");
        REQUIRE(!fixture.model.take_save_intent(fixture.publication.fresh_read(), fixture.tick()));
        REQUIRE(!fixture.model.authorize_save(effect.operation_id, fixture.publication.fresh_read(),
            fixture.tick()).permitted);
        require_terminal(fixture.model, expected);
    }
}

void authorized_commit_retains_truth_after_later_control_changes() {
    for (const auto scope : {RegistrationScope::Registration, RegistrationScope::Performance}) {
        Harness fixture;
        const auto effect = fixture.begin_save("Acknowledged past copy", scope);
        const auto execution = fixture.execute(effect);
        require_final_read(execution, true);
        REQUIRE(execution.result.status == LibrarySaveStatus::Saved);
        require_committed_payload(fixture, effect, execution.result);

        // The synchronous storage call has returned. Only now introduce a
        // later intention, observation, lifecycle boundary and elapsed deadline;
        // none can undo the file already authorized from the earlier copy.
        auto later_controls = expected_controls();
        later_controls.expression = 0.75;
        fixture.prove_controls(later_controls);
        fixture.model.audio_lifecycle_changed(LibraryAudioTransition::Stop);
        fixture.publication.stop();
        fixture.now += kLibraryAcknowledgmentWaitMs;
        fixture.model.observe(fixture.publication.fresh_read(), fixture.tick());
        REQUIRE(operation(fixture.model).phase == LibraryOperationPhase::Saving);
        REQUIRE(!fixture.model.authorize_save(effect.operation_id, fixture.publication.fresh_read(),
            fixture.tick()).permitted);
        REQUIRE(fixture.model.request_save_new(fixture.publication.fresh_read(), fixture.tick()).outcome ==
            LibraryOutcome::Busy);
        REQUIRE(fixture.model.complete_save(effect.operation_id, execution.result) == LibraryOutcome::Saved);
        require_terminal(fixture.model, LibraryOutcome::Saved);
        REQUIRE(reference(fixture.model).key == effect.key);
        REQUIRE(reference(fixture.model).origin == LibraryReferenceOrigin::AcknowledgedSave);
        REQUIRE(reference(fixture.model).modified == (scope == RegistrationScope::Performance));
        REQUIRE(!reference(fixture.model).missing);
        REQUIRE(fixture.publication.actual.controls == later_controls);
        REQUIRE(read_bytes(fixture.root / effect.key) == kCanonicalDocument);
        REQUIRE(fixture.model.complete_save(effect.operation_id, execution.result) == LibraryOutcome::StaleResult);
        require_terminal(fixture.model, LibraryOutcome::Saved);
    }
}

void stale_storage_effect_and_duplicate_result_cannot_retarget() {
    Harness fixture;
    const auto earlier = fixture.begin_save("Earlier target");
    fixture.model.audio_lifecycle_changed(LibraryAudioTransition::Stop);
    fixture.publication.stop();
    fixture.model.observe(fixture.publication.fresh_read(), fixture.tick());
    require_terminal(fixture.model, LibraryOutcome::Cancelled);
    const auto current = fixture.begin_save("Current target", RegistrationScope::Performance);
    REQUIRE(current.operation_id > earlier.operation_id);
    REQUIRE(!fixture.publication.actual.running);

    // Actually execute the stale copied effect. Its bound old ID must refuse
    // inside the real storage authorizer and remove its own staged file.
    const auto stale_execution = fixture.execute(earlier);
    require_final_read(stale_execution, false);
    REQUIRE(stale_execution.result.status == LibrarySaveStatus::NotAuthorized);
    REQUIRE(!fs::exists(fixture.root / earlier.key));
    REQUIRE(staging_directories(fixture.root).empty());
    REQUIRE(directory_entries(fixture.root).empty());
    REQUIRE(fixture.model.complete_save(earlier.operation_id, stale_execution.result) == LibraryOutcome::StaleResult);
    REQUIRE(operation(fixture.model).operation_id == current.operation_id);
    REQUIRE(operation(fixture.model).target_key == current.key);
    REQUIRE(operation(fixture.model).phase == LibraryOperationPhase::Saving);
    REQUIRE(!fixture.model.view().current_reference);

    const auto current_execution = fixture.execute(current);
    require_final_read(current_execution, true);
    REQUIRE(current_execution.final_observation.snapshot.has_value());
    REQUIRE(!current_execution.final_observation.snapshot->running);
    REQUIRE(!current_execution.final_observation.audio_commands_enabled);
    REQUIRE(current_execution.result.status == LibrarySaveStatus::Saved);
    require_committed_payload(fixture, current, current_execution.result);
    REQUIRE(fixture.model.complete_save(current.operation_id, current_execution.result) == LibraryOutcome::Saved);
    REQUIRE(fixture.model.view().selected_key == current.key);
    REQUIRE(reference(fixture.model).key == current.key);
    REQUIRE(fixture.model.complete_save(earlier.operation_id, stale_execution.result) == LibraryOutcome::StaleResult);
    REQUIRE(fixture.model.complete_save(current.operation_id, current_execution.result) == LibraryOutcome::StaleResult);
    REQUIRE(fixture.model.view().selected_key == current.key);
    REQUIRE(reference(fixture.model).key == current.key);
    require_terminal(fixture.model, LibraryOutcome::Saved);
    REQUIRE(directory_entries(fixture.root) == std::vector<fs::path>{fs::path(current.key)});
}

void newer_explicit_refresh_wins_over_compound_generation_zero() {
    Harness fixture;
    REQUIRE(fs::create_directory(fixture.root));
    write_file(fixture.root / "Anchor.b3registration", kCanonicalDocument);
    (void)fixture.refresh();
    const auto effect = fixture.begin_save("Saved after scan");
    const auto newer = fixture.model.request_refresh();
    REQUIRE(newer.has_value());
    const auto precommit_catalog = scan_registration_library(fixture.root, newer->generation);
    REQUIRE(precommit_catalog.entries.size() == 1);
    REQUIRE(fixture.model.replace_catalog(precommit_catalog));
    REQUIRE(fixture.model.select("Anchor.b3registration"));

    const auto execution = fixture.execute(effect);
    require_final_read(execution, true);
    REQUIRE(execution.result.status == LibrarySaveStatus::Saved);
    REQUIRE(execution.result.refreshed_catalog && execution.result.refreshed_catalog->generation == 0);
    REQUIRE(execution.result.refreshed_catalog->entries.size() == 2);
    REQUIRE(fixture.model.complete_save(effect.operation_id, execution.result) == LibraryOutcome::Saved);
    REQUIRE(fixture.model.view().catalog.generation == newer->generation);
    REQUIRE(fixture.model.view().catalog.entries.size() == 1);
    REQUIRE(fixture.model.view().selected_key == "Anchor.b3registration");
    REQUIRE(reference(fixture.model).key == effect.key && !reference(fixture.model).missing);
    require_committed_payload(fixture, effect, execution.result);
    const auto after = fixture.refresh();
    REQUIRE(after.generation > newer->generation && after.entries.size() == 2);
    REQUIRE(fixture.model.view().selected_key == "Anchor.b3registration");
    REQUIRE(!reference(fixture.model).missing);
    require_terminal(fixture.model, LibraryOutcome::Saved);
}

void committed_refresh_failure_remains_saved_with_warning() {
    Harness fixture;
    const auto initial_generation = fixture.model.view().catalog.generation;
    const auto effect = fixture.begin_save("Committed");
    const auto external_key = [](std::size_t index) {
        return "External" + std::to_string(index) + ".b3registration";
    };
    const auto execution = fixture.execute(effect, [&]() {
        // Existing authorizer hook, with no production seam: simulate external
        // directory creation after storage's final capacity scan. The final
        // control observation/authorization still immediately precedes commit.
        for (std::size_t index = 0; index < kRegistrationLibraryMaxEntries; ++index) {
            write_file(fixture.root / external_key(index), kCanonicalDocument);
        }
    });
    require_final_read(execution, true);
    REQUIRE(execution.result.status == LibrarySaveStatus::SavedWithWarning);
    require_committed_payload(fixture, effect, execution.result);
    REQUIRE(execution.result.refreshed_catalog && execution.result.refreshed_catalog->generation == 0);
    REQUIRE(execution.result.refreshed_catalog->status == LibraryCatalogStatus::CapacityExceeded);
    REQUIRE(!execution.result.refreshed_catalog->complete());
    REQUIRE(execution.result.refreshed_catalog->entries.empty());
    REQUIRE(execution.result.reason.find("refresh") != std::string::npos);
    REQUIRE(fixture.model.complete_save(effect.operation_id, execution.result) == LibraryOutcome::SavedWithWarning);
    require_terminal(fixture.model, LibraryOutcome::SavedWithWarning);
    const auto view = fixture.model.view();
    REQUIRE(view.catalog.generation == initial_generation && view.catalog.entries.empty());
    REQUIRE(view.catalog_stale && view.last_scan_status == LibraryCatalogStatus::CapacityExceeded);
    REQUIRE(!view.selected_key);
    REQUIRE(reference(fixture.model).key == effect.key);
    REQUIRE(reference(fixture.model).origin == LibraryReferenceOrigin::AcknowledgedSave);
    REQUIRE(!reference(fixture.model).missing && !reference(fixture.model).modified);
    REQUIRE(directory_entries(fixture.root).size() == kRegistrationLibraryMaxEntries + 1);
    REQUIRE(read_registration_entry(fixture.root, effect.key).valid());

    const auto still_full = fixture.model.request_refresh();
    REQUIRE(still_full.has_value());
    const auto failed_catalog = scan_registration_library(fixture.root, still_full->generation);
    REQUIRE(!fixture.model.replace_catalog(failed_catalog));
    REQUIRE(!reference(fixture.model).missing);
    require_terminal(fixture.model, LibraryOutcome::SavedWithWarning);
    for (std::size_t index = 0; index < kRegistrationLibraryMaxEntries; ++index) {
        REQUIRE(fs::remove(fixture.root / external_key(index)));
    }
    const auto recovered_catalog = fixture.refresh();
    REQUIRE(recovered_catalog.entries.size() == 1);
    REQUIRE(fixture.model.view().selected_key == effect.key);
    REQUIRE(!reference(fixture.model).missing);
    require_terminal(fixture.model, LibraryOutcome::SavedWithWarning);
    REQUIRE(read_bytes(fixture.root / effect.key) == kCanonicalDocument);
    REQUIRE(directory_entries(fixture.root) == std::vector<fs::path>{fs::path(effect.key)});
}

void unicode_root_and_protected_alias_preserve_existing_reference() {
    Harness fixture;
    const auto output = fixture.tree.path() / "output";
    const auto source = fixture.tree.path() / "source";
    REQUIRE(fs::create_directory(output));
    REQUIRE(fs::create_directory(source));
    const auto unicode_parent = output / fs::path(u8"caf\u00e9 staging");
    REQUIRE(fs::create_directory(unicode_parent));
    std::string error;
    REQUIRE(resolve_registration_library_root(unicode_parent / "entries", fixture.root, error));
    REQUIRE(error.empty() && !fs::exists(fixture.root));
    (void)fixture.refresh();
    write_file(source / "reference.controls", "protected source bytes\n");
    const std::array<fs::path, 1> protected_source{source / "reference.controls"};
    const auto admitted = fixture.begin_save("Unicode root");
    const auto saved = fixture.execute(admitted, {}, protected_source);
    require_final_read(saved, true);
    REQUIRE(saved.result.status == LibrarySaveStatus::Saved);
    require_committed_payload(fixture, admitted, saved.result);
    REQUIRE(fixture.model.complete_save(admitted.operation_id, saved.result) == LibraryOutcome::Saved);
    REQUIRE(read_bytes(protected_source[0]) == "protected source bytes\n");

    const auto refused = fixture.begin_save("Protected destination");
    const std::array<fs::path, 1> protected_alias{fixture.root / "PROTECTED DESTINATION.b3registration"};
    const auto blocked = fixture.execute(refused, {}, protected_alias);
    REQUIRE(blocked.result.status == LibrarySaveStatus::ProtectedPath && !blocked.result.committed());
    REQUIRE(blocked.authorizer_calls == 0 && !blocked.authorization);
    REQUIRE(fixture.model.complete_save(refused.operation_id, blocked.result) == LibraryOutcome::SaveFailed);
    REQUIRE(reference(fixture.model).key == admitted.key);
    REQUIRE(reference(fixture.model).origin == LibraryReferenceOrigin::AcknowledgedSave);
    REQUIRE(!reference(fixture.model).missing && !reference(fixture.model).modified);
    REQUIRE(!fs::exists(fixture.root / refused.key) && !fs::exists(protected_alias[0]));
    REQUIRE(directory_entries(fixture.root) == std::vector<fs::path>{fs::path(admitted.key)});
    REQUIRE(read_bytes(fixture.root / admitted.key) == kCanonicalDocument);
    REQUIRE(read_bytes(protected_source[0]) == "protected source bytes\n");
    REQUIRE(staging_directories(fixture.root).empty());
}

} // namespace

int main() {
    using Test = std::pair<std::string_view, void (*)()>;
    const std::array tests{
        Test{"copied catalog and selection", copied_catalog_and_selection_leave_disk_untouched},
        Test{"canonical scope files", both_scope_files_preserve_complete_canonical_snapshot},
        Test{"existing and late targets", existing_or_late_created_target_is_never_replaced},
        Test{"final authorization refusals", final_authorization_refusals_clean_only_owned_staging},
        Test{"later controls after authorization", authorized_commit_retains_truth_after_later_control_changes},
        Test{"stale effects and duplicate results", stale_storage_effect_and_duplicate_result_cannot_retarget},
        Test{"newer explicit refresh", newer_explicit_refresh_wins_over_compound_generation_zero},
        Test{"committed refresh warning", committed_refresh_failure_remains_saved_with_warning},
        Test{"Unicode root and protected alias", unicode_root_and_protected_alias_preserve_existing_reference}};
    std::size_t failures = 0;
    for (const auto& [name, test] : tests) {
        current_case = name;
        try {
            test();
        } catch (const std::exception& error) {
            ++failures;
            std::cerr << "library_storage: " << error.what() << '\n';
        }
    }
    std::cout << "library_storage groups=" << tests.size() << " checks=" << checks <<
        " failures=" << failures << " control_proof=synthetic filesystem=real\n";
    return failures == 0 ? 0 : 1;
}
