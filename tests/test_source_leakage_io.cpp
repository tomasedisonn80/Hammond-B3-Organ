#include "TestSupport.h"
#include "hammond/SourceLeakage.h"

#include <algorithm>
#include <array>
#include <bit>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <locale>
#include <sstream>
#include <stdexcept>
#include <streambuf>
#include <system_error>
#include <utility>
#include <vector>

namespace {

using hammond::SourceLeakageProfile;
using Tokens = std::vector<std::string>;
constexpr std::size_t kEdgeStart = 17;
constexpr std::size_t kEdgeTokens = 7;
constexpr std::string_view kDigest =
    "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef";
std::size_t rejected_inputs = 0;

std::string header(std::size_t edge_count) {
    return "B3LEAKAGE1\nmodel static-source-leakage-v1\n"
           "profile_id synthetic-pair-demo-v1\nevidence_status synthetic\n"
           "boundary normalized-generator-precontact-v1\n"
           "source_content excludes-leakage\nauthoring_sha256 " + std::string(kDigest) +
           "\nsource_count 91\nedge_count " + std::to_string(edge_count) + "\n";
}

std::string fixture() {
    return header(2) + "edge destination 25 source 37 gain 0.0625\n"
                       "edge destination 37 source 25 gain -0.03125\nend\n";
}

std::string single_edge(std::string_view gain) {
    return header(1) + "edge destination 91 source 1 gain " + std::string(gain) + "\nend\n";
}

Tokens split(const std::string& bytes) {
    std::istringstream input(bytes);
    input.imbue(std::locale::classic());
    Tokens result;
    for (std::string token; input >> token;) {
        result.push_back(std::move(token));
    }
    return result;
}

std::string join(const Tokens& tokens, std::string_view separator = "\n") {
    std::string result;
    for (const auto& token : tokens) {
        result += token;
        result += separator;
    }
    return result;
}

void same_profile(const SourceLeakageProfile& actual, const SourceLeakageProfile& expected) {
    CHECK(actual.profile_id == expected.profile_id);
    CHECK(actual.authoring_sha256 == expected.authoring_sha256);
    CHECK(actual.edge_count == expected.edge_count);
    // Include unused slots and signed-zero bits without comparing object padding.
    for (std::size_t i = 0; i < actual.edges.size(); ++i) {
        CHECK(actual.edges[i].source == expected.edges[i].source);
        CHECK(actual.edges[i].destination == expected.edges[i].destination);
        CHECK(std::bit_cast<std::uint64_t>(actual.edges[i].gain) ==
              std::bit_cast<std::uint64_t>(expected.edges[i].gain));
    }
}

SourceLeakageProfile accepted(std::istream& input) {
    SourceLeakageProfile result{};
    std::string error = "stale error";
    if (!hammond::load_source_leakage_profile(input, result, error)) {
        throw std::runtime_error("Valid leakage input rejected: " + error);
    }
    CHECK(error.empty());
    CHECK(hammond::validate_source_leakage_profile(result) == hammond::Status::Ok);
    return result;
}

SourceLeakageProfile accepted(const std::string& bytes) {
    std::istringstream input(bytes);
    return accepted(input);
}

void rejected(std::istream& input, const SourceLeakageProfile& before,
              std::string_view label) {
    auto destination = before;
    std::string error = "stale error";
    if (hammond::load_source_leakage_profile(input, destination, error)) {
        throw std::runtime_error("Malformed leakage input accepted: " + std::string(label));
    }
    CHECK(!error.empty());
    CHECK(error != "stale error");
    same_profile(destination, before);
    ++rejected_inputs;
}

void rejected(const std::string& bytes, const SourceLeakageProfile& before,
              std::string_view label) {
    std::istringstream input(bytes);
    rejected(input, before, label);
}

SourceLeakageProfile sentinel() {
    auto result = accepted(single_edge("-0.125"));
    result.authoring_sha256[0] = 'a';
    for (std::size_t i = result.edge_count; i < result.edges.size(); ++i) {
        result.edges[i] = {12, 13, i % 2 == 0 ? -0.0 : 0.03125};
    }
    return result;
}

void test_valid_forms(const Tokens& original) {
    const auto expected = accepted(fixture());
    CHECK(std::string_view(expected.profile_id.data()) == "synthetic-pair-demo-v1");
    CHECK(std::string_view(expected.authoring_sha256.data()) == kDigest);
    CHECK(expected.edge_count == 2);
    CHECK(expected.edges[0].destination == 25);
    CHECK(expected.edges[0].source == 37);
    CHECK(expected.edges[0].gain == 0.0625);
    CHECK(expected.edges[1].destination == 37);
    CHECK(expected.edges[1].source == 25);
    CHECK(expected.edges[1].gain == -0.03125);
    for (std::size_t i = std::string_view(expected.profile_id.data()).size();
         i < expected.profile_id.size(); ++i) {
        CHECK(expected.profile_id[i] == '\0');
    }
    CHECK(expected.authoring_sha256.back() == '\0');
    for (std::size_t i = expected.edge_count; i < expected.edges.size(); ++i) {
        CHECK(expected.edges[i].source == 0);
        CHECK(expected.edges[i].destination == 0);
        CHECK(std::bit_cast<std::uint64_t>(expected.edges[i].gain) == 0);
    }
    same_profile(accepted(join(original, " \t\r\n\f\v")), expected);
    same_profile(accepted(join(original, "\r\n")), expected);
    auto no_final_newline = fixture();
    no_final_newline.pop_back();
    same_profile(accepted(no_final_newline), expected);

    auto padded = original;
    padded[14] = "00091";
    padded[16] = "0002";
    padded[19] = "00025";
    padded[21] = "00037";
    padded[23] = "+.0625";
    padded[30] = "-3125.E-5";
    same_profile(accepted(join(padded)), expected);
    for (const std::string& id : {std::string("synthetic-a"), std::string("synthetic-0-"),
                                 std::string("synthetic-") + std::string(54, 'a')}) {
        auto changed = original;
        changed[4] = id;
        const auto profile = accepted(join(changed));
        CHECK(std::string_view(profile.profile_id.data()) == id);
    }
    auto longest_integer = original;
    longest_integer[14] = std::string(126, '0') + "91";
    same_profile(accepted(join(longest_integer)), expected);
    auto longest_gain = original;
    longest_gain[23] = "0.0625" + std::string(122, '0');
    same_profile(accepted(join(longest_gain)), expected);

    const auto empty = accepted(header(0) + "end\n");
    CHECK(empty.edge_count == 0);
    for (const auto& edge : empty.edges) {
        CHECK(edge.source == 0 && edge.destination == 0 && edge.gain == 0.0);
    }
    std::string maximum = header(hammond::kMaxSourceLeakageEdges);
    for (std::size_t destination = 1; destination <= 91; ++destination) {
        std::size_t added = 0;
        for (std::size_t source = 1; added < 8; ++source) {
            if (source == destination) continue;
            maximum += "edge destination " + std::to_string(destination) + " source " +
                       std::to_string(source) + " gain 0.015625\n";
            ++added;
        }
    }
    CHECK(accepted(maximum + "end\n").edge_count == hammond::kMaxSourceLeakageEdges);

    struct CommaDecimal final : std::numpunct<char> {
        char do_decimal_point() const override { return ','; }
    };
    std::istringstream localized(fixture());
    localized.imbue(std::locale(std::locale::classic(), new CommaDecimal));
    same_profile(accepted(localized), expected);
    CHECK(std::use_facet<std::numpunct<char>>(localized.getloc()).decimal_point() == ',');
}

void test_malformed(const Tokens& original, const SourceLeakageProfile& before) {
    const auto change = [&](std::size_t position, const std::string& value) {
        auto tokens = original;
        tokens.at(position) = value;
        rejected(join(tokens), before, "token " + std::to_string(position) + " = " + value);
    };
    for (std::size_t at : {0U, 1U, 3U, 5U, 7U, 9U, 11U, 13U, 15U,
                           17U, 18U, 20U, 22U, 24U, 25U, 27U, 29U, 31U}) {
        change(at, "unknown_record");
    }
    change(0, "B3LEAKAGE2");
    change(2, "static-source-leakage-v2");
    change(6, "measured");
    change(8, "post-contact");
    change(10, "includes-leakage");
    for (const std::string& id : {std::string("synthetic-"), std::string("Synthetic-a"),
                                 std::string("synthetic--a"), std::string("synthetic-a_b"),
                                 std::string("measured-a"),
                                 std::string("synthetic-") + std::string(55, 'a')}) {
        change(4, id);
    }
    for (const std::string& digest : {std::string(63, '0'), std::string(65, '0'),
                                     std::string(64, 'A'), std::string(64, 'g')}) {
        change(12, digest);
    }
    for (std::size_t at : {14U, 16U, 19U, 21U, 26U, 28U}) {
        for (const char* number : {"+1", "-1", "1.0", "1e0", "0x1", "4294967296"}) {
            change(at, number);
        }
        change(at, std::string(128, '0') + "1");
    }
    for (const char* count : {"0", "90", "92"}) change(14, count);
    for (const char* count : {"0", "1", "3", "729"}) change(16, count);
    for (std::size_t at : {19U, 21U, 26U, 28U}) {
        for (const char* id : {"0", "92", "256", "281"}) change(at, id);
    }
    for (const char* number : {"0", "-0", "0e99999", "nan", "NaN", "inf", "-inf",
                              "1e99999", "1e-99999", "0x1p-4", "0,0625", ".", "+",
                              "--1", "1e", "1e+", "0.1f", "1_0", "0.251", "-0.251"}) {
        change(23, number);
    }
    change(23, "0.0625" + std::string(123, '0'));
    change(21, "25"); // Self-edge.
    auto duplicate = original;
    std::copy_n(original.begin() + static_cast<std::ptrdiff_t>(kEdgeStart), kEdgeTokens,
                duplicate.begin() + static_cast<std::ptrdiff_t>(kEdgeStart + kEdgeTokens));
    rejected(join(duplicate), before, "duplicate pair");
    auto reversed = original;
    std::swap_ranges(reversed.begin() + static_cast<std::ptrdiff_t>(kEdgeStart),
                     reversed.begin() + static_cast<std::ptrdiff_t>(kEdgeStart + kEdgeTokens),
                     reversed.begin() + static_cast<std::ptrdiff_t>(kEdgeStart + kEdgeTokens));
    rejected(join(reversed), before, "descending destinations");
    auto reversed_sources = original;
    reversed_sources[26] = "25";
    reversed_sources[28] = "24";
    rejected(join(reversed_sources), before, "descending donors in one destination");
    auto repeated_metadata = original;
    repeated_metadata.insert(repeated_metadata.begin() + 5, {"profile_id", original[4]});
    rejected(join(repeated_metadata), before, "duplicate metadata");
    auto reordered = original;
    std::swap(reordered[5], reordered[7]);
    std::swap(reordered[6], reordered[8]);
    rejected(join(reordered), before, "reordered metadata");
    std::string prefix;
    for (const auto& token : original) {
        rejected(prefix, before, "truncated before " + token);
        prefix += token + '\n';
    }
    for (const char* suffix : {"end", "# comment", "extension 1", "0"}) {
        rejected(prefix + suffix, before, "trailing data");
    }
    for (const std::string& invalid_byte : {std::string(1, '\0'), std::string("\xc2\xa0"),
                                          std::string("\xef\xbb\xbf"), std::string(1, '\x01')}) {
        rejected(prefix + invalid_byte, before, "invalid byte after end");
        rejected(invalid_byte + prefix, before, "invalid byte before header");
    }
    auto inside_number = original;
    inside_number[23].insert(3, 1, '\0');
    rejected(join(inside_number), before, "NUL inside gain");
    std::string ninth = header(9);
    for (int source = 1; source <= 9; ++source) {
        ninth += "edge destination 91 source " + std::to_string(source) + " gain 0.015625\n";
    }
    rejected(ninth + "end\n", before, "ninth incoming edge");
    rejected(header(3) + "edge destination 91 source 1 gain 0.25\n"
                         "edge destination 91 source 2 gain -0.25\n"
                         "edge destination 91 source 3 gain 0.125\nend\n",
             before, "excessive absolute row sum");
}

void test_numeric_boundaries(const SourceLeakageProfile& before) {
    // These are the compiler's .17g round-trip tokens, with independent binary
    // endpoint expectations. In particular, subnormal failbit is not underflow.
    const std::array<std::pair<std::string_view, double>, 7> cases{{
        {"4.9406564584124654e-324", std::numeric_limits<double>::denorm_min()},
        {"-4.9406564584124654e-324", -std::numeric_limits<double>::denorm_min()},
        {"2.2250738585072014e-308", std::numeric_limits<double>::min()},
        {"2.2250738585072009e-308",
         std::nextafter(std::numeric_limits<double>::min(), 0.0)},
        {"3e-324", std::numeric_limits<double>::denorm_min()},
        {"0.25", 0.25}, {"-0.25", -0.25}
    }};
    for (const auto& [token, expected] : cases) {
        CHECK(std::bit_cast<std::uint64_t>(accepted(single_edge(token)).edges[0].gain) ==
              std::bit_cast<std::uint64_t>(expected));
    }
    for (const char* token : {"2e-324", "-2e-324", "1e-99999", "0.25000000000000006"}) {
        rejected(single_edge(token), before, "unrepresentable or excessive gain");
    }
    const auto canonical_row = [](bool small_first) {
        std::string text = header(8);
        for (std::size_t source = 1; source <= 8; ++source) {
            const bool large = small_first ? source >= 7 : (source == 1 || source == 8);
            text += "edge destination 91 source " + std::to_string(source) + " gain " +
                    (large ? "0.25" : "1.3877787807814457e-17") + "\n";
        }
        return text + "end\n";
    };
    CHECK(accepted(canonical_row(false)).edge_count == 8);
    rejected(canonical_row(true), before, "canonical row rounds above 0.5");
}

enum class InjectedFailure { Io, Standard, Nonstandard };

class FailingBuffer final : public std::streambuf {
public:
    FailingBuffer(std::string bytes, std::size_t fail_at, InjectedFailure failure)
        : bytes_(std::move(bytes)), fail_at_(fail_at), failure_(failure) {}
private:
    int_type underflow() override {
        if (at_ == fail_at_) {
            switch (failure_) {
            case InjectedFailure::Io: throw std::ios_base::failure("injected read error");
            case InjectedFailure::Standard: throw std::runtime_error("injected read error");
            case InjectedFailure::Nonstandard: throw 17;
            }
        }
        if (at_ == bytes_.size()) return traits_type::eof();
        byte_ = bytes_[at_++];
        setg(&byte_, &byte_, &byte_ + 1);
        return traits_type::to_int_type(byte_);
    }
    std::string bytes_;
    std::size_t fail_at_;
    InjectedFailure failure_;
    std::size_t at_{0};
    char byte_{0};
};

void test_transport(const SourceLeakageProfile& before) {
    const auto bytes = fixture();
    const auto expected = accepted(bytes);
    for (auto mask : {std::ios::eofbit, std::ios::failbit,
                      std::ios::badbit | std::ios::failbit | std::ios::eofbit}) {
        std::istringstream throwing(bytes);
        throwing.exceptions(mask);
        same_profile(accepted(throwing), expected);
        CHECK(throwing.exceptions() == mask);
    }
    for (auto state : {std::ios::failbit, std::ios::badbit, std::ios::eofbit}) {
        std::istringstream failed(bytes);
        failed.setstate(state);
        rejected(failed, before, "already failed stream");
    }
    std::istream missing_buffer(nullptr);
    rejected(missing_buffer, before, "null stream buffer");
    for (auto failure : {InjectedFailure::Io, InjectedFailure::Standard,
                         InjectedFailure::Nonstandard}) {
        for (std::size_t fail_at : {bytes.size() / 2, bytes.size()}) {
            for (bool exceptions : {false, true}) {
                FailingBuffer buffer(bytes, fail_at, failure);
                std::istream input(&buffer);
                if (exceptions) input.exceptions(std::ios::badbit | std::ios::failbit);
                rejected(input, before, "I/O failure during read or after complete end");
                CHECK(input.bad());
            }
        }
    }
    auto exact = bytes;
    exact.resize(hammond::kMaxCompiledSourceLeakageBytes, ' ');
    same_profile(accepted(exact), expected);
    rejected(exact + ' ', before, "one byte over limit");
    rejected(std::string(hammond::kMaxCompiledSourceLeakageBytes + 1, ' '), before,
             "oversized whitespace");
    std::istringstream huge(exact + std::string(hammond::kMaxCompiledSourceLeakageBytes, ' '));
    rejected(huge, before, "bounded read stops after limit plus one byte");
    CHECK(huge.tellg() == static_cast<std::streamoff>(hammond::kMaxCompiledSourceLeakageBytes + 1));
}

class TemporaryDirectory {
public:
    TemporaryDirectory() {
        const auto stamp = std::chrono::steady_clock::now().time_since_epoch().count();
        for (unsigned attempt = 0; attempt < 100; ++attempt) {
            path_ = std::filesystem::temp_directory_path() /
                    ("hammond-source-leakage-io-" + std::to_string(stamp) + "-" +
                     std::to_string(attempt));
            std::error_code error;
            if (std::filesystem::create_directory(path_, error)) return;
            if (error) throw std::runtime_error("Cannot create leakage test directory: " + error.message());
        }
        throw std::runtime_error("Cannot allocate unique leakage test directory");
    }
    ~TemporaryDirectory() {
        std::error_code ignored;
        std::filesystem::remove_all(path_, ignored);
    }
    const std::filesystem::path& path() const noexcept { return path_; }
private:
    std::filesystem::path path_;
};

void test_file(const SourceLeakageProfile& before) {
    const TemporaryDirectory directory;
    const auto path = directory.path() / "fixture.b3l";
    {
        std::ofstream output(path, std::ios::binary);
        output << fixture();
        output.close();
        CHECK(output.good());
    }
    auto destination = before;
    std::string error = "stale error";
    CHECK(hammond::load_source_leakage_profile_file(path, destination, error));
    CHECK(error.empty());
    same_profile(destination, accepted(fixture()));
    {
        std::ofstream output(path, std::ios::binary | std::ios::trunc);
        output << "B3LEAKAGE1\n";
        output.close();
        CHECK(output.good());
    }
    destination = before;
    CHECK(!hammond::load_source_leakage_profile_file(path, destination, error));
    CHECK(!error.empty());
    same_profile(destination, before);
    error = "stale error";
    CHECK(!hammond::load_source_leakage_profile_file(directory.path() / "absent.b3l",
                                                   destination, error));
    CHECK(!error.empty() && error != "stale error");
    same_profile(destination, before);
}

} // namespace

int main() {
    const auto original = split(fixture());
    CHECK(original.size() == 32);
    const auto before = sentinel();
    test_valid_forms(original);
    test_malformed(original, before);
    test_numeric_boundaries(before);
    test_transport(before);
    test_file(before);
    std::cout << "Source-leakage loader accepted strict fixtures and rejected "
              << rejected_inputs << " malformed/transport inputs transactionally.\n";
    return EXIT_SUCCESS;
}
