#include "TestSupport.h"
#include "RotaryRendererInternal.h"

#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <limits>
#include <memory>
#include <span>
#include <type_traits>
#include <vector>

// Independent whole-process experiments from A11's transaction review. The
// closed-form delay/support oracle and untouched control renderer never replay
// or otherwise model the production undo loop. Every large value is heap owned.
namespace transaction_test {

using namespace hammond::rotary;
constexpr double kRate = 48000.0;
constexpr double kDistance = 3.0 / 128.0;
constexpr std::size_t kCapacity = 10;
constexpr std::size_t kPreload = 40;
constexpr std::size_t kRequest = 37;
constexpr std::size_t kSuffix = 31;
constexpr std::size_t kTotal = kPreload + kRequest + kSuffix;
constexpr std::size_t kGuard = 7;
constexpr long double kOracleTolerance = 1.0e-11L;

std::uint64_t bits(double value) { return std::bit_cast<std::uint64_t>(value); }

// A canonical field stream, not an object representation: floating values are
// saved as bits, integer/enumerator fields as values, and padding is excluded.
struct Fields {
    std::vector<std::uint64_t> words{};

    void add(double value) { words.push_back(bits(value)); }
    template <typename T> requires std::is_integral_v<T>
    void add(T value) { words.push_back(static_cast<std::uint64_t>(value)); }
    template <typename T> requires std::is_enum_v<T>
    void add(T value) { words.push_back(static_cast<std::uint64_t>(value)); }
    template <typename T, std::size_t N>
    void add(const std::array<T, N>& values) { for (const auto& value : values) add(value); }
    void add(const Vec3& value) { add(value.x); add(value.y); add(value.z); }
    void add(const MotionProfile& value) {
        add(value.slow_rad_s); add(value.fast_rad_s); add(value.tau_up_s);
        add(value.tau_down_s); add(value.direction);
    }
    void add(const MotionState& value) {
        add(value.phase_rad); add(value.turns); add(value.speed_rad_s);
    }
    void add(const MotionSegment& value) {
        add(value.anchor_frame); add(value.initial); add(value.target_rad_s);
        add(value.tau_s); add(value.direction);
    }
    void add(const RotorProfile& value) {
        add(value.origin_m); add(value.radius_m); add(value.motion);
        add(value.initial_phase_rad); add(value.initial_speed_rad_s); add(value.initial_command);
    }
    void add(const MicrophoneProfile& value) { add(value.position_m); }
    void add(const Profile& value) {
        add(value.rotors); add(value.microphones); add(value.sound_speed_m_s);
        add(value.reference_distance_m);
    }
    void add(const ProcessSpec& value) { add(value.sample_rate); add(value.max_block_frames); }
    void add(const PathBounds& value) {
        add(value.min_distance_m); add(value.max_distance_m); add(value.max_tangential_mach);
    }
    void add(const SamplePosition& value) { add(value.frame); add(value.fraction); }
    void add(const PathResult& value) {
        add(value.delay_s); add(value.distance_m); add(value.emission_phase_rad);
        add(value.radial_speed_m_s); add(value.frequency_ratio); add(value.distance_gain);
        add(value.residual_s); add(value.iterations);
    }
    void add(const RendererDiagnostics& value) {
        add(value.has_rendered_sample); add(value.last_input_frame); add(value.last_observation);
        add(value.last_paths); add(value.last_emissions); add(value.max_solver_residual_s);
        add(value.max_solver_iterations);
    }
    void add(const RendererState& value) {
        add(value.prepared); add(value.sample_rate); add(value.frame); add(value.max_frame);
        add(value.motion); add(value.epoch_initial); add(value.commands); add(value.segments);
    }
    void owner_projection(const RotaryMotion& value) {
        add(value.prepared()); add(value.sample_rate()); add(value.frame()); add(value.max_frame());
        add(value.profile()); add(value.state()); add(value.epoch_initial_state());
        add(value.command()); add(value.segment());
    }
    void owner(const RotaryMotion& value) {
        owner_projection(value);
        // RotaryMotion has no test friend. Reset a SMALL copy to expose its
        // otherwise private original seed/command as well as its current state.
        auto original = value;
        const auto status = original.reset();
        CHECK(status == Status::Ok);
        add(status);
        owner_projection(original);
    }
};

bool same_segment(const MotionSegment& a, const MotionSegment& b) {
    return a.anchor_frame == b.anchor_frame && bits(a.initial.phase_rad) == bits(b.initial.phase_rad)
        && a.initial.turns == b.initial.turns && bits(a.initial.speed_rad_s) == bits(b.initial.speed_rad_s)
        && bits(a.target_rad_s) == bits(b.target_rad_s) && bits(a.tau_s) == bits(b.tau_s)
        && a.direction == b.direction;
}

double marker(std::size_t index, std::size_t lane) {
    const auto code = UINT64_C(0x4130000000000000) + static_cast<std::uint64_t>(index) * 131U
        + static_cast<std::uint64_t>(lane) * 1048576U;
    return std::bit_cast<double>(code | ((index % 2 == 0) ? UINT64_C(0) : UINT64_C(0x8000000000000000)));
}

detail::RotaryUndoRecord journal_marker(std::size_t index) {
    detail::RotaryUndoRecord result;
    result.slot = kMaxHistoryFrames + index + 1;
    for (std::size_t rotor = 0; rotor < kRotorCount; ++rotor) {
        result.samples[rotor] = marker(index, 8 + rotor);
        result.segments[rotor] = {
            std::numeric_limits<std::uint64_t>::max() - static_cast<std::uint64_t>(index),
            {marker(index, 10 + rotor), -97, marker(index, 12 + rotor)},
            marker(index, 14 + rotor), marker(index, 16 + rotor), -7};
    }
    return result;
}

struct Progress {
    std::size_t completed_samples{0};
    std::size_t journal_records{0};
    std::array<std::size_t, kCapacity> slot_visits{};
    long double maximum_oracle_error{0.0L};
};

} // namespace transaction_test

namespace hammond::rotary::detail {

// Executable-local friend only: there is no shipping hook, callback or switch.
struct RotaryRendererTestAccess {
    static std::unique_ptr<transaction_test::Fields> snapshot(const RotaryRenderer& renderer) {
        using transaction_test::Fields;
        CHECK(renderer.storage_ != nullptr);
        auto result = std::make_unique<Fields>();
        result->words.reserve(8 * kRotorCount * kMaxHistoryFrames + 1024);
        result->add(renderer.prepared()); result->add(renderer.profile()); result->add(renderer.spec());
        result->add(renderer.state()); result->add(renderer.diagnostics()); result->add(renderer.path_bounds());
        result->add(renderer.history_capacity_frames()); result->add(renderer.tail_flush_frames());
        result->add(renderer.algorithmic_latency_frames());
        const auto& storage = *renderer.storage_;
        result->add(storage.original_profile); result->add(storage.spec);
        result->add(storage.capacity_frames); result->add(storage.flush_frames);
        result->add(storage.diagnostics);
        for (const auto& owner : storage.motion) result->owner(owner);
        for (const auto& path : storage.paths) {
            result->add(path.prepared()); result->add(path.bounds());
        }
        for (const auto& waveform : storage.waveform) {
            result->add(waveform.sample_rate_); result->add(waveform.capacity_frames_);
            result->add(waveform.next_frame_); result->add(waveform.max_frame_); result->add(waveform.prepared_);
            result->add(waveform.oldest_frame());
            // ALL physical slots, including the 16,374 inactive backing slots.
            result->add(waveform.samples_);
        }
        for (const auto& history : storage.motion_history) {
            result->add(history.profile_); result->add(history.epoch_initial_);
            result->add(history.sample_rate_); result->add(history.capacity_frames_);
            result->add(history.next_frame_); result->add(history.max_frame_); result->add(history.prepared_);
            result->add(history.oldest_frame()); result->add(history.segments_);
        }
        return result;
    }

    static double replace_sample(RotaryRenderer& renderer, std::uint64_t frame, double replacement) {
        auto& history = renderer.storage_->waveform[0];
        CHECK(frame >= history.oldest_frame() && frame < history.next_frame_);
        auto& sample = history.samples_[static_cast<std::size_t>(frame % history.capacity_frames_)];
        const double saved = sample;
        sample = replacement;
        return saved;
    }

    static std::uint64_t replace_second_motion_limit(RotaryRenderer& renderer, std::uint64_t replacement) {
        auto& limit = renderer.storage_->motion_history[1].max_frame_;
        const auto saved = limit;
        limit = replacement;
        return saved;
    }

    static void seed_work(RotaryRenderer& renderer) {
        auto& storage = *renderer.storage_;
        for (std::size_t index = 0; index < kMaxBlockFrames; ++index) {
            for (std::size_t channel = 0; channel < kMicrophoneCount; ++channel) {
                storage.output[channel][index] = transaction_test::marker(index, channel);
            }
            storage.undo[index] = transaction_test::journal_marker(index);
        }
    }

    template <typename SampleOracle, typename SegmentOracle, typename OutputOracle>
    static transaction_test::Progress progress(const RotaryRenderer& renderer,
        std::size_t expected_completed, std::size_t expected_records,
        SampleOracle sample_at, SegmentOracle segment_at, OutputOracle output_at) {
        using namespace transaction_test;
        const auto& storage = *renderer.storage_;
        Progress result;
        for (std::size_t index = 0; index < kMaxBlockFrames; ++index) {
            for (std::size_t channel = 0; channel < kMicrophoneCount; ++channel) {
                const auto sample = storage.output[channel][index];
                if (index < expected_completed) {
                    CHECK(bits(sample) != bits(marker(index, channel)));
                    const auto error = std::abs(static_cast<long double>(sample) - output_at(kPreload + index));
                    CHECK(error <= kOracleTolerance);
                    result.maximum_oracle_error = std::max(result.maximum_oracle_error, error);
                    if (channel == 0) ++result.completed_samples;
                } else {
                    CHECK(bits(sample) == bits(marker(index, channel)));
                }
            }
            const auto& record = storage.undo[index];
            if (index < expected_records) {
                const auto frame = kPreload + index;
                CHECK(record.slot == frame % kCapacity);
                ++result.journal_records;
                ++result.slot_visits[record.slot];
                // Each overwritten slot held interval n-H. This direct logical
                // timeline calculation is not a replay of any rollback code.
                for (std::size_t rotor = 0; rotor < kRotorCount; ++rotor) {
                    CHECK(bits(record.samples[rotor]) == bits(sample_at(rotor, frame - kCapacity)));
                    CHECK(same_segment(record.segments[rotor], segment_at(rotor, frame - kCapacity)));
                }
            } else {
                const auto untouched = journal_marker(index);
                CHECK(record.slot == untouched.slot);
                for (std::size_t rotor = 0; rotor < kRotorCount; ++rotor) {
                    CHECK(bits(record.samples[rotor]) == bits(untouched.samples[rotor]));
                    CHECK(same_segment(record.segments[rotor], untouched.segments[rotor]));
                }
            }
        }
        CHECK(result.completed_samples == expected_completed && result.journal_records == expected_records);
        return result;
    }
};

} // namespace hammond::rotary::detail

namespace transaction_test {

using Access = detail::RotaryRendererTestAccess;
std::size_t snapshot_comparisons = 0;
std::size_t snapshot_field_words = 0;
std::size_t compared_field_words = 0;
std::size_t compared_output_values = 0;

void same_fields(const Fields& expected, const Fields& actual) {
    CHECK(expected.words.size() == actual.words.size());
    for (std::size_t index = 0; index < expected.words.size(); ++index) {
        if (expected.words[index] != actual.words[index]) {
            std::cerr << "persistent field " << index << " differs\n";
            CHECK(expected.words[index] == actual.words[index]);
        }
    }
    snapshot_field_words = actual.words.size();
    compared_field_words += actual.words.size();
    ++snapshot_comparisons;
}

void unchanged(const RotaryRenderer& renderer, const Fields& before) {
    const auto after = Access::snapshot(renderer);
    same_fields(before, *after);
}

void same_renderers(const RotaryRenderer& subject, const RotaryRenderer& control) {
    const auto expected = Access::snapshot(control);
    unchanged(subject, *expected);
}

void one_injected_field(const Fields& pristine, const Fields& injected) {
    CHECK(pristine.words.size() == injected.words.size());
    std::size_t changes = 0;
    for (std::size_t index = 0; index < pristine.words.size(); ++index) {
        if (pristine.words[index] != injected.words[index]) ++changes;
    }
    CHECK(changes == 1);
}

void same_values(std::span<const double> expected, std::span<const double> actual) {
    CHECK(expected.size() == actual.size());
    for (std::size_t index = 0; index < expected.size(); ++index) CHECK(bits(expected[index]) == bits(actual[index]));
    compared_output_values += expected.size();
}

struct GuardedOutput {
    std::size_t frames;
    std::vector<double> values;
    explicit GuardedOutput(std::size_t count) : frames(count), values(2 * count + 3 * kGuard) {
        for (std::size_t index = 0; index < values.size(); ++index) values[index] = marker(index, 20);
    }
    std::span<double> left() { return std::span(values).subspan(kGuard, frames); }
    std::span<double> right() { return std::span(values).subspan(2 * kGuard + frames, frames); }
    void guards_unchanged() const {
        for (std::size_t index = 0; index < values.size(); ++index) {
            const bool output = (index >= kGuard && index < kGuard + frames)
                || (index >= 2 * kGuard + frames && index < 2 * kGuard + 2 * frames);
            if (!output) CHECK(bits(values[index]) == bits(marker(index, 20)));
        }
    }
};

Profile profile() {
    Profile result;
    result.sound_speed_m_s = 300.0;
    result.reference_distance_m = kDistance;
    result.microphones[0].position_m = {kDistance, 0.0, -0.0};
    result.microphones[1].position_m = {kDistance, 0.0, -0.0};
    result.rotors[0] = {{0.0, -0.0, 0.0}, 0.0, {3.0, 90.0, 0.007, 0.013, 1},
                        6.25, 47.0, SpeedCommand::Chorale};
    result.rotors[1] = {{0.0, -0.0, 0.0}, 0.0, {4.0, 75.0, 0.011, 0.019, -1},
                        0.035, 61.0, SpeedCommand::Chorale};
    return result;
}

double signal(std::size_t frame, std::uint32_t multiplier, std::uint32_t shift) {
    const auto code = (static_cast<std::uint32_t>(frame) * multiplier + shift) % 257U;
    if (code == 128U) return frame % 2 == 0 ? 0.0 : -0.0;
    return static_cast<double>(static_cast<int>(code) - 128) / 256.0;
}

struct Fixture {
    RotaryRenderer subject{}, control{};
    Profile configuration{profile()};
    std::array<std::vector<double>, kRotorCount> truth{};
    std::vector<double> overlapping{};
    std::array<std::vector<MotionSegment>, kRotorCount> logical_segments{};
    std::array<RotaryMotion, kRotorCount> logical_final{};
    std::vector<CommandEvent> preload_events{
        {3, RotorId::Horn, SpeedCommand::Tremolo}, {11, RotorId::Drum, SpeedCommand::Tremolo},
        {17, RotorId::Horn, SpeedCommand::Chorale}, {23, RotorId::Drum, SpeedCommand::Chorale},
        {29, RotorId::Horn, SpeedCommand::Tremolo}, {37, RotorId::Drum, SpeedCommand::Tremolo},
        {40, RotorId::Horn, SpeedCommand::Chorale}};
    std::vector<CommandEvent> request_events{
        {0, RotorId::Horn, SpeedCommand::Tremolo}, {0, RotorId::Drum, SpeedCommand::Chorale},
        {0, RotorId::Horn, SpeedCommand::Chorale}, {0, RotorId::Horn, SpeedCommand::Tremolo},
        {1, RotorId::Drum, SpeedCommand::Tremolo}, {1, RotorId::Drum, SpeedCommand::Tremolo},
        {2, RotorId::Horn, SpeedCommand::Chorale}, {2, RotorId::Drum, SpeedCommand::Chorale},
        {3, RotorId::Horn, SpeedCommand::Tremolo}, {12, RotorId::Drum, SpeedCommand::Tremolo},
        {20, RotorId::Horn, SpeedCommand::Chorale}, {22, RotorId::Drum, SpeedCommand::Chorale},
        {23, RotorId::Horn, SpeedCommand::Tremolo}, {37, RotorId::Drum, SpeedCommand::Tremolo},
        {37, RotorId::Horn, SpeedCommand::Chorale}, {37, RotorId::Horn, SpeedCommand::Tremolo}};
    bool partial_alias;

    explicit Fixture(bool alias) : partial_alias(alias) {
        for (std::size_t rotor = 0; rotor < kRotorCount; ++rotor) {
            truth[rotor].resize(kTotal);
            for (std::size_t frame = 0; frame < kTotal; ++frame) {
                truth[rotor][frame] = signal(frame, rotor == 0 ? 37U : 71U, rotor == 0 ? 9U : 23U);
            }
        }
        if (partial_alias) {
            overlapping.resize(kRequest + 1);
            for (std::size_t index = 0; index < overlapping.size(); ++index) {
                overlapping[index] = signal(kPreload + index, 53U, 17U);
            }
            for (std::size_t index = 0; index < kRequest; ++index) {
                truth[0][kPreload + index] = overlapping[index];
                truth[1][kPreload + index] = overlapping[index + 1];
            }
        }
        CHECK(subject.prepare(configuration, {kRate, 64}) == Status::Ok);
        CHECK(control.prepare(configuration, {kRate, 64}) == Status::Ok);
        CHECK(subject.history_capacity_frames() == kCapacity && subject.tail_flush_frames() == 8);
        CHECK(kRate * kDistance / configuration.sound_speed_m_s == 3.75);
        for (std::size_t rotor = 0; rotor < kRotorCount; ++rotor) {
            const auto& seed = configuration.rotors[rotor];
            CHECK(logical_final[rotor].prepare(seed.motion, seed.initial_phase_rad,
                seed.initial_speed_rad_s, seed.initial_command, kRate) == Status::Ok);
            logical_segments[rotor].resize(kPreload + kRequest + 1);
        }
        // Motion oracle owns just the original command segments. No histories,
        // journals, renderer process calls, interpolation or rollback are used.
        for (std::size_t frame = 0; frame <= kPreload + kRequest; ++frame) {
            for (auto& owner : logical_final) CHECK(owner.advance_to(frame) == Status::Ok);
            for (const auto& event : preload_events) {
                if (event.offset == frame) {
                    CHECK(logical_final[static_cast<std::size_t>(event.rotor)].apply_command(frame, event.command) == Status::Ok);
                }
            }
            for (const auto& event : request_events) {
                if (kPreload + event.offset == frame) {
                    CHECK(logical_final[static_cast<std::size_t>(event.rotor)].apply_command(frame, event.command) == Status::Ok);
                }
            }
            for (std::size_t rotor = 0; rotor < kRotorCount; ++rotor) logical_segments[rotor][frame] = logical_final[rotor].segment();
        }
        GuardedOutput subject_output(kPreload), control_output(kPreload);
        accepted(subject, input(0, 0, kPreload), input(1, 0, kPreload), subject_output, preload_events);
        accepted(control, input(0, 0, kPreload), input(1, 0, kPreload), control_output, preload_events);
        same_values(control_output.values, subject_output.values);
        same_renderers(subject, control);
        CHECK(subject.state().frame == kPreload);
        CHECK(subject.state().motion[0].turns != 0 && subject.state().motion[1].turns != 0);
        CHECK(subject.diagnostics().has_rendered_sample && subject.diagnostics().last_input_frame == kPreload - 1);
    }

    std::span<const double> input(std::size_t rotor, std::size_t first, std::size_t count) const {
        return std::span(truth[rotor]).subspan(first, count);
    }
    std::span<const double> request_input(std::size_t rotor) const {
        if (partial_alias) return std::span(overlapping).subspan(rotor, kRequest);
        return input(rotor, kPreload, kRequest);
    }
    long double output_at(std::size_t frame) const {
        // observation=n-2, delay=3.75, emission=(n-6)+1/4;
        // supports n-7..n-4 have exact weights {-7,105,35,-5}/128.
        constexpr std::array<long double, 4> weights{-7.0L / 128.0L, 105.0L / 128.0L,
                                                     35.0L / 128.0L, -5.0L / 128.0L};
        long double output = 0.0L;
        for (std::size_t rotor = 0; rotor < kRotorCount; ++rotor) {
            long double path = 0.0L;
            for (std::size_t node = 0; node < weights.size(); ++node) path += weights[node] * truth[rotor][frame - 7 + node];
            output += path; // reference distance / path distance is exactly one.
        }
        return output;
    }
    static void accepted(RotaryRenderer& renderer, std::span<const double> horn,
                         std::span<const double> drum, GuardedOutput& output,
                         std::span<const CommandEvent> events = {}) {
        const auto result = renderer.process(horn, drum, output.left(), output.right(), events);
        CHECK(result.status == Status::Ok && result.events_consumed == events.size());
        CHECK(result.max_solver_iterations > 0 && result.max_solver_iterations <= kMaxSolverIterations);
        CHECK(result.max_solver_residual_s <= kMaxSolverResidualSeconds);
        output.guards_unchanged();
    }
    void accepted_continuation() {
        GuardedOutput subject_output(kRequest), control_output(kRequest);
        accepted(subject, request_input(0), request_input(1), subject_output, request_events);
        accepted(control, input(0, kPreload, kRequest), input(1, kPreload, kRequest), control_output, request_events);
        same_values(control_output.values, subject_output.values);
        same_renderers(subject, control);
        for (std::size_t rotor = 0; rotor < kRotorCount; ++rotor) {
            CHECK(same_segment(subject.state().segments[rotor], logical_final[rotor].segment()));
            CHECK(subject.state().commands[rotor] == logical_final[rotor].command());
            CHECK(subject.state().segments[rotor].anchor_frame == kPreload + kRequest);
        }
        // More than two additional H-lengths, with short calls that cannot rely
        // on the rejected call's leftover output/journal work being cleared.
        constexpr std::array<std::size_t, 4> partitions{1, 9, 11, 10};
        const std::array<CommandEvent, 3> next_zero{{{0, RotorId::Horn, SpeedCommand::Chorale},
            {0, RotorId::Drum, SpeedCommand::Chorale}, {0, RotorId::Horn, SpeedCommand::Tremolo}}};
        std::size_t frame = kPreload + kRequest;
        for (const auto count : partitions) {
            GuardedOutput subject_suffix(count), control_suffix(count);
            const std::span<const CommandEvent> events = frame == kPreload + kRequest
                ? std::span<const CommandEvent>(next_zero) : std::span<const CommandEvent>{};
            accepted(subject, input(0, frame, count), input(1, frame, count), subject_suffix, events);
            accepted(control, input(0, frame, count), input(1, frame, count), control_suffix, events);
            same_values(control_suffix.values, subject_suffix.values);
            same_renderers(subject, control);
            frame += count;
        }
        CHECK(frame == kTotal && subject.state().frame == kTotal && kSuffix > 2 * kCapacity);
    }
};

struct ExperimentResult {
    const char* name;
    const char* alias;
    ProcessResult rejected{};
    Progress progress{};
    std::size_t events_before_failure{0};
};

ExperimentResult experiment(bool partial_frame) {
    auto fixture = std::make_unique<Fixture>(partial_frame);
    const auto pristine = Access::snapshot(fixture->subject);
    GuardedOutput rejected_output(kRequest);
    const auto output_before = rejected_output.values;
    double saved_sample = 0.0;
    std::uint64_t saved_limit = 0;
    if (partial_frame) saved_limit = Access::replace_second_motion_limit(fixture->subject, 63);
    else saved_sample = Access::replace_sample(fixture->subject, 39, 2.0);
    const auto injected = Access::snapshot(fixture->subject);
    one_injected_field(*pristine, *injected);
    Access::seed_work(fixture->subject);

    const auto result = fixture->subject.process(fixture->request_input(0), fixture->request_input(1),
        rejected_output.left(), rejected_output.right(), fixture->request_events);
    CHECK(result.status == (partial_frame ? Status::TimelineOverflow : Status::InvalidBuffer));
    CHECK(result.events_consumed == 0);
    CHECK(result.max_solver_iterations > 0 && result.max_solver_iterations <= kMaxSolverIterations);
    CHECK(result.max_solver_residual_s <= kMaxSolverResidualSeconds);
    unchanged(fixture->subject, *injected); // Fault remains part of pre-state.
    same_values(output_before, rejected_output.values); // Includes EVERY guard.
    for (std::size_t rotor = 0; rotor < kRotorCount; ++rotor) {
        const auto actual = fixture->request_input(rotor);
        const auto expected = fixture->input(rotor, kPreload, kRequest);
        for (std::size_t index = 0; index < kRequest; ++index) CHECK(bits(actual[index]) == bits(expected[index]));
    }
    const std::size_t completed = partial_frame ? 23 : 3;
    const std::size_t records = completed + 1;
    const auto observed = Access::progress(fixture->subject, completed, records,
        [&](std::size_t rotor, std::size_t frame) { return fixture->truth[rotor][frame]; },
        [&](std::size_t rotor, std::size_t frame) { return fixture->logical_segments[rotor][frame]; },
        [&](std::size_t frame) { return fixture->output_at(frame); });
    if (partial_frame) {
        CHECK(observed.slot_visits == (std::array<std::size_t, kCapacity>{3, 3, 3, 3, 2, 2, 2, 2, 2, 2}));
        CHECK(observed.journal_records > 2 * kCapacity);
        CHECK(Access::replace_second_motion_limit(fixture->subject, saved_limit) == 63);
    } else {
        // Frame 43 first reads poison frame 39; its current write is slot 3,
        // not poison slot 9. Earlier supports end at frames 36, 37 and 38.
        CHECK(kPreload + completed - 4 == 39 && (kPreload + completed) % kCapacity == 3);
        CHECK(Access::replace_sample(fixture->subject, 39, saved_sample) == 2.0);
    }
    unchanged(fixture->subject, *pristine); // Restore ONLY the injected field.
    unchanged(fixture->control, *pristine);
    fixture->accepted_continuation();
    ExperimentResult report{partial_frame ? "partial_second_motion_append" : "late_poisoned_support",
        partial_frame ? "partial_inputs_one_sample_apart" : "separate_inputs", result, observed, 0};
    for (const auto& event : fixture->request_events) if (event.offset <= completed) ++report.events_before_failure;
    CHECK(report.events_before_failure > 1 && report.events_before_failure < fixture->request_events.size());
    return report;
}

void print_experiment(const ExperimentResult& value) {
    std::cout << "{\"name\":\"" << value.name << "\",\"inputs\":\"" << value.alias
              << "\",\"status\":\"" << status_name(value.rejected.status)
              << "\",\"failure_frame\":" << kPreload + value.progress.completed_samples
              << ",\"completed_samples\":" << value.progress.completed_samples
              << ",\"journal_records\":" << value.progress.journal_records
              << ",\"events_before_failure\":" << value.events_before_failure
              << ",\"events_consumed\":" << value.rejected.events_consumed
              << ",\"solver_iterations_max\":" << value.rejected.max_solver_iterations
              << ",\"solver_residual_max_s\":" << value.rejected.max_solver_residual_s
              << ",\"scratch_oracle_max_error\":" << value.progress.maximum_oracle_error
              << ",\"slot_visits\":[";
    for (std::size_t slot = 0; slot < value.progress.slot_visits.size(); ++slot) {
        if (slot != 0) std::cout << ',';
        std::cout << value.progress.slot_visits[slot];
    }
    std::cout << "],\"accepted_continuation_frames\":" << kRequest + kSuffix << '}';
}

} // namespace transaction_test

int main() {
    using namespace transaction_test;
    CHECK(bits(0.0) != bits(-0.0));
    const auto poison = experiment(false);
    const auto partial = experiment(true);
    std::cout << std::setprecision(17) << "{\"experiments\":[";
    print_experiment(poison);
    std::cout << ',';
    print_experiment(partial);
    std::cout << "],\"rate\":48000,\"capacity\":10,\"preload_frames\":40,\"request_frames\":37"
              << ",\"snapshot_comparisons\":" << snapshot_comparisons
              << ",\"snapshot_field_words\":" << snapshot_field_words
              << ",\"compared_field_words\":" << compared_field_words
              << ",\"waveform_slots_per_snapshot\":" << kRotorCount * kMaxHistoryFrames
              << ",\"motion_slots_per_snapshot\":" << kRotorCount * kMaxHistoryFrames
              << ",\"compared_output_values_with_guards\":" << compared_output_values
              << ",\"storage_bytes\":" << sizeof(detail::RotaryRendererStorage)
              << ",\"motion_segment_bytes\":" << sizeof(MotionSegment)
              << ",\"result\":\"pass\"}\n";
}
