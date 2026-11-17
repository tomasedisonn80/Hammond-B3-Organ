#pragma once

#include "RegistrationLibrary.h"
#include "Session.h"

#include <cstdint>
#include <limits>
#include <memory>
#include <optional>
#include <string>
#include <string_view>

namespace hammond::standalone {

// Main-thread copied-state foundation, not a Session or filesystem adapter.
// See docs/LIBRARY_MODEL_DESIGN.md and REGISTRATION_LIBRARY_CONTRACT.md.
inline constexpr std::string_view kLibraryModelId = "standalone-library-model-v1";
inline constexpr std::uint64_t kLibraryAcknowledgmentWaitMs = 2000;

struct LibraryModelLimits {
    std::uint64_t operation_ids{std::numeric_limits<std::uint64_t>::max()};
    std::uint64_t desired_revisions{std::numeric_limits<std::uint64_t>::max()};
    std::uint64_t submission_failure_revisions{std::numeric_limits<std::uint64_t>::max()};
    std::uint64_t catalog_generations{std::numeric_limits<std::uint64_t>::max()};
};

enum class LibraryOperationKind : std::uint8_t { Recall, SaveNew };
enum class LibraryOperationPhase : std::uint8_t {
    AwaitingSubmission, AwaitingAcknowledgment, ReadyToSave, Saving, Finished
};
enum class LibraryOutcome : std::uint8_t {
    None, Accepted, Busy, InvalidInput, CatalogUnavailable, NoSelection,
    InvalidEntry, EntryChanged, NoAudio, SnapshotUnavailable,
    NoAcknowledgedControls, Rejected, Superseded, Unconfirmed, Cancelled,
    Exhausted, Applied, Saved, SavedWithWarning, SaveFailed, StaleResult,
    ProtocolError
};
enum class LibraryReferenceOrigin : std::uint8_t { Recall, AcknowledgedSave };
enum class LibraryAudioTransition : std::uint8_t { Stop, Start, Prepare };

// Each call site must supply its own just-completed read_snapshot result.
// nullopt means the read failed: cached display values are never fresh proof.
// audio_commands_enabled is the actual native dispatch gate, not a UI guess.
struct LibraryObservation {
    std::optional<SessionSnapshot> snapshot;
    bool audio_commands_enabled{false};
};

// Obtained for EVERY whole-control intent, including a same-value intent.
// The token is attached to exactly one actual post result. An ordinary
// non-control post is reported without a token, including direct MIDI posts.
struct LibraryControlIntent {
    std::uint64_t desired_revision{};
    ControlSnapshot expected_controls{};
};

struct LibraryRefreshIntent {
    std::uint64_t generation{};
};

// Execute once through UiModel::recall_controls, then report its one post
// result with control_intent. Do not register this intent a second time.
struct LibraryRecallIntent {
    std::uint64_t operation_id{};
    LibraryControlIntent control_intent{};
};

// Execute once with save_registration_entry_new on the main thread. Bind
// operation_id in its mandatory synchronous authorize_commit callback.
struct LibrarySaveIntent {
    std::uint64_t operation_id{};
    LibraryEntryKey key;
    std::string name;
    RegistrationScope scope{RegistrationScope::Registration};
    ControlSnapshot acknowledged_controls{};
};

struct LibraryRequestResult {
    LibraryOutcome outcome{LibraryOutcome::None};
    std::string reason;
    std::optional<LibraryRecallIntent> recall;
};

struct LibraryOperationView {
    std::uint64_t operation_id{};
    LibraryOperationKind kind{LibraryOperationKind::Recall};
    LibraryOperationPhase phase{LibraryOperationPhase::Finished};
    LibraryEntryKey target_key;
    std::string target_name;
    RegistrationScope target_scope{RegistrationScope::Registration};
    std::uint64_t submitted_sequence{};
    LibraryOutcome outcome{LibraryOutcome::None};
    std::string reason;
};

struct LibraryCurrentReferenceView {
    LibraryEntryKey key;
    std::string name;
    RegistrationScope scope{RegistrationScope::Registration};
    LibraryReferenceOrigin origin{LibraryReferenceOrigin::Recall};
    bool modified{false};
    bool missing{false};
};

// All members are owned copies. catalog is the last complete catalog, while
// last_scan_status/reason describe the latest attempted scan. Failed scans
// retain the rows and set catalog_stale; catalog.generation stays unchanged.
// Full receipt guards and current-reference baselines stay inside the model.
struct LibraryView {
    LibraryCatalog catalog;
    LibraryCatalogStatus last_scan_status{LibraryCatalogStatus::DirectoryUnavailable};
    std::string last_scan_reason;
    bool catalog_stale{true};
    std::optional<LibraryEntryKey> selected_key;
    std::optional<LibraryEntry> selected_preview;
    std::string name_draft;
    RegistrationScope save_scope{RegistrationScope::Registration};
    std::optional<LibraryCurrentReferenceView> current_reference;
    std::optional<LibraryOperationView> operation;
    bool controls_pending{false};
    bool observation_fresh{false};
    bool mutations_exhausted{false};
    LibraryOutcome action_outcome{LibraryOutcome::None};
    std::string action_reason;
};

class LibraryModel {
public:
    explicit LibraryModel(LibraryModelLimits limits = {});
    ~LibraryModel();
    LibraryModel(const LibraryModel&) = delete;
    LibraryModel& operator=(const LibraryModel&) = delete;
    LibraryModel(LibraryModel&&) = delete;
    LibraryModel& operator=(LibraryModel&&) = delete;

    [[nodiscard]] LibraryView view() const;

    // No I/O. The caller passes the returned generation to scan_* and then
    // returns that complete value here. Only the newest requested generation
    // may publish; duplicate, unsolicited and late results are rejected.
    [[nodiscard]] std::optional<LibraryRefreshIntent> request_refresh();
    [[nodiscard]] bool replace_catalog(const LibraryCatalog& catalog);
    [[nodiscard]] bool select(std::string_view exact_key);
    // Clamp in the stable admitted row order; zero is a no-op. From no
    // selection, positive chooses the first row and negative the last row.
    // Disabled rows may be selected for inspection, never for Recall.
    [[nodiscard]] bool select_relative(int delta);
    [[nodiscard]] bool set_name(std::string_view draft);
    [[nodiscard]] bool set_save_scope(RegistrationScope scope);

    // Call before dispatching an ordinary valid whole-control intention.
    // Even equal controls allocate a new revision and supersede an unresolved
    // named operation. A failed snapshot still records the intention, but
    // cannot create an acknowledgement basis. nullopt means tracking is
    // exhausted or the input is invalid; ordinary UI operation is not owned
    // by this model, but named mutations then fail closed.
    [[nodiscard]] std::optional<LibraryControlIntent> note_control_intent(
        const ControlSnapshot& desired, const LibraryObservation& before_post);

    // Report EVERY real Session post/disabled-gate result once, synchronously.
    // Failed results increment the failure revision even without a control
    // token. Successful non-control posts cannot establish a control basis.
    // Successful control tokens must match the latest unsubmitted intention;
    // an accepted result requires a nonzero, increasing sequence.
    [[nodiscard]] LibraryOutcome submitted(
        const SubmitResult& result,
        const std::optional<LibraryControlIntent>& control_intent = std::nullopt);

    // now_ms is monotonic milliseconds in the current app invocation. No
    // system clock is read internally. Regressing time/malformed or older
    // snapshots supply no proof. A failed read retains display and still
    // allows timeout processing. Terminal receipts never resume on late ack.
    void observe(const LibraryObservation& observation, std::uint64_t now_ms);

    // Pass the fresh read_registration_entry result for the exact selected
    // key. Changed parsed controls/name/scope update preview and return
    // EntryChanged with no effect; unavailable/invalid entries disable it.
    // latest_desired is UiModel::view().controls at the actual activation;
    // it is the sole expression merge source, never cached/applied fallback.
    // Invalid desired controls reject atomically. Catalog-level Ambiguous
    // rows stay disabled until a complete new scan clears their collision.
    // A valid active request produces exactly one copied control intent.
    [[nodiscard]] LibraryRequestResult request_recall(
        const LibraryEntry& revalidated_entry, const ControlSnapshot& latest_desired,
        const LibraryObservation& observation, std::uint64_t now_ms);
    [[nodiscard]] LibraryRequestResult request_save_new(
        const LibraryObservation& observation, std::uint64_t now_ms);

    // ReadyToSave -> Saving occurs once. A new fresh observation must still
    // prove the receipt before the copied storage effect is released.
    [[nodiscard]] std::optional<LibrarySaveIntent> take_save_intent(
        const LibraryObservation& observation, std::uint64_t now_ms);

    // Bind this to the storage authorizer. The fresh read is the control-state
    // linearization point. No event pumping is permitted between a true
    // authorization and the synchronous storage result. A given operation
    // authorizes at most once. After true authorization, later observations
    // cannot undo an actually committed file or change its staged snapshot.
    [[nodiscard]] LibraryCommitAuthorization authorize_save(
        std::uint64_t operation_id, const LibraryObservation& observation,
        std::uint64_t now_ms);
    [[nodiscard]] LibraryOutcome complete_save(
        std::uint64_t operation_id, const LibrarySaveResult& result);

    // Main calls this at every real stop/start/prepare boundary, even if no
    // intermediate stopped snapshot was sampled. Cancels outstanding named
    // waits and unproved bases. Prepare also invalidates any previously proved
    // control basis; Stop/Start may retain a proved unchanged past copy.
    // Already-authorized storage completion retains its truthful disk outcome.
    void audio_lifecycle_changed(LibraryAudioTransition transition);

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace hammond::standalone
