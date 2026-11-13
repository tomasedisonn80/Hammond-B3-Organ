#include "hammond/HostTimeline.h"

#include <algorithm>
#include <array>
#include <bit>
#include <cmath>
#include <limits>
#include <type_traits>

namespace hammond {
namespace {

[[nodiscard]] std::size_t parameter_index(std::uint32_t id) noexcept {
    const auto descriptors = parameter_descriptors();
    for (std::size_t i = 0; i < descriptors.size(); ++i) {
        if (descriptors[i].id == id) return i;
    }
    return kParameterCount;
}

[[nodiscard]] bool same_bits(double left, double right) noexcept {
    return std::bit_cast<std::uint64_t>(left) == std::bit_cast<std::uint64_t>(right);
}

[[nodiscard]] bool snapshot_anchors(
    const ControlSnapshot& snapshot, std::array<double, kParameterCount>& anchors) noexcept {
    if (!is_valid_control_snapshot(snapshot)) return false;
    const auto descriptors = parameter_descriptors();
    for (std::size_t i = 0; i < descriptors.size(); ++i) {
        const auto& descriptor = descriptors[i];
        const auto manual = static_cast<std::size_t>(descriptor.manual);
        double plain = 0.0;
        switch (descriptor.event_type) {
        case EventType::BankDrawbar:
            plain = snapshot.drawbars[manual][descriptor.index / kDrawbarCount]
                                       [descriptor.index % kDrawbarCount];
            break;
        case EventType::SelectBank:
            plain = static_cast<double>(snapshot.selected_banks[manual]);
            break;
        case EventType::Expression:
            plain = snapshot.expression;
            break;
        case EventType::Percussion:
            switch (descriptor.index) {
            case 0: plain = snapshot.percussion.enabled ? 1.0 : 0.0; break;
            case 1: plain = static_cast<double>(snapshot.percussion.harmonic); break;
            case 2: plain = static_cast<double>(snapshot.percussion.volume); break;
            case 3: plain = static_cast<double>(snapshot.percussion.decay); break;
            default: return false;
            }
            break;
        case EventType::PedalDrawbar:
            plain = snapshot.pedal_drawbars[descriptor.index];
            break;
        default: return false;
        }
        if (!plain_to_normalized(descriptor.id, plain, anchors[i])) return false;
    }
    return true;
}

[[nodiscard]] bool musical_offset(const HostMusicalEvent& event,
                                   std::uint32_t& destination) noexcept {
    if (const auto* manual = std::get_if<HostNoteEvent>(&event)) {
        destination = manual->offset;
        return true;
    }
    if (const auto* pedal = std::get_if<PedalNoteEvent>(&event)) {
        destination = pedal->offset;
        return true;
    }
    return false;
}

template <typename Note>
[[nodiscard]] Status translate_note(Note note, NoteOwnership& manual,
                                     PedalNoteOwnership& pedal,
                                     std::span<Event> destination,
                                     std::uint32_t& produced) noexcept {
    note.offset = 0;
    if constexpr (std::is_same_v<Note, HostNoteEvent>) {
        const auto result = manual.translate(0, std::span<const Note>{&note, 1}, destination);
        produced = result.output_events;
        return result.status;
    } else {
        const auto result = pedal.translate(0, std::span<const Note>{&note, 1}, destination);
        produced = result.output_events;
        return result.status;
    }
}

// Callback-local borrowed views. No cursor or pointer is retained after process.
struct CurveCursor {
    std::span<const HostParameterPoint> points{};
    std::size_t next_point{0};
    bool carry_pending{false};
    double carry_value{0.0};
    bool active{false};
    std::int32_t left_offset{-1};
    double left_value{0.0};
    HostParameterPoint right{};
    bool has_right{false};

    void advance() noexcept {
        if (carry_pending) {
            right = {0, carry_value};
            carry_pending = false;
            has_right = true;
            // Fresh points at zero follow carried points and win their tie.
            while (next_point < points.size() && points[next_point].offset == 0) {
                right = points[next_point++];
            }
            return;
        }
        if (next_point == points.size()) {
            has_right = false;
            return;
        }
        right = points[next_point++];
        while (next_point < points.size() && points[next_point].offset == right.offset) {
            right = points[next_point++];
        }
        has_right = true;
    }

    [[nodiscard]] double value(std::int32_t sample, bool& explicit_point) noexcept {
        while (has_right && sample > right.offset) {
            left_offset = right.offset;
            left_value = right.normalized;
            advance();
        }
        explicit_point = has_right && sample == right.offset;
        if (explicit_point) return right.normalized;
        if (!has_right || same_bits(left_value, right.normalized)) return left_value;
        const auto numerator = static_cast<double>(sample - left_offset);
        const auto denominator = static_cast<double>(right.offset - left_offset);
        // Multiply before division. All factors are bounded; this also retains
        // exact dyadic ramps across integer callback subdivisions. The clamp is
        // a bounded interpolation-roundoff guard, not an audio limiter.
        const auto interpolated = left_value +
            ((right.normalized - left_value) * numerator) / denominator;
        return std::clamp(interpolated, std::min(left_value, right.normalized),
                           std::max(left_value, right.normalized));
    }
};

} // namespace

static_assert(std::is_trivially_copyable_v<Engine>);
static_assert(std::is_nothrow_copy_assignable_v<Engine>);
static_assert(std::is_trivially_copyable_v<NoteOwnership>);
static_assert(std::is_trivially_copyable_v<PedalNoteOwnership>);
static_assert(std::is_trivially_copyable_v<HostCarryEvent>);
static_assert(std::is_nothrow_copy_assignable_v<HostCarryEvent>);
static_assert(std::is_trivially_copyable_v<HostTimeline>);

Status HostTimeline::prepare(const RuntimeProfile& profile, const ProcessSpec& spec) noexcept {
    return prepare(profile, spec, make_legacy_console_model());
}

Status HostTimeline::prepare(const RuntimeProfile& profile, const ProcessSpec& spec,
                             const ConsoleModel& console_model) noexcept {
    if (spec.max_block_frames == 0 || spec.max_block_frames > kHardMaxBlockFrames) {
        return Status::InvalidSpec;
    }
    auto core_spec = spec;
    core_spec.max_block_frames = kHardMaxBlockFrames;
    const auto status = work_.engine.prepare(profile, core_spec, console_model);
    if (status != Status::Ok) return status;
    work_.retained = {};
    if (!snapshot_anchors(work_.engine.controls_snapshot(), work_.retained.anchors)) {
        return Status::InvalidSpec;
    }
    engine_ = work_.engine;
    manual_ = {};
    pedal_ = {};
    retained_ = work_.retained;
    max_block_frames_ = spec.max_block_frames;
    return Status::Ok;
}

Status HostTimeline::reconfigure(double sample_rate, std::uint32_t max_block_frames) noexcept {
    if (!engine_.prepared()) return Status::NotPrepared;
    if (max_block_frames == 0 || max_block_frames > kHardMaxBlockFrames) {
        return Status::InvalidSpec;
    }
    work_.engine = engine_;
    const auto status = work_.engine.reconfigure_sample_rate(sample_rate);
    if (status != Status::Ok) return status;
    engine_ = work_.engine;
    max_block_frames_ = max_block_frames;
    return Status::Ok;
}

bool HostTimeline::set_manual_bus_route(std::uint32_t bus, Manual manual) noexcept {
    return engine_.prepared() && manual_.set_bus_route(bus, manual);
}

bool HostTimeline::normalized_anchor(std::uint32_t parameter_id,
                                      double& destination) const noexcept {
    const auto index = parameter_index(parameter_id);
    if (!engine_.prepared() || index == kParameterCount) return false;
    destination = retained_.anchors[index];
    return true;
}

bool HostTimeline::carry_event(std::size_t index, HostCarryEvent& destination) const noexcept {
    if (!engine_.prepared() || index >= retained_.carry_count) return false;
    destination = retained_.carry[index];
    return true;
}

HostTimelineResult HostTimeline::process(
    std::uint32_t frames, std::span<float> mono_output,
    std::span<const HostParameterQueue> parameter_queues,
    std::span<const HostMusicalEvent> musical_events,
    std::span<const ControlSnapshot> restores) noexcept {
    const auto failure = [](Status status) noexcept { return HostTimelineResult{status}; };
    const auto previous_carry_count = retained_.carry_count;
    if (!engine_.prepared()) return failure(Status::NotPrepared);
    if (frames > max_block_frames_ || frames > kHardMaxBlockFrames) {
        return failure(Status::BlockTooLarge);
    }
    if (!mono_output.empty() && (mono_output.data() == nullptr || mono_output.size() < frames)) {
        return failure(Status::InvalidBuffer);
    }
    if (frames > std::numeric_limits<std::uint64_t>::max() - engine_.frame_clock()) {
        return failure(Status::TimelineOverflow);
    }
    if (parameter_queues.size() > kParameterCount || restores.size() > kMaxHostStateRestores ||
        musical_events.size() > kMaxEventsPerBlock - retained_.carry_count) {
        return failure(Status::TooManyEvents);
    }
    if ((!parameter_queues.empty() && parameter_queues.data() == nullptr) ||
        (!musical_events.empty() && musical_events.data() == nullptr) ||
        (!restores.empty() && restores.data() == nullptr)) {
        return failure(Status::InvalidEvent);
    }
    for (const auto& snapshot : restores) {
        if (!is_valid_control_snapshot(snapshot)) return failure(Status::InvalidEvent);
    }

    const auto descriptors = parameter_descriptors();
    std::array<const HostParameterQueue*, kParameterCount> queues{};
    auto raw_count = retained_.carry_count + musical_events.size();
    for (const auto& queue : parameter_queues) {
        const auto index = parameter_index(queue.parameter_id);
        if (index == kParameterCount || queues[index] != nullptr) {
            return failure(Status::InvalidEvent);
        }
        if (queue.points.size() > kMaxEventsPerBlock - raw_count) {
            return failure(Status::TooManyEvents);
        }
        raw_count += queue.points.size();
        if (!queue.points.empty() && queue.points.data() == nullptr) {
            return failure(Status::InvalidEvent);
        }
        queues[index] = &queue;
        std::int32_t previous = 0;
        for (const auto& point : queue.points) {
            if (point.offset < previous || point.offset > static_cast<std::int32_t>(frames) ||
                !std::isfinite(point.normalized) || point.normalized < 0.0 ||
                point.normalized > 1.0) {
                return failure(Status::InvalidEvent);
            }
            previous = point.offset;
        }
    }
    std::uint32_t previous = 0;
    for (const auto& event : musical_events) {
        std::uint32_t offset = 0;
        if (!musical_offset(event, offset) || offset < previous || offset > frames) {
            return failure(Status::InvalidEvent);
        }
        previous = offset;
    }

    // Validate every musical payload and owner transition before any candidate
    // rendering, including future boundary records. These copies are discarded;
    // ownership at N remains uncommitted until the next accepted callback.
    auto preview_manual = manual_;
    auto preview_pedal = pedal_;
    std::array<Event, kManualCount * kManualKeyCount> ignored{};
    std::uint32_t produced = 0;
    for (std::size_t i = 0; i < retained_.carry_count; ++i) {
        const auto& event = retained_.carry[i];
        Status status = Status::Ok;
        if (const auto* note = std::get_if<HostNoteEvent>(&event)) {
            status = translate_note(*note, preview_manual, preview_pedal, ignored, produced);
        } else if (const auto* pedal_note = std::get_if<PedalNoteEvent>(&event)) {
            status = translate_note(*pedal_note, preview_manual, preview_pedal, ignored, produced);
        }
        if (status != Status::Ok) return failure(status);
    }
    for (const auto& event : musical_events) {
        Status status = Status::InvalidEvent;
        if (const auto* note = std::get_if<HostNoteEvent>(&event)) {
            status = translate_note(*note, preview_manual, preview_pedal, ignored, produced);
        } else if (const auto* pedal_note = std::get_if<PedalNoteEvent>(&event)) {
            status = translate_note(*pedal_note, preview_manual, preview_pedal, ignored, produced);
        }
        if (status != Status::Ok) return failure(status);
    }

    work_.engine = engine_;
    work_.manual = manual_;
    work_.pedal = pedal_;
    work_.retained = retained_;
    work_.retained.carry_count = 0;
    for (const auto& snapshot : restores) {
        if (!work_.engine.restore_controls(snapshot) ||
            !snapshot_anchors(snapshot, work_.retained.anchors)) {
            return failure(Status::InvalidEvent);
        }
    }

    std::array<CurveCursor, kParameterCount> curves{};
    std::array<double, kParameterCount> last_plain{};
    for (std::size_t i = 0; i < curves.size(); ++i) {
        curves[i].left_value = work_.retained.anchors[i];
        if (queues[i] != nullptr) curves[i].points = queues[i]->points;
    }
    for (std::size_t i = 0; i < retained_.carry_count; ++i) {
        if (const auto* point = std::get_if<HostParameterCarry>(&retained_.carry[i])) {
            auto& curve = curves[parameter_index(point->parameter_id)];
            curve.carry_pending = true;
            curve.carry_value = point->normalized;
        }
    }
    for (std::size_t i = 0; i < curves.size(); ++i) {
        curves[i].active = curves[i].carry_pending || !curves[i].points.empty();
        curves[i].advance();
        Event initial;
        if (!normalized_to_event(descriptors[i].id, work_.retained.anchors[i], 0, initial)) {
            return failure(Status::InvalidEvent);
        }
        last_plain[i] = initial.value;
        if (frames > 0) {
            for (const auto& point : curves[i].points) {
                if (point.offset == static_cast<std::int32_t>(frames)) {
                    work_.retained.carry[work_.retained.carry_count++] =
                        HostParameterCarry{descriptors[i].id, point.normalized};
                }
            }
        }
    }
    if (frames > 0) {
        for (const auto& event : musical_events) {
            if (const auto* note = std::get_if<HostNoteEvent>(&event); note && note->offset == frames) {
                auto copy = *note;
                copy.offset = 0;
                work_.retained.carry[work_.retained.carry_count++] = copy;
            } else if (const auto* pedal_note = std::get_if<PedalNoteEvent>(&event);
                       pedal_note && pedal_note->offset == frames) {
                auto copy = *pedal_note;
                copy.offset = 0;
                work_.retained.carry[work_.retained.carry_count++] = copy;
            }
        }
    }

    HostTimelineResult result;
    std::uint32_t start = 0;
    std::size_t event_count = 0;
    // A full buffer can contain both earlier and current-sample events. Render
    // its strict prefix first, then apply its current-sample tail without time.
    // This admits dense same-sample panic expansion without losing a release.
    const auto flush_at = [&](std::uint32_t frame) noexcept -> Status {
        const auto length = frame - start;
        std::size_t prefix = 0;
        while (prefix < event_count && work_.events[prefix].offset < length) ++prefix;
        if (length != 0) {
            const auto rendered = work_.engine.process(
                length, std::span<float>{work_.mono}.subspan(start, length),
                std::span<const Event>{work_.events.data(), prefix});
            if (!rendered) return rendered.status;
            result.physical_events_applied += rendered.events_consumed;
            ++result.engine_calls;
        }
        if (prefix < event_count) {
            for (std::size_t i = prefix; i < event_count; ++i) work_.events[i].offset = 0;
            const auto flushed = work_.engine.process(
                0, {}, std::span<const Event>{work_.events.data() + prefix, event_count - prefix});
            if (!flushed) return flushed.status;
            result.physical_events_applied += flushed.events_consumed;
            ++result.engine_calls;
        }
        event_count = 0;
        start = frame;
        return Status::Ok;
    };
    const auto reserve = [&](std::uint32_t frame, std::size_t needed) noexcept -> Status {
        if (needed <= kMaxEventsPerBlock - event_count) return Status::Ok;
        return flush_at(frame);
    };
    const auto append_note = [&]<typename Note>(const Note& note, std::uint32_t frame) noexcept {
        constexpr auto capacity = std::is_same_v<Note, HostNoteEvent>
            ? kManualCount * kManualKeyCount : kPedalCount;
        const auto reserved = reserve(frame, capacity);
        if (reserved != Status::Ok) return reserved;
        std::uint32_t emitted = 0;
        const auto translated = translate_note(note, work_.manual, work_.pedal,
            std::span<Event>{work_.events}.subspan(event_count), emitted);
        if (translated != Status::Ok) return translated;
        for (std::size_t i = 0; i < emitted; ++i) {
            work_.events[event_count + i].offset = frame - start;
        }
        event_count += emitted;
        return Status::Ok;
    };

    std::size_t next_music = 0;
    const auto evaluations = frames == 0 ? 1U : frames;
    for (std::uint32_t frame = 0; frame < evaluations; ++frame) {
        for (std::size_t i = 0; i < curves.size(); ++i) {
            if (!curves[i].active) continue;
            bool explicit_point = false;
            const auto value = curves[i].value(static_cast<std::int32_t>(frame), explicit_point);
            const auto changed = !same_bits(value, work_.retained.anchors[i]);
            work_.retained.anchors[i] = value;
            if (!changed && !explicit_point) continue;
            Event control;
            if (!normalized_to_event(descriptors[i].id, value, 0, control)) {
                return failure(Status::InvalidEvent);
            }
            if (!explicit_point && same_bits(control.value, last_plain[i])) continue;
            const auto reserved = reserve(frame, 1);
            if (reserved != Status::Ok) return failure(reserved);
            control.offset = frame - start;
            work_.events[event_count++] = control;
            last_plain[i] = control.value;
        }
        if (frame == 0) {
            for (std::size_t i = 0; i < retained_.carry_count; ++i) {
                Status status = Status::Ok;
                if (const auto* note = std::get_if<HostNoteEvent>(&retained_.carry[i])) {
                    status = append_note(*note, frame);
                } else if (const auto* pedal_note = std::get_if<PedalNoteEvent>(&retained_.carry[i])) {
                    status = append_note(*pedal_note, frame);
                }
                if (status != Status::Ok) return failure(status);
            }
        }
        while (next_music < musical_events.size()) {
            std::uint32_t offset = 0;
            (void)musical_offset(musical_events[next_music], offset);
            if (offset != frame) break;
            const auto& event = musical_events[next_music++];
            Status status = Status::InvalidEvent;
            if (const auto* note = std::get_if<HostNoteEvent>(&event)) {
                status = append_note(*note, frame);
            } else if (const auto* pedal_note = std::get_if<PedalNoteEvent>(&event)) {
                status = append_note(*pedal_note, frame);
            }
            if (status != Status::Ok) return failure(status);
        }
    }
    const auto length = frames - start;
    const auto rendered = work_.engine.process(
        length, length == 0 ? std::span<float>{} : std::span<float>{work_.mono}.subspan(start, length),
        std::span<const Event>{work_.events.data(), event_count});
    if (!rendered) return failure(rendered.status);
    result.physical_events_applied += rendered.events_consumed;
    ++result.engine_calls;

    // All potentially failing work is complete. These fixed value assignments
    // and bounded float copies cannot fail and retain no caller-owned pointer.
    engine_ = work_.engine;
    manual_ = work_.manual;
    pedal_ = work_.pedal;
    retained_ = work_.retained;
    if (!mono_output.empty()) std::copy_n(work_.mono.begin(), frames, mono_output.begin());
    result.input_records_consumed = static_cast<std::uint32_t>(raw_count - previous_carry_count);
    result.carried_records_consumed = static_cast<std::uint32_t>(previous_carry_count);
    result.restores_consumed = static_cast<std::uint32_t>(restores.size());
    return result;
}

} // namespace hammond
