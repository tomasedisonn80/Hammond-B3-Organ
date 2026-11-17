#!/usr/bin/env python3
"""Permanent stdlib-only H1 regression against the real native case46 frame.

Run with --executable PATH_TO_test_standalone_header_material. The executable
must already be built; this test never configures, builds, imports a painter or
reads image files. One bounded JSON-header/RGBA stream supplies the canonical
1672 by 941 frame. All 103 material inequalities retain the independently
admitted H1 revision 1.1 limits and primary-patch order.

The immutable reference literals below are exact observations from A22's
pre-candidate report, not fitted candidate statistics. Ordinary-coordinate
integer moments and Fraction arithmetic independently recover RGB and encoded
Y' planes. RMS decisions use the prescribed binary64 conversion; other
binary64 statistics are display values only. A
genuine pre-H1 fixture is a valid transport: it still receives all 103 screens,
but fails the separate helper-presence gate as well as its numerical failures.

This one-frame numerical gate supplements the complete paired preservation,
renderer/state, full-frame visual, timing and platform qualification gates.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import sys
import threading


PROTOCOL = "header-material-h1-v1"
CASE = 46
WIDTH, HEIGHT = 1672, 941
PIXELS = WIDTH * HEIGHT
FRAME_BYTES = PIXELS * 4
MAX_HEADER_BYTES = 512 * 1024
MAX_STDOUT_BYTES = MAX_HEADER_BYTES + 1 + FRAME_BYTES
MAX_STDERR_BYTES = 64 * 1024
READ_BYTES = 64 * 1024
DEFAULT_TIMEOUT_SECONDS = 20.0
MAX_TIMEOUT_SECONDS = 60.0
CLEANUP_TIMEOUT_SECONDS = 5.0
MAX_ERROR_CHARACTERS = 4096
FIXTURE_SHA256 = "86acc068fa23826fb39f245f9327e919c076660f315bed5d57f63e586d6d3ac6"
CONTRACT_SHA256 = "07d64498a14431b64742d79e7fbe4d2ac71d77fe51d09f71c638f52594fd9282"
OBSERVATIONS_SHA256 = "8f591b6d80bb6934a955ac2eb4b0005b78c4c164434510bc7125b4c511856c7b"
COMPARATOR_SHA256 = "098398562f1b9134739ff9bd6f015892c10ca7ad707ab4703d84051883299f1b"
REFERENCE_IMAGE_SHA256 = "9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187"
REFERENCE_RGB_SHA256 = "07a7e35a2fd6610d623bbc1da8c995f3f4d95c4b45a0a5c1f41ad1395584bbeb"

# In primary_patch_order: ID, half-open (x,y,width,height), exact RGB sums,
# exact encoded-Y' vertical slope, and exact encoded-Y' residual SSE.
# Every value is transcribed from measurements[ID]["reference"] in the
# observation report identified above. Means are derived from these integers;
# rounded display decimals are never used as a numerical oracle.
REFERENCE_ROWS = (
    ('L', (86, 24, 8, 64), (13975, 12423, 11013),
     '-27110449/174720000', '1799662751014693/873600000000'),
    ('TL', (112, 20, 96, 20), (74467, 62471, 53651),
     '-1497497/3192000', '869486846789593021/48378750000000'),
    ('TM', (264, 20, 96, 20), (78826, 69078, 62162),
     '-7622337/13300000', '49531793219298137/3225250000000'),
    ('TR', (420, 20, 80, 20), (61004, 54800, 51684),
     '-7295727/16625000', '343341718611359551/35461125000000'),
    ('CLT', (530, 20, 48, 16), (25519, 25231, 26487),
     '-6226357/40800000', '83202774639121133/19176000000000'),
    ('CL', (530, 50, 48, 44), (58302, 58302, 58486),
     '-11094799/212850000', '11211980614198560673/1225483875000000'),
    ('CR', (1100, 50, 96, 44), (131512, 124088, 127968),
     '-85509/1892000', '107876856257527723/6740250000000'),
    ('RT', (1130, 18, 64, 16), (35618, 34666, 35631),
     '-78112543/217600000', '3586849270919768281/594048000000000'),
    ('RU', (1240, 18, 72, 16), (41453, 38973, 39901),
     '-400477/1800000', '78102459644284631/11661750000000'),
    ('RF', (1440, 16, 128, 6), (25817, 24281, 25049),
     '-551/896', '178093641883/29358336'),
    ('CM1', (620, 60, 96, 6), (16236, 15597, 15557),
     '699109/16800000', '2487168449542551457/928872000000000'),
    ('CM2', (780, 60, 96, 6), (15601, 15109, 14958),
     '649547/2400000', '19152723356209909/6984000000000'),
    ('CM3', (940, 60, 96, 6), (16357, 16069, 16116),
     '1435387/16800000', '649633732372417973/185774400000000'),
    ('BL', (534, 96, 60, 8), (12779, 12754, 12977),
     '19989/1400000', '98341858613442229/75579000000000'),
    ('BC1', (650, 92, 96, 10), (25145, 23964, 24043),
     '-63477/1100000', '196053667309589883/101365000000000'),
    ('BC2', (790, 92, 96, 10), (25189, 23924, 23882),
     '-6717211/79200000', '12337064929540924879/7298280000000000'),
    ('BC3', (930, 92, 96, 10), (25620, 24415, 24846),
     '-2150761/39600000', '3762944891730854791/1824570000000000'),
    ('BR', (1100, 96, 96, 8), (23400, 22184, 21800),
     '-28537/840000', '7992808910235047/2418937500000'),
)
PRIMARY = tuple(row[0] for row in REFERENCE_ROWS)
VERTICAL_LIMITS = (
    ("L", "3/40"), ("TL", "3/20"), ("TM", "3/20"), ("TR", "3/20"),
    ("CL", "3/40"), ("CR", "3/40"), ("RT", "1/5"), ("RF", "1/5"),
)
LATERAL_LIMITS = (("TM", "TL", "2"), ("CR", "CL", "5/4"), ("BR", "BC2", "7/4"))
MEAN_MAE_LIMIT = Fraction(846310429693, 456192000000)
RMS_MAE_LIMIT = 0.8336586440740232


def require(condition, message):
    if not condition:
        raise ValueError(message)


INDEXED_FIXTURE_SHA256 = "8c8226b04931569cdbff78cddcfd6241fd334c1f15c764a04d016d958bc912aa"
ARRAY_ORIGINAL_BYTES = b"""template <typename Range, typename Writer>
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
"""
ARRAY_INDEXED_BYTES = b"""template <typename Range, typename Writer>
void array(std::ostream& out, const Range& values, Writer write) {
    out << '[';
    for (std::size_t index = 0; index < values.size(); ++index) {
        if (index != 0) out << ',';
        write(out, values[index]);
    }
    out << ']';
}
"""


def admit_fixture_bytes(source_bytes):
    """Admit one canonical serializer transition without weakening the protocol."""
    require(type(source_bytes) is bytes, "fixture admission requires complete byte source")
    observed = hashlib.sha256(source_bytes).hexdigest()
    result = dict(variant="original-fixture", original_sha256=FIXTURE_SHA256,
                  observed_sha256=observed, reversed_sha256=FIXTURE_SHA256,
                  candidate_only=True)
    if observed == FIXTURE_SHA256:
        return result
    require(source_bytes.count(ARRAY_INDEXED_BYTES) == 1 and ARRAY_ORIGINAL_BYTES not in source_bytes,
            "fixture requires one exact indexed array block")
    restored = source_bytes.replace(ARRAY_INDEXED_BYTES, ARRAY_ORIGINAL_BYTES, 1)
    require(hashlib.sha256(restored).hexdigest() == FIXTURE_SHA256,
            "indexed array reversal does not reconstruct original fixture")
    require(observed == INDEXED_FIXTURE_SHA256,
            "indexed fixture does not match complete admitted identity")
    result.update(variant="indexed-array-v1", whole_file_reversal_verified=True)
    return result


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(READ_BYTES), b""):
            digest.update(chunk)
    return digest.hexdigest()


def typed_equal(actual, expected):
    """Keep booleans distinct from integers throughout copied JSON records."""
    if type(actual) is not type(expected):
        return False
    if isinstance(expected, dict):
        return actual.keys() == expected.keys() and all(
            typed_equal(actual[key], value) for key, value in expected.items())
    if isinstance(expected, list):
        return len(actual) == len(expected) and all(
            typed_equal(left, right) for left, right in zip(actual, expected))
    return actual == expected


def copied_state_difference(actual, expected, path="root"):
    """Describe the first exact mismatch; never alter equality or accept data."""
    def value_text(value):
        return repr(value)[:96]
    if type(actual) is not type(expected):
        return (path + ": actual " + type(actual).__name__ + " " + value_text(actual) +
                "; expected " + type(expected).__name__ + " " + value_text(expected))
    if type(expected) is dict:
        if actual.keys() != expected.keys():
            return path + ": dictionary keys differ"
        for key, value in expected.items():
            if not typed_equal(actual[key], value):
                return copied_state_difference(actual[key], value, path + "." + key)
    elif type(expected) is list:
        if len(actual) != len(expected):
            return path + ": list lengths " + str(len(actual)) + " / " + str(len(expected))
        for index, (left, right) in enumerate(zip(actual, expected)):
            if not typed_equal(left, right):
                return copied_state_difference(left, right, path + "[" + str(index) + "]")
    elif actual != expected:
        return path + ": actual " + value_text(actual) + "; expected " + value_text(expected)
    return path + ": no difference"


def unique_members(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON member: " + key)
        result[key] = value
    return result


def invalid_constant(value):
    raise ValueError("non-JSON numeric token: " + value)


def finite_float(token):
    value = float(token)
    require(math.isfinite(value), "nonfinite JSON number")
    return value


def capture_frame(executable, timeout):
    """Bound both retained pipe buffers, even for a failing or noisy child."""
    process = subprocess.Popen(
        [str(executable), "--case", str(CASE)], stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    buffers = [bytearray(), bytearray()]
    failures = []

    def kill():
        try:
            process.kill()
        except OSError:
            pass  # A reader or normal child exit may already have ended it.

    def collect(stream, channel, cap):
        try:
            while True:
                chunk = stream.read(READ_BYTES)
                if not chunk:
                    break
                if len(buffers[channel]) + len(chunk) > cap:
                    failures.append(("stdout" if channel == 0 else "stderr") + " exceeded byte bound")
                    kill()
                    break
                buffers[channel].extend(chunk)
        except OSError as error:
            failures.append(str(error)[:MAX_ERROR_CHARACTERS])
            kill()
        finally:
            stream.close()

    readers = [
        threading.Thread(target=collect, args=(process.stdout, 0, MAX_STDOUT_BYTES), daemon=True),
        threading.Thread(target=collect, args=(process.stderr, 1, MAX_STDERR_BYTES), daemon=True),
    ]
    for reader in readers:
        reader.start()
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        failures.append(f"native case46 exceeded {timeout:g}-second timeout")
        kill()
        try:
            process.wait(timeout=CLEANUP_TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired:
            failures.append("native fixture exceeded bounded termination wait")
    finally:
        for reader in readers:
            reader.join(timeout=CLEANUP_TIMEOUT_SECONDS)
    require(not any(reader.is_alive() for reader in readers), "native fixture left an open pipe")
    require(not failures, "; ".join(failures)[:MAX_ERROR_CHARACTERS])
    diagnostic = buffers[1][:MAX_ERROR_CHARACTERS].decode("utf-8", errors="replace")
    require(process.returncode == 0, f"native case46 exited {process.returncode}: {diagnostic}")
    require(not buffers[1], "unexpected native fixture stderr: " + diagnostic)
    return buffers[0]


def expected_header():
    return {
        "schema": 1, "protocol": PROTOCOL, "case": CASE, "variant": "main",
        "logical_size": [WIDTH, HEIGHT], "output_size": [WIDTH, HEIGHT],
        "width": WIDTH, "height": HEIGHT, "bytes": FRAME_BYTES,
        "scale": [1, 1], "origin": [0, 0], "clip_kind": "disabled",
        "clip_space": "physical", "clip_request": [0, 0, 0, 0],
        "requested_clip_enabled": False, "viewport": [0, 0, WIDTH, HEIGHT],
        "clip": [0, 0, 0, 0], "logical_viewport": [0, 0, WIDTH, HEIGHT],
        "logical_clip": [0, 0, 0, 0], "clip_enabled": False, "blend": 1,
        "level": 4, "route": "B", "route_index": 11, "pending": False,
        "pending_route": "None", "pending_route_index": -1, "held": True,
        "edited_bank": "B", "lower_route": "B", "lower_edited_bank": "B",
        "focus": [4, 0, 1, 4], "workspace": 0, "presentation": 0,
        "active_reference": True, "eligible_h1": True, "resource_crop": False,
        "visible_clip_pixels": PIXELS, "quiet_clip_pixels": 0, "history_states": 0,
        "checks": {
            "transform_unchanged": True, "model_unchanged": True, "session_unchanged": True,
            "hit_unchanged": True, "clip_containment": True, "deterministic_repaint": True,
            "inactive_classification": True, "clip_companion_checked": False,
            "after_all_repeat_checked": False, "fresh_repeat_checked": False,
        },
    }


def validate_transform(record, color=None):
    keys = set("scale viewport clip logical_viewport logical_clip clip_enabled blend draw_color".split())
    require(type(record) is dict and set(record) == keys, "incomplete renderer record")
    fixed = expected_header()
    for key in keys - {"draw_color"}:
        require(typed_equal(record[key], fixed[key]), "renderer " + key + " differs")
    rgba = record["draw_color"]
    require(type(rgba) is list and len(rgba) == 4 and
            all(type(v) is int and 0 <= v <= 255 for v in rgba), "invalid renderer draw color")
    if color is not None:
        require(typed_equal(rgba, color), "incoming/helper draw color differs")


def vector(value, length, label, integer=False):
    types = (int,) if integer else (int, float)
    require(type(value) is list and len(value) == length and
            all(type(v) in types and (type(v) is int or math.isfinite(v)) for v in value),
            "invalid " + label)


def expected_session():
    controls = {
        "drawbars": [[[4] * 9 for _ in range(2)] for _ in range(2)],
        "selected_banks": [1, 1], "route_enabled": [1, 1], "expression": .625,
        "percussion": [True, 0, 0, 0], "pedal_drawbars": [3, 7], "fixed_registrations": [0, 0],
    }
    held_keys, held_pedals = [[False] * 61 for _ in range(2)], [False] * 25
    held_keys[0][24] = held_keys[1][36] = held_pedals[12] = True
    session = {
        "controls": controls, "held_keys": held_keys, "held_pedals": held_pedals,
        "frame_clock": 38400, "sample_rate": 48000, "peak": .125,
        "prepared": True, "running": True, "publication_revision": 4,
    }
    session.update(dict.fromkeys(("resolved_sequence", "last_applied_sequence", "recovery_count",
                                 "queue_overflows", "rejected_commands", "discarded_commands",
                                 "fault_flags", "last_core_status"), 0))
    return session


def validate_model(model, session, hit):
    require(type(model) is dict and set(model) == {"view", "layout"}, "incomplete model record")
    view, layout = model["view"], model["layout"]
    view_keys = set(("controls applied edited_banks focus roving_manual_keys roving_pedal_key keyboard_target "
                     "manual_base_midi pedal_octave controls_pending controls_dirty text_entry_active pointer_captured "
                     "input_recovery last_submit_status workspace presentation workspace_focus").split())
    layout_keys = set(("width height show_cabinet bank_controls_in_cheeks sidebar_pedals header registration_panels "
                       "performance_panel keyboard_toolbar manual_panels pedal_panel footer cabinet_panel cabinet_art "
                       "manual_rail_panels control_count controls manual_keys pedal_keys preset_key_panels workspace "
                       "presentation workspace_panel").split())
    require(type(view) is dict and set(view) == view_keys and
            type(layout) is dict and set(layout) == layout_keys, "incomplete view/layout record")
    expected = expected_session()
    if not typed_equal(session, expected):
        require(False, "complete canonical copied session differs; " +
                copied_state_difference(session, expected, "session"))
    if not typed_equal(view["applied"], expected):
        require(False, "complete canonical copied session differs; " +
                copied_state_difference(view["applied"], expected, "view.applied"))
    for key, value in {"controls": expected["controls"], "edited_banks": [1, 1],
                       "focus": [4, 0, 1, 4], "controls_pending": False,
                       "workspace": 0, "presentation": 0}.items():
        require(typed_equal(view[key], value), "canonical view " + key + " differs")
    vector(view["roving_manual_keys"], 2, "roving manual keys", integer=True)
    for key in ("roving_pedal_key", "keyboard_target", "manual_base_midi", "pedal_octave", "last_submit_status"):
        require(type(view[key]) is int and view[key] >= 0, "invalid view " + key)
    for key in ("controls_dirty", "text_entry_active", "pointer_captured", "input_recovery"):
        require(type(view[key]) is bool, "invalid view " + key)
    require(type(view["workspace_focus"]) is list and len(view["workspace_focus"]) == 3,
            "complete workspace focus records required")
    for focus in view["workspace_focus"]:
        vector(focus, 4, "workspace focus", integer=True)
    for key, value in {"width": WIDTH, "height": HEIGHT, "workspace": 0, "presentation": 0,
                       "control_count": 68, "header": [72, 10, 1528, 102]}.items():
        require(typed_equal(layout[key], value), "canonical layout " + key + " differs")
    for key in ("show_cabinet", "bank_controls_in_cheeks", "sidebar_pedals"):
        require(type(layout[key]) is bool, "invalid layout " + key)
    for key in ("performance_panel", "keyboard_toolbar", "pedal_panel", "footer", "cabinet_panel",
                "cabinet_art", "workspace_panel"):
        vector(layout[key], 4, "layout " + key)
    for key in ("registration_panels", "manual_panels", "manual_rail_panels", "preset_key_panels"):
        require(type(layout[key]) is list and len(layout[key]) == 2, "incomplete layout " + key)
        for rect in layout[key]:
            vector(rect, 4, "layout " + key)
    controls = layout["controls"]
    require(type(controls) is list and len(controls) == 68, "all 68 control geometries required")
    identities = set()
    for control in controls:
        require(type(control) is dict and
                set(control) == {"id", "bounds", "label_bounds", "value_bounds", "track"},
                "incomplete control geometry")
        vector(control["id"], 4, "control identity", integer=True)
        identities.add(tuple(control["id"]))
        for key in ("bounds", "label_bounds", "value_bounds", "track"):
            vector(control[key], 4, "control " + key)
    require(len(identities) == 68 and sum(identity[0] == 19 for identity in identities) == 24,
            "duplicate control or incomplete 24-preset inventory")
    manuals, pedals = layout["manual_keys"], layout["pedal_keys"]
    require(type(manuals) is list and len(manuals) == 2 and
            all(type(keys) is list and len(keys) == 61 for keys in manuals) and
            type(pedals) is list and len(pedals) == 25, "all 147 playing-key geometries required")
    for keys in [*manuals, pedals]:
        for key in keys:
            require(type(key) is dict and set(key) == {"note", "bounds", "accidental", "hit", "top", "front"},
                    "incomplete playing-key geometry")
            vector(key["note"], 2, "key note", integer=True)
            vector(key["bounds"], 4, "key bounds")
            require(type(key["accidental"]) is bool, "invalid accidental marker")
            for name in ("hit", "top", "front"):
                require(type(key[name]) is list and len(key[name]) == 4, "incomplete key quad")
                for point in key[name]:
                    vector(point, 2, "key quad point")
    require(type(hit) is dict and set(hit) == {"controls", "manual_keys", "pedal_keys"},
            "incomplete hit record")
    require(type(hit["controls"]) is list and len(hit["controls"]) == 68 and
            type(hit["manual_keys"]) is list and len(hit["manual_keys"]) == 2 and
            all(type(keys) is list and len(keys) == 61 for keys in hit["manual_keys"]) and
            type(hit["pedal_keys"]) is list and len(hit["pedal_keys"]) == 25,
            "complete hit inventory required")
    groups = [(hit["controls"], controls), (hit["manual_keys"][0], manuals[0]),
              (hit["manual_keys"][1], manuals[1]), (hit["pedal_keys"], pedals)]
    for records, geometry in groups:
        for record, item in zip(records, geometry):
            field = "id" if "id" in item else "note"
            fields = {field, "probes", "visible"} if field == "id" else {field, "probes"}
            require(type(record) is dict and set(record) == fields and
                    typed_equal(record[field], item[field]), "incomplete or contradictory hit identity")
            if field == "id":
                require(type(record["visible"]) is bool, "invalid hit visibility")
            probes = record["probes"]
            require(type(probes) is list and len(probes) == 5, "five hit probes required")
            for probe in probes:
                require(type(probe) is dict and set(probe) == {"point", "hit"}, "incomplete hit probe")
                vector(probe["point"], 2, "hit point")
                vector(probe["hit"], 4, "hit identity", integer=True)


def validate_header(header):
    fixed = expected_header()
    records = {"renderer_before", "renderer_after", "model_before", "model_after",
               "session_before", "session_after", "hit_before", "hit_after", "info", "backend", "helper_probe"}
    require(type(header) is dict and set(header) == set(fixed) | records,
            "missing or unexpected native protocol fields")
    for key, value in fixed.items():
        require(typed_equal(header[key], value), "native protocol " + key + " differs from canonical case46")
    validate_transform(header["renderer_before"], [17, 23, 31, 127])
    validate_transform(header["renderer_after"])
    for name in ("model", "session", "hit"):
        require(typed_equal(header[name + "_before"], header[name + "_after"]),
                "paint changed complete " + name + " record")
    validate_model(header["model_before"], header["session_before"], header["hit_before"])
    backend = header["backend"]
    require(type(backend) is dict and set(backend) == {
        "name", "flags", "texture_formats", "maximum_texture_size", "sdl_version", "surface_format"},
        "incomplete software backend identity")
    require(backend["name"] == "software" and typed_equal(backend["sdl_version"], [2, 32, 10]),
            "unexpected SDL software backend")
    require(type(backend["flags"]) is int and backend["flags"] >= 0 and
            type(backend["surface_format"]) is int and backend["surface_format"] > 0,
            "invalid backend numeric identity")
    require(type(backend["texture_formats"]) is list and 0 < len(backend["texture_formats"]) <= 16 and
            all(type(value) is int and value > 0 for value in backend["texture_formats"]),
            "invalid backend texture formats")
    vector(backend["maximum_texture_size"], 2, "maximum texture size", integer=True)
    helper = header["helper_probe"]
    require(type(helper) is dict and set(helper) == {
        "present", "invoked", "bounds", "composition_scale", "before", "after", "unchanged"},
        "incomplete helper probe")
    require(type(helper["present"]) is bool and type(helper["invoked"]) is bool and
            helper["invoked"] is helper["present"], "contradictory helper availability/invocation")
    require(typed_equal(helper["bounds"], [76, 14, 1520, 94]) and
            typed_equal(helper["composition_scale"], [1, 1, 1]), "helper probe geometry differs")
    validate_transform(helper["before"], [17, 23, 31, 127])
    validate_transform(helper["after"], [17, 23, 31, 127])
    require(typed_equal(helper["before"], helper["after"]) and helper["unchanged"] is True,
            "helper changed renderer state or color")
    info = {
        "audio_running": True, "sample_rate": 48000, "buffer_frames": 512,
        "audio_driver": "fixed-software-fixture", "device_name": "fixed copied state",
        "status_message": "Frozen header material qualification", "clipped_samples": 0,
        "overlay": 0, "audio_choices": [], "selected_device": 0, "selected_sample_rate": 48000,
        "selected_buffer_frames": 512, "midi_available": False, "midi_open": False,
        "midi_backend": "", "midi_port": "", "midi_status": "", "midi_choices": [],
        "selected_midi_port": 0, "selected_midi_channels": [1, 2, 3],
        "selected_midi_expression": [0, 127, False], "active_midi_expression": [0, 127, False],
        "midi_expression_active": False, "midi_reconnect_pending": False, "midi_messages": 0,
        "inspection": None,
    }
    require(typed_equal(header["info"], info), "complete fixed information record differs")


def parse_frame(payload):
    require(len(payload) <= MAX_STDOUT_BYTES, "native stdout exceeded total byte bound")
    end = payload.find(b"\n", 0, MAX_HEADER_BYTES + 1)
    require(0 < end <= MAX_HEADER_BYTES, "missing bounded JSON-line frame header")
    header = json.loads(payload[:end].decode("utf-8"), object_pairs_hook=unique_members,
                        parse_constant=invalid_constant, parse_float=finite_float)
    validate_header(header)
    require(len(payload) - end - 1 == FRAME_BYTES, "missing or trailing canonical RGBA bytes")
    return header, memoryview(payload)[end + 1:], hashlib.sha256(payload[:end]).hexdigest()


def plane_from_moments(moments, width, height, denominator):
    """Fit z=a+b*x+c*y using ordinary local integer coordinates, without pixels.

    On a complete rectangular lattice the centered x/y covariance is zero.
    Multiplying each centered covariance by N keeps all sufficient statistics
    integer until the exact rational division. This differs from the original
    comparator's doubled-centered-coordinate implementation.
    """
    require(width > 1 and height > 1 and denominator > 0, "invalid plane dimensions")
    count = width * height
    total, squares, x_values, y_values = moments
    x_sum = height * width * (width - 1) // 2
    y_sum = width * height * (height - 1) // 2
    xx_sum = height * width * (width - 1) * (2 * width - 1) // 6
    yy_sum = width * height * (height - 1) * (2 * height - 1) // 6
    xx = count * xx_sum - x_sum * x_sum
    yy = count * yy_sum - y_sum * y_sum
    xz = count * x_values - x_sum * total
    yz = count * y_values - y_sum * total
    mean = Fraction(total, count * denominator)
    dx, dy = Fraction(xz, xx * denominator), Fraction(yz, yy * denominator)
    sse = (Fraction(squares) - Fraction(total * total, count) -
           Fraction(xz * xz, count * xx) - Fraction(yz * yz, count * yy)) / denominator ** 2
    require(sse >= 0, "negative exact plane residual")
    rms = math.sqrt(float(sse / count))
    return {
        "mean_exact": str(mean), "mean": float(mean),
        "dx_per_pixel_exact": str(dx), "dx_per_pixel": float(dx),
        "dy_per_pixel_exact": str(dy), "dy_per_pixel": float(dy),
        "residual_sse_exact": str(sse), "plane_residual_population_rms": rms,
        "rms_hex": rms.hex(),
        "ordinary_integer_moments": {
            "count": count, "denominator": denominator, "sum": total, "sum_squared": squares,
            "sum_x_times_value": x_values, "sum_y_times_value": y_values,
            "sum_x": x_sum, "sum_y": y_sum, "sum_x_squared": xx_sum, "sum_y_squared": yy_sum,
        },
    }


def measurements(raw):
    require(len(raw) == FRAME_BYTES, "statistics require the complete canonical RGBA frame")
    result = {}
    for name, rect, _, _, _ in REFERENCE_ROWS:
        x0, y0, width, height = rect
        moments = [[0, 0, 0, 0] for _ in range(4)]
        rgb = bytearray()
        for y in range(height):
            start = 4 * ((y0 + y) * WIDTH + x0)
            for x in range(width):
                offset = start + 4 * x
                r, g, b = raw[offset], raw[offset + 1], raw[offset + 2]
                rgb.extend((r, g, b))
                values = (r, g, b, 2126 * r + 7152 * g + 722 * b)
                for sums, value in zip(moments, values):
                    sums[0] += value
                    sums[1] += value * value
                    sums[2] += x * value
                    sums[3] += y * value
        planes = [plane_from_moments(sums, width, height, 10000 if index == 3 else 1)
                  for index, sums in enumerate(moments)]
        result[name] = {
            "box_xywh_half_open": list(rect), "decoded_patch_rgb_sha256": hashlib.sha256(rgb).hexdigest(),
            "encoded_rgb": dict(zip("RGB", planes[:3])), "encoded_y_prime": planes[3],
        }
    return result


def reference_measurements():
    result = {}
    for name, rect, sums, dy, sse in REFERENCE_ROWS:
        count = rect[2] * rect[3]
        mean_y = Fraction(2126 * sums[0] + 7152 * sums[1] + 722 * sums[2], 10000 * count)
        result[name] = {
            "encoded_rgb": {channel: {"mean_exact": str(Fraction(total, count))}
                            for channel, total in zip("RGB", sums)},
            "encoded_y_prime": {"mean_exact": str(mean_y), "dy_per_pixel_exact": dy,
                                "residual_sse_exact": sse},
        }
    return result


def numerical_screens(candidate):
    reference = reference_measurements()
    results, mean_errors, rms_errors = [], [], []

    def mean(data, name, channel="Y"):
        record = data[name]["encoded_y_prime"] if channel == "Y" else data[name]["encoded_rgb"][channel]
        return Fraction(record["mean_exact"])

    def exact(name, error, limit):
        results.append({"name": name, "error_exact": str(error), "error": float(error),
                        "limit_exact": str(limit), "limit": float(limit), "passed": error <= limit})

    def binary64(name, error, limit):
        require(math.isfinite(error), "nonfinite numerical result")
        results.append({"name": name, "error": error, "error_hex": error.hex(),
                        "limit": limit, "limit_hex": limit.hex(), "passed": error <= limit})

    for name, rect, _, _, _ in REFERENCE_ROWS:
        error = abs(mean(candidate, name) - mean(reference, name))
        mean_errors.append(error)
        exact(name + ":mean:Y", error, Fraction(3))
        for channel in "RGB":
            exact(name + ":mean:" + channel,
                  abs(mean(candidate, name, channel) - mean(reference, name, channel)), Fraction(4))
        count = rect[2] * rect[3]
        # Each rational SSE/N is converted once and square-rooted once. Do not
        # obtain RMS from rounded displayed values or change this arithmetic.
        rms = [math.sqrt(float(Fraction(data[name]["encoded_y_prime"]["residual_sse_exact"]) / count))
               for data in (candidate, reference)]
        rms_error = abs(rms[0] - rms[1])
        rms_errors.append(rms_error)
        binary64(name + ":rms:Y", rms_error, 1.2)
    for name, limit in VERTICAL_LIMITS:
        error = abs(Fraction(candidate[name]["encoded_y_prime"]["dy_per_pixel_exact"]) -
                    Fraction(reference[name]["encoded_y_prime"]["dy_per_pixel_exact"]))
        exact(name + ":vertical:Y", error, Fraction(limit))
    for left, right, limit in LATERAL_LIMITS:
        error = abs((mean(candidate, left) - mean(candidate, right)) -
                    (mean(reference, left) - mean(reference, right)))
        exact(left + "-minus-" + right, error, Fraction(limit))
    mean_mae = sum(mean_errors, Fraction(0)) / 18
    rms_mae = math.fsum(rms_errors) / 18.0
    exact("equal_patch_mean_Y_MAE", mean_mae, MEAN_MAE_LIMIT)
    binary64("equal_patch_RMS_Y_MAE", rms_mae, RMS_MAE_LIMIT)
    require(len(results) == 103 and len({row["name"] for row in results}) == 103,
            "frozen numerical criterion count/order differs")
    passed = sum(row["passed"] for row in results)
    return {
        "inequality_count": 103, "evaluated_count": len(results), "passed_count": passed,
        "failed_count": 103 - passed, "passed": passed == 103,
        "mean_error_exact": str(mean_mae), "rms_error": rms_mae, "rms_error_hex": rms_mae.hex(),
        "RMS_aggregation": "binary64 sqrt of exact SSE/N, binary64 abs, math.fsum in primary order, /18.0",
        "results": results,
    }


def bounded_timeout(token):
    try:
        value = float(token)
    except ValueError as error:
        raise argparse.ArgumentTypeError("timeout must be a finite number") from error
    if not math.isfinite(value) or not 0 < value <= MAX_TIMEOUT_SECONDS:
        raise argparse.ArgumentTypeError("timeout must be positive and at most 60 seconds")
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path, required=True, help="already-built native H1 material fixture")
    parser.add_argument("--timeout-seconds", type=bounded_timeout, default=DEFAULT_TIMEOUT_SECONDS,
                        help="native case46 deadline; default 20, maximum 60 for instrumented builds")
    args = parser.parse_args()
    report = {
        "schema": 1, "test": "standalone-header-statistics-v1", "status": "failed",
        "native_protocol": PROTOCOL, "case": CASE, "logical_size": [WIDTH, HEIGHT],
        "primary_patch_order": list(PRIMARY), "protocol_passed": False, "helper_passed": False,
        "identities": {
            "frozen_fixture_source_sha256": FIXTURE_SHA256, "contract_sha256": CONTRACT_SHA256,
            "reference_observations_sha256": OBSERVATIONS_SHA256,
            "reference_image_sha256": REFERENCE_IMAGE_SHA256, "reference_decoded_rgb_sha256": REFERENCE_RGB_SHA256,
            "independent_comparator_sha256": COMPARATOR_SHA256,
            "reference_origin": "immutable literals from A22 reference observations; no runtime image decode",
        },
        "resources": {
            "native_invocations": 0, "canonical_rgba_bytes": FRAME_BYTES, "header_max_bytes": MAX_HEADER_BYTES,
            "stdout_max_bytes": MAX_STDOUT_BYTES, "stderr_max_bytes": MAX_STDERR_BYTES,
            "process_timeout_seconds": args.timeout_seconds, "cleanup_wait_seconds": CLEANUP_TIMEOUT_SECONDS,
            "retained_frames": 1, "images_persisted": 0,
        },
        "python": platform.python_version(), "numerical": {
            "inequality_count": 103, "evaluated_count": 0, "passed_count": 0,
            "failed_count": 0, "passed": False, "results": [],
        },
        "scope": "one canonical numerical regression; complete paired, visual, timing and platform gates remain separate",
    }
    try:
        source = Path(__file__).resolve(strict=True)
        fixture = source.with_name("test_standalone_header_material.cpp")
        report["identities"]["test_source_sha256"] = sha256_file(source)
        report["identities"]["fixture_source_admission"] = admit_fixture_bytes(fixture.read_bytes())
        executable = args.executable.resolve(strict=True)
        require(executable.is_file() and os.access(executable, os.X_OK), "native fixture is not executable")
        executable_sha = sha256_file(executable)
        report["identities"].update({"executable": str(executable), "executable_sha256": executable_sha})
        report["resources"]["native_invocations"] = 1
        payload = capture_frame(executable, args.timeout_seconds)
        header, raw, header_sha = parse_frame(payload)
        report["protocol_passed"] = True
        report["identities"].update({"header_sha256": header_sha, "rgba_sha256": hashlib.sha256(raw).hexdigest()})
        report["backend"] = header["backend"]
        helper = header["helper_probe"]
        report["helper_passed"] = helper["present"] and helper["invoked"]
        report["helper"] = {"present": helper["present"], "invoked": helper["invoked"],
                            "passed": report["helper_passed"]}
        # Do not reject a genuinely absent old helper before measuring: baseline
        # qualification must distinguish its 59 numerical failures from parsing.
        observed = measurements(raw)
        report["patches"] = observed
        report["numerical"] = numerical_screens(observed)
        del raw, payload
        require(sha256_file(executable) == executable_sha, "native executable changed during regression")
        require(sha256_file(fixture) == report["identities"]["fixture_source_admission"]["observed_sha256"], "native fixture source changed during regression")
        require(sha256_file(source) == report["identities"]["test_source_sha256"],
                "regression source changed during execution")
        if report["helper_passed"] and report["numerical"]["passed"]:
            report["status"] = "passed"
    except (OSError, ValueError, KeyError, TypeError, IndexError, RecursionError, OverflowError) as error:
        report["error"] = str(error)[:MAX_ERROR_CHARACTERS]
    print(json.dumps(report, separators=(",", ":"), allow_nan=False), flush=True)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
