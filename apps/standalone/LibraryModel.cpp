#include "LibraryModel.h"

#include <algorithm>
#include <bit>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <utility>

namespace hammond::standalone {
namespace {

constexpr auto kMaximum = std::numeric_limits<std::uint64_t>::max();

[[nodiscard]] std::string bounded(std::string_view text) {
    return std::string(text.substr(0, kRegistrationLibraryMaxDiagnosticBytes));
}

void append_reason(std::string& destination, std::string_view addition) {
    if (addition.empty() || destination.size() >= kRegistrationLibraryMaxDiagnosticBytes) return;
    if (!destination.empty()) destination.append("; ",
        std::min<std::size_t>(2, kRegistrationLibraryMaxDiagnosticBytes - destination.size()));
    destination.append(addition.substr(0, kRegistrationLibraryMaxDiagnosticBytes - destination.size()));
}

[[nodiscard]] char fold(char value) noexcept {
    return value >= 'A' && value <= 'Z' ? static_cast<char>(value + ('a' - 'A')) : value;
}

[[nodiscard]] int compare_names(std::string_view left, std::string_view right) noexcept {
    const auto count = std::min(left.size(), right.size());
    for (std::size_t index = 0; index < count; ++index) {
        const auto a = fold(left[index]);
        const auto b = fold(right[index]);
        if (a != b) return a < b ? -1 : 1;
    }
    if (left.size() == right.size()) return 0;
    return left.size() < right.size() ? -1 : 1;
}

[[nodiscard]] bool valid_entry_status(LibraryEntryStatus status) noexcept {
    switch (status) {
    case LibraryEntryStatus::Valid:
    case LibraryEntryStatus::InvalidKey:
    case LibraryEntryStatus::Ambiguous:
    case LibraryEntryStatus::InvalidPayload:
    case LibraryEntryStatus::TooLarge:
    case LibraryEntryStatus::NotRegularFile:
    case LibraryEntryStatus::Unavailable: return true;
    }
    return false;
}

[[nodiscard]] bool valid_catalog_status(LibraryCatalogStatus status) noexcept {
    switch (status) {
    case LibraryCatalogStatus::Ready:
    case LibraryCatalogStatus::Empty:
    case LibraryCatalogStatus::MissingDirectory:
    case LibraryCatalogStatus::InvalidRoot:
    case LibraryCatalogStatus::CapacityExceeded:
    case LibraryCatalogStatus::DirectoryUnavailable: return true;
    }
    return false;
}

[[nodiscard]] bool valid_save_status(LibrarySaveStatus status) noexcept {
    switch (status) {
    case LibrarySaveStatus::Saved:
    case LibrarySaveStatus::SavedWithWarning:
    case LibrarySaveStatus::InvalidName:
    case LibrarySaveStatus::InvalidScope:
    case LibrarySaveStatus::InvalidControls:
    case LibrarySaveStatus::NameExists:
    case LibrarySaveStatus::CapacityExceeded:
    case LibrarySaveStatus::InvalidRoot:
    case LibrarySaveStatus::DirectoryUnavailable:
    case LibrarySaveStatus::ProtectedPath:
    case LibrarySaveStatus::StagingFailed:
    case LibrarySaveStatus::WriteFailed:
    case LibrarySaveStatus::FlushFailed:
    case LibrarySaveStatus::CloseFailed:
    case LibrarySaveStatus::NotAuthorized:
    case LibrarySaveStatus::CommitFailed: return true;
    }
    return false;
}

[[nodiscard]] std::string_view submit_status_name(SessionStatus status) noexcept {
    switch (status) {
    case SessionStatus::Ok: return "Ok";
    case SessionStatus::NotPrepared: return "NotPrepared";
    case SessionStatus::AlreadyRunning: return "AlreadyRunning";
    case SessionStatus::NotRunning: return "NotRunning";
    case SessionStatus::InvalidSpec: return "InvalidSpec";
    case SessionStatus::InvalidProfile: return "InvalidProfile";
    case SessionStatus::InvalidBuffer: return "InvalidBuffer";
    case SessionStatus::BlockTooLarge: return "BlockTooLarge";
    case SessionStatus::TimelineOverflow: return "TimelineOverflow";
    case SessionStatus::InvalidCommand: return "InvalidCommand";
    case SessionStatus::QueueFull: return "QueueFull";
    case SessionStatus::RecoveryPending: return "RecoveryPending";
    case SessionStatus::SequenceExhausted: return "SequenceExhausted";
    case SessionStatus::CoreFailure: return "CoreFailure";
    }
    return {};
}

[[nodiscard]] bool valid_entry(const LibraryEntry& entry) noexcept {
    if (!is_valid_registration_scope(entry.scope) || !is_valid_registration_name(entry.name) ||
        !valid_entry_status(entry.status)) return false;
    const auto suffix = registration_scope_suffix(entry.scope);
    if (entry.key.size() != entry.name.size() + suffix.size() ||
        !entry.key.starts_with(entry.name) || !entry.key.ends_with(suffix)) return false;
    return entry.status == LibraryEntryStatus::Valid ?
        entry.controls.has_value() && is_valid_control_snapshot(*entry.controls) :
        !entry.controls.has_value();
}

[[nodiscard]] LibraryEntry copy_entry(const LibraryEntry& entry) {
    LibraryEntry result;
    result.key = entry.key;
    result.name = entry.name;
    result.scope = entry.scope;
    result.status = entry.status;
    result.reason = bounded(entry.reason);
    result.controls = entry.controls;
    return result;
}

[[nodiscard]] bool entry_less(const LibraryEntry& left, const LibraryEntry& right) noexcept {
    const auto names = compare_names(left.name, right.name);
    if (names != 0) return names < 0;
    if (left.scope != right.scope) return left.scope < right.scope;
    return left.key < right.key;
}

// Bounds precede every addition. Storage counts invalid payload rows separately
// from ambiguous rows; invalid names are candidates omitted from the row list.
[[nodiscard]] bool valid_complete_catalog(const LibraryCatalog& catalog) noexcept {
    if (!valid_catalog_status(catalog.status) || !catalog.complete() ||
        catalog.entries.size() > kRegistrationLibraryMaxEntries ||
        catalog.candidate_count > kRegistrationLibraryMaxEntries ||
        catalog.invalid_name_count > kRegistrationLibraryMaxEntries ||
        catalog.invalid_entry_count > kRegistrationLibraryMaxEntries ||
        catalog.ambiguous_entry_count > kRegistrationLibraryMaxEntries ||
        catalog.directory_items > kRegistrationLibraryMaxDirectoryItems) return false;
    if (catalog.candidate_count != catalog.entries.size() + catalog.invalid_name_count ||
        catalog.candidate_count > catalog.directory_items) return false;
    if (catalog.status == LibraryCatalogStatus::Ready && catalog.entries.empty()) return false;
    if (catalog.status == LibraryCatalogStatus::Empty && !catalog.entries.empty()) return false;
    if (catalog.status == LibraryCatalogStatus::MissingDirectory &&
        (!catalog.entries.empty() || catalog.directory_items != 0 || catalog.candidate_count != 0)) return false;

    std::size_t invalid = 0;
    std::size_t ambiguous = 0;
    for (std::size_t index = 0; index < catalog.entries.size(); ++index) {
        const auto& entry = catalog.entries[index];
        if (!valid_entry(entry)) return false;
        if (index != 0) {
            const auto& previous = catalog.entries[index - 1];
            if (!entry_less(previous, entry)) return false;
            if (previous.scope == entry.scope && compare_names(previous.name, entry.name) == 0 &&
                (previous.status != LibraryEntryStatus::Ambiguous ||
                 entry.status != LibraryEntryStatus::Ambiguous)) return false;
        }
        if (entry.status == LibraryEntryStatus::Ambiguous) ++ambiguous;
        else if (entry.status != LibraryEntryStatus::Valid) ++invalid;
    }
    return invalid == catalog.invalid_entry_count && ambiguous == catalog.ambiguous_entry_count;
}

[[nodiscard]] bool same_snapshot(const SessionSnapshot& left, const SessionSnapshot& right) noexcept {
    return left.controls == right.controls &&
        std::bit_cast<std::uint64_t>(left.controls.expression) ==
            std::bit_cast<std::uint64_t>(right.controls.expression) &&
        left.held_keys == right.held_keys && left.held_pedals == right.held_pedals &&
        left.frame_clock == right.frame_clock &&
        std::bit_cast<std::uint64_t>(left.sample_rate) == std::bit_cast<std::uint64_t>(right.sample_rate) &&
        std::bit_cast<std::uint32_t>(left.peak) == std::bit_cast<std::uint32_t>(right.peak) &&
        left.prepared == right.prepared && left.running == right.running &&
        left.publication_revision == right.publication_revision &&
        left.resolved_sequence == right.resolved_sequence &&
        left.last_applied_sequence == right.last_applied_sequence &&
        left.recovery_count == right.recovery_count && left.queue_overflows == right.queue_overflows &&
        left.rejected_commands == right.rejected_commands && left.discarded_commands == right.discarded_commands &&
        left.fault_flags == right.fault_flags && left.last_core_status == right.last_core_status;
}

[[nodiscard]] bool valid_snapshot(const SessionSnapshot& snapshot,
                                const std::optional<SessionSnapshot>& previous) noexcept {
    constexpr auto known_faults = static_cast<std::uint32_t>(SessionFault::QueueOverflow) |
        static_cast<std::uint32_t>(SessionFault::RejectedCommand) |
        static_cast<std::uint32_t>(SessionFault::SequenceExhausted) |
        static_cast<std::uint32_t>(SessionFault::RenderRejected) |
        static_cast<std::uint32_t>(SessionFault::CoreFailure);
    if (!is_valid_control_snapshot(snapshot.controls) ||
        (snapshot.publication_revision & 1U) != 0 ||
        (snapshot.prepared && snapshot.publication_revision == 0) ||
        (snapshot.running && !snapshot.prepared) ||
        snapshot.last_applied_sequence > snapshot.resolved_sequence ||
        !std::isfinite(snapshot.peak) || snapshot.peak < 0.0F ||
        (snapshot.prepared ? !is_supported_sample_rate(snapshot.sample_rate) : snapshot.sample_rate != 0.0) ||
        (snapshot.fault_flags & ~known_faults) != 0 ||
        snapshot.last_core_status > Status::TimelineOverflow) return false;
    if (!previous) return true;
    if (snapshot.publication_revision == previous->publication_revision) return same_snapshot(snapshot, *previous);
    return snapshot.publication_revision > previous->publication_revision &&
        snapshot.resolved_sequence >= previous->resolved_sequence &&
        snapshot.last_applied_sequence >= previous->last_applied_sequence &&
        snapshot.recovery_count >= previous->recovery_count &&
        snapshot.queue_overflows >= previous->queue_overflows &&
        snapshot.rejected_commands >= previous->rejected_commands &&
        snapshot.discarded_commands >= previous->discarded_commands &&
        (snapshot.fault_flags & previous->fault_flags) == previous->fault_flags;
}

} // namespace

class LibraryModel::Impl {
public:
    explicit Impl(LibraryModelLimits limits) : limits_(limits) {}

    enum class BasisPhase { Unsubmitted, Awaiting, Proved, Invalid };
    struct Guards {
        std::uint64_t recovery{};
        std::uint64_t rejected{};
        std::uint64_t discarded{};
        std::uint64_t failures{};
        [[nodiscard]] bool operator==(const Guards&) const noexcept = default;
    };
    struct Basis {
        BasisPhase phase{BasisPhase::Invalid};
        std::uint64_t revision{};
        ControlSnapshot expected{};
        std::uint64_t sequence{};
        std::uint64_t publication{};
        std::uint64_t before_resolved{};
        Guards guards{};
        bool original_observation_valid{false};
        bool submission_reported{false};
    };
    struct Operation {
        LibraryOperationView view;
        ControlSnapshot expected{};
        std::uint64_t desired_revision{};
        Basis original_basis;
        Guards guards;
        std::uint64_t started{};
        std::uint64_t deadline{};
        std::uint64_t refresh_generation{};
        bool effect_issued{false};
        bool authorized{false};
        bool result_received{false};
    };
    struct Reference {
        LibraryCurrentReferenceView view;
        ControlSnapshot baseline{};
        // Scans already requested before a Save completed cannot newly assert
        // that its just-committed entry is missing. Its compound scan can.
        std::uint64_t missing_generation_floor{};
    };
    struct CatalogRequest {
        std::uint64_t generation{};
        bool for_save{false};
    };

    [[nodiscard]] LibraryView view() const {
        auto result = state_;
        result.controls_pending = pending_controls();
        if (const auto* entry = selected_entry()) result.selected_preview = *entry;
        if (operation_) result.operation = operation_->view;
        if (reference_) {
            result.current_reference = reference_->view;
            if (actual_) result.current_reference->modified = !registration_controls_equal(
                reference_->view.scope, actual_->controls, reference_->baseline);
        }
        return result;
    }

    [[nodiscard]] bool active() const noexcept {
        return operation_ && operation_->view.phase != LibraryOperationPhase::Finished;
    }

    [[nodiscard]] bool pending_controls() const noexcept {
        return basis_ && (basis_->phase == BasisPhase::Unsubmitted || basis_->phase == BasisPhase::Awaiting);
    }

    void action(LibraryOutcome outcome, std::string_view reason) {
        state_.action_outcome = outcome;
        state_.action_reason = bounded(reason);
    }

    [[nodiscard]] LibraryRequestResult answer(LibraryOutcome outcome, std::string_view reason) {
        auto message = bounded(reason);
        action(outcome, message);
        return {outcome, std::move(message), std::nullopt};
    }

    void finish(LibraryOutcome outcome, std::string_view reason) {
        if (!active() || operation_->authorized) return;
        operation_->view.phase = LibraryOperationPhase::Finished;
        operation_->view.outcome = outcome;
        operation_->view.reason = bounded(reason);
    }

    void invalidate_basis(bool include_proved = false) {
        if (basis_ && (include_proved || pending_controls())) basis_->phase = BasisPhase::Invalid;
        if (!pending_controls() && actual_) desired_ = actual_->controls;
    }

    void exhausted(std::string_view reason) {
        state_.mutations_exhausted = true;
        finish(LibraryOutcome::Exhausted, reason);
        invalidate_basis();
        action(LibraryOutcome::Exhausted, reason);
    }

    [[nodiscard]] bool available(std::uint64_t counter, std::uint64_t limit, std::string_view reason) {
        if (counter < limit) return true;
        exhausted(reason);
        return false;
    }

    [[nodiscard]] Guards guards() const noexcept {
        if (!actual_) return {0, 0, 0, failure_revision_};
        return {actual_->recovery_count, actual_->rejected_commands,
                actual_->discarded_commands, failure_revision_};
    }

    [[nodiscard]] bool counters_available() const noexcept {
        return actual_ && actual_->recovery_count != kMaximum &&
            actual_->rejected_commands != kMaximum && actual_->discarded_commands != kMaximum;
    }

    [[nodiscard]] bool guards_match(const Guards& captured) const noexcept {
        return counters_available() && captured == guards();
    }

    [[nodiscard]] const LibraryEntry* selected_entry() const noexcept {
        if (!state_.selected_key) return nullptr;
        const auto found = std::find_if(state_.catalog.entries.begin(), state_.catalog.entries.end(),
            [this](const LibraryEntry& entry) { return entry.key == *state_.selected_key; });
        return found == state_.catalog.entries.end() ? nullptr : &*found;
    }

    [[nodiscard]] bool contains_key(std::string_view key) const noexcept {
        return std::any_of(state_.catalog.entries.begin(), state_.catalog.entries.end(),
            [key](const LibraryEntry& entry) { return entry.key == key; });
    }

    [[nodiscard]] std::optional<LibraryRefreshIntent> request_refresh() {
        if (!available(catalog_generation_, limits_.catalog_generations,
                       "Catalog generations are exhausted")) return std::nullopt;
        ++catalog_generation_;
        catalog_request_ = CatalogRequest{catalog_generation_, false};
        state_.catalog_stale = true;
        action(LibraryOutcome::Accepted, "Refreshing the library");
        return LibraryRefreshIntent{catalog_generation_};
    }

    [[nodiscard]] bool publish_catalog(const LibraryCatalog& catalog, std::uint64_t generation,
                                       bool post_save = false) {
        if (!valid_catalog_status(catalog.status) ||
            (catalog.complete() && !valid_complete_catalog(catalog))) {
            state_.last_scan_status = LibraryCatalogStatus::DirectoryUnavailable;
            state_.last_scan_reason = "Malformed library catalog result";
            state_.catalog_stale = true;
            return false;
        }
        if (!catalog.complete()) {
            state_.last_scan_status = catalog.status;
            state_.last_scan_reason = bounded(catalog.reason);
            state_.catalog_stale = true;
            return false;
        }

        LibraryCatalog admitted;
        admitted.generation = generation;
        admitted.status = catalog.status;
        admitted.reason = bounded(catalog.reason);
        admitted.directory_items = catalog.directory_items;
        admitted.candidate_count = catalog.candidate_count;
        admitted.invalid_name_count = catalog.invalid_name_count;
        admitted.invalid_entry_count = catalog.invalid_entry_count;
        admitted.ambiguous_entry_count = catalog.ambiguous_entry_count;
        admitted.entries.reserve(catalog.entries.size());
        for (const auto& entry : catalog.entries) admitted.entries.push_back(copy_entry(entry));
        state_.catalog = std::move(admitted);
        state_.last_scan_status = catalog.status;
        state_.last_scan_reason = bounded(catalog.reason);
        state_.catalog_stale = false;
        if (state_.selected_key && !contains_key(*state_.selected_key)) state_.selected_key.reset();
        if (!first_nonempty_catalog_ && !state_.catalog.entries.empty()) {
            first_nonempty_catalog_ = true;
            if (!state_.selected_key) state_.selected_key = state_.catalog.entries.front().key;
        }
        if (reference_ && (post_save || generation > reference_->missing_generation_floor)) {
            reference_->view.missing = !contains_key(reference_->view.key);
        }
        return true;
    }

    [[nodiscard]] bool replace_catalog(const LibraryCatalog& catalog) {
        if (!catalog_request_ || catalog_request_->for_save || catalog.generation == 0 ||
            catalog.generation != catalog_request_->generation) {
            action(LibraryOutcome::StaleResult, "No matching outstanding library refresh");
            return false;
        }
        catalog_request_.reset();
        const bool admitted = publish_catalog(catalog, catalog.generation);
        action(admitted ? LibraryOutcome::Accepted : LibraryOutcome::CatalogUnavailable,
               admitted ? "Library refreshed" : std::string_view(state_.last_scan_reason));
        return admitted;
    }

    [[nodiscard]] bool select(std::string_view key) {
        if (!contains_key(key)) {
            action(LibraryOutcome::NoSelection, "The requested library entry is not in the catalog");
            return false;
        }
        state_.selected_key = std::string(key);
        action(LibraryOutcome::Accepted, "Entry selected");
        return true;
    }

    [[nodiscard]] bool select_relative(int delta) {
        if (delta == 0) return true;
        if (state_.catalog.entries.empty()) {
            action(LibraryOutcome::NoSelection, "The library has no rows to select");
            return false;
        }
        const auto* selected = selected_entry();
        std::size_t index = delta > 0 ? 0 : state_.catalog.entries.size() - 1;
        if (selected) {
            const auto current = static_cast<std::int64_t>(selected - state_.catalog.entries.data());
            const auto last = static_cast<std::int64_t>(state_.catalog.entries.size() - 1);
            index = static_cast<std::size_t>(std::clamp(current + static_cast<std::int64_t>(delta),
                                                       std::int64_t{0}, last));
        }
        return select(state_.catalog.entries[index].key);
    }

    [[nodiscard]] bool set_name(std::string_view draft) {
        if (!is_valid_registration_name_draft(draft)) {
            action(LibraryOutcome::InvalidInput, "Name draft contains invalid bytes or exceeds 48 bytes");
            return false;
        }
        state_.name_draft = std::string(draft);
        action(LibraryOutcome::Accepted, "Name draft updated");
        return true;
    }

    [[nodiscard]] bool set_save_scope(RegistrationScope scope) {
        if (!is_valid_registration_scope(scope)) {
            action(LibraryOutcome::InvalidInput, "Invalid registration scope");
            return false;
        }
        state_.save_scope = scope;
        action(LibraryOutcome::Accepted, "Save scope updated");
        return true;
    }

    void lifecycle(LibraryAudioTransition transition) {
        if (transition != LibraryAudioTransition::Stop && transition != LibraryAudioTransition::Start &&
            transition != LibraryAudioTransition::Prepare) {
            finish(LibraryOutcome::ProtocolError, "Unrecognized audio lifecycle transition");
            invalidate_basis(true);
            state_.observation_fresh = false;
            action(LibraryOutcome::ProtocolError, "Unrecognized audio lifecycle transition");
            return;
        }
        const bool prepare = transition == LibraryAudioTransition::Prepare;
        finish(LibraryOutcome::Cancelled, prepare ? "Audio preparation cancelled the operation" :
               "Audio lifecycle changed during the operation");
        invalidate_basis(prepare);
        state_.observation_fresh = false;
    }

    [[nodiscard]] bool admit_time(std::uint64_t now) {
        if (last_time_ && now < *last_time_) {
            state_.observation_fresh = false;
            return false;
        }
        last_time_ = now;
        if (active() && !operation_->authorized && now >= operation_->deadline) {
            finish(LibraryOutcome::Unconfirmed, "The two-second acknowledgment deadline expired");
        }
        return true;
    }

    [[nodiscard]] bool same_basis(const Basis& original) const noexcept {
        return basis_ && basis_->revision == original.revision && basis_->expected == original.expected &&
            basis_->sequence == original.sequence && basis_->publication == original.publication &&
            basis_->before_resolved == original.before_resolved && basis_->guards == original.guards &&
            basis_->original_observation_valid && original.original_observation_valid;
    }

    [[nodiscard]] bool proved_now(const Basis& basis) const noexcept {
        return actual_ && actual_->prepared && basis.phase == BasisPhase::Proved && basis.sequence != 0 &&
            actual_->publication_revision > basis.publication &&
            actual_->resolved_sequence >= basis.sequence && actual_->last_applied_sequence >= basis.sequence &&
            actual_->controls == basis.expected && desired_ && *desired_ == basis.expected &&
            desired_revision_ == basis.revision;
    }

    void establish_reference(LibraryReferenceOrigin origin) {
        Reference reference;
        reference.view.key = operation_->view.target_key;
        reference.view.name = operation_->view.target_name;
        reference.view.scope = operation_->view.target_scope;
        reference.view.origin = origin;
        reference.baseline = operation_->expected;
        if (origin == LibraryReferenceOrigin::AcknowledgedSave) {
            reference.missing_generation_floor = catalog_generation_;
        } else {
            reference.view.missing = !contains_key(reference.view.key);
        }
        reference_ = std::move(reference);
    }

    void progress_operation() {
        if (!active() || operation_->authorized) return;
        if (state_.mutations_exhausted) {
            finish(LibraryOutcome::Exhausted, "Named mutation tracking is exhausted");
        } else if (!actual_->prepared ||
                   (operation_->view.kind == LibraryOperationKind::Recall &&
                    (!actual_->running || !audio_enabled_))) {
            finish(LibraryOutcome::Cancelled, "Audio became unavailable during the operation");
        } else if (!guards_match(operation_->guards)) {
            finish(LibraryOutcome::Rejected, "Submission failure, rejection, discard or recovery changed");
        } else if (desired_revision_ != operation_->desired_revision || !desired_ ||
                   *desired_ != operation_->expected) {
            finish(LibraryOutcome::Superseded, "A newer control intention superseded the operation");
        } else if (!same_basis(operation_->original_basis) || basis_->phase == BasisPhase::Invalid) {
            finish(LibraryOutcome::Cancelled, "The original control acknowledgment basis is unavailable");
        } else if (proved_now(*basis_)) {
            if (operation_->view.kind == LibraryOperationKind::Recall) {
                establish_reference(LibraryReferenceOrigin::Recall);
                finish(LibraryOutcome::Applied, "Recall applied");
            } else if (operation_->view.phase == LibraryOperationPhase::AwaitingAcknowledgment) {
                operation_->view.phase = LibraryOperationPhase::ReadyToSave;
                operation_->view.reason = "Acknowledged controls are ready to save";
            }
        }
    }

    [[nodiscard]] bool receive(const LibraryObservation& observation) {
        audio_enabled_ = observation.audio_commands_enabled;
        state_.observation_fresh = false;
        if (!audio_enabled_ && active() && operation_->view.kind == LibraryOperationKind::Recall) {
            finish(LibraryOutcome::Cancelled, "Audio command dispatch was disabled");
        }
        if (!observation.snapshot || !valid_snapshot(*observation.snapshot, actual_)) return false;
        const auto& snapshot = *observation.snapshot;
        if (actual_) {
            if (actual_->prepared != snapshot.prepared ||
                (actual_->prepared && (actual_->sample_rate != snapshot.sample_rate ||
                                      snapshot.frame_clock < actual_->frame_clock))) {
                lifecycle(LibraryAudioTransition::Prepare);
            } else if (actual_->running != snapshot.running) {
                lifecycle(snapshot.running ? LibraryAudioTransition::Start : LibraryAudioTransition::Stop);
            }
        }
        actual_ = snapshot;
        state_.observation_fresh = true;

        if (active() && !operation_->authorized && !guards_match(operation_->guards)) {
            finish(LibraryOutcome::Rejected, "Submission failure, rejection, discard or recovery changed");
        }
        if (pending_controls() && basis_->original_observation_valid && !guards_match(basis_->guards)) {
            invalidate_basis();
        } else if (basis_ && basis_->phase == BasisPhase::Awaiting &&
                   snapshot.publication_revision > basis_->publication &&
                   snapshot.resolved_sequence >= basis_->sequence) {
            if (basis_->original_observation_valid && guards_match(basis_->guards) &&
                snapshot.last_applied_sequence >= basis_->sequence &&
                snapshot.controls == basis_->expected && desired_ && *desired_ == basis_->expected &&
                desired_revision_ == basis_->revision) {
                basis_->phase = BasisPhase::Proved;
            } else {
                invalidate_basis();
                finish(LibraryOutcome::Unconfirmed, "Resolved controls did not confirm the original control intention");
            }
        }
        if (basis_ && basis_->phase == BasisPhase::Proved && snapshot.controls != basis_->expected) {
            invalidate_basis(true);
            finish(LibraryOutcome::Cancelled, "The proved control copy changed before completion");
        }
        if (!pending_controls()) desired_ = snapshot.controls;
        progress_operation();
        return true;
    }

    [[nodiscard]] bool update(const LibraryObservation& observation, std::uint64_t now) {
        if (!admit_time(now)) return false;
        return receive(observation);
    }

    [[nodiscard]] Basis new_basis(const ControlSnapshot& desired) const noexcept {
        Basis basis;
        basis.phase = BasisPhase::Unsubmitted;
        basis.revision = desired_revision_;
        basis.expected = desired;
        basis.guards = guards();
        if (actual_) {
            basis.publication = actual_->publication_revision;
            basis.before_resolved = actual_->resolved_sequence;
        }
        basis.original_observation_valid = state_.observation_fresh && actual_ &&
            actual_->prepared && counters_available();
        return basis;
    }

    [[nodiscard]] std::optional<LibraryControlIntent> note_control_intent(
        const ControlSnapshot& desired, const LibraryObservation& observation) {
        if (!is_valid_control_snapshot(desired)) {
            action(LibraryOutcome::InvalidInput, "Invalid complete control intention");
            return std::nullopt;
        }
        if (state_.mutations_exhausted || !available(desired_revision_, limits_.desired_revisions,
                                                    "Desired control revisions are exhausted")) {
            action(LibraryOutcome::Exhausted, "Named mutation tracking is exhausted");
            return std::nullopt;
        }
        finish(LibraryOutcome::Superseded, "A newer control intention superseded the operation");
        (void)receive(observation);
        ++desired_revision_;
        desired_ = desired;
        basis_ = new_basis(desired);
        action(LibraryOutcome::Accepted, "Control intention recorded");
        return LibraryControlIntent{desired_revision_, desired};
    }

    [[nodiscard]] LibraryOutcome protocol_error(std::string_view reason, bool invalidate_current = true) {
        finish(LibraryOutcome::ProtocolError, reason);
        if (invalidate_current) invalidate_basis(true);
        action(LibraryOutcome::ProtocolError, reason);
        return LibraryOutcome::ProtocolError;
    }

    [[nodiscard]] LibraryOutcome submitted(const SubmitResult& result,
                                           const std::optional<LibraryControlIntent>& token) {
        const bool failed = result.status != SessionStatus::Ok;
        if (failed) {
            if (!available(failure_revision_, limits_.submission_failure_revisions,
                           "Submission failure revisions are exhausted")) return LibraryOutcome::Exhausted;
            ++failure_revision_;
        }
        const auto status_name = submit_status_name(result.status);
        if (status_name.empty() || (failed && result.sequence != 0) || (!failed && result.sequence == 0)) {
            return protocol_error("Malformed Session submission result");
        }
        const bool preserve_newer = !failed && token && token->desired_revision != 0 &&
            token->desired_revision < desired_revision_ && pending_controls();
        if (!failed) {
            if (result.sequence <= last_submitted_sequence_ ||
                (actual_ && result.sequence <= actual_->resolved_sequence)) {
                return protocol_error("Accepted Session sequences must be nonzero and increasing", !preserve_newer);
            }
            last_submitted_sequence_ = result.sequence;
        }
        if (token && (!basis_ || basis_->submission_reported ||
                      basis_->phase != BasisPhase::Unsubmitted || token->desired_revision == 0 ||
                      token->desired_revision != desired_revision_ || token->desired_revision != basis_->revision ||
                      token->expected_controls != basis_->expected ||
                      !is_valid_control_snapshot(token->expected_controls))) {
            // An old completion cannot roll a newer valid pending desired copy
            // back to the displayed controls. It still cannot certify a named
            // receipt or attach its sequence to either intention. Real failed
            // posts affect all current waits, regardless of token age.
            return protocol_error("Control submission token is stale, duplicate or mismatched", !preserve_newer);
        }
        if (token) basis_->submission_reported = true;
        if (failed) {
            std::string reason = "Session post failed: ";
            reason.append(status_name);
            finish(LibraryOutcome::Rejected, reason);
            invalidate_basis();
            action(LibraryOutcome::Rejected, reason);
            return LibraryOutcome::Rejected;
        }
        if (token) {
            if (result.sequence <= basis_->before_resolved) {
                return protocol_error("Control sequence predates its original observation");
            }
            basis_->sequence = result.sequence;
            basis_->phase = BasisPhase::Awaiting;
            if (active() && operation_->view.kind == LibraryOperationKind::Recall &&
                operation_->desired_revision == token->desired_revision) {
                operation_->original_basis = *basis_;
                operation_->view.submitted_sequence = result.sequence;
                operation_->view.phase = LibraryOperationPhase::AwaitingAcknowledgment;
                operation_->view.reason = "Recall queued; awaiting acknowledgment";
            }
        }
        action(LibraryOutcome::Accepted, "Session command accepted; application is not yet established");
        return LibraryOutcome::Accepted;
    }

    void replace_preview(const LibraryEntry& entry) {
        const auto found = std::find_if(state_.catalog.entries.begin(), state_.catalog.entries.end(),
            [&entry](const LibraryEntry& row) { return row.key == entry.key; });
        if (found == state_.catalog.entries.end()) return;
        *found = copy_entry(entry);
        state_.catalog.invalid_entry_count = 0;
        state_.catalog.ambiguous_entry_count = 0;
        for (const auto& row : state_.catalog.entries) {
            if (row.status == LibraryEntryStatus::Ambiguous) ++state_.catalog.ambiguous_entry_count;
            else if (row.status != LibraryEntryStatus::Valid) ++state_.catalog.invalid_entry_count;
        }
    }

    [[nodiscard]] bool request_time_valid(std::uint64_t now) const noexcept {
        return (!last_time_ || now >= *last_time_) && now <= kMaximum - kLibraryAcknowledgmentWaitMs;
    }

    [[nodiscard]] LibraryRequestResult request_recall(const LibraryEntry& entry,
        const ControlSnapshot& latest_desired, const LibraryObservation& observation, std::uint64_t now) {
        if (!is_valid_control_snapshot(latest_desired)) {
            return answer(LibraryOutcome::InvalidInput, "Invalid latest desired controls");
        }
        if (!request_time_valid(now)) {
            state_.observation_fresh = false;
            return answer(LibraryOutcome::InvalidInput, "Recall time regressed or its deadline would overflow");
        }
        (void)update(observation, now);
        if (active()) return answer(LibraryOutcome::Busy, "A named operation is already in progress");
        if (state_.mutations_exhausted) return answer(LibraryOutcome::Exhausted, "Named mutation tracking is exhausted");
        if (state_.catalog_stale || !state_.catalog.complete()) {
            return answer(LibraryOutcome::CatalogUnavailable, "Refresh the library before recalling an entry");
        }
        const auto* selected = selected_entry();
        if (!selected) return answer(LibraryOutcome::NoSelection, "Select a library entry to recall");
        if (!valid_entry(entry) || entry.key != selected->key || entry.name != selected->name ||
            entry.scope != selected->scope) {
            return answer(LibraryOutcome::InvalidEntry, "Revalidation does not identify the exact selected entry");
        }
        if (selected->status == LibraryEntryStatus::Ambiguous) {
            return answer(LibraryOutcome::InvalidEntry, "Refresh must resolve this entry's case-insensitive ambiguity");
        }
        if (!entry.valid()) {
            replace_preview(entry);
            return answer(LibraryOutcome::InvalidEntry, entry.reason.empty() ?
                          "The selected entry is unavailable or invalid" : std::string_view(entry.reason));
        }
        const bool changed = !selected->valid() || selected->controls != entry.controls;
        replace_preview(entry);
        if (changed) return answer(LibraryOutcome::EntryChanged, "Entry changed; review the preview and Recall again");
        if (!state_.observation_fresh) return answer(LibraryOutcome::SnapshotUnavailable, "A fresh Session snapshot is unavailable");
        if (!actual_->prepared || !actual_->running || !audio_enabled_) {
            return answer(LibraryOutcome::NoAudio, "Start audio to recall; no controls were submitted");
        }
        if (!counters_available()) return answer(LibraryOutcome::Exhausted, "Saturated Session counters cannot prove a recall");
        ControlSnapshot candidate;
        if (!merge_registration_controls(entry.scope, *entry.controls, latest_desired, candidate)) {
            return answer(LibraryOutcome::InvalidInput, "Could not form a valid complete recall candidate");
        }
        if (!available(operation_id_, limits_.operation_ids, "Named operation IDs are exhausted") ||
            !available(desired_revision_, limits_.desired_revisions, "Desired control revisions are exhausted")) {
            return answer(LibraryOutcome::Exhausted, state_.action_reason);
        }
        ++operation_id_;
        ++desired_revision_;
        desired_ = candidate;
        basis_ = new_basis(candidate);
        Operation operation;
        operation.view = {operation_id_, LibraryOperationKind::Recall, LibraryOperationPhase::AwaitingSubmission,
            entry.key, entry.name, entry.scope, 0, LibraryOutcome::Accepted, "Recall awaits its one submission"};
        operation.expected = candidate;
        operation.desired_revision = desired_revision_;
        operation.original_basis = *basis_;
        operation.guards = guards();
        operation.started = now;
        operation.deadline = now + kLibraryAcknowledgmentWaitMs;
        operation_ = std::move(operation);
        auto result = answer(LibraryOutcome::Accepted, "Recall accepted for one control submission");
        result.recall = LibraryRecallIntent{operation_id_, LibraryControlIntent{desired_revision_, candidate}};
        return result;
    }

    [[nodiscard]] LibraryRequestResult request_save_new(const LibraryObservation& observation, std::uint64_t now) {
        if (!request_time_valid(now)) {
            state_.observation_fresh = false;
            return answer(LibraryOutcome::InvalidInput, "Save time regressed or its deadline would overflow");
        }
        (void)update(observation, now);
        if (active()) return answer(LibraryOutcome::Busy, "A named operation is already in progress");
        if (state_.mutations_exhausted) return answer(LibraryOutcome::Exhausted, "Named mutation tracking is exhausted");
        if (state_.catalog_stale || !state_.catalog.complete()) {
            return answer(LibraryOutcome::CatalogUnavailable, "Refresh the library before saving a new entry");
        }
        if (!is_valid_registration_name(state_.name_draft) || !is_valid_registration_scope(state_.save_scope)) {
            return answer(LibraryOutcome::InvalidInput, "Choose a valid portable name and save scope");
        }
        if (state_.catalog.candidate_count >= kRegistrationLibraryMaxEntries ||
            state_.catalog.directory_items >= kRegistrationLibraryMaxDirectoryItems) {
            return answer(LibraryOutcome::CatalogUnavailable, "Library has no capacity for another entry");
        }
        for (const auto& entry : state_.catalog.entries) {
            if (entry.scope == state_.save_scope && compare_names(entry.name, state_.name_draft) == 0) {
                return answer(LibraryOutcome::InvalidInput, "An entry with this name and scope already exists");
            }
        }
        if (!state_.observation_fresh) return answer(LibraryOutcome::SnapshotUnavailable, "A fresh Session snapshot is unavailable");
        if (!actual_->prepared) return answer(LibraryOutcome::NoAudio, "Prepared audio controls are required to save");
        if (!counters_available()) return answer(LibraryOutcome::Exhausted, "Saturated Session counters cannot authorize a save");
        if (!basis_ || !basis_->original_observation_valid || basis_->sequence == 0 ||
            !desired_ || *desired_ != basis_->expected || desired_revision_ != basis_->revision ||
            (basis_->phase != BasisPhase::Awaiting && basis_->phase != BasisPhase::Proved) ||
            (basis_->phase == BasisPhase::Awaiting && (!actual_->running || !guards_match(basis_->guards))) ||
            (basis_->phase == BasisPhase::Proved && !proved_now(*basis_))) {
            return answer(LibraryOutcome::NoAcknowledgedControls, "No valid submitted or proved control basis is available");
        }
        if (!available(operation_id_, limits_.operation_ids, "Named operation IDs are exhausted")) {
            return answer(LibraryOutcome::Exhausted, state_.action_reason);
        }
        ++operation_id_;
        Operation operation;
        operation.view.operation_id = operation_id_;
        operation.view.kind = LibraryOperationKind::SaveNew;
        operation.view.phase = basis_->phase == BasisPhase::Proved ? LibraryOperationPhase::ReadyToSave :
                                                                  LibraryOperationPhase::AwaitingAcknowledgment;
        operation.view.target_name = state_.name_draft;
        operation.view.target_scope = state_.save_scope;
        operation.view.target_key = state_.name_draft + std::string(registration_scope_suffix(state_.save_scope));
        operation.view.submitted_sequence = basis_->sequence;
        operation.view.outcome = LibraryOutcome::Accepted;
        operation.view.reason = basis_->phase == BasisPhase::Proved ? "Acknowledged controls are ready to save" :
                                                                   "Save awaits the original control acknowledgment";
        operation.expected = basis_->expected;
        operation.desired_revision = desired_revision_;
        operation.original_basis = *basis_;
        operation.guards = guards();
        operation.started = now;
        operation.deadline = now + kLibraryAcknowledgmentWaitMs;
        operation_ = std::move(operation);
        return answer(LibraryOutcome::Accepted, operation_->view.reason);
    }

    [[nodiscard]] bool fresh_save_guard() {
        if (!active()) return false;
        if (!state_.observation_fresh) {
            finish(LibraryOutcome::SnapshotUnavailable, "A fresh Session snapshot is required to authorize storage");
            return false;
        }
        progress_operation();
        if (!active()) return false;
        if (!same_basis(operation_->original_basis) || !basis_ || !proved_now(*basis_)) {
            finish(LibraryOutcome::Cancelled, "The original acknowledged controls no longer authorize storage");
            return false;
        }
        return true;
    }

    [[nodiscard]] std::optional<LibrarySaveIntent> take_save_intent(
        const LibraryObservation& observation, std::uint64_t now) {
        if (!operation_ || operation_->view.kind != LibraryOperationKind::SaveNew ||
            operation_->effect_issued || !active()) {
            action(LibraryOutcome::StaleResult, "No unconsumed Save new effect is available");
            return std::nullopt;
        }
        if (!admit_time(now)) {
            finish(LibraryOutcome::InvalidInput, "Save time regressed");
        } else {
            (void)receive(observation);
        }
        if (!active()) {
            action(operation_->view.outcome, operation_->view.reason);
            return std::nullopt;
        }
        if (operation_->view.phase != LibraryOperationPhase::ReadyToSave) return std::nullopt;
        if (!fresh_save_guard()) {
            action(operation_->view.outcome, operation_->view.reason);
            return std::nullopt;
        }
        if (!available(catalog_generation_, limits_.catalog_generations, "Catalog generations are exhausted")) {
            return std::nullopt;
        }
        ++catalog_generation_;
        catalog_request_ = CatalogRequest{catalog_generation_, true};
        operation_->refresh_generation = catalog_generation_;
        operation_->effect_issued = true;
        operation_->view.phase = LibraryOperationPhase::Saving;
        operation_->view.reason = "Storage effect issued; fresh final authorization is still required";
        action(LibraryOutcome::Accepted, operation_->view.reason);
        return LibrarySaveIntent{operation_->view.operation_id, operation_->view.target_key,
            operation_->view.target_name, operation_->view.target_scope, operation_->expected};
    }

    [[nodiscard]] LibraryCommitAuthorization authorize_save(std::uint64_t id,
        const LibraryObservation& observation, std::uint64_t now) {
        if (!operation_ || id == 0 || operation_->view.operation_id != id ||
            operation_->view.kind != LibraryOperationKind::SaveNew || !operation_->effect_issued ||
            operation_->result_received) {
            return {false, "No matching Save new storage effect"};
        }
        if (operation_->authorized) return {false, "This save has already consumed its commit authorization"};
        if (!active()) return {false, operation_->view.reason};
        if (operation_->view.phase != LibraryOperationPhase::Saving) {
            return {false, "Save new is not awaiting final storage authorization"};
        }
        if (!admit_time(now)) finish(LibraryOutcome::InvalidInput, "Save authorization time regressed");
        else (void)receive(observation);
        if (!fresh_save_guard()) {
            action(operation_->view.outcome, operation_->view.reason);
            return {false, operation_->view.reason};
        }
        operation_->authorized = true;
        operation_->view.reason = "Commit authorized from the fresh acknowledged control copy";
        action(LibraryOutcome::Accepted, operation_->view.reason);
        return {true, {}};
    }

    [[nodiscard]] LibraryOutcome complete_save(std::uint64_t id, const LibrarySaveResult& result) {
        if (!operation_ || id == 0 || operation_->view.operation_id != id ||
            operation_->view.kind != LibraryOperationKind::SaveNew || !operation_->effect_issued ||
            operation_->result_received) {
            action(LibraryOutcome::StaleResult, "No matching unfinished Save new storage result");
            return LibraryOutcome::StaleResult;
        }
        auto& operation = *operation_;
        operation.result_received = true;
        const bool owns_refresh = catalog_request_ && catalog_request_->for_save &&
            catalog_request_->generation == operation.refresh_generation;
        if (owns_refresh) catalog_request_.reset();
        if (!valid_save_status(result.status)) {
            operation.view.phase = LibraryOperationPhase::Finished;
            operation.view.outcome = LibraryOutcome::ProtocolError;
            operation.view.reason = "Unrecognized storage result status";
        } else if (!result.committed()) {
            if (!(result.status == LibrarySaveStatus::NotAuthorized &&
                  operation.view.phase == LibraryOperationPhase::Finished && !operation.authorized)) {
                operation.view.phase = LibraryOperationPhase::Finished;
                operation.view.outcome = LibraryOutcome::SaveFailed;
                operation.view.reason = result.reason.empty() ? "Save new failed before publication" : bounded(result.reason);
            }
        } else {
            bool warning = result.status == LibrarySaveStatus::SavedWithWarning;
            std::string reason;
            const bool metadata_matches = result.committed_entry && valid_entry(*result.committed_entry) &&
                result.committed_entry->valid() && result.committed_entry->key == operation.view.target_key &&
                result.committed_entry->name == operation.view.target_name &&
                result.committed_entry->scope == operation.view.target_scope &&
                *result.committed_entry->controls == operation.expected;
            if (!operation.authorized || !metadata_matches) {
                warning = true;
                reason = "Saved; inconsistent committed-entry metadata or missing commit authorization";
            } else {
                establish_reference(LibraryReferenceOrigin::AcknowledgedSave);
            }

            const auto& refreshed = result.refreshed_catalog;
            const bool generation_matches = refreshed && (refreshed->generation == 0 ||
                                                          refreshed->generation == operation.refresh_generation);
            const bool complete_refresh = generation_matches && valid_complete_catalog(*refreshed);
            bool refreshed_entry_matches = false;
            if (complete_refresh) {
                const auto found = std::find_if(refreshed->entries.begin(), refreshed->entries.end(),
                    [&operation](const LibraryEntry& entry) { return entry.key == operation.view.target_key; });
                refreshed_entry_matches = found != refreshed->entries.end() && found->valid() &&
                    *found->controls == operation.expected;
            }
            if (!complete_refresh || !refreshed_entry_matches) {
                warning = true;
                append_reason(reason, !complete_refresh ? "Saved; post-save refresh is absent, failed or malformed" :
                              "Saved; the committed entry changed or disappeared during refresh");
            }
            if (owns_refresh) {
                if (generation_matches) {
                    (void)publish_catalog(*refreshed, operation.refresh_generation, true);
                    if (complete_refresh && contains_key(operation.view.target_key)) {
                        state_.selected_key = operation.view.target_key;
                    }
                } else {
                    state_.catalog_stale = true;
                    state_.last_scan_status = LibraryCatalogStatus::DirectoryUnavailable;
                    state_.last_scan_reason = "Missing or mismatched post-save refresh result";
                }
            }
            append_reason(reason, result.reason);
            if (reason.empty()) reason = warning ? "Saved with warning" : "Saved";
            operation.view.phase = LibraryOperationPhase::Finished;
            operation.view.outcome = warning ? LibraryOutcome::SavedWithWarning : LibraryOutcome::Saved;
            operation.view.reason = bounded(reason);
        }
        action(operation.view.outcome, operation.view.reason);
        return operation.view.outcome;
    }

private:
    LibraryModelLimits limits_;
    LibraryView state_;
    std::optional<SessionSnapshot> actual_;
    std::optional<ControlSnapshot> desired_;
    std::optional<Basis> basis_;
    std::optional<Operation> operation_;
    std::optional<Reference> reference_;
    std::optional<CatalogRequest> catalog_request_;
    std::optional<std::uint64_t> last_time_;
    std::uint64_t operation_id_{};
    std::uint64_t desired_revision_{};
    std::uint64_t failure_revision_{};
    std::uint64_t catalog_generation_{};
    std::uint64_t last_submitted_sequence_{};
    bool first_nonempty_catalog_{false};
    bool audio_enabled_{false};
};

LibraryModel::LibraryModel(LibraryModelLimits limits) : impl_(std::make_unique<Impl>(limits)) {}
LibraryModel::~LibraryModel() = default;

LibraryView LibraryModel::view() const { return impl_->view(); }
std::optional<LibraryRefreshIntent> LibraryModel::request_refresh() { return impl_->request_refresh(); }
bool LibraryModel::replace_catalog(const LibraryCatalog& catalog) { return impl_->replace_catalog(catalog); }
bool LibraryModel::select(std::string_view key) { return impl_->select(key); }
bool LibraryModel::select_relative(int delta) { return impl_->select_relative(delta); }
bool LibraryModel::set_name(std::string_view draft) { return impl_->set_name(draft); }
bool LibraryModel::set_save_scope(RegistrationScope scope) { return impl_->set_save_scope(scope); }

std::optional<LibraryControlIntent> LibraryModel::note_control_intent(
    const ControlSnapshot& desired, const LibraryObservation& observation) {
    return impl_->note_control_intent(desired, observation);
}

LibraryOutcome LibraryModel::submitted(const SubmitResult& result,
                                      const std::optional<LibraryControlIntent>& token) {
    return impl_->submitted(result, token);
}

void LibraryModel::observe(const LibraryObservation& observation, std::uint64_t now) {
    (void)impl_->update(observation, now);
}

LibraryRequestResult LibraryModel::request_recall(const LibraryEntry& entry,
    const ControlSnapshot& latest_desired, const LibraryObservation& observation, std::uint64_t now) {
    return impl_->request_recall(entry, latest_desired, observation, now);
}

LibraryRequestResult LibraryModel::request_save_new(const LibraryObservation& observation, std::uint64_t now) {
    return impl_->request_save_new(observation, now);
}

std::optional<LibrarySaveIntent> LibraryModel::take_save_intent(
    const LibraryObservation& observation, std::uint64_t now) {
    return impl_->take_save_intent(observation, now);
}

LibraryCommitAuthorization LibraryModel::authorize_save(std::uint64_t id,
    const LibraryObservation& observation, std::uint64_t now) {
    return impl_->authorize_save(id, observation, now);
}

LibraryOutcome LibraryModel::complete_save(std::uint64_t id, const LibrarySaveResult& result) {
    return impl_->complete_save(id, result);
}

void LibraryModel::audio_lifecycle_changed(LibraryAudioTransition transition) { impl_->lifecycle(transition); }

} // namespace hammond::standalone
