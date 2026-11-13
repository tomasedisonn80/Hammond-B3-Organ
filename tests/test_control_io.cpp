#include "TestSupport.h"
#include "hammond/ControlStateIO.h"

#include <array>
#include <bit>
#include <cfenv>
#include <cstdint>
#include <iterator>
#include <locale>
#include <sstream>
#include <stdexcept>
#include <streambuf>
#include <utility>
#include <vector>

namespace {
using hammond::ControlSnapshot;
using hammond::DrawbarBank;
using Tokens = std::vector<std::string>;
std::size_t rejected_inputs = 0;

// Frozen historical input. Its 60-token offsets below remain migration coverage.
constexpr std::string_view kLegacyCanonical =
    "B3CONTROLS1\n"
    "expression 0.375\n"
    "manual upper selected A route_enabled 0\n"
    "bank A 0 1 2 3 4 5 6 7 8\n"
    "bank B 8 7 6 5 4 3 2 1 0\n"
    "manual lower selected B route_enabled 1\n"
    "bank A 1 3 5 7 0 2 4 6 8\n"
    "bank B 8 6 4 2 0 7 5 3 1\n"
    "end\n";

constexpr std::string_view kCanonicalV2 =
    "B3CONTROLS2\n"
    "expression 0.375\n"
    "percussion enabled 0 harmonic second volume normal decay slow\n"
    "manual upper selected A route_enabled 0\n"
    "bank A 0 1 2 3 4 5 6 7 8\n"
    "bank B 8 7 6 5 4 3 2 1 0\n"
    "manual lower selected B route_enabled 1\n"
    "bank A 1 3 5 7 0 2 4 6 8\n"
    "bank B 8 6 4 2 0 7 5 3 1\n"
    "end\n";

constexpr std::string_view kCanonicalV3 =
    "B3CONTROLS3\n"
    "expression 0.375\n"
    "percussion enabled 0 harmonic second volume normal decay slow\n"
    "pedal drawbars 0 0\n"
    "manual upper selected A route_enabled 0\n"
    "bank A 0 1 2 3 4 5 6 7 8\n"
    "bank B 8 7 6 5 4 3 2 1 0\n"
    "manual lower selected B route_enabled 1\n"
    "bank A 1 3 5 7 0 2 4 6 8\n"
    "bank B 8 6 4 2 0 7 5 3 1\n"
    "end\n";

ControlSnapshot varied_snapshot() {
    ControlSnapshot result;
    result.expression = 0.375;
    result.selected_banks = {DrawbarBank::A, DrawbarBank::B};
    result.route_enabled = {false, true};
    result.drawbars[0][0] = {0, 1, 2, 3, 4, 5, 6, 7, 8};
    result.drawbars[0][1] = {8, 7, 6, 5, 4, 3, 2, 1, 0};
    result.drawbars[1][0] = {1, 3, 5, 7, 0, 2, 4, 6, 8};
    result.drawbars[1][1] = {8, 6, 4, 2, 0, 7, 5, 3, 1};
    return result;
}

void same_snapshot(const ControlSnapshot& actual, const ControlSnapshot& expected) {
    // Check all controls, including retained percussion and both route bits;
    // no object-representation/padding comparison is a state oracle.
    CHECK(actual.drawbars == expected.drawbars);
    CHECK(actual.selected_banks == expected.selected_banks);
    CHECK(actual.route_enabled == expected.route_enabled);
    CHECK(actual.expression == expected.expression);
    CHECK(std::signbit(actual.expression) == std::signbit(expected.expression));
    CHECK(actual.percussion == expected.percussion);
    CHECK(actual.pedal_drawbars == expected.pedal_drawbars);
}

std::string encoded(const ControlSnapshot& state) {
    std::string destination = "old destination";
    std::string error = "stale error";
    CHECK(hammond::serialize_controls(state, destination, error));
    CHECK(error.empty());
    CHECK(destination.size() <= hammond::kMaxControlStateBytes);
    return destination;
}

ControlSnapshot accepted(std::istream& input) {
    auto destination = varied_snapshot();
    destination.pedal_drawbars = {8, 7};
    std::string error = "stale error";
    if (!hammond::parse_controls(input, destination, error)) {
        throw std::runtime_error("Valid controls rejected: " + error);
    }
    CHECK(error.empty());
    return destination;
}

ControlSnapshot accepted(const std::string& text) {
    std::istringstream input(text);
    return accepted(input);
}

void rejected(std::istream& input, std::string_view label) {
    auto destination = varied_snapshot();
    destination.expression = 0.875;
    destination.pedal_drawbars = {8, 7};
    destination.route_enabled = {true, false};
    destination.percussion = {true, hammond::PercussionHarmonic::Third,
                             hammond::PercussionVolume::Soft, hammond::PercussionDecay::Fast};
    const auto before = destination;
    std::string error = "stale error";
    if (hammond::parse_controls(input, destination, error)) {
        throw std::runtime_error("Malformed controls accepted: " + std::string(label));
    }
    CHECK(!error.empty() && error != "stale error");
    same_snapshot(destination, before);
    ++rejected_inputs;
}

void rejected(const std::string& text, std::string_view label) {
    std::istringstream input(text);
    rejected(input, label);
}

void rejected(const ControlSnapshot& invalid) {
    std::string destination = "preserve these existing bytes\n";
    const auto before = destination;
    std::string error = "stale error";
    CHECK(!hammond::serialize_controls(invalid, destination, error));
    CHECK(destination == before);
    CHECK(!error.empty() && error != "stale error");
    ++rejected_inputs;
}

std::string joined(const Tokens& tokens, std::string_view separator = " ") {
    std::string result;
    for (const auto& token : tokens) result += token + std::string(separator);
    return result;
}

void test_roundtrip() {
    const auto varied = varied_snapshot();
    CHECK(encoded(varied) == kCanonicalV3);
    same_snapshot(accepted(std::string(kLegacyCanonical)), varied);
    CHECK(encoded(accepted(std::string(kLegacyCanonical))) == kCanonicalV3);
    same_snapshot(accepted(std::string(kCanonicalV2)), varied);
    CHECK(encoded(accepted(std::string(kCanonicalV2))) == kCanonicalV3);
    same_snapshot(accepted(std::string(kCanonicalV3)), varied);
    CHECK(encoded(accepted(std::string(kCanonicalV3))) == kCanonicalV3);
    CHECK(encoded(ControlSnapshot{}) ==
          "B3CONTROLS3\nexpression 1\n"
          "percussion enabled 0 harmonic second volume normal decay slow\n"
          "pedal drawbars 0 0\n"
          "manual upper selected B route_enabled 1\n"
          "bank A 0 0 0 0 0 0 0 0 0\nbank B 0 0 0 0 0 0 0 0 0\n"
          "manual lower selected B route_enabled 1\n"
          "bank A 0 0 0 0 0 0 0 0 0\nbank B 0 0 0 0 0 0 0 0 0\nend\n");
    for (const auto upper : {DrawbarBank::A, DrawbarBank::B}) {
        for (const auto lower : {DrawbarBank::A, DrawbarBank::B}) {
            for (bool upper_route : {false, true}) {
                for (bool lower_route : {false, true}) {
                    auto state = varied;
                    state.selected_banks = {upper, lower};
                    state.route_enabled = {upper_route, lower_route};
                    same_snapshot(accepted(encoded(state)), state);
                }
            }
        }
    }
    for (std::size_t manual = 0; manual < hammond::kManualCount; ++manual) {
        for (std::size_t bank = 0; bank < hammond::kDrawbarBankCount; ++bank) {
            for (std::size_t drawbar = 0; drawbar < hammond::kDrawbarCount; ++drawbar) {
                for (std::uint8_t position = 0; position <= 8; ++position) {
                    auto state = varied;
                    state.drawbars[manual][bank][drawbar] = position;
                    same_snapshot(accepted(encoded(state)), state);
                }
            }
        }
    }
    for (double expression : {0.0, -0.0, 1.0, 0.1, 0.12345678901234566,
                              std::nextafter(1.0, 0.0), std::numeric_limits<double>::min(),
                              std::numeric_limits<double>::denorm_min()}) {
        auto state = varied;
        state.expression = expression;
        same_snapshot(accepted(encoded(state)), state);
    }
    auto state = varied;
    state.expression = 0.1;
    CHECK(encoded(state).find("expression 0.10000000000000001\n") != std::string::npos);
    std::string aliased = "preserved alias";
    CHECK(!hammond::serialize_controls(varied, aliased, aliased));
    CHECK(aliased == "preserved alias");
}

void test_rounding_mode_isolation() {
    const int original_mode = std::fegetround();
    CHECK(original_mode != -1);
    // Fixed binary64 inputs are the round-trip oracle. Include the ordinary
    // expression that previously lost one ULP under downward/toward-zero output.
    constexpr std::array<std::uint64_t, 9> expressions{
        0x3fbfd7f684a99224ULL, 0x0000000000000000ULL, 0x8000000000000000ULL,
        0x0000000000000001ULL, 0x000fffffffffffffULL,
        0x0010000000000000ULL, 0x3fb999999999999aULL,
        0x3fefffffffffffffULL, 0x3ff0000000000000ULL};
    std::array<std::string, expressions.size()> nearest_bytes;
    CHECK(std::fesetround(FE_TONEAREST) == 0);
    for (std::size_t i = 0; i < expressions.size(); ++i) {
        auto state = varied_snapshot();
        state.expression = std::bit_cast<double>(expressions[i]);
        nearest_bytes[i] = encoded(state);
    }
    for (const int mode : {FE_TONEAREST, FE_DOWNWARD, FE_UPWARD, FE_TOWARDZERO}) {
        CHECK(std::fesetround(mode) == 0);
        for (std::size_t i = 0; i < expressions.size(); ++i) {
            auto state = varied_snapshot();
            state.expression = std::bit_cast<double>(expressions[i]);
            const auto bytes = encoded(state);
            CHECK(std::fegetround() == mode);
            const auto restored = accepted(bytes);
            CHECK(std::fegetround() == mode);
            CHECK(std::bit_cast<std::uint64_t>(restored.expression) == expressions[i]);
            CHECK(bytes == nearest_bytes[i]);
            same_snapshot(restored, state);
        }

        // Rejected serialization and parsing must preserve the mode and their
        // existing destination-atomicity/diagnostic contracts too.
        auto invalid = varied_snapshot();
        invalid.expression = std::bit_cast<double>(0x3ff0000000000001ULL);
        rejected(invalid);
        CHECK(std::fegetround() == mode);
        std::string aliased = "preserved alias";
        CHECK(!hammond::serialize_controls(varied_snapshot(), aliased, aliased));
        CHECK(aliased == "preserved alias");
        CHECK(std::fegetround() == mode);
        for (const auto canonical : {kLegacyCanonical, kCanonicalV2, kCanonicalV3}) {
            auto underflow = std::string(canonical);
            underflow.replace(underflow.find("0.375"), 5, "1e-9999");
            rejected(underflow, "nonzero expression underflow under caller rounding mode");
        }
        CHECK(std::fegetround() == mode);
    }
    CHECK(std::fesetround(original_mode) == 0);
}

void test_serialization_rejection() {
    for (double expression : {-0.001, std::nextafter(0.0, -1.0),
                              std::nextafter(1.0, 2.0), 1.001,
                              std::numeric_limits<double>::quiet_NaN(),
                              std::numeric_limits<double>::infinity(),
                              -std::numeric_limits<double>::infinity()}) {
        auto state = varied_snapshot();
        state.expression = expression;
        rejected(state);
    }
    for (std::size_t manual = 0; manual < hammond::kManualCount; ++manual) {
        for (unsigned selector : {2U, 127U, 255U}) {
            auto state = varied_snapshot();
            state.selected_banks[manual] = static_cast<DrawbarBank>(selector);
            rejected(state);
        }
        for (std::size_t bank = 0; bank < hammond::kDrawbarBankCount; ++bank) {
            for (std::size_t drawbar = 0; drawbar < hammond::kDrawbarCount; ++drawbar) {
                for (unsigned position : {9U, 255U}) {
                    auto state = varied_snapshot();
                    state.drawbars[manual][bank][drawbar] = static_cast<std::uint8_t>(position);
                    rejected(state);
                }
            }
        }
    }
}

void test_percussion_semantics_and_migration() {
    const std::string default_record =
        "percussion enabled 0 harmonic second volume normal decay slow\n";
    for (unsigned switches = 0; switches < 16; ++switches) {
        const bool enabled = (switches & 1U) != 0;
        const bool third = (switches & 2U) != 0;
        const bool soft = (switches & 4U) != 0;
        const bool fast = (switches & 8U) != 0;
        auto expected = varied_snapshot();
        expected.percussion = {
            enabled,
            third ? hammond::PercussionHarmonic::Third : hammond::PercussionHarmonic::Second,
            soft ? hammond::PercussionVolume::Soft : hammond::PercussionVolume::Normal,
            fast ? hammond::PercussionDecay::Fast : hammond::PercussionDecay::Slow};

        // Construct input from the documented names, independently of the writer.
        const std::string record = std::string("percussion enabled ") + (enabled ? "1" : "0") +
            " harmonic " + (third ? "third" : "second") +
            " volume " + (soft ? "soft" : "normal") +
            " decay " + (fast ? "fast" : "slow") + '\n';
        auto fixture = std::string(kCanonicalV2);
        fixture.replace(fixture.find(default_record), default_record.size(), record);
        same_snapshot(accepted(fixture), expected);
        auto current_fixture = std::string(kCanonicalV3);
        current_fixture.replace(current_fixture.find(default_record), default_record.size(), record);
        CHECK(encoded(expected) == current_fixture);
        same_snapshot(accepted(encoded(expected)), expected);

        // All previous percussion combinations must migrate to the same defaults.
        auto destination = expected;
        destination.expression = 0.875;
        destination.selected_banks = {DrawbarBank::B, DrawbarBank::A};
        destination.pedal_drawbars = {6, 8};
        std::istringstream legacy{std::string(kLegacyCanonical)};
        std::string error = "stale error";
        CHECK(hammond::parse_controls(legacy, destination, error));
        CHECK(error.empty());
        same_snapshot(destination, varied_snapshot());
        CHECK(!destination.percussion.enabled);
        CHECK(destination.percussion.harmonic == hammond::PercussionHarmonic::Second);
        CHECK(destination.percussion.volume == hammond::PercussionVolume::Normal);
        CHECK(destination.percussion.decay == hammond::PercussionDecay::Slow);
        CHECK(encoded(destination) == kCanonicalV3);
    }
}

void test_percussion_enum_rejection() {
    auto initial = varied_snapshot();
    initial.percussion = {true, hammond::PercussionHarmonic::Third,
                         hammond::PercussionVolume::Soft, hammond::PercussionDecay::Fast};
    hammond::ControlState controls;
    CHECK(controls.restore(initial));
    for (unsigned invalid : {2U, 127U, 255U}) {
        for (unsigned field = 0; field < 3; ++field) {
            auto candidate = initial;
            candidate.expression = 0.125;
            candidate.drawbars[0][0][0] = 8;
            candidate.route_enabled = {true, false};
            candidate.percussion.enabled = false;
            if (field == 0) {
                candidate.percussion.harmonic = static_cast<hammond::PercussionHarmonic>(invalid);
            } else if (field == 1) {
                candidate.percussion.volume = static_cast<hammond::PercussionVolume>(invalid);
            } else {
                candidate.percussion.decay = static_cast<hammond::PercussionDecay>(invalid);
            }
            rejected(candidate);
            CHECK(!controls.restore(candidate));
            same_snapshot(controls.snapshot(), initial);
            CHECK(!controls.set_percussion_settings(candidate.percussion));
            same_snapshot(controls.snapshot(), initial);
        }
    }
}

void test_version2_text_rejection(const Tokens& original) {
    auto change = [&](std::size_t at, std::string_view value) {
        auto tokens = original;
        tokens.at(at) = value;
        rejected(joined(tokens), "version 2 token " + std::to_string(at) + " = " + std::string(value));
    };
    for (const char* version : {"B3CONTROLS", "B3CONTROLS0", "B3CONTROLS1", "B3CONTROLS3",
                               "B3CONTROLS02", "B3CONTROLS2.0", "B3CONTROLS 2", "b3controls2"}) {
        change(0, version);
    }
    for (std::size_t at : {1U, 3U, 4U, 6U, 8U, 10U, 12U, 13U, 14U, 16U, 18U, 19U,
                           29U, 30U, 40U, 41U, 42U, 44U, 46U, 47U, 57U, 58U, 68U}) {
        change(at, "unknown");
    }
    for (const char* enabled : {"true", "false", "2", "-1", "+0", "00", "1.0", "on", "off"}) {
        change(5, enabled);
    }
    for (const char* harmonic : {"Second", "THIRD", "fourth", "2", "3", "0", "1", "secondthird"}) {
        change(7, harmonic);
    }
    for (const char* volume : {"Normal", "SOFT", "loud", "0", "1", "normalsoft"}) change(9, volume);
    for (const char* decay : {"Slow", "FAST", "medium", "0", "1", "slowfast"}) change(11, decay);
    for (std::size_t at : {15U, 43U}) change(at, "C");
    for (std::size_t at : {17U, 45U}) change(at, "2");
    for (std::size_t start : {20U, 31U, 48U, 59U}) {
        for (std::size_t offset = 0; offset < 9; ++offset) change(start + offset, "9");
    }
    for (const char* expression : {"nan", "inf", "1e9999", "1e-9999", "-0.001",
                                   "1.0000000000000002", "0,375", "0.375junk"}) change(2, expression);

    std::string prefix;
    for (const auto& token : original) {
        rejected(prefix, "version 2 truncated before " + token);
        prefix += token + ' ';
    }
    for (std::size_t at = 3; at < 12; ++at) {
        auto missing = original;
        missing.erase(missing.begin() + static_cast<Tokens::difference_type>(at));
        rejected(joined(missing), "missing percussion token");
    }
    auto missing_record = original;
    missing_record.erase(missing_record.begin() + 3, missing_record.begin() + 12);
    rejected(joined(missing_record), "version 2 cannot use implicit version 1 defaults");

    auto duplicate = original;
    duplicate.insert(duplicate.begin() + 12, original.begin() + 3, original.begin() + 12);
    rejected(joined(duplicate), "duplicate percussion record");
    for (std::size_t at : {4U, 6U, 8U, 10U}) {
        duplicate = original;
        const auto offset = static_cast<Tokens::difference_type>(at);
        duplicate.insert(duplicate.begin() + offset + 2,
                         original.begin() + offset, original.begin() + offset + 2);
        rejected(joined(duplicate), "duplicate percussion field");
    }
    duplicate = original;
    duplicate.insert(duplicate.begin() + 3, original.begin() + 1, original.begin() + 3);
    rejected(joined(duplicate), "version 2 duplicate expression");
    duplicate = original;
    duplicate.insert(duplicate.begin() + 40, original.begin() + 12, original.begin() + 40);
    rejected(joined(duplicate), "version 2 duplicate upper manual");
    auto reordered = original;
    std::swap(reordered[6], reordered[8]);
    std::swap(reordered[7], reordered[9]);
    rejected(joined(reordered), "percussion fields must follow declared order");
    for (const char* suffix : {"end", "percussion enabled 0 harmonic second volume normal decay slow",
                               "# comment", "extension 1"}) rejected(prefix + suffix, "version 2 trailing data");
    rejected(std::string("\xef\xbb\xbf") + prefix, "version 2 UTF-8 BOM");
    rejected(prefix + std::string(1, '\0'), "version 2 embedded NUL");
    rejected(prefix + std::string("\xc2\xa0"), "version 2 non-ASCII whitespace");
    auto exact = prefix;
    exact.resize(hammond::kMaxControlStateBytes, ' ');
    same_snapshot(accepted(exact), varied_snapshot());
    rejected(exact + ' ', "version 2 one byte over limit");
}

void test_text_rejection(const Tokens& original) {
    auto change = [&](std::size_t at, std::string_view value) {
        auto tokens = original;
        tokens.at(at) = value;
        rejected(joined(tokens), "token " + std::to_string(at) + " = " + std::string(value));
    };
    for (const char* version : {"B3CONTROLS", "B3CONTROLS0", "B3CONTROLS2", "B3CONTROLS01",
                               "B3CONTROLS1.0", "B3CONTROLS 1", "b3controls1"}) change(0, version);
    for (std::size_t at : {1U, 3U, 4U, 5U, 7U, 9U, 10U, 20U, 21U,
                           31U, 32U, 33U, 35U, 37U, 38U, 48U, 49U, 59U}) change(at, "unknown");
    for (std::size_t at : {6U, 34U}) {
        for (const char* bank : {"0", "1", "2", "C", "a", "b", "A#", "-1"}) change(at, bank);
    }
    for (std::size_t at : {8U, 36U}) {
        for (const char* bit : {"true", "false", "2", "-1", "+0", "00", "1.0"}) change(at, bit);
    }
    for (std::size_t start : {11U, 22U, 39U, 50U}) {
        for (std::size_t offset = 0; offset < 9; ++offset) change(start + offset, "9");
        for (const char* position : {"-1", "256", "4294967296", "+1", "01", "1.0",
                                     "nan", "inf", "0x1", "1junk"}) change(start, position);
    }
    for (const char* expression : {"nan", "NaN", "nan(1)", "inf", "Infinity", "-inf",
                                   "1e9999", "1e-9999", "-0.001", "1.0000000000000002",
                                   "0x1p-1", "0,375", "3e", ".", "+", "--1", "+-0",
                                   "++1", "0.375f", "1_0", "0.375junk"}) change(2, expression);
    std::string prefix;
    for (const auto& token : original) {
        rejected(prefix, "truncated before " + token);
        prefix += token + ' ';
    }
    for (const char* suffix : {"end", "# comment", "extension 1", "0"}) {
        rejected(prefix + suffix, "trailing data");
    }
    auto duplicate = original;
    duplicate.insert(duplicate.begin() + 3, original.begin() + 1, original.begin() + 3);
    rejected(joined(duplicate), "duplicate expression");
    duplicate = original;
    duplicate.insert(duplicate.begin() + 20, original.begin() + 9, original.begin() + 20);
    rejected(joined(duplicate), "duplicate upper A bank");
    duplicate = original;
    duplicate.insert(duplicate.begin() + 31, original.begin() + 3, original.begin() + 31);
    rejected(joined(duplicate), "duplicate upper manual");
    auto reordered = original;
    std::swap(reordered[4], reordered[32]);
    rejected(joined(reordered), "lower before upper");
    reordered = original;
    std::swap(reordered[10], reordered[21]);
    rejected(joined(reordered), "B before A");
    auto extra = original;
    extra.insert(extra.begin() + 20, "8");
    rejected(joined(extra), "ten positions in one bank");
    extra = original;
    extra.erase(extra.begin() + 19);
    rejected(joined(extra), "eight positions in one bank");
    rejected(std::string("\xef\xbb\xbf") + prefix, "UTF-8 BOM");
    rejected(prefix + std::string(1, '\0'), "embedded NUL");
    rejected(prefix + std::string("\xc2\xa0"), "non-ASCII whitespace");
    auto exact = prefix;
    exact.resize(hammond::kMaxControlStateBytes, ' ');
    same_snapshot(accepted(exact), varied_snapshot());
    rejected(exact + ' ', "one byte over limit");
    rejected(std::string(hammond::kMaxControlStateBytes + 1, ' '), "oversized whitespace");
    rejected(std::string(hammond::kMaxControlStateBytes + 1, 'x'), "oversized token");
}

void test_transport(const Tokens& tokens, std::string_view input_fixture) {
    struct CommaDecimal : std::numpunct<char> {
        char do_decimal_point() const override { return ','; }
    };
    const auto localized_locale = std::locale(std::locale::classic(), new CommaDecimal);
    std::istringstream localized(joined(tokens, " \t\r\n\f\v"));
    localized.imbue(localized_locale);
    same_snapshot(accepted(localized), varied_snapshot());
    CHECK(localized.getloc() == localized_locale);
    const auto old_global = std::locale::global(localized_locale);
    const auto canonical = encoded(varied_snapshot());
    std::locale::global(old_global);
    CHECK(canonical == kCanonicalV3);
    std::istringstream throwing{std::string(input_fixture)};
    const auto mask = std::ios::eofbit | std::ios::failbit | std::ios::badbit;
    throwing.exceptions(mask);
    same_snapshot(accepted(throwing), varied_snapshot());
    CHECK(throwing.exceptions() == mask);
    for (auto state : {std::ios::failbit, std::ios::badbit, std::ios::eofbit}) {
        std::istringstream failed{std::string(input_fixture)};
        failed.setstate(state);
        rejected(failed, "initial stream failure");
    }
    class FailingBuffer : public std::streambuf {
    public:
        FailingBuffer(std::string bytes, std::size_t stop, bool original_exception)
            : bytes_(std::move(bytes)), stop_(stop), original_exception_(original_exception) {}
    private:
        int_type underflow() override {
            if (at_ == stop_) {
                if (original_exception_) throw std::runtime_error("injected original read failure");
                throw std::ios_base::failure("injected read failure");
            }
            if (at_ == bytes_.size()) return traits_type::eof();
            byte_ = bytes_[at_++];
            setg(&byte_, &byte_, &byte_ + 1);
            return traits_type::to_int_type(byte_);
        }
        std::string bytes_;
        std::size_t stop_;
        bool original_exception_;
        std::size_t at_{0};
        char byte_{0};
    };
    for (bool exceptions : {false, true}) {
        for (bool original_exception : {false, true}) {
            for (std::size_t stop : {std::size_t{0}, input_fixture.size() / 2, input_fixture.size()}) {
                FailingBuffer buffer(std::string(input_fixture), stop, original_exception);
                std::istream interrupted(&buffer);
                if (exceptions) interrupted.exceptions(std::ios::badbit | std::ios::failbit);
                rejected(interrupted, "I/O failure before, during or after complete payload");
            }
        }
    }
    auto decimals = tokens;
    for (const char* expression : {"+3.75e-1", ".375", "0.3750", "000.375", "3.75E-01"}) {
        decimals[2] = expression;
        same_snapshot(accepted(joined(decimals)), varied_snapshot());
    }
    decimals[2] = "1.";
    auto expected = varied_snapshot();
    expected.expression = 1.0;
    same_snapshot(accepted(joined(decimals)), expected);
    const auto bytes = std::string(input_fixture);
    same_snapshot(accepted(bytes.substr(0, bytes.size() - 1)), varied_snapshot());
    std::istringstream oversized(bytes + std::string(hammond::kMaxControlStateBytes * 2, ' '));
    rejected(oversized, "bounded consumption");
    CHECK(oversized.tellg() == static_cast<std::streamoff>(hammond::kMaxControlStateBytes + 1));
}
} // namespace

int main() {
    try {
        std::istringstream fixture{std::string(kLegacyCanonical)};
        const Tokens tokens{std::istream_iterator<std::string>(fixture),
                            std::istream_iterator<std::string>()};
        CHECK(tokens.size() == 60);
        test_roundtrip();
        test_rounding_mode_isolation();
        test_serialization_rejection();
        test_text_rejection(tokens);
        test_transport(tokens, kLegacyCanonical);
        std::istringstream fixture_v2{std::string(kCanonicalV2)};
        const Tokens tokens_v2{std::istream_iterator<std::string>(fixture_v2),
                               std::istream_iterator<std::string>()};
        CHECK(tokens_v2.size() == 69);
        test_percussion_semantics_and_migration();
        test_percussion_enum_rejection();
        test_version2_text_rejection(tokens_v2);
        test_transport(tokens_v2, kCanonicalV2);
        std::istringstream fixture_v3{std::string(kCanonicalV3)};
        const Tokens tokens_v3{std::istream_iterator<std::string>(fixture_v3),
                               std::istream_iterator<std::string>()};
        CHECK(tokens_v3.size() == 73);
        test_transport(tokens_v3, kCanonicalV3);
        std::cout << "Control persistence tests passed; " << rejected_inputs
                  << " malformed inputs preserved destination semantics.\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Control persistence tests failed: " << error.what() << '\n';
        return 1;
    }
}
