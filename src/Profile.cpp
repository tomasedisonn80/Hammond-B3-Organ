#include "hammond/Profile.h"
#include "hammond/detail/Decimal.h"

#include <algorithm>
#include <charconv>
#include <cmath>
#include <exception>
#include <fstream>
#include <istream>
#include <locale>
#include <string_view>
#include <system_error>

namespace hammond {
namespace {

[[nodiscard]] bool is_unit_interval(double value) noexcept {
    return std::isfinite(value) && value >= 0.0 && value <= 1.0;
}

[[nodiscard]] bool is_lower_hex(char value) noexcept {
    return (value >= '0' && value <= '9') || (value >= 'a' && value <= 'f');
}

[[nodiscard]] bool valid_profile_id(const RuntimeProfile& profile) noexcept {
    for (std::size_t i = 0; i < profile.profile_id.size(); ++i) {
        const char expected = i < kNominalProfileId.size() ? kNominalProfileId[i] : '\0';
        if (profile.profile_id[i] != expected) {
            return false;
        }
    }
    return true;
}

[[nodiscard]] bool valid_digest(const RuntimeProfile& profile) noexcept {
    for (std::size_t i = 0; i < kSha256HexLength; ++i) {
        if (!is_lower_hex(profile.authoring_sha256[i])) {
            return false;
        }
    }
    return profile.authoring_sha256[kSha256HexLength] == '\0';
}

[[nodiscard]] bool valid_intrinsic_data(const RuntimeProfile& profile) noexcept {
    if (!valid_profile_id(profile) || !valid_digest(profile) ||
        !is_unit_interval(profile.output_gain) || profile.drawbar_gains.front() != 0.0 ||
        profile.drawbar_gains.back() != 1.0) {
        return false;
    }
    for (double gain : profile.drawbar_gains) {
        if (!is_unit_interval(gain)) {
            return false;
        }
    }
    for (const auto& source : profile.sources) {
        if (!std::isfinite(source.frequency_hz) || source.frequency_hz <= 0.0 ||
            !is_unit_interval(source.peak_amplitude) ||
            !std::isfinite(source.base_phase_turns) || source.base_phase_turns < 0.0 ||
            source.base_phase_turns >= 1.0) {
            return false;
        }
    }
    for (const auto& row : profile.manual_map) {
        for (ToneId tone_id : row) {
            if (tone_id < kMinManualToneId || tone_id > kMaxToneId) {
                return false;
            }
        }
    }
    return true;
}

[[nodiscard]] bool ascii_space(char value) noexcept {
    return value == ' ' || value == '\t' || value == '\n' || value == '\r' ||
           value == '\f' || value == '\v';
}

// Tokenization uses precisely the classic locale's ASCII whitespace. Non-ASCII
// bytes, embedded NULs, comments and extra records cannot be silently skipped.
class Tokens {
public:
    explicit Tokens(std::string_view text) noexcept : text_(text) {}

    [[nodiscard]] bool next(std::string_view& token) noexcept {
        while (position_ < text_.size() && ascii_space(text_[position_])) {
            ++position_;
        }
        if (position_ == text_.size()) {
            return false;
        }
        const auto first = position_;
        while (position_ < text_.size() && !ascii_space(text_[position_])) {
            ++position_;
        }
        token = text_.substr(first, position_ - first);
        return true;
    }

    [[nodiscard]] bool expect(std::string_view expected, std::string& error) {
        std::string_view token;
        if (!next(token) || token != expected) {
            error = "Expected token '" + std::string(expected) + "'.";
            return false;
        }
        return true;
    }

    [[nodiscard]] bool unsigned_integer(std::uint32_t& value, std::string_view field,
                                         std::string& error) {
        std::string_view token;
        if (!next(token) || token.empty() ||
            !std::all_of(token.begin(), token.end(), [](char ch) {
                return ch >= '0' && ch <= '9';
            })) {
            error = "Expected unsigned decimal integer for " + std::string(field) + ".";
            return false;
        }
        const auto result = std::from_chars(token.data(), token.data() + token.size(), value);
        if (result.ec != std::errc{} || result.ptr != token.data() + token.size()) {
            error = "Unsigned integer is out of range for " + std::string(field) + ".";
            return false;
        }
        return true;
    }

    [[nodiscard]] bool number(double& value, std::string_view field, std::string& error) {
        std::string_view token;
        if (!next(token)) {
            error = "Expected finite decimal number for " + std::string(field) + ".";
            return false;
        }
        const auto result = detail::parse_decimal(token, value);
        if (result == detail::DecimalResult::InvalidSyntax) {
            error = "Expected finite decimal number for " + std::string(field) + ".";
            return false;
        }
        if (result != detail::DecimalResult::Ok) {
            error = "Number is not finite or representable for " + std::string(field) + ".";
            return false;
        }
        return true;
    }

private:
    std::string_view text_;
    std::size_t position_{0};
};

[[nodiscard]] bool parse_profile(std::string_view text, RuntimeProfile& destination,
                                 std::string& error) {
    Tokens tokens(text);
    RuntimeProfile candidate;
    if (!tokens.expect("B3PROFILE", error) || !tokens.expect("1", error) ||
        !tokens.expect("profile_id", error) || !tokens.expect(kNominalProfileId, error)) {
        return false;
    }
    std::copy(kNominalProfileId.begin(), kNominalProfileId.end(), candidate.profile_id.begin());
    if (!tokens.expect("authoring_sha256", error)) {
        return false;
    }
    std::string_view digest;
    if (!tokens.next(digest) || digest.size() != kSha256HexLength ||
        !std::all_of(digest.begin(), digest.end(), is_lower_hex)) {
        error = "authoring_sha256 must contain exactly 64 lowercase hexadecimal characters.";
        return false;
    }
    std::copy(digest.begin(), digest.end(), candidate.authoring_sha256.begin());

    if (!tokens.expect("output_gain", error) ||
        !tokens.number(candidate.output_gain, "output_gain", error)) {
        return false;
    }
    if (!is_unit_interval(candidate.output_gain)) {
        error = "output_gain must be in [0,1].";
        return false;
    }
    if (!tokens.expect("drawbar_gains", error)) {
        return false;
    }
    for (auto& gain : candidate.drawbar_gains) {
        if (!tokens.number(gain, "drawbar_gains", error)) {
            return false;
        }
        if (!is_unit_interval(gain)) {
            error = "Every drawbar gain must be in [0,1].";
            return false;
        }
    }
    if (candidate.drawbar_gains.front() != 0.0 || candidate.drawbar_gains.back() != 1.0) {
        error = "Drawbar position 0 must be exactly 0 and position 8 exactly 1.";
        return false;
    }
    if (!tokens.expect("sources", error) || !tokens.expect("91", error)) {
        return false;
    }
    for (std::size_t i = 0; i < candidate.sources.size(); ++i) {
        std::uint32_t tone_id = 0;
        if (!tokens.unsigned_integer(tone_id, "source tone_id", error)) {
            return false;
        }
        if (tone_id != i + 1) {
            error = "Source tone_id must be " + std::to_string(i + 1) + " in consecutive order.";
            return false;
        }
        auto& source = candidate.sources[i];
        if (!tokens.number(source.frequency_hz, "frequency_hz", error) ||
            !tokens.number(source.peak_amplitude, "peak_amplitude", error) ||
            !tokens.number(source.base_phase_turns, "base_phase_turns", error)) {
            return false;
        }
        if (source.frequency_hz <= 0.0 || !is_unit_interval(source.peak_amplitude) ||
            source.base_phase_turns < 0.0 || source.base_phase_turns >= 1.0) {
            error = "Invalid source " + std::to_string(tone_id) +
                    ": require positive Hz, normalized peak in [0,1], and phase turns in [0,1).";
            return false;
        }
    }
    if (!tokens.expect("manual_map", error) || !tokens.expect("61", error) ||
        !tokens.expect("9", error)) {
        return false;
    }
    for (std::size_t key = 0; key < candidate.manual_map.size(); ++key) {
        for (auto& tone : candidate.manual_map[key]) {
            std::uint32_t tone_id = 0;
            if (!tokens.unsigned_integer(tone_id, "manual tone_id", error)) {
                return false;
            }
            if (tone_id < kMinManualToneId || tone_id > kMaxToneId) {
                error = "Manual key " + std::to_string(key + 1) + " has a tone_id outside 13..91.";
                return false;
            }
            tone = static_cast<ToneId>(tone_id);
        }
    }
    if (!tokens.expect("end", error)) {
        return false;
    }
    std::string_view trailing;
    if (tokens.next(trailing)) {
        error = "Unexpected trailing token after 'end'.";
        return false;
    }
    if (!valid_intrinsic_data(candidate)) {
        error = "Compiled profile failed intrinsic runtime validation.";
        return false;
    }
    destination = candidate;
    error.clear();
    return true;
}

} // namespace

Status validate_runtime_profile(const RuntimeProfile& profile, double sample_rate) noexcept {
    if (!is_supported_sample_rate(sample_rate)) {
        return Status::InvalidSpec;
    }
    if (!valid_intrinsic_data(profile)) {
        return Status::InvalidProfile;
    }
    const double nyquist_hz = sample_rate * 0.5;
    for (const auto& source : profile.sources) {
        if (source.frequency_hz >= nyquist_hz) {
            return Status::InvalidProfile;
        }
    }
    return Status::Ok;
}

bool load_runtime_profile(std::istream& input, RuntimeProfile& destination, std::string& error) {
    // Reading bytes does not depend on the caller's locale. Parse numbers with
    // the classic-locale decimal parser and classic ASCII whitespace, without
    // changing caller state.
    std::string bytes;
    bytes.reserve(kMaxCompiledProfileBytes);
    try {
        char byte = '\0';
        while (input.get(byte)) {
            if (bytes.size() == kMaxCompiledProfileBytes) {
                error = "Compiled profile exceeds the 128 KiB byte limit.";
                return false;
            }
            bytes.push_back(byte);
        }
    } catch (const std::ios_base::failure&) {
        // A stream configured to throw at EOF still completed a valid read.
        if (!input.eof() || input.bad()) {
            error = "Failed while reading the compiled profile stream.";
            return false;
        }
    } catch (const std::exception&) {
        // An exception-enabled istream can rethrow a streambuf's original
        // exception instead of ios_base::failure. Only normalize a confirmed
        // read failure; unrelated allocation/programming exceptions propagate.
        if (!input.bad()) {
            throw;
        }
        error = "Failed while reading the compiled profile stream.";
        return false;
    }
    if (input.bad() || !input.eof()) {
        error = "Failed while reading the compiled profile stream.";
        return false;
    }
    return parse_profile(bytes, destination, error);
}

bool load_runtime_profile_file(const std::filesystem::path& path, RuntimeProfile& destination,
                              std::string& error) {
    std::ifstream input(path, std::ios::binary);
    input.imbue(std::locale::classic());
    if (!input.is_open()) {
        error = "Cannot open compiled profile file: " + path.string();
        return false;
    }
    return load_runtime_profile(input, destination, error);
}

} // namespace hammond
