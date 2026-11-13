#include "hammond/ConsoleModel.h"

#include <array>
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

constexpr std::size_t kMaxMetadataBytes = 128 * 1024;
constexpr std::array<std::string_view, hammond::kManualCount> kManualNames{
    "upper", "lower"};
static_assert(hammond::kManualCount == 2);

// Every string emitted here is a fixed ASCII contract string or a model ID
// supplied by the compiled core. Escape even those IDs rather than relying on
// their present spelling remaining JSON-safe forever.
void quoted(std::ostream& output, std::string_view value) {
    constexpr std::string_view hex = "0123456789abcdef";
    output << '"';
    for (const char character : value) {
        const auto byte = static_cast<unsigned char>(character);
        if (byte == static_cast<unsigned char>('"') ||
            byte == static_cast<unsigned char>('\\')) {
            output << '\\' << character;
        } else if (byte < 0x20U || byte >= 0x7fU) {
            output << "\\u00" << hex[byte >> 4U] << hex[byte & 0x0fU];
        } else {
            output << character;
        }
    }
    output << '"';
}

template <std::size_t Size>
void numbers(std::ostream& output, const std::array<double, Size>& values) {
    output << '[';
    for (std::size_t index = 0; index < values.size(); ++index) {
        if (index != 0) output << ',';
        output << values[index];
    }
    output << ']';
}

void contact_metadata(std::ostream& output, const hammond::ContactProfile& contacts) {
    output << "{\"algorithm_id\":";
    quoted(output, hammond::contact_model_id(contacts.mode));
    output << ",\"mode\":";
    quoted(output, contacts.mode == hammond::ContactMode::Ideal ? "ideal" : "linear_travel");
    output << ",\"evidence_class\":\"proposed\",\"atlas_pages\":[37,39,40,115,116,117,118,119,120],"
              "\"uncertainty\":null,\"missing_evidence\":\"No specimen contact captures; repeated key defaults are synthetic.\","
              "\"units\":{\"on_thresholds\":\"normalized_key_travel\","
              "\"off_thresholds\":\"normalized_key_travel\",\"press_seconds\":\"s\","
              "\"release_seconds\":\"s\"},\"manuals\":[";
    for (std::size_t manual = 0; manual < contacts.keys.size(); ++manual) {
        if (manual != 0) output << ',';
        output << "{\"manual\":";
        quoted(output, kManualNames[manual]);
        output << ",\"keys\":[";
        for (std::size_t index = 0; index < contacts.keys[manual].size(); ++index) {
            if (index != 0) output << ',';
            const auto& key = contacts.keys[manual][index];
            output << "{\"midi_note\":"
                   << static_cast<unsigned>(hammond::kMinManualMidiNote) + index
                   << ",\"press_seconds\":" << key.press_seconds
                   << ",\"release_seconds\":" << key.release_seconds
                   << ",\"on_thresholds\":";
            numbers(output, key.on_thresholds);
            output << ",\"off_thresholds\":";
            numbers(output, key.off_thresholds);
            output << '}';
        }
        output << "]}";
    }
    output << "]}";
}

void parameter(std::ostream& output, std::string_view name, double value,
               std::string_view unit, std::string_view evidence, std::string_view pages) {
    quoted(output, name);
    output << ":{\"value\":" << value << ",\"unit\":";
    quoted(output, unit);
    output << ",\"evidence_class\":";
    quoted(output, evidence);
    output << ",\"atlas_pages\":" << pages << '}';
}

void percussion_metadata(std::ostream& output, const hammond::PercussionProfile& profile,
                         const hammond::PercussionSettings& settings) {
    output << "{\"algorithm_id\":";
    quoted(output, hammond::kPercussionModelId);
    output << ",\"readiness_unit\":\"dimensionless\",\"gain_map\":\"F(q)=q\","
              "\"uncertainty\":null,\"missing_evidence\":"
              "\"No calibrated specimen envelope or complete AO-28 transfer; RC products are hypotheses, not audible decay lengths.\","
              "\"parameters\":{";
    parameter(output, "slow_decay_seconds", profile.slow_decay_seconds, "s", "derived", "[133,135]");
    output << ',';
    parameter(output, "fast_decay_seconds", profile.fast_decay_seconds, "s", "derived", "[133,135]");
    output << ',';
    parameter(output, "recovery_seconds", profile.recovery_seconds, "s", "derived", "[133,135]");
    output << ',';
    parameter(output, "normal_gain", profile.normal_gain, "normalized_amplitude", "proposed", "[134,135]");
    output << ',';
    parameter(output, "soft_gain", profile.soft_gain, "normalized_amplitude", "proposed", "[134,135]");
    output << ',';
    parameter(output, "fast_gain_multiplier", profile.fast_gain_multiplier, "dimensionless", "proposed", "[134,135]");
    output << ',';
    parameter(output, "normal_sustain_gain", profile.normal_sustain_gain, "dimensionless", "proposed", "[134]");
    output << "},\"default_settings\":{\"enabled\":" << settings.enabled
           << ",\"harmonic\":";
    quoted(output, settings.harmonic == hammond::PercussionHarmonic::Second ? "second" : "third");
    output << ",\"volume\":";
    quoted(output, settings.volume == hammond::PercussionVolume::Normal ? "normal" : "soft");
    output << ",\"decay\":";
    quoted(output, settings.decay == hammond::PercussionDecay::Slow ? "slow" : "fast");
    output << "}}";
}

void console_metadata(std::ostream& output, std::string_view choice,
                      std::string_view factory, const hammond::ConsoleModel& model,
                      const hammond::PercussionSettings& settings) {
    output << "{\"choice\":";
    quoted(output, choice);
    output << ",\"factory\":";
    quoted(output, factory);
    output << ",\"contacts\":";
    contact_metadata(output, model.contacts);
    output << ",\"percussion\":";
    percussion_metadata(output, model.percussion, settings);
    output << '}';
}

[[nodiscard]] std::string metadata() {
    const auto legacy = hammond::make_legacy_console_model();
    const auto nominal = hammond::make_nominal_console_model();
    const hammond::PercussionSettings settings;
    for (const double rate : {44100.0, 48000.0, 96000.0}) {
        if (hammond::validate_console_model(legacy, rate) != hammond::Status::Ok ||
            hammond::validate_console_model(nominal, rate) != hammond::Status::Ok) {
            throw std::runtime_error("Compiled console factory parameters are invalid.");
        }
    }
    if (!hammond::is_valid_percussion_settings(settings)) {
        throw std::runtime_error("Compiled default percussion settings are invalid.");
    }

    std::ostringstream output;
    output.imbue(std::locale::classic());
    output << std::setprecision(std::numeric_limits<double>::max_digits10) << std::boolalpha
           << "{\"schema_version\":1,\"evidence_scope\":\"synthetic_engineering\","
              "\"physical_fidelity\":\"unestablished\",\"source_generator\":{"
              "\"included\":false,\"profile_type\":\"RuntimeProfile\",\"source_count\":"
           << hammond::kToneSourceCount
           << ",\"reason\":\"Source tuning, amplitudes, phases and routing are independent profile inputs.\"},"
              "\"console_models\":[";
    console_metadata(output, "legacy", "make_legacy_console_model", legacy, settings);
    output << ',';
    console_metadata(output, "nominal", "make_nominal_console_model", nominal, settings);
    output << "]}\n";
    if (!output) throw std::runtime_error("Cannot construct model metadata.");
    auto result = output.str();
    if (result.size() >= kMaxMetadataBytes) {
        throw std::runtime_error("Model metadata exceeds its supported size limit.");
    }
    return result;
}

} // namespace

int main(int argc, char* argv[]) {
    try {
#ifdef _WIN32
        // Metadata identity includes its bytes. Disable CRT LF translation;
        // this does not change error reporting or any engine/audio behavior.
        if (_setmode(_fileno(stdout), _O_BINARY) == -1) {
            throw std::runtime_error("Cannot select binary stdout mode.");
        }
#endif
        if (argc == 2 && std::string_view(argv[1]) == "--help") {
            std::cout << "Usage: hammond_model_info [--help]\n"
                         "Without arguments, emit JSON for the compiled console factory defaults.\n"
                         "Scope: synthetic engineering metadata; source profiles and measured fidelity are separate.\n";
        } else if (argc == 1) {
            std::cout << metadata();
        } else {
            throw std::runtime_error("Expected no arguments or --help.");
        }
        std::cout.flush();
        if (!std::cout) throw std::runtime_error("Cannot write metadata to stdout.");
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "hammond_model_info: " << error.what() << '\n';
        return 1;
    } catch (...) {
        std::cerr << "hammond_model_info: unknown failure.\n";
        return 1;
    }
}
