// Compile the real app entry and lifecycle unchanged in this test translation
// unit. Only entry-point names and the separately compiled RtMidi dependency
// differ from the ordinary standalone target; no Application internals are used.
#define main hammond_calibration_original_main
#define wmain hammond_calibration_original_wmain
#include "../main.cpp"
#undef wmain
#undef main

#include <RtMidi.h>

namespace {
namespace fixture = hammond_calibration_fixture;

bool select_scenario(std::string_view name, fixture::Scenario& result) {
    constexpr std::array<std::pair<std::string_view, fixture::Scenario>, 7> choices{{
        {"identical", fixture::Scenario::Identical},
        {"calibration", fixture::Scenario::Calibration},
        {"route", fixture::Scenario::Route},
        {"port", fixture::Scenario::Port},
        {"no-input", fixture::Scenario::NoInput},
        {"failed-reopen", fixture::Scenario::FailedReopen},
        {"fault-retry", fixture::Scenario::FaultRetry}}};
    for (const auto& [candidate, value] : choices) {
        if (candidate == name) { result = value; return true; }
    }
    return false;
}

bool write_trace(const char* path, std::string_view scenario, const fixture::State& state,
                 int application_exit) {
    // All native clients and the discovery thread have been destroyed/joined by
    // the returned real guarded_application; this final log cannot race them.
    std::ofstream output(hammond::cli::argument_path(path), std::ios::binary | std::ios::trunc);
    output.imbue(std::locale::classic());
    output << std::boolalpha << "{\"schema_version\":1,\"fixture_id\":\"native-calibration-dependency-v1\","
           << "\"scenario\":\"" << scenario << "\",\"application_exit\":" << application_exit
           << ",\"production_lifecycle\":true,\"physical_backend\":false,\"callback_schedule\":\"synchronous-native-api-boundaries\","
           << "\"counts\":{\"constructions\":" << state.constructions
           << ",\"destructions\":" << state.destructions << ",\"opens\":" << state.opens
           << ",\"closes\":" << state.closes << ",\"cancellations\":" << state.cancellations
           << ",\"offered_messages\":" << state.offered_messages
           << ",\"delivered_messages\":" << state.delivered_messages
           << ",\"errors\":" << state.errors << ",\"cancelled_while_open\":" << state.cancelled_while_open
           << ",\"destroyed_while_open\":" << state.destroyed_while_open
           << ",\"destroyed_with_input_callback\":" << state.destroyed_with_input_callback
           << ",\"invalid_callbacks\":" << state.invalid_callbacks
           << ",\"dropped_events\":" << state.dropped_events << "},\"events\":[";
    for (std::size_t index = 0; index < state.event_count; ++index) {
        if (index != 0) output << ',';
        const auto& event = state.events[index];
        output << "{\"sequence\":" << index + 1 << ",\"operation\":\""
               << fixture::operation_names[static_cast<std::size_t>(event.operation)] << "\",\"client\":" << event.client
               << ",\"transport\":" << event.transport << ",\"open_attempt\":" << event.open_attempt
               << ",\"poll\":" << event.poll << ",\"port\":" << event.port
               << ",\"registered\":" << event.registered << ",\"worker\":" << event.worker << ",\"bytes\":["
               << event.bytes[0] << ',' << event.bytes[1] << ',' << event.bytes[2] << "]}";
    }
    output << "]}\n";
    output.flush();
    return output.good();
}

int fixture_application(int argc, char** argv) {
    // SDL's Windows getenv may reuse one buffer, and application startup also
    // reads the environment. Own each value before another read can replace it.
    const auto copy_environment = [](const char* name) {
        const char* value = SDL_getenv(name);
        return value == nullptr ? std::string{} : std::string{value};
    };
    const std::string selected = copy_environment("HAMMOND_CALIBRATION_SCENARIO");
    const std::string trace = copy_environment("HAMMOND_CALIBRATION_TRACE");
    fixture::Scenario scenario{};
    if (selected.empty() || trace.empty() || !select_scenario(selected, scenario)) {
        std::cerr << "calibration fixture requires a declared scenario and trace destination\n";
        return 2;
    }
    const auto state = fixture::install(scenario);
    const int result = hammond::standalone::guarded_application(argc, argv);
    const bool written = write_trace(trace.c_str(), selected, *state, result);
    fixture::installed.reset();
    if (!written) {
        std::cerr << "calibration fixture could not write its native dependency trace\n";
        return 3;
    }
    return result;
}
} // namespace

#ifdef _WIN32
int wmain(int argc, wchar_t* argv[]) {
    return hammond::cli::run_windows(argc, argv, &fixture_application,
                                    "hammond_standalone_calibration_probe");
}
#else
int main(int argc, char** argv) {
    return fixture_application(argc, argv);
}
#endif
