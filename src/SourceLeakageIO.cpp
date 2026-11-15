#include "hammond/SourceLeakage.h"
#include "hammond/detail/Decimal.h"

#include <algorithm>
#include <charconv>
#include <cstdint>
#include <fstream>
#include <istream>
#include <locale>
#include <system_error>

namespace hammond {
namespace {

constexpr std::size_t kMaxNumericTokenBytes = 128;

[[nodiscard]] bool ascii_space(char value) noexcept {
    return value == ' ' || value == '\t' || value == '\n' || value == '\r' ||
           value == '\f' || value == '\v';
}

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
        const auto start = position_;
        while (position_ < text_.size() && !ascii_space(text_[position_])) {
            ++position_;
        }
        token = text_.substr(start, position_ - start);
        return true;
    }

    [[nodiscard]] bool expect(std::string_view expected, std::string& error) {
        std::string_view token;
        if (!next(token) || token != expected) {
            error = "Expected source-leakage token '" + std::string(expected) + "'.";
            return false;
        }
        return true;
    }

    [[nodiscard]] bool unsigned_integer(std::uint32_t& value, std::string_view field,
                                         std::string& error) {
        std::string_view token;
        if (!next(token) || token.size() > kMaxNumericTokenBytes ||
            !std::all_of(token.begin(), token.end(), [](char digit) {
                return digit >= '0' && digit <= '9';
            })) {
            error = "Expected unsigned decimal " + std::string(field) +
                    " of at most 128 bytes.";
            return false;
        }
        const auto result = std::from_chars(token.data(), token.data() + token.size(), value);
        if (result.ec != std::errc{} || result.ptr != token.data() + token.size()) {
            error = "Source-leakage " + std::string(field) + " is out of range.";
            return false;
        }
        return true;
    }

    [[nodiscard]] bool gain(double& value, std::string& error) {
        std::string_view token;
        if (!next(token) || token.size() > kMaxNumericTokenBytes) {
            error = "Expected source-leakage gain of at most 128 bytes.";
            return false;
        }
        const auto result = detail::parse_decimal(token, value);
        if (result == detail::DecimalResult::InvalidSyntax) {
            error = "Source-leakage gain must be a complete finite decimal number.";
            return false;
        }
        if (result != detail::DecimalResult::Ok) {
            error = "Source-leakage gain overflows or underflows to zero.";
            return false;
        }
        return true;
    }

private:
    std::string_view text_;
    std::size_t position_{0};
};

[[nodiscard]] bool parse_profile(std::string_view bytes,
                                 SourceLeakageProfile& destination, std::string& error) {
    Tokens tokens(bytes);
    SourceLeakageProfile candidate{};
    if (!tokens.expect("B3LEAKAGE1", error) || !tokens.expect("model", error) ||
        !tokens.expect(kSourceLeakageModel, error) || !tokens.expect("profile_id", error)) {
        return false;
    }
    std::string_view id;
    if (!tokens.next(id) || id.size() > kSourceLeakageProfileIdMaxLength) {
        error = "Source-leakage profile_id is missing or exceeds 64 bytes.";
        return false;
    }
    std::copy(id.begin(), id.end(), candidate.profile_id.begin());
    if (!tokens.expect("evidence_status", error) ||
        !tokens.expect(kSourceLeakageEvidenceStatus, error) ||
        !tokens.expect("boundary", error) || !tokens.expect(kSourceLeakageBoundary, error) ||
        !tokens.expect("source_content", error) ||
        !tokens.expect(kSourceLeakageSourceContent, error) ||
        !tokens.expect("authoring_sha256", error)) {
        return false;
    }
    std::string_view digest;
    if (!tokens.next(digest) || digest.size() != kSourceLeakageSha256HexLength) {
        error = "Source-leakage authoring_sha256 must contain 64 lowercase hexadecimal digits.";
        return false;
    }
    std::copy(digest.begin(), digest.end(), candidate.authoring_sha256.begin());

    std::uint32_t source_count = 0;
    if (!tokens.expect("source_count", error) ||
        !tokens.unsigned_integer(source_count, "source_count", error)) {
        return false;
    }
    if (source_count != kToneSourceCount) {
        error = "Source-leakage source_count must be 91.";
        return false;
    }
    std::uint32_t edge_count = 0;
    if (!tokens.expect("edge_count", error) ||
        !tokens.unsigned_integer(edge_count, "edge_count", error)) {
        return false;
    }
    if (edge_count > kMaxSourceLeakageEdges) {
        error = "Source-leakage edge_count exceeds the 728-edge limit.";
        return false;
    }
    candidate.edge_count = edge_count;
    for (std::size_t i = 0; i < candidate.edge_count; ++i) {
        std::uint32_t destination_id = 0;
        std::uint32_t source_id = 0;
        double gain = 0.0;
        if (!tokens.expect("edge", error) || !tokens.expect("destination", error) ||
            !tokens.unsigned_integer(destination_id, "destination tone ID", error) ||
            !tokens.expect("source", error) ||
            !tokens.unsigned_integer(source_id, "source tone ID", error) ||
            !tokens.expect("gain", error) || !tokens.gain(gain, error)) {
            return false;
        }
        // Check before narrowing so an oversized integer cannot wrap to a valid ID.
        if (source_id < 1 || source_id > kToneSourceCount ||
            destination_id < 1 || destination_id > kToneSourceCount) {
            error = "Source-leakage tone IDs must be in 1..91.";
            return false;
        }
        candidate.edges[i] = {static_cast<ToneId>(source_id),
                              static_cast<ToneId>(destination_id), gain};
    }
    if (!tokens.expect("end", error)) {
        return false;
    }
    std::string_view trailing;
    if (tokens.next(trailing)) {
        error = "Unexpected source-leakage data after 'end'.";
        return false;
    }
    // This single validator owns metadata syntax, canonical ordering and all
    // numerical/pair/capacity rules. Do not sort native input to make it valid.
    if (validate_source_leakage_profile(candidate) != Status::Ok) {
        error = "Source-leakage metadata, canonical edge order or coefficient limits are invalid.";
        return false;
    }
    destination = candidate;
    error.clear();
    return true;
}

} // namespace

bool load_source_leakage_profile(std::istream& input, SourceLeakageProfile& destination,
                                 std::string& error) {
    std::string bytes;
    bytes.reserve(kMaxCompiledSourceLeakageBytes);
    try {
        char byte = '\0';
        while (input.get(byte)) {
            if (bytes.size() == kMaxCompiledSourceLeakageBytes) {
                error = "Compiled source leakage exceeds the 128 KiB byte limit.";
                return false;
            }
            if (byte == '\0' || static_cast<unsigned char>(byte) > 0x7f) {
                error = "Compiled source leakage requires ASCII bytes without embedded NUL.";
                return false;
            }
            bytes.push_back(byte);
        }
    } catch (const std::ios_base::failure&) {
        // EOF exception masks are allowed. An observed transport failure is
        // still fatal, including one after a complete 'end' record.
        if (!input.eof() || input.bad()) {
            error = "Failed while reading the compiled source-leakage stream.";
            return false;
        }
    } catch (...) {
        // A streambuf exception may be rethrown verbatim with badbit enabled.
        // Normalize only confirmed stream failures, not unrelated exceptions.
        if (!input.bad()) {
            throw;
        }
        error = "Failed while reading the compiled source-leakage stream.";
        return false;
    }
    if (input.bad() || !input.eof()) {
        error = "Failed while reading the compiled source-leakage stream.";
        return false;
    }
    return parse_profile(bytes, destination, error);
}

bool load_source_leakage_profile_file(const std::filesystem::path& path,
                                      SourceLeakageProfile& destination,
                                      std::string& error) {
    std::ifstream input(path, std::ios::binary);
    input.imbue(std::locale::classic());
    if (!input.is_open()) {
        error = "Cannot open compiled source-leakage file: " + path.string();
        return false;
    }
    return load_source_leakage_profile(input, destination, error);
}

} // namespace hammond
