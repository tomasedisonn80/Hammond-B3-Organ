#include "hammond/ContactBank.h"

#include <algorithm>
#include <cmath>

namespace hammond {
namespace {

[[nodiscard]] bool valid_duration(double seconds) noexcept {
    return std::isfinite(seconds) && seconds >= kMinContactTravelSeconds &&
           seconds <= kMaxContactTravelSeconds;
}

} // namespace

ContactProfile make_ideal_contact_profile() noexcept {
    return ContactProfile{};
}

ContactProfile make_nominal_contact_profile() noexcept {
    ContactProfile profile;
    profile.mode = ContactMode::LinearTravel;
    return profile;
}

bool is_valid_contact_profile(const ContactProfile& profile) noexcept {
    if (!is_valid_contact_mode(profile.mode)) {
        return false;
    }
    for (const auto& manual : profile.keys) {
        for (const auto& key : manual) {
            if (!valid_duration(key.press_seconds) || !valid_duration(key.release_seconds)) {
                return false;
            }
            for (std::size_t contact = 0; contact < kDrawbarCount; ++contact) {
                const double on = key.on_thresholds[contact];
                const double off = key.off_thresholds[contact];
                if (!std::isfinite(on) || !std::isfinite(off) || off < 0.0 ||
                    off >= on || on > 1.0) {
                    return false;
                }
            }
        }
    }
    return true;
}

Status ContactBank::prepare(const ContactProfile& profile, double sample_rate) noexcept {
    if (!is_supported_sample_rate(sample_rate)) {
        return Status::InvalidSpec;
    }
    if (!is_valid_contact_profile(profile)) {
        return Status::InvalidProfile;
    }

    std::array<std::array<Key, kManualKeyCount>, kManualCount> candidate{};
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        for (std::size_t key = 0; key < kManualKeyCount; ++key) {
            auto& prepared = candidate[manual][key];
            prepared.profile = profile.keys[manual][key];
            prepared.press_step = 1.0 / (sample_rate * prepared.profile.press_seconds);
            prepared.release_step = 1.0 / (sample_rate * prepared.profile.release_seconds);
        }
    }
    keys_ = candidate;
    mode_ = profile.mode;
    prepared_ = true;
    return Status::Ok;
}

bool ContactBank::set_key_target(Manual manual, std::uint32_t midi_note, bool down) noexcept {
    return set_position_target(manual, midi_note, down ? 1.0 : 0.0);
}

bool ContactBank::set_position_target(Manual manual, std::uint32_t midi_note,
                                      double target) noexcept {
    if (!std::isfinite(target) || target < 0.0 || target > 1.0 ||
        (mode_ == ContactMode::Ideal && target != 0.0 && target != 1.0)) {
        return false;
    }
    Key* key = checked_key(manual, midi_note);
    if (key == nullptr) {
        return false;
    }
    // Canonicalize negative zero. An identical target is an accepted no-op,
    // preserving the segment origin as well as physical contact histories.
    target = target == 0.0 ? 0.0 : target;
    if (key->state.target == target) {
        return true;
    }
    key->state.target = target;
    key->travel_origin = key->state.position;
    key->travel_frames = 0;
    if (mode_ == ContactMode::Ideal) {
        key->state.position = target;
        key->state.closed.fill(target != 0.0);
    }
    return true;
}

bool ContactBank::panic_manual(Manual manual) noexcept {
    if (!prepared_ || !is_valid_manual(manual)) {
        return false;
    }
    for (auto& key : keys_[static_cast<std::size_t>(manual)]) {
        key.state = ContactKeySnapshot{};
        key.travel_origin = 0.0;
        key.travel_frames = 0;
    }
    return true;
}

bool ContactBank::advance_frame() noexcept {
    if (!prepared_ || mode_ == ContactMode::Ideal) {
        return false;
    }
    bool changed = false;
    for (auto& manual : keys_) {
        for (auto& key : manual) {
            if (key.state.position == key.state.target) {
                continue;
            }
            // Duration <= 1 s, rate <= 96 kHz, and travel distance <= 1 bound
            // every segment below 96,002 increments. Compute from its fixed
            // origin instead of accumulating a per-frame rounding error.
            ++key.travel_frames;
            const double elapsed_frames = static_cast<double>(key.travel_frames);
            if (key.state.target > key.travel_origin) {
                key.state.position = std::min(key.state.target,
                    key.travel_origin + elapsed_frames * key.press_step);
            } else {
                key.state.position = std::max(key.state.target,
                    key.travel_origin - elapsed_frames * key.release_step);
            }
            for (std::size_t contact = 0; contact < kDrawbarCount; ++contact) {
                const bool previous = key.state.closed[contact];
                if (previous) {
                    if (key.state.position <= key.profile.off_thresholds[contact]) {
                        key.state.closed[contact] = false;
                    }
                } else if (key.state.position >= key.profile.on_thresholds[contact]) {
                    key.state.closed[contact] = true;
                }
                changed = changed || previous != key.state.closed[contact];
            }
        }
    }
    return changed;
}

const ContactBank::Key* ContactBank::checked_key(Manual manual,
                                                std::uint32_t midi_note) const noexcept {
    std::size_t key = 0;
    if (!prepared_ || !is_valid_manual(manual) || !manual_midi_to_key_index(midi_note, key)) {
        return nullptr;
    }
    return &keys_[static_cast<std::size_t>(manual)][key];
}

ContactBank::Key* ContactBank::checked_key(Manual manual, std::uint32_t midi_note) noexcept {
    std::size_t key = 0;
    if (!prepared_ || !is_valid_manual(manual) || !manual_midi_to_key_index(midi_note, key)) {
        return nullptr;
    }
    return &keys_[static_cast<std::size_t>(manual)][key];
}

bool ContactBank::key_snapshot(Manual manual, std::uint32_t midi_note,
                                ContactKeySnapshot& destination) const noexcept {
    const Key* key = checked_key(manual, midi_note);
    if (key == nullptr) {
        return false;
    }
    destination = key->state;
    return true;
}

bool ContactBank::position(Manual manual, std::uint32_t midi_note,
                           double& destination) const noexcept {
    const Key* key = checked_key(manual, midi_note);
    if (key == nullptr) {
        return false;
    }
    destination = key->state.position;
    return true;
}

bool ContactBank::position_target(Manual manual, std::uint32_t midi_note,
                                  double& destination) const noexcept {
    const Key* key = checked_key(manual, midi_note);
    if (key == nullptr) {
        return false;
    }
    destination = key->state.target;
    return true;
}

bool ContactBank::key_target(Manual manual, std::uint32_t midi_note,
                             bool& destination) const noexcept {
    const Key* key = checked_key(manual, midi_note);
    if (key == nullptr) {
        return false;
    }
    destination = key->state.target > 0.0;
    return true;
}

bool ContactBank::contact_closed(Manual manual, std::uint32_t midi_note,
                                 std::size_t contact, bool& destination) const noexcept {
    const Key* key = checked_key(manual, midi_note);
    if (key == nullptr || contact >= kDrawbarCount) {
        return false;
    }
    destination = key->state.closed[contact];
    return true;
}

bool ContactBank::any_closed(Manual manual, std::size_t contact,
                             bool& destination) const noexcept {
    if (!prepared_ || !is_valid_manual(manual) || contact >= kDrawbarCount) {
        return false;
    }
    for (const auto& key : keys_[static_cast<std::size_t>(manual)]) {
        if (key.state.closed[contact]) {
            destination = true;
            return true;
        }
    }
    destination = false;
    return true;
}

} // namespace hammond
