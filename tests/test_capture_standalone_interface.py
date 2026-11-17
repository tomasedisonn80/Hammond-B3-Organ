#!/usr/bin/env python3
"""Validate retained native frames and reject synthetic painted-state mutations.

The eight positive fixtures are actual v3 application diagnostics. Mutations
exist only in copied Python dictionaries; no native process or image is edited.
All three final painted records are changed together so the new checks cannot
pass merely because the existing painted-record equality guard rejects them.

The five default extensions and two optional header-aspect scenes use explicitly
synthetic in-memory contract variants and pixel buffers to test admission rules.
CLI orchestration tests mock native/image boundaries and use temporary non-image
byte placeholders. None of these tests creates native capture evidence; root
must run the selected thirteen- or fifteen-case native suite.
"""

from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
GALLERY = ROOT / "examples/demos/standalone-interface-preview-v3"
SPEC = importlib.util.spec_from_file_location("interface_capture", ROOT / "tools/capture_standalone_interface.py")
CAPTURE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CAPTURE)
CASES = (
    ("play-reference-1672x941", 1672, 941, "play", "dimensional", 66),
    ("play-default-1280x900", 1280, 900, "play", "dimensional", 66),
    ("play-minimum-960x700", 960, 700, "play", "dimensional", 66),
    ("service-reference-1672x941", 1672, 941, "service", "dimensional", 66),
    ("service-minimum-960x700", 960, 700, "service", "dimensional", 66),
    ("rotary-reference-1672x941", 1672, 941, "rotary", "dimensional", 66),
    ("rotary-minimum-960x700", 960, 700, "rotary", "dimensional", 66),
    ("flat-minimum-960x700", 960, 700, "play", "flat", 68),
)
ADDED_CASES = (
    ("play-minimum-active-1400x820", 1400, 820, "play", "dimensional", 66, "standard"),
    ("flat-reference-1672x941", 1672, 941, "play", "flat", 68, "standard"),
    ("play-toolbar-focus-1672x941", 1672, 941, "play", "dimensional", 151, "toolbar-focus"),
    ("play-pedal-focus-1672x941", 1672, 941, "play", "dimensional", 161, "pedal-focus"),
    ("play-wide-1920x1080", 1920, 1080, "play", "dimensional", 66, "standard"),
)
HEADER_ASPECT_CASES = (
    ("play-header-wide-1920x820", 1920, 820, "play", "dimensional", 66, "standard"),
    ("play-header-tall-1400x1080", 1400, 1080, "play", "dimensional", 66, "standard"),
)
# Independent literal canonical samples, not imported from the capture utility.
FOCUS_PROBES = {
    "toolbar-focus": {"top": (1448, 616, 1576, 618), "bottom": (1448, 640, 1576, 642),
                      "left": (1444, 620, 1446, 638), "right": (1578, 620, 1580, 638)},
    "pedal-focus": {"top": (1556, 774, 1575, 776), "bottom": (1556, 850, 1575, 852),
                    "left": (1553, 778, 1555, 848), "right": (1576, 778, 1578, 848)},
}
HELD = {"upper": 2, "lower": 1, "pedals": 1}
POINTER = {"sdl_captured": False, "ui_captured": False, "attempts": 0,
           "successes": 0, "losses": 0, "release_calls": 0}
MISSING = object()


class InterfaceCaptureValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.diagnostics = {
            case[0]: json.loads((GALLERY / "diagnostics" / f"{case[0]}.json").read_text(encoding="utf-8"))
            for case in CASES
        }

    def altered_painted(self, field, value):
        data = deepcopy(self.diagnostics[CASES[0][0]])
        for name in ("screenshot", "before_shutdown", "last_painted"):
            frame = data["presentation"][name]
            if value is MISSING:
                del frame[field]
            else:
                frame[field] = deepcopy(value)
        return data

    def reject(self, field, value, message):
        data = self.altered_painted(field, value)
        # The independently observed replay endpoint remains valid throughout.
        self.assertEqual(data["replay"]["before_shutdown"]["manual_notes"], [[60, 64], [67]])
        self.assertEqual(data["replay"]["before_shutdown"]["pedal_ids"], [3])
        with self.assertRaisesRegex(ValueError, message):
            CAPTURE.validate(data, *CASES[0][1:])

    def test_all_eight_retained_native_diagnostics_pass(self):
        for name, *arguments in CASES:
            with self.subTest(case=name):
                result = CAPTURE.validate(self.diagnostics[name], *arguments)
                self.assertIs(result["passed"], True)
                self.assertEqual(result["actual_painted_view"]["held_targets"], HELD)
                self.assertEqual(result["actual_painted_view"]["pointer_capture"], POINTER)

    def test_thirteen_case_matrix_preserves_original_identities_and_adds_required_views(self):
        self.assertEqual(CAPTURE.CASES, tuple(case[:5] for case in (*CASES, *ADDED_CASES)))
        self.assertEqual(CAPTURE.CASE_SCENES, {
            "play-toolbar-focus-1672x941": "toolbar-focus",
            "play-pedal-focus-1672x941": "pedal-focus",
        })
        self.assertEqual(len({case[0] for case in CAPTURE.CASES}), 13)

    def test_optional_header_aspects_are_exact_distinct_dimensional_play_views(self):
        self.assertEqual(CAPTURE.HEADER_ASPECT_CASES, tuple(case[:5] for case in HEADER_ASPECT_CASES))
        combined = CAPTURE.CASES + CAPTURE.HEADER_ASPECT_CASES
        self.assertEqual(len(combined), 15)
        self.assertEqual(len({case[0] for case in combined}), 15)
        self.assertEqual(len({case[1:5] for case in combined}), 13)  # Two existing canonical focus scenes.

    def run_cli_with_mocked_native_and_image_boundaries(self, extra_args):
        """Exercise the real CLI/receipt path without a native process or image."""
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source, build, output = (base / name for name in ("source", "build", "gallery"))
            source.mkdir()
            build.mkdir()
            fixture_bytes = b"Unit-test fixture only; never an application or image.\n"
            fixture_sha256 = hashlib.sha256(fixture_bytes).hexdigest()
            executable = base / "native-stub"
            executable.write_bytes(fixture_bytes)
            executable.chmod(0o700)
            qualified_sources = {}
            for name in CAPTURE.REQUIRED_QUALIFIED_SOURCES:
                path = source / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(fixture_bytes)
                qualified_sources[name] = fixture_sha256
            qualification = base / "qualification.json"
            qualification.write_text(json.dumps({"binary_sha256": fixture_sha256,
                                                  "source_sha256": qualified_sources}), encoding="utf-8")
            for name in ("EmbeddedProfile.h", "ReferenceArtData.h", "ReferenceApronData.h"):
                path = build / "apps/standalone/generated" / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(fixture_bytes)
            (build / "CMakeCache.txt").write_text("HAMMOND_BUILD_STANDALONE:BOOL=ON\n", encoding="utf-8")
            argv = [str(ROOT / "tools/capture_standalone_interface.py"),
                    "--exe", str(executable), "--source-root", str(source), "--build-root", str(build),
                    "--source-qualification", str(qualification), "--expected-exe-sha256", fixture_sha256,
                    "--output", str(output), "--dummy-sdl", *extra_args]
            commands, sizes = [], {}

            def native_boundary(command, **options):
                self.assertEqual(command[0], str(executable.resolve()))
                self.assertEqual(options["timeout"], 12.0)
                self.assertIs(options["capture_output"], True)
                self.assertIs(options["check"], False)
                self.assertEqual(options["stdin"], CAPTURE.subprocess.DEVNULL)
                self.assertEqual(options["env"]["SDL_VIDEODRIVER"], "dummy")
                self.assertEqual(options["env"]["SDL_AUDIODRIVER"], "dummy")
                self.assertEqual(options["env"]["SDL_RENDER_DRIVER"], "software")
                commands.append(command)
                bmp = Path(command[command.index("--screenshot") + 1])
                sizes[bmp.stem] = (int(command[command.index("--width") + 1]),
                                   int(command[command.index("--height") + 1]))
                bmp.write_bytes(fixture_bytes)
                Path(command[command.index("--diagnostics") + 1]).write_text("{}\n", encoding="utf-8")
                return SimpleNamespace(returncode=0, stdout=b"", stderr=b"")

            class ImageBoundary:
                mode = "RGB"

                def __init__(self, path):
                    self.size = sizes[Path(path).stem]

                def __enter__(self):
                    return self

                def __exit__(self, *_):
                    return False

                def load(self):
                    pass

                def tobytes(self):
                    return fixture_bytes

                def save(self, path, **_):
                    path.write_bytes(fixture_bytes)

            pillow = SimpleNamespace(Image=SimpleNamespace(open=ImageBoundary), __version__="unit-test-stub")
            with (mock.patch.object(sys, "argv", argv), mock.patch.dict(sys.modules, {"PIL": pillow}),
                  mock.patch.object(CAPTURE.platform, "platform", return_value="unit-test"),
                  mock.patch.object(CAPTURE, "git_identity", return_value={"head": "unit-test", "committed_tree": "unit-test"}),
                  mock.patch.object(CAPTURE.subprocess, "run", side_effect=native_boundary),
                  mock.patch.object(CAPTURE, "validate", side_effect=lambda *_: {}) as validation,
                  mock.patch.object(CAPTURE, "validate_focus_pixels", return_value=None),
                  redirect_stdout(io.StringIO()) as stdout):
                result = CAPTURE.main()
            record = json.loads((output / "provenance.json").read_text(encoding="utf-8"))
            manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["status"], "passed")
            self.assertIs(record["all_recorded_inputs_unchanged"], True)
            return result, record, json.loads(stdout.getvalue()), commands, validation.call_args_list

    def test_cli_selects_exact_default_or_extended_matrix_and_records_actual_count(self):
        original = tuple((*case, "standard") for case in CASES) + ADDED_CASES
        for options, expected in (([], original), (["--include-header-aspects"], original + HEADER_ASPECT_CASES)):
            with self.subTest(options=options):
                result, record, summary, commands, validations = self.run_cli_with_mocked_native_and_image_boundaries(options)
                self.assertEqual(result, 0)
                self.assertEqual(record["status"], "passed")
                self.assertEqual(summary["captures"], len(expected))
                self.assertEqual(len(commands), len(expected))
                self.assertEqual(tuple((case["name"], case["width"], case["height"], case["workspace"],
                                        case["presentation"], case["scene"]) for case in record["cases"]),
                                 tuple((*case[:5], case[-1]) for case in expected))
                self.assertEqual([call.args[1:] for call in validations], [case[1:] for case in expected])
                self.assertEqual([case["command"] for case in record["cases"]], commands)
                self.assertTrue(all(case["status"] == "passed" for case in record["cases"]))
                self.assertEqual(record["capture_contract"], "standalone-interface-capture-v1")
                if options:
                    self.assertIn("15 views", record["case_matrix"])
                    self.assertIn("Original thirteen views retained in order", record["case_matrix"])
                    for case in HEADER_ASPECT_CASES:
                        self.assertIn(case[0], record["case_matrix"])
                else:
                    self.assertEqual(record["case_matrix"],
                                     "Original twelve views retained in order; play-wide-1920x1080 appended for apron inspection.")

    def test_optional_header_aspects_preserve_dummy_acknowledgment_and_new_directory_refusal(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            sentinel = output / "retained.txt"
            sentinel.write_bytes(b"retain these bytes")
            argv = ["capture_standalone_interface.py", "--exe", "unused", "--source-root", "unused",
                    "--build-root", "unused", "--source-qualification", "unused",
                    "--expected-exe-sha256", "0" * 64, "--output", str(output), "--include-header-aspects"]
            with (mock.patch.object(sys, "argv", argv), mock.patch.object(CAPTURE.subprocess, "run") as native,
                  redirect_stderr(io.StringIO()) as stderr):
                with self.assertRaises(SystemExit) as missing_ack:
                    CAPTURE.main()
                self.assertEqual(missing_ack.exception.code, 2)
                self.assertIn("--dummy-sdl", stderr.getvalue())
                argv.append("--dummy-sdl")
                with self.assertRaisesRegex(ValueError, "output already exists; refusing to overwrite"):
                    CAPTURE.main()
                native.assert_not_called()
            self.assertEqual(list(output.iterdir()), [sentinel])
            self.assertEqual(sentinel.read_bytes(), b"retain these bytes")

    def test_original_replay_and_state_bytes_match_immutable_gallery(self):
        self.assertEqual(CAPTURE.STATE.encode("ascii"), (GALLERY / "inputs/controls.b3controls").read_bytes())
        for _, _, _, workspace, presentation, expected_events in CASES:
            with self.subTest(workspace=workspace, presentation=presentation):
                script, events = CAPTURE.replay(workspace, presentation)
                self.assertEqual(script.encode("ascii"),
                                 (GALLERY / "inputs" / f"{workspace}-{presentation}.b3uireplay").read_bytes())
                self.assertEqual(events, expected_events)

    def test_focus_replays_retain_original_prefix_and_target_exact_semantic_stops(self):
        original, _ = CAPTURE.replay("play", "dimensional")
        for scene, tabs, expected_events, ending in (
            ("toolbar-focus", 66, 151,
             ["1500 key_down Return none 0", "1510 key_up Return none", "1550 key_down W none 0"]),
            ("pedal-focus", 71, 161,
             ["1500 key_down End none 0", "1510 key_up End none", "1550 key_down Space none 0"]),
        ):
            with self.subTest(scene=scene):
                script, events = CAPTURE.replay("play", "dimensional", scene)
                self.assertTrue(script.startswith(original))
                records = [line for line in script.splitlines()[2:] if line and not line.startswith("#")]
                self.assertEqual(events, expected_events)
                self.assertEqual(len(records), expected_events)
                self.assertEqual(sum(" key_down Tab " in line for line in records), tabs)
                self.assertEqual(records[-3:], ending)
                times = [int(line.split()[0]) for line in records]
                self.assertTrue(all(left < right for left, right in zip(times, times[1:])))
                self.assertEqual(CAPTURE.DURATION_MS - times[-1], 250)
                for key in ("A", "D", "G", "S", "W", "Space"):
                    self.assertFalse(any(f" key_up {key} " in line for line in records))

    def contract_variant(self, case):
        """A dictionary-only validator input, never an observed native capture."""
        _, width, height, workspace, presentation, event_count, scene = case
        source = "flat-minimum-960x700" if presentation == "flat" else "play-reference-1672x941"
        data = deepcopy(self.diagnostics[source])
        data["runtime"].update(window_width=width, drawable_width=width,
                               window_height=height, drawable_height=height)
        data["replay"].update(scheduled_events=event_count, pushed_events=event_count)
        for name in ("screenshot", "before_shutdown", "last_painted"):
            data["presentation"][name].update(window_width=width, window_height=height,
                                              workspace=workspace, presentation=presentation)
        if scene != "standard":
            data["replay"]["accepted_note_on_commands"] = 5
            data["replay"]["before_shutdown"]["pedal_ids"] = [2, 3] if scene == "toolbar-focus" else [3, 25]
            for name in ("screenshot", "before_shutdown", "last_painted"):
                data["presentation"][name]["held_targets"]["pedals"] = 2
        return data

    def test_added_scene_contract_variants_reuse_complete_semantic_validation(self):
        for case in (*ADDED_CASES, *HEADER_ASPECT_CASES):
            with self.subTest(case=case[0]):
                data = self.contract_variant(case)
                result = CAPTURE.validate(data, *case[1:])
                self.assertIs(result["passed"], True)
                self.assertIs(result["complete_control_state_checked"], True)
                self.assertEqual(result["ui_events"], case[5])
                self.assertEqual(result["held_manual_notes"], [[60, 64], [67]])
                self.assertEqual(result["held_pedal_ids"], data["replay"]["before_shutdown"]["pedal_ids"])
                self.assertEqual(result["actual_painted_view"]["pointer_capture"], POINTER)
                if case[-1] != "standard":
                    self.assertIs(result["focus_scene"]["original_four_holds_preserved"], True)
                    self.assertIs(result["focus_scene"]["ordinary_focus_id_exported"], False)
                    self.assertIs(result["focus_scene"]["pixel_focus_check_required"], True)
                else:
                    self.assertNotIn("focus_scene", result)

    def test_added_cases_reject_wrong_dimensions_and_painted_presentation(self):
        for case in (*ADDED_CASES, *HEADER_ASPECT_CASES):
            for field in ("window_width", "window_height", "drawable_width", "drawable_height"):
                with self.subTest(case=case[0], field=field):
                    data = self.contract_variant(case)
                    data["runtime"][field] += 1
                    with self.assertRaisesRegex(ValueError, "actual logical/drawable dimensions differ"):
                        CAPTURE.validate(data, *case[1:])
            for field, value in (("workspace", "service"), ("presentation", "flat" if case[4] == "dimensional" else "dimensional")):
                with self.subTest(case=case[0], field=field):
                    data = self.contract_variant(case)
                    for name in ("screenshot", "before_shutdown", "last_painted"):
                        data["presentation"][name][field] = value
                    with self.assertRaisesRegex(ValueError, "actual painted screenshot is not the requested view/size"):
                        CAPTURE.validate(data, *case[1:])

    def test_added_cases_reject_changed_controls_and_loss_of_original_holds(self):
        for case in (*ADDED_CASES, *HEADER_ASPECT_CASES):
            with self.subTest(case=case[0], mutation="controls"):
                data = self.contract_variant(case)
                for controls in (data["controls"], data["replay"]["desired_controls_before_shutdown"],
                                 data["replay"]["before_shutdown"]["controls"]):
                    controls["percussion"]["enabled"] = False
                with self.assertRaisesRegex(ValueError, "final live control state differs"):
                    CAPTURE.validate(data, *case[1:])
            with self.subTest(case=case[0], mutation="original hold"):
                data = self.contract_variant(case)
                data["replay"]["before_shutdown"]["manual_notes"][0] = [60]
                with self.assertRaisesRegex(ValueError, "expected Upper/Lower/Pedal holds missing"):
                    CAPTURE.validate(data, *case[1:])

    def test_focus_scenes_require_exact_fifth_owner_and_zero_releases(self):
        for case in (case for case in ADDED_CASES if case[-1] != "standard"):
            for wrong_pedals in ([3], [2, 25], [2, 3, 25]):
                with self.subTest(case=case[0], pedals=wrong_pedals):
                    data = self.contract_variant(case)
                    data["replay"]["before_shutdown"]["pedal_ids"] = wrong_pedals
                    with self.assertRaisesRegex(ValueError, "expected Upper/Lower/Pedal holds missing"):
                        CAPTURE.validate(data, *case[1:])
            for field, value in (("accepted_note_on_commands", 4), ("accepted_note_on_commands", 6),
                                 ("accepted_note_off_commands", 1)):
                with self.subTest(case=case[0], field=field, value=value):
                    data = self.contract_variant(case)
                    data["replay"][field] = value
                    with self.assertRaisesRegex(ValueError, "held-note ownership, device or observation counts differ"):
                        CAPTURE.validate(data, *case[1:])
            data = self.contract_variant(case)
            for name in ("screenshot", "before_shutdown", "last_painted"):
                data["presentation"][name]["held_targets"]["pedals"] = 1
            with self.assertRaisesRegex(ValueError, "actual painted held targets"):
                CAPTURE.validate(data, *case[1:])

    def test_focus_scenes_require_observed_edited_four_owner_prefix(self):
        for case in (case for case in ADDED_CASES if case[-1] != "standard"):
            with self.subTest(case=case[0]):
                data = self.contract_variant(case)
                data["replay"]["observations"] = [item for item in data["replay"]["observations"]
                                                  if item["controls"] != CAPTURE.FINAL_CONTROLS]
                with self.assertRaisesRegex(ValueError, "no observed edited four-owner state"):
                    CAPTURE.validate(data, *case[1:])

    @staticmethod
    def focus_pixel_contract(scene, mode="RGB"):
        """Synthetic probe bytes for unit tests only; no image file is created."""
        channels = 3 if mode == "RGB" else 4
        pixels = bytearray(1672 * 941 * channels)
        cyan = bytes((165, 228, 223) if channels == 3 else (165, 228, 223, 255))
        for left, top, right, bottom in FOCUS_PROBES[scene].values():
            for y in range(top, bottom):
                start = (y * 1672 + left) * channels
                pixels[start:start + (right - left) * channels] = cyan * (right - left)
        return bytes(pixels)

    def test_focus_pixel_receipts_check_all_four_edges_and_bind_decoded_bytes(self):
        for scene, counts in (("toolbar-focus", {"top": 256, "bottom": 256, "left": 36, "right": 36}),
                              ("pedal-focus", {"top": 38, "bottom": 38, "left": 140, "right": 140})):
            for mode in ("RGB", "RGBA"):
                with self.subTest(scene=scene, mode=mode):
                    pixels = self.focus_pixel_contract(scene, mode)
                    result = CAPTURE.validate_focus_pixels(mode, (1672, 941), pixels, scene)
                    self.assertIs(result["passed"], True)
                    self.assertEqual(result["matched_pixels"], counts)
                    self.assertEqual(result["edge_probe_rectangles"], FOCUS_PROBES[scene])
                    self.assertEqual(result["decoded_sha256"], hashlib.sha256(pixels).hexdigest())

    def test_each_focus_edge_rejects_even_one_missing_or_wrong_color_pixel(self):
        for scene in FOCUS_PROBES:
            original = self.focus_pixel_contract(scene)
            for edge, (left, top, _, _) in FOCUS_PROBES[scene].items():
                with self.subTest(scene=scene, edge=edge):
                    pixels = bytearray(original)
                    offset = (top * 1672 + left) * 3
                    pixels[offset + 2] = 222
                    with self.assertRaisesRegex(ValueError, f"{edge} cyan focus pixels missing"):
                        CAPTURE.validate_focus_pixels("RGB", (1672, 941), pixels, scene)
            other_scene = "pedal-focus" if scene == "toolbar-focus" else "toolbar-focus"
            with self.assertRaisesRegex(ValueError, "cyan focus pixels missing"):
                CAPTURE.validate_focus_pixels("RGB", (1672, 941), original, other_scene)

    def test_focus_pixel_checks_reject_wrong_size_mode_or_truncated_bytes(self):
        pixels = self.focus_pixel_contract("toolbar-focus")
        with self.assertRaisesRegex(ValueError, "1672x941 reference frame"):
            CAPTURE.validate_focus_pixels("RGB", (1400, 820), pixels, "toolbar-focus")
        for mode, value in (("L", pixels), ("RGB", pixels[:-1]), ("RGBA", pixels)):
            with self.subTest(mode=mode, bytes=len(value)):
                with self.assertRaisesRegex(ValueError, "complete RGB/RGBA decoded bytes"):
                    CAPTURE.validate_focus_pixels(mode, (1672, 941), value, "toolbar-focus")
        self.assertIsNone(CAPTURE.validate_focus_pixels("RGB", (1672, 941), pixels))

    def test_unknown_or_inapplicable_focus_scenes_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "unknown capture scene"):
            CAPTURE.replay("play", "dimensional", "unknown")
        with self.assertRaisesRegex(ValueError, "unknown capture scene"):
            CAPTURE.validate(self.diagnostics[CASES[0][0]], *CASES[0][1:], "unknown")
        with self.assertRaisesRegex(ValueError, "unknown capture scene"):
            CAPTURE.validate_focus_pixels("RGB", (1672, 941), b"", "unknown")
        for workspace, presentation in (("rotary", "dimensional"), ("play", "flat")):
            with self.subTest(workspace=workspace, presentation=presentation):
                with self.assertRaisesRegex(ValueError, "focused scenes require Dimensional Play"):
                    CAPTURE.replay(workspace, presentation, "toolbar-focus")
        with self.assertRaisesRegex(ValueError, "reference-size Dimensional Play"):
            CAPTURE.validate(self.diagnostics[CASES[0][0]], 1400, 820, "play", "dimensional", 151, "toolbar-focus")

    def backend_record(self, available, backend, state):
        # Contract variants are copied diagnostics, not newly observed captures.
        data = deepcopy(self.diagnostics[CASES[0][0]])
        data["midi"].update(backend_available=available, backend=backend,
                            state_before_shutdown=state, state_after_shutdown=state)
        return data

    def test_consistent_compiled_backend_facts_choose_the_exact_inert_state(self):
        for available, backend, state in ((False, "unavailable", "unavailable"),
                                          (True, "ALSA", "closed"),
                                          (True, "CoreMIDI", "closed"),
                                          (True, "WinMM", "closed")):
            with self.subTest(available=available, backend=backend):
                data = self.backend_record(available, backend, state)
                result = CAPTURE.validate(data, *CASES[0][1:])
                self.assertIs(result["passed"], True)
                self.assertIs(result["midi_backend_available"], available)
                self.assertEqual(result["midi_backend"], backend)
                self.assertEqual(result["midi_state"], state)

    def test_missing_malformed_or_contradictory_backend_facts_are_rejected(self):
        invalid = (
            ("backend_available", MISSING), ("backend_available", None),
            ("backend_available", 0), ("backend_available", 1),
            ("backend_available", "false"), ("backend_available", "true"),
            ("backend_available", []), ("backend_available", {}),
            ("backend", MISSING), ("backend", None), ("backend", True),
            ("backend", 0), ("backend", []), ("backend", {}),
            ("backend", ""), ("backend", "JACK"), ("backend", "alsa"),
        )
        for available, backend, state in ((True, "ALSA", "closed"), (False, "unavailable", "unavailable")):
            for field, value in (*invalid, ("backend", "unavailable" if available else "ALSA")):
                with self.subTest(available=available, field=field, value=value):
                    data = self.backend_record(available, backend, state)
                    if value is MISSING:
                        del data["midi"][field]
                    else:
                        data["midi"][field] = value
                    with self.assertRaisesRegex(ValueError, "compiled MIDI backend facts"):
                        CAPTURE.validate(data, *CASES[0][1:])

    def test_both_midi_states_must_match_the_compiled_backend(self):
        for available, backend, state in ((True, "ALSA", "closed"), (False, "unavailable", "unavailable")):
            wrong_states = (MISSING, None, False, 0, [], {}, "open", "faulted", "closing", "",
                            "unavailable" if available else "closed")
            for fields in (("state_before_shutdown",), ("state_after_shutdown",),
                           ("state_before_shutdown", "state_after_shutdown")):
                for value in wrong_states:
                    with self.subTest(available=available, fields=fields, value=value):
                        data = self.backend_record(available, backend, state)
                        for field in fields:
                            if value is MISSING:
                                del data["midi"][field]
                            else:
                                data["midi"][field] = value
                        with self.assertRaisesRegex(ValueError, "state differs from the declared compiled backend"):
                            CAPTURE.validate(data, *CASES[0][1:])

    def test_neither_backend_mode_allows_port_or_device_activity(self):
        mutations = (("source", "native"), ("source", "synthetic-replay"),
                     ("generation", 1), ("generation", False), ("generation", 0.0),
                     ("opened_port_index", 1), ("opened_port_index", False), ("opened_port_index", 0.0),
                     ("requested_port", "controller"), ("port_name", "controller"),
                     ("active_before_shutdown", True), ("active_before_shutdown", 0))
        for available, backend, state in ((True, "ALSA", "closed"), (False, "unavailable", "unavailable")):
            for field, value in mutations:
                with self.subTest(available=available, field=field, value=value):
                    data = self.backend_record(available, backend, state)
                    data["midi"][field] = value
                    with self.assertRaisesRegex(ValueError, "opened/enumerated a native MIDI device"):
                        CAPTURE.validate(data, *CASES[0][1:])
            data = self.backend_record(available, backend, state)
            data["midi_replay"] = {}
            with self.subTest(available=available, field="midi_replay"):
                with self.assertRaisesRegex(ValueError, "opened/enumerated a native MIDI device"):
                    CAPTURE.validate(data, *CASES[0][1:])

    def test_device_and_discovery_facts_must_be_complete_typed_and_inert(self):
        for available, backend, state in ((True, "ALSA", "closed"), (False, "unavailable", "unavailable")):
            for group in ("device", "discovery"):
                original = self.diagnostics[CASES[0][0]]["midi"][group]
                for field, expected in original.items():
                    wrong_values = (MISSING, True, 0, None) if type(expected) is bool else (MISSING, 1, -1, False, 0.0, "0", None)
                    for value in wrong_values:
                        with self.subTest(available=available, group=group, field=field, value=value):
                            data = self.backend_record(available, backend, state)
                            if value is MISSING:
                                del data["midi"][group][field]
                            else:
                                data["midi"][group][field] = value
                            with self.assertRaisesRegex(ValueError, "opened/enumerated a native MIDI device"):
                                CAPTURE.validate(data, *CASES[0][1:])
                for value in (MISSING, None, {}, [], {**original, "other": 0}):
                    with self.subTest(available=available, group=group, value=value):
                        data = self.backend_record(available, backend, state)
                        if value is MISSING:
                            del data["midi"][group]
                        else:
                            data["midi"][group] = value
                        with self.assertRaisesRegex(ValueError, "opened/enumerated a native MIDI device"):
                            CAPTURE.validate(data, *CASES[0][1:])

    def test_midi_shutdown_remains_strict_in_both_backend_modes(self):
        for available, backend, state in ((True, "ALSA", "closed"), (False, "unavailable", "unavailable")):
            for field, expected in (("quiescent_after_shutdown", True), ("diagnostics_stable_after_shutdown", True),
                                    ("active_after_shutdown", False), ("shutdown_failed", False), ("startup_failed", False)):
                for value in (not expected, int(expected), None):
                    with self.subTest(available=available, field=field, value=value):
                        data = self.backend_record(available, backend, state)
                        data["midi"][field] = value
                        with self.assertRaisesRegex(ValueError, "MIDI shutdown was not clean and quiescent"):
                            CAPTURE.validate(data, *CASES[0][1:])

    def test_wrong_painted_hold_counts_are_rejected_despite_valid_endpoint(self):
        for division, count in HELD.items():
            for value in (count - 1, count + 1, -1):
                with self.subTest(division=division, value=value):
                    self.reject("held_targets", {**HELD, division: value}, "actual painted held targets")

    def test_painted_hold_counts_require_integers_without_boolean_coercion(self):
        for division, count in HELD.items():
            for value in (True, float(count), str(count), None):
                with self.subTest(division=division, value=value):
                    self.reject("held_targets", {**HELD, division: value}, "actual painted held targets")

    def test_missing_or_extra_painted_holds_are_rejected(self):
        for value in (MISSING, None, {}, [2, 1, 1], {"upper": 2, "lower": 1}, {**HELD, "other": 0}):
            with self.subTest(value=value):
                self.reject("held_targets", value, "actual painted held targets")

    def test_pointer_capture_activity_is_rejected_for_keyboard_only_replay(self):
        for field in POINTER:
            value = True if field in ("sdl_captured", "ui_captured") else 1
            with self.subTest(field=field):
                self.reject("pointer_capture", {**POINTER, field: value}, "unexpected pointer capture")

    def test_pointer_flags_and_counters_preserve_boolean_and_integer_types(self):
        for field in ("sdl_captured", "ui_captured"):
            for value in (0, "false", None):
                with self.subTest(field=field, value=value):
                    self.reject("pointer_capture", {**POINTER, field: value}, "unexpected pointer capture")
        for field in ("attempts", "successes", "losses", "release_calls"):
            for value in (False, 0.0, "0", None):
                with self.subTest(field=field, value=value):
                    self.reject("pointer_capture", {**POINTER, field: value}, "unexpected pointer capture")

    def test_missing_or_extra_capture_facts_are_rejected(self):
        missing_counter = {key: value for key, value in POINTER.items() if key != "release_calls"}
        for value in (MISSING, None, {}, missing_counter, {**POINTER, "other": 0}):
            with self.subTest(value=value):
                self.reject("pointer_capture", value, "unexpected pointer capture")


if __name__ == "__main__":
    unittest.main()
