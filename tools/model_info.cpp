#include "CliArguments.h"
#include "hammond/ConsoleModel.h"
#include "hammond/ControlState.h"
#include "hammond/PedalRouting.h"
#include "hammond/PedalVoice.h"

#include <array>
#include <cmath>
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
constexpr std::array<std::string_view, hammond::kPedalBusCount> kPedalBusNames{
    "Brown", "Red", "Orange", "Yellow"};
static_assert(hammond::kPedalBusCount == 4);

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

void pedal_metadata(std::ostream& output) {
    const auto& routes = hammond::compiled_pedal_routes();
    const auto identity = hammond::compiled_pedal_identity();
    const auto weights = hammond::nominal_pedal_reference_weights();
    const hammond::ControlState controls;
    const auto defaults = controls.pedal_drawbar_positions();
    hammond::PedalBusKernel prepared;
    if (prepared.prepare(routes, weights) != hammond::Status::Ok ||
        !hammond::is_valid_pedal_drawbar_positions(defaults)) {
        throw std::runtime_error("Compiled pedal factory parameters are invalid.");
    }
    for (const auto& row : hammond::kNominalPedalMixtureMatrix) {
        for (const double value : row) {
            if (!std::isfinite(value)) {
                throw std::runtime_error("Compiled pedal mixture contains a nonfinite value.");
            }
        }
    }
    for (const double value : hammond::kNominalPedalPositionGains) {
        if (!std::isfinite(value)) {
            throw std::runtime_error("Compiled pedal gains contain a nonfinite value.");
        }
    }
    for (const double limit : {hammond::kNominalPedalBusInputLimit,
                               hammond::kNominalPedalMixtureOutputLimit,
                               hammond::kNominalPedalOutputLimit}) {
        if (!std::isfinite(limit) || limit < 0.0) {
            throw std::runtime_error("Compiled pedal limits are invalid.");
        }
    }

    std::size_t connected = 0;
    std::size_t repeated_pairs = 0;
    std::array<std::size_t, hammond::kPedalBusCount> connected_per_bus{};
    for (std::size_t index = 0; index < routes.size(); ++index) {
        const auto& route = routes[index];
        if (!route.tone) continue;
        ++connected;
        ++connected_per_bus[static_cast<std::size_t>(route.bus)];
        for (std::size_t other = index + 1; other < routes.size(); ++other) {
            if (routes[other].pedal != route.pedal) break;
            if (routes[other].tone == route.tone) ++repeated_pairs;
        }
    }

    output << "{\"runtime_state_included\":false,\"evidence_class\":\"proposed\","
              "\"atlas_pages\":[139,140,142,144,447],\"uncertainty\":null,"
              "\"missing_evidence\":\"No specimen pedal contact, reactor/loading or calibrated mixture transfer measurements; the fixed voice is an original engineering fixture.\","
              "\"routing\":{\"model_id\":";
    quoted(output, identity.model_id);
    output << ",\"map_id\":";
    quoted(output, identity.map_id);
    output << ",\"map_raw_sha256\":";
    quoted(output, identity.map_raw_sha256);
    output << ",\"map_canonical_sha256\":";
    quoted(output, identity.map_canonical_sha256);
    output << ",\"factory_comparison_id\":";
    quoted(output, identity.factory_comparison_id);
    output << ",\"factory_comparison_raw_sha256\":";
    quoted(output, identity.factory_comparison_raw_sha256);
    output << ",\"review_a_sha256\":";
    quoted(output, identity.review_a_sha256);
    output << ",\"review_b_sha256\":";
    quoted(output, identity.review_b_sha256);
    output << ",\"evidence_class\":\"documented\",\"pedal_count\":"
           << hammond::kPedalCount << ",\"contacts_per_pedal\":"
           << hammond::kPedalContactCount << ",\"position_count\":" << routes.size()
           << ",\"bus_count\":" << hammond::kPedalBusCount
           << ",\"connected_count\":" << connected
           << ",\"disconnected_count\":" << routes.size() - connected
           << ",\"repeated_source_pairs\":" << repeated_pairs
           << ",\"bus_order\":[";
    for (std::size_t bus = 0; bus < kPedalBusNames.size(); ++bus) {
        if (bus != 0) output << ',';
        quoted(output, kPedalBusNames[bus]);
    }
    output << "],\"connected_per_bus\":[";
    for (std::size_t bus = 0; bus < connected_per_bus.size(); ++bus) {
        if (bus != 0) output << ',';
        output << connected_per_bus[bus];
    }
    output << "],\"disconnections\":[";
    bool first = true;
    for (const auto& route : routes) {
        if (route.tone) continue;
        if (!first) output << ',';
        first = false;
        output << "{\"pedal_id\":" << static_cast<unsigned>(route.pedal.value)
               << ",\"contact_index\":" << static_cast<unsigned>(route.contact)
               << ",\"bus\":";
        quoted(output, kPedalBusNames[static_cast<std::size_t>(route.bus)]);
        output << ",\"source_tone_id\":null}";
    }
    output << "]},\"contacts\":{\"policy\":\"ideal_simultaneous\","
              "\"canonical_event_manual\":\"lower\",\"null_contact_state_retained\":true,"
              "\"velocity_scales_output\":false,\"source_clock_owned\":false,"
              "\"prepared_closed_contact_count\":" << prepared.closed_contact_count()
           << "},\"weights\":{\"factory\":\"nominal_pedal_reference_weights\","
              "\"unit\":\"dimensionless\",\"position_order\":\"pedal_id_then_contact_index\","
              "\"values\":";
    numbers(output, weights);
    output << "},\"voice\":{\"model_id\":";
    quoted(output, hammond::kNominalPedalVoiceModelId);
    output << ",\"gain_law_id\":";
    quoted(output, hammond::kNominalPedalGainLawId);
    output << ",\"mixture_labels\":[";
    for (std::size_t mixture = 0; mixture < hammond::kNominalPedalMixtureLabels.size(); ++mixture) {
        if (mixture != 0) output << ',';
        quoted(output, hammond::kNominalPedalMixtureLabels[mixture]);
    }
    output << "],\"matrix\":[";
    for (std::size_t mixture = 0; mixture < hammond::kNominalPedalMixtureMatrix.size(); ++mixture) {
        if (mixture != 0) output << ',';
        numbers(output, hammond::kNominalPedalMixtureMatrix[mixture]);
    }
    output << "],\"position_gains\":";
    numbers(output, hammond::kNominalPedalPositionGains);
    output << ",\"default_positions\":[";
    for (std::size_t mixture = 0; mixture < defaults.size(); ++mixture) {
        if (mixture != 0) output << ',';
        output << static_cast<unsigned>(defaults[mixture]);
    }
    output << "],\"units\":{\"matrix\":\"dimensionless\",\"position_gains\":\"dimensionless\","
              "\"default_positions\":\"drawbar_position\",\"bus_input\":\"source_normalized_dimensionless\","
              "\"mixture_output\":\"source_normalized_dimensionless\",\"combined_output\":\"source_normalized_dimensionless\"},"
              "\"absolute_limits\":{\"bus_input\":" << hammond::kNominalPedalBusInputLimit
           << ",\"mixture_output\":" << hammond::kNominalPedalMixtureOutputLimit
           << ",\"combined_output\":" << hammond::kNominalPedalOutputLimit << "}}}";
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
           << "{\"schema_version\":2,\"evidence_scope\":\"synthetic_engineering\","
              "\"physical_fidelity\":\"unestablished\",\"source_generator\":{"
              "\"included\":false,\"profile_type\":\"RuntimeProfile\",\"source_count\":"
           << hammond::kToneSourceCount
           << ",\"reason\":\"Source tuning, amplitudes, phases and routing are independent profile inputs.\"},"
              "\"console_models\":[";
    console_metadata(output, "legacy", "make_legacy_console_model", legacy, settings);
    output << ',';
    console_metadata(output, "nominal", "make_nominal_console_model", nominal, settings);
    output << "],\"pedal_model\":";
    pedal_metadata(output);
    output << "}\n";
    if (!output) throw std::runtime_error("Cannot construct model metadata.");
    auto result = output.str();
    if (result.size() >= kMaxMetadataBytes) {
        throw std::runtime_error("Model metadata exceeds its supported size limit.");
    }
    return result;
}

} // namespace

static int model_info_main(int argc, char* argv[]) {
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
                         "Without arguments, emit JSON for the compiled console and pedal factory defaults.\n"
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

#ifdef _WIN32
int wmain(int argc, wchar_t* argv[]) {
    return hammond::cli::run_windows(argc, argv, model_info_main, "hammond_model_info");
}
#else
int main(int argc, char* argv[]) {
    return model_info_main(argc, argv);
}
#endif
