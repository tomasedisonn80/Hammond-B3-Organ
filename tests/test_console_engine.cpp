#include "TestSupport.h"
#include "hammond/Engine.h"

#include <algorithm>
#include <array>
#include <bit>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <initializer_list>
#include <iostream>
#include <limits>
#include <span>
#include <vector>

namespace {

using namespace hammond;
constexpr Manual upper = Manual::Upper;
constexpr Manual lower = Manual::Lower;
constexpr std::uint64_t seed = 713;
constexpr std::array<double, 3> rates{44100.0, 48000.0, 96000.0};
std::size_t source_oracle_samples = 0;
std::size_t partition_comparisons = 0;
std::size_t recovery_checks = 0;
std::size_t atomic_checks = 0;

[[nodiscard]] Event on(std::uint8_t note, Manual manual = upper, double velocity = 100.0) {
    return {0, EventType::NoteOn, manual, note, velocity};
}
[[nodiscard]] Event off(std::uint8_t note, Manual manual = upper) {
    return {0, EventType::NoteOff, manual, note, 0.0};
}
[[nodiscard]] Event draw(std::uint8_t index, double position, Manual manual = upper) {
    return {0, EventType::Drawbar, manual, index, position};
}
[[nodiscard]] Event percussion(std::uint8_t index, double value) {
    return {0, EventType::Percussion, upper, index, value};
}
[[nodiscard]] Event select(DrawbarBank bank, Manual manual = upper) {
    return {0, EventType::SelectBank, manual, 0, static_cast<double>(bank)};
}
[[nodiscard]] Event cancel(Manual manual = upper) {
    return {0, EventType::Cancel, manual, 0, 0.0};
}
[[nodiscard]] Event panic(Manual manual = upper) {
    return {0, EventType::AllNotesOff, manual, 0, 0.0};
}

void process(Engine& engine, std::uint32_t frames, std::span<float> output = {},
             std::span<const Event> events = {}) {
    const auto result = engine.process(frames, output, events);
    CHECK(result.status == Status::Ok);
    CHECK(result.events_consumed == events.size());
}
void flush(Engine& engine, std::initializer_list<Event> events) {
    process(engine, 0, {}, std::span<const Event>(events.begin(), events.size()));
}

[[nodiscard]] ConsoleModel oracle_model(bool travel = false) {
    auto model = travel ? make_nominal_console_model() : make_legacy_console_model();
    // Deliberately non-factory, exact binary gain choices: integration must use
    // the prepared profile, not hard-code the nominal factory's gain constants.
    model.percussion = {0.25, 0.0625, 0.125, 0.75, 0.125, 2.0, 0.25};
    return model;
}

[[nodiscard]] Engine prepare(const RuntimeProfile& profile, const ConsoleModel& model,
                              double rate = 48000.0, std::uint64_t origin = 0) {
    Engine engine;
    CHECK(engine.prepare(profile, ProcessSpec{rate, 4096, seed, origin}, model) == Status::Ok);
    return engine;
}

struct Sources {
    TonewheelBank bank;
    std::array<double, kToneSourceCount> samples{};
    explicit Sources(const RuntimeProfile& profile, double rate = 48000.0) {
        CHECK(bank.prepare(profile, rate, seed) == Status::Ok);
    }
    void advance() { bank.process_frame(samples); }
    [[nodiscard]] double at(const RuntimeProfile& profile, std::uint8_t note,
                            std::size_t contact) const {
        const auto key = static_cast<std::size_t>(note - kMinManualMidiNote);
        const auto tone = static_cast<std::size_t>(profile.manual_map[key][contact]) - 1;
        return samples[tone];
    }
};

[[nodiscard]] float frame(Engine& engine, Sources& sources) {
    sources.advance();
    std::array<float, 1> output{};
    process(engine, 1, output);
    return output[0];
}
void check_audio(float actual, double unscaled, const RuntimeProfile& profile,
                 double expression = 1.0) {
    const auto expected = static_cast<float>(unscaled * profile.output_gain * expression);
    // A source-bank oracle fixes source identity/phase independently of Engine
    // routing. Different legitimate summation groupings can round one float ULP.
    CHECK_NEAR(actual, expected, 2.0e-8);
    ++source_oracle_samples;
}
void check_q(const Engine& engine, long double expected) {
    CHECK_NEAR(engine.percussion_diagnostics().readiness, expected, 2.0e-11L);
    ++recovery_checks;
}
[[nodiscard]] long double decay(long double initial, std::uint32_t frames,
                                double rate, double tau) {
    return initial * std::exp(-static_cast<long double>(frames) /
                              (static_cast<long double>(rate) * tau));
}
[[nodiscard]] long double recover(long double initial, std::uint32_t frames,
                                  double rate, double tau) {
    return 1.0L - (1.0L - initial) * std::exp(-static_cast<long double>(frames) /
                                            (static_cast<long double>(rate) * tau));
}

void same_histories(const Engine& left, const Engine& right) {
    CHECK(left.prepared() == right.prepared());
    CHECK(left.frame_clock() == right.frame_clock());
    CHECK(left.contact_mode() == right.contact_mode());
    CHECK(left.percussion_diagnostics().readiness == right.percussion_diagnostics().readiness);
    CHECK(left.active_key_count() == right.active_key_count());
    for (const Manual manual : {upper, lower}) {
        for (std::uint32_t note = kMinManualMidiNote; note <= kMaxManualMidiNote; ++note) {
            ContactKeySnapshot first, second;
            CHECK(left.contact_snapshot(manual, note, first));
            CHECK(right.contact_snapshot(manual, note, second));
            CHECK(first == second);
            CHECK(left.key_down(manual, note) == right.key_down(manual, note));
        }
    }
    for (std::uint32_t id = 1; id <= kToneSourceCount; ++id) {
        double first = 0.0, second = 0.0;
        CHECK(left.source_phase_turns(static_cast<ToneId>(id), first));
        CHECK(right.source_phase_turns(static_cast<ToneId>(id), second));
        CHECK(first == second);
    }
}
void same_state(const Engine& left, const Engine& right) {
    same_histories(left, right);
    CHECK(left.controls_snapshot() == right.controls_snapshot());
    CHECK(left.percussion_diagnostics() == right.percussion_diagnostics());
}
void same_audio(std::span<const float> left, std::span<const float> right) {
    CHECK(left.size() == right.size());
    for (std::size_t i = 0; i < left.size(); ++i) {
        CHECK(std::bit_cast<std::uint32_t>(left[i]) == std::bit_cast<std::uint32_t>(right[i]));
    }
}
void same_future(Engine left, Engine right) {
    same_state(left, right);
    const std::array<Event, 4> events{percussion(1, 1), on(72), off(60), draw(0, 5, lower)};
    std::array<float, 1024> a{}, b{};
    process(left, 1024, a, events);
    process(right, 1024, b, events);
    same_audio(a, b);
    same_state(left, right);
}

void test_distinct_folded_contacts(const RuntimeProfile& profile) {
    auto model = oracle_model(true);
    auto& key = model.contacts.keys[0][0];
    key.press_seconds = 0.01;
    key.on_thresholds[0] = 0.125;
    key.off_thresholds[0] = 0.0625;
    key.on_thresholds[2] = 0.5;
    key.off_thresholds[2] = 0.25;
    CHECK(profile.manual_map[0][0] == profile.manual_map[0][2]);
    Engine engine = prepare(profile, model);
    Sources sources(profile);
    flush(engine, {draw(0, 8), draw(2, 8), on(36)});
    for (std::uint32_t n = 0; n < 501; ++n) {
        const auto actual = frame(engine, sources);
        // Full travel is 480 samples. These two independently switched paths
        // become conductive at samples 60 and 240, despite sharing the same tone.
        const double paths = (n >= 60 ? 1.0 : 0.0) + (n >= 240 ? 1.0 : 0.0);
        check_audio(actual, paths * sources.at(profile, 36, 0), profile);
    }
    ContactKeySnapshot snapshot;
    CHECK(engine.contact_snapshot(upper, 36, snapshot));
    CHECK(snapshot.position == 1.0 && snapshot.closed[0] && snapshot.closed[2]);
}

void test_routing_audio_and_masks(const RuntimeProfile& profile) {
    const auto model = oracle_model();
    Engine engine = prepare(profile, model);
    Sources sources(profile);
    flush(engine, {draw(2, 8), draw(8, 8), draw(2, 8, lower), draw(8, 8, lower),
                   percussion(0, 1), on(60), on(48, lower)});
    auto diagnostic = engine.percussion_diagnostics();
    CHECK(diagnostic.prepared && diagnostic.physical_detector && diagnostic.eligible &&
          diagnostic.routed_detector && diagnostic.readiness == 1.0);
    const auto audio = frame(engine, sources);
    check_audio(audio, 0.25 * sources.at(profile, 60, 2) +
                       sources.at(profile, 48, 2) + sources.at(profile, 48, 8) +
                       0.75 * sources.at(profile, 60, 3), profile);

    // Audible masking leaves the physical detector and stored drawbar intact.
    std::uint8_t retained = 0;
    CHECK(engine.drawbar_position(upper, 8, retained) && retained == 8);
    Engine silent_one_foot = engine;
    flush(silent_one_foot, {draw(8, 0)});
    CHECK(silent_one_foot.percussion_diagnostics().routed_detector);
    std::array<float, 91> masked{}, silent{};
    Engine masked_one_foot = engine;
    process(masked_one_foot, 91, masked);
    process(silent_one_foot, 91, silent);
    same_audio(masked, silent);
    same_histories(masked_one_foot, silent_one_foot);

    // Use the retained A bank: no percussion, no normal-mode attenuation, and
    // the upper 1-foot branch returns while lower contributions remain intact.
    const auto before_q = engine.percussion_diagnostics().readiness;
    flush(engine, {{0, EventType::BankDrawbar, upper, 8, 8.0}, select(DrawbarBank::A)});
    diagnostic = engine.percussion_diagnostics();
    CHECK(diagnostic.physical_detector && !diagnostic.eligible && !diagnostic.routed_detector);
    CHECK(diagnostic.readiness == before_q);
    const auto bank_a_audio = frame(engine, sources);
    check_audio(bank_a_audio, sources.at(profile, 60, 8) +
                sources.at(profile, 48, 2) + sources.at(profile, 48, 8), profile);
    CHECK(engine.controls_snapshot().percussion.enabled);
    flush(engine, {cancel()});
    CHECK(engine.key_down(upper, 60));
    CHECK(engine.percussion_diagnostics().physical_detector);
    const auto cancelled_audio = frame(engine, sources);
    check_audio(cancelled_audio, sources.at(profile, 48, 2) +
                sources.at(profile, 48, 8), profile);
    flush(engine, {select(DrawbarBank::B), percussion(0, 0)});
    const auto disabled_audio = frame(engine, sources);
    check_audio(disabled_audio, sources.at(profile, 60, 2) +
                sources.at(profile, 60, 8) + sources.at(profile, 48, 2) +
                sources.at(profile, 48, 8), profile);

    Engine lower_only = prepare(profile, model);
    Sources lower_sources(profile);
    flush(lower_only, {percussion(0, 1), draw(8, 8, lower), on(60, lower)});
    CHECK(!lower_only.percussion_diagnostics().physical_detector);
    CHECK(!lower_only.percussion_diagnostics().routed_detector);
    const auto lower_audio = frame(lower_only, lower_sources);
    check_audio(lower_audio, lower_sources.at(profile, 60, 8), profile);
    CHECK(lower_only.percussion_diagnostics().readiness == 1.0);
}

void test_shared_harmonic_and_readiness(const RuntimeProfile& profile) {
    for (const double rate : rates) {
        const auto model = oracle_model();
        Engine engine = prepare(profile, model, rate);
        Sources sources(profile, rate);
        flush(engine, {percussion(0, 1), on(60)});
        // All sustained drawbars remain zero; selected harmonic still sounds.
        for (std::uint32_t n = 0; n < 101; ++n) {
            const long double q = decay(1.0L, n, rate, 0.25);
            check_q(engine, q);
            const auto audio = frame(engine, sources);
            check_audio(audio, static_cast<double>(q) * 0.75 *
                        sources.at(profile, 60, 3), profile);
        }
        const auto held_q = engine.percussion_diagnostics().readiness;
        flush(engine, {on(64), on(60), off(60), on(60)});
        CHECK(engine.percussion_diagnostics().readiness == held_q);
        CHECK(engine.active_key_count(upper) == 2);
        const long double joined_q = decay(1.0L, 101, rate, 0.25);
        const auto joined_audio = frame(engine, sources);
        check_audio(joined_audio, static_cast<double>(joined_q) * 0.75 *
                    (sources.at(profile, 60, 3) + sources.at(profile, 64, 3)), profile);
        check_q(engine, decay(1.0L, 102, rate, 0.25));

        // Selected-harmonic drawbar is a sustained branch, not an envelope knob.
        flush(engine, {draw(3, 8), percussion(1, 1)});
        const auto third_q = decay(1.0L, 102, rate, 0.25);
        const auto third_audio = frame(engine, sources);
        check_audio(third_audio,
                    0.25 * (sources.at(profile, 60, 3) + sources.at(profile, 64, 3)) +
                    0.75 * static_cast<double>(third_q) *
                    (sources.at(profile, 60, 4) + sources.at(profile, 64, 4)), profile);
        const auto q_before_mode = engine.percussion_diagnostics().readiness;
        flush(engine, {percussion(2, 1), percussion(3, 1)});
        CHECK(engine.percussion_diagnostics().readiness == q_before_mode);
        const auto mode_audio = frame(engine, sources);
        check_audio(mode_audio,
                    sources.at(profile, 60, 3) + sources.at(profile, 64, 3) +
                    0.25 * q_before_mode *
                    (sources.at(profile, 60, 4) + sources.at(profile, 64, 4)), profile);
        const long double after_fast = decay(decay(1.0L, 103, rate, 0.25), 1, rate, 0.0625);
        check_q(engine, after_fast);

        // One remaining upper contact prevents a false all-released recovery.
        flush(engine, {off(60)});
        process(engine, 127);
        check_q(engine, decay(after_fast, 127, rate, 0.0625));
        flush(engine, {off(64)});
        const long double released_q = decay(after_fast, 127, rate, 0.0625);
        const auto q_at_release = engine.percussion_diagnostics().readiness;
        process(engine, 0);
        CHECK(engine.percussion_diagnostics().readiness == q_at_release);
        process(engine, 211);
        check_q(engine, recover(released_q, 211, rate, 0.125));
        CHECK(engine.percussion_diagnostics().readiness > q_at_release);
    }
}

void test_contact_keying_order_and_restore(const RuntimeProfile& profile) {
    auto model = oracle_model(true);
    auto& key = model.contacts.keys[0][24]; // MIDI 60
    key.press_seconds = 0.01;
    key.release_seconds = 0.01;
    key.on_thresholds[3] = 0.25;
    key.off_thresholds[3] = 0.125;
    key.on_thresholds[8] = 0.75;
    key.off_thresholds[8] = 0.5;
    Engine engine = prepare(profile, model);
    Sources sources(profile);
    const Engine initial = engine;
    flush(engine, {percussion(0, 1), on(60), off(60), on(60)});
    ContactKeySnapshot contact;
    CHECK(engine.contact_snapshot(upper, 60, contact));
    CHECK(contact.position == 0.0 && contact.target == 1.0);
    CHECK(engine.frame_clock() == 0 && engine.percussion_diagnostics().readiness == 1.0);
    for (std::uint32_t id = 1; id <= kToneSourceCount; ++id) {
        double before = 0.0, after = 0.0;
        CHECK(initial.source_phase_turns(static_cast<ToneId>(id), before));
        CHECK(engine.source_phase_turns(static_cast<ToneId>(id), after));
        CHECK(before == after);
    }
    for (std::uint32_t n = 0; n <= 360; ++n) {
        const auto before = engine.percussion_diagnostics();
        CHECK(before.physical_detector == (n >= 360));
        CHECK(before.readiness == 1.0);
        const auto sample = frame(engine, sources);
        check_audio(sample, n >= 120 ? 0.75 * sources.at(profile, 60, 3) : 0.0, profile);
    }
    check_q(engine, decay(1.0L, 1, 48000.0, 0.25));
    CHECK(engine.contact_snapshot(upper, 60, contact));
    CHECK(contact.closed[3] && contact.closed[8] && contact.position < 1.0);

    // Ordinary saved controls preserve evolving mechanical/source/q histories.
    Engine unchanged = engine;
    auto controls = engine.controls_snapshot();
    controls.route_enabled[0] = false;
    controls.percussion.harmonic = PercussionHarmonic::Third;
    CHECK(engine.restore_controls(controls));
    same_histories(engine, unchanged);
    CHECK(!engine.percussion_diagnostics().eligible);
    const auto q_before_cancel = engine.percussion_diagnostics().readiness;
    process(engine, 53);
    check_q(engine, recover(q_before_cancel, 53, 48000.0, 0.125));
    flush(engine, {select(DrawbarBank::B)});
    const auto before_repress = engine.percussion_diagnostics().readiness;
    flush(engine, {off(60), on(60)});
    CHECK(engine.percussion_diagnostics().readiness == before_repress);
    CHECK(engine.contact_snapshot(upper, 60, contact));
    CHECK(contact.position > 0.8 && contact.position < 1.0);

    // A released target is not a released detector until its contact actually opens.
    flush(engine, {off(60)});
    CHECK(!engine.key_down(upper, 60));
    CHECK(engine.percussion_diagnostics().physical_detector);
    process(engine, 1);
    CHECK(engine.percussion_diagnostics().readiness < before_repress);
    const auto before_panic = engine.percussion_diagnostics().readiness;
    flush(engine, {panic()});
    CHECK(engine.contact_snapshot(upper, 60, contact));
    CHECK(contact.position == 0.0 && contact.target == 0.0);
    CHECK(std::none_of(contact.closed.begin(), contact.closed.end(), [](bool value) { return value; }));
    CHECK(!engine.percussion_diagnostics().physical_detector);
    CHECK(engine.percussion_diagnostics().readiness == before_panic);
    process(engine, 1);
    check_q(engine, recover(before_panic, 1, 48000.0, 0.125));
}

struct TimedEvent { std::uint32_t frame; Event event; };
[[nodiscard]] std::vector<TimedEvent> timeline() {
    return {
        {0, draw(0, 8)}, {0, draw(2, 8)}, {0, draw(2, 4, lower)},
        {0, percussion(0, 1)}, {0, on(36)}, {3, on(48, lower)},
        {47, on(60)}, {60, on(60)}, {79, percussion(1, 1)},
        {97, percussion(2, 1)}, {127, percussion(3, 1)}, {128, cancel()},
        {129, {0, EventType::BankDrawbar, upper, 8, 8}},
        {153, select(DrawbarBank::A)}, {199, select(DrawbarBank::B)},
        {210, off(36)}, {225, off(60)}, {226, on(60)},
        {257, {0, EventType::Expression, upper, 0, 0.42}},
        {509, on(55, lower)}, {511, percussion(0, 0)}, {512, percussion(0, 1)},
        {700, on(64)}, {901, off(60)}, {902, off(64)}, {902, on(60)},
        {1023, cancel(lower)}, {1024, select(DrawbarBank::A, lower)},
        {1044, {0, EventType::BankDrawbar, lower, 0, 3}}, {1500, panic()},
        {1530, on(67)}, {1599, {0, EventType::BankDrawbar, upper, 17, 8}},
        {1700, select(DrawbarBank::A)}, {1799, select(DrawbarBank::B)},
        {1911, off(67)}, {1999, on(72)}
    };
}
struct Rendered { Engine engine; std::vector<float> audio; };
[[nodiscard]] Rendered render_timeline(const RuntimeProfile& profile, const ConsoleModel& model,
                                       double rate, std::span<const std::uint32_t> pattern,
                                       bool disconnected = false) {
    constexpr std::uint32_t total = 2053;
    Rendered rendered{prepare(profile, model, rate, 1000), std::vector<float>(total)};
    const auto score = timeline();
    std::size_t next = 0, part = 0;
    std::uint32_t cursor = 0;
    while (cursor < total) {
        const auto count = std::min(pattern[part % pattern.size()], total - cursor);
        ++part;
        std::array<Event, 64> local{};
        std::size_t used = 0;
        while (next < score.size() && score[next].frame < cursor + count) {
            CHECK(score[next].frame >= cursor);
            local[used] = score[next].event;
            local[used].offset = score[next].frame - cursor;
            ++used;
            ++next;
        }
        const auto before = rendered.engine.percussion_diagnostics().readiness;
        process(rendered.engine, 0);
        CHECK(rendered.engine.percussion_diagnostics().readiness == before);
        process(rendered.engine, count,
                disconnected ? std::span<float>{} : std::span<float>(rendered.audio).subspan(cursor, count),
                std::span<const Event>(local.data(), used));
        cursor += count;
    }
    CHECK(next == score.size());
    CHECK(rendered.engine.frame_clock() == 1000 + total);
    return rendered;
}

void test_partition_disconnected_and_velocity(const RuntimeProfile& profile) {
    const std::array<std::uint32_t, 1> single{1}, seventeen{17}, sixty_four{64},
        one_twenty_seven{127}, big{1024}, whole{2053};
    const std::array<std::uint32_t, 8> irregular{3, 29, 1, 211, 7, 64, 509, 5};
    const std::array<std::span<const std::uint32_t>, 6> patterns{
        seventeen, sixty_four, one_twenty_seven, big, whole, irregular};
    for (const bool travel : {false, true}) {
        const auto model = oracle_model(travel);
        for (const double rate : rates) {
            const auto reference = render_timeline(profile, model, rate, single);
            for (const auto pattern : patterns) {
                const auto actual = render_timeline(profile, model, rate, pattern);
                same_audio(actual.audio, reference.audio);
                same_state(actual.engine, reference.engine);
                ++partition_comparisons;
            }
            const auto disconnected = render_timeline(profile, model, rate, irregular, true);
            same_future(disconnected.engine, reference.engine);
            ++partition_comparisons;

            Engine soft = prepare(profile, model, rate);
            Engine hard = prepare(profile, model, rate);
            flush(soft, {draw(2, 8), percussion(0, 1), on(60, upper, 1)});
            flush(hard, {draw(2, 8), percussion(0, 1), on(60, upper, 127)});
            same_future(soft, hard);
        }
    }
}

void test_failure_atomicity_and_owned_model(const RuntimeProfile& profile) {
    auto model = oracle_model(true);
    Engine original = prepare(profile, model);
    flush(original, {draw(0, 8), percussion(0, 1), on(60)});
    process(original, 731);
    const std::array<Event, 9> bad_events{
        Event{1, EventType::Percussion, lower, 0, 1}, percussion(4, 0),
        percussion(0, 0.5), percussion(1, -1), percussion(2, 2),
        percussion(3, std::numeric_limits<double>::quiet_NaN()),
        percussion(0, std::numeric_limits<double>::infinity()),
        Event{16, EventType::Percussion, upper, 0, 1},
        Event{1, static_cast<EventType>(255), upper, 0, 1}};
    for (auto bad : bad_events) {
        if (bad.offset == 0) bad.offset = 3;
        Engine actual = original;
        std::array<float, 16> output;
        output.fill(-1234.5F);
        const std::array<Event, 2> events{on(64), bad};
        const auto result = actual.process(16, output, events);
        CHECK(result.status == Status::InvalidEvent && result.events_consumed == 0);
        CHECK(std::all_of(output.begin(), output.end(), [](float value) { return value == -1234.5F; }));
        same_future(actual, original);
        ++atomic_checks;
    }
    for (int variant = 0; variant < 4; ++variant) {
        auto invalid = model;
        if (variant == 0) invalid.contacts.keys[1][60].off_thresholds[8] = 1.0;
        if (variant == 1) invalid.contacts.keys[0][24].press_seconds = std::numeric_limits<double>::infinity();
        if (variant == 2) invalid.percussion.recovery_seconds = 0.0;
        if (variant == 3) invalid.percussion.fast_gain_multiplier = std::numeric_limits<double>::quiet_NaN();
        Engine actual = original;
        CHECK(actual.prepare(profile, ProcessSpec{48000, 4096, 9, 999}, invalid) == Status::InvalidProfile);
        same_future(actual, original);
        ++atomic_checks;
    }
    for (int variant = 0; variant < 3; ++variant) {
        auto invalid = original.controls_snapshot();
        invalid.drawbars[0][0][0] = 8;
        invalid.expression = 0.125;
        if (variant == 0) invalid.percussion.harmonic = static_cast<PercussionHarmonic>(255);
        if (variant == 1) invalid.percussion.volume = static_cast<PercussionVolume>(255);
        if (variant == 2) invalid.percussion.decay = static_cast<PercussionDecay>(255);
        Engine actual = original;
        CHECK(!actual.restore_controls(invalid));
        same_future(actual, original);
        ++atomic_checks;
    }
    auto distinct_model = model;
    Engine owned = prepare(profile, model);
    Engine independent = prepare(profile, distinct_model);
    model.contacts.keys[0][24].press_seconds = 1.0;
    model.contacts.keys[0][24].on_thresholds[8] = 1.0;
    model.percussion.normal_gain = 4.0;
    model.percussion.slow_decay_seconds = 60.0;
    flush(owned, {draw(2, 8), percussion(0, 1), on(60)});
    flush(independent, {draw(2, 8), percussion(0, 1), on(60)});
    same_future(owned, independent);

    ContactKeySnapshot destination;
    destination.position = 0.321;
    const auto sentinel = destination;
    CHECK(!original.contact_snapshot(upper, 97, destination));
    CHECK(destination == sentinel);
    CHECK(!original.contact_snapshot(static_cast<Manual>(255), 60, destination));
    CHECK(destination == sentinel);
}

} // namespace

int main() {
    const auto profile = load_test_profile();
    test_distinct_folded_contacts(profile);
    test_routing_audio_and_masks(profile);
    test_shared_harmonic_and_readiness(profile);
    test_contact_keying_order_and_restore(profile);
    test_partition_disconnected_and_velocity(profile);
    test_failure_atomicity_and_owned_model(profile);
    std::cout << "Console engine passed: " << source_oracle_samples << " source/audio oracles, "
              << recovery_checks << " closed-form readiness checks, "
              << partition_comparisons << " partition/disconnected comparisons, "
              << atomic_checks << " failure-preservation cases.\n";
}
