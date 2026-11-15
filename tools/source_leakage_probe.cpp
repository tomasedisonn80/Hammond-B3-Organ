#include "CliArguments.h"
#include "hammond/SourceLeakage.h"

#include <exception>
#include <filesystem>
#include <iomanip>
#include <iostream>
#include <limits>
#include <locale>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <system_error>

#ifdef _WIN32
#include <cstdio>
#include <fcntl.h>
#include <io.h>
#endif

namespace {

constexpr std::size_t kMaxArgumentBytes = 32768;
constexpr std::size_t kMaxReportBytes = 128 * 1024;

[[noreturn]] void fail(const std::string& message) {
    throw std::runtime_error(message);
}

void require_status(hammond::Status status, std::string_view operation) {
    if (status != hammond::Status::Ok) {
        fail(std::string(operation) + ": " + hammond::status_name(status));
    }
}

void quoted(std::ostream& output, std::string_view text) {
    constexpr std::string_view hex = "0123456789abcdef";
    output << '"';
    for (const char character : text) {
        const auto byte = static_cast<unsigned char>(character);
        if (character == '"' || character == '\\') {
            output << '\\' << character;
        } else if (byte < 0x20U || byte >= 0x7fU) {
            output << "\\u00" << hex[byte >> 4U] << hex[byte & 0x0fU];
        } else {
            output << character;
        }
    }
    output << '"';
}

void frame(std::ostream& output, const hammond::SourceLeakageFrame& values) {
    output << '[';
    for (std::size_t index = 0; index < values.size(); ++index) {
        if (index != 0) output << ',';
        output << values[index];
    }
    output << ']';
}

[[nodiscard]] std::filesystem::path input_path(int argc, char* argv[]) {
    if (argc != 3 || std::string_view(argv[1]) != "--input") {
        fail("Expected --input FILE exactly once, or --help alone.");
    }
    const std::string_view value(argv[2]);
    if (value.empty() || value.size() > kMaxArgumentBytes) {
        fail("Input path requires 1..32768 bytes.");
    }
    const auto path = hammond::cli::argument_path(value);
    std::error_code error;
    const auto resolved = std::filesystem::canonical(path, error);
    if (error || !std::filesystem::is_regular_file(resolved, error) || error) {
        fail("Input must name a readable regular file: " + hammond::cli::path_text(path));
    }
    const auto bytes = std::filesystem::file_size(resolved, error);
    if (error || bytes > hammond::kMaxCompiledSourceLeakageBytes) {
        fail("Input is unreadable or exceeds 128 KiB.");
    }
    return resolved;
}

[[nodiscard]] std::string report(const std::filesystem::path& path) {
    hammond::SourceLeakageProfile profile;
    std::string error;
    if (!hammond::load_source_leakage_profile_file(path, profile, error)) {
        fail("Cannot load source leakage: " + error);
    }
    hammond::SourceLeakage leakage;
    require_status(leakage.prepare({profile.edges.data(), profile.edge_count}), "prepare");

    // Fixed published fixture, independent of the graph: dyadic inputs in
    // [-1,1], containing positive, negative and zero values. This is one
    // algebra observation, not a spectrum, timing or physical acceptance.
    hammond::SourceLeakageFrame input{};
    for (std::size_t index = 0; index < input.size(); ++index) {
        const auto numerator = static_cast<int>(((index + 1) * 37) % 129) - 64;
        input[index] = static_cast<double>(numerator) / 64.0;
    }
    hammond::SourceLeakageFrame output{};
    require_status(leakage.process_frame(input, output), "process_frame");

    std::ostringstream json;
    json.imbue(std::locale::classic());
    json << std::setprecision(std::numeric_limits<double>::max_digits10)
         << "{\"schema_version\":1,\"probe_id\":\"source-leakage-profile-probe-v1\","
            "\"status\":\"ok\",\"model\":";
    quoted(json, hammond::kSourceLeakageModel);
    json << ",\"profile_id\":";
    quoted(json, profile.profile_id.data());
    json << ",\"evidence_status\":";
    quoted(json, hammond::kSourceLeakageEvidenceStatus);
    json << ",\"boundary\":";
    quoted(json, hammond::kSourceLeakageBoundary);
    json << ",\"source_content\":";
    quoted(json, hammond::kSourceLeakageSourceContent);
    json << ",\"authoring_sha256\":";
    quoted(json, profile.authoring_sha256.data());
    json << ",\"authoring_digest_verification\":\"file-supplied-unverified\","
            "\"source_count\":" << hammond::kToneSourceCount
         << ",\"edge_count\":" << leakage.edge_count()
         << ",\"maximum_row_absolute_gain_sum\":" << leakage.max_row_absolute_gain_sum()
         << ",\"edges\":[";
    for (std::size_t index = 0; index < profile.edge_count; ++index) {
        if (index != 0) json << ',';
        const auto& edge = profile.edges[index];
        json << "{\"destination\":" << static_cast<unsigned>(edge.destination)
             << ",\"source\":" << static_cast<unsigned>(edge.source)
             << ",\"gain\":" << edge.gain << '}';
    }
    json << "],\"rows\":[";
    for (std::size_t index = 0; index < hammond::kToneSourceCount; ++index) {
        if (index != 0) json << ',';
        const auto destination = static_cast<hammond::ToneId>(index + 1);
        double sum = 0.0;
        if (!leakage.row_absolute_gain_sum(destination, sum)) fail("Prepared row query failed.");
        json << "{\"destination\":" << index + 1 << ",\"absolute_gain_sum\":" << sum << '}';
    }
    json << "],\"frame_id\":\"dyadic-permuted-ramp-v1\","
            "\"frame_definition\":\"x[i]=(((37*i)%129)-64)/64; tone IDs i=1..91\","
            "\"input_frame\":";
    frame(json, input);
    json << ",\"output_frame\":";
    frame(json, output);
    json << "}\n";
    if (!json) fail("Cannot assemble source-leakage report.");
    auto bytes = json.str();
    if (bytes.size() > kMaxReportBytes) fail("Source-leakage report exceeds 128 KiB.");
    return bytes;
}

} // namespace

static int source_leakage_probe_main(int argc, char* argv[]) {
    try {
#ifdef _WIN32
        if (_setmode(_fileno(stdout), _O_BINARY) == -1) {
            fail("Cannot select binary stdout mode.");
        }
#endif
        if (argc == 2 && std::string_view(argv[1]) == "--help") {
            std::cout << "Usage: hammond_source_leakage_probe --input FILE\n"
                         "       hammond_source_leakage_probe --help\n"
                         "Load a regular compiled B3LEAKAGE1 file of at most 128 KiB.\n"
                         "Emit schema-1 JSON: canonical edges, stored row sums and one fixed frame.\n"
                         "Frame: x[i]=(((37*i)%129)-64)/64, for tone IDs i=1..91.\n"
                         "The authoring digest is file-supplied and unverified; no author bytes are read.\n"
                         "Synthetic engineering inspection only; no measured-leakage claim.\n";
        } else {
            // Validate and assemble everything before emitting any JSON bytes.
            std::cout << report(input_path(argc, argv));
        }
        std::cout.flush();
        if (!std::cout) fail("Cannot write source-leakage report to stdout.");
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "hammond_source_leakage_probe: " << error.what() << '\n';
        return 1;
    } catch (...) {
        std::cerr << "hammond_source_leakage_probe: unknown failure.\n";
        return 1;
    }
}

#ifdef _WIN32
int wmain(int argc, wchar_t* argv[]) {
    return hammond::cli::run_windows(argc, argv, source_leakage_probe_main,
        "hammond_source_leakage_probe", {3, kMaxArgumentBytes});
}
#else
int main(int argc, char* argv[]) {
    return source_leakage_probe_main(argc, argv);
}
#endif
