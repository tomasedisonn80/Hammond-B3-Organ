#include "hammond/SourceLeakage.h"

#include <cmath>

namespace hammond {
namespace {

[[nodiscard]] bool lower_alphanumeric(char value) noexcept {
    return (value >= 'a' && value <= 'z') || (value >= '0' && value <= '9');
}

[[nodiscard]] bool valid_profile_id(const SourceLeakageProfile& profile) noexcept {
    constexpr std::string_view prefix = "synthetic-";
    const auto& id = profile.profile_id;
    std::size_t length = 0;
    while (length < id.size() && id[length] != '\0') {
        ++length;
    }
    if (length <= prefix.size() || length > kSourceLeakageProfileIdMaxLength) {
        return false;
    }
    for (std::size_t i = 0; i < prefix.size(); ++i) {
        if (id[i] != prefix[i]) {
            return false;
        }
    }
    if (!lower_alphanumeric(id[prefix.size()])) {
        return false;
    }
    for (std::size_t i = prefix.size() + 1; i < length; ++i) {
        if (!lower_alphanumeric(id[i]) && id[i] != '-') {
            return false;
        }
    }
    for (std::size_t i = length; i < id.size(); ++i) {
        if (id[i] != '\0') {
            return false;
        }
    }
    return true;
}

[[nodiscard]] bool valid_digest(const SourceLeakageProfile& profile) noexcept {
    for (std::size_t i = 0; i < kSourceLeakageSha256HexLength; ++i) {
        const char digit = profile.authoring_sha256[i];
        if (!((digit >= '0' && digit <= '9') || (digit >= 'a' && digit <= 'f'))) {
            return false;
        }
    }
    return profile.authoring_sha256[kSourceLeakageSha256HexLength] == '\0';
}

[[nodiscard]] bool canonical_less(const SourceLeakageEdge& left,
                                   const SourceLeakageEdge& right) noexcept {
    return left.destination < right.destination ||
           (left.destination == right.destination && left.source < right.source);
}

} // namespace

Status SourceLeakage::prepare(std::span<const SourceLeakageEdge> edges) noexcept {
    if (edges.size() > kMaxSourceLeakageEdges) {
        return Status::InvalidProfile;
    }

    SourceLeakage candidate;
    for (const auto& edge : edges) {
        std::size_t source = 0;
        std::size_t destination = 0;
        if (!tone_id_to_index(edge.source, source) ||
            !tone_id_to_index(edge.destination, destination) ||
            source == destination || !std::isfinite(edge.gain) ||
            edge.gain == 0.0 || std::abs(edge.gain) > 0.25) {
            return Status::InvalidProfile;
        }

        auto& row = candidate.rows_[destination];
        if (row.count == kMaxSourceLeakageEdgesPerDestination) {
            return Status::InvalidProfile;
        }
        std::size_t position = 0;
        while (position < row.count && row.terms[position].source_index < source) {
            ++position;
        }
        if (position < row.count && row.terms[position].source_index == source) {
            return Status::InvalidProfile;
        }
        // At most eight fixed entries: no allocating sort or retained pointers.
        for (std::size_t i = row.count; i > position; --i) {
            row.terms[i] = row.terms[i - 1];
        }
        row.terms[position] = Term{source, edge.gain};
        ++row.count;
    }

    for (auto& row : candidate.rows_) {
        double sum = 0.0;
        for (std::size_t i = 0; i < row.count; ++i) {
            // Admission is explicitly sequential binary64 in source-ID order;
            // a more accurate or reassociated sum would change this contract.
            sum += std::abs(row.terms[i].gain);
        }
        if (sum > 0.5) {
            return Status::InvalidProfile;
        }
        row.absolute_gain_sum = sum;
        if (sum > candidate.max_row_absolute_gain_sum_) {
            candidate.max_row_absolute_gain_sum_ = sum;
        }
    }
    candidate.edge_count_ = edges.size();
    candidate.prepared_ = true;
    *this = candidate;
    return Status::Ok;
}

Status SourceLeakage::process_frame(const SourceLeakageFrame& input,
                                     SourceLeakageFrame& output) const noexcept {
    if (!prepared_) {
        return Status::NotPrepared;
    }
    for (double value : input) {
        if (!std::isfinite(value) || value < -1.0 || value > 1.0) {
            return Status::InvalidBuffer;
        }
    }

    SourceLeakageFrame candidate = input;
    for (std::size_t destination = 0; destination < rows_.size(); ++destination) {
        const auto& row = rows_[destination];
        if (row.count == 0) {
            continue;
        }
        double value = input[destination];
        for (std::size_t i = 0; i < row.count; ++i) {
            const auto& term = row.terms[i];
            value += term.gain * input[term.source_index];
        }
        candidate[destination] = value;
    }
    output = candidate;
    return Status::Ok;
}

bool SourceLeakage::row_absolute_gain_sum(ToneId destination,
                                          double& value) const noexcept {
    std::size_t index = 0;
    if (!prepared_ || !tone_id_to_index(destination, index)) {
        return false;
    }
    value = rows_[index].absolute_gain_sum;
    return true;
}

Status validate_source_leakage_profile(const SourceLeakageProfile& profile) noexcept {
    if (!valid_profile_id(profile) || !valid_digest(profile) ||
        profile.edge_count > kMaxSourceLeakageEdges) {
        return Status::InvalidProfile;
    }
    for (std::size_t i = 1; i < profile.edge_count; ++i) {
        if (!canonical_less(profile.edges[i - 1], profile.edges[i])) {
            return Status::InvalidProfile;
        }
    }
    SourceLeakage candidate;
    return candidate.prepare(
        std::span<const SourceLeakageEdge>{profile.edges.data(), profile.edge_count});
}

} // namespace hammond
