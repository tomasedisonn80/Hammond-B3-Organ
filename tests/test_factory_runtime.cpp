#include "TestSupport.h"
#include "hammond/Engine.h"
#include "hammond/TonewheelBank.h"

#include <algorithm>
#include <array>
#include <charconv>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <limits>
#include <span>
#include <string>
#include <string_view>
#include <system_error>
#include <vector>

namespace {
using hammond::Engine;
using hammond::Event;
using hammond::EventType;
using hammond::Manual;
using hammond::RuntimeProfile;
using hammond::Status;
using hammond::ToneId;
using SourceFrame = std::array<double, hammond::kToneSourceCount>;
using CsvRoutes = std::array<std::array<ToneId, 9>, 61>;

static_assert(hammond::kManualCount == 2 && hammond::kManualKeyCount == 61 &&
              hammond::kDrawbarCount == 9 && hammond::kToneSourceCount == 91);
constexpr std::uint32_t kFrames = 128;
constexpr std::uint32_t kSilentLead = 17;
constexpr std::uint64_t kSeed = 0x0123456789abcdefULL;
constexpr std::array<Manual, 2> kManuals{Manual::Upper, Manual::Lower};

struct Branch {
    Manual manual;
    std::size_t key;     // One-based factory playing key, distinct from MIDI.
    std::size_t drawbar; // One-based factory column d1..d9.
    std::uint8_t position;
};

struct ExpectedAudio {
    std::array<double, kFrames> samples{};
    double tolerance{0.0};
};

struct Comparison {
    std::size_t mismatches{0};
    double peak_error{0.0};
};

struct Counts {
    std::size_t full_routes{0};
    std::size_t other_rate_routes{0};
    std::size_t coherent_cases{0};
    std::size_t transition_stages{0};
    std::size_t probes{0};
    std::size_t matched_frames{0};
    std::size_t probe_frames{0};
    std::size_t silent_frames{0};
    double peak_error{0.0};
};

CsvRoutes read_csv(std::string_view relative_path) {
    std::ifstream input(hammond_test::source_path(relative_path));
    CHECK(input.is_open());
    std::string line;
    const auto read_line = [&]() {
        CHECK(static_cast<bool>(std::getline(input, line)));
        CHECK(line.size() <= 128);
        if (!line.empty() && line.back() == '\r') line.pop_back();
    };
    read_line();
    CHECK(line == "key,d1,d2,d3,d4,d5,d6,d7,d8,d9");
    CsvRoutes routes{};
    for (std::size_t key = 0; key < routes.size(); ++key) {
        read_line();
        std::string_view remaining(line);
        for (std::size_t field = 0; field <= routes[key].size(); ++field) {
            const auto comma = remaining.find(',');
            CHECK((field == routes[key].size()) == (comma == std::string_view::npos));
            const auto token = remaining.substr(0, comma);
            unsigned int value = 0;
            const auto parsed = std::from_chars(token.data(), token.data() + token.size(), value);
            CHECK(parsed.ec == std::errc{} && parsed.ptr == token.data() + token.size());
            if (field == 0) {
                CHECK(value == key + 1);
            } else {
                CHECK(value >= 13 && value <= 91);
                routes[key][field - 1] = static_cast<ToneId>(value);
            }
            if (comma != std::string_view::npos) remaining.remove_prefix(comma + 1);
        }
    }
    CHECK(!std::getline(input, line));
    CHECK(input.eof());
    return routes;
}

std::size_t source_index(const CsvRoutes& routes, const Branch& branch) {
    CHECK(branch.key >= 1 && branch.key <= 61);
    CHECK(branch.drawbar >= 1 && branch.drawbar <= 9);
    CHECK(branch.position <= 8);
    // The CSV is the only routing oracle. No profile map or foldback formula.
    return static_cast<std::size_t>(routes[branch.key - 1][branch.drawbar - 1]) - 1;
}

std::vector<SourceFrame> source_timeline(const RuntimeProfile& profile, double rate,
                                         std::size_t frames) {
    hammond::TonewheelBank bank;
    CHECK(bank.prepare(profile, rate, kSeed) == Status::Ok);
    std::vector<SourceFrame> timeline(frames);
    for (auto& frame : timeline) bank.process_frame(frame);
    return timeline;
}

ExpectedAudio expected_audio(const RuntimeProfile& profile, const CsvRoutes& routes,
                             std::span<const SourceFrame> timeline, std::size_t start,
                             std::span<const Branch> branches,
                             std::array<bool, 2> enabled = {true, true}) {
    CHECK(start + kFrames <= timeline.size());
    ExpectedAudio expected;
    double peak_bound = 0.0;
    for (const auto& branch : branches) {
        if (!enabled[static_cast<std::size_t>(branch.manual)]) continue;
        const auto tone = source_index(routes, branch);
        const double gain = profile.drawbar_gains[branch.position];
        peak_bound += gain * profile.sources[tone].peak_amplitude;
        // Sum individual CSV-selected branches directly. Keep duplicate routes.
        for (std::size_t frame = 0; frame < kFrames; ++frame)
            expected.samples[frame] += gain * timeline[start + frame][tone];
    }
    for (double& sample : expected.samples) sample *= profile.output_gain;
    peak_bound *= profile.output_gain;
    // Binary32 output rounding plus a small binary64 branch-order allowance.
    // This does not depend on long double being wider than double on MSVC.
    expected.tolerance = peak_bound * (2.0 * std::numeric_limits<float>::epsilon() +
                                      32.0 * std::numeric_limits<double>::epsilon());
    return expected;
}

Comparison compare_audio(std::span<const float> actual, const ExpectedAudio& expected) {
    CHECK(actual.size() == expected.samples.size());
    Comparison result;
    for (std::size_t frame = 0; frame < actual.size(); ++frame) {
        CHECK(std::isfinite(actual[frame]) && std::isfinite(expected.samples[frame]));
        const double error = std::abs(static_cast<double>(actual[frame]) - expected.samples[frame]);
        result.peak_error = std::max(result.peak_error, error);
        if (error > expected.tolerance) ++result.mismatches;
    }
    return result;
}

void require_match(std::span<const float> actual, const ExpectedAudio& expected,
                   std::string_view label, Counts& counts) {
    const auto comparison = compare_audio(actual, expected);
    if (comparison.mismatches != 0) {
        for (std::size_t frame = 0; frame < actual.size(); ++frame) {
            if (std::abs(static_cast<double>(actual[frame]) - expected.samples[frame]) >
                expected.tolerance) {
                std::cerr << label << ", frame " << frame << '\n';
                CHECK_NEAR(actual[frame], expected.samples[frame], expected.tolerance);
            }
        }
    }
    counts.peak_error = std::max(counts.peak_error, comparison.peak_error);
    counts.matched_frames += actual.size();
}

void process_ok(Engine& engine, std::span<float> output, std::span<const Event> events = {}) {
    const auto result = engine.process(static_cast<std::uint32_t>(output.size()), output, events);
    CHECK(result.status == Status::Ok);
    CHECK(result.events_consumed == events.size());
}

Engine prepared_engine(const RuntimeProfile& profile, double rate, Counts& counts) {
    Engine engine;
    CHECK(engine.prepare(profile, {rate, kFrames, kSeed, 0}) == Status::Ok);
    std::array<float, kSilentLead> silence{};
    process_ok(engine, silence);
    for (const float sample : silence) CHECK(sample == 0.0F);
    counts.silent_frames += silence.size();
    return engine;
}

std::vector<Event> registration_events(std::span<const Branch> branches) {
    std::vector<Event> events;
    std::array<std::array<bool, 61>, 2> keys{};
    std::array<std::array<std::uint8_t, 9>, 2> positions{};
    for (const auto& branch : branches) {
        const auto manual = static_cast<std::size_t>(branch.manual);
        const auto key = branch.key - 1;
        const auto bar = branch.drawbar - 1;
        CHECK(branch.position != 0);
        if (positions[manual][bar] == 0) {
            positions[manual][bar] = branch.position;
            events.push_back({0, EventType::Drawbar, branch.manual,
                              static_cast<std::uint8_t>(bar), static_cast<double>(branch.position)});
        } else {
            CHECK(positions[manual][bar] == branch.position);
        }
        if (!keys[manual][key]) {
            keys[manual][key] = true;
            events.push_back({0, EventType::NoteOn, branch.manual,
                              static_cast<std::uint8_t>(hammond::kMinManualMidiNote + key), 100.0});
        }
    }
    return events;
}

std::array<float, kFrames> render_case(const RuntimeProfile& profile, double rate,
                                      std::span<const Branch> branches, Counts& counts) {
    auto engine = prepared_engine(profile, rate, counts);
    const auto events = registration_events(branches);
    std::array<float, kFrames> output{};
    process_ok(engine, output, events);
    CHECK(engine.frame_clock() == kSilentLead + kFrames);
    return output;
}

void check_case(const RuntimeProfile& profile, const CsvRoutes& routes,
                std::span<const SourceFrame> timeline, double rate,
                std::span<const Branch> branches, std::string_view label, Counts& counts) {
    const auto expected = expected_audio(profile, routes, timeline, kSilentLead, branches);
    CHECK(expected.tolerance > 0.0);
    CHECK(std::any_of(expected.samples.begin(), expected.samples.end(),
                      [](double sample) { return std::abs(sample) > 1e-3; }));
    require_match(render_case(profile, rate, branches, counts), expected, label, counts);
}

void check_one_hot(const RuntimeProfile& profile, const CsvRoutes& routes,
                   std::span<const SourceFrame> timeline, double rate,
                   Manual manual, std::size_t key, std::size_t bar, Counts& counts) {
    const std::array branches{Branch{manual, key, bar, 8}};
    const std::string label = (manual == Manual::Upper ? "upper" : "lower") +
        std::string(" key=") + std::to_string(key) + " d" + std::to_string(bar) +
        " CSV-tone=" + std::to_string(routes[key - 1][bar - 1]) +
        " rate=" + std::to_string(rate);
    check_case(profile, routes, timeline, rate, branches, label, counts);
}

void coherent_cases(const RuntimeProfile& profile, const CsvRoutes& routes,
                    std::span<const SourceFrame> timeline, Counts& counts) {
    for (const auto manual : kManuals) {
        const std::array low{Branch{manual, 1, 1, 8}, Branch{manual, 1, 3, 8}};
        const std::array overlap{Branch{manual, 1, 1, 8}, Branch{manual, 13, 1, 8}};
        std::array<Branch, 9> high{};
        for (std::size_t bar = 1; bar <= 9; ++bar) high[bar - 1] = {manual, 61, bar, 8};
        check_case(profile, routes, timeline, 48000.0, low, "low duplicate drawbars", counts);
        check_case(profile, routes, timeline, 48000.0, overlap, "low overlapping keys", counts);
        check_case(profile, routes, timeline, 48000.0, high, "high duplicate drawbars", counts);
        counts.coherent_cases += 3;
    }
}

void manual_addition_and_cancel(const RuntimeProfile& profile, const CsvRoutes& routes,
                                std::span<const SourceFrame> timeline, Counts& counts) {
    std::array<Branch, 18> branches{};
    constexpr std::array<std::uint8_t, 9> lower_positions{1, 8, 4, 7, 2, 6, 3, 5, 8};
    for (std::size_t bar = 1; bar <= 9; ++bar) {
        branches[bar - 1] = {Manual::Upper, 61, bar, 8};
        branches[9 + bar - 1] = {Manual::Lower, 61, bar, lower_positions[bar - 1]};
    }
    const auto all_branches = std::span<const Branch>(branches);
    const std::array<std::vector<Event>, 8> events{
        registration_events(all_branches.first(9)), registration_events(all_branches.last(9)),
        std::vector<Event>{{0, EventType::Cancel, Manual::Upper, 0, 0.0}},
        std::vector<Event>{{0, EventType::SelectBank, Manual::Upper, 0, 1.0}},
        std::vector<Event>{{0, EventType::Cancel, Manual::Lower, 0, 0.0}},
        std::vector<Event>{{0, EventType::Cancel, Manual::Upper, 0, 0.0}},
        std::vector<Event>{{0, EventType::SelectBank, Manual::Lower, 0, 1.0}},
        std::vector<Event>{{0, EventType::SelectBank, Manual::Upper, 0, 1.0}}};
    constexpr std::array<std::array<bool, 2>, 8> enabled{{
        {true, false}, {true, true}, {false, true}, {true, true},
        {true, false}, {false, false}, {false, true}, {true, true}}};
    auto engine = prepared_engine(profile, 48000.0, counts);
    for (std::size_t stage = 0; stage < events.size(); ++stage) {
        std::array<float, kFrames> output{};
        process_ok(engine, output, events[stage]);
        const auto expected = expected_audio(profile, routes, timeline,
                                             kSilentLead + stage * kFrames, branches, enabled[stage]);
        require_match(output, expected, "manual addition/Cancel stage " + std::to_string(stage), counts);
        CHECK(engine.key_down(Manual::Upper, 96));
        CHECK(engine.key_down(Manual::Lower, 96) == (stage != 0));
        for (const auto manual : kManuals) {
            bool route_enabled = false;
            CHECK(engine.route_enabled(manual, route_enabled));
            // Before the first lower note it is enabled but has no held key.
            if (stage != 0) CHECK(route_enabled == enabled[stage][static_cast<std::size_t>(manual)]);
        }
        ++counts.transition_stages;
    }
    CHECK(engine.frame_clock() == kSilentLead + 8 * kFrames);
    for (const auto& branch : branches) {
        std::uint8_t position = 0;
        CHECK(engine.drawbar_position(branch.manual, branch.drawbar - 1, position));
        CHECK(position == branch.position);
    }
}

void rejection_probes(const RuntimeProfile& nominal, const CsvRoutes& routes,
                      std::span<const SourceFrame> timeline, Counts& counts) {
    const std::array wrong_branch{Branch{Manual::Upper, 1, 1, 8}};
    const std::array muted_branch{Branch{Manual::Lower, 61, 9, 8}};
    auto wrong_route = nominal;
    CHECK(routes[0][0] != routes[0][1]);
    // This is the only access to the production map: a deliberate local mutation,
    // never an expected route. The frozen profile and CSV files are not modified.
    wrong_route.manual_map[0][0] = routes[0][1];
    auto muted_source = nominal;
    muted_source.sources[source_index(routes, muted_branch.front())].peak_amplitude = 0.0;
    const std::array profiles{wrong_route, muted_source};
    const std::array branch_sets{wrong_branch, muted_branch};
    for (std::size_t probe = 0; probe < profiles.size(); ++probe) {
        const auto expected = expected_audio(nominal, routes, timeline, kSilentLead, branch_sets[probe]);
        const auto actual = render_case(profiles[probe], 48000.0, branch_sets[probe], counts);
        const auto comparison = compare_audio(actual, expected);
        CHECK(comparison.mismatches != 0);
        CHECK(comparison.peak_error > 1000.0 * expected.tolerance);
        std::cout << (probe == 0 ? "wrong-route" : "muted-source")
                  << " probe rejected: mismatched_frames=" << comparison.mismatches
                  << " peak_error=" << comparison.peak_error << '\n';
        ++counts.probes;
        counts.probe_frames += actual.size();
    }
}
} // namespace

int main() {
    const auto profile = load_test_profile();
    CHECK(std::string_view(profile.authoring_sha256.data()) ==
          "49791eac8d0b556b0abd2018b8cabc6f240161edab8a9fa0ef97905f2badda83");
    const auto routes = read_csv("data/references/review-a-manual.csv");
    CHECK(routes == read_csv("data/references/review-b-manual.csv"));
    std::array<bool, 91> sources_seen{};
    for (const auto& row : routes)
        for (const auto id : row) sources_seen[static_cast<std::size_t>(id) - 1] = true;
    for (std::size_t source = 0; source < sources_seen.size(); ++source)
        CHECK(sources_seen[source] == (source >= 12));

    Counts counts;
    const auto baseline = source_timeline(profile, 48000.0, kSilentLead + 8 * kFrames);
    for (const auto manual : kManuals)
        for (std::size_t key = 1; key <= 61; ++key)
            for (std::size_t bar = 1; bar <= 9; ++bar) {
                check_one_hot(profile, routes, baseline, 48000.0, manual, key, bar, counts);
                ++counts.full_routes;
            }

    // Both sides of eight documented low/high/second-fold transitions. Values
    // still come solely from CSV cells; these coordinates do not derive routes.
    constexpr std::array<std::array<std::size_t, 2>, 16> boundaries{{
        {12, 1}, {13, 1}, {43, 9}, {44, 9}, {48, 8}, {49, 8}, {51, 7}, {52, 7},
        {55, 6}, {56, 6}, {55, 9}, {56, 9}, {60, 5}, {61, 5}, {60, 8}, {61, 8}}};
    for (const double rate : {44100.0, 96000.0}) {
        const auto timeline = source_timeline(profile, rate, kSilentLead + kFrames);
        for (const auto manual : kManuals)
            for (const auto& cell : boundaries) {
                check_one_hot(profile, routes, timeline, rate, manual, cell[0], cell[1], counts);
                ++counts.other_rate_routes;
            }
    }
    coherent_cases(profile, routes, baseline, counts);
    manual_addition_and_cancel(profile, routes, baseline, counts);
    std::cout << std::setprecision(12);
    rejection_probes(profile, routes, baseline, counts);
    CHECK(counts.full_routes == 1098 && counts.other_rate_routes == 64);
    CHECK(counts.coherent_cases == 6 && counts.transition_stages == 8 && counts.probes == 2);
    CHECK(counts.matched_frames == 150528 && counts.probe_frames == 256);
    CHECK(counts.silent_frames == 19907);
    std::cout << "factory runtime: 1098 routes at 48000 Hz; 32 boundary routes each at 44100/96000 Hz; "
                 "6 coherent cases; 8 manual addition/Cancel stages; 2 rejected probes\n"
              << "matched_audio_frames=" << counts.matched_frames
              << " probe_frames=" << counts.probe_frames
              << " checked_silent_frames=" << counts.silent_frames
              << " total_engine_frames=" << counts.matched_frames + counts.probe_frames + counts.silent_frames
              << " peak_nominal_error=" << counts.peak_error << '\n'
              << "CSV source coverage: all 79 tone IDs 13..91; no manual reference to IDs 1..12. "
                 "Nominal source/mix software only; no pedal audio or physical-fidelity claim.\n";
}
