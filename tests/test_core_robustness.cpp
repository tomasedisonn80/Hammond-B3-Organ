#include "TestSupport.h"

#include <array>
#include <fstream>
#include <iterator>
#include <locale>
#include <sstream>
#include <stdexcept>
#include <streambuf>

namespace {

// A streambuf may throw its own exception; istream rethrows that original
// exception when badbit is included in the caller's exception mask.
class OriginalExceptionBuffer final : public std::streambuf {
public:
    OriginalExceptionBuffer(std::string_view bytes, std::size_t failure_at)
        : bytes_(bytes), failure_at_(failure_at) {}

private:
    int_type underflow() override {
        if (position_ == failure_at_) {
            throw std::runtime_error("injected original stream-buffer failure");
        }
        if (position_ == bytes_.size()) return traits_type::eof();
        byte_ = bytes_[position_++];
        setg(&byte_, &byte_, &byte_ + 1);
        return traits_type::to_int_type(byte_);
    }

    std::string_view bytes_;
    std::size_t failure_at_;
    std::size_t position_{0};
    char byte_{0};
};

void same_profile(const hammond::RuntimeProfile& actual,
                  const hammond::RuntimeProfile& expected) {
    CHECK(actual.profile_id == expected.profile_id);
    CHECK(actual.authoring_sha256 == expected.authoring_sha256);
    CHECK(actual.output_gain == expected.output_gain);
    CHECK(actual.drawbar_gains == expected.drawbar_gains);
    CHECK(actual.manual_map == expected.manual_map);
    for (std::size_t source = 0; source < actual.sources.size(); ++source) {
        CHECK(actual.sources[source].frequency_hz == expected.sources[source].frequency_hz);
        CHECK(actual.sources[source].peak_amplitude == expected.sources[source].peak_amplitude);
        CHECK(actual.sources[source].base_phase_turns == expected.sources[source].base_phase_turns);
    }
}

void test_original_stream_exceptions(const hammond::RuntimeProfile& nominal,
                                     const std::string& bytes) {
    // Distinct valid destination: even a fully read candidate must not commit
    // if the final read reports a transport failure instead of clean EOF.
    auto retained = nominal;
    retained.output_gain = 0.875;
    retained.drawbar_gains[4] = 0.375;
    retained.sources.back() = {123.0, 0.25, 0.75};
    retained.manual_map.front().front() = 91;
    retained.authoring_sha256.fill('a');
    retained.authoring_sha256.back() = '\0';
    CHECK(hammond::validate_runtime_profile(retained, 48000.0) == hammond::Status::Ok);

    const std::array<std::ios::iostate, 3> masks{
        std::ios::goodbit, std::ios::badbit,
        std::ios::badbit | std::ios::failbit | std::ios::eofbit};
    const std::array<std::size_t, 3> failures{0, bytes.size() / 2, bytes.size()};
    for (const auto mask : masks) {
        for (const auto failure_at : failures) {
            OriginalExceptionBuffer buffer(bytes, failure_at);
            std::istream input(&buffer);
            input.imbue(std::locale::classic());
            input.exceptions(mask);
            const auto original_locale = input.getloc();
            auto destination = retained;
            std::string error = "stale error";
            CHECK(!hammond::load_runtime_profile(input, destination, error));
            CHECK(input.bad());
            CHECK(input.exceptions() == mask);
            CHECK(input.getloc() == original_locale);
            CHECK(!error.empty() && error != "stale error");
            same_profile(destination, retained);

            // No hidden parser state remains after rejection. EOF exceptions
            // still denote a successfully read profile on a healthy stream.
            std::istringstream healthy(bytes);
            healthy.exceptions(mask);
            CHECK(hammond::load_runtime_profile(healthy, destination, error));
            CHECK(healthy.exceptions() == mask);
            CHECK(error.empty());
            same_profile(destination, nominal);
        }
    }
}

} // namespace

int main() {
    try {
        const auto nominal = load_test_profile();
        std::ifstream input(HAMMOND_TEST_PROFILE, std::ios::binary);
        CHECK(input.is_open());
        const std::string bytes{std::istreambuf_iterator<char>(input),
                                std::istreambuf_iterator<char>()};
        CHECK(!input.bad() && !bytes.empty());
        test_original_stream_exceptions(nominal, bytes);
        std::cout << "Core robustness: 9 original-exception rejection/recovery cases passed.\n";
    } catch (const std::exception& error) {
        std::cerr << "Core robustness failure: " << error.what() << '\n';
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
