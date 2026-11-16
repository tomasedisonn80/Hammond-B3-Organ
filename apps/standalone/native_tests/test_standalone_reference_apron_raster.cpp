#include "InstrumentView.h"

#include <SDL.h>

#include <algorithm>
#include <array>
#include <charconv>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <limits>
#include <locale>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

#ifdef _WIN32
#include <cstdio>
#include <fcntl.h>
#include <io.h>
#endif

// Frozen pre-edit fixture for REFERENCE_APRON_CONTRACT.md v1. This identical
// source must be built against the genuine before painter before production
// changes. No apron API, asset, alternate painter or permitted-change mask is
// used here. Independent admission owns source equality and paired masks.
namespace {
using namespace hammond;
using namespace hammond::standalone;
using Pixel = std::array<std::uint8_t, 4>;
static_assert(sizeof(Pixel) == 4);
constexpr std::string_view protocol = "reference-apron-v1";
constexpr std::size_t maximum_header = 65536;
constexpr std::size_t maximum_payload = 67108864;

struct Totals {
    std::size_t cases{}, checks{}, state_restorations{}, repeats{};
    std::size_t clip_companions{}, clip_pixels{}, clip_differences{}, exterior_pixels{};
} totals;
void require(bool condition, std::string_view message) {
    ++totals.checks;
    if (!condition) throw std::runtime_error(std::string(message) + ": " + SDL_GetError());
}

enum class State { Stopped, Running, Pending, Recovery, AudioOverlay };
struct Case {
    std::string_view name;
    float width, height, sx, sy;
    int output_width, output_height;
    SDL_Rect viewport, clip;
    bool clipped;
    std::string_view clip_kind;
    State state;
    UiWorkspace workspace;
    UiPresentation presentation;
};
constexpr std::array<Case, 25> fixtures{{
    {"reference-1672x941", 1672.0F, 941.0F, 1.0F, 1.0F, 1672, 941,
     {0, 0, 1672, 941}, {0, 0, 0, 0}, false, "disabled", State::Stopped, UiWorkspace::Play, UiPresentation::Dimensional},
    {"minimum-active-1400x820", 1400.0F, 820.0F, 1.0F, 1.0F, 1400, 820,
     {0, 0, 1400, 820}, {0, 0, 0, 0}, false, "disabled", State::Stopped, UiWorkspace::Play, UiPresentation::Dimensional},
    {"large-1920x1080", 1920.0F, 1080.0F, 1.0F, 1.0F, 1920, 1080,
     {0, 0, 1920, 1080}, {0, 0, 0, 0}, false, "disabled", State::Stopped, UiWorkspace::Play, UiPresentation::Dimensional},
    {"wide-2200x820", 2200.0F, 820.0F, 1.0F, 1.0F, 2200, 820,
     {0, 0, 2200, 820}, {0, 0, 0, 0}, false, "disabled", State::Stopped, UiWorkspace::Play, UiPresentation::Dimensional},
    {"tall-1400x1100", 1400.0F, 1100.0F, 1.0F, 1.0F, 1400, 1100,
     {0, 0, 1400, 1100}, {0, 0, 0, 0}, false, "disabled", State::Stopped, UiWorkspace::Play, UiPresentation::Dimensional},
    {"scale-1.5", 1672.0F, 941.0F, 1.5F, 1.5F, 2508, 1412,
     {0, 0, 2508, 1412}, {0, 0, 0, 0}, false, "disabled", State::Stopped, UiWorkspace::Play, UiPresentation::Dimensional},
    {"scale-2", 1672.0F, 941.0F, 2.0F, 2.0F, 3344, 1882,
     {0, 0, 3344, 1882}, {0, 0, 0, 0}, false, "disabled", State::Stopped, UiWorkspace::Play, UiPresentation::Dimensional},
    {"scale-1.25x1.5", 1672.0F, 941.0F, 1.25F, 1.5F, 2090, 1412,
     {0, 0, 2090, 1412}, {0, 0, 0, 0}, false, "disabled", State::Stopped, UiWorkspace::Play, UiPresentation::Dimensional},
    {"translated-full-companion", 1672.0F, 941.0F, 1.5F, 1.5F, 2534, 1448,
     {13, 17, 2508, 1414}, {0, 0, 0, 0}, false, "disabled", State::Stopped, UiWorkspace::Play, UiPresentation::Dimensional},
    {"translated-clip-left", 1672.0F, 941.0F, 1.5F, 1.5F, 2534, 1448,
     {13, 17, 2508, 1414}, {22, 1328, 4, 86}, true, "physical-left", State::Stopped, UiWorkspace::Play, UiPresentation::Dimensional},
    {"translated-clip-right", 1672.0F, 941.0F, 1.5F, 1.5F, 2534, 1448,
     {13, 17, 2508, 1414}, {2482, 1328, 4, 86}, true, "physical-right", State::Stopped, UiWorkspace::Play, UiPresentation::Dimensional},
    {"translated-clip-top", 1672.0F, 941.0F, 1.5F, 1.5F, 2534, 1448,
     {13, 17, 2508, 1414}, {22, 1328, 2464, 4}, true, "physical-top", State::Stopped, UiWorkspace::Play, UiPresentation::Dimensional},
    {"translated-clip-bottom", 1672.0F, 941.0F, 1.5F, 1.5F, 2534, 1448,
     {13, 17, 2508, 1414}, {22, 1410, 2464, 4}, true, "physical-bottom", State::Stopped, UiWorkspace::Play, UiPresentation::Dimensional},
    {"translated-enabled-empty", 1672.0F, 941.0F, 1.5F, 1.5F, 2534, 1448,
     {13, 17, 2508, 1414}, {24, 1330, 0, 0}, true, "physical-empty", State::Stopped, UiWorkspace::Play, UiPresentation::Dimensional},
    {"translated-disjoint", 1672.0F, 941.0F, 1.5F, 1.5F, 2534, 1448,
     {13, 17, 2508, 1414}, {100, 100, 16, 16}, true, "physical-disjoint", State::Stopped, UiWorkspace::Play, UiPresentation::Dimensional},
    {"output-cropped-height-880", 1672.0F, 941.0F, 1.0F, 1.0F, 1672, 880,
     {0, 0, 1672, 880}, {0, 0, 0, 0}, false, "disabled", State::Stopped, UiWorkspace::Play, UiPresentation::Dimensional},
    {"running-meter-dirty-clipped", 1672.0F, 941.0F, 1.0F, 1.0F, 1672, 941,
     {0, 0, 1672, 941}, {0, 0, 0, 0}, false, "disabled", State::Running, UiWorkspace::Play, UiPresentation::Dimensional},
    {"pending-preset-controls-focus-held", 1672.0F, 941.0F, 1.0F, 1.0F, 1672, 941,
     {0, 0, 1672, 941}, {0, 0, 0, 0}, false, "disabled", State::Pending, UiWorkspace::Play, UiPresentation::Dimensional},
    {"input-recovery-status", 1672.0F, 941.0F, 1.0F, 1.0F, 1672, 941,
     {0, 0, 1672, 941}, {0, 0, 0, 0}, false, "disabled", State::Recovery, UiWorkspace::Play, UiPresentation::Dimensional},
    {"audio-settings-overlay", 1672.0F, 941.0F, 1.0F, 1.0F, 1672, 941,
     {0, 0, 1672, 941}, {0, 0, 0, 0}, false, "disabled", State::AudioOverlay, UiWorkspace::Play, UiPresentation::Dimensional},
    {"inactive-width-1399", 1399.0F, 941.0F, 1.0F, 1.0F, 1399, 941,
     {0, 0, 1399, 941}, {0, 0, 0, 0}, false, "disabled", State::Stopped, UiWorkspace::Play, UiPresentation::Dimensional},
    {"inactive-height-819", 1672.0F, 819.0F, 1.0F, 1.0F, 1672, 819,
     {0, 0, 1672, 819}, {0, 0, 0, 0}, false, "disabled", State::Stopped, UiWorkspace::Play, UiPresentation::Dimensional},
    {"flat-play", 1672.0F, 941.0F, 1.0F, 1.0F, 1672, 941,
     {0, 0, 1672, 941}, {0, 0, 0, 0}, false, "disabled", State::Stopped, UiWorkspace::Play, UiPresentation::Flat},
    {"rotary", 1672.0F, 941.0F, 1.0F, 1.0F, 1672, 941,
     {0, 0, 1672, 941}, {0, 0, 0, 0}, false, "disabled", State::Stopped, UiWorkspace::Rotary, UiPresentation::Dimensional},
    {"service", 1672.0F, 941.0F, 1.0F, 1.0F, 1672, 941,
     {0, 0, 1672, 941}, {0, 0, 0, 0}, false, "disabled", State::Stopped, UiWorkspace::Service, UiPresentation::Dimensional},
}};

constexpr std::string_view fixture_manifest = R"apron({"schema":1,"protocol":"reference-apron-v1","case_count":25,"indexing":"--case uses zero-based case; contract_case is one-based","transport":{"header_max_bytes":65536,"dimension_max":4096,"payload_max_bytes":67108864,"pixel_format":"RGBA8","row_order":"top-down","padding_bytes":0,"trailer_bytes":0,"header_terminator":"LF","binary_stdout_on_windows":true},"renderer":{"creation":"SDL_CreateSoftwareRenderer on SDL_PIXELFORMAT_RGBA32 surface","initial_blend":1,"transform_installation":"Set physical viewport and enabled clip at scale 1, then install scale; query physical rectangles at scale 1 and restore scale","default_full_viewport":true},"state_defaults":{"session":{"controls":{"drawbars":[[[4,4,4,4,4,4,4,4,4],[4,4,4,4,4,4,4,4,4]],[[4,4,4,4,4,4,4,4,4],[4,4,4,4,4,4,4,4,4]]],"selected_banks":[1,1],"route_enabled":[true,true],"expression":0.625,"percussion":[true,0,0,0],"pedal_drawbars":[3,7],"fixed_registrations":[0,0]},"held_keys":[[false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false],[false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false]],"held_pedals":[false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false],"frame_clock":38400,"sample_rate":48000,"peak":0,"prepared":true,"running":false,"publication_revision":4,"resolved_sequence":0,"last_applied_sequence":0,"recovery_count":0,"queue_overflows":0,"rejected_commands":0,"discarded_commands":0,"fault_flags":0,"last_core_status":0},"info":{"audio_running":false,"sample_rate":48000,"buffer_frames":512,"audio_driver":"fixed-software-fixture","device_name":"fixed copied state","status_message":"Reference apron qualification","clipped_samples":0,"overlay":0,"audio_choices":["Default fixture device","Second fixture device"],"selected_device":0,"selected_sample_rate":48000,"selected_buffer_frames":512,"midi_available":false,"midi_open":false,"midi_backend":"none","midi_port":"","midi_status":"MIDI unavailable in fixed fixture","midi_choices":[],"selected_midi_port":0,"selected_midi_channels":[1,2,3],"selected_midi_expression":[0,127,false],"active_midi_expression":[0,127,false],"midi_expression_active":false,"midi_reconnect_pending":false,"midi_messages":0,"inspection":null},"model_setup":["UiModel default construction","resize to logical_size","set_presentation to case presentation","set_workspace to case workspace","observe copied session","mark_saved with stopped base controls"],"text_entry_active":false,"no_live_session_window_audio_or_midi":true},"state_profiles":{"stopped":{"session_changes":{},"info_changes":{}},"running":{"session_changes":{"running":true,"peak":0.75,"controls.drawbars[0][1][2]":6},"info_changes":{"audio_running":true,"clipped_samples":17},"saved_controls":"unchanged stopped base; controls_dirty true"},"pending":{"session_changes":{"held_keys[0][24]":true,"held_keys[1][36]":true,"held_pedals[12]":true},"actions":["activate upper PresetKey BankA (index10)","external_parameter for lower bankB drawbar index4 with normalized0.625","submit resulting copied control command with Ok and sequence9","Tab down/up until focus [4,1,1,4]"],"expected":{"controls_pending":true,"controls_dirty":true,"focus":[4,1,1,4],"desired_selected_banks":[0,1],"applied_selected_banks":[1,1],"desired_lower_B_drawbar4":5},"info_changes":{}},"recovery":{"session_changes":{"recovery_count":2,"queue_overflows":1,"rejected_commands":2,"discarded_commands":3,"fault_flags":1},"actions":["submitted ReleaseUiNotes with RecoveryPending and sequence0"],"info_changes":{"status_message":"Input recovered: release held keys before playing again."},"expected":{"input_recovery":true,"last_submit_status":11}},"audio-overlay":{"session_changes":{},"info_changes":{"overlay":2,"selected_device":1,"selected_sample_rate":96000,"selected_buffer_frames":256}}},"metadata_schema":{"model":"Every public UiViewState member, complete desired/applied controls and copied session; layout scalar members and all named regions. Detailed control/key geometry is checked before/after paint locally and omitted from the bounded stream.","info":"Every InstrumentViewInfo member; inspection is explicitly null","control_id":["kind","manual","bank","index"],"layout.controls_entry":["id","bounds","label_bounds","value_bounds","track"],"layout.key_entry":["note[target,value]","bounds","accidental","hit","top","front"],"rect":"[x,y,width,height]","quad":"four [x,y] pairs TL,TR,BR,BL","physical_clip_coordinates":"relative to physical viewport origin","logical_rectangles":"SDL public queries at incoming scale","renderer_identity":"name, flags, texture formats, limits, compiled/runtime SDL versions and RGBA format name","local_geometry_only":["layout.controls","layout.manual_keys","layout.pedal_keys"]},"cases":[{"case":0,"contract_case":1,"name":"reference-1672x941","logical_size":[1672,941],"output_size":[1672,941],"scale":[1,1],"viewport":[0,0,1672,941],"clip":[0,0,0,0],"clip_enabled":false,"clip_kind":"disabled","blend":1,"state_profile":"stopped","workspace":0,"presentation":0},{"case":1,"contract_case":2,"name":"minimum-active-1400x820","logical_size":[1400,820],"output_size":[1400,820],"scale":[1,1],"viewport":[0,0,1400,820],"clip":[0,0,0,0],"clip_enabled":false,"clip_kind":"disabled","blend":1,"state_profile":"stopped","workspace":0,"presentation":0},{"case":2,"contract_case":3,"name":"large-1920x1080","logical_size":[1920,1080],"output_size":[1920,1080],"scale":[1,1],"viewport":[0,0,1920,1080],"clip":[0,0,0,0],"clip_enabled":false,"clip_kind":"disabled","blend":1,"state_profile":"stopped","workspace":0,"presentation":0},{"case":3,"contract_case":4,"name":"wide-2200x820","logical_size":[2200,820],"output_size":[2200,820],"scale":[1,1],"viewport":[0,0,2200,820],"clip":[0,0,0,0],"clip_enabled":false,"clip_kind":"disabled","blend":1,"state_profile":"stopped","workspace":0,"presentation":0},{"case":4,"contract_case":5,"name":"tall-1400x1100","logical_size":[1400,1100],"output_size":[1400,1100],"scale":[1,1],"viewport":[0,0,1400,1100],"clip":[0,0,0,0],"clip_enabled":false,"clip_kind":"disabled","blend":1,"state_profile":"stopped","workspace":0,"presentation":0},{"case":5,"contract_case":6,"name":"scale-1.5","logical_size":[1672,941],"output_size":[2508,1412],"scale":[1.5,1.5],"viewport":[0,0,2508,1412],"clip":[0,0,0,0],"clip_enabled":false,"clip_kind":"disabled","blend":1,"state_profile":"stopped","workspace":0,"presentation":0},{"case":6,"contract_case":7,"name":"scale-2","logical_size":[1672,941],"output_size":[3344,1882],"scale":[2,2],"viewport":[0,0,3344,1882],"clip":[0,0,0,0],"clip_enabled":false,"clip_kind":"disabled","blend":1,"state_profile":"stopped","workspace":0,"presentation":0},{"case":7,"contract_case":8,"name":"scale-1.25x1.5","logical_size":[1672,941],"output_size":[2090,1412],"scale":[1.25,1.5],"viewport":[0,0,2090,1412],"clip":[0,0,0,0],"clip_enabled":false,"clip_kind":"disabled","blend":1,"state_profile":"stopped","workspace":0,"presentation":0},{"case":8,"contract_case":9,"name":"translated-full-companion","logical_size":[1672,941],"output_size":[2534,1448],"scale":[1.5,1.5],"viewport":[13,17,2508,1414],"clip":[0,0,0,0],"clip_enabled":false,"clip_kind":"disabled","blend":1,"state_profile":"stopped","workspace":0,"presentation":0},{"case":9,"contract_case":10,"name":"translated-clip-left","logical_size":[1672,941],"output_size":[2534,1448],"scale":[1.5,1.5],"viewport":[13,17,2508,1414],"clip":[22,1328,4,86],"clip_enabled":true,"clip_kind":"physical-left","blend":1,"state_profile":"stopped","workspace":0,"presentation":0},{"case":10,"contract_case":11,"name":"translated-clip-right","logical_size":[1672,941],"output_size":[2534,1448],"scale":[1.5,1.5],"viewport":[13,17,2508,1414],"clip":[2482,1328,4,86],"clip_enabled":true,"clip_kind":"physical-right","blend":1,"state_profile":"stopped","workspace":0,"presentation":0},{"case":11,"contract_case":12,"name":"translated-clip-top","logical_size":[1672,941],"output_size":[2534,1448],"scale":[1.5,1.5],"viewport":[13,17,2508,1414],"clip":[22,1328,2464,4],"clip_enabled":true,"clip_kind":"physical-top","blend":1,"state_profile":"stopped","workspace":0,"presentation":0},{"case":12,"contract_case":13,"name":"translated-clip-bottom","logical_size":[1672,941],"output_size":[2534,1448],"scale":[1.5,1.5],"viewport":[13,17,2508,1414],"clip":[22,1410,2464,4],"clip_enabled":true,"clip_kind":"physical-bottom","blend":1,"state_profile":"stopped","workspace":0,"presentation":0},{"case":13,"contract_case":14,"name":"translated-enabled-empty","logical_size":[1672,941],"output_size":[2534,1448],"scale":[1.5,1.5],"viewport":[13,17,2508,1414],"clip":[24,1330,0,0],"clip_enabled":true,"clip_kind":"physical-empty","blend":1,"state_profile":"stopped","workspace":0,"presentation":0},{"case":14,"contract_case":15,"name":"translated-disjoint","logical_size":[1672,941],"output_size":[2534,1448],"scale":[1.5,1.5],"viewport":[13,17,2508,1414],"clip":[100,100,16,16],"clip_enabled":true,"clip_kind":"physical-disjoint","blend":1,"state_profile":"stopped","workspace":0,"presentation":0},{"case":15,"contract_case":16,"name":"output-cropped-height-880","logical_size":[1672,941],"output_size":[1672,880],"scale":[1,1],"viewport":[0,0,1672,880],"clip":[0,0,0,0],"clip_enabled":false,"clip_kind":"disabled","blend":1,"state_profile":"stopped","workspace":0,"presentation":0},{"case":16,"contract_case":17,"name":"running-meter-dirty-clipped","logical_size":[1672,941],"output_size":[1672,941],"scale":[1,1],"viewport":[0,0,1672,941],"clip":[0,0,0,0],"clip_enabled":false,"clip_kind":"disabled","blend":1,"state_profile":"running","workspace":0,"presentation":0},{"case":17,"contract_case":18,"name":"pending-preset-controls-focus-held","logical_size":[1672,941],"output_size":[1672,941],"scale":[1,1],"viewport":[0,0,1672,941],"clip":[0,0,0,0],"clip_enabled":false,"clip_kind":"disabled","blend":1,"state_profile":"pending","workspace":0,"presentation":0},{"case":18,"contract_case":19,"name":"input-recovery-status","logical_size":[1672,941],"output_size":[1672,941],"scale":[1,1],"viewport":[0,0,1672,941],"clip":[0,0,0,0],"clip_enabled":false,"clip_kind":"disabled","blend":1,"state_profile":"recovery","workspace":0,"presentation":0},{"case":19,"contract_case":20,"name":"audio-settings-overlay","logical_size":[1672,941],"output_size":[1672,941],"scale":[1,1],"viewport":[0,0,1672,941],"clip":[0,0,0,0],"clip_enabled":false,"clip_kind":"disabled","blend":1,"state_profile":"audio-overlay","workspace":0,"presentation":0},{"case":20,"contract_case":21,"name":"inactive-width-1399","logical_size":[1399,941],"output_size":[1399,941],"scale":[1,1],"viewport":[0,0,1399,941],"clip":[0,0,0,0],"clip_enabled":false,"clip_kind":"disabled","blend":1,"state_profile":"stopped","workspace":0,"presentation":0},{"case":21,"contract_case":22,"name":"inactive-height-819","logical_size":[1672,819],"output_size":[1672,819],"scale":[1,1],"viewport":[0,0,1672,819],"clip":[0,0,0,0],"clip_enabled":false,"clip_kind":"disabled","blend":1,"state_profile":"stopped","workspace":0,"presentation":0},{"case":22,"contract_case":23,"name":"flat-play","logical_size":[1672,941],"output_size":[1672,941],"scale":[1,1],"viewport":[0,0,1672,941],"clip":[0,0,0,0],"clip_enabled":false,"clip_kind":"disabled","blend":1,"state_profile":"stopped","workspace":0,"presentation":1},{"case":23,"contract_case":24,"name":"rotary","logical_size":[1672,941],"output_size":[1672,941],"scale":[1,1],"viewport":[0,0,1672,941],"clip":[0,0,0,0],"clip_enabled":false,"clip_kind":"disabled","blend":1,"state_profile":"stopped","workspace":1,"presentation":0},{"case":24,"contract_case":25,"name":"service","logical_size":[1672,941],"output_size":[1672,941],"scale":[1,1],"viewport":[0,0,1672,941],"clip":[0,0,0,0],"clip_enabled":false,"clip_kind":"disabled","blend":1,"state_profile":"stopped","workspace":2,"presentation":0}]}
)apron";

template <typename Range, typename Writer>
void array(std::ostream& out, const Range& values, Writer write) {
    out << '[';
    bool first = true;
    for (const auto& value : values) {
        if (!first) out << ',';
        first = false;
        write(out, value);
    }
    out << ']';
}

void rect(std::ostream& out, UiRect r) {
    out << '[' << r.x << ',' << r.y << ',' << r.width << ',' << r.height << ']';
}
void rect(std::ostream& out, SDL_Rect r) {
    out << '[' << r.x << ',' << r.y << ',' << r.w << ',' << r.h << ']';
}
void control_id(std::ostream& out, UiControlId id) {
    out << '[' << static_cast<unsigned>(id.kind) << ',' << static_cast<unsigned>(id.manual)
        << ',' << static_cast<unsigned>(id.bank) << ',' << static_cast<unsigned>(id.index) << ']';
}
void quad(std::ostream& out, const UiQuad& value) {
    array(out, value.points, [](auto& stream, UiPoint point) {
        stream << '[' << point.x << ',' << point.y << ']';
    });
}
void key_geometry(std::ostream& out, const UiKeyGeometry& key) {
    out << "[[" << static_cast<unsigned>(key.note.target) << ','
        << static_cast<unsigned>(key.note.value) << "],";
    rect(out, key.bounds);
    out << ',' << key.accidental << ',';
    quad(out, key.hit);
    out << ',';
    quad(out, key.top);
    out << ',';
    quad(out, key.front);
    out << ']';
}
void controls(std::ostream& out, const ControlSnapshot& value) {
    const auto number = [](auto& stream, auto v) { stream << static_cast<unsigned>(v); };
    out << "{\"drawbars\":";
    array(out, value.drawbars, [&](auto& stream, const auto& manual) {
        array(stream, manual, [&](auto& bank_stream, const auto& bank) { array(bank_stream, bank, number); });
    });
    out << ",\"selected_banks\":";
    array(out, value.selected_banks, number);
    out << ",\"route_enabled\":";
    array(out, value.route_enabled, number);
    out << ",\"expression\":" << value.expression << ",\"percussion\":[" << value.percussion.enabled
        << ',' << static_cast<unsigned>(value.percussion.harmonic)
        << ',' << static_cast<unsigned>(value.percussion.volume)
        << ',' << static_cast<unsigned>(value.percussion.decay) << "],\"pedal_drawbars\":";
    array(out, value.pedal_drawbars, number);
    out << ",\"fixed_registrations\":";
    array(out, value.fixed_registrations, number);
    out << '}';
}
void session(std::ostream& out, const SessionSnapshot& value) {
    out << "{\"controls\":";
    controls(out, value.controls);
    out << ",\"held_keys\":";
    array(out, value.held_keys, [](auto& stream, const auto& manual) {
        array(stream, manual, [](auto& key_stream, bool held) { key_stream << held; });
    });
    out << ",\"held_pedals\":";
    array(out, value.held_pedals, [](auto& stream, bool held) { stream << held; });
    out << ",\"frame_clock\":" << value.frame_clock << ",\"sample_rate\":" << value.sample_rate
        << ",\"peak\":" << value.peak << ",\"prepared\":" << value.prepared
        << ",\"running\":" << value.running << ",\"publication_revision\":" << value.publication_revision
        << ",\"resolved_sequence\":" << value.resolved_sequence
        << ",\"last_applied_sequence\":" << value.last_applied_sequence
        << ",\"recovery_count\":" << value.recovery_count << ",\"queue_overflows\":" << value.queue_overflows
        << ",\"rejected_commands\":" << value.rejected_commands
        << ",\"discarded_commands\":" << value.discarded_commands << ",\"fault_flags\":" << value.fault_flags
        << ",\"last_core_status\":" << static_cast<unsigned>(value.last_core_status) << '}';
}
std::string session_record(const SessionSnapshot& value) {
    std::ostringstream out;
    out.imbue(std::locale::classic());
    out << std::boolalpha << std::setprecision(std::numeric_limits<double>::max_digits10);
    session(out, value);
    return out.str();
}

// Explicit, padding-independent serialization covers every public view/layout
// member. The same records are compared around paint and across paired streams;
// no hash collision or implementation-specific struct padding can hide a change.
std::string model_record(const UiModel& model, bool include_geometry = true) {
    std::ostringstream out;
    out.imbue(std::locale::classic());
    out << std::boolalpha << std::setprecision(std::numeric_limits<double>::max_digits10);
    const auto& view = model.view();
    out << "{\"view\":{\"controls\":";
    controls(out, view.controls);
    out << ",\"applied\":";
    session(out, view.applied);
    const auto number = [](auto& stream, auto v) { stream << static_cast<unsigned>(v); };
    out << ",\"edited_banks\":";
    array(out, view.edited_banks, number);
    out << ",\"focus\":";
    control_id(out, view.focus);
    out << ",\"roving_manual_keys\":";
    array(out, view.roving_manual_keys, number);
    out << ",\"roving_pedal_key\":" << static_cast<unsigned>(view.roving_pedal_key)
        << ",\"keyboard_target\":" << static_cast<unsigned>(view.keyboard_target)
        << ",\"manual_base_midi\":" << static_cast<unsigned>(view.manual_base_midi)
        << ",\"pedal_octave\":" << static_cast<unsigned>(view.pedal_octave)
        << ",\"controls_pending\":" << view.controls_pending << ",\"controls_dirty\":" << view.controls_dirty
        << ",\"text_entry_active\":" << view.text_entry_active << ",\"pointer_captured\":" << view.pointer_captured
        << ",\"input_recovery\":" << view.input_recovery
        << ",\"last_submit_status\":" << static_cast<unsigned>(view.last_submit_status)
        << ",\"workspace\":" << static_cast<unsigned>(view.workspace)
        << ",\"presentation\":" << static_cast<unsigned>(view.presentation) << ",\"workspace_focus\":";
    array(out, view.workspace_focus, [](auto& stream, UiControlId id) { control_id(stream, id); });
    const auto& layout = model.layout();
    out << "},\"layout\":{" << std::setprecision(std::numeric_limits<float>::max_digits10)
        << "\"width\":" << layout.width << ",\"height\":" << layout.height
        << ",\"show_cabinet\":" << layout.show_cabinet
        << ",\"bank_controls_in_cheeks\":" << layout.bank_controls_in_cheeks
        << ",\"sidebar_pedals\":" << layout.sidebar_pedals;
    const auto named_rect = [&](std::string_view name, UiRect bounds) {
        out << ",\"" << name << "\":";
        rect(out, bounds);
    };
    const auto named_rects = [&](std::string_view name, const auto& bounds) {
        out << ",\"" << name << "\":";
        array(out, bounds, [](auto& stream, UiRect r) { rect(stream, r); });
    };
    named_rect("header", layout.header);
    named_rects("registration_panels", layout.registration_panels);
    named_rect("performance_panel", layout.performance_panel);
    named_rect("keyboard_toolbar", layout.keyboard_toolbar);
    named_rects("manual_panels", layout.manual_panels);
    named_rect("pedal_panel", layout.pedal_panel);
    named_rect("footer", layout.footer);
    named_rect("cabinet_panel", layout.cabinet_panel);
    named_rect("cabinet_art", layout.cabinet_art);
    named_rects("manual_rail_panels", layout.manual_rail_panels);
    out << ",\"control_count\":" << layout.control_count;
    if (include_geometry) {
    out << ",\"controls\":";
    array(out, layout.controls, [](auto& stream, const UiControlGeometry& control) {
        stream << '[';
        control_id(stream, control.id);
        stream << ',';
        rect(stream, control.bounds);
        stream << ',';
        rect(stream, control.label_bounds);
        stream << ',';
        rect(stream, control.value_bounds);
        stream << ',';
        rect(stream, control.track);
        stream << ']';
    });
    out << ",\"manual_keys\":";
    array(out, layout.manual_keys, [](auto& stream, const auto& manual) {
        array(stream, manual, [](auto& key_stream, const auto& key) { key_geometry(key_stream, key); });
    });
    out << ",\"pedal_keys\":";
    array(out, layout.pedal_keys, [](auto& stream, const auto& key) { key_geometry(stream, key); });
    }
    named_rects("preset_key_panels", layout.preset_key_panels);
    out << ",\"workspace\":" << static_cast<unsigned>(layout.workspace)
        << ",\"presentation\":" << static_cast<unsigned>(layout.presentation);
    named_rect("workspace_panel", layout.workspace_panel);
    out << "}}";
    return out.str();
}

void quoted(std::ostream& out, std::string_view value) {
    constexpr char hex[] = "0123456789abcdef";
    out << '"';
    for (const char character : value) {
        const auto byte = static_cast<unsigned char>(character);
        if (byte == '"' || byte == '\\') out << '\\' << character;
        else if (byte < 0x20U) out << "\\u00" << hex[byte >> 4U] << hex[byte & 15U];
        else out << character;
    }
    out << '"';
}

void calibration(std::ostream& out, const MidiExpressionCalibration& value) {
    out << '[' << static_cast<unsigned>(value.minimum) << ','
        << static_cast<unsigned>(value.maximum) << ',' << value.inverted << ']';
}

std::string info_record(const InstrumentViewInfo& info) {
    std::ostringstream out;
    out.imbue(std::locale::classic());
    out << std::boolalpha << "{\"audio_running\":" << info.audio_running
        << ",\"sample_rate\":" << info.sample_rate << ",\"buffer_frames\":" << info.buffer_frames;
    const auto named_string = [&](std::string_view name, std::string_view value) {
        out << ",\"" << name << "\":";
        quoted(out, value);
    };
    named_string("audio_driver", info.audio_driver);
    named_string("device_name", info.device_name);
    named_string("status_message", info.status_message);
    out << ",\"clipped_samples\":" << info.clipped_samples
        << ",\"overlay\":" << static_cast<unsigned>(info.overlay) << ",\"audio_choices\":";
    array(out, info.audio_choices, [](auto& stream, const auto& value) { quoted(stream, value); });
    out << ",\"selected_device\":" << info.selected_device
        << ",\"selected_sample_rate\":" << info.selected_sample_rate
        << ",\"selected_buffer_frames\":" << info.selected_buffer_frames
        << ",\"midi_available\":" << info.midi_available << ",\"midi_open\":" << info.midi_open;
    named_string("midi_backend", info.midi_backend);
    named_string("midi_port", info.midi_port);
    named_string("midi_status", info.midi_status);
    out << ",\"midi_choices\":";
    array(out, info.midi_choices, [](auto& stream, const auto& value) { quoted(stream, value); });
    out << ",\"selected_midi_port\":" << info.selected_midi_port << ",\"selected_midi_channels\":";
    array(out, info.selected_midi_channels, [](auto& stream, auto value) { stream << static_cast<unsigned>(value); });
    out << ",\"selected_midi_expression\":";
    calibration(out, info.selected_midi_expression);
    out << ",\"active_midi_expression\":";
    calibration(out, info.active_midi_expression);
    out << ",\"midi_expression_active\":" << info.midi_expression_active
        << ",\"midi_reconnect_pending\":" << info.midi_reconnect_pending
        << ",\"midi_messages\":" << info.midi_messages << ",\"inspection\":null}";
    require(info.inspection == nullptr, "fixture inspection pointer is explicitly null");
    return out.str();
}

ControlSnapshot base_controls() {
    ControlSnapshot controls;
    for (auto& manual : controls.drawbars)
        for (auto& bank : manual) bank.fill(4);
    controls.selected_banks = {DrawbarBank::B, DrawbarBank::B};
    controls.route_enabled = {true, true};
    controls.expression = 0.625;
    controls.percussion = {true, PercussionHarmonic::Second, PercussionVolume::Normal, PercussionDecay::Slow};
    controls.pedal_drawbars = {3, 7};
    controls.fixed_registrations = {FixedRegistration::None, FixedRegistration::None};
    require(is_valid_control_snapshot(controls), "frozen complete control snapshot is valid");
    return controls;
}

UiModel state_for(const Case& test) {
    UiModel model;
    require(model.resize(test.width, test.height) && model.set_presentation(test.presentation) &&
            model.set_workspace(test.workspace), "fixed admitted UI layout");
    SessionSnapshot snapshot;
    snapshot.controls = base_controls();
    snapshot.frame_clock = 38400;
    snapshot.sample_rate = 48000;
    snapshot.prepared = true;
    snapshot.publication_revision = 4;
    if (test.state == State::Running) {
        snapshot.running = true;
        snapshot.peak = 0.75F;
        snapshot.controls.drawbars[0][1][2] = 6;
    } else if (test.state == State::Pending) {
        snapshot.held_keys[0][24] = true;
        snapshot.held_keys[1][36] = true;
        snapshot.held_pedals[12] = true;
    } else if (test.state == State::Recovery) {
        snapshot.recovery_count = 2;
        snapshot.queue_overflows = 1;
        snapshot.rejected_commands = 2;
        snapshot.discarded_commands = 3;
        snapshot.fault_flags = static_cast<std::uint32_t>(SessionFault::QueueOverflow);
    }
    model.observe(snapshot);
    model.mark_saved(base_controls());
    if (test.state == State::Pending) {
        require(model.activate({UiControlKind::PresetKey, Manual::Upper, DrawbarBank::A,
                    static_cast<std::uint8_t>(PresetSelection::BankA)}).count == 1,
                "pending preset uses unchanged public activation API");
        const UiControlId focus{UiControlKind::ManualDrawbar, Manual::Lower, DrawbarBank::B, 4};
        std::uint32_t parameter = 0;
        require(ui_parameter_id(focus, parameter), "pending drawbar has public parameter identity");
        const auto actions = model.external_parameter(parameter, 0.625);
        require(actions.count == 1 && std::holds_alternative<SessionCommand>(actions.items[0]),
                "pending controls are one copied public command");
        require(model.submitted(std::get<SessionCommand>(actions.items[0]), {SessionStatus::Ok, 9}).count == 0,
                "accepted sequence remains pending without a live Session");
        for (unsigned step = 0; step < 256 && model.view().focus != focus; ++step)
            require(model.key({UiKey::Tab, true}).count == 0 && model.key({UiKey::Tab, false}).count == 0,
                    "fixed focus traversal emits no musical actions");
        require(model.view().focus == focus && model.view().controls_pending && model.view().controls_dirty &&
                model.view().controls.selected_banks[0] == DrawbarBank::A &&
                model.view().controls.drawbars[1][1][4] == 5,
                "pending preset, controls and fixed focus are present");
    } else if (test.state == State::Recovery) {
        require(model.submitted(SessionCommand{ReleaseUiNotes{}}, {SessionStatus::RecoveryPending, 0}).count == 0 &&
                model.view().input_recovery && model.view().last_submit_status == SessionStatus::RecoveryPending,
                "explicit copied input recovery state");
    }
    require(session_record(model.view().applied) == session_record(snapshot), "complete applied state is fixed");
    require(model.view().controls_dirty == (test.state == State::Running || test.state == State::Pending),
            "declared saved versus dirty state");
    require(model.view().controls_pending == (test.state == State::Pending), "declared pending state");
    return model;
}

InstrumentViewInfo info_for(const Case& test) {
    static const std::array<std::string, 2> audio_choices{"Default fixture device", "Second fixture device"};
    InstrumentViewInfo info;
    info.audio_running = test.state == State::Running;
    info.sample_rate = 48000;
    info.buffer_frames = 512;
    info.audio_driver = "fixed-software-fixture";
    info.device_name = "fixed copied state";
    info.status_message = test.state == State::Recovery ?
        "Input recovered: release held keys before playing again." : "Reference apron qualification";
    info.clipped_samples = test.state == State::Running ? 17U : 0U;
    info.audio_choices = audio_choices;
    info.midi_backend = "none";
    info.midi_status = "MIDI unavailable in fixed fixture";
    if (test.state == State::AudioOverlay) {
        info.overlay = ViewOverlay::Audio;
        info.selected_device = 1;
        info.selected_sample_rate = 96000;
        info.selected_buffer_frames = 256;
    }
    return info;
}

bool equal(SDL_Rect a, SDL_Rect b) {
    return a.x == b.x && a.y == b.y && a.w == b.w && a.h == b.h;
}
struct Transform {
    float sx{}, sy{};
    SDL_Rect viewport{}, clip{}, logical_viewport{}, logical_clip{};
    bool clipped{};
    SDL_BlendMode blend{};
};
Transform transform(SDL_Renderer* renderer) {
    Transform result;
    SDL_RenderGetScale(renderer, &result.sx, &result.sy);
    SDL_RenderGetViewport(renderer, &result.logical_viewport);
    SDL_RenderGetClipRect(renderer, &result.logical_clip);
    result.clipped = SDL_RenderIsClipEnabled(renderer) == SDL_TRUE;
    require(SDL_GetRenderDrawBlendMode(renderer, &result.blend) == 0, "query renderer blend");
    require(SDL_RenderSetScale(renderer, 1, 1) == 0, "query exact physical rectangles at scale one");
    SDL_RenderGetViewport(renderer, &result.viewport);
    SDL_RenderGetClipRect(renderer, &result.clip);
    require(SDL_RenderSetScale(renderer, result.sx, result.sy) == 0, "restore incoming scale after query");
    return result;
}
bool equal(const Transform& a, const Transform& b) {
    return a.sx == b.sx && a.sy == b.sy && equal(a.viewport, b.viewport) && equal(a.clip, b.clip) &&
        equal(a.logical_viewport, b.logical_viewport) && equal(a.logical_clip, b.logical_clip) &&
        a.clipped == b.clipped && a.blend == b.blend;
}
bool visible(const Transform& t, int x, int y) {
    const int local_x = x - t.viewport.x, local_y = y - t.viewport.y;
    return local_x >= 0 && local_y >= 0 && local_x < t.viewport.w && local_y < t.viewport.h &&
        (!t.clipped || (local_x >= t.clip.x && local_y >= t.clip.y &&
                       local_x < t.clip.x + t.clip.w && local_y < t.clip.y + t.clip.h));
}

void validate_fixture(const Case& test) {
    require(test.output_width > 0 && test.output_height > 0 && test.output_width <= 4096 &&
            test.output_height <= 4096, "bounded output dimensions before allocation");
    require(static_cast<std::size_t>(test.output_width) * static_cast<std::size_t>(test.output_height) *
            sizeof(Pixel) <= maximum_payload, "bounded output payload before allocation");
    require(test.width > 0 && test.height > 0 && test.width <= 4096 && test.height <= 4096 &&
            std::isfinite(test.sx) && std::isfinite(test.sy) && test.sx > 0 && test.sy > 0,
            "bounded logical dimensions and finite positive scale");
    if (test.viewport.x == 13) {
        const double bottom = static_cast<double>(test.viewport.y) + 941.0 * test.sy;
        require(static_cast<double>(test.output_height) >= bottom + 2.0 &&
                static_cast<double>(test.viewport.y + test.viewport.h) >= bottom + 2.0,
                "translated output and viewport retain two pixels below apron");
    }
}

struct Frame {
    int width{}, height{};
    Transform coordinates;
    std::vector<Pixel> pixels;
    std::string model, info, renderer;
    std::size_t at(int x, int y) const {
        return static_cast<std::size_t>(y) * static_cast<std::size_t>(width) + static_cast<std::size_t>(x);
    }
};

std::string renderer_record(SDL_Renderer* renderer) {
    SDL_RendererInfo identity{};
    require(SDL_GetRendererInfo(renderer, &identity) == 0 && identity.name != nullptr,
            "query actual renderer identity");
    SDL_version runtime{};
    SDL_GetVersion(&runtime);
    std::ostringstream out;
    out.imbue(std::locale::classic());
    out << "{\"name\":";
    quoted(out, identity.name);
    out << ",\"flags\":" << identity.flags << ",\"texture_formats\":[";
    for (std::uint32_t index = 0; index < identity.num_texture_formats; ++index) {
        if (index != 0) out << ',';
        out << identity.texture_formats[index];
    }
    out << "],\"max_texture_size\":[" << identity.max_texture_width << ',' << identity.max_texture_height
        << "],\"compiled_sdl\":[" << SDL_MAJOR_VERSION << ',' << SDL_MINOR_VERSION << ',' << SDL_PATCHLEVEL
        << "],\"runtime_sdl\":[" << static_cast<unsigned>(runtime.major) << ','
        << static_cast<unsigned>(runtime.minor) << ',' << static_cast<unsigned>(runtime.patch)
        << "],\"surface_format\":";
    quoted(out, SDL_GetPixelFormatName(SDL_PIXELFORMAT_RGBA32));
    out << '}';
    return out.str();
}

class Target {
public:
    explicit Target(const Case& test) :
        width_(test.output_width), height_(test.output_height),
        surface_(SDL_CreateRGBSurfaceWithFormat(0, width_, height_, 32, SDL_PIXELFORMAT_RGBA32), SDL_FreeSurface),
        renderer_(surface_ ? SDL_CreateSoftwareRenderer(surface_.get()) : nullptr, SDL_DestroyRenderer),
        drawing_(renderer_.get()) {
        require(surface_ && renderer_, "create fixed software surface and renderer");
        int actual_width = 0, actual_height = 0;
        require(SDL_GetRendererOutputSize(renderer_.get(), &actual_width, &actual_height) == 0 &&
                actual_width == width_ && actual_height == height_, "actual output equals declared dimensions");
        std::string error;
        require(drawing_.initialize(error), "initialize existing fonts and optional decoration");
        require(SDL_RenderSetScale(renderer_.get(), 1, 1) == 0 &&
                SDL_RenderSetViewport(renderer_.get(), &test.viewport) == 0 &&
                SDL_RenderSetClipRect(renderer_.get(), test.clipped ? &test.clip : nullptr) == 0 &&
                SDL_RenderSetScale(renderer_.get(), test.sx, test.sy) == 0 &&
                SDL_SetRenderDrawBlendMode(renderer_.get(), SDL_BLENDMODE_BLEND) == 0,
                "install physical viewport, physical clip and incoming scale");
        const auto actual = transform(renderer_.get());
        require(actual.sx == test.sx && actual.sy == test.sy && equal(actual.viewport, test.viewport) &&
                equal(actual.clip, test.clip) && actual.clipped == test.clipped && actual.blend == SDL_BLENDMODE_BLEND,
                "queried physical renderer state equals the frozen specification");
        identity_ = renderer_record(renderer_.get());
    }

    Frame paint(const UiModel& model, const InstrumentViewInfo& info) {
        const auto before = transform(renderer_.get());
        const auto copied_model = model_record(model);
        const auto copied_info = info_record(info);
        paint_instrument(drawing_, model, info);
        require(equal(before, transform(renderer_.get())), "paint preserves scale, viewport, clip-enable/rectangles and blend");
        require(copied_model == model_record(model) && copied_info == info_record(info),
                "paint preserves every copied public model/layout/info member");
        ++totals.state_restorations;
        require(SDL_RenderFlush(renderer_.get()) == 0 && SDL_LockSurface(surface_.get()) == 0,
                "flush and lock exact RGBA surface bytes");
        Frame frame{width_, height_, before, std::vector<Pixel>(static_cast<std::size_t>(width_) *
                    static_cast<std::size_t>(height_)), model_record(model, false), copied_info, identity_};
        const auto* input = static_cast<const std::uint8_t*>(surface_->pixels);
        for (int row = 0; row < height_; ++row)
            std::memcpy(frame.pixels.data() + frame.at(0, row),
                input + static_cast<std::size_t>(row) * static_cast<std::size_t>(surface_->pitch),
                static_cast<std::size_t>(width_) * sizeof(Pixel));
        SDL_UnlockSurface(surface_.get());
        return frame;
    }

private:
    int width_, height_;
    std::unique_ptr<SDL_Surface, decltype(&SDL_FreeSurface)> surface_;
    std::unique_ptr<SDL_Renderer, decltype(&SDL_DestroyRenderer)> renderer_;
    Drawing drawing_;
    std::string identity_;
};

std::string header(std::size_t index, const Case& test, const Frame& frame) {
    const auto& t = frame.coordinates;
    std::ostringstream out;
    out.imbue(std::locale::classic());
    out << std::boolalpha << std::setprecision(std::numeric_limits<float>::max_digits10)
        << "{\"schema\":1,\"protocol\":\"" << protocol << "\",\"case\":" << index
        << ",\"contract_case\":" << index + 1 << ",\"name\":";
    quoted(out, test.name);
    out << ",\"logical_size\":[" << test.width << ',' << test.height << ']'
        << ",\"width\":" << frame.width << ",\"height\":" << frame.height
        << ",\"output_size\":[" << frame.width << ',' << frame.height << ']'
        << ",\"scale\":[" << t.sx << ',' << t.sy << "],\"viewport\":";
    rect(out, t.viewport);
    out << ",\"clip\":";
    rect(out, t.clip);
    out << ",\"logical_viewport\":";
    rect(out, t.logical_viewport);
    out << ",\"logical_clip\":";
    rect(out, t.logical_clip);
    out << ",\"clip_enabled\":" << t.clipped << ",\"blend\":" << static_cast<unsigned>(t.blend)
        << ",\"clip_kind\":";
    quoted(out, test.clip_kind);
    out << ",\"renderer\":" << frame.renderer << ",\"model\":" << frame.model
        << ",\"info\":" << frame.info << ",\"bytes\":" << frame.pixels.size() * sizeof(Pixel) << "}\n";
    const auto result = out.str();
    require(result.size() <= maximum_header,
            "JSON header exceeds 64 KiB: case=" + std::to_string(index) + " bytes=" + std::to_string(result.size()));
    require(result.find('\n') == result.size() - 1, "JSON header has exactly one final LF");
    return result;
}

void stream(std::string_view metadata, const Frame& frame) {
    const auto bytes = frame.pixels.size() * sizeof(Pixel);
    require(bytes <= maximum_payload, "exact bounded payload before binary write");
    std::cout.write(metadata.data(), static_cast<std::streamsize>(metadata.size()));
    std::cout.write(reinterpret_cast<const char*>(frame.pixels.data()), static_cast<std::streamsize>(bytes));
    std::cout.flush();
    require(static_cast<bool>(std::cout), "write exact JSON line plus RGBA payload without trailer");
}

void compare_clip(const Case& test, const Frame& frame, const Frame& full) {
    require(frame.width == full.width && frame.height == full.height && frame.model == full.model &&
            frame.info == full.info && frame.renderer == full.renderer &&
            equal(frame.coordinates.viewport, full.coordinates.viewport), "full companion retains geometry and state");
    std::size_t interior = 0, exterior = 0;
    for (int y = 0; y < frame.height; ++y) {
        for (int x = 0; x < frame.width; ++x) {
            const auto at = frame.at(x, y);
            if (visible(frame.coordinates, x, y)) {
                if (frame.pixels[at] != full.pixels[at]) ++totals.clip_differences;
                ++totals.clip_pixels;
                // Population checks validate fixture design only. They do not
                // define or emit any candidate-permitted-change mask.
                const double local_x = (static_cast<double>(x) + 0.5 - frame.coordinates.viewport.x) / test.sx;
                const double local_y = (static_cast<double>(y) + 0.5 - frame.coordinates.viewport.y) / test.sy;
                if (local_x >= 16.0 && local_x < 1656.0 && local_y >= 887.0 && local_y < 941.0) ++interior;
                else ++exterior;
            } else {
                // SDL_RenderClear intentionally clears the entire output.
                require(frame.pixels[at] == Pixel{85, 54, 36, 255}, "no painted primitive escapes caller viewport/clip");
                ++totals.exterior_pixels;
            }
        }
    }
    if (test.clip_kind == "physical-left" || test.clip_kind == "physical-right" ||
        test.clip_kind == "physical-top" || test.clip_kind == "physical-bottom")
        require(interior > 0 && exterior > 0 && (test.clip.w == 4 || test.clip.h == 4),
                "four-pixel strip retains nonempty apron interior and protected exterior");
    if (test.clip_kind == "physical-empty")
        require(frame.coordinates.clipped && frame.coordinates.clip.w == 0 && frame.coordinates.clip.h == 0 &&
                interior == 0 && exterior == 0, "empty physical clip remains enabled and hides every primitive");
    if (test.clip_kind == "physical-disjoint")
        require(interior == 0 && exterior > 0, "positive-area disjoint clip excludes complete apron");
    ++totals.clip_companions;
}
} // namespace

int main(int argc, char* argv[]) {
    SDL_SetMainReady();
    try {
        if (argc == 2 && std::string_view(argv[1]) == "--list") {
            std::cout << fixture_manifest;
            require(static_cast<bool>(std::cout), "write ordered frozen case specification");
            return EXIT_SUCCESS;
        }
        std::size_t selected = fixtures.size();
        if (argc != 1) {
            require(argc == 3 && std::string_view(argv[1]) == "--case", "expected --case INDEX or --list");
            const std::string_view value(argv[2]);
            const auto parsed = std::from_chars(value.data(), value.data() + value.size(), selected);
            require(parsed.ec == std::errc{} && parsed.ptr == value.data() + value.size() && selected < fixtures.size(),
                    "case index must be an integer from 0 through 24");
#ifdef _WIN32
            require(_setmode(_fileno(stdout), _O_BINARY) != -1, "switch frame stdout to binary mode on Windows");
#endif
        }
        require(SDL_Init(0) == 0, "initialize SDL without windows or audio");
        Frame full_companion;
        for (std::size_t index = 0; index < fixtures.size(); ++index) {
            if (selected != fixtures.size() && index != selected) continue;
            const auto& test = fixtures[index];
            validate_fixture(test);
            const auto model = state_for(test);
            const auto info = info_for(test);
            Target target(test);
            const auto frame = target.paint(model, info);
            const auto metadata = header(index, test, frame);
            if (selected != fixtures.size()) stream(metadata, frame);
            else {
                if (index == 8) full_companion = frame;
                if (test.clipped) compare_clip(test, frame, full_companion);
                if (index == 0) {
                    const auto alternate = state_for(fixtures[16]);
                    (void)target.paint(alternate, info_for(fixtures[16]));
                    const auto repeated = target.paint(model, info);
                    require(repeated.pixels == frame.pixels && header(index, test, repeated) == metadata,
                            "canonical frame repeats after another state on the same renderer");
                    Target fresh(test);
                    const auto recreated = fresh.paint(model, info);
                    require(recreated.pixels == frame.pixels && header(index, test, recreated) == metadata,
                            "canonical frame repeats on a fresh Drawing and renderer");
                    totals.repeats += 2;
                }
            }
            ++totals.cases;
        }
        SDL_Quit();
        if (selected == fixtures.size())
            std::cout << "{\"schema\":1,\"protocol\":\"" << protocol << "\",\"status\":\"passed\",\"cases\":" << totals.cases
                << ",\"checks\":" << totals.checks << ",\"state_restorations\":" << totals.state_restorations
                << ",\"same_and_fresh_repeats\":" << totals.repeats << ",\"clip_companions\":" << totals.clip_companions
                << ",\"visible_clip_pixels\":" << totals.clip_pixels
                << ",\"reported_clip_interior_differences\":" << totals.clip_differences
                << ",\"protected_exterior_pixels\":" << totals.exterior_pixels
                << ",\"backend\":\"SDL software surface; fixed copied state; no audio/window\"}\n";
        return EXIT_SUCCESS;
    } catch (const std::exception& error) {
        std::cerr << "Reference-apron raster fixture failed: " << error.what() << '\n';
        SDL_Quit();
        return EXIT_FAILURE;
    }
}
