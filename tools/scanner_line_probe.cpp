#include "CliArguments.h"
#include "hammond/ScannerLine.h"
#include "hammond/detail/Decimal.h"

#include <algorithm>
#include <array>
#include <charconv>
#include <cmath>
#include <complex>
#include <cstddef>
#include <cstdint>
#include <exception>
#include <iomanip>
#include <iostream>
#include <limits>
#include <locale>
#include <numbers>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <system_error>
#include <vector>

namespace {

using hammond::ScannerLine;
using hammond::ScannerLineFrame;
using hammond::ScannerLineState;
using hammond::ScannerReturnMode;
using hammond::Status;
constexpr std::size_t kChannels = hammond::kScannerTapCount + 2;
constexpr std::size_t kMaximumFrequencies = 1024;
constexpr std::size_t kMaximumTraceFrames = 16384;
constexpr std::uint64_t kMaximumSineFrames = 16777216;
constexpr std::size_t kMaximumArgumentBytes = 32768;
constexpr std::size_t kMaximumJsonBytes = 64 * 1024 * 1024;

[[noreturn]] void fail(const std::string& message) {
    throw std::runtime_error(message);
}

void require_status(Status status, std::string_view context) {
    if (status != Status::Ok) {
        fail(std::string(context) + ": " + hammond::status_name(status));
    }
}

[[nodiscard]] double real_number(std::string_view text) {
    if (text.empty() || text.size() > 128) fail("A number requires 1..128 bytes.");
    double value = 0.0;
    if (hammond::detail::parse_decimal(text, value) != hammond::detail::DecimalResult::Ok
        || !std::isfinite(value)) {
        fail("Expected a complete finite decimal number.");
    }
    return value;
}

[[nodiscard]] std::uint64_t unsigned_number(std::string_view text) {
    if (text.empty() || text.size() > 20) fail("An unsigned integer requires 1..20 digits.");
    for (const char character : text) {
        if (character < '0' || character > '9') fail("Expected unsigned decimal digits.");
    }
    std::uint64_t value = 0;
    const auto result = std::from_chars(text.data(), text.data() + text.size(), value);
    if (result.ec != std::errc{} || result.ptr != text.data() + text.size()) {
        fail("Unsigned integer exceeds uint64 range.");
    }
    return value;
}

[[nodiscard]] std::vector<double> real_list(std::string_view text, std::size_t maximum) {
    std::vector<double> result;
    std::size_t start = 0;
    for (;;) {
        if (result.size() == maximum) fail("Too many comma-separated values.");
        const auto end = text.find(',', start);
        result.push_back(real_number(text.substr(start, end == std::string_view::npos
                                                       ? end : end - start)));
        if (end == std::string_view::npos) break;
        start = end + 1;
    }
    return result;
}

struct Options {
    std::string_view operation;
    double sample_rate{0.0};
    ScannerReturnMode mode{ScannerReturnMode::Vibrato};
    std::vector<double> frequencies;
    double frequency{0.0};
    double amplitude{1.0};
    std::uint64_t warmup_frames{65536};
    std::uint64_t measurement_frames{65536};
    ScannerLineState initial_state{};
};

[[nodiscard]] Options parse_options(int argc, char** argv) {
    constexpr std::array<std::string_view, 12> names{
        "--operation", "--sample-rate", "--mode", "--frequencies", "--frequency",
        "--amplitude", "--warmup-frames", "--measurement-frames", "--capacitor-volts",
        "--inductor-amps", "--previous-input", "--initial-frame"};
    if (argc < 1 || argc > 1 + 2 * static_cast<int>(names.size())) {
        fail("Too many command-line arguments.");
    }
    std::array<bool, names.size()> seen{};
    Options options;
    for (int argument = 1; argument < argc; ++argument) {
        const std::string_view name(argv[argument]);
        const auto found = std::find(names.begin(), names.end(), name);
        if (found == names.end()) fail("Unknown option: " + std::string(name));
        const auto index = static_cast<std::size_t>(found - names.begin());
        if (seen[index]) fail("Duplicate option: " + std::string(name));
        seen[index] = true;
        if (++argument >= argc) fail("Missing option value: " + std::string(name));
        const std::string_view value(argv[argument]);
        if (value.empty() || value.size() > kMaximumArgumentBytes) {
            fail("Option values require 1..32768 bytes.");
        }
        switch (index) {
        case 0:
            if (value != "response" && value != "sine" && value != "trace") {
                fail("Operation must be response, sine or trace.");
            }
            options.operation = value;
            break;
        case 1: options.sample_rate = real_number(value); break;
        case 2:
            if (value == "vibrato") options.mode = ScannerReturnMode::Vibrato;
            else if (value == "chorus") options.mode = ScannerReturnMode::Chorus;
            else fail("Mode must be vibrato or chorus.");
            break;
        case 3: options.frequencies = real_list(value, kMaximumFrequencies); break;
        case 4: options.frequency = real_number(value); break;
        case 5: options.amplitude = real_number(value); break;
        case 6: options.warmup_frames = unsigned_number(value); break;
        case 7: options.measurement_frames = unsigned_number(value); break;
        case 8:
        case 9: {
            const auto values = real_list(value, hammond::kScannerSectionCount);
            if (values.size() != hammond::kScannerSectionCount) {
                fail("Physical-state lists require exactly 18 values.");
            }
            auto& destination = index == 8 ? options.initial_state.capacitor_volts
                                          : options.initial_state.inductor_amps;
            std::copy(values.begin(), values.end(), destination.begin());
            break;
        }
        case 10: options.initial_state.previous_input_volts = real_number(value); break;
        case 11: options.initial_state.frames = unsigned_number(value); break;
        default: fail("Internal option index.");
        }
    }
    for (std::size_t index = 0; index < 3; ++index) {
        if (!seen[index]) fail("Required option: " + std::string(names[index]));
    }
    if (!hammond::is_supported_scanner_sample_rate(options.sample_rate)) {
        fail("Unsupported scanner research sample rate.");
    }
    for (std::size_t index = 3; index < names.size(); ++index) {
        const bool allowed = options.operation == "response" ? index == 3
                           : options.operation == "sine" ? index >= 4 && index <= 7
                                                         : index >= 8;
        if (seen[index] && !allowed) {
            fail("Option is not applicable to this operation: " + std::string(names[index]));
        }
    }
    if (options.operation == "response") {
        if (!seen[3]) fail("Response requires --frequencies.");
        for (const double frequency : options.frequencies) {
            if (frequency < 0.0 || frequency >= options.sample_rate / 2.0) {
                fail("Response frequencies require 0 <= Hz < sample_rate/2.");
            }
        }
    } else if (options.operation == "sine") {
        if (!seen[4]) fail("Sine requires --frequency.");
        if (options.frequency <= 0.0 || options.frequency >= options.sample_rate / 2.0) {
            fail("Sine frequency requires 0 < Hz < sample_rate/2.");
        }
        if (options.amplitude <= 0.0 || options.amplitude > hammond::kScannerMaxInputVolts) {
            fail("Sine amplitude requires 0 < volts <= 64.");
        }
        if (options.warmup_frames > kMaximumSineFrames || options.measurement_frames < 8
            || options.measurement_frames > kMaximumSineFrames - options.warmup_frames) {
            fail("Sine requires at least 8 measured frames and at most 16777216 total frames.");
        }
        if (static_cast<double>(options.measurement_frames) * options.frequency
            / options.sample_rate < 4.0) {
            fail("The measurement window must span at least four sine cycles.");
        }
    }
    return options;
}

template <typename Value, std::size_t Count>
void write_array(std::ostream& output, const std::array<Value, Count>& values) {
    output << '[';
    for (std::size_t index = 0; index < values.size(); ++index) {
        if (index != 0) output << ',';
        output << values[index];
    }
    output << ']';
}

void write_complex(std::ostream& output, const std::complex<double>& value) {
    output << '[' << value.real() << ',' << value.imag() << ']';
}

template <std::size_t Count>
void write_complex_array(std::ostream& output,
                         const std::array<std::complex<double>, Count>& values) {
    output << '[';
    for (std::size_t index = 0; index < values.size(); ++index) {
        if (index != 0) output << ',';
        write_complex(output, values[index]);
    }
    output << ']';
}

void write_state(std::ostream& output, const ScannerLineState& state) {
    output << "{\"capacitor_volts\":";
    write_array(output, state.capacitor_volts);
    output << ",\"inductor_amps\":";
    write_array(output, state.inductor_amps);
    output << ",\"previous_input_volts\":" << state.previous_input_volts
           << ",\"frames\":" << state.frames << '}';
}

void write_frame_fields(std::ostream& output, const ScannerLineFrame& frame) {
    output << "\"frame\":" << frame.frame << ",\"taps_volts\":";
    write_array(output, frame.taps_volts);
    output << ",\"return_volts\":" << frame.return_volts
           << ",\"input_current_amps\":" << frame.input_current_amps
           << ",\"energy_joules\":" << frame.energy_joules;
}

void write_preamble(std::ostream& output, const Options& options, const ScannerLine& line) {
    output << "{\"schema_version\":1,\"probe_id\":\"scanner-line-probe-v1\","
              "\"evidence_scope\":\"synthetic_nominal_engineering\",\"operation\":\""
           << options.operation << "\",\"model_id\":\"" << hammond::kScannerLineModelId
           << "\",\"realization_id\":\"" << hammond::kScannerLineRealizationId
           << "\",\"authoring_sha256\":\"" << ScannerLine::authoring_sha256()
           << "\",\"sample_rate_hz\":" << options.sample_rate << ",\"mode\":\""
           << (options.mode == ScannerReturnMode::Vibrato ? "vibrato" : "chorus")
           << "\",\"clock_convention\":\"previous_endpoint_at_minus_one_sample;"
              "first_processed_knot_at_zero;frame_counts_completed_intervals\","
              "\"preparation_residual\":" << line.preparation_residual();
}

void response_report(std::ostream& output, const Options& options, const ScannerLine& line) {
    output << ",\"measurement_method\":\"prepared_discrete_recurrence_solve\",\"responses\":[";
    for (std::size_t index = 0; index < options.frequencies.size(); ++index) {
        hammond::ScannerLineResponse response;
        require_status(line.response(options.frequencies[index], options.mode, response),
                       "Response rejected");
        if (index != 0) output << ',';
        output << "{\"frequency_hz\":" << options.frequencies[index] << ",\"taps\":";
        write_complex_array(output, response.taps);
        output << ",\"return_gain\":";
        write_complex(output, response.return_gain);
        output << ",\"input_admittance\":";
        write_complex(output, response.input_admittance);
        output << ",\"normalized_residual\":" << response.normalized_residual
               << ",\"condition_inf\":" << response.condition_inf << '}';
    }
    output << ']';
}

using Channels = std::array<double, kChannels>;
using Transfers = std::array<std::complex<double>, kChannels>;

[[nodiscard]] Channels channels(const ScannerLineFrame& frame) noexcept {
    Channels result{};
    std::copy(frame.taps_volts.begin(), frame.taps_volts.end(), result.begin());
    result[hammond::kScannerTapCount] = frame.return_volts;
    result[hammond::kScannerTapCount + 1] = frame.input_current_amps;
    return result;
}

struct FitResult {
    Transfers transfer{};
    Channels residual_rms{};
};

// A three-column least-squares fit accepts non-bin-centered frequencies. The
// constant column avoids conflating a small remaining DC offset with phase.
// Long-double accumulation reduces cancellation in a long measurement window;
// no fitted timing, amplitude or polarity correction is applied.
struct SineFit {
    using Row = std::array<long double, 3>;
    std::array<Row, 3> gram{};
    std::array<Row, kChannels> rhs{};
    std::array<long double, kChannels> squares{};
    std::uint64_t count{0};

    void add(double cosine, double sine, const Channels& values) noexcept {
        const Row basis{cosine, sine, 1.0L};
        for (std::size_t row = 0; row < 3; ++row) {
            for (std::size_t column = 0; column < 3; ++column) {
                gram[row][column] += basis[row] * basis[column];
            }
        }
        for (std::size_t channel = 0; channel < kChannels; ++channel) {
            const auto value = static_cast<long double>(values[channel]);
            for (std::size_t column = 0; column < 3; ++column) {
                rhs[channel][column] += value * basis[column];
            }
            squares[channel] += value * value;
        }
        ++count;
    }

    [[nodiscard]] FitResult solve(double amplitude) const {
        if (count < 4) fail("Insufficient sine fit samples.");
        auto matrix = gram;
        auto right = rhs;
        long double norm = 0.0L;
        for (const auto& row : matrix) {
            long double sum = 0.0L;
            for (const auto value : row) sum += std::abs(value);
            norm = std::max(norm, sum);
        }
        for (std::size_t column = 0; column < 3; ++column) {
            std::size_t pivot = column;
            for (std::size_t row = column + 1; row < 3; ++row) {
                if (std::abs(matrix[row][column]) > std::abs(matrix[pivot][column])) pivot = row;
            }
            if (std::abs(matrix[pivot][column])
                <= 1.0e-12L * norm) fail("Sine fit is ill-conditioned; extend the window.");
            std::swap(matrix[pivot], matrix[column]);
            for (auto& row : right) std::swap(row[pivot], row[column]);
            for (std::size_t row = column + 1; row < 3; ++row) {
                const auto factor = matrix[row][column] / matrix[column][column];
                for (std::size_t other = column; other < 3; ++other) {
                    matrix[row][other] -= factor * matrix[column][other];
                }
                for (auto& values : right) values[row] -= factor * values[column];
            }
        }
        FitResult result;
        for (std::size_t channel = 0; channel < kChannels; ++channel) {
            Row coefficients{};
            for (std::size_t reverse = 3; reverse > 0; --reverse) {
                const auto row = reverse - 1;
                auto value = right[channel][row];
                for (std::size_t column = row + 1; column < 3; ++column) {
                    value -= matrix[row][column] * coefficients[column];
                }
                coefficients[row] = value / matrix[row][row];
            }
            const auto real = static_cast<double>(coefficients[0] / amplitude);
            const auto imaginary = static_cast<double>(-coefficients[1] / amplitude);
            auto squared_error = squares[channel];
            for (std::size_t column = 0; column < 3; ++column) {
                squared_error -= coefficients[column] * rhs[channel][column];
            }
            // Roundoff in y'y-beta'X'y can be slightly negative at exact fits.
            // This nonnegative diagnostic is not the qualification criterion.
            const auto rms = static_cast<double>(std::sqrt(std::max(0.0L, squared_error)
                                                  / static_cast<long double>(count)));
            if (!std::isfinite(real) || !std::isfinite(imaginary) || !std::isfinite(rms)) {
                fail("Nonfinite sine fit result.");
            }
            result.transfer[channel] = {real, imaginary};
            result.residual_rms[channel] = rms;
        }
        return result;
    }
};

void write_transfers(std::ostream& output, const Transfers& values) {
    output << "{\"taps\":[";
    for (std::size_t index = 0; index < hammond::kScannerTapCount; ++index) {
        if (index != 0) output << ',';
        write_complex(output, values[index]);
    }
    output << "],\"return_gain\":";
    write_complex(output, values[hammond::kScannerTapCount]);
    output << ",\"input_admittance\":";
    write_complex(output, values[hammond::kScannerTapCount + 1]);
    output << '}';
}

void sine_report(std::ostream& output, const Options& options, ScannerLine& line) {
    SineFit whole, first_half, second_half;
    const auto count = options.warmup_frames + options.measurement_frames;
    for (std::uint64_t index = 0; index < count; ++index) {
        const auto turns = static_cast<long double>(options.frequency)
                         * static_cast<long double>(index)
                         / static_cast<long double>(options.sample_rate);
        const auto angle = 2.0L * std::numbers::pi_v<long double> * std::remainder(turns, 1.0L);
        const auto cosine = static_cast<double>(std::cos(angle));
        const auto sine = static_cast<double>(std::sin(angle));
        ScannerLineFrame frame;
        require_status(line.process_frame(options.amplitude * cosine, options.mode, frame),
                       "Sine process_frame rejected");
        if (index < options.warmup_frames) continue;
        const auto values = channels(frame);
        whole.add(cosine, sine, values);
        if (index - options.warmup_frames < options.measurement_frames / 2) {
            first_half.add(cosine, sine, values);
        } else {
            second_half.add(cosine, sine, values);
        }
    }
    const auto fit = whole.solve(options.amplitude);
    const auto early = first_half.solve(options.amplitude);
    const auto late = second_half.solve(options.amplitude);
    double half_difference = 0.0;
    for (std::size_t channel = 0; channel < kChannels; ++channel) {
        const auto scale = channel == kChannels - 1 ? 15000.0 : 1.0;
        half_difference = std::max(half_difference,
            scale * std::abs(early.transfer[channel] - late.transfer[channel]));
    }
    output << ",\"measurement_method\":\"actual_process_frame_cos_sin_constant_least_squares\","
              "\"drive\":\"amplitude*cos(2*pi*frequency*knot_index/sample_rate)\","
              "\"startup_convergence_status\":\"caller_must_compare_longer_warmup\","
              "\"frequency_hz\":" << options.frequency
           << ",\"amplitude_volts\":" << options.amplitude
           << ",\"warmup_frames\":" << options.warmup_frames
           << ",\"measurement_frames\":" << options.measurement_frames
           << ",\"first_half_frames\":" << first_half.count
           << ",\"second_half_frames\":" << second_half.count << ",\"transfer\":";
    write_transfers(output, fit.transfer);
    output << ",\"first_half_transfer\":";
    write_transfers(output, early.transfer);
    output << ",\"second_half_transfer\":";
    write_transfers(output, late.transfer);
    output << ",\"half_window_max_difference\":" << half_difference
           << ",\"half_window_current_scale_ohms\":15000,\"fit_residual_rms\":{\"taps_volts\":[";
    for (std::size_t index = 0; index < hammond::kScannerTapCount; ++index) {
        if (index != 0) output << ',';
        output << fit.residual_rms[index];
    }
    output << "],\"return_volts\":" << fit.residual_rms[hammond::kScannerTapCount]
           << ",\"input_current_amps\":" << fit.residual_rms[hammond::kScannerTapCount + 1]
           << "},\"final_state\":";
    write_state(output, line.state());
}

[[nodiscard]] std::vector<double> read_inputs() {
    std::vector<double> inputs;
    std::string token;
    token.reserve(128);
    const auto append = [&]() {
        if (!token.empty() && token.back() == '\r') token.pop_back();
        if (inputs.size() == kMaximumTraceFrames) fail("Trace exceeds 16384 input knots.");
        const auto value = real_number(token);
        if (std::abs(value) > hammond::kScannerMaxInputVolts) fail("Trace input exceeds 64 volts.");
        inputs.push_back(value);
        token.clear();
    };
    for (;;) {
        const auto next = std::cin.get();
        if (next == std::char_traits<char>::eof()) break;
        const auto character = static_cast<char>(next);
        if (character == '\n') append();
        else {
            if (token.size() == 128) fail("Trace input line exceeds 128 bytes.");
            token.push_back(character);
        }
    }
    if (std::cin.bad() || (!std::cin.eof() && std::cin.fail())) fail("Cannot read trace input.");
    if (!token.empty()) append();
    if (inputs.empty()) fail("Trace requires at least one input knot on stdin.");
    return inputs;
}

void trace_report(std::ostream& output, const Options& options, ScannerLine& line) {
    require_status(line.restore_state(options.initial_state), "Initial checkpoint rejected");
    const auto inputs = read_inputs();
    if (inputs.size() > std::numeric_limits<std::uint64_t>::max() - options.initial_state.frames) {
        fail("Trace would overflow its completed-interval count.");
    }
    ScannerLineFrame observed;
    require_status(line.observe(options.mode, observed), "Initial observation rejected");
    output << ",\"measurement_method\":\"actual_process_frame_endpoint_trace\","
              "\"input_reconstruction\":\"trapezoidal_endpoint_forcing\","
              "\"time_origin\":\"relative_to_first_supplied_input_knot\","
              "\"initial_state\":";
    write_state(output, options.initial_state);
    output << ",\"initial_observation\":{\"time_seconds\":" << -1.0 / options.sample_rate << ',';
    write_frame_fields(output, observed);
    output << "},\"frames\":[";
    for (std::size_t index = 0; index < inputs.size(); ++index) {
        ScannerLineFrame frame;
        require_status(line.process_frame(inputs[index], options.mode, frame), "Trace frame rejected");
        if (index != 0) output << ',';
        output << "{\"knot_index\":" << index << ",\"time_seconds\":"
               << static_cast<double>(index) / options.sample_rate
               << ",\"input_volts\":" << inputs[index] << ',';
        write_frame_fields(output, frame);
        output << ",\"state\":";
        write_state(output, line.state());
        output << '}';
    }
    output << "]";
}

[[nodiscard]] std::string make_report(const Options& options) {
    const hammond::detail::DecimalRounding rounding;
    if (!rounding.ready()) fail("Cannot select nearest rounding for the probe.");
    ScannerLine line;
    require_status(line.prepare(options.sample_rate), "Preparation rejected");
    std::ostringstream output;
    output.imbue(std::locale::classic());
    output << std::setprecision(std::numeric_limits<double>::max_digits10);
    write_preamble(output, options, line);
    if (options.operation == "response") response_report(output, options, line);
    else if (options.operation == "sine") sine_report(output, options, line);
    else trace_report(output, options, line);
    output << "}\n";
    if (!output) fail("Cannot construct JSON report.");
    auto result = output.str();
    if (result.size() > kMaximumJsonBytes) fail("JSON report exceeds 64 MiB.");
    return result;
}

} // namespace

static int scanner_line_probe_main(int argc, char** argv) {
    try {
        if (argc == 2 && std::string_view(argv[1]) == "--help") {
            std::cout <<
                "Usage: hammond_scanner_line_probe --operation response|sine|trace\n"
                "       --sample-rate HZ --mode vibrato|chorus [operation options]\n"
                "response: --frequencies CSV (1..1024 values, 0 <= Hz < Nyquist)\n"
                "sine: --frequency HZ [--amplitude V] [--warmup-frames N]\n"
                "      [--measurement-frames N]; defaults 1 V, 65536 + 65536 frames.\n"
                "      At least four measured cycles, 8 measured frames; total <=16777216.\n"
                "trace: one input voltage per stdin line, 1..16384 knots, |V|<=64.\n"
                "       [--capacitor-volts CSV18] [--inductor-amps CSV18]\n"
                "       [--previous-input V] [--initial-frame UINT64]; defaults zero.\n"
                "Each applicable option appears at most once; --help must be used alone.\n"
                "Research rates: 44100/48000/96000 times 1/2/4/8/16; no host API change.\n"
                "JSON on stdout only after complete success; errors on stderr, exit 1.\n"
                "The tool opens no output file. Shell redirection has its own overwrite behavior.\n"
                "Nominal unloaded line; response helper, actual sine and trace are distinct.\n";
            std::cout.flush();
            if (!std::cout) fail("Cannot write help output.");
            return 0;
        }
        const auto options = parse_options(argc, argv);
        const auto report = make_report(options);
        std::cout.write(report.data(), static_cast<std::streamsize>(report.size()));
        std::cout.flush();
        if (!std::cout) fail("Cannot write JSON report.");
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "hammond_scanner_line_probe: " << error.what() << '\n';
        return 1;
    } catch (...) {
        std::cerr << "hammond_scanner_line_probe: unexpected failure.\n";
        return 1;
    }
}

#ifdef _WIN32
int wmain(int argc, wchar_t* argv[]) {
    return hammond::cli::run_windows(argc, argv, scanner_line_probe_main,
        "hammond_scanner_line_probe", {25, kMaximumArgumentBytes,
        "Too many command-line arguments.", "Invalid or oversized Unicode argument."});
}
#else
int main(int argc, char* argv[]) {
    return scanner_line_probe_main(argc, argv);
}
#endif
