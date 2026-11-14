#pragma once

#include <array>
#include <cstddef>

namespace hammond::native_test::preset_oracle {

// Independent literal oracle from the frozen state/parameter contract. Native
// tests do not call ParameterBridge to decide expected selector values. The
// separate parameter suite also verifies these values with rational arithmetic.
inline constexpr std::array<double, 12> canonical{
    0x0.0p+0, 0x1.745d1745d1746p-4, 0x1.745d1745d1746p-3,
    0x1.1745d1745d174p-2, 0x1.745d1745d1746p-2, 0x1.d1745d1745d17p-2,
    0x1.1745d1745d174p-1, 0x1.45d1745d1745dp-1, 0x1.745d1745d1746p-1,
    0x1.a2e8ba2e8ba2fp-1, 0x1.d1745d1745d17p-1, 0x1.0p+0};

inline constexpr std::array<double, 11> thresholds{
    0x1.745d1745d1746p-5, 0x1.1745d1745d174p-3, 0x1.d1745d1745d17p-3,
    0x1.45d1745d1745dp-2, 0x1.a2e8ba2e8ba2fp-2, 0x1.0p-1,
    0x1.2e8ba2e8ba2e9p-1, 0x1.5d1745d1745d1p-1, 0x1.8ba2e8ba2e8bap-1,
    0x1.ba2e8ba2e8ba3p-1, 0x1.e8ba2e8ba2e8cp-1};

inline std::size_t plain(double normalized) {
    std::size_t result = 0;
    for (const auto threshold : thresholds) result += normalized >= threshold ? 1U : 0U;
    return result;
}

} // namespace hammond::native_test::preset_oracle
