#include "hammond/ParameterBridge.h"

#include <array>
#include <bit>
#include <cfenv>
#include <cstdint>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

namespace {

constexpr std::uint64_t one_bits = 0x3ff0000000000000ULL;
constexpr std::uint64_t negative_zero_bits = 0x8000000000000000ULL;
constexpr std::uint64_t poison_bits = 0x7ff800000000a021ULL;

void require(bool condition, std::string_view message) {
    if (!condition) throw std::runtime_error(std::string(message));
}

// Construct the normalized significand using integers only. For the small
// contract fractions, scaled_numerator < 44 and the shift fits uint64_t.
// This is independent of production literals and the older Fraction/binary
// search oracle. No floating division or ambient rounding participates.
std::uint64_t nearest_ratio_bits(std::uint64_t numerator, std::uint64_t denominator) {
    require(denominator != 0 && numerator <= denominator && denominator <= 22,
            "oracle ratio is outside its declared small nonnegative domain");
    if (numerator == 0) return 0;
    int exponent = 0;
    while (numerator < denominator) {
        numerator <<= 1U;
        --exponent;
    }
    const auto dividend = numerator << 52U;
    auto significand = dividend / denominator;
    const auto remainder = dividend % denominator;
    if (2U * remainder > denominator ||
        (2U * remainder == denominator && (significand & 1U) != 0)) {
        ++significand;
    }
    if (significand == (1ULL << 53U)) {
        significand >>= 1U;
        ++exponent;
    }
    return (static_cast<std::uint64_t>(exponent + 1023) << 52U) |
           (significand - (1ULL << 52U));
}

struct Mode {
    std::string_view name;
    int code;
};
constexpr std::array modes{
    Mode{"nearest", FE_TONEAREST}, Mode{"downward", FE_DOWNWARD},
    Mode{"upward", FE_UPWARD}, Mode{"towardzero", FE_TOWARDZERO}};

class RestoreRounding {
public:
    RestoreRounding() : original_(std::fegetround()) {
        require(original_ != -1, "cannot read caller rounding mode");
    }
    ~RestoreRounding() { static_cast<void>(std::fesetround(original_)); }
    int original() const { return original_; }

private:
    int original_;
};

struct Target {
    std::uint32_t id;
    hammond::EventType type;
    hammond::Manual manual;
    std::uint8_t steps;
};
constexpr std::array selectors{
    Target{20480, hammond::EventType::SelectPreset, hammond::Manual::Upper, 11},
    Target{20481, hammond::EventType::SelectPreset, hammond::Manual::Lower, 11}};
// One representative per unchanged kind; the Python test independently checks
// all 45 old records and the actual CLI's complete old-ID conversions.
constexpr std::array legacy{
    Target{4096, hammond::EventType::BankDrawbar, hammond::Manual::Upper, 8},
    Target{8192, hammond::EventType::Expression, hammond::Manual::Upper, 0},
    Target{8208, hammond::EventType::SelectBank, hammond::Manual::Upper, 1},
    Target{12288, hammond::EventType::Percussion, hammond::Manual::Upper, 1},
    Target{16384, hammond::EventType::PedalDrawbar, hammond::Manual::Lower, 8}};
constexpr std::array<std::uint32_t, 21> unknown_ids{
    0, 4095, 4105, 4111, 4121, 4127, 4137, 4143, 4153, 8191, 8193,
    8207, 8210, 12287, 12292, 16383, 16386, 20479, 20482,
    0x7fffffffU, 0xffffffffU};

struct Sample {
    std::string_view mode;
    char operation;
    std::uint32_t id;
    std::uint64_t input;
    std::uint64_t output;
};
std::vector<Sample> samples;
std::size_t rejected = 0;
std::size_t rejected_descriptors = 0;

double decode(std::uint64_t bits) { return std::bit_cast<double>(bits); }
std::uint64_t encode(double value) { return std::bit_cast<std::uint64_t>(value); }

void normalized(const Mode& mode, const Target& target, std::uint64_t input,
                std::uint64_t expected) {
    hammond::Event event{123, hammond::EventType::NoteOff,
                         hammond::Manual::Lower, 253, decode(poison_bits)};
    constexpr auto offset = std::numeric_limits<std::uint32_t>::max();
    require(hammond::normalized_to_event(target.id, decode(input), offset, event),
            "valid normalized conversion rejected");
    require(event.offset == offset && event.type == target.type &&
            event.manual == target.manual && event.index == 0 &&
            encode(event.value) == expected, "normalized event differs from integer oracle");
    require(std::fegetround() == mode.code, "normalized conversion changed caller mode");
    samples.push_back({mode.name, 'N', target.id, input, encode(event.value)});
}

void plain(const Mode& mode, const Target& target, std::uint64_t input,
           std::uint64_t expected) {
    double output = decode(poison_bits);
    require(hammond::plain_to_normalized(target.id, decode(input), output),
            "valid plain conversion rejected");
    require(encode(output) == expected, "plain normalization differs from integer oracle");
    require(std::fegetround() == mode.code, "plain conversion changed caller mode");
    samples.push_back({mode.name, 'P', target.id, input, encode(output)});
}

void reject_normalized(const Mode& mode, std::uint32_t id, std::uint64_t input) {
    hammond::Event event{0xabcdef12U, static_cast<hammond::EventType>(251),
                         static_cast<hammond::Manual>(252), 253, decode(poison_bits)};
    std::array<unsigned char, sizeof(event)> before{};
    std::memcpy(before.data(), &event, sizeof(event));
    require(!hammond::normalized_to_event(id, decode(input), 37, event),
            "invalid normalized conversion accepted");
    require(std::memcmp(before.data(), &event, sizeof(event)) == 0,
            "rejection changed Event destination bytes");
    require(std::fegetround() == mode.code, "normalized rejection changed caller mode");
    ++rejected;
}

void reject_plain(const Mode& mode, std::uint32_t id, std::uint64_t input) {
    double output = decode(poison_bits);
    require(!hammond::plain_to_normalized(id, decode(input), output),
            "invalid plain conversion accepted");
    require(encode(output) == poison_bits, "rejection changed plain destination bits");
    require(std::fegetround() == mode.code, "plain rejection changed caller mode");
    ++rejected;
}

void check_selectors(const Mode& mode) {
    for (const auto& target : selectors) {
        for (std::uint64_t k = 0; k < 11; ++k) {
            const auto boundary = nearest_ratio_bits(2 * k + 1, 22);
            normalized(mode, target, boundary - 1, encode(static_cast<double>(k)));
            normalized(mode, target, boundary, encode(static_cast<double>(k + 1)));
            normalized(mode, target, boundary + 1, encode(static_cast<double>(k + 1)));
        }
        for (std::uint64_t k = 0; k <= 11; ++k) {
            const auto canonical = nearest_ratio_bits(k, 11);
            const auto integer = encode(static_cast<double>(k));
            plain(mode, target, integer, canonical);
            normalized(mode, target, canonical, integer);
        }
        normalized(mode, target, negative_zero_bits, 0);
        plain(mode, target, negative_zero_bits, 0);
        normalized(mode, target, 1, 0);
        normalized(mode, target, 0x0010000000000000ULL, 0);
        normalized(mode, target, one_bits - 1, encode(11.0));

        constexpr std::array<std::uint64_t, 7> invalid_normalized{
            negative_zero_bits + 1, one_bits + 1, 0x4000000000000000ULL,
            0x7ff0000000000000ULL, 0xfff0000000000000ULL,
            0x7ff8000000001234ULL, 0xfff8000000005678ULL};
        for (const auto input : invalid_normalized) reject_normalized(mode, target.id, input);
        const std::array invalid_plain{
            negative_zero_bits + 1, encode(11.0) + 1, encode(12.0), encode(0.5),
            one_bits - 1, std::uint64_t{1}, std::uint64_t{0x7ff0000000000000ULL},
            std::uint64_t{0xfff0000000000000ULL}, std::uint64_t{0x7ff8000000001234ULL}};
        for (const auto input : invalid_plain) reject_plain(mode, target.id, input);
    }
}

void check_legacy(const Mode& mode) {
    constexpr auto half = 0x3fe0000000000000ULL;
    for (const auto& target : legacy) {
        normalized(mode, target, negative_zero_bits, target.steps == 0 ? negative_zero_bits : 0);
        normalized(mode, target, 1, target.steps == 0 ? 1 : 0);
        for (const auto input : {half - 1, half, half + 1}) {
            const double discrete = target.steps == 8 ? 4.0 : (input < half ? 0.0 : 1.0);
            normalized(mode, target, input, target.steps == 0 ? input : encode(discrete));
        }
        const auto maximum = target.steps == 8 ? encode(8.0) : one_bits;
        normalized(mode, target, one_bits, maximum);
        plain(mode, target, negative_zero_bits, negative_zero_bits);
        plain(mode, target, 0, 0);
        plain(mode, target, maximum, one_bits);
        if (target.steps == 8) plain(mode, target, encode(4.0), half);
        if (target.steps == 0) plain(mode, target, 0x3fd8000000000000ULL, 0x3fd8000000000000ULL);
    }
}

void check_unknown(const Mode& mode) {
    for (const auto id : unknown_ids) {
        hammond::ParameterDescriptor descriptor{
            37, "sentinel.path", "sentinel.kind", "sentinel.unit", -3.0, 0.5, 79,
            hammond::EventType::NoteOff, hammond::Manual::Lower, 241};
        std::array<unsigned char, sizeof(descriptor)> before{};
        std::memcpy(before.data(), &descriptor, sizeof(descriptor));
        require(!hammond::parameter_descriptor(id, descriptor), "unknown descriptor accepted");
        require(std::memcmp(before.data(), &descriptor, sizeof(descriptor)) == 0,
                "unknown ID changed descriptor destination bytes");
        require(std::fegetround() == mode.code, "descriptor rejection changed caller mode");
        ++rejected_descriptors;
        reject_normalized(mode, id, 0x3fe0000000000000ULL);
        reject_plain(mode, id, 0);
    }
}

void vectors() {
    std::cout << "preset-parameter-boundaries-v1\n";
    for (const auto& mode : modes) std::cout << "mode " << mode.name << ' ' << mode.code << '\n';
    for (const auto& sample : samples) {
        std::cout << "sample " << sample.mode << ' ' << sample.operation << ' ' << sample.id
                  << ' ' << std::hex << std::setfill('0') << std::setw(16) << sample.input
                  << ' ' << std::setw(16) << sample.output << std::dec << '\n';
    }
    std::cout << "complete " << samples.size() << ' ' << rejected << ' '
              << rejected_descriptors << '\n';
}

} // namespace

int main(int argc, char* argv[]) {
    try {
        const bool emit_vectors = argc == 2 && std::string_view(argv[1]) == "--vectors";
        require(argc == 1 || emit_vectors, "expected no arguments or --vectors");
        static_assert(std::numeric_limits<double>::is_iec559 &&
                      std::numeric_limits<double>::digits == 53 && sizeof(double) == 8);
        const RestoreRounding rounding;
        for (const auto& mode : modes) {
            require(std::fesetround(mode.code) == 0, "required rounding mode unavailable");
            check_selectors(mode);
            check_legacy(mode);
            check_unknown(mode);
        }
        require(std::fesetround(rounding.original()) == 0, "cannot restore caller rounding mode");
        if (emit_vectors) {
            vectors();
        } else {
            std::cout << samples.size() << " integer-oracle conversions, " << rejected
                      << " atomic conversion rejections, " << rejected_descriptors
                      << " unchanged unknown-ID descriptors; four rounding modes passed\n";
        }
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "test_preset_parameter_boundaries: " << error.what() << '\n';
        return 1;
    }
}
