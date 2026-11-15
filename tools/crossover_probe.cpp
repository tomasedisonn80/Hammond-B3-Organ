#include "hammond/LeslieCrossover.h"
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
using hammond::LeslieCrossover;
using hammond::LeslieCrossoverFrame;
using hammond::LeslieCrossoverLoads;
using hammond::LeslieCrossoverResponse;
using hammond::Status;
constexpr std::size_t kMaximumFrequencies = 512;
constexpr std::size_t kMaximumArgumentBytes = 32768;
constexpr std::uint64_t kMaximumSineFrames = 16777216;
constexpr std::size_t kMaximumReportBytes = 2 * 1024 * 1024;
constexpr std::array<std::string_view, 3> kPortNames{
    "treble_gain", "bass_gain", "input_admittance"};

[[noreturn]] void fail(const std::string& message) { throw std::runtime_error(message); }
void require_status(Status status, std::string_view operation) {
    if (status != Status::Ok) fail(std::string(operation) + ": " + hammond::status_name(status));
}

[[nodiscard]] double real_number(std::string_view text) {
    double value = 0.0;
    if (text.empty() || text.size() > 128 ||
        hammond::detail::parse_decimal(text, value) != hammond::detail::DecimalResult::Ok ||
        !std::isfinite(value)) fail("Expected a complete finite decimal number of 1..128 bytes.");
    return value;
}

[[nodiscard]] std::uint64_t unsigned_number(std::string_view text) {
    if (text.empty() || text.size() > 20) fail("Expected 1..20 unsigned decimal digits.");
    for (const char digit : text) {
        if (digit < '0' || digit > '9') fail("Expected unsigned decimal digits.");
    }
    std::uint64_t value = 0;
    const auto parsed = std::from_chars(text.data(), text.data() + text.size(), value);
    if (parsed.ec != std::errc{} || parsed.ptr != text.data() + text.size()) {
        fail("Unsigned integer exceeds uint64 range.");
    }
    return value;
}

[[nodiscard]] std::vector<double> frequency_list(std::string_view text) {
    std::vector<double> result;
    std::size_t start = 0;
    for (;;) {
        if (result.size() == kMaximumFrequencies) fail("At most 512 response frequencies are admitted.");
        const auto end = text.find(',', start);
        result.push_back(real_number(text.substr(start, end == std::string_view::npos ? end : end - start)));
        if (end == std::string_view::npos) break;
        start = end + 1;
    }
    return result;
}

struct Options {
    std::string_view operation{};
    double sample_rate{0.0};
    LeslieCrossoverLoads loads{};
    std::vector<double> frequencies{};
    double frequency{0.0};
    double amplitude{0.25};
    std::uint64_t warmup_frames{65536};
    std::uint64_t measurement_frames{8192};
};

[[nodiscard]] Options parse_options(int argc, char* argv[]) {
    constexpr std::array<std::string_view, 9> names{
        "--operation", "--sample-rate", "--treble-ohms", "--bass-ohms", "--frequencies",
        "--frequency", "--amplitude", "--warmup-frames", "--measurement-frames"};
    if (argc < 1 || argc > 1 + 2 * static_cast<int>(names.size())) fail("Too many command-line arguments.");
    Options result;
    std::array<bool, names.size()> seen{};
    for (int at = 1; at < argc; ++at) {
        const std::string_view name(argv[at]);
        const auto found = std::find(names.begin(), names.end(), name);
        if (found == names.end()) fail("Unknown option: " + std::string(name));
        const auto index = static_cast<std::size_t>(found - names.begin());
        if (seen[index]) fail("Duplicate option: " + std::string(name));
        seen[index] = true;
        if (++at >= argc) fail("Missing value: " + std::string(name));
        const std::string_view value(argv[at]);
        if (value.empty() || value.size() > kMaximumArgumentBytes) fail("Option value exceeds its byte bound or is empty.");
        switch (index) {
        case 0: result.operation = value; break;
        case 1: result.sample_rate = real_number(value); break;
        case 2: result.loads.treble_ohms = real_number(value); break;
        case 3: result.loads.bass_ohms = real_number(value); break;
        case 4: result.frequencies = frequency_list(value); break;
        case 5: result.frequency = real_number(value); break;
        case 6: result.amplitude = real_number(value); break;
        case 7: result.warmup_frames = unsigned_number(value); break;
        case 8: result.measurement_frames = unsigned_number(value); break;
        default: fail("Internal option index.");
        }
    }
    if (!seen[0] || !seen[1]) fail("--operation and --sample-rate are required.");
    if (result.operation != "response" && result.operation != "sine") fail("Operation must be response or sine.");
    if (result.sample_rate != 44100.0 && result.sample_rate != 48000.0 &&
        result.sample_rate != 96000.0 && result.sample_rate != 192000.0) fail("Unsupported research sample rate.");
    if (result.loads.treble_ohms < 1.0 || result.loads.treble_ohms > 1024.0 ||
        result.loads.bass_ohms < 1.0 || result.loads.bass_ohms > 1024.0) fail("Resistive loads must be in [1,1024] ohm.");
    for (std::size_t index = 4; index < names.size(); ++index) {
        const bool applicable = result.operation == "response" ? index == 4 : index >= 5;
        if (seen[index] && !applicable) fail("Option is not applicable: " + std::string(names[index]));
    }
    if (result.operation == "response") {
        if (!seen[4]) fail("Response requires --frequencies.");
        for (const double frequency : result.frequencies) {
            if (frequency < 0.0 || frequency >= result.sample_rate / 2.0) fail("Response frequencies require 0 <= f < Nyquist.");
        }
    } else {
        if (!seen[5]) fail("Sine requires --frequency.");
        if (result.frequency <= 0.0 || result.frequency >= result.sample_rate / 2.0) fail("Sine frequency requires 0 < f < Nyquist.");
        if (result.amplitude <= 0.0 || result.amplitude > 64.0) fail("Sine amplitude requires 0 < V <= 64.");
        if (result.measurement_frames < 8 || result.measurement_frames > kMaximumSineFrames ||
            result.warmup_frames > kMaximumSineFrames - result.measurement_frames) {
            fail("Sine requires >=8 measured frames and <=16777216 total frames.");
        }
    }
    return result;
}

void write_complex(std::ostream& output, std::complex<double> value) {
    if (!std::isfinite(value.real()) || !std::isfinite(value.imag())) fail("Nonfinite complex report value.");
    output << "{\"real\":" << value.real() << ",\"imag\":" << value.imag() << '}';
}

void write_ports(std::ostream& output, const std::array<std::complex<double>, 3>& values) {
    output << '{';
    for (std::size_t port = 0; port < values.size(); ++port) {
        if (port != 0) output << ',';
        output << '"' << kPortNames[port] << "\":";
        write_complex(output, values[port]);
    }
    output << '}';
}

void response_report(std::ostream& output, const Options& options, const LeslieCrossover& model) {
    output << ",\"responses\":[";
    for (std::size_t index = 0; index < options.frequencies.size(); ++index) {
        LeslieCrossoverResponse response;
        require_status(model.response(options.frequencies[index], response), "response");
        if (index != 0) output << ',';
        output << "{\"frequency_hz\":" << options.frequencies[index] << ",\"transfer\":";
        write_ports(output, {response.treble_gain, response.bass_gain, response.input_admittance});
        if (!std::isfinite(response.normalized_residual)) fail("Nonfinite response residual.");
        output << ",\"normalized_residual\":" << response.normalized_residual << '}';
    }
    output << "]";
}

struct FitResult {
    std::array<std::complex<double>, 3> gain{};
    // If each measured output's absolute error is <= e, complex gain error is
    // <= this factor * e / amplitude. It bounds the two fitted coefficients.
    double error_amplification_bound{0.0};
};

struct SineFit {
    long double ss{0.0L}, cc{0.0L}, sc{0.0L};
    std::array<long double, 3> ys{}, yc{};
    std::uint64_t count{0};

    void add(double sine, double cosine, const LeslieCrossoverFrame& frame) {
        const long double s = sine, c = cosine;
        ss += s * s; cc += c * c; sc += s * c;
        const std::array<double, 3> values{frame.treble_volts, frame.bass_volts, frame.input_current_amps};
        for (std::size_t port = 0; port < values.size(); ++port) {
            ys[port] += s * values[port];
            yc[port] += c * values[port];
        }
        ++count;
    }

    [[nodiscard]] FitResult solve(double amplitude) const {
        const long double determinant = ss * cc - sc * sc;
        const long double norm = std::max(ss, cc);
        if (count < 4 || !std::isfinite(determinant) ||
            determinant <= 256.0L * std::numeric_limits<double>::epsilon() * norm * norm) {
            fail("Sine fit is ill-conditioned; extend its measurement window.");
        }
        FitResult result;
        for (std::size_t port = 0; port < ys.size(); ++port) {
            const double real = static_cast<double>((cc * ys[port] - sc * yc[port]) / determinant / amplitude);
            const double imaginary = static_cast<double>((ss * yc[port] - sc * ys[port]) / determinant / amplitude);
            if (!std::isfinite(real) || !std::isfinite(imaginary)) fail("Nonfinite sine fit.");
            result.gain[port] = {real, imaginary};
        }
        result.error_amplification_bound = static_cast<double>(static_cast<long double>(count) *
            (ss + cc + 2.0L * std::abs(sc)) / determinant);
        if (!std::isfinite(result.error_amplification_bound)) fail("Nonfinite sine fit conditioning.");
        return result;
    }
};

void sine_report(std::ostream& output, const Options& options, LeslieCrossover& model) {
    SineFit whole, early, late;
    const auto total = options.warmup_frames + options.measurement_frames;
    double maximum_port_magnitude = 0.0;
    for (std::uint64_t frame_number = 1; frame_number <= total; ++frame_number) {
        const long double turns = static_cast<long double>(options.frequency) * static_cast<long double>(frame_number)
                                / static_cast<long double>(options.sample_rate);
        const long double angle = 2.0L * std::numbers::pi_v<long double> * std::remainder(turns, 1.0L);
        const double sine = static_cast<double>(std::sin(angle));
        const double cosine = static_cast<double>(std::cos(angle));
        LeslieCrossoverFrame frame;
        require_status(model.process_frame(options.amplitude * sine, frame), "sine process_frame");
        if (frame.frame != frame_number) fail("Unexpected processed endpoint frame.");
        maximum_port_magnitude = std::max({maximum_port_magnitude, std::abs(frame.treble_volts),
                                          std::abs(frame.bass_volts), std::abs(frame.input_current_amps)});
        if (frame_number <= options.warmup_frames) continue;
        whole.add(sine, cosine, frame);
        if (frame_number - options.warmup_frames <= options.measurement_frames / 2) early.add(sine, cosine, frame);
        else late.add(sine, cosine, frame);
    }
    const auto fit = whole.solve(options.amplitude);
    const auto first = early.solve(options.amplitude);
    const auto second = late.solve(options.amplitude);
    double half_difference = 0.0;
    for (std::size_t port = 0; port < fit.gain.size(); ++port) {
        half_difference = std::max(half_difference, std::abs(first.gain[port] - second.gain[port]));
    }
    output << ",\"drive\":\"amplitude*sin(2*pi*frequency*right_endpoint_frame/sample_rate)\""
              ",\"initial_state\":\"zero physical state and previous input; frame 0\""
              ",\"fit_method\":\"two-column sine/cosine least squares of actual process_frame outputs\""
              ",\"transient_bound\":\"not inferred by this probe; caller must independently qualify warmup\""
           << ",\"frequency_hz\":" << options.frequency << ",\"amplitude_volts\":" << options.amplitude
           << ",\"warmup_frames\":" << options.warmup_frames << ",\"measurement_frames\":" << options.measurement_frames
           << ",\"completed_frames\":" << model.state().frames << ",\"transfer\":";
    write_ports(output, fit.gain);
    output << ",\"first_half_transfer\":"; write_ports(output, first.gain);
    output << ",\"second_half_transfer\":"; write_ports(output, second.gain);
    output << ",\"fit_error_amplification_bound\":" << fit.error_amplification_bound
           << ",\"first_half_error_amplification_bound\":" << first.error_amplification_bound
           << ",\"second_half_error_amplification_bound\":" << second.error_amplification_bound
           << ",\"half_window_max_difference\":" << half_difference
           << ",\"maximum_port_magnitude\":" << maximum_port_magnitude;
}
} // namespace

int main(int argc, char* argv[]) {
    try {
        if (argc == 2 && std::string_view(argv[1]) == "--help") {
            std::cout << "Independent ideal Leslie crossover observation probe. JSON is emitted only after success.\n"
                         "--operation response|sine --sample-rate 44100|48000|96000|192000\n"
                         "[--treble-ohms 1..1024] [--bass-ohms 1..1024]\n"
                         "response: --frequencies comma-separated-Hz (1..512, 0<=f<Nyquist)\n"
                         "sine: --frequency Hz [--amplitude V] [--warmup-frames N] [--measurement-frames N]\n"
                         "Sine defaults: 0.25 V, 65536 warmup, 8192 measurement; at most16777216 total.\n"
                         "No real-driver, same-Hz audible, acoustic, or Engine qualification is implied.\n";
            return 0;
        }
        const auto options = parse_options(argc, argv);
        LeslieCrossover model;
        require_status(model.prepare(options.sample_rate, options.loads), "prepare");
        std::ostringstream output;
        output.imbue(std::locale::classic());
        output << std::setprecision(std::numeric_limits<double>::max_digits10)
               << "{\"schema_version\":1,\"probe_id\":\"leslie-crossover-public-api-probe-v1\""
                  ",\"model_id\":\"" << hammond::kLeslieCrossoverModelId << "\",\"realization_id\":\""
               << hammond::kLeslieCrossoverRealizationId << "\",\"operation\":\"" << options.operation
               << "\",\"sample_rate_hz\":" << options.sample_rate << ",\"loads\":{\"treble_ohms\":"
               << options.loads.treble_ohms << ",\"bass_ohms\":" << options.loads.bass_ohms
               << "},\"physical_measurement_claim\":false,\"engine_integration\":false,\"preparation_residual\":"
               << model.preparation_residual();
        if (options.operation == "response") response_report(output, options, model);
        else sine_report(output, options, model);
        output << "}\n";
        const auto report = output.str();
        if (report.size() > kMaximumReportBytes) fail("Report exceeds its bounded output capacity.");
        std::cout << report;
        if (!std::cout) fail("Cannot write complete report.");
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "crossover_probe: " << error.what() << '\n';
        return 2;
    }
}
