#pragma once

#include "hammond/Profile.h"

#include <cmath>
#include <cstdlib>
#include <filesystem>
#include <iomanip>
#include <iostream>
#include <limits>
#include <string>
#include <string_view>

#ifndef HAMMOND_TEST_PROFILE
#error "C++ tests require HAMMOND_TEST_PROFILE, supplied by the CMake test targets."
#endif

#ifndef HAMMOND_SOURCE_DIR
#error "C++ tests require HAMMOND_SOURCE_DIR, supplied by the CMake test targets."
#endif

namespace hammond_test {

[[noreturn]] inline void fail(const char* expression, const char* file, int line,
                             std::string_view detail = {}) {
    std::cerr << file << ':' << line << ": CHECK failed: " << expression;
    if (!detail.empty()) {
        std::cerr << " (" << detail << ')';
    }
    std::cerr << '\n';
    std::exit(EXIT_FAILURE);
}

inline void check(bool condition, const char* expression, const char* file, int line) {
    if (!condition) {
        fail(expression, file, line);
    }
}

template <typename Actual, typename Expected, typename Tolerance>
inline void check_near(Actual actual, Expected expected, Tolerance tolerance,
                       const char* actual_text, const char* expected_text,
                       const char* tolerance_text, const char* file, int line) {
    const auto a = static_cast<long double>(actual);
    const auto e = static_cast<long double>(expected);
    const auto t = static_cast<long double>(tolerance);
    if (!std::isfinite(a) || !std::isfinite(e) || !std::isfinite(t) || t < 0.0L ||
        std::fabs(a - e) > t) {
        std::cerr << file << ':' << line << ": CHECK_NEAR failed: " << actual_text
                  << " vs " << expected_text << ", tolerance " << tolerance_text
                  << std::setprecision(std::numeric_limits<long double>::max_digits10)
                  << " (actual=" << a << ", expected=" << e << ", tolerance=" << t << ")\n";
        std::exit(EXIT_FAILURE);
    }
}

[[nodiscard]] inline std::filesystem::path source_path(std::string_view relative) {
    return std::filesystem::path(HAMMOND_SOURCE_DIR) / std::filesystem::path(relative);
}

} // namespace hammond_test

// These checks remain active in Release builds and evaluate each argument once.
#define CHECK(expression) \
    ::hammond_test::check(static_cast<bool>(expression), #expression, __FILE__, __LINE__)
#define CHECK_NEAR(actual, expected, tolerance) \
    ::hammond_test::check_near((actual), (expected), (tolerance), #actual, #expected, \
                             #tolerance, __FILE__, __LINE__)

[[nodiscard]] inline hammond::RuntimeProfile load_test_profile() {
    hammond::RuntimeProfile profile;
    std::string error;
    if (!hammond::load_runtime_profile_file(HAMMOND_TEST_PROFILE, profile, error)) {
        hammond_test::fail("load_runtime_profile_file(HAMMOND_TEST_PROFILE)",
                           __FILE__, __LINE__, error);
    }
    return profile;
}
