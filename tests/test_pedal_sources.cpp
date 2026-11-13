#include "TestSupport.h"
#include "hammond/PedalRouting.h"
#include "hammond/TonewheelBank.h"

#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <limits>
#include <optional>
#include <span>
#include <vector>

namespace {
using hammond::PedalBusFrame;
using hammond::PedalBusKernel;
using hammond::PedalContactEdit;
using hammond::PedalContactStates;
using hammond::PedalId;
using hammond::PedalSourceFrame;
using hammond::PedalWeights;
using hammond::RuntimeProfile;
using hammond::Status;
using hammond::ToneId;
using hammond::TonewheelBank;

constexpr std::array<double, 3> kRates{44100.0, 48000.0, 96000.0};
constexpr std::uint64_t kSeed = 0x6af02bd185cc3907ULL;
constexpr std::uint32_t kFrames = 2053;

// Frozen before execution: the fixture has at most ten nonzero pedal terms
// and three manual terms, each of magnitude <=1. Two evaluations (separate
// buses/manual versus one source-indexed sum) need fewer than 64 nontrivial
// multiply/add roundings with absolute term sum <7. 512*epsilon bounds both
// evaluation errors, also where long double has only binary64 precision.
constexpr long double kCoherenceTolerance =
    512.0L * std::numeric_limits<double>::epsilon();

struct Branch {
    PedalId pedal;
    std::uint8_t contact;
    std::optional<ToneId> source;
    std::size_t bus;
    double weight;
};

// Explicit selected cells from retained review-a-pedal.csv, corroborated by
// review-b-pedal.csv. These are not generated from the production map formula.
// The two source-13 branches of pedal 1 remain separate, and pedal 13 also
// shares source 13. Pedal 8/contact 1 remains an independently held null.
constexpr std::array<Branch, 10> kBranches{{
    {{1}, 0, ToneId{1}, 0, 0.5},
    {{1}, 1, ToneId{13}, 0, 0.25},
    {{1}, 2, ToneId{13}, 1, -0.5},
    {{8}, 1, std::nullopt, 0, 0.75},
    {{8}, 4, ToneId{39}, 2, 0.5},
    {{13}, 0, ToneId{13}, 0, 0.625},
    {{13}, 1, ToneId{32}, 0, -0.125},
    {{13}, 2, ToneId{25}, 1, 0.25},
    {{25}, 6, ToneId{65}, 3, -0.375},
    {{25}, 7, ToneId{68}, 3, 0.125},
}};

struct ManualBranch { ToneId source; double weight; };
// A simple declared manual reference, not the Engine's complete manual mixer.
// These sources are checked against the nominal fundamental routes below.
constexpr std::array<ManualBranch, 3> kManual{{{13, 0.75}, {25, 0.25}, {68, 0.125}}};

struct Observations {
    std::uint64_t source_frames{0};
    std::uint64_t phase_values{0};
    std::uint64_t coherent_frames{0};
    std::uint64_t nonzero_frames{0};
    std::uint64_t discarded_frames{0};
    std::uint64_t zero_time_edits{0};
    std::uint64_t rate_changes{0};
    std::uint64_t partition_runs{0};
    long double maximum_error{0.0L};
};

template <std::size_t N>
void same_bits(const std::array<double, N>& actual,
               const std::array<double, N>& expected) {
    for (std::size_t i = 0; i < N; ++i) {
        CHECK(std::bit_cast<std::uint64_t>(actual[i]) ==
              std::bit_cast<std::uint64_t>(expected[i]));
    }
}

PedalSourceFrame phases(const TonewheelBank& bank) {
    PedalSourceFrame result{};
    for (std::size_t i = 0; i < result.size(); ++i) {
        CHECK(bank.phase_turns(static_cast<ToneId>(i + 1), result[i]));
    }
    return result;
}

void same_phases(const TonewheelBank& actual, const TonewheelBank& reference,
                 Observations& observed) {
    same_bits(phases(actual), phases(reference));
    observed.phase_values += hammond::kToneSourceCount;
}

std::size_t contact_position(PedalId pedal, std::uint8_t contact) {
    return (static_cast<std::size_t>(pedal.value) - 1) * 8 + contact;
}

PedalWeights fixture_weights() {
    PedalWeights result{};
    const auto& routes = hammond::compiled_pedal_routes();
    for (const auto& branch : kBranches) {
        const auto position = contact_position(branch.pedal, branch.contact);
        CHECK(routes[position].pedal == branch.pedal);
        CHECK(routes[position].contact == branch.contact);
        CHECK(routes[position].tone == branch.source);
        CHECK(static_cast<std::size_t>(routes[position].bus) == branch.bus);
        result[position] = branch.weight;
    }
    return result;
}

std::array<PedalContactEdit, 200> all_contacts(bool closed) {
    std::array<PedalContactEdit, 200> edits{};
    for (std::size_t i = 0; i < edits.size(); ++i) {
        edits[i] = {{static_cast<std::uint8_t>(i / 8 + 1)},
                    static_cast<std::uint8_t>(i % 8), closed};
    }
    return edits;
}

double manual_reference(const PedalSourceFrame& sources, bool enabled) {
    double result = 0.0;
    if (enabled) {
        for (const auto& branch : kManual) {
            result += branch.weight * sources[static_cast<std::size_t>(branch.source) - 1];
        }
    }
    return result;
}

// This independently collects manual and pedal contributions by source, then
// performs one long-double dot product. It never reads the kernel's routes or
// contact snapshot to determine the expected mathematical sum.
long double combined_reference(const PedalSourceFrame& sources,
                               const PedalContactStates& intended, bool manual_enabled) {
    std::array<long double, hammond::kToneSourceCount> coefficients{};
    if (manual_enabled) {
        for (const auto& branch : kManual) {
            coefficients[static_cast<std::size_t>(branch.source) - 1] += branch.weight;
        }
    }
    for (const auto& branch : kBranches) {
        if (intended[contact_position(branch.pedal, branch.contact)] && branch.source) {
            coefficients[static_cast<std::size_t>(*branch.source) - 1] += branch.weight;
        }
    }
    long double result = 0.0L;
    for (std::size_t i = 0; i < sources.size(); ++i) {
        result += coefficients[i] * static_cast<long double>(sources[i]);
    }
    return result;
}

struct Command {
    std::uint32_t frame;
    bool all;
    PedalContactEdit edit;
};

constexpr std::array<Command, 19> kSchedule{{
    {0, true, {{1}, 0, true}},
    {17, false, {{13}, 1, false}},
    {63, false, {{8}, 4, false}},
    {64, false, {{1}, 1, false}},
    {64, false, {{1}, 1, true}},
    {64, false, {{1}, 1, false}},
    {127, false, {{25}, 6, false}},
    {128, false, {{1}, 2, false}},
    {192, true, {{1}, 0, false}},
    {200, true, {{1}, 0, true}},
    {255, false, {{8}, 1, false}},
    {256, false, {{8}, 1, true}},
    {511, false, {{25}, 7, false}},
    {512, true, {{1}, 0, false}},
    {640, true, {{1}, 0, true}},
    {900, true, {{1}, 0, false}},
    {1024, false, {{13}, 0, true}},
    {1024, false, {{25}, 7, true}},
    {2047, true, {{1}, 0, false}},
}};

struct Sample {
    PedalBusFrame buses{};
    double manual{0.0};
    double combined{0.0};
    bool connected{false};
};

struct Result {
    std::vector<Sample> samples;
    PedalSourceFrame final_phases{};
    PedalContactStates final_contacts{};
    std::uint32_t source_calls{0};
};

void apply_zero_time(const Command& command, PedalBusKernel& pedals,
                     PedalContactStates& intended, const TonewheelBank& sources,
                     Observations& observed) {
    const auto before = phases(sources);
    if (command.all) {
        const auto edits = all_contacts(command.edit.closed);
        CHECK(pedals.apply_contacts(edits) == Status::Ok);
        intended.fill(command.edit.closed);
    } else {
        CHECK(pedals.apply_contacts(std::span{&command.edit, 1}) == Status::Ok);
        intended[contact_position(command.edit.pedal, command.edit.contact)] = command.edit.closed;
    }
    CHECK(pedals.contacts_snapshot() == intended);
    same_bits(phases(sources), before);
    ++observed.zero_time_edits;
}

Result run_schedule(const RuntimeProfile& profile, double initial_rate,
                    std::span<const std::uint32_t> partitions, bool drop_outputs,
                    Observations& observed) {
    CHECK(!partitions.empty());
    TonewheelBank sources, source_only;
    CHECK(sources.prepare(profile, initial_rate, kSeed) == Status::Ok);
    CHECK(source_only.prepare(profile, initial_rate, kSeed) == Status::Ok);
    PedalBusKernel pedals;
    CHECK(pedals.prepare(hammond::compiled_pedal_routes(), fixture_weights()) == Status::Ok);
    PedalContactStates intended{};
    Result result;
    result.samples.resize(kFrames);
    std::size_t next_command = 0;
    std::size_t partition = 0;
    std::uint32_t start = 0;
    same_phases(sources, source_only, observed);

    while (start < kFrames) {
        CHECK(partitions[partition % partitions.size()] != 0);
        const auto count = std::min(partitions[partition % partitions.size()], kFrames - start);
        const auto end = start + count;
        // Events on end belong to the following half-open block. Equal-frame
        // commands retain their input order, including the three edits at 64.
        std::size_t block_end_command = next_command;
        while (block_end_command < kSchedule.size() && kSchedule[block_end_command].frame < end) {
            ++block_end_command;
        }
        for (std::uint32_t frame = start; frame < end; ++frame) {
            while (next_command < block_end_command && kSchedule[next_command].frame == frame) {
                apply_zero_time(kSchedule[next_command], pedals, intended, sources, observed);
                ++next_command;
            }
            if (frame == 64) CHECK(!intended[1]);
            double new_rate = 0.0;
            if (frame == 257) new_rate = 48000.0;
            if (frame == 769) new_rate = 96000.0;
            if (frame == 1280) new_rate = 44100.0;
            if (frame == 1600) new_rate = 48000.0;
            if (new_rate != 0.0) {
                const auto previous_phases = phases(sources);
                const auto previous_pedals = pedals;
                CHECK(sources.reconfigure_sample_rate(new_rate) == Status::Ok);
                CHECK(source_only.reconfigure_sample_rate(new_rate) == Status::Ok);
                same_bits(phases(sources), previous_phases);
                CHECK(pedals == previous_pedals);
                ++observed.rate_changes;
            }

            // Exactly one source evaluation per modeled frame. Both consumers
            // below receive this same const-valued array; neither owns sources.
            PedalSourceFrame shared{}, control{};
            sources.process_frame(shared);
            ++result.source_calls;
            source_only.process_frame(control);
            same_bits(shared, control);
            same_phases(sources, source_only, observed);
            ++observed.source_frames;

            auto& sample = result.samples[frame];
            const bool manual_enabled = !(frame >= 512 && frame < 640);
            sample.manual = manual_reference(shared, manual_enabled);
            sample.connected = !(drop_outputs &&
                ((frame >= 160 && frame < 225) || (frame >= 900 && frame < 1000)));
            if (sample.connected) {
                const auto kernel_before = pedals;
                const auto sources_before = phases(sources);
                CHECK(pedals.render_frame(shared, sample.buses) == Status::Ok);
                CHECK(pedals == kernel_before);
                same_bits(phases(sources), sources_before);
                double pedal_sum = 0.0;
                for (const double bus : sample.buses) pedal_sum += bus;
                sample.combined = sample.manual + pedal_sum;
                const auto expected = combined_reference(shared, intended, manual_enabled);
                const auto error = std::fabs(static_cast<long double>(sample.combined) - expected);
                CHECK_NEAR(sample.combined, expected, kCoherenceTolerance);
                observed.maximum_error = std::max(observed.maximum_error, error);
                ++observed.coherent_frames;
                if (std::fabs(sample.combined) > 0.01) ++observed.nonzero_frames;
                if (frame >= 512 && frame < 640) {
                    CHECK(sample.combined == 0.0);
                    CHECK(sample.buses == PedalBusFrame{});
                }
            } else {
                ++observed.discarded_frames;
            }
            CHECK(pedals.contacts_snapshot() == intended);
        }
        CHECK(next_command == block_end_command);
        start = end;
        ++partition;
    }
    CHECK(next_command == kSchedule.size());
    CHECK(result.source_calls == kFrames);
    result.final_phases = phases(sources);
    result.final_contacts = pedals.contacts_snapshot();
    ++observed.partition_runs;
    return result;
}

void compare_runs(const Result& actual, const Result& reference) {
    CHECK(actual.samples.size() == reference.samples.size());
    CHECK(actual.source_calls == reference.source_calls);
    same_bits(actual.final_phases, reference.final_phases);
    CHECK(actual.final_contacts == reference.final_contacts);
    for (std::size_t i = 0; i < actual.samples.size(); ++i) {
        const auto& a = actual.samples[i];
        const auto& b = reference.samples[i];
        CHECK(std::bit_cast<std::uint64_t>(a.manual) == std::bit_cast<std::uint64_t>(b.manual));
        if (a.connected) {
            CHECK(b.connected);
            same_bits(a.buses, b.buses);
            CHECK(std::bit_cast<std::uint64_t>(a.combined) ==
                  std::bit_cast<std::uint64_t>(b.combined));
        }
    }
}

void test_partition_and_coherence(const RuntimeProfile& profile, Observations& observed) {
    CHECK(profile.manual_map[0][2] == kManual[0].source);
    CHECK(profile.manual_map[12][2] == kManual[1].source);
    CHECK(profile.manual_map[55][2] == kManual[2].source);
    constexpr std::array<std::uint32_t, 1> one{1}, fixed{64};
    constexpr std::array<std::uint32_t, 9> irregular{7, 1, 113, 3, 64, 257, 2, 31, 5};
    for (const double rate : kRates) {
        const auto reference = run_schedule(profile, rate, one, false, observed);
        compare_runs(run_schedule(profile, rate, fixed, false, observed), reference);
        compare_runs(run_schedule(profile, rate, irregular, false, observed), reference);
        compare_runs(run_schedule(profile, rate, irregular, true, observed), reference);
    }
}

void test_all_rate_pairs(const RuntimeProfile& profile, Observations& observed) {
    for (const double initial_rate : kRates) {
        for (const double new_rate : kRates) {
            TonewheelBank sources, control;
            CHECK(sources.prepare(profile, initial_rate, kSeed + 1) == Status::Ok);
            CHECK(control.prepare(profile, initial_rate, kSeed + 1) == Status::Ok);
            PedalBusKernel pedals;
            CHECK(pedals.prepare(hammond::compiled_pedal_routes(), fixture_weights()) == Status::Ok);
            const auto edits = all_contacts(true);
            CHECK(pedals.apply_contacts(edits) == Status::Ok);
            for (std::uint32_t frame = 0; frame < 129; ++frame) {
                PedalSourceFrame a{}, b{};
                sources.process_frame(a);
                control.process_frame(b);
                same_bits(a, b);
                same_phases(sources, control, observed);
                ++observed.source_frames;
            }
            const auto original_pedals = pedals;
            const auto before = phases(sources);
            CHECK(sources.reconfigure_sample_rate(new_rate) == Status::Ok);
            CHECK(control.reconfigure_sample_rate(new_rate) == Status::Ok);
            same_bits(phases(sources), before);
            CHECK(pedals == original_pedals);
            ++observed.rate_changes;
            CHECK(sources.reconfigure_sample_rate(192000.0) == Status::InvalidSpec);
            CHECK(sources.reconfigure_sample_rate(std::numeric_limits<double>::quiet_NaN()) ==
                  Status::InvalidSpec);
            same_bits(phases(sources), before);
            CHECK(pedals == original_pedals);
            CHECK(sources.sample_rate() == new_rate);
            for (std::uint32_t frame = 0; frame < 513; ++frame) {
                PedalSourceFrame a{}, b{};
                sources.process_frame(a);
                control.process_frame(b);
                same_bits(a, b);
                same_phases(sources, control, observed);
                PedalBusFrame first{}, repeated{};
                CHECK(pedals.render_frame(a, first) == Status::Ok);
                CHECK(pedals.render_frame(a, repeated) == Status::Ok);
                same_bits(first, repeated);
                CHECK(pedals == original_pedals);
                same_phases(sources, control, observed);
                ++observed.source_frames;
            }
        }
    }
}
} // namespace

int main() {
    Observations observed;
    const auto profile = load_test_profile();
    test_partition_and_coherence(profile, observed);
    test_all_rate_pairs(profile, observed);
    CHECK(observed.nonzero_frames > 1000);
    CHECK(observed.discarded_frames == 495);
    CHECK(observed.partition_runs == 12);
    CHECK(observed.zero_time_edits == 228);
    CHECK(observed.rate_changes == 57);
    std::cout << "pedal source harness passed: source_frames=" << observed.source_frames
              << ", phase_values=" << observed.phase_values
              << ", coherent_frames=" << observed.coherent_frames
              << ", nonzero_frames=" << observed.nonzero_frames
              << ", discarded_pedal_frames=" << observed.discarded_frames
              << ", zero_time_edit_batches=" << observed.zero_time_edits
              << ", rate_changes=" << observed.rate_changes
              << ", partition_runs=" << observed.partition_runs
              << ", max_coherence_error=" << std::setprecision(18) << observed.maximum_error
              << ", fixed_tolerance=" << kCoherenceTolerance << '\n';
}
