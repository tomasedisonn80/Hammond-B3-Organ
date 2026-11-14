#include "TestSupport.h"
#include "UiModel.h"
#include "hammond/ControlStateIO.h"

#include <algorithm>
#include <array>
#include <bit>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <iomanip>
#include <initializer_list>
#include <iostream>
#include <limits>
#include <numbers>
#include <span>
#include <sstream>
#include <string>
#include <string_view>
#include <tuple>
#include <variant>
#include <vector>

namespace {
using namespace hammond;
using namespace hammond::standalone;

static_assert(kParameterCount == 47);
constexpr float sentinel = -8137.25F;
constexpr std::uint64_t fnv_basis = 14695981039346656037ULL;
constexpr std::array<std::uint32_t, 47> parameter_ids{
    4096, 4097, 4098, 4099, 4100, 4101, 4102, 4103, 4104,
    4112, 4113, 4114, 4115, 4116, 4117, 4118, 4119, 4120,
    4128, 4129, 4130, 4131, 4132, 4133, 4134, 4135, 4136,
    4144, 4145, 4146, 4147, 4148, 4149, 4150, 4151, 4152,
    8192, 8208, 8209, 12288, 12289, 12290, 12291, 16384, 16385, 20480, 20481};
constexpr std::array<UiPoint, 7> sizes{{
    {960, 700}, {1280, 900}, {1672, 941}, {1399, 819},
    {1400, 819}, {1399, 820}, {1400, 820}}};

struct Counts {
    std::uint64_t cases{}, blocks{}, frames{}, stereo_samples{}, commands{};
    std::uint64_t transitions{}, zero_action_checks{}, serialized_comparisons{};
    std::uint64_t phase_checks{}, readiness_checks{}, parameter_edits{};
    std::uint64_t audible_blocks{}, silent_blocks{}, isolated_samples{}, cancelled_upper_blocks{};
    std::uint64_t pcm_hash{fnv_basis};
    std::array<std::array<bool, 2>, 3> views{};
} counts;

void hash_word(std::uint64_t& hash, std::uint32_t word) {
    for (unsigned byte = 0; byte < 4; ++byte) {
        hash ^= (word >> (byte * 8)) & 255U;
        hash *= 1099511628211ULL;
    }
}

std::string saved_bytes(const ControlSnapshot& controls) {
    std::string bytes, error;
    CHECK(serialize_controls(controls, bytes, error));
    CHECK(error.empty() && bytes.starts_with("B3CONTROLS4\n"));
    return bytes;
}

void same_controls(const ControlSnapshot& a, const ControlSnapshot& b) {
    CHECK(a == b);
    CHECK(std::bit_cast<std::uint64_t>(a.expression) ==
          std::bit_cast<std::uint64_t>(b.expression));
    CHECK(saved_bytes(a) == saved_bytes(b));
    ++counts.serialized_comparisons;
}

SessionSnapshot read(const Session& session) {
    SessionSnapshot snapshot;
    CHECK(session.read_snapshot(snapshot));
    return snapshot;
}

void same_snapshot(const SessionSnapshot& a, const SessionSnapshot& b) {
    same_controls(a.controls, b.controls);
    CHECK(std::tie(a.held_keys, a.held_pedals, a.frame_clock, a.sample_rate,
                   a.prepared, a.running, a.publication_revision, a.resolved_sequence,
                   a.last_applied_sequence, a.recovery_count, a.queue_overflows,
                   a.rejected_commands, a.discarded_commands, a.fault_flags, a.last_core_status) ==
          std::tie(b.held_keys, b.held_pedals, b.frame_clock, b.sample_rate,
                   b.prepared, b.running, b.publication_revision, b.resolved_sequence,
                   b.last_applied_sequence, b.recovery_count, b.queue_overflows,
                   b.rejected_commands, b.discarded_commands, b.fault_flags, b.last_core_status));
    CHECK(std::bit_cast<std::uint32_t>(a.peak) == std::bit_cast<std::uint32_t>(b.peak));
}

void same_command(const SessionCommand& actual, const SessionCommand& expected) {
    CHECK(actual.index() == expected.index());
    if (const auto* controls = std::get_if<ControlSnapshot>(&actual)) {
        same_controls(*controls, std::get<ControlSnapshot>(expected));
        return;
    }
    CHECK(std::holds_alternative<PerformanceInputEvent>(actual));
    const auto& a = std::get<PerformanceInputEvent>(actual);
    const auto& b = std::get<PerformanceInputEvent>(expected);
    CHECK(a.index() == b.index());
    if (const auto* note = std::get_if<HostNoteEvent>(&a)) {
        const auto& other = std::get<HostNoteEvent>(b);
        CHECK(std::tie(note->offset, note->kind, note->bus, note->channel,
                       note->midi_note, note->velocity, note->note_id) ==
              std::tie(other.offset, other.kind, other.bus, other.channel,
                       other.midi_note, other.velocity, other.note_id));
    } else {
        CHECK(std::holds_alternative<PedalNoteEvent>(a));
        const auto& pedal = std::get<PedalNoteEvent>(a);
        const auto& other = std::get<PedalNoteEvent>(b);
        CHECK(std::tie(pedal.offset, pedal.kind, pedal.bus, pedal.channel,
                       pedal.pedal.value, pedal.velocity, pedal.note_id) ==
              std::tie(other.offset, other.kind, other.bus, other.channel,
                       other.pedal.value, other.velocity, other.note_id));
    }
}

void no_actions(const UiActions& actions) {
    CHECK(actions.count == 0);
    ++counts.zero_action_checks;
}

void tap(UiModel& model, UiKey key, bool shift = false) {
    no_actions(model.key({key, true, false, shift}));
    no_actions(model.key({key, false}));
}

UiControlId note_id(UiNote note) {
    if (note.target == UiTarget::Pedals)
        return {UiControlKind::PedalKey, Manual::Upper, DrawbarBank::A,
                static_cast<std::uint8_t>(note.value - 1)};
    return {UiControlKind::ManualKey,
            note.target == UiTarget::Upper ? Manual::Upper : Manual::Lower,
            DrawbarBank::A, static_cast<std::uint8_t>(note.value - 36)};
}

UiPoint playing_point(const UiModel& model, UiNote note) {
    const auto id = note_id(note);
    const auto& key = note.target == UiTarget::Pedals ? model.layout().pedal_keys[id.index] :
        model.layout().manual_keys[static_cast<std::size_t>(id.manual)][id.index];
    const auto& q = key.hit.points;
    const float depth = key.accidental ? 0.3F : 0.9F;
    const float left = q[0].x + (q[3].x - q[0].x) * depth;
    const float right = q[1].x + (q[2].x - q[1].x) * depth;
    return {(left + right) * 0.5F, q[0].y + (q[3].y - q[0].y) * depth};
}

SessionCommand owned_note(UiNote note, bool down, std::int32_t owner,
                          std::uint8_t channel = 0) {
    const auto velocity = static_cast<std::uint8_t>(down ? 127 : 0);
    if (note.target == UiTarget::Pedals)
        return PerformanceInputEvent{PedalNoteEvent{0,
            down ? PedalNoteKind::On : PedalNoteKind::Off, 0, channel,
            PedalId{note.value}, velocity, owner}};
    return PerformanceInputEvent{HostNoteEvent{0,
        down ? HostNoteKind::On : HostNoteKind::Off,
        static_cast<std::uint8_t>(note.target == UiTarget::Upper ? 0 : 1),
        channel, note.value, velocity, owner}};
}

Event physical_note(UiNote note, bool down) {
    if (note.target == UiTarget::Pedals)
        return {0, down ? EventType::PedalOn : EventType::PedalOff,
                Manual::Lower, note.value, down ? 127.0 : 0.0};
    return {0, down ? EventType::NoteOn : EventType::NoteOff,
            note.target == UiTarget::Upper ? Manual::Upper : Manual::Lower,
            note.value, down ? 127.0 : 0.0};
}

enum class Energy { Audible, Silent };

// The control UI never changes workspace, presentation or dimensions. Both real
// Sessions receive independently checked, identical commands at identical block
// boundaries. The Engine oracle receives explicitly planned physical events:
// it uses neither Session's command dispatcher nor either ownership adapter.
struct Pair {
    Session navigated, control;
    UiModel ui, plain_ui;
    Engine reference;
    const RuntimeProfile& profile;
    ProcessSpec spec;
    std::array<double, kToneSourceCount> phases{}, increments{};
    std::array<std::array<bool, kManualKeyCount>, kManualCount> holds{};
    std::array<bool, kPedalCount> pedals{};
    long double readiness{1.0L};
    std::uint64_t sequence{}, frames{}, pcm_hash{fnv_basis};
    float peak{}, last_peak{};
    double energy{}, isolated_energy{};
    ControlSnapshot saved{};

    Pair(const RuntimeProfile& source, double rate, std::uint64_t seed)
        : profile(source), spec{rate, 1024, seed, 1234567 + seed % 1024} {
        CHECK(navigated.prepare(profile, spec) == SessionStatus::Ok);
        CHECK(control.prepare(profile, spec) == SessionStatus::Ok);
        CHECK(reference.prepare(profile, spec) == Status::Ok);
        CHECK(navigated.start() == SessionStatus::Ok && control.start() == SessionStatus::Ok);
        ui.observe(read(navigated));
        plain_ui.observe(read(control));
        for (std::size_t tone = 0; tone < phases.size(); ++tone) {
            CHECK(reference.source_phase_turns(static_cast<ToneId>(tone + 1), phases[tone]));
            increments[tone] = profile.sources[tone].frequency_hz / rate;
        }
        same_snapshot(read(navigated), read(control));
    }

    void post(const SessionCommand& a, const SessionCommand& b) {
        same_command(a, b);
        const auto x = navigated.post(a);
        const auto y = control.post(b);
        CHECK(x.ok() && y.ok() && x.sequence == sequence + 1 && y.sequence == x.sequence);
        sequence = x.sequence;
        no_actions(ui.submitted(a, x));
        no_actions(plain_ui.submitted(b, y));
        ++counts.commands;
    }

    void dispatch(const UiActions& a, const UiActions& b, const SessionCommand& expected) {
        CHECK(a.count == 1 && b.count == 1);
        CHECK(std::holds_alternative<SessionCommand>(a.items[0]));
        CHECK(std::holds_alternative<SessionCommand>(b.items[0]));
        const auto& x = std::get<SessionCommand>(a.items[0]);
        const auto& y = std::get<SessionCommand>(b.items[0]);
        same_command(x, expected);
        same_command(y, expected);
        post(x, y);
    }

    void physical(UiNote note, bool down) {
        const std::array events{physical_note(note, down)};
        CHECK(reference.process(0, {}, events));
        if (note.target == UiTarget::Pedals) pedals[note.value - 1] = down;
        else holds[note.target == UiTarget::Upper ? 0 : 1][note.value - 36] = down;
    }

    void load(const ControlSnapshot& controls) {
        dispatch(ui.load_controls(controls), plain_ui.load_controls(controls), controls);
        CHECK(reference.restore_controls(controls));
        saved = controls;
    }

    // Every deliberate sound edit is applied to both UIs/Sessions and, as a
    // physical control event, to the independent reference before any sample.
    bool parameter(std::uint32_t id, double value) {
        double normalized = 0.0;
        CHECK(plain_to_normalized(id, value, normalized));
        Event event;
        CHECK(normalized_to_event(id, normalized, 0, event));
        const auto before = reference.controls_snapshot();
        const std::array events{event};
        CHECK(reference.process(0, {}, events));
        const auto expected = reference.controls_snapshot();
        const auto a = ui.external_parameter(id, normalized);
        const auto b = plain_ui.external_parameter(id, normalized);
        if (before == expected) {
            no_actions(a);
            no_actions(b);
            return false;
        }
        dispatch(a, b, expected);
        return true;
    }

    void save_checkpoint() {
        same_controls(ui.view().controls, plain_ui.view().controls);
        saved = ui.view().controls;
        ui.mark_saved(saved);
        plain_ui.mark_saved(saved);
        CHECK(!ui.view().controls_dirty && !plain_ui.view().controls_dirty);
        std::istringstream input(saved_bytes(saved));
        ControlSnapshot roundtrip;
        std::string error;
        CHECK(parse_controls(input, roundtrip, error));
        same_controls(roundtrip, saved);
    }

    void transition(unsigned step) {
        const auto before = ui.view();
        const auto session_before = read(navigated);
        const auto baseline_before = read(control);
        const auto saved_before = saved_bytes(saved);
        const auto commands_before = counts.commands;
        constexpr std::array workspaces{UiWorkspace::Rotary, UiWorkspace::Service, UiWorkspace::Play};
        const auto workspace = workspaces[step % 3];
        const auto presentation = step % 6 < 3 ? UiPresentation::Flat : UiPresentation::Dimensional;
        if (step % 3 == 0) CHECK(ui.set_workspace(workspace));
        else if (step % 3 == 1) no_actions(ui.activate({UiControlKind::Workspace,
            Manual::Upper, DrawbarBank::A, static_cast<std::uint8_t>(workspace)}));
        else tap(ui, workspace == UiWorkspace::Play ? UiKey::F4 :
                     workspace == UiWorkspace::Rotary ? UiKey::F5 : UiKey::F6);
        if (step % 2 == 0) CHECK(ui.set_presentation(presentation));
        else if (ui.view().presentation != presentation) tap(ui, UiKey::F7);
        else {
            no_actions(ui.activate({UiControlKind::Presentation}));
            no_actions(ui.activate({UiControlKind::Presentation}));
        }
        const auto size = sizes[step % sizes.size()];
        CHECK(ui.resize(size.x, size.y));
        for (unsigned tab = 0; tab < 1 + step % 3; ++tab) tap(ui, UiKey::Tab, step % 2 != 0);
        // Old Up events must retain captured pitches/owners despite changed
        // focus, manual/pedal target and both kinds of octave mapping.
        tap(ui, step % 3 == 0 ? UiKey::F1 : step % 3 == 1 ? UiKey::F2 : UiKey::F3);
        tap(ui, step % 2 == 0 ? UiKey::RightBracket : UiKey::LeftBracket);
        if (ui.view().pointer_captured)
            no_actions(ui.pointer({UiPointerKind::Move, playing_point(ui, {UiTarget::Upper, 36})}));
        CHECK(ui.view().workspace == workspace && ui.view().presentation == presentation);
        CHECK(plain_ui.view().workspace == UiWorkspace::Play);
        CHECK(plain_ui.view().presentation == UiPresentation::Dimensional);
        CHECK(plain_ui.layout().width == 1280 && plain_ui.layout().height == 900);
        same_controls(ui.view().controls, before.controls);
        same_snapshot(ui.view().applied, before.applied);
        CHECK(std::tie(ui.view().controls_dirty, ui.view().controls_pending,
                       ui.view().pointer_captured, ui.view().last_submit_status, ui.view().input_recovery) ==
              std::tie(before.controls_dirty, before.controls_pending,
                       before.pointer_captured, before.last_submit_status, before.input_recovery));
        CHECK(saved_bytes(saved) == saved_before && counts.commands == commands_before);
        same_snapshot(read(navigated), session_before);
        same_snapshot(read(control), baseline_before);
        counts.views[static_cast<std::size_t>(workspace)][static_cast<std::size_t>(presentation)] = true;
        ++counts.transitions;
    }

    void render(std::uint32_t count, Energy expected_energy = Energy::Audible,
                bool isolated_percussion = false, bool cancelled_upper = false) {
        const auto before = read(navigated);
        const auto controls = reference.controls_snapshot();
        const bool physical_detector = std::any_of(holds[0].begin(), holds[0].end(), [](bool on) { return on; });
        const bool eligible = controls.percussion.enabled && controls.route_enabled[0] &&
            controls.selected_banks[0] == DrawbarBank::B && controls.fixed_registrations[0] == FixedRegistration::None;
        const bool routed_detector = eligible && physical_detector;
        const auto percussion = make_nominal_percussion_profile();
        const long double tau = routed_detector ?
            (controls.percussion.decay == PercussionDecay::Slow ? percussion.slow_decay_seconds : percussion.fast_decay_seconds) :
            percussion.recovery_seconds;
        const long double q_before = readiness;
        std::vector<float> a(static_cast<std::size_t>(count) * 2 + 2, sentinel);
        std::vector<float> b(a.size(), sentinel), mono(static_cast<std::size_t>(count) + 2, sentinel);
        std::vector<float> upper_removed(count);
        if (cancelled_upper) {
            CHECK(!controls.route_enabled[0] && physical_detector);
            Engine muted_upper = reference;
            const std::array release{Event{0, EventType::AllNotesOff, Manual::Upper, 0, 0}};
            CHECK(muted_upper.process(0, {}, release));
            CHECK(muted_upper.process(count, upper_removed, {}));
            ++counts.cancelled_upper_blocks;
        }
        const auto x = navigated.render(count, std::span<float>{a}.subspan(1, static_cast<std::size_t>(count) * 2));
        const auto y = control.render(count, std::span<float>{b}.subspan(1, static_cast<std::size_t>(count) * 2));
        CHECK(x.ok() && y.ok() && x.frames_rendered == count && y.frames_rendered == count);
        CHECK(reference.process(count, std::span<float>{mono}.subspan(1, count), {}));
        CHECK(a.front() == sentinel && a.back() == sentinel && b.front() == sentinel && b.back() == sentinel);
        CHECK(mono.front() == sentinel && mono.back() == sentinel);
        double block_energy = 0.0, analytic_energy = 0.0;
        float block_peak = 0.0F;
        if (isolated_percussion) {
            CHECK(eligible && holds[0][24] && reference.active_key_count() == 1);
            CHECK(reference.active_pedal_count() == 0 && controls.fixed_registrations[0] == FixedRegistration::None);
            for (const auto& manual : controls.drawbars) for (const auto& bank : manual)
                CHECK(std::all_of(bank.begin(), bank.end(), [](auto value) { return value == 0; }));
        }
        for (std::uint32_t frame = 0; frame < count; ++frame) {
            const float expected = mono[1 + frame];
            CHECK(std::isfinite(expected));
            const auto bits = std::bit_cast<std::uint32_t>(expected);
            for (std::size_t channel = 0; channel < 2; ++channel) {
                const auto index = 1 + static_cast<std::size_t>(frame) * 2 + channel;
                CHECK(std::isfinite(a[index]) && std::isfinite(b[index]));
                CHECK(std::bit_cast<std::uint32_t>(a[index]) == bits);
                CHECK(std::bit_cast<std::uint32_t>(b[index]) == bits);
                hash_word(pcm_hash, bits);
                hash_word(counts.pcm_hash, bits);
                ++counts.stereo_samples;
            }
            if (cancelled_upper) CHECK(std::bit_cast<std::uint32_t>(upper_removed[frame]) == bits);
            if (isolated_percussion) {
                const auto contact = controls.percussion.harmonic == PercussionHarmonic::Second ? 3U : 4U;
                const auto tone = static_cast<std::size_t>(profile.manual_map[24][contact] - 1);
                const auto& source = profile.sources[tone];
                const long double q = q_before * std::exp(-static_cast<long double>(frame) / (spec.sample_rate * tau));
                const double level = controls.percussion.volume == PercussionVolume::Normal ? percussion.normal_gain : percussion.soft_gain;
                const double fast = controls.percussion.decay == PercussionDecay::Fast ? percussion.fast_gain_multiplier : 1.0;
                const long double analytic = source.peak_amplitude *
                    std::sin(2.0 * std::numbers::pi_v<double> * phases[tone]) * q * level * fast *
                    profile.output_gain * controls.expression;
                CHECK_NEAR(expected, analytic, 1.0e-7);
                analytic_energy += static_cast<double>(analytic * analytic);
                ++counts.isolated_samples;
            }
            for (std::size_t tone = 0; tone < phases.size(); ++tone) {
                phases[tone] += increments[tone];
                if (phases[tone] >= 1.0) phases[tone] -= 1.0;
            }
            block_peak = std::max(block_peak, std::abs(expected));
            block_energy += static_cast<double>(expected) * expected;
        }
        if (count != 0) {
            last_peak = block_peak;
            if (expected_energy == Energy::Audible) {
                CHECK(block_peak > 1.0e-7F && block_energy > 1.0e-14);
                ++counts.audible_blocks;
            } else {
                CHECK(block_peak == 0.0F && block_energy == 0.0);
                ++counts.silent_blocks;
            }
            if (isolated_percussion) {
                CHECK(analytic_energy > 1.0e-8);
                CHECK_NEAR(block_energy, analytic_energy, analytic_energy * 2.0e-7);
                isolated_energy += block_energy;
            }
        }
        const long double factor = std::exp(-static_cast<long double>(count) / (spec.sample_rate * tau));
        readiness = routed_detector ? readiness * factor : 1.0L - (1.0L - readiness) * factor;
        const auto diagnostic = reference.percussion_diagnostics();
        CHECK(diagnostic.prepared && diagnostic.physical_detector == physical_detector);
        CHECK(diagnostic.eligible == eligible && diagnostic.routed_detector == routed_detector);
        CHECK_NEAR(diagnostic.readiness, readiness, 2.0e-11);
        ++counts.readiness_checks;
        for (std::size_t tone = 0; tone < phases.size(); ++tone) {
            double actual = -1.0;
            CHECK(reference.source_phase_turns(static_cast<ToneId>(tone + 1), actual));
            CHECK(std::bit_cast<std::uint64_t>(actual) == std::bit_cast<std::uint64_t>(phases[tone]));
            ++counts.phase_checks;
        }
        const auto after = read(navigated);
        same_snapshot(after, read(control));
        same_controls(after.controls, controls);
        CHECK(after.held_keys == holds && after.held_pedals == pedals);
        CHECK(after.frame_clock == spec.initial_frame + frames + count);
        CHECK(after.frame_clock == reference.frame_clock() && after.frame_clock == before.frame_clock + count);
        CHECK(after.publication_revision == before.publication_revision + 2);
        CHECK(after.resolved_sequence == sequence && after.last_applied_sequence == sequence);
        CHECK(after.prepared && after.running && after.sample_rate == spec.sample_rate);
        CHECK(after.recovery_count == 0 && after.queue_overflows == 0 && after.rejected_commands == 0);
        CHECK(after.discarded_commands == 0 && after.fault_flags == 0 && after.last_core_status == Status::Ok);
        CHECK(std::bit_cast<std::uint32_t>(after.peak) == std::bit_cast<std::uint32_t>(last_peak));
        ui.observe(after);
        plain_ui.observe(read(control));
        same_controls(ui.view().controls, plain_ui.view().controls);
        CHECK(!ui.view().controls_pending && !plain_ui.view().controls_pending);
        CHECK(ui.view().controls_dirty == plain_ui.view().controls_dirty);
        CHECK(ui.view().controls_dirty == !(controls == saved));
        peak = std::max(peak, block_peak);
        energy += block_energy;
        frames += count;
        counts.frames += count;
        ++counts.blocks;
    }

    void finish(std::string_view kind, unsigned variant) {
        CHECK(sequence != 0 && frames > 1024 && peak > 0.0F && energy > 0.0);
        CHECK(std::none_of(pedals.begin(), pedals.end(), [](bool held) { return held; }));
        for (const auto& manual : holds)
            CHECK(std::none_of(manual.begin(), manual.end(), [](bool held) { return held; }));
        save_checkpoint();
        std::cout << "case kind=" << kind << " variant=" << variant << " rate=" << spec.sample_rate
                  << " seed=" << spec.seed << " frames=" << frames << " commands=" << sequence
                  << " peak=" << peak << " energy=" << energy << " isolated_energy=" << isolated_energy
                  << " pcm_fnv1a64=" << std::hex << pcm_hash << std::dec << '\n';
        ++counts.cases;
    }
};

// Three UI owners plus three independent channel-7 external owners. In the
// isolated scores all six owners overlap the SAME Upper C; in mixed scores
// each UI owner overlaps its corresponding external owner on another part.
using Owners = std::array<UiNote, 3>;
constexpr std::array<Owners, 3> mixed_owners{{
    {{{UiTarget::Upper, 60}, {UiTarget::Lower, 60}, {UiTarget::Pedals, 25}}},
    {{{UiTarget::Lower, 60}, {UiTarget::Pedals, 25}, {UiTarget::Upper, 60}}},
    {{{UiTarget::Pedals, 1}, {UiTarget::Upper, 60}, {UiTarget::Lower, 60}}}}};
constexpr Owners overlapping_upper{{{UiTarget::Upper, 60}, {UiTarget::Upper, 60}, {UiTarget::Upper, 60}}};

void start_owners(Pair& pair, const Owners& notes) {
    const auto target = notes[0].target == UiTarget::Upper ? UiKey::F1 :
        notes[0].target == UiTarget::Lower ? UiKey::F2 : UiKey::F3;
    tap(pair.ui, target);
    tap(pair.plain_ui, target);
    pair.dispatch(pair.ui.key({UiKey::A, true}), pair.plain_ui.key({UiKey::A, true}), owned_note(notes[0], true, 1));
    pair.physical(notes[0], true);
    pair.dispatch(pair.ui.pointer({UiPointerKind::Down, playing_point(pair.ui, notes[1])}),
                  pair.plain_ui.pointer({UiPointerKind::Down, playing_point(pair.plain_ui, notes[1])}),
                  owned_note(notes[1], true, 100));
    if (notes[1] != notes[0]) pair.physical(notes[1], true);
    no_actions(pair.ui.activate(note_id(notes[2])));
    no_actions(pair.plain_ui.activate(note_id(notes[2])));
    pair.dispatch(pair.ui.key({UiKey::Space, true}), pair.plain_ui.key({UiKey::Space, true}), owned_note(notes[2], true, 101));
    if (notes[2] != notes[0] && notes[2] != notes[1]) pair.physical(notes[2], true);
    for (std::size_t owner = 0; owner < notes.size(); ++owner) {
        const auto command = owned_note(notes[owner], true, 700 + static_cast<std::int32_t>(owner), 7);
        pair.post(command, command);
    }
}

void release_ui_owners(Pair& pair, const Owners& notes, bool isolated = false) {
    pair.dispatch(pair.ui.key({UiKey::A, false}), pair.plain_ui.key({UiKey::A, false}), owned_note(notes[0], false, 1));
    pair.transition(13);
    pair.render(127, Energy::Audible, isolated);
    pair.dispatch(pair.ui.pointer({UiPointerKind::Up, {-300, -300}}),
                  pair.plain_ui.pointer({UiPointerKind::Up, {-300, -300}}), owned_note(notes[1], false, 100));
    pair.transition(14);
    pair.render(257, Energy::Audible, isolated);
    pair.dispatch(pair.ui.key({UiKey::Space, false}), pair.plain_ui.key({UiKey::Space, false}), owned_note(notes[2], false, 101));
    pair.transition(15);
    pair.render(509, Energy::Audible, isolated);
    CHECK(!pair.ui.view().pointer_captured && !pair.plain_ui.view().pointer_captured);
}

void release_external_owners(Pair& pair, const Owners& notes, bool isolated = false,
                             Energy after_second = Energy::Audible) {
    for (std::size_t owner = 0; owner < notes.size(); ++owner) {
        const auto command = owned_note(notes[owner], false, 700 + static_cast<std::int32_t>(owner), 7);
        pair.post(command, command);
        bool last = true;
        for (std::size_t later = owner + 1; later < notes.size(); ++later)
            if (notes[later] == notes[owner]) last = false;
        if (last) pair.physical(notes[owner], false);
        pair.transition(16 + static_cast<unsigned>(owner));
        pair.render(113 + static_cast<std::uint32_t>(owner) * 32,
                    owner == 2 ? Energy::Silent : owner == 1 ? after_second : Energy::Audible,
                    isolated && owner != 2);
    }
}

ControlSnapshot registration(unsigned variant) {
    ControlSnapshot controls;
    for (std::size_t manual = 0; manual < 2; ++manual)
        for (std::size_t bank = 0; bank < 2; ++bank)
            for (std::size_t drawbar = 0; drawbar < 9; ++drawbar)
                controls.drawbars[manual][bank][drawbar] = static_cast<std::uint8_t>(
                    (manual * 5 + bank * 3 + drawbar + variant) % 9);
    controls.expression = 0.75;
    controls.pedal_drawbars = {8, 5};
    controls.percussion = {variant < 8,
        (variant & 1U) != 0 ? PercussionHarmonic::Third : PercussionHarmonic::Second,
        (variant & 2U) != 0 ? PercussionVolume::Soft : PercussionVolume::Normal,
        (variant & 4U) != 0 ? PercussionDecay::Fast : PercussionDecay::Slow};
    ControlState state;
    CHECK(state.restore(controls));
    CHECK(state.select_preset(Manual::Upper, static_cast<PresetSelection>(variant % 12)));
    CHECK(state.select_preset(Manual::Lower, static_cast<PresetSelection>(11 - variant % 12)));
    return state.snapshot();
}

void future_probe(Pair& pair, bool isolated = false) {
    for (unsigned step = 19; step < 22; ++step) {
        pair.transition(step);
        pair.render(step == 19 ? 37 : step == 20 ? 509 : 1024, Energy::Silent);
    }
    // A later held note makes accumulated silent phase/recovery audible. There
    // is no prepare, load, Panic or phase/readiness reset at this new attack.
    constexpr UiNote note{UiTarget::Upper, 60};
    const auto on = owned_note(note, true, 900, 9);
    pair.post(on, on);
    pair.physical(note, true);
    pair.transition(22);
    pair.render(1024, Energy::Audible, isolated);
    pair.transition(23);
    pair.render(997, Energy::Audible, isolated);
    const auto off = owned_note(note, false, 900, 9);
    pair.post(off, off);
    pair.physical(note, false);
    pair.render(257, Energy::Silent);
}

void registration_scores(const RuntimeProfile& profile, double rate) {
    for (unsigned variant = 0; variant < 12; ++variant) {
        Pair pair(profile, rate, 0xB32600ULL + variant);
        pair.load(registration(variant));
        pair.render(0);
        const auto& owners = mixed_owners[variant % mixed_owners.size()];
        start_owners(pair, owners);
        pair.render(127);
        constexpr std::array<std::uint32_t, 6> blocks{1, 7, 31, 64, 257, 1024};
        for (unsigned step = 0; step < blocks.size(); ++step) {
            pair.transition(step);
            pair.render(blocks[step]);
        }
        (void)pair.parameter(20480, 11); // Eligible adjustable Upper B.
        (void)pair.parameter(12288, 1);
        pair.transition(6);
        pair.render(509);
        CHECK(pair.reference.percussion_diagnostics().eligible);
        CHECK(pair.reference.percussion_diagnostics().readiness < 1.0);
        (void)pair.parameter(20480, 1 + variant % 9); // Fixed mode is ineligible.
        pair.transition(7);
        pair.render(333);
        CHECK(!pair.reference.percussion_diagnostics().eligible);
        (void)pair.parameter(20480, 0); // Cancel preserves every held owner.
        pair.transition(8);
        pair.render(257, Energy::Audible, false, true);
        (void)pair.parameter(20480, 10); // Upper A remains ineligible.
        pair.transition(9);
        pair.render(64);
        CHECK(!pair.reference.percussion_diagnostics().eligible);
        (void)pair.parameter(20480, 11); // Resume the same Upper B history.
        pair.transition(10);
        pair.render(1024);
        CHECK(pair.reference.percussion_diagnostics().readiness < 1.0);
        pair.save_checkpoint();
        release_ui_owners(pair, owners);
        // Variant 11 retains Lower Cancel. Its last surviving owner is Lower;
        // after the Upper release that held, disconnected route is silent.
        release_external_owners(pair, owners, false,
            variant == 11 ? Energy::Silent : Energy::Audible);
        future_probe(pair);
        pair.finish("registration", variant);
    }
}

double plain_value(const ControlSnapshot& state, const ParameterDescriptor& descriptor) {
    const auto manual = static_cast<std::size_t>(descriptor.manual);
    switch (descriptor.event_type) {
    case EventType::BankDrawbar: return state.drawbars[manual][descriptor.index / 9][descriptor.index % 9];
    case EventType::Expression: return state.expression;
    case EventType::SelectBank: return static_cast<double>(state.selected_banks[manual]);
    case EventType::PedalDrawbar: return state.pedal_drawbars[descriptor.index];
    case EventType::SelectPreset: {
        PresetSelection selected;
        CHECK(control_preset_selection(state, descriptor.manual, selected));
        return static_cast<double>(selected);
    }
    case EventType::Percussion:
        switch (descriptor.index) {
        case 0: return state.percussion.enabled ? 1.0 : 0.0;
        case 1: return static_cast<double>(state.percussion.harmonic);
        case 2: return static_cast<double>(state.percussion.volume);
        case 3: return static_cast<double>(state.percussion.decay);
        default: break;
        }
        break;
    default: break;
    }
    hammond_test::fail("known literal parameter", __FILE__, __LINE__);
}

void all_parameter_score(const RuntimeProfile& profile, double rate) {
    Pair pair(profile, rate, 0xB32647);
    pair.load(registration(11));
    pair.render(0);
    const auto& owners = mixed_owners[0];
    start_owners(pair, owners);
    pair.render(127);
    const auto descriptors = parameter_descriptors();
    constexpr std::array<std::uint32_t, 8> blocks{1, 7, 31, 64, 127, 509, 1024, 257};
    for (std::size_t index = 0; index < parameter_ids.size(); ++index) {
        CHECK(descriptors[index].id == parameter_ids[index]);
        const double old = plain_value(pair.ui.view().controls, descriptors[index]);
        const double next = parameter_ids[index] == 8192 ? 0.375 :
            descriptors[index].maximum == 8 ? std::fmod(old + 3, 9) :
            descriptors[index].maximum == 11 ? (old == 11 ? 2 : 11) : 1 - old;
        CHECK(pair.parameter(parameter_ids[index], next));
        ++counts.parameter_edits;
        pair.transition(static_cast<unsigned>(index));
        if (index % 8 == 0) pair.render(0);
        pair.render(blocks[index % blocks.size()]);
    }
    pair.save_checkpoint();
    (void)pair.parameter(20480, 11);
    (void)pair.parameter(12288, 1);
    pair.render(509);
    release_ui_owners(pair, owners);
    release_external_owners(pair, owners);
    future_probe(pair);
    pair.finish("47-parameters", 0);
}

void isolated_percussion_scores(const RuntimeProfile& profile, double rate) {
    for (unsigned variant = 0; variant < 8; ++variant) {
        Pair pair(profile, rate, 0xB32680ULL + variant);
        ControlSnapshot controls;
        controls.expression = 0.625;
        controls.percussion = registration(variant).percussion;
        CHECK(controls.percussion.enabled);
        pair.load(controls); // All 36 manual and both pedal drawbars are zero.
        pair.render(0);
        start_owners(pair, overlapping_upper);
        pair.render(509, Energy::Audible, true);
        constexpr std::array<std::uint32_t, 12> blocks{
            1024, 257, 511, 64, 997, 127, 1024, 31, 509, 1024, 257, 1024};
        for (unsigned step = 0; step < blocks.size(); ++step) {
            pair.transition(step);
            pair.render(blocks[step], Energy::Audible, true);
        }
        const double depleted = pair.reference.percussion_diagnostics().readiness;
        CHECK(depleted > 0.0 && depleted < 0.98);
        for (const double selection : {10.0, 0.0}) {
            CHECK(pair.parameter(20480, selection));
            pair.transition(6);
            pair.render(509, Energy::Silent);
            CHECK(pair.reference.percussion_diagnostics().readiness > depleted);
            CHECK(pair.parameter(20480, 11));
            pair.transition(7);
            pair.render(257, Energy::Audible, true);
        }
        CHECK(pair.parameter(12288, 0));
        pair.transition(8);
        pair.render(127, Energy::Silent);
        CHECK(pair.parameter(12288, 1));
        pair.transition(9);
        pair.render(257, Energy::Audible, true);
        pair.save_checkpoint();
        release_ui_owners(pair, overlapping_upper, true);
        release_external_owners(pair, overlapping_upper, true);
        future_probe(pair, true);
        CHECK(pair.isolated_energy > 1.0e-4);
        pair.finish("isolated-percussion", variant);
    }
}

} // namespace

int main() {
    const auto profile = load_test_profile();
    std::cout << std::setprecision(17);
    for (const double rate : {44100.0, 48000.0, 96000.0}) {
        registration_scores(profile, rate);
        all_parameter_score(profile, rate);
        isolated_percussion_scores(profile, rate);
    }
    CHECK(counts.cases == 63 && counts.parameter_edits == 141);
    CHECK(counts.cancelled_upper_blocks == 36 && counts.isolated_samples > 100000);
    for (const auto& workspace : counts.views) for (const bool visited : workspace) CHECK(visited);
    std::cout << "workspace musical continuity: cases=" << counts.cases << " blocks=" << counts.blocks
              << " frames=" << counts.frames << " paired_stereo_samples=" << counts.stereo_samples
              << " matched_commands=" << counts.commands << " transitions=" << counts.transitions
              << " zero_action_checks=" << counts.zero_action_checks << " view_commands=0"
              << " state_byte_comparisons=" << counts.serialized_comparisons
              << " phase_checks=" << counts.phase_checks << " readiness_checks=" << counts.readiness_checks
              << " parameter_edits=" << counts.parameter_edits << " audible_blocks=" << counts.audible_blocks
              << " silent_blocks=" << counts.silent_blocks << " isolated_samples=" << counts.isolated_samples
              << " cancelled_upper_blocks=" << counts.cancelled_upper_blocks
              << " pcm_fnv1a64=" << std::hex << counts.pcm_hash << std::dec << '\n';
    return 0;
}
