#include "TestSupport.h"
#include "hammond/Engine.h"

#include <algorithm>
#include <array>
#include <bit>
#include <cmath>
#include <cstdint>
#include <initializer_list>
#include <iostream>
#include <limits>
#include <numbers>
#include <span>
#include <vector>

namespace {
using namespace hammond;
constexpr Manual upper = Manual::Upper;
constexpr Manual lower = Manual::Lower;
constexpr std::array<double, 3> rates{44100.0, 48000.0, 96000.0};
constexpr std::uint64_t seed = 1939;
std::size_t state_pairs = 0;
std::size_t audio_pairs = 0;
std::size_t formula_samples = 0;
std::size_t rejected_calls = 0;
long double largest_audio_error = 0.0L;

static_assert(static_cast<unsigned>(EventType::NoteOn) == 0);
static_assert(static_cast<unsigned>(EventType::NoteOff) == 1);
static_assert(static_cast<unsigned>(EventType::Drawbar) == 2);
static_assert(static_cast<unsigned>(EventType::Expression) == 3);
static_assert(static_cast<unsigned>(EventType::AllNotesOff) == 4);
static_assert(static_cast<unsigned>(EventType::BankDrawbar) == 5);
static_assert(static_cast<unsigned>(EventType::SelectBank) == 6);
static_assert(static_cast<unsigned>(EventType::Cancel) == 7);
static_assert(static_cast<unsigned>(EventType::Percussion) == 8);
static_assert(static_cast<unsigned>(EventType::KeyPosition) == 9);

[[nodiscard]] Event position(double target, Manual manual = upper,
                             std::uint8_t note = 60) {
    return {0, EventType::KeyPosition, manual, note, target};
}
[[nodiscard]] Event note_on(Manual manual = upper, std::uint8_t note = 60) {
    return {0, EventType::NoteOn, manual, note, 100.0};
}
[[nodiscard]] Event percussion() { return {0, EventType::Percussion, upper, 0, 1.0}; }

void process(Engine& engine, std::uint32_t frames, std::span<float> output = {},
             std::span<const Event> events = {}) {
    const auto result = engine.process(frames, output, events);
    CHECK(result.status == Status::Ok);
    CHECK(result.events_consumed == events.size());
}
void flush(Engine& engine, std::initializer_list<Event> events) {
    process(engine, 0, {}, std::span<const Event>(events.begin(), events.size()));
}
[[nodiscard]] Engine prepared(const RuntimeProfile& profile, double rate, bool nominal = true) {
    Engine engine;
    CHECK(engine.prepare(profile, {rate, 4096, seed, 11}, nominal ?
                         make_nominal_console_model() : make_legacy_console_model()) == Status::Ok);
    return engine;
}
[[nodiscard]] ContactKeySnapshot contact(const Engine& engine, Manual manual = upper,
                                         std::uint8_t note = 60) {
    ContactKeySnapshot result;
    CHECK(engine.contact_snapshot(manual, note, result));
    return result;
}

void same_phases(const Engine& first, const Engine& second) {
    for (std::uint32_t id = 1; id <= kToneSourceCount; ++id) {
        double a = -1.0, b = -2.0;
        CHECK(first.source_phase_turns(static_cast<ToneId>(id), a));
        CHECK(second.source_phase_turns(static_cast<ToneId>(id), b));
        CHECK(a == b);
    }
}
void same_state(const Engine& first, const Engine& second) {
    CHECK(first.frame_clock() == second.frame_clock());
    CHECK(first.sample_rate() == second.sample_rate());
    CHECK(first.contact_mode() == second.contact_mode());
    CHECK(first.controls_snapshot() == second.controls_snapshot());
    CHECK(first.percussion_diagnostics() == second.percussion_diagnostics());
    CHECK(first.active_key_count() == second.active_key_count());
    for (Manual manual : {upper, lower}) {
        for (std::uint32_t note = 36; note <= 96; ++note) {
            ContactKeySnapshot a, b;
            CHECK(first.contact_snapshot(manual, note, a));
            CHECK(second.contact_snapshot(manual, note, b));
            CHECK(a == b);
            CHECK(first.key_down(manual, note) == second.key_down(manual, note));
        }
    }
    same_phases(first, second);
    ++state_pairs;
}
void same_audio(std::span<const float> first, std::span<const float> second) {
    CHECK(first.size() == second.size());
    for (std::size_t i = 0; i < first.size(); ++i) {
        CHECK(std::bit_cast<std::uint32_t>(first[i]) ==
              std::bit_cast<std::uint32_t>(second[i]));
        ++audio_pairs;
    }
}
void same_future(Engine first, Engine second) {
    same_state(first, second);
    std::array<float, 257> a{}, b{};
    process(first, 257, a);
    process(second, 257, b);
    same_audio(a, b);
    same_state(first, second);
}

// The oracle reads the public current phase and applies the stated isolated
// single-contact sine route. It does not call TonewheelBank or copy its PRNG.
void check_isolated_sample(Engine& engine, const RuntimeProfile& profile,
                           std::size_t contact_index, double gain) {
    const auto tone = profile.manual_map[60 - 36][contact_index];
    double phase = 0.0;
    CHECK(engine.source_phase_turns(tone, phase));
    const auto& source = profile.sources[static_cast<std::size_t>(tone) - 1];
    const long double expected = std::sin(2.0L * std::numbers::pi_v<long double> * phase) *
        source.peak_amplitude * profile.output_gain * gain;
    std::array<float, 1> output{};
    process(engine, 1, output);
    largest_audio_error = std::max(largest_audio_error,
                                  std::fabs(static_cast<long double>(output[0]) - expected));
    CHECK_NEAR(output[0], expected, 5e-9L);
    ++formula_samples;
}

void hysteresis_and_phase(const RuntimeProfile& profile) {
    for (double rate : rates) {
        for (Manual manual : {upper, lower}) {
            Engine below = prepared(profile, rate), above = prepared(profile, rate);
            flush(below, {position(0.5, manual)});
            flush(above, {position(1.0, manual)});
            process(below, 1024);
            process(above, 1024);
            flush(above, {position(0.5, manual)});
            process(below, 1024);
            process(above, 1024);
            const auto lo = contact(below, manual), hi = contact(above, manual);
            CHECK(lo.position == 0.5 && lo.target == 0.5);
            CHECK(hi.position == 0.5 && hi.target == 0.5);
            for (std::size_t index = 0; index < 9; ++index) {
                CHECK(lo.closed[index] == (index < 4));
                CHECK(hi.closed[index] == (index < 5));
            }
            CHECK(below.key_down(manual, 60) && above.key_down(manual, 60));
            CHECK(below.active_key_count(manual) == 1);
            same_phases(below, above); // Different gestures never restart a source.
            const Event draw{0, EventType::Drawbar, manual, 4, 8.0};
            flush(below, {draw});
            flush(above, {draw});
            std::array<float, 64> silent{};
            process(below, 64, silent);
            CHECK(std::all_of(silent.begin(), silent.end(), [](float x) { return x == 0.0F; }));
            for (std::size_t i = 0; i < silent.size(); ++i) {
                check_isolated_sample(above, profile, 4, profile.drawbar_gains[8]);
            }
            same_phases(below, above);
        }
    }
}

void partial_percussion_and_full_press(const RuntimeProfile& profile) {
    for (double rate : rates) {
        Engine engine = prepared(profile, rate);
        flush(engine, {percussion(), position(0.5)});
        process(engine, 1024);
        CHECK(contact(engine).closed[3]);
        CHECK(!contact(engine).closed[8]);
        CHECK(engine.percussion_diagnostics().readiness == 1.0);
        CHECK(!engine.percussion_diagnostics().routed_detector);
        for (std::size_t i = 0; i < 128; ++i) {
            check_isolated_sample(engine, profile, 3, 1.0);
            CHECK(engine.percussion_diagnostics().readiness == 1.0);
        }
        const Engine before = engine;
        flush(engine, {note_on()}); // Positive held Boolean must not suppress full travel.
        CHECK(contact(engine).position == 0.5);
        CHECK(contact(engine).target == 1.0);
        CHECK(contact(engine).closed == contact(before).closed);
        CHECK(engine.frame_clock() == before.frame_clock());
        CHECK(engine.percussion_diagnostics().readiness == before.percussion_diagnostics().readiness);
        same_phases(engine, before);
        const auto detector_frame = static_cast<std::uint32_t>(std::ceil(0.42 * 0.008 * rate));
        process(engine, detector_frame - 1);
        CHECK(!contact(engine).closed[8]);
        CHECK(engine.percussion_diagnostics().readiness == 1.0);
        process(engine, 1);
        CHECK(contact(engine).closed[8]);
        CHECK(engine.percussion_diagnostics().readiness == 1.0);
        process(engine, 101);
        CHECK_NEAR(engine.percussion_diagnostics().readiness,
                   std::exp(-101.0L / (static_cast<long double>(rate) * 1.551L)), 3e-14L);
    }
}

void duplicate_reversal_and_zero_time(const RuntimeProfile& profile) {
    for (double rate : rates) {
        Engine repeated = prepared(profile, rate), once = repeated;
        flush(repeated, {percussion(), position(0.8)});
        flush(once, {percussion(), position(0.8)});
        for (std::uint32_t frame = 0; frame < 257; ++frame) {
            if (frame % 7 == 0) {
                const Engine before = repeated;
                flush(repeated, {position(0.8)});
                same_state(repeated, before);
            }
            process(repeated, 1);
            process(once, 1);
        }
        same_future(repeated, once);
        const auto old = contact(repeated);
        const Engine before = repeated;
        flush(repeated, {position(0.2), position(0.9)});
        CHECK(contact(repeated).position == old.position);
        CHECK(contact(repeated).closed == old.closed);
        CHECK(contact(repeated).target == 0.9);
        CHECK(repeated.frame_clock() == before.frame_clock());
        CHECK(repeated.percussion_diagnostics().readiness == before.percussion_diagnostics().readiness);
        same_phases(repeated, before);
        process(repeated, 1);
        CHECK_NEAR(contact(repeated).position,
                   std::min(0.9L, static_cast<long double>(old.position) + 1.0L / (rate * 0.008L)),
                   8e-16L);
        const auto start_release = contact(repeated);
        flush(repeated, {{0, EventType::NoteOff, upper, 60, 0.0}});
        CHECK(!repeated.key_down(upper, 60));
        CHECK(contact(repeated).closed == start_release.closed);
        CHECK(contact(repeated).position == start_release.position);
        process(repeated, 1);
        CHECK_NEAR(contact(repeated).position,
                   std::max(0.0L, static_cast<long double>(start_release.position) -
                            1.0L / (rate * 0.012L)), 8e-16L);
        const Engine prior_panic = repeated;
        flush(repeated, {{0, EventType::AllNotesOff, upper, 0, 0.0}});
        CHECK(contact(repeated) == ContactKeySnapshot{});
        CHECK(repeated.percussion_diagnostics().readiness == prior_panic.percussion_diagnostics().readiness);
        CHECK(repeated.frame_clock() == prior_panic.frame_clock());
        same_phases(repeated, prior_panic);
    }
}

void atomic_rejection_and_ideal_endpoints(const RuntimeProfile& profile) {
    const std::array invalid{
        position(-0.01), position(std::nextafter(1.0, 2.0)),
        position(std::numeric_limits<double>::quiet_NaN()),
        position(std::numeric_limits<double>::infinity()), position(0.5, upper, 35),
        position(0.5, lower, 97), position(0.5, static_cast<Manual>(255))};
    for (double rate : rates) {
        for (bool nominal : {false, true}) {
            Engine base = prepared(profile, rate, nominal);
            flush(base, {percussion(), note_on()});
            process(base, 1001);
            for (Event bad : invalid) {
                Engine subject = base;
                std::array<float, 2> output{0.125F, -0.25F};
                bad.offset = 1;
                const std::array events{position(0.0), bad};
                const auto result = subject.process(2, output, events);
                CHECK(result.status == Status::InvalidEvent && result.events_consumed == 0);
                CHECK(output[0] == 0.125F && output[1] == -0.25F);
                same_future(subject, base);
                ++rejected_calls;
            }
            if (!nominal) {
                for (double target : {std::nextafter(0.0, 1.0), 0.5, std::nextafter(1.0, 0.0)}) {
                    Engine subject = base;
                    const std::array events{position(target)};
                    const auto result = subject.process(0, {}, events);
                    CHECK(result.status == Status::InvalidEvent && result.events_consumed == 0);
                    same_future(subject, base);
                    ++rejected_calls;
                }
                Engine endpoint = base, notes = base;
                flush(endpoint, {position(0.0), position(1.0, lower, 96)});
                flush(notes, {{0, EventType::NoteOff, upper, 60, 0.0}, note_on(lower, 96)});
                same_future(endpoint, notes);
                flush(endpoint, {position(-0.0, lower, 96)});
                CHECK(contact(endpoint, lower, 96) == ContactKeySnapshot{});
            }
        }
    }
}

[[nodiscard]] std::vector<float> render_timeline(Engine& engine, std::uint32_t block) {
    const std::array<Event, 17> events{{
        {0, EventType::Percussion, upper, 0, 1},
        {0, EventType::Drawbar, lower, 2, 4},
        {0, EventType::KeyPosition, upper, 60, 0.5},
        {100, EventType::KeyPosition, lower, 48, 0.3},
        {250, EventType::KeyPosition, upper, 60, 0.5},
        {600, EventType::NoteOn, upper, 60, 100},
        {1000, EventType::KeyPosition, upper, 60, 0.65},
        {1100, EventType::KeyPosition, upper, 60, 0.9},
        {1500, EventType::KeyPosition, upper, 60, 0.2},
        {1550, EventType::KeyPosition, upper, 60, 0.75},
        {1700, EventType::NoteOff, lower, 48, 0},
        {1900, EventType::KeyPosition, upper, 60, 0.5},
        {2400, EventType::NoteOff, upper, 60, 0},
        {2400, EventType::KeyPosition, upper, 60, 0.8},
        {2700, EventType::AllNotesOff, upper, 0, 0},
        {2750, EventType::KeyPosition, lower, 48, 1},
        {3000, EventType::KeyPosition, lower, 48, 0.1}}};
    std::vector<float> output(4096);
    std::size_t cursor = 0;
    for (std::uint32_t start = 0; start < 4096;) {
        const auto length = std::min(block, 4096U - start);
        std::vector<Event> local;
        while (cursor < events.size() && events[cursor].offset < start + length) {
            local.push_back(events[cursor++]);
            local.back().offset -= start;
        }
        process(engine, length, std::span<float>(output).subspan(start, length), local);
        start += length;
    }
    return output;
}
void partition_invariance(const RuntimeProfile& profile) {
    for (double rate : rates) {
        Engine reference = prepared(profile, rate);
        const auto audio = render_timeline(reference, 1);
        for (std::uint32_t block : {31U, 257U, 1024U}) {
            Engine candidate = prepared(profile, rate);
            const auto rendered = render_timeline(candidate, block);
            same_audio(audio, rendered);
            same_state(reference, candidate);
        }
    }
}
} // namespace

int main() {
    const auto profile = load_test_profile();
    hysteresis_and_phase(profile);
    partial_percussion_and_full_press(profile);
    duplicate_reversal_and_zero_time(profile);
    atomic_rejection_and_ideal_endpoints(profile);
    partition_invariance(profile);
    std::cout << "partial-key acceptance: " << state_pairs << " exact state pairs, "
              << audio_pairs << " exact audio samples, " << formula_samples
              << " isolated current-phase samples, " << rejected_calls
              << " rejected calls; max audio error=" << largest_audio_error << '\n';
}
