#include "hammond/ParameterBridge.h"
#include "hammond/detail/Decimal.h"

#include <cstddef>
#include <exception>
#include <iomanip>
#include <iostream>
#include <limits>
#include <locale>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>

#ifdef _WIN32
#include <cstdio>
#include <fcntl.h>
#include <io.h>
#endif

namespace {

constexpr std::size_t kMaxArgumentBytes = 128;
constexpr std::size_t kMaxMetadataBytes = 32 * 1024;

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

[[nodiscard]] std::string_view event_name(hammond::EventType type) {
    switch (type) {
    case hammond::EventType::BankDrawbar: return "bank_drawbar";
    case hammond::EventType::Expression: return "expression";
    case hammond::EventType::SelectBank: return "select_bank";
    case hammond::EventType::Percussion: return "percussion";
    default: throw std::runtime_error("Compiled descriptor has an unsupported event type.");
    }
}

[[nodiscard]] double argument(std::string_view token) {
    double value = 0.0;
    if (token.size() > kMaxArgumentBytes ||
        hammond::detail::parse_decimal(token, value) != hammond::detail::DecimalResult::Ok ||
        value < 0.0 || value > 1.0) {
        throw std::runtime_error("Expected a finite decimal normalized value in [0,1], at most 128 bytes.");
    }
    return value;
}

[[nodiscard]] std::string metadata(double normalized) {
    const hammond::detail::DecimalRounding rounding;
    if (!rounding.ready()) throw std::runtime_error("Cannot select nearest rounding for metadata.");
    std::ostringstream output;
    output.imbue(std::locale::classic());
    output << std::setprecision(std::numeric_limits<double>::max_digits10)
           << "{\"schema_version\":1,\"registry_schema_version\":"
           << hammond::kParameterRegistrySchemaVersion << ",\"model\":";
    quoted(output, hammond::kParameterRegistryModel);
    output << ",\"scope\":\"implemented-console-subset\",\"status\":\"proposed-internal\","
              "\"host_exports_verified\":false,\"native_host_curves_implemented\":false,"
              "\"normalized\":" << normalized << ",\"parameters\":[";
    bool first = true;
    for (const auto& descriptor : hammond::parameter_descriptors()) {
        hammond::Event event;
        double default_normalized = 0.0;
        if (!hammond::normalized_to_event(descriptor.id, normalized, 0, event) ||
            !hammond::plain_to_normalized(descriptor.id, descriptor.default_plain,
                                          default_normalized)) {
            throw std::runtime_error("Compiled parameter metadata cannot be converted.");
        }
        if (!first) output << ',';
        first = false;
        output << "{\"id\":" << descriptor.id << ",\"path\":";
        quoted(output, descriptor.path);
        output << ",\"kind\":";
        quoted(output, descriptor.kind);
        output << ",\"unit\":";
        quoted(output, descriptor.unit);
        output << ",\"minimum\":0,\"maximum\":" << descriptor.maximum
               << ",\"default_plain\":" << descriptor.default_plain
               << ",\"default_normalized\":" << default_normalized
               << ",\"step_count\":" << static_cast<unsigned>(descriptor.step_count)
               << ",\"event\":{\"offset\":" << event.offset << ",\"type\":";
        quoted(output, event_name(event.type));
        output << ",\"manual\":";
        quoted(output, event.manual == hammond::Manual::Upper ? "upper" : "lower");
        output << ",\"index\":" << static_cast<unsigned>(event.index)
               << ",\"value\":" << event.value << "}}";
    }
    output << "]}\n";
    if (!output) throw std::runtime_error("Cannot construct parameter metadata.");
    auto result = output.str();
    if (result.size() >= kMaxMetadataBytes) {
        throw std::runtime_error("Parameter metadata exceeds its supported size limit.");
    }
    return result;
}

} // namespace

int main(int argc, char* argv[]) {
    try {
#ifdef _WIN32
        if (_setmode(_fileno(stdout), _O_BINARY) == -1) {
            throw std::runtime_error("Cannot select binary stdout mode.");
        }
#endif
        if (argc == 2 && std::string_view(argv[1]) == "--help") {
            std::cout << "Usage: hammond_parameter_info [--normalized U | --help]\n"
                         "Emit the 43 compiled internal parameter mappings; U defaults to 0.5.\n"
                         "U must be a finite decimal in [0,1], at most 128 bytes.\n"
                         "Scope: proposed internal mapping; no native host exports or curves are verified.\n";
        } else if (argc == 1) {
            std::cout << metadata(0.5);
        } else if (argc == 3 && std::string_view(argv[1]) == "--normalized") {
            std::cout << metadata(argument(argv[2]));
        } else {
            throw std::runtime_error("Expected no arguments, --normalized U, or --help alone.");
        }
        std::cout.flush();
        if (!std::cout) throw std::runtime_error("Cannot write parameter metadata to stdout.");
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "hammond_parameter_info: " << error.what() << '\n';
        return 1;
    } catch (...) {
        std::cerr << "hammond_parameter_info: unknown failure.\n";
        return 1;
    }
}
