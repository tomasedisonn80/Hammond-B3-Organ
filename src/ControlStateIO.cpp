#include "hammond/ControlStateIO.h"
#include "hammond/detail/Decimal.h"

#include <iomanip>
#include <istream>
#include <limits>
#include <locale>
#include <sstream>
#include <string_view>

namespace hammond {
namespace {

constexpr std::array<std::string_view, kManualCount> kManualNames{"upper", "lower"};
constexpr std::array<std::string_view, kDrawbarBankCount> kBankNames{"A", "B"};
constexpr std::array<std::string_view, 2> kHarmonicNames{"second", "third"};
constexpr std::array<std::string_view, 2> kVolumeNames{"normal", "soft"};
constexpr std::array<std::string_view, 2> kDecayNames{"slow", "fast"};
static_assert(kManualCount == 2 && kDrawbarBankCount == 2 && kDrawbarCount == 9);
static_assert(kPedalDrawbarCount == 2);

[[nodiscard]] bool ascii_space(char value) noexcept {
    return value == ' ' || value == '\t' || value == '\n' || value == '\r' ||
           value == '\f' || value == '\v';
}

class Tokens {
public:
    explicit Tokens(std::string_view text) noexcept : text_(text) {}

    [[nodiscard]] bool next(std::string_view& token) noexcept {
        while (position_ < text_.size() && ascii_space(text_[position_])) ++position_;
        if (position_ == text_.size()) return false;
        const auto first = position_;
        while (position_ < text_.size() && !ascii_space(text_[position_])) ++position_;
        token = text_.substr(first, position_ - first);
        return true;
    }

    [[nodiscard]] bool expect(std::string_view expected, std::string& error) {
        std::string_view token;
        if (!next(token) || token != expected) {
            error = "Expected control token '" + std::string(expected) + "'.";
            return false;
        }
        return true;
    }

private:
    std::string_view text_;
    std::size_t position_{0};
};

[[nodiscard]] bool parse_expression(Tokens& tokens, double& destination, std::string& error) {
    std::string_view token;
    if (!tokens.next(token)) {
        error = "Missing control expression.";
        return false;
    }
    double value = 0.0;
    if (detail::parse_decimal(token, value) != detail::DecimalResult::Ok) {
        error = "Control expression must be a finite representable decimal.";
        return false;
    }
    destination = value;
    return true;
}

[[nodiscard]] bool parse_percussion(Tokens& tokens, PercussionSettings& destination,
                                    std::string& error) {
    if (!tokens.expect("percussion", error) || !tokens.expect("enabled", error)) return false;
    std::string_view token;
    if (!tokens.next(token) || (token != "0" && token != "1")) {
        error = "Control percussion enabled must be 0 or 1.";
        return false;
    }
    destination.enabled = token == "1";
    if (!tokens.expect("harmonic", error)) return false;
    if (!tokens.next(token) || (token != "second" && token != "third")) {
        error = "Control percussion harmonic must be second or third.";
        return false;
    }
    destination.harmonic = token == "second" ? PercussionHarmonic::Second
                                             : PercussionHarmonic::Third;
    if (!tokens.expect("volume", error)) return false;
    if (!tokens.next(token) || (token != "normal" && token != "soft")) {
        error = "Control percussion volume must be normal or soft.";
        return false;
    }
    destination.volume = token == "normal" ? PercussionVolume::Normal : PercussionVolume::Soft;
    if (!tokens.expect("decay", error)) return false;
    if (!tokens.next(token) || (token != "slow" && token != "fast")) {
        error = "Control percussion decay must be slow or fast.";
        return false;
    }
    destination.decay = token == "slow" ? PercussionDecay::Slow : PercussionDecay::Fast;
    return true;
}

[[nodiscard]] bool parse_manual(Tokens& tokens, std::size_t manual,
                                ControlSnapshot& candidate, std::string& error) {
    if (!tokens.expect("manual", error) || !tokens.expect(kManualNames[manual], error) ||
        !tokens.expect("selected", error)) return false;
    std::string_view token;
    if (!tokens.next(token) || (token != "A" && token != "B")) {
        error = "Selected control bank must be A or B.";
        return false;
    }
    candidate.selected_banks[manual] = token == "A" ? DrawbarBank::A : DrawbarBank::B;
    if (!tokens.expect("route_enabled", error)) return false;
    if (!tokens.next(token) || (token != "0" && token != "1")) {
        error = "Control route_enabled must be 0 or 1.";
        return false;
    }
    candidate.route_enabled[manual] = token == "1";
    for (std::size_t bank = 0; bank < kDrawbarBankCount; ++bank) {
        if (!tokens.expect("bank", error) || !tokens.expect(kBankNames[bank], error)) return false;
        for (auto& position : candidate.drawbars[manual][bank]) {
            if (!tokens.next(token) || token.size() != 1 || token.front() < '0' ||
                token.front() > '8') {
                error = "Each control bank requires nine single-digit positions in 0..8.";
                return false;
            }
            position = static_cast<std::uint8_t>(token.front() - '0');
        }
    }
    return true;
}

[[nodiscard]] bool parse_pedals(Tokens& tokens, PedalDrawbarPositions& destination,
                               std::string& error) {
    if (!tokens.expect("pedal", error) || !tokens.expect("drawbars", error)) return false;
    for (auto& position : destination) {
        std::string_view token;
        if (!tokens.next(token) || token.size() != 1 || token.front() < '0' ||
            token.front() > '8') {
            error = "Pedal controls require two single-digit positions in 0..8.";
            return false;
        }
        position = static_cast<std::uint8_t>(token.front() - '0');
    }
    return true;
}

[[nodiscard]] bool parse_text(std::string_view text, ControlSnapshot& destination,
                              std::string& error) {
    Tokens tokens(text);
    ControlSnapshot candidate;
    std::string_view version;
    if (!tokens.next(version) || (version != "B3CONTROLS1" && version != "B3CONTROLS2" &&
                                  version != "B3CONTROLS3")) {
        error = "Unsupported control version; expected B3CONTROLS1, B3CONTROLS2 or B3CONTROLS3.";
        return false;
    }
    if (!tokens.expect("expression", error) ||
        !parse_expression(tokens, candidate.expression, error)) return false;
    // A fresh candidate gives historical version 1 explicit Off/Second/Normal/
    // Slow defaults, and versions 1/2 explicit muted pedal defaults, independent
    // of the caller's destination. Newer formats must supply all their records;
    // a missing version-3 pedal record never activates legacy migration.
    if (version != "B3CONTROLS1" && !parse_percussion(tokens, candidate.percussion, error)) {
        return false;
    }
    if (version == "B3CONTROLS3" && !parse_pedals(tokens, candidate.pedal_drawbars, error)) {
        return false;
    }
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        if (!parse_manual(tokens, manual, candidate, error)) return false;
    }
    if (!tokens.expect("end", error)) return false;
    std::string_view trailing;
    if (tokens.next(trailing)) {
        error = "Unexpected trailing control data after 'end'.";
        return false;
    }
    if (!is_valid_control_snapshot(candidate)) {
        error = "Control snapshot contains values outside its supported bounds.";
        return false;
    }
    destination = candidate;
    error.clear();
    return true;
}

} // namespace

bool serialize_controls(const ControlSnapshot& snapshot, std::string& destination,
                        std::string& error) {
    if (&destination == &error) return false;
    if (!is_valid_control_snapshot(snapshot)) {
        error = "Cannot serialize an invalid control snapshot.";
        return false;
    }
    std::ostringstream output;
    output.imbue(std::locale::classic());
    {
        // num_put can follow the caller's rounding mode just as num_get can.
        // Match the parser's nearest rounding so max_digits10 preserves every
        // binary64 expression. Restore the caller's mode before any later exit.
        const detail::DecimalRounding rounding;
        if (!rounding.ready()) {
            error = "Cannot select nearest rounding for the control expression.";
            return false;
        }
        output << std::setprecision(std::numeric_limits<double>::max_digits10)
               << "B3CONTROLS3\nexpression " << snapshot.expression << '\n';
    }
    output << "percussion enabled " << (snapshot.percussion.enabled ? '1' : '0')
           << " harmonic " << kHarmonicNames[static_cast<std::size_t>(snapshot.percussion.harmonic)]
           << " volume " << kVolumeNames[static_cast<std::size_t>(snapshot.percussion.volume)]
           << " decay " << kDecayNames[static_cast<std::size_t>(snapshot.percussion.decay)] << '\n';
    output << "pedal drawbars";
    for (const auto position : snapshot.pedal_drawbars) {
        output << ' ' << static_cast<unsigned>(position);
    }
    output << '\n';
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        output << "manual " << kManualNames[manual] << " selected "
               << kBankNames[static_cast<std::size_t>(snapshot.selected_banks[manual])]
               << " route_enabled " << (snapshot.route_enabled[manual] ? '1' : '0') << '\n';
        for (std::size_t bank = 0; bank < kDrawbarBankCount; ++bank) {
            output << "bank " << kBankNames[bank];
            for (const auto position : snapshot.drawbars[manual][bank]) {
                output << ' ' << static_cast<unsigned>(position);
            }
            output << '\n';
        }
    }
    output << "end\n";
    if (!output) {
        error = "Failed while serializing the control snapshot.";
        return false;
    }
    auto bytes = output.str();
    if (bytes.size() > kMaxControlStateBytes) {
        error = "Serialized controls exceed the 16 KiB byte limit.";
        return false;
    }
    destination.swap(bytes);
    error.clear();
    return true;
}

bool parse_controls(std::istream& input, ControlSnapshot& destination, std::string& error) {
    if (!input.good()) {
        error = "Control input stream is not readable.";
        return false;
    }
    std::string bytes;
    bytes.reserve(kMaxControlStateBytes);
    try {
        char byte = '\0';
        while (input.get(byte)) {
            if (bytes.size() == kMaxControlStateBytes) {
                error = "Control input exceeds the 16 KiB byte limit.";
                return false;
            }
            bytes.push_back(byte);
        }
    } catch (...) {
        // istream may rethrow a streambuf's original exception. A configured
        // EOF exception is normal completion; every bad/non-EOF state is failure.
        if (input.bad() || !input.eof()) {
            error = "Failed while reading the control input stream.";
            return false;
        }
    }
    if (input.bad() || !input.eof()) {
        error = "Failed while reading the control input stream.";
        return false;
    }
    return parse_text(bytes, destination, error);
}

} // namespace hammond
