#!/usr/bin/env python3
"""Independent native MIDI CLI and modal acceptance without MIDI hardware.

Set HAMMOND_STANDALONE_EXECUTABLE to the built native application. All windowed
runs explicitly use SDL dummy drivers. Ordinary runs only Apply No input; the
one finite negative-open case requests a unique nonexistent exact
name. Backend unavailability, empty enumeration and enumeration errors remain
distinct observed outcomes. No production parser, handler or layout is imported.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
import uuid

from test_standalone_app import diagnostic_excerpt


TIMEOUT = 12
CHANNEL_OPTIONS = (
    "--midi-upper-channel", "--midi-lower-channel", "--midi-pedal-channel",
)
DEFAULT_CHANNELS = {"upper": 1, "lower": 2, "pedals": 3}
ENUMERATION_ERROR = "hammond_standalone: Cannot enumerate MIDI input ports: "
INVALID_CHANNEL_ERROR = "hammond_standalone: Choose three distinct MIDI channels from 1 through 16."
REPLAY_ERROR = "hammond_standalone: Native input replay failed or was interrupted; inspect the copied diagnostics"

# Independently retained centers, not values computed by the application. The
# MIDI dialog is 740 x 520; the two windows exercise its translation and the
# separate header button. Pointer-down activates a modal control immediately.
POINTER_CASES = (
    (960, 700, {
        "header": (830, 66), "upper": (244, 348), "lower": (480, 348),
        "pedals": (716, 348), "apply": (264, 534),
        "disconnect": (500, 534), "close": (780, 130),
    }),
    (1280, 900, {
        "header": (1150, 66), "upper": (404, 448), "lower": (640, 448),
        "pedals": (876, 448), "apply": (424, 634),
        "disconnect": (660, 634), "close": (940, 230),
    }),
)


def unique_members(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON member: {key}")
        result[key] = value
    return result


def invalid_number(value: str) -> None:
    raise ValueError(f"Non-JSON numeric token: {value}")


class InputScript:
    """Only serializes explicit test actions; does not model modal behavior."""

    def __init__(self) -> None:
        self.events: list[tuple[int, str]] = []
        self.at = 80

    def key(self, name: str, modifier: str = "none", repeat: int = 0) -> InputScript:
        self.events += [(self.at, f"key_down {name} {modifier} {repeat}"),
                        (self.at + 4, f"key_up {name} {modifier}")]
        self.at += 18
        return self

    def tabs(self, count: int, modifier: str = "none") -> InputScript:
        for _ in range(count):
            self.key("Tab", modifier)
        return self

    def click(self, point: tuple[int, int]) -> InputScript:
        x, y = point
        self.events += [(self.at, f"mouse_down {x} {y}"),
                        (self.at + 4, f"mouse_up {x} {y}")]
        self.at += 18
        return self

    def note(self) -> InputScript:
        self.events += [(self.at, "key_down A none 0"),
                        (self.at + 100, "key_up A none")]
        self.at += 130
        return self

    def source(self) -> bytes:
        duration = max(600, self.at + 160)
        return (f"B3UIREPLAY1\nduration_ms {duration}\n" + "".join(
            f"{at} {event}\n" for at, event in self.events)).encode("ascii")


class NativeMidiAcceptance(unittest.TestCase):
    invocations = 0
    enumeration_failures = 0
    successful_replays = 0
    expected_failed_replays = 0

    @classmethod
    def setUpClass(cls) -> None:
        configured = os.environ.get("HAMMOND_STANDALONE_EXECUTABLE", "")
        if not configured:
            raise RuntimeError("HAMMOND_STANDALONE_EXECUTABLE is required; build the app first")
        cls.executable = Path(configured).resolve(strict=True)
        if not cls.executable.is_file() or not os.access(cls.executable, os.X_OK):
            raise RuntimeError(f"Native executable is not executable: {cls.executable}")
        print("MIDI CLI/modal executable SHA-256: " +
              hashlib.sha256(cls.executable.read_bytes()).hexdigest(), flush=True)

    @classmethod
    def tearDownClass(cls) -> None:
        print(f"Actual MIDI CLI/modal subprocesses: {cls.invocations}; "
              f"enumeration errors: {cls.enumeration_failures}; "
              f"successful UI replays: {cls.successful_replays}; "
              f"expected failed UI replays: {cls.expected_failed_replays}", flush=True)

    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="hammond-midi-cli-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.sequence = 0

    def directory(self) -> Path:
        self.sequence += 1
        result = self.root / f"case-{self.sequence}"
        result.mkdir()
        return result

    def execute(self, directory: Path, arguments: list[str], *, no_sdl: bool = False
                ) -> subprocess.CompletedProcess:
        driver = "hammond_no_such_sdl_driver" if no_sdl else "dummy"
        environment = dict(os.environ, SDL_VIDEODRIVER=driver, SDL_AUDIODRIVER=driver)
        self.__class__.invocations += 1
        try:
            return subprocess.run([str(self.executable), *arguments], cwd=directory,
                                  env=environment, stdin=subprocess.DEVNULL, capture_output=True,
                                  text=True, encoding="utf-8", errors="replace", timeout=TIMEOUT,
                                  check=False)
        except subprocess.TimeoutExpired as error:
            self.fail(f"Native MIDI case exceeded the finite process guard: {error}")

    def before_sdl(self, arguments: list[str], expected: int,
                   error: str = "") -> subprocess.CompletedProcess:
        directory = self.directory()
        files = {"controls.b3controls": b"state sentinel\x00\xff",
                 "diagnostics.json": b"diagnostics sentinel", "screen.bmp": b"image sentinel"}
        for name, contents in files.items():
            (directory / name).write_bytes(contents)
        process = self.execute(directory, ["--state", str(directory / "controls.b3controls"),
                                          "--diagnostics", str(directory / "diagnostics.json"),
                                          "--screenshot", str(directory / "screen.bmp"),
                                          *arguments], no_sdl=True)
        self.assertEqual(process.returncode, expected, process.stdout + "\n" + process.stderr)
        if error:
            self.assertEqual(process.stdout, "")
            self.assertEqual(process.stderr, f"hammond_standalone: {error}\n")
        self.assertEqual({path.name: path.read_bytes() for path in directory.iterdir()}, files)
        self.assertNotIn("Cannot initialize", process.stderr)
        return process

    def runtime(self, arguments: list[str], source: bytes | None = None
                ) -> tuple[subprocess.CompletedProcess, dict]:
        directory = self.directory()
        state, diagnostics = directory / "absent controls 音.b3controls", directory / "diagnostics.json"
        command = ["--state", str(state), "--diagnostics", str(diagnostics), *arguments]
        expected_files = {diagnostics.name}
        if source is not None:
            path = directory / "modal input Ω.b3ui"
            path.write_bytes(source)
            command += ["--input-script", str(path)]
            expected_files.add(path.name)
        try:
            process = self.execute(directory, command)
            self.assertTrue(diagnostics.is_file(), process.stdout + "\n" + process.stderr)
            data = json.loads(diagnostics.read_text(encoding="utf-8"),
                              object_pairs_hook=unique_members, parse_constant=invalid_number)
            self.assertEqual(data["schema_version"], 3)
            self.assertEqual(data["application"], "hammond_standalone")
            self.assertEqual(data["runtime"]["video_driver"], "dummy")
            self.assertGreater(data["runtime"]["rendered_images"], 0)
            audio, session, midi = data["audio"], data["session"], data["midi"]
            self.assertEqual(audio["driver"], "dummy")
            self.assertTrue(audio["open_before_shutdown"])
            self.assertTrue(audio["running_before_shutdown"])
            self.assertGreater(audio["callback_count"], 0)
            self.assertGreater(audio["rendered_frames"], 0)
            for key in ("render_failures", "format_failures", "overrange_failures", "nonfinite_failures"):
                self.assertEqual(audio[key], 0, key)
            self.assertTrue(session["snapshot_available"])
            self.assertFalse(session["running_after_shutdown"])
            self.assertFalse(session["held_after_shutdown"])
            self.assertEqual(session["fault_flags"], 0)
            self.assertFalse(midi["active_before_shutdown"])
            self.assertFalse(midi["active_after_shutdown"])
            self.assertTrue(midi["quiescent_after_shutdown"])
            self.assertTrue(midi["diagnostics_stable_after_shutdown"])
            self.assertFalse(midi["shutdown_failed"])
            self.assertEqual(midi["generation"], 0)
            self.assertEqual(midi["port_name"], "")
            self.assertNotEqual(midi["state_before_shutdown"], "open")
            self.assertNotEqual(midi["state_after_shutdown"], "open")
            self.assertEqual(midi["device"]["callback_messages"], 0)
            self.assertEqual(midi["device"]["forwarded_messages"], 0)
            self.assertEqual(midi["inbox"]["received_packets"], 0)
            self.assertEqual(midi["inbox"]["pending_packets"], 0)
            self.assertEqual(midi["decoder"]["packets"], 0)
            self.assertFalse(state.exists(), "MIDI settings must not save controls automatically")
            self.assertEqual({path.name for path in directory.iterdir()}, expected_files)
            if source is not None:
                self.assertEqual(path.read_bytes(), source)
            return process, data
        except Exception as error:
            raise AssertionError(f"Native MIDI runtime: {error}\n" + diagnostic_excerpt(diagnostics)) from error

    def modal(self, replay: InputScript, *, arguments: list[str] | None = None,
              invalid_applies: int = 0, openings: int = 1,
              notes: int = 0) -> dict:
        source = replay.source()
        process, data = self.runtime(arguments or [], source)
        try:
            midi, observed = data["midi"], data["replay"]
            enum_errors = process.stderr.count(ENUMERATION_ERROR)
            self.__class__.enumeration_failures += enum_errors
            self.assertLessEqual(enum_errors, openings)
            if not midi["backend_available"]:
                self.assertEqual(enum_errors, 0, "Unavailable builds must not enumerate a native backend")
                self.assertEqual(midi["backend"], "unavailable")
            else:
                self.assertIn(midi["backend"], ("ALSA", "WinMM", "CoreMIDI"))
            self.assertEqual(process.stderr.count(INVALID_CHANNEL_ERROR), invalid_applies)
            expected_errors = enum_errors + invalid_applies
            for key in ("completed", "delivered", "final_acknowledged"):
                self.assertTrue(observed[key], key + ": " + process.stderr)
            self.assertFalse(observed["observations_truncated"])
            self.assertEqual(observed["scheduled_events"], len(replay.events))
            self.assertEqual(observed["pushed_events"], len(replay.events))
            self.assertEqual(observed["accepted_note_on_commands"], notes)
            self.assertEqual(observed["accepted_note_off_commands"], notes)
            self.assertEqual(observed["before_shutdown"]["manual_notes"], [[], []])
            self.assertEqual(observed["before_shutdown"]["pedal_ids"], [])
            self.assertEqual(observed["device_starts"], 1)
            self.assertFalse(data["smoke"]["requested"])
            self.assertFalse(midi["startup_failed"])
            self.assertEqual(midi["requested_port"], "")
            self.assertEqual(midi["open_failures"], 0)
            self.assertEqual(midi["decoder"]["epochs"], 0)
            self.assertEqual(process.stdout, "")
            self.assertEqual(process.returncode, 1 if expected_errors else 0, process.stderr)
            self.assertEqual(observed["passed"], expected_errors == 0)
            if expected_errors:
                self.__class__.expected_failed_replays += 1
                self.assertEqual(data["errors"]["count"], expected_errors + 1)
                self.assertEqual(data["errors"]["last"], REPLAY_ERROR.removeprefix("hammond_standalone: "))
                self.assertEqual(process.stderr.count(REPLAY_ERROR), 1)
            else:
                self.__class__.successful_replays += 1
                self.assertEqual(data["errors"], {"count": 0, "last": ""})
            return data
        except Exception as error:
            raise AssertionError(f"Native MIDI modal: {error}\n" + diagnostic_excerpt(data)) from error

    def test_cli_numeric_channels_are_strict_and_bounded(self) -> None:
        lexical = ("-1", "+1", " 1", "1 ", "1.0", "1e0", "0x1", "NaN", "inf",
                   "1x", "2147483648", "999999999999999999999999999")
        for option in CHANNEL_OPTIONS:
            for value in lexical:
                with self.subTest(option=option, value=value):
                    self.before_sdl(["--help", option, value], 2, f"Invalid integer for {option}")
            for value in ("0", "17", "256"):
                with self.subTest(option=option, value=value):
                    self.before_sdl(["--help", option, value], 2,
                                    f"Unsupported value for {option}; see --help")
            for suffix in ([], [""]):
                with self.subTest(option=option, suffix=suffix):
                    self.before_sdl(["--help", option, *suffix], 2, f"Missing value for {option}")

    def test_cli_distinct_channels_and_all_boundary_positions(self) -> None:
        for option, value in ((CHANNEL_OPTIONS[0], "2"), (CHANNEL_OPTIONS[0], "3"),
                              (CHANNEL_OPTIONS[1], "1"), (CHANNEL_OPTIONS[1], "3"),
                              (CHANNEL_OPTIONS[2], "1"), (CHANNEL_OPTIONS[2], "2")):
            with self.subTest(option=option, value=value):
                self.before_sdl(["--help", option, value], 2,
                                "MIDI upper, lower, and pedal channels must be distinct values from 1 through 16")
        for channels in (("1", "2", "16"), ("16", "1", "2"), ("2", "16", "1"),
                         ("00016", "00001", "00002")):
            with self.subTest(channels=channels):
                arguments = [piece for pair in zip(CHANNEL_OPTIONS, channels) for piece in pair]
                process = self.before_sdl(["--help", *arguments], 0)
                self.assertIn("Ctrl+M opens MIDI", process.stdout)
                self.assertEqual(process.stderr, "")

    def test_cli_repeated_options_and_conflicting_lists(self) -> None:
        for option in ("--list-midi", *CHANNEL_OPTIONS, "--midi-port"):
            with self.subTest(option=option):
                value = [] if option == "--list-midi" else ["1" if "channel" in option else "unused name"]
                self.before_sdl(["--help", option, *value, option, *value], 2,
                                f"Repeated option: {option}")
        self.before_sdl(["--list-midi", "--list-audio"], 2,
                        "--list-audio and --list-midi are mutually exclusive")
        self.before_sdl(["--list-audio", "--list-midi"], 2,
                        "--list-audio and --list-midi are mutually exclusive")

    def test_cli_exact_port_argument_bytes_and_no_name_coercion(self) -> None:
        # Help validates syntax without trying any of these names. A numeric
        # string is an exact name, not an input-port index; spaces are retained.
        for name in ("0", "1", " ", " exact name Ω ", "--help", "x" * 1024, "Ω" * 512):
            with self.subTest(name=name[:40], bytes=len(name.encode("utf-8"))):
                process = self.before_sdl(["--midi-port", name, "--help"], 0)
                self.assertIn("--midi-port NAME", process.stdout)
                self.assertEqual(process.stderr, "")
        for name in ("x" * 1025, "Ω" * 513):
            with self.subTest(bytes=len(name.encode("utf-8"))):
                self.before_sdl(["--help", "--midi-port", name], 2, "Invalid exact MIDI input name")
        self.before_sdl(["--help", "--midi-port"], 2, "Missing value for --midi-port")
        self.before_sdl(["--help", "--midi-port", ""], 2, "Missing value for --midi-port")
        self.before_sdl(["--midi-port=unused", "--help"], 2, "Unknown option: --midi-port=unused")

    def test_cli_list_midi_precedes_sdl_initialization(self) -> None:
        directory = self.directory()
        process = self.execute(directory, ["--list-midi"], no_sdl=True)
        self.assertIn(process.returncode, (0, 1), process.stdout + process.stderr)
        self.assertTrue(process.stdout.startswith("MIDI backend: "), process.stdout)
        backend = process.stdout.splitlines()[0].removeprefix("MIDI backend: ")
        self.assertIn(backend, ("unavailable", "ALSA", "WinMM", "CoreMIDI"))
        self.assertNotIn("Cannot initialize", process.stderr)
        self.assertNotIn("hammond_no_such_sdl_driver", process.stderr)
        self.assertEqual(list(directory.iterdir()), [])
        if process.returncode == 0:
            self.assertNotEqual(backend, "unavailable")
            self.assertIn("Default input: none; select an exact name with --midi-port or MIDI settings\n",
                          process.stdout)
            self.assertTrue("No MIDI input ports found.\n" in process.stdout or "\n1: " in process.stdout)
        else:
            self.assertIn("hammond_standalone: ", process.stderr)
            self.assertIn("MIDI", process.stderr)
            self.assertNotIn("Default input:", process.stdout)
            if backend == "unavailable":
                self.assertIn("MIDI backend is unavailable in this build", process.stderr)

    def test_cli_startup_defaults_to_no_input_with_custom_routing(self) -> None:
        for arguments, channels in (([], DEFAULT_CHANNELS),
                                    (["--midi-upper-channel", "16", "--midi-lower-channel", "1",
                                      "--midi-pedal-channel", "2"], {"upper": 16, "lower": 1, "pedals": 2})):
            with self.subTest(channels=channels):
                process, data = self.runtime(["--smoke-ms", "600", *arguments])
                self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
                self.assertEqual(process.stderr, "")
                self.assertTrue(data["smoke"]["passed"])
                self.assertEqual(data["errors"], {"count": 0, "last": ""})
                midi = data["midi"]
                self.assertEqual(midi["requested_port"], "")
                self.assertEqual(midi["open_failures"], 0)
                self.assertEqual(midi["decoder"]["epochs"], 0)
                self.assertEqual(midi["channels"], channels)
                expected_state = "closed" if midi["backend_available"] else "unavailable"
                self.assertEqual(midi["state_before_shutdown"], expected_state)
                self.assertEqual(midi["state_after_shutdown"], expected_state)
                self.assertEqual(midi["status"], "No MIDI input selected." if midi["backend_available"]
                                 else "MIDI backend unavailable in this build.")

    def test_cli_nonexistent_exact_name_fails_finitely_and_preserves_name(self) -> None:
        # Never use a name obtained from enumeration. The nonce and surrounding
        # spaces make this an explicitly nonexistent exact-name negative case.
        name = f" __hammond_acceptance_missing_{uuid.uuid4().hex}_Ω__ "
        process, data = self.runtime(["--smoke-ms", "600", "--midi-port", name])
        self.assertEqual(process.returncode, 1, process.stdout + process.stderr)
        midi = data["midi"]
        self.assertEqual(midi["requested_port"], name)
        self.assertEqual(midi["channels"], DEFAULT_CHANNELS)
        self.assertTrue(midi["startup_failed"])
        self.assertFalse(data["smoke"]["passed"])
        self.assertTrue(data["smoke"]["completed"])
        self.assertIn("Native smoke failed", process.stderr)
        if midi["backend_available"]:
            self.assertIn("Cannot open MIDI input:", process.stderr)
            self.assertEqual(midi["open_failures"], 1)
        else:
            self.assertIn("MIDI backend unavailable in this build.", process.stderr)
            self.assertEqual(midi["open_failures"], 0)

    def test_modal_ctrl_and_command_m_open_then_escape_restores_playing(self) -> None:
        for modifier in ("ctrl", "meta"):
            with self.subTest(modifier=modifier):
                replay = InputScript().key("M", modifier).note().key("Escape").note()
                data = self.modal(replay, notes=1)
                self.assertEqual(data["midi"]["channels"], DEFAULT_CHANNELS)
                status = data["midi"]["status"]
                if not data["midi"]["backend_available"]:
                    self.assertEqual(status, "MIDI backend unavailable in this build.")
                elif data["errors"]["count"]:
                    self.assertTrue(status.startswith("Cannot enumerate MIDI input ports: "), status)
                else:
                    self.assertIn(status, ("No MIDI input ports were found.", "No MIDI input selected."))

    def test_modal_pointer_open_apply_disconnect_close_at_two_sizes(self) -> None:
        for width, height, points in POINTER_CASES:
            with self.subTest(width=width, height=height):
                replay = InputScript().click(points["header"]).note()
                for control in ("upper", "lower", "pedals", "apply", "disconnect", "close"):
                    replay.click(points[control])
                replay.note()
                data = self.modal(replay, arguments=["--width", str(width), "--height", str(height)], notes=1)
                self.assertEqual(data["midi"]["channels"], {"upper": 2, "lower": 3, "pedals": 4})
                self.assertEqual(data["midi"]["status"], "No MIDI input selected.")

    def test_modal_all_eight_keyboard_controls_and_no_port_auto_open(self) -> None:
        replay = InputScript().key("M", "ctrl")
        replay.key("Return").key("Home")  # Previous port, then explicit No input.
        replay.tabs(1).key("Space").key("Home")  # Next port, then No input.
        replay.tabs(1).key("End")  # Upper = 16.
        replay.tabs(1).key("Home")  # Lower = 1.
        replay.tabs(1).key("End").key("Down")  # Pedals = 15.
        replay.tabs(1).key("Return")  # Apply, still on No input.
        replay.tabs(1).key("Space")  # Disconnect.
        replay.tabs(1).key("Return").note()  # Close, then ordinary playing.
        data = self.modal(replay, notes=1)
        self.assertEqual(data["midi"]["channels"], {"upper": 16, "lower": 1, "pedals": 15})
        self.assertEqual(data["midi"]["status"], "No MIDI input selected.")

    def test_modal_focus_wraps_forward_and_reverse_across_eight_controls(self) -> None:
        replay = InputScript().key("M", "ctrl").tabs(8).tabs(2).key("End")
        replay.tabs(3).key("Return").key("Escape")
        replay.key("M", "ctrl").tabs(1, "shift").key("Return").note()
        data = self.modal(replay, openings=2, notes=1)
        self.assertEqual(data["midi"]["channels"], {"upper": 16, "lower": 2, "pedals": 3})

    def test_modal_channels_wrap_and_home_end_apply_without_connecting(self) -> None:
        replay = InputScript().key("M", "ctrl").tabs(2)
        replay.key("End").key("Right").key("Left")  # 16 -> 1 -> 16.
        replay.tabs(1).key("Home").key("Left").key("Right")  # 1 -> 16 -> 1.
        replay.tabs(1).key("End").key("Up").key("Up")  # 16 -> 1 -> 2.
        replay.tabs(1).key("Space")
        data = self.modal(replay)
        self.assertEqual(data["midi"]["channels"], {"upper": 16, "lower": 1, "pedals": 2})
        self.assertEqual(data["midi"]["status"], "No MIDI input selected.")

    def test_modal_invalid_apply_preserves_active_routing_and_edit_intent(self) -> None:
        arguments = ["--midi-upper-channel", "4", "--midi-lower-channel", "5",
                     "--midi-pedal-channel", "6"]
        for correct in (False, True):
            with self.subTest(correct_without_reopening=correct):
                replay = InputScript().key("M", "ctrl").tabs(2).key("Home")
                replay.tabs(1).key("Home").tabs(1).key("End").tabs(1).key("Return")
                if correct:
                    # Preserve selected Upper=1 and Pedals=16 across rejection;
                    # change only Lower=1 to 2, then retry the same Apply control.
                    replay.tabs(2, "shift").key("Right").tabs(2).key("Return")
                data = self.modal(replay, arguments=arguments, invalid_applies=1)
                expected = {"upper": 1, "lower": 2, "pedals": 16} if correct else {
                    "upper": 4, "lower": 5, "pedals": 6}
                self.assertEqual(data["midi"]["channels"], expected)
                self.assertEqual(data["midi"]["status"], "No MIDI input selected." if correct else
                                 "Choose three distinct MIDI channels from 1 through 16.")

    def test_modal_escape_discards_unapplied_channels(self) -> None:
        replay = InputScript().key("M", "ctrl").tabs(2).key("End").key("Escape")
        replay.key("M", "ctrl").tabs(5).key("Return").key("Escape").note()
        data = self.modal(replay, openings=2, notes=1)
        self.assertEqual(data["midi"]["channels"], DEFAULT_CHANNELS)

    def test_modal_shortcut_and_navigation_ignore_repeat_and_alt(self) -> None:
        replay = InputScript().key("M", "ctrl", repeat=1).key("M", "ctrl+alt").note()
        replay.key("M", "ctrl").key("Tab", repeat=1).key("Tab", "ctrl").key("Tab", "alt")
        replay.tabs(2).key("End").key("Right", "alt").key("Right", repeat=1)
        replay.tabs(3).key("Return").key("Escape")
        data = self.modal(replay, notes=1)
        self.assertEqual(data["midi"]["channels"], {"upper": 16, "lower": 2, "pedals": 3})


if __name__ == "__main__":
    unittest.main(verbosity=2)
