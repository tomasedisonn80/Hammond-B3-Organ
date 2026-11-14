#include "hammond/RotaryHistory.h"

#include <algorithm>
#include <array>
#include <bit>
#include <cfenv>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <memory>
#include <numbers>
#include <sstream>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

// This independent acceptance executable uses the declared test friend only
// for bitwise observation of every physical slot and to move a valid clock to
// the end of its one-day epoch. It does not call production interpolation or
// motion helpers to calculate expected values. Large histories/snapshots live
// on the heap; no full-history object is a function-local value.
namespace hammond::rotary::detail {
struct RotaryRendererTestAccess {
    static bool equal_bits(double a, double b) noexcept {
        return std::bit_cast<std::uint64_t>(a) == std::bit_cast<std::uint64_t>(b);
    }
    static bool equal_state(const MotionState& a, const MotionState& b) noexcept {
        return equal_bits(a.phase_rad, b.phase_rad) && a.turns == b.turns
            && equal_bits(a.speed_rad_s, b.speed_rad_s);
    }
    static bool equal_segment(const MotionSegment& a, const MotionSegment& b) noexcept {
        return a.anchor_frame == b.anchor_frame && equal_state(a.initial, b.initial)
            && equal_bits(a.target_rad_s, b.target_rad_s)
            && equal_bits(a.tau_s, b.tau_s) && a.direction == b.direction;
    }
    static bool equal_history(const WaveformHistory& a, const WaveformHistory& b) noexcept {
        if (a.prepared_ != b.prepared_ || !equal_bits(a.sample_rate_, b.sample_rate_)
            || a.capacity_frames_ != b.capacity_frames_ || a.next_frame_ != b.next_frame_
            || a.max_frame_ != b.max_frame_) return false;
        for (std::size_t i = 0; i < a.samples_.size(); ++i) {
            if (!equal_bits(a.samples_[i], b.samples_[i])) return false;
        }
        return true;
    }
    static bool equal_history(const MotionFrameHistory& a, const MotionFrameHistory& b) noexcept {
        if (a.prepared_ != b.prepared_ || !equal_bits(a.sample_rate_, b.sample_rate_)
            || a.capacity_frames_ != b.capacity_frames_ || a.next_frame_ != b.next_frame_
            || a.max_frame_ != b.max_frame_ || !equal_state(a.epoch_initial_, b.epoch_initial_)
            || !equal_bits(a.profile_.slow_rad_s, b.profile_.slow_rad_s)
            || !equal_bits(a.profile_.fast_rad_s, b.profile_.fast_rad_s)
            || !equal_bits(a.profile_.tau_up_s, b.profile_.tau_up_s)
            || !equal_bits(a.profile_.tau_down_s, b.profile_.tau_down_s)
            || a.profile_.direction != b.profile_.direction) return false;
        for (std::size_t i = 0; i < a.segments_.size(); ++i) {
            if (!equal_segment(a.segments_[i], b.segments_[i])) return false;
        }
        return true;
    }
    static void relocate_clock(WaveformHistory& history, std::uint64_t frame) noexcept {
        history.next_frame_ = frame;
    }
    static void relocate_clock(MotionFrameHistory& history, std::uint64_t frame) noexcept {
        history.next_frame_ = frame;
    }
};
} // namespace hammond::rotary::detail

namespace {
using namespace hammond::rotary;
using Access = detail::RotaryRendererTestAccess;

constexpr std::array<double, 4> kRates{44100.0, 48000.0, 96000.0, 192000.0};
constexpr std::array<int, 4> kNodes{-1, 0, 1, 2};
constexpr long double kCubicBudget = 2.0e-12L;
constexpr long double kLowBandBudget = 0.005L;
constexpr std::uint64_t kTupleSeed = 0xa14c0b1c5eed1234ULL;
constexpr MotionState kStateSentinel{0.875, -91, 123.25};

struct Checks {
    std::string group;
    std::vector<std::string> failures;
    std::size_t count{0};
    std::size_t rejected_calls{0};

    bool check(bool condition, std::string_view detail) {
        ++count;
        if (!condition) failures.push_back(group + ": " + std::string(detail));
        return condition;
    }
    bool status(Status actual, Status expected, std::string_view detail) {
        if (actual == expected) return check(true, detail);
        return check(false, std::string(detail) + " expected=" + std::string(status_name(expected))
                           + " actual=" + std::string(status_name(actual)));
    }
};

struct ErrorStats {
    std::size_t count{0};
    long double maximum{0.0L};
    long double sum_squares{0.0L};
    std::size_t worst_a{0};
    std::size_t worst_b{0};
    bool finite{true};

    void observe(long double error, std::size_t a, std::size_t b) {
        ++count;
        if (!std::isfinite(error)) {
            finite = false;
            return;
        }
        sum_squares += error * error;
        if (error > maximum) {
            maximum = error;
            worst_a = a;
            worst_b = b;
        }
    }
    long double rms() const {
        return count == 0 ? 0.0L : std::sqrt(sum_squares / static_cast<long double>(count));
    }
};

struct Results {
    ErrorStats polynomial_product;
    ErrorStats polynomial_analytic;
    ErrorStats additional_product;
    ErrorStats static_product;
    ErrorStats static_full_band;
    ErrorStats static_low_band;
    ErrorStats waveform_product;
    ErrorStats motion_angle;
    ErrorStats motion_speed;
    std::size_t endpoint_cases{0};
    std::size_t aliased_cases{0};
    std::size_t waveform_reads{0};
    std::size_t waveform_interpolations{0};
    std::size_t waveform_pushes{0};
    std::size_t motion_appends{0};
    std::size_t accelerated_epoch_fixtures{0};
    std::size_t static_rows_written{0};
    std::size_t full_band_above_low_budget{0};
};

long double integer_power(long double x, unsigned degree) {
    long double result = 1.0L;
    for (unsigned i = 0; i < degree; ++i) result *= x;
    return result;
}

// Defining Lagrange product, deliberately not a copied specialized kernel or
// production coefficient table. Inputs are the independently authored values.
long double product_cubic(const std::array<double, 4>& values, long double fraction) {
    long double result = 0.0L;
    for (std::size_t j = 0; j < kNodes.size(); ++j) {
        long double weight = 1.0L;
        for (std::size_t m = 0; m < kNodes.size(); ++m) {
            if (m != j) {
                weight *= (fraction - static_cast<long double>(kNodes[m]))
                        / static_cast<long double>(kNodes[j] - kNodes[m]);
            }
        }
        result += static_cast<long double>(values[j]) * weight;
    }
    return result;
}

bool equal_tuple(const std::array<double, 4>& a, const std::array<double, 4>& b) {
    for (std::size_t i = 0; i < a.size(); ++i) {
        if (!Access::equal_bits(a[i], b[i])) return false;
    }
    return true;
}

double output_sentinel() {
    // A payload-bearing NaN detects preservation by representation, not ==.
    return std::bit_cast<double>(std::uint64_t{0x7ff8a14000000071ULL});
}

template <typename Call>
void reject_output(Checks& checks, Status expected, std::string_view name, Call call) {
    double output = output_sentinel();
    checks.status(call(output), expected, name);
    checks.check(Access::equal_bits(output, output_sentinel()), std::string(name) + " output preserved");
    ++checks.rejected_calls;
}

template <typename Call>
void reject_state(Checks& checks, Status expected, std::string_view name, Call call) {
    MotionState output = kStateSentinel;
    checks.status(call(output), expected, name);
    checks.check(Access::equal_state(output, kStateSentinel), std::string(name) + " state preserved");
    ++checks.rejected_calls;
}

template <typename History, typename Call>
void reject_history(Checks& checks, History& history, Status expected,
                    std::string_view name, Call call) {
    const auto before = std::make_unique<History>(history);
    checks.status(call(), expected, name);
    checks.check(Access::equal_history(history, *before), std::string(name) + " all slots and metadata preserved");
    ++checks.rejected_calls;
}

void cubic_acceptance(Checks& checks, Results& results) {
    checks.group = "cubic";
    for (unsigned degree = 0; degree <= 3; ++degree) {
        std::array<double, 4> values{};
        for (std::size_t node = 0; node < values.size(); ++node) {
            values[node] = static_cast<double>(integer_power(static_cast<long double>(kNodes[node]) / 2.0L,
                                                             degree));
        }
        for (unsigned fraction_index = 0; fraction_index <= 256; ++fraction_index) {
            const double fraction = static_cast<double>(fraction_index) / 256.0;
            double actual = output_sentinel();
            checks.status(interpolate_cubic_lagrange(values, fraction, actual), Status::Ok,
                          "polynomial primitive admission");
            results.polynomial_product.observe(std::abs(static_cast<long double>(actual)
                - product_cubic(values, fraction)), degree, fraction_index);
            results.polynomial_analytic.observe(std::abs(static_cast<long double>(actual)
                - integer_power(static_cast<long double>(fraction) / 2.0L, degree)), degree, fraction_index);
        }
    }
    checks.check(results.polynomial_product.count == 1028, "all four degrees and 257 fractions visited");
    checks.check(results.polynomial_product.finite && results.polynomial_product.maximum <= kCubicBudget,
                 "polynomial product budget");
    checks.check(results.polynomial_analytic.finite && results.polynomial_analytic.maximum <= kCubicBudget,
                 "analytic polynomial budget");

    std::vector<std::array<double, 4>> tuples{
        {-1.0, 1.0, -1.0, 1.0}, {-1.0, 1.0, 1.0, -1.0}, {1.0, -1.0, -1.0, 1.0},
        {-0.875, 0.125, -0.375, 0.625}, {0.0, -0.0, 0.0, -0.0},
        {0.75, -0.25, -0.0, 1.0}, {-1.0, 0.0, 1.0, -0.5}};
    for (std::size_t node = 0; node < 4; ++node) {
        std::array<double, 4> impulse{};
        impulse[node] = 1.0;
        tuples.push_back(impulse);
        impulse[node] = -1.0;
        tuples.push_back(impulse);
    }
    std::uint64_t seed = kTupleSeed;
    for (unsigned tuple = 0; tuple < 64; ++tuple) {
        std::array<double, 4> values{};
        for (double& value : values) {
            seed = seed * 6364136223846793005ULL + 1442695040888963407ULL;
            const auto integer = static_cast<std::int32_t>((seed >> 32U) & 2047ULL) - 1024;
            value = static_cast<double>(integer) / 1024.0;
        }
        tuples.push_back(values);
    }
    for (std::size_t tuple = 0; tuple < tuples.size(); ++tuple) {
        for (unsigned fraction_index = 0; fraction_index <= 256; ++fraction_index) {
            const double fraction = static_cast<double>(fraction_index) / 256.0;
            double actual = output_sentinel();
            checks.status(interpolate_cubic_lagrange(tuples[tuple], fraction, actual), Status::Ok,
                          "additional support admission");
            results.additional_product.observe(std::abs(static_cast<long double>(actual)
                - product_cubic(tuples[tuple], fraction)), tuple, fraction_index);
            if (fraction_index == 0 || fraction_index == 256) {
                const std::size_t selected = fraction_index == 0 ? 1U : 2U;
                checks.check(Access::equal_bits(actual, tuples[tuple][selected]),
                             "integer endpoint is exact, including signed zero and every node impulse");
                ++results.endpoint_cases;
            }
            // Every support location can be the destination; all fractions of
            // the fifteen explicit adversarial tuples cover each alias.
            if (tuple < 15) {
                for (std::size_t alias = 0; alias < 4; ++alias) {
                    auto values = tuples[tuple];
                    auto expected = values;
                    expected[alias] = actual;
                    checks.status(interpolate_cubic_lagrange(values, fraction, values[alias]), Status::Ok,
                                  "aliased destination admission");
                    checks.check(equal_tuple(values, expected), "aliased result and remaining supports exact");
                    ++results.aliased_cases;
                }
            }
        }
    }
    checks.check(results.additional_product.count == 79 * 257, "complete bounded support grid");
    checks.check(results.additional_product.finite && results.additional_product.maximum <= kCubicBudget,
                 "additional product budget");
    for (const double sign : {-1.0, 1.0}) {
        const std::array<double, 4> values{-sign, sign, sign, -sign};
        double actual = 0.0;
        checks.status(interpolate_cubic_lagrange(values, 0.5, actual), Status::Ok, "overshoot admission");
        checks.check(actual == sign * 1.25, "cubic overshoot is not clipped or normalized");
    }
    const std::array<double, 4> signed_zero{1.0, -0.0, 0.0, -1.0};
    double actual = 1.0;
    checks.status(interpolate_cubic_lagrange(signed_zero, -0.0, actual), Status::Ok, "negative-zero fraction");
    checks.check(Access::equal_bits(actual, -0.0), "negative-zero endpoint sample preserved");

    const double nan = std::numeric_limits<double>::quiet_NaN();
    const double infinity = std::numeric_limits<double>::infinity();
    const std::array<double, 7> invalid_fractions{
        -std::numeric_limits<double>::denorm_min(), -0.5, std::nextafter(1.0, 2.0),
        2.0, nan, infinity, -infinity};
    for (const double fraction : invalid_fractions) {
        reject_output(checks, Status::InvalidSpec, "invalid primitive fraction", [&](double& output) {
            return interpolate_cubic_lagrange(signed_zero, fraction, output);
        });
        for (std::size_t alias = 0; alias < 4; ++alias) {
            auto values = signed_zero;
            checks.status(interpolate_cubic_lagrange(values, fraction, values[alias]), Status::InvalidSpec,
                          "invalid aliased fraction");
            checks.check(equal_tuple(values, signed_zero), "rejected alias preserves all sample bits");
            ++checks.rejected_calls;
        }
    }
    for (const double bad : {std::nextafter(-1.0, -2.0), std::nextafter(1.0, 2.0), nan, infinity, -infinity}) {
        for (std::size_t node = 0; node < 4; ++node) {
            auto values = signed_zero;
            values[node] = bad;
            for (const double fraction : {0.0, 0.5, 1.0}) {
                reject_output(checks, Status::InvalidBuffer, "invalid support, including zero-weight nodes",
                              [&](double& output) { return interpolate_cubic_lagrange(values, fraction, output); });
                for (std::size_t alias = 0; alias < 4; ++alias) {
                    auto aliased = values;
                    checks.status(interpolate_cubic_lagrange(aliased, fraction, aliased[alias]), Status::InvalidBuffer,
                                  "invalid aliased support");
                    checks.check(equal_tuple(aliased, values), "invalid support preserves aliased bytes");
                    ++checks.rejected_calls;
                }
            }
        }
    }
}

void static_delay_grid(Checks& checks, Results& results, std::ostream* csv) {
    checks.group = "static_grid";
    if (csv != nullptr) {
        *csv << "fraction_index,frequency_index,native_real,native_imag,ideal_real,ideal_imag,complex_error\n"
             << std::scientific << std::setprecision(std::numeric_limits<long double>::max_digits10);
    }
    for (unsigned fraction_index = 0; fraction_index <= 64; ++fraction_index) {
        const double fraction = static_cast<double>(fraction_index) / 64.0;
        for (unsigned frequency_index = 0; frequency_index < 512; ++frequency_index) {
            const long double omega = 2.0L * std::numbers::pi_v<long double>
                                    * static_cast<long double>(frequency_index) / 1024.0L;
            std::array<double, 4> real{};
            std::array<double, 4> imaginary{};
            for (std::size_t node = 0; node < 4; ++node) {
                const long double angle = omega * static_cast<long double>(kNodes[node]);
                real[node] = static_cast<double>(std::cos(angle));
                imaginary[node] = static_cast<double>(std::sin(angle));
            }
            double actual_real = output_sentinel();
            double actual_imag = output_sentinel();
            checks.status(interpolate_cubic_lagrange(real, fraction, actual_real), Status::Ok, "native real response");
            checks.status(interpolate_cubic_lagrange(imaginary, fraction, actual_imag), Status::Ok, "native imaginary response");
            const long double ideal_real = std::cos(omega * static_cast<long double>(fraction));
            const long double ideal_imag = std::sin(omega * static_cast<long double>(fraction));
            const long double error = std::hypot(static_cast<long double>(actual_real) - ideal_real,
                                                 static_cast<long double>(actual_imag) - ideal_imag);
            const long double product_error = std::hypot(static_cast<long double>(actual_real) - product_cubic(real, fraction),
                                                         static_cast<long double>(actual_imag) - product_cubic(imaginary, fraction));
            results.static_product.observe(product_error, fraction_index, frequency_index);
            results.static_full_band.observe(error, fraction_index, frequency_index);
            if (frequency_index <= 102) results.static_low_band.observe(error, fraction_index, frequency_index);
            if (error > kLowBandBudget) ++results.full_band_above_low_budget;
            if (csv != nullptr) {
                *csv << fraction_index << ',' << frequency_index << ',' << actual_real << ',' << actual_imag << ','
                     << ideal_real << ',' << ideal_imag << ',' << error << '\n';
                ++results.static_rows_written;
            }
        }
    }
    checks.check(results.static_full_band.count == 33280, "all 65 by 512 native grid coordinates");
    checks.check(results.static_low_band.count == 6695, "all 65 by 103 low-band coordinates");
    checks.check(results.static_product.finite && results.static_product.maximum <= kCubicBudget,
                 "complete native complex product-expression budget");
    checks.check(results.static_full_band.finite, "full-band complex results finite");
    checks.check(results.static_low_band.finite && results.static_low_band.maximum <= kLowBandBudget,
                 "frozen low-band complex budget");
    if (csv != nullptr) checks.check(csv->good() && results.static_rows_written == 33280, "complete CSV written");
}

double waveform_value(std::uint64_t frame) {
    if (frame % 23U == 0) return -0.0;
    const auto integer = static_cast<std::int32_t>((frame * 73U + 19U) % 257U) - 128;
    return static_cast<double>(integer) / 128.0;
}

std::int64_t epoch_limit(double rate) {
    return static_cast<std::int64_t>(kMaxEpochSeconds * static_cast<std::uint64_t>(rate));
}

Status expected_waveform_support(std::int64_t frame, double rate, std::uint64_t oldest,
                                std::uint64_t next, std::array<double, 4>& values) {
    const auto limit = epoch_limit(rate);
    if (frame < -limit + 1 || frame > limit - 2) return Status::TimelineOverflow;
    for (std::size_t node = 0; node < 4; ++node) {
        const auto index = frame + kNodes[node];
        if (index < 0) values[node] = 0.0;
        else {
            const auto positive = static_cast<std::uint64_t>(index);
            if (positive < oldest || positive >= next) return Status::InsufficientHistory;
            values[node] = waveform_value(positive);
        }
    }
    return Status::Ok;
}

void check_waveform_position(Checks& checks, Results& results, const WaveformHistory& history,
                             SamplePosition position) {
    std::array<double, 4> values{};
    const Status expected = expected_waveform_support(position.frame, history.sample_rate(),
                                                       history.oldest_frame(), history.next_frame(), values);
    double output = output_sentinel();
    const Status actual = history.interpolate(position, output);
    checks.status(actual, expected, "independent strict four-node coverage");
    ++results.waveform_interpolations;
    if (expected == Status::Ok && actual == Status::Ok) {
        const long double error = std::abs(static_cast<long double>(output) - product_cubic(values, position.fraction));
        results.waveform_product.observe(error, static_cast<std::size_t>(history.next_frame()), 0);
        if (position.fraction == 0.0) checks.check(Access::equal_bits(output, values[1]), "history endpoint bits");
    } else if (expected != Status::Ok) {
        checks.check(Access::equal_bits(output, output_sentinel()), "missing support preserves destination");
        ++checks.rejected_calls;
    }
}

void waveform_acceptance(Checks& checks, Results& results) {
    checks.group = "waveform_history";
    auto history = std::make_unique<WaveformHistory>();
    checks.check(!history->prepared() && history->next_frame() == 0 && history->capacity_frames() == 0,
                 "empty waveform metadata");
    reject_history(checks, *history, Status::NotPrepared, "unprepared waveform reset", [&] { return history->reset(); });
    reject_history(checks, *history, Status::NotPrepared, "unprepared waveform push", [&] { return history->push(0.25); });
    reject_output(checks, Status::NotPrepared, "unprepared waveform read", [&](double& out) { return history->sample_at(-1, out); });
    reject_output(checks, Status::NotPrepared, "unprepared waveform interpolation", [&](double& out) { return history->interpolate({-2, 0.0}, out); });

    const double nan = std::numeric_limits<double>::quiet_NaN();
    const double infinity = std::numeric_limits<double>::infinity();
    const std::array<double, 5> fractions{0.0, std::nextafter(0.0, 1.0), 0.25, 0.5, std::nextafter(1.0, 0.0)};
    for (const double rate : kRates) {
        const auto limit = epoch_limit(rate);
        for (const std::size_t capacity : std::array<std::size_t, 8>{1, 2, 3, 4, 5, 7, 16, kMaxHistoryFrames}) {
            if (!checks.status(history->prepare(rate, capacity), Status::Ok, "waveform capacity/rate preparation")) continue;
            checks.check(history->prepared() && history->sample_rate() == rate
                         && history->capacity_frames() == capacity && history->next_frame() == 0,
                         "prepared waveform metadata");
            for (const auto frame : std::array<std::int64_t, 4>{-limit, -limit + 1, -257, -1}) {
                double value = 0.875;
                checks.status(history->sample_at(frame, value), Status::Ok, "negative sample is declared zero");
                checks.check(value == 0.0, "negative-time waveform silence");
                ++results.waveform_reads;
            }
            // Empty and progressively available support, including a missing
            // k+2 with zero coefficient at mu=0, are tested at every step.
            const auto total = static_cast<std::uint64_t>(2 * capacity + 11);
            for (std::uint64_t frame = 0; frame < total; ++frame) {
                if (frame < 24 || frame + 1 == total) {
                    const auto oldest = static_cast<std::int64_t>(history->oldest_frame());
                    const auto next = static_cast<std::int64_t>(history->next_frame());
                    for (const auto query : std::array<std::int64_t, 10>{-3, -2, -1, 0,
                             oldest - 1, oldest, oldest + 1, next - 3, next - 2, next}) {
                        for (const double fraction : fractions) {
                            check_waveform_position(checks, results, *history, {query, fraction});
                        }
                    }
                }
                checks.status(history->push(waveform_value(frame)), Status::Ok, "bounded waveform push");
                ++results.waveform_pushes;
                checks.check(history->next_frame() == frame + 1, "exact append clock");
                const auto expected_oldest = frame + 1 > capacity ? frame + 1 - capacity : 0;
                checks.check(history->oldest_frame() == expected_oldest, "exact ring eviction boundary");
            }
            const auto before_queries = std::make_unique<WaveformHistory>(*history);
            for (std::uint64_t frame = history->oldest_frame(); frame < history->next_frame(); ++frame) {
                double value = output_sentinel();
                checks.status(history->sample_at(static_cast<std::int64_t>(frame), value), Status::Ok, "every retained sample after wraps");
                checks.check(Access::equal_bits(value, waveform_value(frame)), "retained absolute sample bits after wraps");
                ++results.waveform_reads;
            }
            reject_output(checks, Status::InsufficientHistory, "retired oldest sample", [&](double& out) {
                return history->sample_at(static_cast<std::int64_t>(history->oldest_frame()) - 1, out);
            });
            reject_output(checks, Status::InsufficientHistory, "future sample", [&](double& out) {
                return history->sample_at(static_cast<std::int64_t>(history->next_frame()), out);
            });
            for (const auto frame : std::array<std::int64_t, 4>{-limit - 1, limit + 1,
                     std::numeric_limits<std::int64_t>::min(), std::numeric_limits<std::int64_t>::max()}) {
                reject_output(checks, Status::TimelineOverflow, "signed sample epoch overflow", [&](double& out) {
                    return history->sample_at(frame, out);
                });
                reject_output(checks, Status::TimelineOverflow, "signed support arithmetic overflow", [&](double& out) {
                    return history->interpolate({frame, 0.0}, out);
                });
            }
            for (const double fraction : {-std::numeric_limits<double>::denorm_min(), 1.0,
                                          std::nextafter(1.0, 2.0), nan, infinity, -infinity}) {
                reject_output(checks, Status::InvalidSpec, "noncanonical history fraction", [&](double& out) {
                    return history->interpolate({-2, fraction}, out);
                });
            }
            check_waveform_position(checks, results, *history, {-limit, 0.0});
            check_waveform_position(checks, results, *history, {-limit + 1, std::nextafter(1.0, 0.0)});
            check_waveform_position(checks, results, *history, {limit - 2, 0.0});
            check_waveform_position(checks, results, *history, {limit - 1, 0.0});
            checks.check(Access::equal_history(*history, *before_queries), "all successful and rejected reads are immutable");
            for (const double sample : {std::nextafter(-1.0, -2.0), std::nextafter(1.0, 2.0), nan, infinity, -infinity}) {
                reject_history(checks, *history, Status::InvalidBuffer, "rejected waveform append", [&] {
                    return history->push(sample);
                });
            }
            for (const double bad_rate : {0.0, 48000.5, nan, infinity}) {
                reject_history(checks, *history, Status::InvalidSpec, "rejected waveform rate", [&] {
                    return history->prepare(bad_rate, capacity);
                });
            }
            for (const auto bad_capacity : std::array<std::size_t, 3>{0, kMaxHistoryFrames + 1,
                     std::numeric_limits<std::size_t>::max()}) {
                reject_history(checks, *history, Status::InvalidSpec, "rejected waveform capacity", [&] {
                    return history->prepare(rate, bad_capacity);
                });
            }
            auto copied = std::make_unique<WaveformHistory>(*history);
            checks.status(history->push(0.75), Status::Ok, "mutate original after copy");
            checks.check(Access::equal_history(*copied, *before_queries), "copy owns independent sample bytes");
            const auto original_after_push = std::make_unique<WaveformHistory>(*history);
            checks.status(copied->push(-0.75), Status::Ok, "mutate copied history");
            checks.check(Access::equal_history(*history, *original_after_push), "copy cannot mutate original");
            checks.status(history->reset(), Status::Ok, "waveform reset");
            checks.status(copied->prepare(rate, capacity), Status::Ok, "fresh prepared comparison");
            checks.check(Access::equal_history(*history, *copied), "reset clears every slot and restores prepared epoch");
        }

        // Clock-only acceleration: public pushes establish exactly the retained
        // samples at the matching modulo positions; only next_frame changes.
        // This tests end-of-epoch admission, not a literal one-day stress run.
        constexpr std::size_t capacity = 8;
        checks.status(history->prepare(rate, capacity), Status::Ok, "end-epoch waveform prepare");
        const auto before_end = static_cast<std::uint64_t>(limit - 2);
        const auto initial_count = static_cast<std::uint64_t>(capacity) + before_end % capacity;
        const auto translation = before_end - initial_count;
        for (std::uint64_t frame = 0; frame < initial_count; ++frame) {
            checks.status(history->push(waveform_value(translation + frame)), Status::Ok, "end-epoch slot seed");
        }
        Access::relocate_clock(*history, before_end);
        for (std::uint64_t frame = before_end; frame < static_cast<std::uint64_t>(limit); ++frame) {
            checks.status(history->push(waveform_value(frame)), Status::Ok, "last legal sample append");
        }
        checks.check(history->next_frame() == static_cast<std::uint64_t>(limit), "waveform final boundary reached");
        check_waveform_position(checks, results, *history, {limit - 3, 0.0});
        check_waveform_position(checks, results, *history, {limit - 3, std::nextafter(1.0, 0.0)});
        check_waveform_position(checks, results, *history, {limit - 2, 0.0});
        reject_history(checks, *history, Status::TimelineOverflow, "exhausted waveform append", [&] { return history->push(0.5); });
        reject_output(checks, Status::InsufficientHistory, "unwritten final-boundary sample", [&](double& out) {
            return history->sample_at(limit, out);
        });
        double negative = 0.75;
        checks.status(history->sample_at(-limit, negative), Status::Ok, "negative epoch survives positive retirement");
        checks.check(negative == 0.0, "negative end-epoch silence");
        ++results.accelerated_epoch_fixtures;
    }
    checks.check(results.waveform_product.finite && results.waveform_product.maximum <= kCubicBudget,
                 "waveform interpolation independent product budget");
}

struct AnalyticState { long double angle; long double speed; };
struct AnalyticSegment {
    std::uint64_t frame;
    AnalyticState initial;
    long double target;
    long double tau;
};

// Separate unwrapped analytical oracle. These fixtures are short and bounded;
// long double expm1 has ample margin under the frozen absolute-plus-relative
// motion budgets. No production state or segment feeds this calculation.
class AnalyticMotion {
public:
    AnalyticMotion(MotionProfile profile, double phase, double speed, SpeedCommand command, double rate)
        : profile_(profile), seed_{phase, speed}, rate_(rate), command_(command) {
        add(0, seed_, command);
    }
    AnalyticState at(SamplePosition position) const {
        if (position.frame < 0) {
            const long double seconds = (static_cast<long double>(position.frame) + position.fraction) / rate_;
            return {seed_.angle + static_cast<long double>(profile_.direction) * seed_.speed * seconds, seed_.speed};
        }
        const auto frame = static_cast<std::uint64_t>(position.frame);
        const AnalyticSegment* segment = &segments_.front();
        for (const auto& candidate : segments_) {
            if (candidate.frame > frame) break;
            segment = &candidate;
        }
        const long double elapsed = (static_cast<long double>(frame - segment->frame) + position.fraction) / rate_;
        const long double decay = std::exp(-elapsed / segment->tau);
        const long double speed = segment->target + (segment->initial.speed - segment->target) * decay;
        const long double distance = segment->target * elapsed
            + (segment->initial.speed - segment->target) * segment->tau * (-std::expm1(-elapsed / segment->tau));
        return {segment->initial.angle + static_cast<long double>(profile_.direction) * distance, speed};
    }
    void command(std::uint64_t frame, SpeedCommand command_value) {
        if (command_value == command_) return;
        const auto initial = at({static_cast<std::int64_t>(frame), 0.0});
        add(frame, initial, command_value);
        command_ = command_value;
    }
private:
    void add(std::uint64_t frame, AnalyticState initial, SpeedCommand command_value) {
        const long double target = command_value == SpeedCommand::Chorale ? profile_.slow_rad_s : profile_.fast_rad_s;
        segments_.push_back({frame, initial, target, target >= initial.speed ? profile_.tau_up_s : profile_.tau_down_s});
    }
    MotionProfile profile_;
    AnalyticState seed_;
    long double rate_;
    SpeedCommand command_;
    std::vector<AnalyticSegment> segments_;
};

void check_motion_value(Checks& checks, Results& results, const MotionFrameHistory& history,
                         const AnalyticMotion& reference, SamplePosition position) {
    MotionState output = kStateSentinel;
    if (!checks.status(history.state_at(position, output), Status::Ok, "covered motion query")) return;
    const auto expected = reference.at(position);
    // The public phase/turn representation uses the supplied binary64 2*pi;
    // compare the reconstructed unwrapped value, not epsilon-sensitive turns.
    const long double angle = output.phase_rad + static_cast<long double>(kTwoPi) * static_cast<long double>(output.turns);
    const long double angle_error = std::abs(angle - expected.angle);
    const long double speed_error = std::abs(static_cast<long double>(output.speed_rad_s) - expected.speed);
    results.motion_angle.observe(angle_error, static_cast<std::size_t>(history.next_frame()), 0);
    results.motion_speed.observe(speed_error, static_cast<std::size_t>(history.next_frame()), 0);
    checks.check(std::isfinite(angle_error) && angle_error <= 5.0e-12L + 4.0e-15L * std::abs(expected.angle),
                 "independent historical motion angle budget");
    checks.check(std::isfinite(speed_error) && speed_error <= 5.0e-12L + 4.0e-14L * std::abs(expected.speed),
                 "independent historical motion speed budget");
}

void motion_acceptance(Checks& checks, Results& results) {
    checks.group = "motion_history";
    auto history = std::make_unique<MotionFrameHistory>();
    RotaryMotion owner;
    reject_history(checks, *history, Status::NotPrepared, "unprepared motion append", [&] { return history->append(owner); });
    reject_history(checks, *history, Status::NotPrepared, "unprepared owner preparation", [&] { return history->prepare(owner, 4); });
    reject_state(checks, Status::NotPrepared, "unprepared motion query", [&](MotionState& out) { return history->state_at({0, 0.0}, out); });
    const double nan = std::numeric_limits<double>::quiet_NaN();
    const double infinity = std::numeric_limits<double>::infinity();
    for (const double rate : kRates) {
        for (const std::int8_t direction : std::array<std::int8_t, 2>{-1, 1}) {
            const MotionProfile profile{4.0, 40.0, 0.7, 1.1, direction};
            const auto limit = epoch_limit(rate);
            for (const std::size_t capacity : std::array<std::size_t, 4>{1, 2, 4, 9}) {
                checks.status(owner.prepare(profile, 0.001, 8.0, SpeedCommand::Chorale, rate), Status::Ok, "motion owner prepare");
                if (!checks.status(history->prepare(owner, capacity), Status::Ok, "motion history prepare")) continue;
                AnalyticMotion reference(profile, 0.001, 8.0, SpeedCommand::Chorale, rate);
                check_motion_value(checks, results, *history, reference, {0, 0.0});
                reject_state(checks, Status::InsufficientHistory, "empty positive fraction", [&](MotionState& out) {
                    return history->state_at({0, std::nextafter(0.0, 1.0)}, out);
                });
                for (std::uint64_t frame = 0; frame < 48; ++frame) {
                    checks.status(owner.advance_to(frame), Status::Ok, "advance matching owner");
                    const auto apply = [&](SpeedCommand command) {
                        checks.status(owner.apply_command(frame, command), Status::Ok, "ordered boundary command");
                        reference.command(frame, command);
                    };
                    if (frame == 3 || frame == 19) apply(SpeedCommand::Tremolo);
                    if (frame == 11) {
                        apply(SpeedCommand::Chorale);
                        apply(SpeedCommand::Tremolo);
                        apply(SpeedCommand::Chorale);
                    }
                    if (frame == 12 || frame == 34) apply(owner.command());
                    if (frame == 37) apply(SpeedCommand::Chorale);
                    checks.status(history->append(owner), Status::Ok, "retain original command segment");
                    ++results.motion_appends;
                    const auto next = frame + 1;
                    const auto oldest = next > capacity ? next - capacity : 0;
                    checks.check(history->next_frame() == next && history->oldest_frame() == oldest,
                                 "motion ring exact retained range");
                    for (const auto query_frame : std::array<std::uint64_t, 2>{oldest, frame}) {
                        for (const double fraction : {0.0, std::nextafter(0.0, 1.0), 0.5, std::nextafter(1.0, 0.0)}) {
                            check_motion_value(checks, results, *history, reference,
                                               {static_cast<std::int64_t>(query_frame), fraction});
                        }
                    }
                    check_motion_value(checks, results, *history, reference, {static_cast<std::int64_t>(next), 0.0});
                    reject_state(checks, Status::InsufficientHistory, "positive fraction beyond final boundary", [&](MotionState& out) {
                        return history->state_at({static_cast<std::int64_t>(next), std::nextafter(0.0, 1.0)}, out);
                    });
                    if (oldest != 0) {
                        reject_state(checks, Status::InsufficientHistory, "retired motion floor", [&](MotionState& out) {
                            return history->state_at({static_cast<std::int64_t>(oldest) - 1, std::nextafter(1.0, 0.0)}, out);
                        });
                    }
                    for (const auto position : std::array<SamplePosition, 4>{{{-1, 0.0}, {-1, std::nextafter(1.0, 0.0)},
                             {-257, 0.25}, {-limit, 0.0}}}) {
                        check_motion_value(checks, results, *history, reference, position);
                    }
                }
                const auto snapshot = std::make_unique<MotionFrameHistory>(*history);
                for (const double fraction : {-std::numeric_limits<double>::denorm_min(), 1.0, nan, infinity, -infinity}) {
                    reject_state(checks, Status::InvalidSpec, "noncanonical motion fraction", [&](MotionState& out) {
                        return history->state_at({-1, fraction}, out);
                    });
                }
                for (const auto frame : std::array<std::int64_t, 4>{-limit - 1, limit + 1,
                         std::numeric_limits<std::int64_t>::min(), std::numeric_limits<std::int64_t>::max()}) {
                    reject_state(checks, Status::TimelineOverflow, "signed motion epoch overflow", [&](MotionState& out) {
                        return history->state_at({frame, 0.0}, out);
                    });
                }
                reject_state(checks, Status::TimelineOverflow, "fraction after maximum epoch", [&](MotionState& out) {
                    return history->state_at({limit, std::nextafter(0.0, 1.0)}, out);
                });
                checks.check(Access::equal_history(*history, *snapshot), "all motion queries leave physical slots unchanged");
                reject_history(checks, *history, Status::InvalidEvent, "old owner append boundary", [&] { return history->append(owner); });
                reject_history(checks, *history, Status::InvalidEvent, "nonzero owner prepare boundary", [&] { return history->prepare(owner, capacity); });
                checks.status(owner.advance_to(48), Status::Ok, "owner exact final boundary");
                auto copy = std::make_unique<MotionFrameHistory>(*history);
                checks.status(history->append(owner), Status::Ok, "independent copied history append");
                checks.check(Access::equal_history(*copy, *snapshot), "motion copy retains independent segment bytes");
            }

            // All retained intervals intentionally contain the original anchor
            // zero. Public owner advance covers the real long-time evaluation;
            // only the history clock is relocated to avoid billions of appends.
            const MotionProfile constant{8.0, 8.0, 0.7, 1.1, direction};
            checks.status(owner.prepare(constant, 0.125, 8.0, SpeedCommand::Chorale, rate), Status::Ok, "end-epoch owner prepare");
            checks.status(history->prepare(owner, 5), Status::Ok, "end-epoch motion prepare");
            AnalyticMotion reference(constant, 0.125, 8.0, SpeedCommand::Chorale, rate);
            for (std::uint64_t frame = 0; frame < 5; ++frame) {
                checks.status(owner.advance_to(frame), Status::Ok, "end-epoch original segment seed advance");
                checks.status(history->append(owner), Status::Ok, "end-epoch original segment seed append");
            }
            Access::relocate_clock(*history, static_cast<std::uint64_t>(limit - 2));
            for (const auto frame : std::array<std::int64_t, 2>{limit - 2, limit - 1}) {
                checks.status(owner.advance_to(static_cast<std::uint64_t>(frame)), Status::Ok, "last owner interval advance");
                checks.status(history->append(owner), Status::Ok, "last legal motion interval append");
                check_motion_value(checks, results, *history, reference, {frame, std::nextafter(1.0, 0.0)});
            }
            checks.status(owner.advance_to(static_cast<std::uint64_t>(limit)), Status::Ok, "owner end boundary");
            check_motion_value(checks, results, *history, reference, {limit, 0.0});
            MotionState boundary;
            checks.status(history->state_at({limit, 0.0}, boundary), Status::Ok, "exact final motion endpoint");
            checks.check(Access::equal_state(boundary, owner.state()), "final retained endpoint matches exact owner state");
            reject_history(checks, *history, Status::TimelineOverflow, "exhausted motion append", [&] { return history->append(owner); });
            check_motion_value(checks, results, *history, reference, {-limit, 0.0});
            ++results.accelerated_epoch_fixtures;
        }
    }

    const MotionProfile profile{4.0, 40.0, 0.7, 1.1, 1};
    checks.status(owner.prepare(profile, 0.25, 8.0, SpeedCommand::Chorale, 48000.0), Status::Ok, "admission owner seed");
    checks.status(history->prepare(owner, 4), Status::Ok, "admission history seed");
    for (const auto capacity : std::array<std::size_t, 3>{0, kMaxHistoryFrames + 1, std::numeric_limits<std::size_t>::max()}) {
        reject_history(checks, *history, Status::InvalidSpec, "invalid motion capacity", [&] { return history->prepare(owner, capacity); });
    }
    RotaryMotion incompatible;
    reject_history(checks, *history, Status::NotPrepared, "unprepared matching owner", [&] { return history->append(incompatible); });
    checks.status(incompatible.prepare(profile, 0.25, 8.0, SpeedCommand::Chorale, 96000.0), Status::Ok, "mismatched rate owner seed");
    reject_history(checks, *history, Status::InvalidSpec, "mismatched owner rate", [&] { return history->append(incompatible); });
    auto other_profile = profile;
    other_profile.fast_rad_s = 41.0;
    checks.status(incompatible.prepare(other_profile, 0.25, 8.0, SpeedCommand::Chorale, 48000.0), Status::Ok, "mismatched profile owner seed");
    reject_history(checks, *history, Status::InvalidProfile, "mismatched owner profile", [&] { return history->append(incompatible); });
    checks.status(incompatible.prepare(profile, 0.5, 8.0, SpeedCommand::Chorale, 48000.0), Status::Ok, "mismatched epoch owner seed");
    reject_history(checks, *history, Status::InvalidProfile, "mismatched owner epoch seed", [&] { return history->append(incompatible); });
    checks.status(owner.apply_command(0, SpeedCommand::Tremolo), Status::Ok, "continuity branch command");
    checks.status(history->append(owner), Status::Ok, "continuity branch append");
    checks.status(incompatible.prepare(profile, 0.25, 8.0, SpeedCommand::Chorale, 48000.0), Status::Ok, "divergent past owner seed");
    checks.status(incompatible.advance_to(1), Status::Ok, "divergent past exact frame");
    reject_history(checks, *history, Status::InvalidProfile, "matching metadata but discontinuous physical state", [&] {
        return history->append(incompatible);
    });
    checks.status(owner.advance_to(2), Status::Ok, "future owner boundary");
    reject_history(checks, *history, Status::InvalidEvent, "future owner append boundary", [&] { return history->append(owner); });
}

void write_json_string(std::ostream& out, std::string_view value) {
    out << '"';
    for (const char character : value) {
        if (character == '"' || character == '\\') out << '\\' << character;
        else if (character == '\n') out << "\\n";
        else out << character;
    }
    out << '"';
}

void write_stats(std::ostream& out, const ErrorStats& stats) {
    out << "{\"count\":" << stats.count << ",\"finite\":" << (stats.finite ? "true" : "false")
        << ",\"maximum\":" << stats.maximum << ",\"rms\":" << stats.rms()
        << ",\"worst_indices\":[" << stats.worst_a << ',' << stats.worst_b << "]}";
}

void write_report(std::ostream& out, const Checks& checks, const Results& results, std::string_view grid_path) {
    out << std::setprecision(std::numeric_limits<long double>::max_digits10)
        << "{\"status\":\"" << (checks.failures.empty() ? "pass" : "fail")
        << "\",\"experiment\":\"rotary-history-acceptance-a14-v1\",\"contract\":\"rotary-numerics-v1\","
        << "\"scope\":\"native cubic and owned histories; not complete renderer R4, R5, R6 or physical M7\","
        << "\"checks\":" << checks.count << ",\"rejected_calls\":" << checks.rejected_calls
        << ",\"compiler\":";
#ifdef __VERSION__
    write_json_string(out, __VERSION__);
#else
    write_json_string(out, "compiler macro unavailable");
#endif
    out << ",\"precision\":{\"double_bytes\":" << sizeof(double)
        << ",\"double_digits\":" << std::numeric_limits<double>::digits
        << ",\"double_max_digits10\":" << std::numeric_limits<double>::max_digits10
        << ",\"long_double_bytes\":" << sizeof(long double)
        << ",\"long_double_digits\":" << std::numeric_limits<long double>::digits
        << ",\"long_double_max_digits10\":" << std::numeric_limits<long double>::max_digits10
        << ",\"radix\":" << std::numeric_limits<long double>::radix
        << ",\"rounding_mode\":" << std::fegetround() << "},\"tuple_seed\":\"0xa14c0b1c5eed1234\","
        << "\"polynomial_product\":";
    write_stats(out, results.polynomial_product);
    out << ",\"polynomial_analytic\":"; write_stats(out, results.polynomial_analytic);
    out << ",\"additional_product\":"; write_stats(out, results.additional_product);
    out << ",\"static_product\":"; write_stats(out, results.static_product);
    out << ",\"static_full_band\":"; write_stats(out, results.static_full_band);
    out << ",\"static_low_band\":"; write_stats(out, results.static_low_band);
    out << ",\"static_full_band_above_low_budget\":" << results.full_band_above_low_budget
        << ",\"static_grid\":{\"evaluated_rows\":" << results.static_full_band.count
        << ",\"written_rows\":" << results.static_rows_written << ",\"columns\":7,\"path\":";
    write_json_string(out, grid_path);
    out << "},\"waveform_product\":"; write_stats(out, results.waveform_product);
    out << ",\"motion_angle\":"; write_stats(out, results.motion_angle);
    out << ",\"motion_speed\":"; write_stats(out, results.motion_speed);
    out << ",\"cubic_endpoints\":" << results.endpoint_cases
        << ",\"aliased_cubic_cases\":" << results.aliased_cases
        << ",\"waveform_reads\":" << results.waveform_reads
        << ",\"waveform_interpolations\":" << results.waveform_interpolations
        << ",\"waveform_pushes\":" << results.waveform_pushes
        << ",\"motion_appends\":" << results.motion_appends
        << ",\"accelerated_epoch_fixtures\":" << results.accelerated_epoch_fixtures
        << ",\"budgets\":{\"cubic\":2e-12,\"low_band_complex\":0.005},\"failures\":[";
    for (std::size_t index = 0; index < checks.failures.size(); ++index) {
        if (index != 0) out << ',';
        write_json_string(out, checks.failures[index]);
    }
    out << "]}\n";
}
} // namespace

int main(int argc, char** argv) {
    std::string grid_path;
    std::string report_path;
    for (int argument = 1; argument < argc; ++argument) {
        const std::string_view option(argv[argument]);
        if ((option == "--static-grid" || option == "--report") && argument + 1 < argc) {
            const std::string value(argv[++argument]);
            if (option == "--static-grid") grid_path = value;
            else report_path = value;
        } else {
            std::cerr << "usage: test_rotary_history_acceptance [--static-grid CSV] [--report JSON]\n";
            return 2;
        }
    }
    std::ofstream grid;
    if (!grid_path.empty()) {
        grid.open(grid_path, std::ios::out | std::ios::trunc);
        if (!grid) { std::cerr << "cannot open static grid output\n"; return 2; }
    }
    Checks checks;
    Results results;
    cubic_acceptance(checks, results);
    static_delay_grid(checks, results, grid.is_open() ? &grid : nullptr);
    waveform_acceptance(checks, results);
    motion_acceptance(checks, results);
    if (grid.is_open()) {
        grid.flush();
        checks.group = "artifact";
        checks.check(grid.good(), "static grid flush");
    }
    if (!report_path.empty()) {
        std::ofstream report(report_path, std::ios::out | std::ios::trunc);
        if (!report) { std::cerr << "cannot open report output\n"; return 2; }
        write_report(report, checks, results, grid_path);
        report.flush();
        if (!report.good()) { std::cerr << "cannot flush report output\n"; return 2; }
    }
    write_report(std::cout, checks, results, grid_path);
    return checks.failures.empty() ? 0 : 1;
}
