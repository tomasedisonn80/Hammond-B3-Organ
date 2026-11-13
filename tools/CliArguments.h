#pragma once

// Offline CLI boundary only: this header is not part of the realtime core.
#include <cstddef>
#include <filesystem>
#include <string>
#include <string_view>

#ifdef _WIN32
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <Windows.h>

#include <exception>
#include <iostream>
#include <stdexcept>
#include <utility>
#include <vector>
#endif

namespace hammond::cli {

[[nodiscard]] inline std::filesystem::path argument_path(std::string_view value) {
#ifdef _WIN32
    // wmain supplies strict UTF-8. char8_t selects the UTF-8 filesystem
    // constructor without an ANSI-code-page or best-fit conversion.
    return std::filesystem::path(std::u8string(value.begin(), value.end()));
#else
    // Preserve native POSIX argument bytes, including non-UTF-8 filenames.
    return std::filesystem::path(value);
#endif
}

[[nodiscard]] inline std::string path_text(const std::filesystem::path& value) {
#ifdef _WIN32
    const auto utf8 = value.u8string();
    return std::string(reinterpret_cast<const char*>(utf8.data()), utf8.size());
#else
    return value.string();
#endif
}

#ifdef _WIN32
struct WindowsArgumentLimits {
    // Zero leaves the existing tool parser responsible for its own bounds.
    int maximum_count = 0;
    std::size_t maximum_bytes = 0;
    const char* count_error = "Too many command-line arguments.";
    const char* value_error = "Command-line argument is invalid Unicode.";
};

[[nodiscard]] inline int run_windows(int argc, wchar_t* argv[],
                                     int (*entry)(int, char**),
                                     std::string_view program,
                                     WindowsArgumentLimits limits = {}) {
    try {
        if (argc < 1 || (limits.maximum_count != 0 && argc > limits.maximum_count)) {
            throw std::runtime_error(limits.count_error);
        }
        std::vector<std::string> arguments;
        arguments.reserve(static_cast<std::size_t>(argc));
        for (int index = 0; index < argc; ++index) {
            // Both passes reject malformed UTF-16. No normalization or best-fit
            // substitution may turn an unsupported token into an accepted one.
            const int bytes = WideCharToMultiByte(
                CP_UTF8, WC_ERR_INVALID_CHARS, argv[index], -1, nullptr, 0, nullptr, nullptr);
            if (bytes <= 0 ||
                (index != 0 && limits.maximum_bytes != 0 &&
                 static_cast<std::size_t>(bytes - 1) > limits.maximum_bytes)) {
                throw std::runtime_error(limits.value_error);
            }
            std::string value(static_cast<std::size_t>(bytes), '\0');
            if (WideCharToMultiByte(CP_UTF8, WC_ERR_INVALID_CHARS, argv[index], -1,
                                    value.data(), bytes, nullptr, nullptr) != bytes) {
                throw std::runtime_error("Cannot convert command-line argument to UTF-8.");
            }
            value.pop_back(); // The measured size includes the terminating NUL.
            arguments.push_back(std::move(value));
        }
        std::vector<char*> pointers;
        pointers.reserve(static_cast<std::size_t>(argc) + 1);
        for (auto& value : arguments) pointers.push_back(value.data());
        pointers.push_back(nullptr);
        // Storage outlives the parser and every string_view retained by it.
        return entry(argc, pointers.data());
    } catch (const std::exception& error) {
        std::cerr << program << ": " << error.what() << '\n';
        return 1;
    } catch (...) {
        std::cerr << program << ": invalid command-line encoding.\n";
        return 1;
    }
}
#endif

} // namespace hammond::cli
