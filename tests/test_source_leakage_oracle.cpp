#include "TestSupport.h"
#include "hammond/SourceLeakage.h"

#include <algorithm>
#include <array>
#include <bit>
#include <cmath>
#include <complex>
#include <cstdint>
#include <iomanip>
#include <limits>
#include <numbers>
#include <span>
#include <vector>

namespace {
using hammond::SourceLeakage;
using hammond::SourceLeakageEdge;
using hammond::SourceLeakageFrame;
using hammond::Status;
constexpr std::size_t kSources = 91;
constexpr long double kTolerance = 32.0L * std::numeric_limits<double>::epsilon();
constexpr long double kSpectrumTolerance = 1.0e-12L;

struct Counts {
    std::uint64_t graphs{}, frames{}, samples{}, bit_checks{}, rejections{}, spectrum_bins{};
    long double max_error{}, max_spectral_error{}, max_unprovided_bin{};
} counts;

// A local, explicitly specified stream avoids implementation-defined standard
// distribution algorithms. No random seed is taken from time or the environment.
struct Random {
    std::uint64_t state;
    std::uint64_t next() {
        state += UINT64_C(0x9e3779b97f4a7c15);
        auto value = state;
        value = (value ^ (value >> 30)) * UINT64_C(0xbf58476d1ce4e5b9);
        value = (value ^ (value >> 27)) * UINT64_C(0x94d049bb133111eb);
        return value ^ (value >> 31);
    }
    double unit() { return static_cast<double>(next() >> 11) * 0x1p-53; }
};

// Dense full-matrix reference, including the identity diagonal. Its reverse
// source traversal, long-double products and compensated summation do not copy
// the sparse production rows, sorting, sequential accumulation or output path.
struct Dense {
    std::array<std::array<long double, kSources>, kSources> matrix{};
    std::array<bool, kSources> coupled{};

    explicit Dense(std::span<const SourceLeakageEdge> edges) {
        for (std::size_t i = 0; i < kSources; ++i) matrix[i][i] = 1.0L;
        for (const auto& edge : edges) {
            const auto destination = static_cast<std::size_t>(edge.destination - 1);
            const auto source = static_cast<std::size_t>(edge.source - 1);
            CHECK(source < kSources && destination < kSources && source != destination);
            CHECK(matrix[destination][source] == 0.0L);
            matrix[destination][source] = static_cast<long double>(edge.gain);
            coupled[destination] = true;
        }
    }
};

void accumulate(long double term, long double& sum, long double& correction) {
    const long double next = sum + term;
    correction += std::abs(sum) >= std::abs(term) ?
        (sum - next) + term : (term - next) + sum;
    sum = next;
}

void same_bits(const SourceLeakageFrame& actual, const SourceLeakageFrame& expected) {
    for (std::size_t i = 0; i < kSources; ++i) {
        CHECK(std::bit_cast<std::uint64_t>(actual[i]) ==
              std::bit_cast<std::uint64_t>(expected[i]));
        ++counts.bit_checks;
    }
}

void compare(const Dense& reference, const SourceLeakageFrame& input,
             const SourceLeakageFrame& actual) {
    for (std::size_t destination = 0; destination < kSources; ++destination) {
        long double sum = 0.0L, correction = 0.0L;
        for (std::size_t source = kSources; source-- != 0;) {
            accumulate(reference.matrix[destination][source] *
                       static_cast<long double>(input[source]), sum, correction);
        }
        const long double expected = sum + correction;
        const long double error = std::abs(static_cast<long double>(actual[destination]) - expected);
        const long double limit = kTolerance * std::max(1.0L, std::abs(expected));
        CHECK(std::isfinite(actual[destination]));
        CHECK_NEAR(actual[destination], expected, limit);
        counts.max_error = std::max(counts.max_error, error);
        ++counts.samples;
        if (!reference.coupled[destination]) {
            CHECK(std::bit_cast<std::uint64_t>(actual[destination]) ==
                  std::bit_cast<std::uint64_t>(input[destination]));
            ++counts.bit_checks;
        }
    }
}

std::vector<SourceLeakageEdge> graph(unsigned index, Random& random) {
    std::vector<SourceLeakageEdge> edges;
    edges.reserve(728);
    for (std::size_t destination = 0; destination < kSources; ++destination) {
        const std::size_t count = index < 2 ? 8 : index == 2 ? 2 : index == 3 ? 0 :
            static_cast<std::size_t>(random.next() % 9);
        std::array<bool, kSources> chosen{};
        chosen[destination] = true;
        for (std::size_t term = 0; term < count; ++term) {
            std::size_t source = (destination + term + 1) % kSources;
            if (index >= 4) {
                source = static_cast<std::size_t>(random.next() % kSources);
                while (chosen[source]) source = (source + 1) % kSources;
            }
            chosen[source] = true;
            double gain = index == 2 ? 0.25 : index < 2 ? 0.0625 :
                0.0625 * (0.25 + 0.75 * random.unit());
            if (index == 0 || (index <= 2 ? (term % 2) == 0 : (random.next() & 1) != 0)) {
                gain = -gain;
            }
            edges.push_back({static_cast<hammond::ToneId>(source + 1),
                             static_cast<hammond::ToneId>(destination + 1), gain});
        }
    }
    return edges;
}

SourceLeakageFrame frame(unsigned index, Random& random) {
    SourceLeakageFrame input{};
    for (std::size_t i = 0; i < kSources; ++i) {
        const double sign = i % 2 == 0 ? 1.0 : -1.0;
        switch (index) {
        case 0: input[i] = 0.0; break;
        case 1: input[i] = -0.0; break;
        case 2: input[i] = 1.0; break;
        case 3: input[i] = -1.0; break;
        case 4: input[i] = sign; break;
        case 5: input[i] = std::nextafter(sign, 0.0); break;
        case 6: input[i] = sign * (i % 3 == 0 ? std::numeric_limits<double>::min() :
                                  std::numeric_limits<double>::denorm_min()); break;
        case 7: input[i] = i == 0 ? 0.5 : 1.0; break;
        default: input[i] = 2.0 * random.unit() - 1.0; break;
        }
    }
    return input;
}

void exhaustive_bad_input(const SourceLeakage& leakage) {
    const std::array bad{
        std::nextafter(1.0, std::numeric_limits<double>::infinity()),
        std::nextafter(-1.0, -std::numeric_limits<double>::infinity()),
        std::numeric_limits<double>::quiet_NaN(),
        std::numeric_limits<double>::infinity(),
        -std::numeric_limits<double>::infinity()};
    SourceLeakageFrame sentinel{};
    for (std::size_t i = 0; i < kSources; ++i) sentinel[i] = static_cast<double>(i) + 17.0;
    sentinel[45] = -0.0;
    for (std::size_t position = 0; position < kSources; ++position) {
        for (const double value : bad) {
            SourceLeakageFrame input{};
            input[position] = value;
            auto output = sentinel;
            CHECK(leakage.process_frame(input, output) == Status::InvalidBuffer);
            same_bits(output, sentinel);
            auto alias = input;
            CHECK(leakage.process_frame(alias, alias) == Status::InvalidBuffer);
            same_bits(alias, input);
            ++counts.rejections;
        }
    }
}

void dense_cases() {
    Random random{UINT64_C(0x61a9b3c700000019)};
    for (unsigned index = 0; index < 36; ++index) {
        auto authoring = graph(index, random);
        const Dense reference(authoring);
        SourceLeakage original;
        CHECK(original.prepare(authoring) == Status::Ok);
        CHECK(original.edge_count() == authoring.size());
        if (index < 2) CHECK(authoring.size() == 728);
        if (index <= 2) CHECK(original.max_row_absolute_gain_sum() == 0.5);

        auto shuffled = authoring;
        for (std::size_t i = shuffled.size(); i > 1; --i) {
            std::swap(shuffled[i - 1], shuffled[static_cast<std::size_t>(random.next() % i)]);
        }
        SourceLeakage permuted;
        CHECK(permuted.prepare(shuffled) == Status::Ok);
        const SourceLeakage copied = original;
        // The dense oracle already owns its complete matrix. Destroy the useful
        // author values and replace the original object before testing its copy.
        for (auto& edge : authoring) edge.gain = std::numeric_limits<double>::quiet_NaN();
        for (auto& edge : shuffled) edge.gain = 0.0;
        CHECK(original.prepare({}) == Status::Ok);

        const auto exercise = [&](const SourceLeakageFrame& input) {
            SourceLeakageFrame output{}, other{};
            CHECK(copied.process_frame(input, output) == Status::Ok);
            compare(reference, input, output);
            CHECK(permuted.process_frame(input, other) == Status::Ok);
            same_bits(other, output);
            auto alias = input;
            CHECK(copied.process_frame(alias, alias) == Status::Ok);
            same_bits(alias, output);
            ++counts.frames;
            return output;
        };
        for (unsigned sample = 0; sample < 20; ++sample) {
            const auto output = exercise(frame(sample, random));
            // Eight original donors at one cancel destination one's own 0.5.
            if (index == 0 && sample == 7) CHECK(output[0] == 0.0);
        }
        if (index <= 2) {
            // Every dense matrix column is exposed by one independent impulse.
            for (std::size_t source = 0; source < kSources; ++source) {
                SourceLeakageFrame impulse{};
                impulse[source] = 1.0;
                (void)exercise(impulse);
            }
        }
        if (index == 0 || index == 3) exhaustive_bad_input(copied);
        ++counts.graphs;
    }
}

void coherent_spectra() {
    constexpr std::size_t length = 1024;
    constexpr std::array<unsigned, 3> bins{7, 31, 97};
    constexpr std::array<std::size_t, 3> sources{0, 24, 90}; // IDs 1, 25, 91.
    constexpr std::array<long double, 3> amplitudes{0.5L, 0.375L, 0.25L};
    constexpr std::array<long double, 3> phases{0.0L, 0.37L, -0.71L};
    constexpr std::array<std::size_t, 5> recipients{0, 24, 49, 89, 90};
    // Frozen before execution: signed gains plus a 50 <-> 90 cycle whose input
    // donors are zero. ID90 must stay silent: cascading ID50's new output fails.
    constexpr std::array edges{
        SourceLeakageEdge{25, 1, -0.125}, SourceLeakageEdge{1, 25, 0.0625},
        SourceLeakageEdge{91, 25, -0.03125}, SourceLeakageEdge{1, 50, 0.25},
        SourceLeakageEdge{25, 50, -0.125}, SourceLeakageEdge{91, 50, 0.0625},
        SourceLeakageEdge{50, 90, 0.25}, SourceLeakageEdge{90, 50, 0.03125},
        SourceLeakageEdge{25, 91, -0.25}};
    // Analytical complex amplitudes, independently declared by recipient/bin.
    // This table includes each recipient's identity term and no C*C term.
    constexpr std::array<std::array<long double, 3>, 5> signed_weights{{
        {1.0L, -0.125L, 0.0L}, {0.0625L, 1.0L, -0.03125L},
        {0.25L, -0.125L, 0.0625L}, {0.0L, 0.0L, 0.0L},
        {0.0L, -0.25L, 1.0L}}};
    constexpr long double tau = 2.0L * std::numbers::pi_v<long double>;
    SourceLeakage leakage;
    CHECK(leakage.prepare(edges) == Status::Ok);
    for (const unsigned rate : {44100U, 48000U, 96000U}) {
        // The core is rate independent. Explicit physical time/Hz construction
        // exercises the declared three rates without resampling or a window.
        std::vector<std::array<double, recipients.size()>> signal(length);
        for (std::size_t n = 0; n < length; ++n) {
            SourceLeakageFrame input{}, output{};
            const long double seconds = static_cast<long double>(n) / rate;
            for (std::size_t tone = 0; tone < bins.size(); ++tone) {
                const long double hertz = static_cast<long double>(bins[tone]) * rate / length;
                input[sources[tone]] = static_cast<double>(amplitudes[tone] *
                    std::cos(tau * hertz * seconds + phases[tone]));
                CHECK(std::abs(input[sources[tone]]) <= 0.5);
            }
            CHECK(leakage.process_frame(input, output) == Status::Ok);
            for (std::size_t r = 0; r < recipients.size(); ++r) {
                signal[n][r] = output[recipients[r]];
            }
        }
        for (std::size_t bin = 0; bin <= length / 2; ++bin) {
            std::array<long double, recipients.size()> real{}, imag{}, real_error{}, imag_error{};
            for (std::size_t n = 0; n < length; ++n) {
                const long double angle = tau * static_cast<long double>(bin) * n / length;
                const long double cosine = std::cos(angle), sine = -std::sin(angle);
                for (std::size_t r = 0; r < recipients.size(); ++r) {
                    accumulate(static_cast<long double>(signal[n][r]) * cosine, real[r], real_error[r]);
                    accumulate(static_cast<long double>(signal[n][r]) * sine, imag[r], imag_error[r]);
                }
            }
            const long double scale = (bin == 0 || bin == length / 2 ? 1.0L : 2.0L) / length;
            for (std::size_t r = 0; r < recipients.size(); ++r) {
                const std::complex<long double> actual{
                    scale * (real[r] + real_error[r]), scale * (imag[r] + imag_error[r])};
                std::complex<long double> expected{};
                for (std::size_t tone = 0; tone < bins.size(); ++tone) {
                    if (bin == bins[tone]) {
                        expected = signed_weights[r][tone] * amplitudes[tone] *
                            std::complex<long double>{std::cos(phases[tone]), std::sin(phases[tone])};
                    }
                }
                const long double error = std::abs(actual - expected);
                CHECK(std::isfinite(error) && error <= kSpectrumTolerance);
                counts.max_spectral_error = std::max(counts.max_spectral_error, error);
                if (expected == std::complex<long double>{}) {
                    counts.max_unprovided_bin = std::max(counts.max_unprovided_bin, std::abs(actual));
                }
                ++counts.spectrum_bins;
            }
        }
    }
}
} // namespace

int main() {
    dense_cases();
    coherent_spectra();
    std::cout << std::setprecision(std::numeric_limits<long double>::max_digits10)
              << "{\"test\":\"source-leakage-independent-oracle-v1\",\"graphs\":" << counts.graphs
              << ",\"frames\":" << counts.frames << ",\"samples\":" << counts.samples
              << ",\"bit_checks\":" << counts.bit_checks << ",\"rejections\":" << counts.rejections
              << ",\"spectrum_bins\":" << counts.spectrum_bins
              << ",\"rates\":[44100,48000,96000],\"max_dense_error\":" << counts.max_error
              << ",\"max_spectral_error\":" << counts.max_spectral_error
              << ",\"max_unprovided_bin\":" << counts.max_unprovided_bin << "}\n";
    return 0;
}
