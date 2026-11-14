#include "InspectionModel.h"
#include "InstrumentView.h"

#include "hammond/ControlStateIO.h"
#include "hammond/Profile.h"

#include <SDL.h>

#include <algorithm>
#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <locale>
#include <memory>
#include <stdexcept>
#include <string>
#include <string_view>
#include <variant>
#include <vector>

// Native rendering harness: actual Session queue, UiModel, Drawing and
// InstrumentView; no application window, AudioDevice, callback or timing hook.
namespace {
using namespace hammond;
using namespace hammond::standalone;
using Pixel = std::array<std::uint8_t, 4>;
std::size_t assertions = 0;

void require(bool condition, std::string_view detail) {
    ++assertions;
    if (!condition) throw std::runtime_error(std::string(detail));
}

SessionSnapshot read(const Session& session) {
    SessionSnapshot result;
    require(session.read_snapshot(result), "read real Session publication");
    require(result.fault_flags == 0 && result.last_core_status == Status::Ok &&
            result.recovery_count == 0 && result.queue_overflows == 0 &&
            result.rejected_commands == 0 && result.discarded_commands == 0,
            "real Session publication has no faults, recovery or discarded commands");
    return result;
}

bool same_publication(const SessionSnapshot& a, const SessionSnapshot& b) {
    return a.controls == b.controls && a.held_keys == b.held_keys &&
        a.held_pedals == b.held_pedals && a.frame_clock == b.frame_clock &&
        a.sample_rate == b.sample_rate && a.peak == b.peak &&
        a.prepared == b.prepared && a.running == b.running &&
        a.publication_revision == b.publication_revision &&
        a.resolved_sequence == b.resolved_sequence &&
        a.last_applied_sequence == b.last_applied_sequence &&
        a.recovery_count == b.recovery_count && a.queue_overflows == b.queue_overflows &&
        a.rejected_commands == b.rejected_commands &&
        a.discarded_commands == b.discarded_commands &&
        a.fault_flags == b.fault_flags && a.last_core_status == b.last_core_status;
}

void held_a_only(const SessionSnapshot& snapshot, bool held) {
    for (std::size_t manual = 0; manual < kManualCount; ++manual)
        for (std::size_t key = 0; key < kManualKeyCount; ++key)
            require(snapshot.held_keys[manual][key] ==
                    (held && manual == 0 && key == 60 - kMinManualMidiNote),
                    "only the original Upper MIDI 60 target is held");
    require(std::none_of(snapshot.held_pedals.begin(), snapshot.held_pedals.end(),
                        [](bool value) { return value; }), "pedals remain released");
}

struct Queued {
    SessionCommand command;
    SubmitResult result;
};

Queued dispatch(Session& session, UiModel& ui, const UiActions& actions) {
    require(actions.count == 1, "actual UiModel gesture emits exactly one action");
    const auto* command = std::get_if<SessionCommand>(&actions.items[0]);
    require(command != nullptr, "actual UiModel action is a Session command");
    const auto result = session.post(*command);
    const auto recovery = ui.submitted(*command, result);
    require(result.ok() && result.sequence != 0, "Session accepts copied command with a sequence");
    require(recovery.count == 0, "immediate UiModel submitted acknowledgement needs no recovery");
    return {*command, result};
}

HostNoteEvent note_command(const Queued& queued, HostNoteKind kind) {
    const auto* input = std::get_if<PerformanceInputEvent>(&queued.command);
    require(input != nullptr, "key gesture submits actual performance input");
    const auto* note = std::get_if<HostNoteEvent>(input);
    require(note != nullptr, "key gesture submits a manual note event");
    require(note->offset == 0 && note->kind == kind && note->bus == 0 &&
            note->channel == kUiInputChannel && note->midi_note == 60 &&
            note->note_id == kUiKeyboardOwnerBase &&
            note->velocity == (kind == HostNoteKind::On ? kUiNoteVelocity : 0),
            "A key retains exact Upper MIDI 60/channel 0/owner 1 identity");
    return *note;
}

PresetSelection selection(const ControlSnapshot& controls) {
    PresetSelection result;
    require(control_preset_selection(controls, Manual::Upper, result), "valid Upper selection");
    return result;
}

const InspectionRow& row(const InspectionDocument& document, std::string_view id) {
    for (const auto& section : document.sections)
        for (std::size_t index = 0; index < section.row_count; ++index)
            if (section.rows[index].id == id) return section.rows[index];
    throw std::runtime_error("missing required inspection row: " + std::string(id));
}

std::string row_text(const InspectionRow& value) {
    return std::string(value.value.view()) +
        (value.unit.empty() ? "" : " " + std::string(value.unit));
}

InspectionDocument inspect(const RuntimeProfile& profile, const UiModel& ui, bool pending) {
    const auto document = make_inspection_document(profile, ui.view(), {true, true});
    require(document.snapshot_state == InspectionSnapshotState::Current &&
            document.controls_pending == pending, "inspection is Current with exact pending status");
    require(document.frame_clock == ui.view().applied.frame_clock &&
            document.publication_revision == ui.view().applied.publication_revision,
            "inspection retains actual publication frame and revision");
    require(row_text(row(document, "controls.upper")) ==
            (pending ? "Sound Bank B / Edit B" : "Sound Fixed F / Edit B"),
            "inspection reports applied Upper selection, independently from desired F");
    for (const auto id : {"contacts.upper_held", "contacts.lower_held", "contacts.pedals_held"}) {
        const auto& value = row(document, id);
        require(row_text(value) == (id == std::string_view("contacts.upper_held") ? "1 target" : "0 targets"),
                "native inspection uses singular/plural held-target units");
        require(value.availability == InspectionAvailability::Available &&
                value.evidence == InspectionEvidence::Software,
                "held target is available software evidence, not audibility evidence");
    }
    return document;
}

struct Frame {
    std::string stage, workspace, file, renderer;
    int width{}, height{};
    std::uint32_t renderer_flags{};
    InspectionDocument document;
    std::vector<Pixel> pixels;
};

Frame paint(Session& session, UiModel& ui, const RuntimeProfile& profile,
            bool pending, UiWorkspace workspace, int width, int height,
            const std::filesystem::path& capture_directory) {
    const auto before = read(session);
    const auto desired = ui.view().controls;
    require(ui.resize(static_cast<float>(width), static_cast<float>(height)), "resize actual UiModel");
    require(ui.activate({UiControlKind::Workspace, Manual::Upper, DrawbarBank::A,
                        static_cast<std::uint8_t>(workspace)}).count == 0,
            "workspace change emits no musical command");
    require(ui.view().workspace == workspace && ui.view().controls == desired &&
            ui.view().controls_pending == pending && same_publication(ui.view().applied, before),
            "workspace/resize preserve desired, applied, pending and held state");
    Frame frame;
    frame.stage = pending ? "pending" : "acknowledged";
    frame.workspace = workspace == UiWorkspace::Play ? "Play" : "Service";
    frame.width = width;
    frame.height = height;
    frame.document = inspect(profile, ui, pending);
    const std::unique_ptr<SDL_Surface, decltype(&SDL_FreeSurface)> surface(
        SDL_CreateRGBSurfaceWithFormat(0, width, height, 32, SDL_PIXELFORMAT_RGBA32), SDL_FreeSurface);
    require(surface != nullptr, "create SDL RGBA32 software surface");
    const std::unique_ptr<SDL_Renderer, decltype(&SDL_DestroyRenderer)> renderer(
        SDL_CreateSoftwareRenderer(surface.get()), SDL_DestroyRenderer);
    require(renderer != nullptr, "create SDL software renderer");
    SDL_RendererInfo renderer_info{};
    require(SDL_GetRendererInfo(renderer.get(), &renderer_info) == 0 && renderer_info.name != nullptr,
            "read actual renderer information");
    require((renderer_info.flags & SDL_RENDERER_SOFTWARE) != 0, "renderer reports software operation");
    frame.renderer = renderer_info.name;
    frame.renderer_flags = renderer_info.flags;
    Drawing drawing(renderer.get());
    std::string error;
    const bool initialized = drawing.initialize(error);
    require(initialized, "initialize actual Drawing: " + error);
    InstrumentViewInfo info;
    info.inspection = &frame.document;
    info.status_message = "Native rendering harness: no window or audio device";
    paint_instrument(drawing, ui, info);
    require(SDL_RenderFlush(renderer.get()) == 0, "flush actual native painter before capture");
    frame.pixels.resize(static_cast<std::size_t>(width) * static_cast<std::size_t>(height));
    static_assert(sizeof(Pixel) == 4);
    require(SDL_RenderReadPixels(renderer.get(), nullptr, SDL_PIXELFORMAT_RGBA32,
            frame.pixels.data(), width * 4) == 0, "read native pixels before Present");
    require(std::any_of(frame.pixels.begin(), frame.pixels.end(), [&](const Pixel& pixel) {
                return pixel != frame.pixels.front(); }), "actual native frame contains painted content");
    if (!capture_directory.empty()) {
        frame.file = frame.stage + "-" + (workspace == UiWorkspace::Play ? "play-" : "service-") +
            std::to_string(width) + "x" + std::to_string(height) + ".bmp";
        const bool saved = drawing.save_bmp((capture_directory / frame.file).string(), error);
        require(saved, "save actual native BMP before Present: " + error);
    }
    SDL_RenderPresent(renderer.get());
    require(same_publication(read(session), before), "painting does not publish, flush or advance Session");
    return frame;
}

void json_string(std::ostream& out, std::string_view value) {
    constexpr char hex[] = "0123456789abcdef";
    out << '"';
    for (const char byte : value) {
        const auto character = static_cast<unsigned char>(byte);
        if (character == '"' || character == '\\') out << '\\' << static_cast<char>(character);
        else if (character < 0x20) out << "\\u00" << hex[character >> 4] << hex[character & 15];
        else out << static_cast<char>(character);
    }
    out << '"';
}

void controls_json(std::ostream& out, const ControlSnapshot& controls) {
    std::string serialized, error;
    const bool success = serialize_controls(controls, serialized, error);
    require(success, "serialize the complete actual control copy: " + error);
    json_string(out, serialized);
}

void snapshot_json(std::ostream& out, const SessionSnapshot& snapshot) {
    out << "{\"frame_clock\":" << snapshot.frame_clock
        << ",\"publication_revision\":" << snapshot.publication_revision
        << ",\"resolved_sequence\":" << snapshot.resolved_sequence
        << ",\"last_applied_sequence\":" << snapshot.last_applied_sequence
        << ",\"prepared\":" << snapshot.prepared << ",\"running\":" << snapshot.running
        << ",\"sample_rate\":" << snapshot.sample_rate << ",\"peak\":" << snapshot.peak
        << ",\"fault_flags\":" << snapshot.fault_flags
        << ",\"last_core_status\":" << static_cast<unsigned>(snapshot.last_core_status)
        << ",\"recovery_count\":" << snapshot.recovery_count
        << ",\"queue_overflows\":" << snapshot.queue_overflows
        << ",\"rejected_commands\":" << snapshot.rejected_commands
        << ",\"discarded_commands\":" << snapshot.discarded_commands
        << ",\"held_manual_midi\":[";
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        if (manual != 0) out << ',';
        out << '[';
        bool first = true;
        for (std::size_t key = 0; key < kManualKeyCount; ++key) {
            if (!snapshot.held_keys[manual][key]) continue;
            if (!first) out << ',';
            out << key + kMinManualMidiNote;
            first = false;
        }
        out << ']';
    }
    out << "],\"held_pedal_ids\":[";
    bool first = true;
    for (std::size_t key = 0; key < kPedalCount; ++key) {
        if (!snapshot.held_pedals[key]) continue;
        if (!first) out << ',';
        out << key + 1;
        first = false;
    }
    out << "],\"applied_controls_state4\":";
    controls_json(out, snapshot.controls);
    out << '}';
}

void note_json(std::ostream& out, const HostNoteEvent& note, std::uint64_t sequence) {
    out << "{\"kind\":\"" << (note.kind == HostNoteKind::On ? "On" : "Off")
        << "\",\"offset\":" << note.offset << ",\"bus\":" << static_cast<unsigned>(note.bus)
        << ",\"channel\":" << static_cast<unsigned>(note.channel)
        << ",\"midi_note\":" << static_cast<unsigned>(note.midi_note)
        << ",\"velocity\":" << static_cast<unsigned>(note.velocity)
        << ",\"note_id\":" << note.note_id << ",\"sequence\":" << sequence << '}';
}

void write_metadata(const std::filesystem::path& directory, const char* executable,
                    const RuntimeProfile& profile, const std::array<SessionSnapshot, 6>& observations,
                    const ControlSnapshot& desired, const std::array<Queued, 3>& commands,
                    const HostNoteEvent& on, const HostNoteEvent& off,
                    const std::array<Frame, 6>& frames, const std::array<std::size_t, 3>& changed) {
    std::ofstream out(directory / "metadata.json", std::ios::binary);
    require(out.good(), "open new capture metadata");
    out.imbue(std::locale::classic());
    out << std::boolalpha << std::setprecision(17)
        << "{\"schema_version\":1,\"evidence_kind\":\"native rendering harness captures, no application window or audio device\","
        << "\"source_root\":";
    json_string(out, HAMMOND_TEST_SOURCE_ROOT);
    out << ",\"executable\":";
    json_string(out, std::filesystem::absolute(executable).lexically_normal().string());
    out << ",\"profile\":{\"path\":";
    json_string(out, HAMMOND_TEST_PROFILE);
    out << ",\"id\":";
    json_string(out, profile.profile_id.data());
    out << ",\"authoring_sha256\":";
    json_string(out, profile.authoring_sha256.data());
    SDL_version version{};
    SDL_GetVersion(&version);
    out << "},\"runtime\":{\"sdl_version\":\"" << static_cast<unsigned>(version.major) << '.'
        << static_cast<unsigned>(version.minor) << '.' << static_cast<unsigned>(version.patch)
        << "\",\"sdl_initialized_subsystems\":" << SDL_WasInit(0)
        << ",\"application_window\":false,\"audio_device\":false,\"surface_format\":\"RGBA32\","
        << "\"capture_before_present\":true},\"prepare\":{\"sample_rate\":48000,\"max_block_frames\":64,\"seed\":819,\"initial_frame\":0},"
        << "\"commands\":{\"key_down\":";
    note_json(out, on, commands[0].result.sequence);
    out << ",\"preset\":{\"gesture\":\"UiModel::activate Upper PresetKey F\",\"command\":\"ControlSnapshot\",\"sequence\":"
        << commands[1].result.sequence << ",\"controls_state4\":";
    controls_json(out, desired);
    out << "},\"key_up\":";
    note_json(out, off, commands[2].result.sequence);
    out << "},\"observations\":{";
    constexpr std::array<std::string_view, 6> names{"started", "held", "pending", "acknowledged", "released", "stopped"};
    for (std::size_t index = 0; index < observations.size(); ++index) {
        if (index != 0) out << ',';
        json_string(out, names[index]);
        out << ':';
        snapshot_json(out, observations[index]);
    }
    out << "},\"desired_controls_state4\":";
    controls_json(out, desired);
    out << ",\"assertions\":{\"pending_unresolved\":"
        << (observations[2].resolved_sequence < commands[1].result.sequence)
        << ",\"pending_controls_differ\":" << (desired != observations[2].controls)
        << ",\"acknowledged_controls_equal\":" << (desired == observations[3].controls)
        << ",\"zero_frame_clock_unchanged\":" << (observations[2].frame_clock == observations[3].frame_clock)
        << ",\"zero_frame_holds_unchanged\":" << (observations[2].held_keys == observations[3].held_keys &&
                                                   observations[2].held_pedals == observations[3].held_pedals)
        << ",\"acknowledgement_publication_advanced\":"
        << (observations[3].publication_revision == observations[2].publication_revision + 2)
        << ",\"release_owner_matches\":" << (on.note_id == off.note_id && on.bus == off.bus &&
                                               on.channel == off.channel && on.midi_note == off.midi_note)
        << ",\"frames\":6},\"captures\":[";
    for (std::size_t index = 0; index < frames.size(); ++index) {
        const auto& frame = frames[index];
        if (index != 0) out << ',';
        out << "{\"file\":"; json_string(out, frame.file);
        out << ",\"stage\":"; json_string(out, frame.stage);
        out << ",\"workspace\":"; json_string(out, frame.workspace);
        out << ",\"renderer\":"; json_string(out, frame.renderer);
        out << ",\"renderer_flags\":" << frame.renderer_flags << ",\"width\":" << frame.width
            << ",\"height\":" << frame.height << ",\"snapshot_state\":\"Current\",\"controls_pending\":"
            << frame.document.controls_pending << ",\"frame_clock\":" << frame.document.frame_clock
            << ",\"publication_revision\":" << frame.document.publication_revision << ",\"rows\":{";
        bool first_row = true;
        for (const auto id : {"controls.upper", "contacts.upper_held", "contacts.lower_held", "contacts.pedals_held"}) {
            if (!first_row) out << ',';
            json_string(out, id); out << ':'; json_string(out, row_text(row(frame.document, id)));
            first_row = false;
        }
        out << "}}";
    }
    out << "],\"changed_pixels_pending_to_acknowledged\":[" << changed[0] << ',' << changed[1] << ',' << changed[2]
        << "],\"assertions_passed_before_metadata_close\":" << assertions << "}\n";
    out.close();
    require(out.good(), "complete capture metadata write");
}

void run(const std::filesystem::path& directory, const char* executable) {
    RuntimeProfile profile;
    std::string error;
    const bool loaded = load_runtime_profile_file(HAMMOND_TEST_PROFILE, profile, error);
    require(loaded, "load unchanged compiled nominal profile: " + error);
    Session session;
    UiModel ui;
    require(session.prepare(profile, {48000.0, 64, 819, 0}) == SessionStatus::Ok, "prepare real nominal Session");
    require(session.start() == SessionStatus::Ok, "start real Session without audio device");
    std::array<SessionSnapshot, 6> observations;
    observations[0] = read(session);
    ui.observe(observations[0]);
    require(ui.resize(1672.0F, 941.0F), "initial reference resize");
    require(observations[0].prepared && observations[0].running && observations[0].frame_clock == 0 &&
            observations[0].resolved_sequence == 0 && observations[0].last_applied_sequence == 0,
            "prepared running initial publication has no elapsed frames or applied command");
    held_a_only(observations[0], false);

    std::array<Queued, 3> commands;
    commands[0] = dispatch(session, ui, ui.key({UiKey::A, true}));
    const auto on = note_command(commands[0], HostNoteKind::On);
    require(commands[0].result.sequence == 1, "first real note command has sequence 1");
    std::array<float, 64> stereo{};
    const auto rendered = session.render(32, stereo);
    require(rendered.ok() && rendered.frames_rendered == 32, "render 32 actual stereo frames");
    observations[1] = read(session);
    ui.observe(observations[1]);
    held_a_only(observations[1], true);
    require(observations[1].frame_clock == 32 && observations[1].resolved_sequence == 1 &&
            observations[1].last_applied_sequence == 1 &&
            observations[1].publication_revision == observations[0].publication_revision + 2,
            "held publication advances exactly 32 frames and acknowledges note sequence 1");

    commands[1] = dispatch(session, ui, ui.activate({UiControlKind::PresetKey, Manual::Upper,
        DrawbarBank::A, static_cast<std::uint8_t>(PresetSelection::F)}));
    const auto q = commands[1].result.sequence;
    const auto* requested = std::get_if<ControlSnapshot>(&commands[1].command);
    require(requested != nullptr && *requested == ui.view().controls && q == 2,
            "preset action queues desired whole ControlSnapshot at sequence 2");
    const auto desired = *requested;
    observations[2] = read(session); // No render between posting q and this genuine publication.
    ui.observe(observations[2]);
    require(same_publication(observations[2], observations[1]) && observations[2].resolved_sequence < q,
            "pre-flush read is precisely the old held publication with unresolved preset sequence");
    require(selection(ui.view().controls) == PresetSelection::F &&
            selection(ui.view().applied.controls) == PresetSelection::BankB &&
            ui.view().controls != ui.view().applied.controls && ui.view().controls_pending,
            "real pending view separates desired Fixed F from applied Bank B");
    held_a_only(observations[2], true);

    std::array<Frame, 6> frames;
    constexpr std::array<UiWorkspace, 3> workspaces{UiWorkspace::Play, UiWorkspace::Service, UiWorkspace::Service};
    constexpr std::array<int, 3> widths{1672, 1672, 960}, heights{941, 941, 700};
    for (std::size_t index = 0; index < 3; ++index)
        frames[index] = paint(session, ui, profile, true, workspaces[index], widths[index], heights[index], directory);

    const auto flushed = session.render(0, {});
    require(flushed.ok() && flushed.frames_rendered == 0, "zero-frame render applies queued preset");
    observations[3] = read(session);
    ui.observe(observations[3]);
    require(observations[3].resolved_sequence == q && observations[3].last_applied_sequence == q &&
            observations[3].publication_revision == observations[2].publication_revision + 2,
            "zero-frame acknowledgement resolves/applies exactly q and publishes one newer revision");
    require(observations[3].frame_clock == observations[2].frame_clock &&
            observations[3].held_keys == observations[2].held_keys &&
            observations[3].held_pedals == observations[2].held_pedals &&
            observations[3].peak == observations[2].peak,
            "zero-frame acknowledgement preserves clock, held targets and previous peak");
    require(!ui.view().controls_pending && ui.view().controls == desired &&
            ui.view().controls == ui.view().applied.controls && selection(ui.view().applied.controls) == PresetSelection::F,
            "acknowledged desired/applied whole controls agree and pending clears");
    held_a_only(observations[3], true);
    std::array<std::size_t, 3> changed{};
    for (std::size_t index = 0; index < 3; ++index) {
        frames[index + 3] = paint(session, ui, profile, false, workspaces[index], widths[index], heights[index], directory);
        for (std::size_t pixel = 0; pixel < frames[index].pixels.size(); ++pixel)
            if (frames[index].pixels[pixel] != frames[index + 3].pixels[pixel]) ++changed[index];
        require(changed[index] != 0, "actual pending and acknowledged native pixels differ");
    }

    commands[2] = dispatch(session, ui, ui.key({UiKey::A, false}));
    const auto off = note_command(commands[2], HostNoteKind::Off);
    require(commands[2].result.sequence == q + 1 && off.note_id == on.note_id,
            "key release retains original owner after workspace/resize/preset changes");
    const auto released = session.render(0, {});
    require(released.ok() && released.frames_rendered == 0, "flush actual key release with zero frames");
    observations[4] = read(session);
    ui.observe(observations[4]);
    held_a_only(observations[4], false);
    require(observations[4].frame_clock == 32 && observations[4].resolved_sequence == q + 1 &&
            observations[4].last_applied_sequence == q + 1 && observations[4].controls == desired &&
            observations[4].publication_revision == observations[3].publication_revision + 2,
            "release clears held target without changing clock or applied preset");
    require(session.stop() == SessionStatus::Ok, "stop quiescent Session");
    observations[5] = read(session);
    ui.observe(observations[5]);
    held_a_only(observations[5], false);
    require(!observations[5].running && observations[5].prepared && observations[5].frame_clock == 32 &&
            observations[5].controls == desired && observations[5].resolved_sequence == q + 1 &&
            observations[5].last_applied_sequence == q + 1 &&
            observations[5].publication_revision == observations[4].publication_revision + 2,
            "orderly stop preserves clock and acknowledged controls with no owners");
    require(SDL_WasInit(0) == 0, "no SDL hardware subsystem was initialized");
    if (!directory.empty()) write_metadata(directory, executable, profile, observations, desired, commands, on, off, frames, changed);
    std::cout << "Native inspection rendering harness: 6 frames; q=" << q
              << "; frame clock pending/acknowledged=" << observations[2].frame_clock << '/' << observations[3].frame_clock
              << "; publication pending/acknowledged=" << observations[2].publication_revision << '/' << observations[3].publication_revision
              << "; changed pixels=" << changed[0] << ',' << changed[1] << ',' << changed[2]
              << "; assertions=" << assertions << "; no application window or audio device\n";
}
} // namespace

int main(int argc, char** argv) {
    SDL_SetMainReady();
    const auto started = std::chrono::steady_clock::now();
    try {
        require(argc == 1 || (argc == 3 && std::string_view(argv[1]) == "--capture-dir"),
                "usage: test_standalone_inspection_raster [--capture-dir NEW_DIRECTORY]");
        std::filesystem::path directory;
        if (argc == 3) {
            directory = argv[2];
            require(!directory.empty(), "capture directory must not be empty");
            require(std::filesystem::create_directory(directory), "capture directory must be new; refusing overwrite");
        }
        require(SDL_Init(0) == 0, "initialize SDL without hardware subsystems");
        run(directory, argv[0]);
        SDL_Quit();
    } catch (const std::exception& error) {
        std::cerr << "Native inspection rendering harness failed: " << error.what() << '\n';
        SDL_Quit();
        return EXIT_FAILURE;
    }
    std::cout << "Elapsed " << std::chrono::duration<double>(std::chrono::steady_clock::now() - started).count()
              << " seconds\n";
    return EXIT_SUCCESS;
}
