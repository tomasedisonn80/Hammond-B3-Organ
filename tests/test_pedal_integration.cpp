#include "TestSupport.h"
#include "hammond/ControlStateIO.h"
#include "hammond/Engine.h"

#include <algorithm>
#include <array>
#include <bit>
#include <charconv>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <limits>
#include <optional>
#include <span>
#include <sstream>
#include <string>
#include <string_view>
#include <system_error>
#include <vector>

namespace {
using hammond::Engine;
using hammond::Event;
using hammond::EventType;
using hammond::Manual;
using hammond::PedalId;
using hammond::RuntimeProfile;
using hammond::Status;

constexpr Manual upper = Manual::Upper;
constexpr Manual lower = Manual::Lower;
constexpr std::uint64_t seed = 0x13579bdf2468ace0ULL;
constexpr std::uint64_t origin = 100000007ULL;
constexpr std::uint32_t max_block = 256;
constexpr float sentinel = -12345.25F;
// Fixed before execution: reversed, independently grouped sums have at most
// 50 unit-weight terms per bus. This absolute allowance also covers platforms
// where long double has double precision. Float output gets its rounding term.
constexpr long double double_tolerance = 2e-12L;
constexpr long double float_relative_tolerance =
    2.0L * std::numeric_limits<float>::epsilon();

using CsvRoutes = std::array<std::array<std::optional<unsigned>, 8>, 25>;
using HeldPedals = std::array<bool, 25>;
constexpr std::array<std::array<std::size_t, 2>, 4> bus_columns{{
    {{0, 1}}, {{2, 3}}, {{4, 5}}, {{6, 7}},
}};
static_assert(hammond::kPedalCount == 25 && hammond::kPedalContactCount == 8 &&
              hammond::kToneSourceCount == 91);

struct Counts {
    std::size_t oracle_frames{};
    std::size_t contact_checks{};
    std::size_t phase_checks{};
    std::size_t partition_samples{};
    std::size_t rejection_cases{};
    long double peak_bus_error{};
    long double peak_voice_error{};
    long double peak_audio_error{};
} counts;

CsvRoutes read_csv(std::string_view relative) {
    std::ifstream input(hammond_test::source_path(relative));
    CHECK(input.is_open());
    std::string line;
    const auto read_line = [&]() {
        CHECK(static_cast<bool>(std::getline(input, line)));
        CHECK(line.size() <= 128);
        if (!line.empty() && line.back() == '\r') line.pop_back();
    };
    read_line();
    CHECK(line == "pedal,c1,c2,c3,c4,c5,c6,c7,c8");
    CsvRoutes result{};
    for (std::size_t pedal = 0; pedal < result.size(); ++pedal) {
        read_line();
        std::array<std::string_view, 9> fields{};
        std::size_t begin = 0;
        for (std::size_t field = 0; field < fields.size(); ++field) {
            const auto end = line.find(',', begin);
            CHECK((field == fields.size() - 1) == (end == std::string::npos));
            fields[field] = std::string_view(line).substr(
                begin, end == std::string::npos ? end : end - begin);
            if (end != std::string::npos) begin = end + 1;
        }
        const auto number = [](std::string_view field) {
            unsigned value = 0;
            const auto parsed = std::from_chars(field.data(), field.data() + field.size(), value);
            CHECK(parsed.ec == std::errc{} && parsed.ptr == field.data() + field.size());
            return value;
        };
        CHECK(number(fields[0]) == pedal + 1);
        for (std::size_t contact = 0; contact < 8; ++contact) {
            if (fields[contact + 1].empty()) continue;
            const auto tone = number(fields[contact + 1]);
            CHECK(tone >= 1 && tone <= 91);
            result[pedal][contact] = tone;
        }
    }
    CHECK(!std::getline(input, line));
    CHECK(input.eof());
    return result;
}

Event pedal_on(std::uint8_t pedal, double velocity = 100.0, std::uint32_t offset = 0) {
    return {offset, EventType::PedalOn, lower, pedal, velocity};
}

Event pedal_off(std::uint8_t pedal, std::uint32_t offset = 0) {
    return {offset, EventType::PedalOff, lower, pedal, 0.0};
}

Event pedal_bar(std::uint8_t index, double position, std::uint32_t offset = 0) {
    return {offset, EventType::PedalDrawbar, lower, index, position};
}

void process_ok(Engine& engine, std::uint32_t frames, std::span<float> output = {},
                std::span<const Event> events = {}) {
    const auto result = engine.process(frames, output, events);
    CHECK(result.status == Status::Ok);
    CHECK(result.events_consumed == events.size());
}

Engine prepare(const RuntimeProfile& profile, double rate,
               const hammond::ConsoleModel& console = hammond::make_legacy_console_model()) {
    Engine result;
    CHECK(result.prepare(profile, {rate, max_block, seed, origin}, console) == Status::Ok);
    CHECK(!result.last_pedal_frame().valid);
    return result;
}

hammond::TonewheelBank source_bank(const RuntimeProfile& profile, double rate) {
    hammond::TonewheelBank result;
    CHECK(result.prepare(profile, rate, seed) == Status::Ok);
    return result;
}

void check_phase_histories(const Engine& engine, const hammond::TonewheelBank& sources) {
    for (unsigned id = 1; id <= 91; ++id) {
        double actual = -1.0;
        double expected = -2.0;
        CHECK(engine.source_phase_turns(static_cast<hammond::ToneId>(id), actual));
        CHECK(sources.phase_turns(static_cast<hammond::ToneId>(id), expected));
        CHECK(std::bit_cast<std::uint64_t>(actual) == std::bit_cast<std::uint64_t>(expected));
        ++counts.phase_checks;
    }
}

void check_contacts(const Engine& engine, const HeldPedals& held) {
    hammond::PedalContactStates contacts{};
    CHECK(engine.pedal_contacts_snapshot(contacts));
    CHECK(engine.active_pedal_count() == static_cast<std::size_t>(
        std::count(held.begin(), held.end(), true)));
    for (std::size_t pedal = 0; pedal < 25; ++pedal) {
        const PedalId id{static_cast<std::uint8_t>(pedal + 1)};
        CHECK(engine.pedal_down(id) == held[pedal]);
        for (std::uint32_t contact = 0; contact < 8; ++contact) {
            bool closed = !held[pedal];
            CHECK(engine.pedal_contact_closed(id, contact, closed));
            CHECK(closed == held[pedal]);
            CHECK(contacts[pedal * 8 + contact] == held[pedal]);
            ++counts.contact_checks;
        }
    }
}

// Documentary CSV cells choose source IDs; these literals choose bus columns.
// Reverse pedal/column order and integer-numerator voice equations deliberately
// avoid the generated table, routing formula, production matrix, gain table,
// kernel and render_nominal_pedal_voice as sources of expected values.
struct OracleFrame {
    std::array<long double, 4> buses{};
    std::array<long double, 2> mixtures{};
    long double output{};
};

OracleFrame oracle_frame(const CsvRoutes& routes, const HeldPedals& held,
                         const std::array<double, 91>& samples,
                         const hammond::PedalDrawbarPositions& positions) {
    OracleFrame result;
    for (std::size_t bus = 0; bus < 4; ++bus) {
        for (std::size_t pedal = 25; pedal-- > 0;) {
            if (!held[pedal]) continue;
            for (std::size_t slot = 2; slot-- > 0;) {
                const auto tone = routes[pedal][bus_columns[bus][slot]];
                if (tone) result.buses[bus] += samples[*tone - 1];
            }
        }
    }
    const auto& b = result.buses;
    result.mixtures[0] = (4 * b[0] + 2 * b[1] + b[2] + b[3]) / 8;
    result.mixtures[1] = (b[0] + 4 * b[1] + 2 * b[2] + b[3]) / 8;
    result.output = (positions[0] * result.mixtures[0] +
                     positions[1] * result.mixtures[1]) / 8;
    return result;
}

void check_frames(Engine& engine, hammond::TonewheelBank& sources,
                  const RuntimeProfile& profile, const CsvRoutes& routes,
                  const HeldPedals& held, hammond::PedalDrawbarPositions positions,
                  std::uint32_t frames, long double manual_source13_gain = 0.0L,
                  bool connected = true) {
    for (std::uint32_t frame = 0; frame < frames; ++frame) {
        const auto clock = engine.frame_clock();
        std::array<double, 91> samples{};
        sources.process_frame(samples);
        const auto expected = oracle_frame(routes, held, samples, positions);
        std::array<float, 1> output{sentinel};
        process_ok(engine, 1, connected ? std::span<float>(output) : std::span<float>{});
        const auto actual = engine.last_pedal_frame();
        CHECK(actual.valid && actual.frame == clock);
        CHECK(actual.sample_rate == sources.sample_rate());
        CHECK(actual.positions == positions);
        for (std::size_t bus = 0; bus < 4; ++bus) {
            CHECK_NEAR(actual.buses[bus], expected.buses[bus], double_tolerance);
            counts.peak_bus_error = std::max(counts.peak_bus_error,
                std::fabs(static_cast<long double>(actual.buses[bus]) - expected.buses[bus]));
        }
        for (std::size_t mix = 0; mix < 2; ++mix) {
            CHECK_NEAR(actual.voice.mixtures[mix], expected.mixtures[mix], double_tolerance);
        }
        CHECK_NEAR(actual.voice.output, expected.output, double_tolerance);
        counts.peak_voice_error = std::max(counts.peak_voice_error,
            std::fabs(static_cast<long double>(actual.voice.output) - expected.output));
        if (connected) {
            const auto expected_audio = (manual_source13_gain * samples[12] + expected.output) *
                profile.output_gain * engine.expression();
            const auto tolerance = double_tolerance +
                float_relative_tolerance * std::fabs(expected_audio);
            CHECK_NEAR(output[0], expected_audio, tolerance);
            counts.peak_audio_error = std::max(counts.peak_audio_error,
                std::fabs(static_cast<long double>(output[0]) - expected_audio));
        } else {
            CHECK(output[0] == sentinel);
        }
        check_phase_histories(engine, sources);
        ++counts.oracle_frames;
    }
}

struct Histories {
    std::uint64_t clock{};
    std::array<std::uint64_t, 91> phase_bits{};
    std::array<hammond::ContactKeySnapshot, 122> manual_contacts{};
    std::array<bool, 122> manual_down{};
    hammond::PedalContactStates pedal_contacts{};
    HeldPedals pedal_down{};
    std::size_t manual_count{};
    std::size_t pedal_count{};
    std::uint64_t readiness_bits{};
    hammond::PedalRenderDiagnostics last_pedal{};
    bool operator==(const Histories&) const = default;
};

Histories histories(const Engine& engine) {
    Histories result;
    result.clock = engine.frame_clock();
    for (std::size_t tone = 0; tone < 91; ++tone) {
        double phase = -1.0;
        CHECK(engine.source_phase_turns(static_cast<hammond::ToneId>(tone + 1), phase));
        result.phase_bits[tone] = std::bit_cast<std::uint64_t>(phase);
    }
    for (std::size_t manual = 0; manual < 2; ++manual) {
        for (std::uint32_t key = 0; key < 61; ++key) {
            const auto slot = manual * 61 + key;
            CHECK(engine.contact_snapshot(static_cast<Manual>(manual), key + 36,
                                           result.manual_contacts[slot]));
            result.manual_down[slot] = engine.key_down(static_cast<Manual>(manual), key + 36);
        }
    }
    CHECK(engine.pedal_contacts_snapshot(result.pedal_contacts));
    for (std::size_t pedal = 0; pedal < 25; ++pedal)
        result.pedal_down[pedal] = engine.pedal_down(PedalId{static_cast<std::uint8_t>(pedal + 1)});
    result.manual_count = engine.active_key_count();
    result.pedal_count = engine.active_pedal_count();
    result.readiness_bits = std::bit_cast<std::uint64_t>(engine.percussion_diagnostics().readiness);
    result.last_pedal = engine.last_pedal_frame();
    return result;
}

void same_audio(std::span<const float> actual, std::span<const float> expected) {
    CHECK(actual.size() == expected.size());
    for (std::size_t frame = 0; frame < actual.size(); ++frame)
        CHECK(std::bit_cast<std::uint32_t>(actual[frame]) ==
              std::bit_cast<std::uint32_t>(expected[frame]));
}

void all_pedals_and_shared_sources(const RuntimeProfile& profile, const CsvRoutes& routes) {
    CHECK(profile.manual_map[0][2] == 13);
    for (const double rate : {44100.0, 48000.0, 96000.0}) {
        auto engine = prepare(profile, rate);
        auto sources = source_bank(profile, rate);
        auto controls = engine.controls_snapshot();
        controls.expression = 0.625;
        controls.pedal_drawbars = {8, 3};
        CHECK(engine.restore_controls(controls));
        HeldPedals held{};
        check_contacts(engine, held);
        for (std::uint8_t pedal = 1; pedal <= 25; ++pedal) {
            const std::array press{pedal_on(pedal, pedal % 2 == 0 ? 1 : 127)};
            process_ok(engine, 0, {}, press);
            held[pedal - 1] = true;
            check_contacts(engine, held); // Includes every disconnected C2 state.
            CHECK(engine.active_key_count() == 0);
            check_frames(engine, sources, profile, routes, held, {8, 3}, 17);
            const std::array release{pedal_off(pedal)};
            process_ok(engine, 0, {}, release);
            held[pedal - 1] = false;
            check_contacts(engine, held);
        }
        std::vector<Event> press_all;
        for (std::uint8_t pedal = 1; pedal <= 25; ++pedal) press_all.push_back(pedal_on(pedal));
        process_ok(engine, 0, {}, press_all);
        held.fill(true);
        check_contacts(engine, held);
        check_frames(engine, sources, profile, routes, held, {8, 3}, 64);

        // Both manuals and two pedal contacts consume source 13 from the same
        // source sample. Its coherence is tested without reading Engine phases
        // to construct audio expectations or starting a note-local oscillator.
        const std::array collide{
            Event{0, EventType::PedalAllNotesOff, lower, 0, 0}, pedal_on(1),
            Event{0, EventType::Drawbar, upper, 2, 7},
            Event{0, EventType::Drawbar, lower, 2, 3},
            Event{0, EventType::NoteOn, upper, 36, 100},
            Event{0, EventType::NoteOn, lower, 36, 100}};
        process_ok(engine, 0, {}, collide);
        held.fill(false);
        held[0] = true;
        check_contacts(engine, held);
        const long double manual_gain = static_cast<long double>(profile.drawbar_gains[7]) +
                                        profile.drawbar_gains[3];
        check_frames(engine, sources, profile, routes, held, {8, 3}, 96, manual_gain);
    }
}

void division_routing_and_percussion(const RuntimeProfile& profile, const CsvRoutes& routes) {
    auto engine = prepare(profile, 48000.0);
    auto sources = source_bank(profile, 48000.0);
    HeldPedals held{};
    held[0] = true;
    const std::array start{pedal_bar(0, 8), pedal_bar(1, 4), pedal_on(1),
        Event{0, EventType::Drawbar, lower, 2, 8},
        Event{0, EventType::NoteOn, lower, 36, 100}};
    process_ok(engine, 0, {}, start);
    check_frames(engine, sources, profile, routes, held, {8, 4}, 31, profile.drawbar_gains[8]);
    const std::array cancel{Event{0, EventType::Cancel, lower, 0, 0}};
    process_ok(engine, 0, {}, cancel);
    CHECK(engine.key_down(lower, 36) && engine.active_key_count() == 1);
    check_contacts(engine, held);
    check_frames(engine, sources, profile, routes, held, {8, 4}, 37);
    const std::array select{Event{0, EventType::SelectBank, lower, 0, 1}};
    process_ok(engine, 0, {}, select);
    check_frames(engine, sources, profile, routes, held, {8, 4}, 29, profile.drawbar_gains[8]);
    const std::array manual_panic{Event{0, EventType::AllNotesOff, lower, 0, 0}};
    process_ok(engine, 0, {}, manual_panic);
    CHECK(engine.active_key_count() == 0);
    check_contacts(engine, held);
    check_frames(engine, sources, profile, routes, held, {8, 4}, 23);
    const std::array pedal_panic{Event{0, EventType::NoteOn, lower, 36, 100},
        Event{0, EventType::PedalAllNotesOff, lower, 0, 0}};
    process_ok(engine, 0, {}, pedal_panic);
    held.fill(false);
    CHECK(engine.key_down(lower, 36));
    check_contacts(engine, held);
    check_frames(engine, sources, profile, routes, held, {8, 4}, 41, profile.drawbar_gains[8]);

    auto manual_only = prepare(profile, 48000.0);
    auto with_pedals = prepare(profile, 48000.0);
    const std::array upper_start{Event{0, EventType::Percussion, upper, 0, 1},
        Event{0, EventType::Drawbar, upper, 2, 7},
        Event{0, EventType::NoteOn, upper, 60, 100}};
    process_ok(manual_only, 0, {}, upper_start);
    process_ok(with_pedals, 0, {}, upper_start);
    for (std::uint32_t frame = 0; frame < 1536; ++frame) {
        if (frame == 0 || frame == 300 || frame == 700 || frame == 1100) {
            const Event command = frame == 0 ? pedal_on(25) :
                frame == 300 ? pedal_bar(0, 8) : frame == 700 ? pedal_off(25) :
                Event{0, EventType::PedalAllNotesOff, lower, 0, 0};
            process_ok(with_pedals, 0, {}, std::span(&command, 1));
        }
        if (frame == 900) {
            const std::array release{Event{0, EventType::NoteOff, upper, 60, 0}};
            process_ok(manual_only, 0, {}, release);
            process_ok(with_pedals, 0, {}, release);
        }
        CHECK(manual_only.percussion_diagnostics() == with_pedals.percussion_diagnostics());
        std::array<float, 1> a{}, b{};
        process_ok(manual_only, 1, a);
        process_ok(with_pedals, 1, b);
        if (frame < 300 || frame >= 700) same_audio(a, b);
        CHECK(manual_only.percussion_diagnostics() == with_pedals.percussion_diagnostics());
    }
}

// Frozen legacy grammars are independent of the current serializer. These are
// the same controls used by the original live-history migration scenario;
// removing fields from production state4 would not qualify an old reader.
constexpr std::string_view kLegacyHistoryManualRecords =
    "manual upper selected B route_enabled 1\n"
    "bank A 0 7 0 0 0 0 0 0 0\n"
    "bank B 0 0 0 0 0 0 0 0 0\n"
    "manual lower selected B route_enabled 1\n"
    "bank A 0 0 0 0 0 0 0 0 0\n"
    "bank B 0 0 0 0 0 0 0 0 0\n"
    "end\n";
constexpr std::string_view kHistoryPercussion =
    "percussion enabled 1 harmonic second volume normal decay slow\n";
constexpr std::string_view kCurrentHistoryDocument =
    "B3CONTROLS4\n"
    "registration_catalog atlas-chapel-nominal-v1 sha256 "
    "c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf\n"
    "expression 0.375\n"
    "percussion enabled 1 harmonic second volume normal decay slow\n"
    "pedal drawbars 6 2\n"
    "manual upper selected A fixed_registration C# route_enabled 0\n"
    "bank A 0 7 0 0 0 0 0 0 0\n"
    "bank B 0 0 0 0 0 0 0 0 0\n"
    "manual lower selected B fixed_registration G# route_enabled 1\n"
    "bank A 0 0 0 0 0 0 0 0 0\n"
    "bank B 0 0 0 0 0 0 0 0 0\n"
    "end\n";

std::string legacy_control_text(unsigned version) {
    CHECK(version >= 1 && version <= 3);
    if (version == 1) {
        return std::string("B3CONTROLS1\nexpression 0.375\n") +
            std::string(kLegacyHistoryManualRecords);
    }
    if (version == 2) {
        return std::string("B3CONTROLS2\nexpression 0.375\n") +
            std::string(kHistoryPercussion) + std::string(kLegacyHistoryManualRecords);
    }
    return std::string("B3CONTROLS3\nexpression 0.375\n") +
        std::string(kHistoryPercussion) + "pedal drawbars 6 2\n" +
        std::string(kLegacyHistoryManualRecords);
}

void controls_rates_and_historical_diagnostics(const RuntimeProfile& profile,
                                               const CsvRoutes& routes) {
    auto engine = prepare(profile, 44100.0);
    auto sources = source_bank(profile, 44100.0);
    HeldPedals held{};
    held[7] = true; // Its second contact is physically closed but unconnected.
    const std::array tied{pedal_on(8), pedal_off(8), pedal_on(8, 1)};
    process_ok(engine, 0, {}, tied);
    CHECK(engine.frame_clock() == origin && !engine.last_pedal_frame().valid);
    check_contacts(engine, held);
    check_frames(engine, sources, profile, routes, held, {0, 0}, 47);
    const auto muted_history = histories(engine);
    const std::array unmute{pedal_bar(0, 5), pedal_bar(1, 7)};
    process_ok(engine, 0, {}, unmute);
    CHECK(histories(engine) == muted_history);
    CHECK(engine.controls_snapshot().pedal_drawbars == (hammond::PedalDrawbarPositions{5, 7}));
    CHECK(engine.last_pedal_frame().positions == (hammond::PedalDrawbarPositions{0, 0}));
    check_frames(engine, sources, profile, routes, held, {5, 7}, 37);

    for (const double rate : {48000.0, 96000.0, 44100.0, 44100.0}) {
        const auto before = histories(engine);
        const auto controls = engine.controls_snapshot();
        CHECK(engine.reconfigure_sample_rate(rate) == Status::Ok);
        CHECK(sources.reconfigure_sample_rate(rate) == Status::Ok);
        CHECK(histories(engine) == before);
        CHECK(engine.controls_snapshot() == controls);
        check_phase_histories(engine, sources);
        check_frames(engine, sources, profile, routes, held, {5, 7}, 43, 0.0L, false);
        CHECK(engine.last_pedal_frame().sample_rate == rate);
    }
    for (const double bad_rate : {32000.0, 0.0, std::numeric_limits<double>::infinity(),
                                  std::numeric_limits<double>::quiet_NaN()}) {
        const auto before = histories(engine);
        const auto controls = engine.controls_snapshot();
        CHECK(engine.reconfigure_sample_rate(bad_rate) == Status::InvalidSpec);
        CHECK(histories(engine) == before && engine.controls_snapshot() == controls);
        CHECK(engine.sample_rate() == 44100.0);
    }
    check_frames(engine, sources, profile, routes, held, {5, 7}, 31);

    // Restore while manual contacts are in flight and readiness has already
    // decayed. Ordinary saved controls cannot replace these transient histories.
    auto moving = prepare(profile, 48000.0, hammond::make_nominal_console_model());
    const std::array moving_start{pedal_on(25), pedal_bar(0, 6), pedal_bar(1, 2),
        Event{0, EventType::Percussion, upper, 0, 1},
        Event{0, EventType::NoteOn, upper, 60, 100},
        Event{0, EventType::NoteOn, lower, 36, 100}};
    process_ok(moving, 0, {}, moving_start);
    for (unsigned block = 0; block < 3; ++block) process_ok(moving, 256);
    const std::array lift{Event{0, EventType::KeyPosition, upper, 60, 0.5},
        Event{0, EventType::NoteOff, lower, 36, 0}};
    process_ok(moving, 73, {}, lift);
    CHECK(moving.percussion_diagnostics().readiness < 1.0);
    auto legacy_expected = moving.controls_snapshot();
    legacy_expected.expression = 0.375;
    legacy_expected.drawbars[0][0][1] = 7;
    auto saved = legacy_expected;
    saved.selected_banks = {hammond::DrawbarBank::A, hammond::DrawbarBank::B};
    saved.fixed_registrations = {hammond::FixedRegistration::CSharp,
                                 hammond::FixedRegistration::GSharp};
    saved.route_enabled = {false, true};
    std::string current, error;
    CHECK(hammond::serialize_controls(saved, current, error));
    CHECK(error.empty() && current == kCurrentHistoryDocument);
    for (const unsigned version : {4U, 3U, 2U, 1U}) {
        // Every old reader starts with cancelled fixed memory and nonzero pedals.
        auto destination = saved;
        std::istringstream input(version == 4 ? current : legacy_control_text(version));
        CHECK(hammond::parse_controls(input, destination, error));
        CHECK(error.empty());
        auto expected_controls = version == 4 ? saved : legacy_expected;
        if (version < 3) expected_controls.pedal_drawbars = {0, 0};
        if (version == 1) expected_controls.percussion = {};
        CHECK(destination == expected_controls);
        const auto before = histories(moving);
        CHECK(moving.restore_controls(destination));
        CHECK(histories(moving) == before);
        CHECK(moving.controls_snapshot() == destination);
        auto selection = hammond::PresetSelection::A;
        CHECK(moving.selected_preset(upper, selection));
        CHECK(selection == (version == 4 ? hammond::PresetSelection::Cancel :
                                            hammond::PresetSelection::BankB));
        CHECK(moving.selected_preset(lower, selection));
        CHECK(selection == (version == 4 ? hammond::PresetSelection::GSharp :
                                            hammond::PresetSelection::BankB));
        CHECK(moving.pedal_down(PedalId{25}));
        CHECK(moving.last_pedal_frame().positions == saved.pedal_drawbars);
    }
    // Preserve the original version-1 -> upper-B percussion re-enable check.
    const auto before_reenable = histories(moving);
    CHECK(moving.restore_controls(legacy_expected));
    CHECK(histories(moving) == before_reenable);
    CHECK(moving.percussion_diagnostics().eligible);
    auto twin = moving;
    process_ok(moving, 0); // Empty flush is also a strict history no-op.
    CHECK(histories(moving) == histories(twin));
    std::array<float, 128> actual{}, expected{};
    process_ok(moving, 128, actual);
    process_ok(twin, 128, expected);
    same_audio(actual, expected);

    const auto before_fixed_restore = histories(moving);
    CHECK(moving.restore_controls(saved));
    CHECK(histories(moving) == before_fixed_restore);
    CHECK(!moving.percussion_diagnostics().eligible);
    auto fixed_twin = moving;
    process_ok(moving, 0);
    CHECK(histories(moving) == histories(fixed_twin));
    process_ok(moving, 128, actual);
    process_ok(fixed_twin, 128, expected);
    same_audio(actual, expected);

    const auto last = engine.last_pedal_frame();
    auto invalid = engine.controls_snapshot();
    invalid.pedal_drawbars[1] = 9;
    CHECK(!engine.restore_controls(invalid));
    CHECK(engine.last_pedal_frame() == last);
    CHECK(engine.prepare(profile, {96000.0, max_block, seed, origin}) == Status::Ok);
    CHECK(!engine.last_pedal_frame().valid && engine.active_pedal_count() == 0);
}

std::vector<Event> schedule() {
    return {
        pedal_bar(0, 8), pedal_bar(1, 3), pedal_on(1),
        Event{0, EventType::Drawbar, upper, 2, 7},
        Event{0, EventType::Drawbar, lower, 2, 6},
        Event{0, EventType::NoteOn, upper, 60, 100},
        Event{0, EventType::Percussion, upper, 0, 1},
        pedal_on(8, 1, 127), pedal_on(25, 127, 128), pedal_off(1, 255),
        pedal_on(1, 100, 255), pedal_on(1, 0, 255), pedal_on(13, 100, 256),
        Event{300, EventType::NoteOn, lower, 36, 100},
        Event{420, EventType::Cancel, lower, 0, 0},
        pedal_bar(1, 8, 511), pedal_off(8, 512),
        Event{613, EventType::SelectBank, lower, 0, 1},
        Event{700, EventType::AllNotesOff, lower, 0, 0},
        pedal_bar(0, 0, 767), pedal_on(2, 100, 768),
        Event{800, EventType::NoteOff, upper, 60, 0},
        Event{900, EventType::Expression, upper, 0, 0.5},
        Event{1023, EventType::PedalAllNotesOff, lower, 0, 0},
        pedal_on(24, 100, 1024), pedal_bar(0, 7, 1201),
        Event{1300, EventType::KeyPosition, upper, 72, 0.65},
        pedal_off(24, 1536)};
}

struct Run {
    Engine engine;
    std::vector<float> audio;
};

Run partition_run(const RuntimeProfile& profile, double rate,
                   std::span<const std::uint32_t> partition, bool disconnect) {
    constexpr std::uint32_t total = 1601;
    Run result{prepare(profile, rate, hammond::make_nominal_console_model()),
               std::vector<float>(total, sentinel)};
    const auto events = schedule();
    std::uint32_t start = 0;
    std::size_t part = 0, next = 0;
    while (start < total) {
        auto frames = std::min(partition[part++ % partition.size()], total - start);
        // Keep the disconnected region fixed in absolute sample time for every
        // partition, including events exactly on both connection boundaries.
        if (start < 512) frames = std::min(frames, 512 - start);
        else if (start < 768) frames = std::min(frames, 768 - start);
        std::vector<Event> batch;
        while (next < events.size() && events[next].offset < start + frames) {
            CHECK(events[next].offset >= start);
            auto event = events[next++];
            event.offset -= start;
            batch.push_back(event);
        }
        const bool connected = !disconnect || start < 512 || start >= 768;
        process_ok(result.engine, frames,
            connected ? std::span<float>(result.audio).subspan(start, frames) : std::span<float>{},
            batch);
        start += frames;
    }
    CHECK(next == events.size());
    return result;
}

void partitioning_and_disconnected_output(const RuntimeProfile& profile) {
    constexpr std::array<std::uint32_t, 1> single{1}, regular{64};
    constexpr std::array<std::uint32_t, 7> irregular{7, 1, 113, 3, 31, 256, 19};
    for (const double rate : {44100.0, 48000.0, 96000.0}) {
        const auto reference = partition_run(profile, rate, single, false);
        for (const bool disconnect : {false, true}) {
            for (const auto chunks : {std::span<const std::uint32_t>(regular),
                                      std::span<const std::uint32_t>(irregular)}) {
                const auto actual = partition_run(profile, rate, chunks, disconnect);
                for (std::size_t frame = 0; frame < actual.audio.size(); ++frame) {
                    if (disconnect && frame >= 512 && frame < 768) {
                        CHECK(actual.audio[frame] == sentinel);
                        continue;
                    }
                    CHECK(std::bit_cast<std::uint32_t>(actual.audio[frame]) ==
                          std::bit_cast<std::uint32_t>(reference.audio[frame]));
                    ++counts.partition_samples;
                }
                CHECK(histories(actual.engine) == histories(reference.engine));
                CHECK(actual.engine.controls_snapshot() == reference.engine.controls_snapshot());
                CHECK(actual.engine.percussion_diagnostics() == reference.engine.percussion_diagnostics());
            }
        }
    }
}

void rejected_batch_is_transactional(const RuntimeProfile& profile) {
    auto original = prepare(profile, 48000.0, hammond::make_nominal_console_model());
    const std::array start{pedal_on(8), pedal_bar(0, 8), pedal_bar(1, 5),
        Event{0, EventType::NoteOn, upper, 60, 100},
        Event{0, EventType::Percussion, upper, 0, 1},
        Event{0, EventType::Drawbar, lower, 2, 7},
        Event{0, EventType::NoteOn, lower, 36, 100}};
    process_ok(original, 256, {}, start);
    process_ok(original, 256);
    const std::array invalid{
        Event{31, EventType::PedalOn, upper, 1, 100},
        Event{31, EventType::PedalOn, lower, 0, 100},
        Event{31, EventType::PedalOn, lower, 26, 100},
        Event{31, EventType::PedalOn, lower, 1, 0.5},
        Event{31, EventType::PedalOn, lower, 1, std::numeric_limits<double>::quiet_NaN()},
        Event{31, EventType::PedalOff, lower, 8, 1},
        Event{31, EventType::PedalDrawbar, lower, 2, 7},
        Event{31, EventType::PedalDrawbar, lower, 1, 9},
        Event{31, EventType::PedalAllNotesOff, lower, 1, 0},
        Event{32, EventType::PedalOn, lower, 1, 100}};
    for (const auto bad : invalid) {
        auto engine = original;
        auto twin = original;
        const auto before = histories(engine);
        const auto controls = engine.controls_snapshot();
        const auto percussion = engine.percussion_diagnostics();
        // A valid early pedal release and control change must not leak through
        // when preflight discovers a bad event at the end of the same batch.
        const std::array events{pedal_off(8), pedal_bar(0, 1, 8), bad};
        std::array<float, 32> output;
        output.fill(sentinel);
        const auto rejected = engine.process(32, output, events);
        CHECK(rejected.status == Status::InvalidEvent && rejected.events_consumed == 0);
        CHECK(std::all_of(output.begin(), output.end(), [](float value) { return value == sentinel; }));
        CHECK(histories(engine) == before && engine.controls_snapshot() == controls);
        CHECK(engine.percussion_diagnostics() == percussion && engine.sample_rate() == 48000.0);
        std::array<float, 128> actual{}, expected{};
        process_ok(engine, 128, actual);
        process_ok(twin, 128, expected);
        same_audio(actual, expected);
        CHECK(histories(engine) == histories(twin));
        ++counts.rejection_cases;
    }
}
} // namespace

int main() {
    const auto review_a = read_csv("data/references/review-a-pedal.csv");
    const auto review_b = read_csv("data/references/review-b-pedal.csv");
    CHECK(review_a == review_b);
    std::size_t unconnected = 0;
    for (const auto& pedal : review_a)
        for (const auto& tone : pedal) if (!tone) ++unconnected;
    CHECK(unconnected == 5);
    auto profile = load_test_profile();
    profile.output_gain = 0.3125;
    all_pedals_and_shared_sources(profile, review_a);
    division_routing_and_percussion(profile, review_b);
    controls_rates_and_historical_diagnostics(profile, review_a);
    partitioning_and_disconnected_output(profile);
    rejected_batch_is_transactional(profile);
    std::cout << "Pedal Engine integration: both 200-cell CSV maps; "
              << counts.oracle_frames << " independent oracle frames; "
              << counts.contact_checks << " contact checks; "
              << counts.phase_checks << " bitwise source-phase checks; "
              << counts.partition_samples << " bitwise partition samples; "
              << counts.rejection_cases << " late-invalid transactions.\n"
              << std::setprecision(18)
              << "Peak absolute bus/voice/audio error: " << counts.peak_bus_error << " / "
              << counts.peak_voice_error << " / " << counts.peak_audio_error << '\n';
}
