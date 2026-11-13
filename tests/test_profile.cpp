#include "TestSupport.h"

#include <algorithm>
#include <array>
#include <fstream>
#include <iterator>
#include <locale>
#include <sstream>
#include <stdexcept>
#include <vector>

namespace {
using hammond::RuntimeProfile;
using hammond::Status;
using Tokens = std::vector<std::string>;
constexpr std::size_t kSourceStart = 20;
constexpr std::size_t kMapHeader = kSourceStart + 4 * hammond::kToneSourceCount;
constexpr std::size_t kMapStart = kMapHeader + 3;
std::size_t rejected_inputs = 0;

void same_profile(const RuntimeProfile& actual, const RuntimeProfile& expected) {
    CHECK(actual.profile_id == expected.profile_id);
    CHECK(actual.authoring_sha256 == expected.authoring_sha256);
    CHECK(actual.output_gain == expected.output_gain);
    CHECK(actual.drawbar_gains == expected.drawbar_gains);
    CHECK(actual.manual_map == expected.manual_map);
    for (std::size_t i = 0; i < actual.sources.size(); ++i) {
        CHECK(actual.sources[i].frequency_hz == expected.sources[i].frequency_hz);
        CHECK(actual.sources[i].peak_amplitude == expected.sources[i].peak_amplitude);
        CHECK(actual.sources[i].base_phase_turns == expected.sources[i].base_phase_turns);
    }
}

RuntimeProfile distinct_profile(const RuntimeProfile& nominal) {
    auto result = nominal;
    std::fill_n(result.authoring_sha256.begin(), hammond::kSha256HexLength, 'a');
    result.output_gain = 0.875;
    for (std::size_t p = 0; p < result.drawbar_gains.size(); ++p)
        result.drawbar_gains[p] = static_cast<double>(p) / 8.0;
    for (std::size_t i = 0; i < result.sources.size(); ++i) {
        const auto n = static_cast<double>(i);
        result.sources[i] = {100.25 + n, (n + 1.0) / 128.0, (n + 0.5) / 128.0};
    }
    for (std::size_t k = 0; k < result.manual_map.size(); ++k)
        for (std::size_t d = 0; d < result.manual_map[k].size(); ++d)
            result.manual_map[k][d] = static_cast<hammond::ToneId>(13 + (k * 9 + d) % 79);
    return result;
}

std::string encode(const RuntimeProfile& profile) {
    std::ostringstream out;
    out.imbue(std::locale::classic());
    out << std::setprecision(std::numeric_limits<double>::max_digits10)
        << "B3PROFILE 1\nprofile_id " << profile.profile_id.data()
        << "\nauthoring_sha256 " << profile.authoring_sha256.data()
        << "\noutput_gain " << profile.output_gain << "\ndrawbar_gains";
    for (double gain : profile.drawbar_gains) out << ' ' << gain;
    out << "\nsources 91\n";
    for (std::size_t i = 0; i < profile.sources.size(); ++i) {
        const auto& s = profile.sources[i];
        out << i + 1 << ' ' << s.frequency_hz << ' ' << s.peak_amplitude
            << ' ' << s.base_phase_turns << '\n';
    }
    out << "manual_map 61 9\n";
    for (const auto& row : profile.manual_map) {
        for (auto id : row) out << static_cast<unsigned>(id) << ' ';
        out << '\n';
    }
    return out.str() + "end\n";
}

RuntimeProfile accepted(std::istream& input) {
    RuntimeProfile result;
    std::string error = "stale error";
    if (!hammond::load_runtime_profile(input, result, error))
        throw std::runtime_error("Valid input rejected: " + error);
    CHECK(error.empty());
    return result;
}
RuntimeProfile accepted(const std::string& text) {
    std::istringstream input(text);
    return accepted(input);
}
void rejected(std::istream& input, const RuntimeProfile& before, std::string_view label) {
    auto destination = before;
    std::string error = "stale error";
    if (hammond::load_runtime_profile(input, destination, error))
        throw std::runtime_error("Malformed input accepted: " + std::string(label));
    CHECK(!error.empty() && error != "stale error");
    same_profile(destination, before); // Every field, without inspecting object padding.
    ++rejected_inputs;
}
void rejected(const std::string& text, const RuntimeProfile& before, std::string_view label) {
    std::istringstream input(text);
    rejected(input, before, label);
}
std::string joined(const Tokens& tokens, std::string_view separator = " ") {
    std::string result;
    for (const auto& token : tokens) result += token + std::string(separator);
    return result;
}

void test_nominal_values(const RuntimeProfile& profile) {
    // Rounded chromatic C1..B1 anchors, then exact binary octave scaling. This is
    // a separate numerical oracle from the compiler's per-tone pow expression.
    constexpr std::array<double, 12> pitches{
        32.703195662574829, 34.647828872109013, 36.708095989675945, 38.890872965260113,
        41.203444614108744, 43.653528929125486, 46.249302838954300, 48.999429497718661,
        51.913087197493143, 55.0, 58.270470189761244, 61.735412657015516};
    constexpr std::array<double, 9> gains{0.0, 0.08912509381337455, 0.12589254117941673,
        0.17782794100389228, 0.25118864315095801, 0.35481338923357547,
        0.50118723362727224, 0.70794578438413791, 1.0};
    CHECK(std::string_view(profile.profile_id.data()) == hammond::kNominalProfileId);
    CHECK(profile.output_gain == 0.03);
    for (std::size_t i = 0; i < profile.sources.size(); ++i) {
        const double expected = std::ldexp(pitches[i % 12], static_cast<int>(i / 12));
        CHECK_NEAR(profile.sources[i].frequency_hz, expected, expected * 2e-14);
        CHECK(profile.sources[i].peak_amplitude == 1.0);
        CHECK(profile.sources[i].base_phase_turns == 0.0);
    }
    CHECK(profile.sources[45].frequency_hz == 440.0);
    for (std::size_t p = 0; p < gains.size(); ++p)
        CHECK_NEAR(profile.drawbar_gains[p], gains[p], 2e-15);
    struct Row { std::size_t key; std::array<hammond::ToneId, 9> ids; };
    // First six rows are printed independently on atlas PDF p.102 (note02).
    // Remaining rows are calculated boundary regressions, not factory evidence.
    constexpr std::array<Row, 13> boundaries{{
        {1,  {13,20,13,25,32,37,41,44,49}}, {13, {13,32,25,37,44,49,53,56,61}},
        {43, {43,62,55,67,74,79,83,86,91}}, {44, {44,63,56,68,75,80,84,87,80}},
        {56, {56,75,68,80,87,80,84,87,80}}, {61, {61,80,73,85,80,85,89,80,85}},
        {12, {24,31,24,36,43,48,52,55,60}}, {48, {48,67,60,72,79,84,88,91,84}},
        {49, {49,68,61,73,80,85,89,80,85}}, {51, {51,70,63,75,82,87,91,82,87}},
        {52, {52,71,64,76,83,88,80,83,88}}, {55, {55,74,67,79,86,91,83,86,91}},
        {60, {60,79,72,84,91,84,88,91,84}}}};
    for (const auto& row : boundaries)
        if (profile.manual_map[row.key - 1] != row.ids)
            throw std::runtime_error("Manual boundary mismatch at key " + std::to_string(row.key));
    for (std::size_t k = 0; k < profile.manual_map.size(); ++k) {
        for (std::size_t d = 0; d < profile.manual_map[k].size(); ++d) {
            const auto id = profile.manual_map[k][d];
            CHECK(id >= 13 && id <= 91);
            if (k == 0) continue;
            const unsigned prior = profile.manual_map[k - 1][d];
            const unsigned next = k == 12 && d == 0 ? 13U : prior == 91 ? 80U : prior + 1;
            CHECK(id == next);
        }
    }
}

void test_text_boundary(const Tokens& original, const RuntimeProfile& before) {
    auto change = [&](std::size_t at, const std::string& value) {
        auto tokens = original;
        tokens.at(at) = value;
        rejected(joined(tokens), before, "token " + std::to_string(at) + " = " + value);
    };
    for (const char* version : {"0", "2", "-1", "01", "+1", "1.0", "4294967296"}) change(1, version);
    for (std::size_t at : {0U, 2U, 4U, 6U, 8U, 18U}) change(at, "unknown_record");
    change(kMapHeader, "unknown_map");
    change(original.size() - 1, "END");
    for (const std::string& id : {std::string("measured-v1"), std::string(64, 'a'), std::string(65, 'a')}) change(3, id);
    for (const std::string& digest : {std::string(63, '0'), std::string(65, '0'),
            std::string(64, 'A'), std::string(64, 'g'), std::string("0x") + std::string(62, '0')}) change(5, digest);
    for (const char* count : {"0", "90", "92", "+91", "091", "91.0"}) change(19, count);
    for (const char* count : {"60", "62", "061"}) change(kMapHeader + 1, count);
    for (const char* count : {"8", "10", "09"}) change(kMapHeader + 2, count);
    for (const char* number : {"nan", "NaN", "inf", "-inf", "1e9999", "1e-9999", "0x1p-1",
            "0,03", "3e", ".", "+", "--1", "0.03f", "1_0", "0.03junk", "-0.01", "1.01"}) change(7, number);
    for (std::size_t p = 0; p < 9; ++p)
        for (const char* value : {"nan", "-0.01", "1.01"}) change(9 + p, value);
    change(9, "0.000001");
    change(17, "0.999999");
    for (std::size_t i = 0; i < 91; ++i) {
        const auto at = kSourceStart + i * 4;
        change(at, std::to_string(i)); // Duplicate, missing, or zero ID at every row.
        for (const char* hz : {"0", "-0", "-1", "nan"}) change(at + 1, hz);
        for (const char* peak : {"-0.01", "1.01", "inf"}) change(at + 2, peak);
        for (const char* phase : {"-0.01", "1", "nan"}) change(at + 3, phase);
    }
    for (const char* id : {"92", "256", "4294967296", "999999999999999999999", "+1", "-1", "1.0", "0x1"}) change(kSourceStart, id);
    for (std::size_t at = kMapStart; at < original.size() - 1; ++at) change(at, "12");
    for (const char* id : {"0", "92", "255", "256", "4294967296", "-1", "+13", "13.0"}) change(kMapStart, id);
    std::string prefix;
    for (const auto& token : original) {
        rejected(prefix, before, "truncated before " + token);
        prefix += token + ' ';
    }
    for (const char* suffix : {"end", "# comment", "extension 1", "0"}) rejected(prefix + suffix, before, "trailing record");
    auto duplicate = original;
    duplicate.insert(duplicate.begin() + 4, {"profile_id", original[3]});
    rejected(joined(duplicate), before, "duplicate metadata");
    auto reordered = original;
    std::swap(reordered[6], reordered[8]);
    rejected(joined(reordered), before, "out-of-order record");
    rejected(std::string("\xef\xbb\xbf") + prefix, before, "UTF-8 BOM");
    rejected(prefix + std::string(1, '\0'), before, "embedded NUL");
    rejected(prefix + std::string("\xc2\xa0"), before, "non-ASCII whitespace");
    for (bool little_endian : {false, true}) {
        std::string utf16;
        for (char c : prefix) { utf16 += little_endian ? c : '\0'; utf16 += little_endian ? '\0' : c; }
        rejected(utf16, before, "UTF-16 bytes are not the ASCII text contract");
    }
    auto exact = prefix;
    CHECK(exact.size() < hammond::kMaxCompiledProfileBytes);
    exact.resize(hammond::kMaxCompiledProfileBytes, ' ');
    same_profile(accepted(exact), accepted(prefix));
    rejected(exact + ' ', before, "one byte over exact limit");
    rejected(std::string(hammond::kMaxCompiledProfileBytes + 1, ' '), before, "oversized whitespace");
}

void test_transport(const Tokens& tokens, const RuntimeProfile& nominal) {
    struct CommaDecimal : std::numpunct<char> { char do_decimal_point() const override { return ','; } };
    std::istringstream localized(joined(tokens, " \t\r\n\f\v"));
    localized.imbue(std::locale(std::locale::classic(), new CommaDecimal));
    same_profile(accepted(localized), nominal);
    CHECK(std::use_facet<std::numpunct<char>>(localized.getloc()).decimal_point() == ',');
    std::istringstream throwing(joined(tokens));
    throwing.exceptions(std::ios::eofbit | std::ios::failbit | std::ios::badbit);
    same_profile(accepted(throwing), nominal);
    for (auto state : {std::ios::failbit, std::ios::badbit}) {
        std::istringstream failed(joined(tokens));
        failed.setstate(state);
        rejected(failed, nominal, "failed input stream");
    }
    class FailingBuffer : public std::streambuf {
    public:
        explicit FailingBuffer(std::string bytes) : bytes_(std::move(bytes)) {}
    private:
        int_type underflow() override {
            if (at_ == bytes_.size() / 2) throw std::ios_base::failure("injected read failure");
            if (at_ == bytes_.size()) return traits_type::eof();
            byte_ = bytes_[at_++];
            setg(&byte_, &byte_, &byte_ + 1);
            return traits_type::to_int_type(byte_);
        }
        std::string bytes_;
        std::size_t at_{0};
        char byte_{0};
    };
    for (bool exceptions : {false, true}) {
        FailingBuffer buffer(joined(tokens));
        std::istream interrupted(&buffer);
        if (exceptions) interrupted.exceptions(std::ios::badbit | std::ios::failbit);
        rejected(interrupted, distinct_profile(nominal), "I/O failure after partial read");
    }
    auto decimals = tokens;
    decimals[7] = "+3e-2";
    decimals[9] = "-0";
    decimals[17] = "1.";
    decimals[kSourceStart + 2] = ".5";
    auto expected = nominal;
    expected.sources[0].peak_amplitude = 0.5;
    same_profile(accepted(joined(decimals)), expected);
    const auto varied = distinct_profile(nominal);
    same_profile(accepted(encode(varied)), varied); // Check all numeric fields and all 549 stored IDs.
    auto digest_only = tokens;
    digest_only[5] = std::string(64, '0');
    expected = nominal;
    std::fill_n(expected.authoring_sha256.begin(), 64, '0');
    same_profile(accepted(joined(digest_only)), expected); // Syntax only; Python owns provenance.
    digest_only[kSourceStart + 1] = "48000";
    const auto high_frequency = accepted(joined(digest_only));
    CHECK(hammond::validate_runtime_profile(high_frequency, 96000) == Status::InvalidProfile);
    std::string error = "stale error";
    auto destination = varied;
    CHECK(hammond::load_runtime_profile_file(HAMMOND_TEST_PROFILE, destination, error));
    CHECK(error.empty());
    same_profile(destination, nominal);
    destination = varied;
    error = "stale error";
    const auto missing = std::filesystem::path(HAMMOND_TEST_PROFILE) / "nonexistent-child.b3p";
    CHECK(!hammond::load_runtime_profile_file(missing, destination, error));
    CHECK(!error.empty() && error != "stale error");
    same_profile(destination, varied);
}

void test_runtime_validation(const RuntimeProfile& nominal) {
    const auto nan = std::numeric_limits<double>::quiet_NaN();
    const auto inf = std::numeric_limits<double>::infinity();
    const auto tiny = std::numeric_limits<double>::denorm_min();
    CHECK(hammond::validate_runtime_profile(RuntimeProfile{}, 48000) == Status::InvalidProfile);
    for (double rate : {0.0, -1.0, 22050.0, 44100.5, 48000.1, 192000.0, nan, inf, -inf}) {
        CHECK(!hammond::is_supported_sample_rate(rate));
        CHECK(hammond::validate_runtime_profile(nominal, rate) == Status::InvalidSpec);
    }
    auto invalid = [&](const RuntimeProfile& p) { CHECK(hammond::validate_runtime_profile(p, 48000) == Status::InvalidProfile); };
    auto valid = [&](const RuntimeProfile& p) { CHECK(hammond::validate_runtime_profile(p, 48000) == Status::Ok); };
    valid(distinct_profile(nominal)); // Runtime safety is distinct from Python's nominal-model validation.
    for (double rate : {44100.0, 48000.0, 96000.0}) {
        CHECK(hammond::is_supported_sample_rate(rate));
        CHECK(hammond::validate_runtime_profile(nominal, rate) == Status::Ok);
        for (std::size_t i = 0; i < 91; ++i) {
            auto p = nominal;
            for (double hz : {rate * 0.5, std::nextafter(rate * 0.5, inf)}) {
                p.sources[i].frequency_hz = hz;
                CHECK(hammond::validate_runtime_profile(p, rate) == Status::InvalidProfile);
            }
            p.sources[i].frequency_hz = std::nextafter(rate * 0.5, 0.0);
            CHECK(hammond::validate_runtime_profile(p, rate) == Status::Ok);
        }
    }
    for (double v : {-tiny, 1.000001, nan, inf, -inf}) {
        auto p = nominal; p.output_gain = v; invalid(p);
        for (std::size_t i = 0; i < 9; ++i) { p = nominal; p.drawbar_gains[i] = v; invalid(p); }
    }
    for (double v : {0.0, 1.0}) { auto p = nominal; p.output_gain = v; valid(p); }
    for (std::size_t i = 0; i < 91; ++i) {
        for (double v : {0.0, -tiny, nan, inf, -inf}) { auto p = nominal; p.sources[i].frequency_hz = v; invalid(p); }
        for (double v : {-tiny, 1.000001, nan, inf, -inf}) { auto p = nominal; p.sources[i].peak_amplitude = v; invalid(p); }
        for (double v : {-tiny, 1.0, nan, inf, -inf}) { auto p = nominal; p.sources[i].base_phase_turns = v; invalid(p); }
        auto p = nominal;
        p.sources[i] = {tiny, 0.0, std::nextafter(1.0, 0.0)};
        valid(p);
    }
    for (std::size_t k = 0; k < 61; ++k)
        for (std::size_t d = 0; d < 9; ++d)
            for (unsigned id : {0U, 12U, 92U, 255U}) {
                auto p = nominal; p.manual_map[k][d] = static_cast<hammond::ToneId>(id); invalid(p);
            }
    auto p = nominal; p.drawbar_gains.front() = tiny; invalid(p);
    p = nominal; p.drawbar_gains.back() = std::nextafter(1.0, 0.0); invalid(p);
    for (std::size_t i = 0; i < p.profile_id.size(); ++i) { p = nominal; p.profile_id[i] = 'X'; invalid(p); }
    for (std::size_t i = 0; i < p.authoring_sha256.size(); ++i) { p = nominal; p.authoring_sha256[i] = 'G'; invalid(p); }
}

void test_domains() {
    for (unsigned id = 0; id <= 255; ++id) {
        std::size_t destination = 999;
        const bool ok = hammond::tone_id_to_index(static_cast<hammond::ToneId>(id), destination);
        CHECK(ok == (id >= 1 && id <= 91));
        CHECK(destination == (ok ? static_cast<std::size_t>(id - 1) : 999));
        const auto manual = static_cast<hammond::Manual>(id);
        CHECK(hammond::is_valid_manual(manual) == (id <= 1));
    }
    for (std::uint32_t note : {0U, 35U, 36U, 37U, 95U, 96U, 97U, 127U, 255U, 65536U, UINT32_MAX}) {
        std::size_t destination = 999;
        const bool ok = hammond::manual_midi_to_key_index(note, destination);
        CHECK(ok == (note >= 36 && note <= 96));
        CHECK(destination == (ok ? static_cast<std::size_t>(note - 36) : 999));
    }
}
} // namespace

int main() {
    try {
        const auto nominal = load_test_profile();
        std::ifstream input(HAMMOND_TEST_PROFILE, std::ios::binary);
        CHECK(input.is_open());
        const Tokens tokens{std::istream_iterator<std::string>(input), std::istream_iterator<std::string>()};
        CHECK(tokens.size() == kMapStart + 61 * 9 + 1);
        test_nominal_values(nominal);
        test_text_boundary(tokens, distinct_profile(nominal));
        test_transport(tokens, nominal);
        test_runtime_validation(nominal);
        test_domains();
        std::cout << "Profile boundary tests passed; " << rejected_inputs
                  << " malformed inputs preserved every destination field.\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Profile boundary tests failed: " << error.what() << '\n';
        return 1;
    }
}
