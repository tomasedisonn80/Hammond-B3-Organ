#pragma once

#include <cfenv>
#include <cmath>
#include <cstddef>
#include <limits>
#include <locale>
#include <sstream>
#include <string>
#include <string_view>

namespace hammond::detail {

enum class DecimalResult { Ok, InvalidSyntax, OutOfRange };

// The exponent does not affect whether the significand is exactly zero.
[[nodiscard]] inline bool decimal_syntax(std::string_view token, bool& nonzero) noexcept {
    nonzero = false;
    if (token.empty()) return false;
    std::size_t at = 0;
    if (token[at] == '+' || token[at] == '-') ++at;
    bool digit = false;
    const auto significand_digits = [&] {
        while (at < token.size() && token[at] >= '0' && token[at] <= '9') {
            digit = true;
            nonzero = nonzero || token[at] != '0';
            ++at;
        }
    };
    significand_digits();
    if (at < token.size() && token[at] == '.') {
        ++at;
        significand_digits();
    }
    if (!digit) return false;
    if (at < token.size() && (token[at] == 'e' || token[at] == 'E')) {
        ++at;
        if (at < token.size() && (token[at] == '+' || token[at] == '-')) ++at;
        const auto exponent_start = at;
        while (at < token.size() && token[at] >= '0' && token[at] <= '9') ++at;
        if (at == exponent_start) return false;
    }
    return at == token.size();
}

// C-library conversion behind num_get can follow the caller's rounding mode.
// Match from_chars' nearest rounding without leaving that mode changed.
class DecimalRounding {
public:
    DecimalRounding() noexcept
        : previous_(std::fegetround()),
          ready_(previous_ != -1 &&
                 (previous_ == FE_TONEAREST || std::fesetround(FE_TONEAREST) == 0)) {}
    ~DecimalRounding() {
        if (ready_ && previous_ != FE_TONEAREST) {
            static_cast<void>(std::fesetround(previous_));
        }
    }
    DecimalRounding(const DecimalRounding&) = delete;
    DecimalRounding& operator=(const DecimalRounding&) = delete;
    [[nodiscard]] bool ready() const noexcept { return ready_; }

private:
    int previous_;
    bool ready_;
};

// Stopped/control-thread use only: stream construction and conversion may allocate.
// Failure (including an exception) never changes destination. Integer parsing is
// deliberately separate. See docs/DECIMAL_PARSING.md for the range contract.
[[nodiscard]] inline DecimalResult parse_decimal(std::string_view token,
                                                 double& destination) {
    bool nonzero = false;
    if (!decimal_syntax(token, nonzero)) return DecimalResult::InvalidSyntax;
    if (!nonzero) {
        // An arbitrarily large exponent cannot overflow or underflow exact zero.
        destination = token.front() == '-' ? -0.0 : 0.0;
        return DecimalResult::Ok;
    }

    std::istringstream input{std::string(token)};
    input.imbue(std::locale::classic());
    double value = 0.0;
    {
        const DecimalRounding rounding;
        if (!rounding.ready()) return DecimalResult::OutOfRange;
        input >> std::noskipws >> value;
    }

    // libc++ can set failbit for a correctly rounded nonzero subnormal, whereas
    // libstdc++ can silently round unrepresentable underflow to zero. Check the
    // value as well as the flags. A tiny result may round up to minimum normal.
    // Overflow that saturates to maximum finite still has failbit and rejects.
    if (input.bad() || input.rdbuf()->sgetc() != std::char_traits<char>::eof() ||
        !std::isfinite(value) || value == 0.0 ||
        (input.fail() && std::abs(value) > std::numeric_limits<double>::min())) {
        return DecimalResult::OutOfRange;
    }
    destination = value;
    return DecimalResult::Ok;
}

} // namespace hammond::detail
