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
static_assert(kManualCount == 2 && kDrawbarBankCount == 2 && kDrawbarCount == 9);

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

[[nodiscard]] bool parse_text(std::string_view text, ControlSnapshot& destination,
                              std::string& error) {
    Tokens tokens(text);
    ControlSnapshot candidate;
    if (!tokens.expect("B3CONTROLS1", error) || !tokens.expect("expression", error) ||
        !parse_expression(tokens, candidate.expression, error)) return false;
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
    output << std::setprecision(std::numeric_limits<double>::max_digits10)
           << "B3CONTROLS1\nexpression " << snapshot.expression << '\n';
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
