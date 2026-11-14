#include "RotaryRendererInternal.h"

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <limits>
#include <new>
#include <utility>

namespace hammond::rotary {
namespace {

struct PreparedConfiguration {
    std::array<RotaryMotion, kRotorCount> motion{};
    std::array<PreparedStreamingPath, kPathCount> paths{};
    std::size_t capacity_frames{0};
    std::uint32_t flush_frames{0};
};

[[nodiscard]] Status history_lengths(double rate, double distance, double sound_speed,
                                      std::size_t& capacity, std::uint32_t& flush) noexcept {
    const double propagation_frames = std::ceil(rate * distance / sound_speed);
    constexpr auto guards = kAlgorithmicLatencyFrames + 4;
    if (!std::isfinite(propagation_frames) || propagation_frames < 0.0
        || propagation_frames > static_cast<double>(kMaxHistoryFrames - guards)) {
        return Status::InvalidSpec;
    }
    const auto integral = static_cast<std::uint32_t>(propagation_frames);
    capacity = static_cast<std::size_t>(integral + guards);
    flush = integral + kAlgorithmicLatencyFrames + 2;
    return Status::Ok;
}

[[nodiscard]] Status configure(const Profile& profile, const ProcessSpec& spec,
                                PreparedConfiguration& destination) noexcept {
    if (!is_supported_sample_rate(spec.sample_rate) || spec.max_block_frames == 0
        || spec.max_block_frames > kMaxBlockFrames) return Status::InvalidSpec;
    PreparedConfiguration candidate;
    double maximum_distance = 0.0;
    for (std::size_t rotor = 0; rotor < kRotorCount; ++rotor) {
        const auto& source = profile.rotors[rotor];
        if (!is_valid_command(source.initial_command)) return Status::InvalidProfile;
        auto status = candidate.motion[rotor].prepare(source.motion, source.initial_phase_rad,
            source.initial_speed_rad_s, source.initial_command, spec.sample_rate);
        if (status != Status::Ok) return status;
        for (std::size_t channel = 0; channel < kMicrophoneCount; ++channel) {
            auto& path = candidate.paths[rotor * kMicrophoneCount + channel];
            status = path.prepare(source, profile.microphones[channel], profile.sound_speed_m_s,
                                   profile.reference_distance_m);
            if (status != Status::Ok) return status;
            maximum_distance = std::max(maximum_distance, path.bounds().max_distance_m);
        }
    }
    const auto status = history_lengths(spec.sample_rate, maximum_distance, profile.sound_speed_m_s,
                                        candidate.capacity_frames, candidate.flush_frames);
    if (status != Status::Ok) return status;
    destination = candidate;
    return Status::Ok;
}

[[nodiscard]] Status initialize_histories(detail::RotaryRendererStorage& storage) noexcept {
    for (std::size_t rotor = 0; rotor < kRotorCount; ++rotor) {
        auto status = storage.waveform[rotor].prepare(storage.spec.sample_rate, storage.capacity_frames);
        if (status != Status::Ok) return status;
        status = storage.motion_history[rotor].prepare(storage.motion[rotor], storage.capacity_frames);
        if (status != Status::Ok) return status;
    }
    return Status::Ok;
}

struct AddressRange {
    std::uintptr_t begin{0};
    std::uintptr_t end{0};
};

[[nodiscard]] bool audio_range(const double* data, std::size_t count,
                                AddressRange& destination) noexcept {
    if (count == 0) {
        destination = {};
        return true;
    }
    if (data == nullptr) return false;
    const auto begin = reinterpret_cast<std::uintptr_t>(data);
    if (count > (std::numeric_limits<std::uintptr_t>::max() - begin) / sizeof(double)) return false;
    destination = {begin, begin + count * sizeof(double)};
    return true;
}

[[nodiscard]] bool overlaps(AddressRange a, AddressRange b) noexcept {
    return a.begin < b.end && b.begin < a.end;
}

} // namespace

RotaryRenderer::RotaryRenderer() noexcept = default;
RotaryRenderer::~RotaryRenderer() = default;

Status RotaryRenderer::prepare(const Profile& profile, const ProcessSpec& spec) noexcept {
    PreparedConfiguration configuration;
    auto status = configure(profile, spec, configuration);
    if (status != Status::Ok) return status;
    std::unique_ptr<detail::RotaryRendererStorage> candidate;
    try {
        candidate = std::make_unique<detail::RotaryRendererStorage>();
    } catch (const std::bad_alloc&) {
        return Status::AllocationFailure;
    }
    candidate->original_profile = profile;
    candidate->spec = spec;
    candidate->capacity_frames = configuration.capacity_frames;
    candidate->flush_frames = configuration.flush_frames;
    candidate->motion = configuration.motion;
    candidate->paths = configuration.paths;
    status = initialize_histories(*candidate);
    if (status != Status::Ok) return status;
    storage_ = std::move(candidate);
    return Status::Ok;
}

bool RotaryRenderer::prepared() const noexcept { return storage_ != nullptr; }
Profile RotaryRenderer::profile() const noexcept { return storage_ ? storage_->original_profile : Profile{}; }
ProcessSpec RotaryRenderer::spec() const noexcept { return storage_ ? storage_->spec : ProcessSpec{0.0, 0}; }

RendererState RotaryRenderer::state() const noexcept {
    RendererState result;
    if (!storage_) return result;
    result.prepared = true;
    result.sample_rate = storage_->spec.sample_rate;
    result.frame = storage_->motion[0].frame();
    result.max_frame = storage_->motion[0].max_frame();
    for (std::size_t rotor = 0; rotor < kRotorCount; ++rotor) {
        result.motion[rotor] = storage_->motion[rotor].state();
        result.epoch_initial[rotor] = storage_->motion[rotor].epoch_initial_state();
        result.commands[rotor] = storage_->motion[rotor].command();
        result.segments[rotor] = storage_->motion[rotor].segment();
    }
    return result;
}

RendererDiagnostics RotaryRenderer::diagnostics() const noexcept {
    return storage_ ? storage_->diagnostics : RendererDiagnostics{};
}

std::array<PathBounds, kPathCount> RotaryRenderer::path_bounds() const noexcept {
    std::array<PathBounds, kPathCount> result{};
    if (storage_) {
        for (std::size_t path = 0; path < kPathCount; ++path) result[path] = storage_->paths[path].bounds();
    }
    return result;
}

std::size_t RotaryRenderer::history_capacity_frames() const noexcept {
    return storage_ ? storage_->capacity_frames : 0;
}

std::uint32_t RotaryRenderer::tail_flush_frames() const noexcept {
    return storage_ ? storage_->flush_frames : 0;
}

ProcessResult RotaryRenderer::process(std::span<const double> horn, std::span<const double> drum,
                                      std::span<double> left, std::span<double> right,
                                      std::span<const CommandEvent> events) noexcept {
    if (!storage_) return {Status::NotPrepared};
    auto& storage = *storage_;
    const std::size_t frames = horn.size();
    if (frames > storage.spec.max_block_frames) return {Status::BlockTooLarge};
    if (events.size() > kMaxEventsPerBlock) return {Status::TooManyEvents};
    if (drum.size() != frames || left.size() != frames || right.size() != frames
        || (!events.empty() && events.data() == nullptr)) return {Status::InvalidBuffer};
    std::array<AddressRange, 4> ranges{};
    if (!audio_range(horn.data(), frames, ranges[0]) || !audio_range(drum.data(), frames, ranges[1])
        || !audio_range(left.data(), frames, ranges[2]) || !audio_range(right.data(), frames, ranges[3])
        || overlaps(ranges[2], ranges[3]) || overlaps(ranges[2], ranges[0])
        || overlaps(ranges[2], ranges[1]) || overlaps(ranges[3], ranges[0])
        || overlaps(ranges[3], ranges[1])) return {Status::InvalidBuffer};
    const auto first_frame = storage.motion[0].frame();
    const auto maximum_frame = storage.motion[0].max_frame();
    if (first_frame > maximum_frame || frames > maximum_frame - first_frame) return {Status::TimelineOverflow};
    std::uint32_t previous_offset = 0;
    for (const auto& event : events) {
        if (!is_valid_rotor(event.rotor) || !is_valid_command(event.command)
            || event.offset > frames || event.offset < previous_offset) return {Status::InvalidEvent};
        previous_offset = event.offset;
    }
    for (std::size_t index = 0; index < frames; ++index) {
        if (!std::isfinite(horn[index]) || !std::isfinite(drum[index])
            || std::abs(horn[index]) > kMaxInputMagnitude || std::abs(drum[index]) > kMaxInputMagnitude) {
            return {Status::InvalidBuffer};
        }
    }

    auto motion = storage.motion;
    auto diagnostics = storage.diagnostics;
    const std::array<std::uint64_t, kRotorCount> old_waveform_frames{
        storage.waveform[0].next_frame_, storage.waveform[1].next_frame_};
    const std::array<std::uint64_t, kRotorCount> old_motion_frames{
        storage.motion_history[0].next_frame_, storage.motion_history[1].next_frame_};
    std::size_t live_undo = 0;
    ProcessResult result;
    const auto reject = [&](Status status) noexcept {
        while (live_undo != 0) {
            const auto& record = storage.undo[--live_undo];
            for (std::size_t rotor = 0; rotor < kRotorCount; ++rotor) {
                storage.waveform[rotor].samples_[record.slot] = record.samples[rotor];
                storage.motion_history[rotor].segments_[record.slot] = record.segments[rotor];
            }
        }
        for (std::size_t rotor = 0; rotor < kRotorCount; ++rotor) {
            storage.waveform[rotor].next_frame_ = old_waveform_frames[rotor];
            storage.motion_history[rotor].next_frame_ = old_motion_frames[rotor];
        }
        result.status = status;
        result.events_consumed = 0;
        return result;
    };
    std::size_t next_event = 0;
    const auto boundary = [&](std::size_t offset) noexcept -> Status {
        const auto frame = first_frame + static_cast<std::uint64_t>(offset);
        for (auto& owner : motion) {
            const auto status = owner.advance_to(frame);
            if (status != Status::Ok) return status;
        }
        while (next_event < events.size() && events[next_event].offset == offset) {
            const auto& event = events[next_event];
            const auto status = motion[static_cast<std::size_t>(event.rotor)].apply_command(frame, event.command);
            if (status != Status::Ok) return status;
            ++next_event;
        }
        return Status::Ok;
    };

    for (std::size_t index = 0; index < frames; ++index) {
        auto status = boundary(index);
        if (status != Status::Ok) return reject(status);
        const auto frame = first_frame + static_cast<std::uint64_t>(index);
        auto& record = storage.undo[live_undo];
        record.slot = static_cast<std::size_t>(frame % storage.capacity_frames);
        for (std::size_t rotor = 0; rotor < kRotorCount; ++rotor) {
            record.samples[rotor] = storage.waveform[rotor].samples_[record.slot];
            record.segments[rotor] = storage.motion_history[rotor].segments_[record.slot];
        }
        ++live_undo; // Live before any partial write, including the failing frame.
        status = storage.waveform[0].push(horn[index]);
        if (status != Status::Ok) return reject(status);
        status = storage.waveform[1].push(drum[index]);
        if (status != Status::Ok) return reject(status);
        for (std::size_t rotor = 0; rotor < kRotorCount; ++rotor) {
            status = storage.motion_history[rotor].append(motion[rotor]);
            if (status != Status::Ok) return reject(status);
        }
        const SamplePosition observation{
            static_cast<std::int64_t>(frame) - static_cast<std::int64_t>(kAlgorithmicLatencyFrames), 0.0};
        std::array<double, kPathCount> pressure{};
        for (std::size_t path = 0; path < kPathCount; ++path) {
            const auto rotor = path / kMicrophoneCount;
            PathResult solved;
            SamplePosition emission;
            status = storage.paths[path].solve(storage.motion_history[rotor], observation, solved, emission);
            if (status != Status::Ok) return reject(status);
            result.max_solver_residual_s = std::max(result.max_solver_residual_s, std::abs(solved.residual_s));
            result.max_solver_iterations = std::max(result.max_solver_iterations, solved.iterations);
            double sample = 0.0;
            status = storage.waveform[rotor].interpolate(emission, sample);
            if (status != Status::Ok) return reject(status);
            pressure[path] = sample * solved.distance_gain;
            if (!std::isfinite(pressure[path])) return reject(Status::NumericalFailure);
            diagnostics.last_paths[path] = solved;
            diagnostics.last_emissions[path] = emission;
        }
        const double left_sample = pressure[0] + pressure[2];
        const double right_sample = pressure[1] + pressure[3];
        if (!std::isfinite(left_sample) || !std::isfinite(right_sample)) return reject(Status::NumericalFailure);
        storage.output[0][index] = left_sample;
        storage.output[1][index] = right_sample;
        diagnostics.has_rendered_sample = true;
        diagnostics.last_input_frame = frame;
        diagnostics.last_observation = observation;
        diagnostics.max_solver_residual_s = std::max(diagnostics.max_solver_residual_s, result.max_solver_residual_s);
        diagnostics.max_solver_iterations = std::max(diagnostics.max_solver_iterations, result.max_solver_iterations);
    }
    const auto final_status = boundary(frames);
    if (final_status != Status::Ok) return reject(final_status);
    // All borrowed events and every fallible operation precede publication.
    storage.motion = motion;
    storage.diagnostics = diagnostics;
    for (std::size_t index = 0; index < frames; ++index) {
        left[index] = storage.output[0][index];
        right[index] = storage.output[1][index];
    }
    result.events_consumed = static_cast<std::uint32_t>(events.size());
    return result;
}

Status RotaryRenderer::reset() noexcept {
    if (!storage_) return Status::NotPrepared;
    auto& storage = *storage_;
    auto motion = storage.motion;
    for (auto& owner : motion) {
        const auto status = owner.reset();
        if (status != Status::Ok) return status;
    }
    // Reset owners have valid frame-zero seeds; existing prepared histories and
    // capacity were admitted together. These clears have no remaining failure.
    for (std::size_t rotor = 0; rotor < kRotorCount; ++rotor) {
        (void)storage.waveform[rotor].reset();
        (void)storage.motion_history[rotor].prepare(motion[rotor], storage.capacity_frames);
    }
    storage.motion = motion;
    storage.diagnostics = {};
    return Status::Ok;
}

Status RotaryRenderer::reconfigure_sample_rate(double sample_rate) noexcept {
    if (!storage_) return Status::NotPrepared;
    if (!is_supported_sample_rate(sample_rate)) return Status::InvalidSpec;
    auto motion = storage_->motion; // Retain each owner's ORIGINAL reset seeds.
    for (auto& owner : motion) {
        const auto status = owner.reconfigure_sample_rate(sample_rate);
        if (status != Status::Ok) return status;
    }
    double maximum_distance = 0.0;
    for (const auto& path : storage_->paths) maximum_distance = std::max(maximum_distance, path.bounds().max_distance_m);
    std::size_t capacity = 0;
    std::uint32_t flush = 0;
    auto status = history_lengths(sample_rate, maximum_distance, storage_->original_profile.sound_speed_m_s, capacity, flush);
    if (status != Status::Ok) return status;
    std::unique_ptr<detail::RotaryRendererStorage> candidate;
    try {
        candidate = std::make_unique<detail::RotaryRendererStorage>();
    } catch (const std::bad_alloc&) {
        return Status::AllocationFailure;
    }
    candidate->original_profile = storage_->original_profile;
    candidate->spec = {sample_rate, storage_->spec.max_block_frames};
    candidate->capacity_frames = capacity;
    candidate->flush_frames = flush;
    candidate->motion = motion;
    candidate->paths = storage_->paths;
    status = initialize_histories(*candidate);
    if (status != Status::Ok) return status;
    storage_ = std::move(candidate);
    return Status::Ok;
}

} // namespace hammond::rotary
