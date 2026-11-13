#include "TestSupport.h"
#include "hammond/detail/Decimal.h"

#include <array>
#include <bit>
#include <cfenv>
#include <cstdint>
#include <locale>
#include <sstream>
#include <string>
#include <string_view>

namespace {

using hammond::detail::DecimalResult;
using hammond::detail::parse_decimal;
std::size_t accepted_count = 0;
std::size_t rejected_count = 0;

static_assert(sizeof(double) == sizeof(std::uint64_t));
static_assert(std::numeric_limits<double>::is_iec559 &&
              std::numeric_limits<double>::digits == 53);

void accepted(std::string_view token, std::uint64_t expected) {
    double actual = -123.75;
    if (parse_decimal(token, actual) != DecimalResult::Ok) {
        hammond_test::fail("valid decimal accepted", __FILE__, __LINE__, token);
    }
    if (std::bit_cast<std::uint64_t>(actual) != expected) {
        hammond_test::fail("decimal has expected binary64 bits", __FILE__, __LINE__, token);
    }
    ++accepted_count;
}

void rejected(std::string_view token, DecimalResult expected) {
    // A finite value, signed zero and a NaN payload must all survive rejection.
    for (const std::uint64_t before : {0x405edd0000000000ULL, 0x8000000000000000ULL,
                                       0x7ff8000000000042ULL}) {
        double destination = std::bit_cast<double>(before);
        if (parse_decimal(token, destination) != expected) {
            hammond_test::fail("invalid decimal rejected with expected category",
                               __FILE__, __LINE__, token);
        }
        CHECK(std::bit_cast<std::uint64_t>(destination) == before);
    }
    ++rejected_count;
}

void test_fixed_vectors() {
    struct Vector { std::string_view text; std::uint64_t bits; };
    // Expected bits are independent binary64 boundary values, not another call
    // to the parser. Halfway decimals below are exact rational expansions.
    constexpr std::array vectors{
        Vector{"0", 0}, Vector{"+000.0e+09", 0},
        Vector{"-0", 0x8000000000000000ULL},
        Vector{"-.000E-999", 0x8000000000000000ULL},
        Vector{".125", 0x3fc0000000000000ULL},
        Vector{"+001.2500e+2", 0x405f400000000000ULL},
        Vector{"125.", 0x405f400000000000ULL},
        Vector{"-12.50E-1", 0xbff4000000000000ULL},
        Vector{"0.1", 0x3fb999999999999aULL},
        Vector{"-1e-3", 0xbf50624dd2f1a9fcULL},
        Vector{"9007199254740993", 0x4340000000000000ULL},
        Vector{"9007199254740995", 0x4340000000000002ULL},
        Vector{"1.00000000000000011102230246251565404236316680908203124",
               0x3ff0000000000000ULL},
        Vector{"1.00000000000000011102230246251565404236316680908203125",
               0x3ff0000000000000ULL},
        Vector{"1.00000000000000011102230246251565404236316680908203126",
               0x3ff0000000000001ULL},
        Vector{"1.00000000000000033306690738754696212708950042724609375",
               0x3ff0000000000002ULL},
        Vector{"2.2250738585072014e-308", 0x0010000000000000ULL},
        Vector{"2.2250738585072012e-308", 0x0010000000000000ULL},
        Vector{"2.2250738585072011e-308", 0x000fffffffffffffULL},
        Vector{"4.9406564584124654e-324", 1},
        Vector{"-5e-324", 0x8000000000000001ULL},
        Vector{"2.4703282292062328e-324", 1},
        Vector{"7.410984687618698e-324", 1},
        Vector{"7.410984687618699e-324", 2},
        Vector{"9.8813129168249309e-324", 2},
        Vector{"1.7976931348623157e308", 0x7fefffffffffffffULL},
        Vector{"1.7976931348623158e308", 0x7fefffffffffffffULL},
        Vector{"-1.7976931348623157e308", 0xffefffffffffffffULL},
    };
    for (const auto& vector : vectors) accepted(vector.text, vector.bits);
    for (const char* token : {"1e-324", "-1e-324", "2.4703282292062327e-324",
                              "1e-9999", "-1e-9999", "1.7976931348623159e308",
                              "-1.7976931348623159e308", "1e309", "1e9999"}) {
        rejected(token, DecimalResult::OutOfRange);
    }
}

void test_grammar_and_bounds() {
    for (const char* token : {"", "+", "-", ".", "+.", "-.", "e1", ".e1",
                              "1e", "1E+", "1e-", "1e+-2", "1e--2", "1e2e3",
                              "+-1", "-+1", "++1", "--1", "1..0", "1.2.3",
                              " 1", "1 ", "\t1", "1\n", "1 2", "1,25",
                              "1_000", "1'000", "1f", "0.5junk", "0x1p0", "0X1",
                              "nan", "NaN", "nan(1)", "+nan", "inf", "-Infinity",
                              "#1", "1#", "\xc2\xa0" "1", "\xd9\xa1"}) {
        rejected(token, DecimalResult::InvalidSyntax);
    }
    rejected(std::string_view("1\0", 2), DecimalResult::InvalidSyntax);
    rejected(std::string_view("\0", 1), DecimalResult::InvalidSyntax);
    const std::string surrounded = "x12.5suffix";
    accepted(std::string_view(surrounded).substr(1, 4), 0x4029000000000000ULL);
    rejected(std::string_view(surrounded).substr(1, 5), DecimalResult::InvalidSyntax);

    const std::string huge_exponent(1024, '9');
    accepted("-0.000e+" + huge_exponent, 0x8000000000000000ULL);
    accepted("+0e-" + huge_exponent, 0);
    rejected("1e" + huge_exponent, DecimalResult::OutOfRange);
    rejected("-1e-" + huge_exponent, DecimalResult::OutOfRange);
    accepted("1" + std::string(1024, '0') + "e-1024", 0x3ff0000000000000ULL);
    accepted("0." + std::string(1023, '0') + "1e1024", 0x3ff0000000000000ULL);
}

void round_trip(std::uint64_t bits) {
    const double expected = std::bit_cast<double>(bits);
    std::ostringstream output;
    output.imbue(std::locale::classic());
    output << std::setprecision(std::numeric_limits<double>::max_digits10) << expected;
    CHECK(output.good());
    accepted(output.str(), bits);
}

void test_round_trips() {
    // Cover both signs, every finite exponent, exact powers of two and both
    // neighboring ends of the significand range, including the subnormal bin.
    constexpr std::array<std::uint64_t, 3> mantissas{0, 1, 0x000fffffffffffffULL};
    for (std::uint64_t exponent = 0; exponent < 2047; ++exponent) {
        for (const auto mantissa : mantissas) {
            const auto bits = (exponent << 52U) | mantissa;
            round_trip(bits);
            round_trip(bits | 0x8000000000000000ULL);
        }
    }
    std::uint64_t state = 0x4d595df4d0f33173ULL;
    for (std::size_t i = 0; i < 4096; ++i) {
        state = state * 6364136223846793005ULL + 1442695040888963407ULL;
        if ((state & 0x7ff0000000000000ULL) != 0x7ff0000000000000ULL) round_trip(state);
    }
}

void test_locale_isolation() {
    class CommaDecimal : public std::numpunct<char> {
        char do_decimal_point() const override { return ','; }
        char do_thousands_sep() const override { return '.'; }
        std::string do_grouping() const override { return "\3"; }
    };
    const auto previous = std::locale();
    const std::locale comma(std::locale::classic(), new CommaDecimal);
    std::locale::global(comma);
    test_fixed_vectors();
    rejected("1,25", DecimalResult::InvalidSyntax);
    accepted("1.25", 0x3ff4000000000000ULL);
    CHECK(std::locale() == comma);
    std::locale::global(previous);
}

void test_rounding_mode_isolation() {
    const int previous = std::fegetround();
    CHECK(previous != -1);
    for (const int mode : {FE_TONEAREST, FE_DOWNWARD, FE_UPWARD, FE_TOWARDZERO}) {
        CHECK(std::fesetround(mode) == 0);
        test_fixed_vectors();
        CHECK(std::fegetround() == mode);
        rejected("1garbage", DecimalResult::InvalidSyntax);
        CHECK(std::fegetround() == mode);
    }
    CHECK(std::fesetround(previous) == 0);
}

} // namespace

int main() {
    test_fixed_vectors();
    test_grammar_and_bounds();
    test_round_trips();
    test_locale_isolation();
    test_rounding_mode_isolation();
    std::cout << "decimal: " << accepted_count << " exact values/round trips; "
              << rejected_count << " rejected tokens with unchanged destinations\n";
}
