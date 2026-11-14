#!/usr/bin/env python3
"""Independent workspace acceptance through the actual standalone executable.

Requires HAMMOND_STANDALONE_EXECUTABLE. Every process selects SDL dummy audio
and video, private input/output paths, and the existing nine-second deadline.
Test-only schema/lifecycle helpers are reused; no production layout, UiModel,
Session, serializer, or decoder supplies the expected controls or coordinates.

Optional HAMMOND_STANDALONE_WORKSPACE_EVIDENCE retains exact scripts, copied
diagnostics and compact process/hash records. BMPs stay temporary: the native
gallery owns retained visual captures. Dummy SDL's immediate CaptureLost is a
failure-path check, not evidence of persistent physical mouse capture.
"""

from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import time
import unittest

import test_standalone_app as app_fixture
import test_standalone_midi_replay as midi_fixture
import test_standalone_workflows as workflow_fixture


PROCESS_TIMEOUT = 9.0
EMPTY = ((), (), ())
STATE = workflow_fixture.FIXED_STATE
CONTROLS = workflow_fixture.FIXED_CONTROLS
NONCANONICAL_STATE = b"\t" + STATE.replace(b"\n", b"\r\n") + b" \t\r\n"

# Independent literal interior points in the reviewed header design. The seven
# cases include both sides of the cabinet and cheek breakpoints. No executable
# geometry or diagnostic coordinate is used to discover the point to click.
# size: (Play, Rotary, Service, Flat, Save)
HEADER_POINTS = {
    (960, 700): ((52, 66), (130, 66), (208, 66), (674, 80), (752, 40)),
    (1280, 900): ((52, 66), (130, 66), (208, 66), (994, 80), (1072, 40)),
    (1672, 941): ((128, 67), (248, 67), (368, 67), (1267, 88), (1359, 40)),
    (1399, 819): ((52, 66), (130, 66), (208, 66), (1113, 80), (1191, 40)),
    (1400, 819): ((116, 67), (236, 67), (356, 67), (1007, 80), (1099, 40)),
    (1399, 820): ((52, 66), (130, 66), (208, 66), (1113, 80), (1191, 40)),
    (1400, 820): ((116, 67), (236, 67), (356, 67), (1007, 88), (1099, 40)),
}

# Valid Play control/key locations at 1280x900: both drawbar racks, both cheek
# edit controls, two presets, upper/lower playing keys, pedal 1, expression,
# percussion, keyboard target Pedals and octave-up. Their hidden activation
# must neither alter sound controls nor redirect a later physical piano key.
HIDDEN_PLAY_POINTS = (
    (60, 350), (690, 350), (58, 508), (58, 654), (35, 590), (154, 700),
    (222, 580), (625, 720), (60, 815), (720, 155), (100, 155),
    (243, 452), (415, 452),
)


def tap(at: int, key: str, modifiers: str = "none") -> list[tuple[int, str]]:
    return [(at, f"key_down {key} {modifiers} 0"), (at + 10, f"key_up {key} {modifiers}")]


def click(at: int, point: tuple[int, int]) -> list[tuple[int, str]]:
    x, y = point
    return [(at, f"mouse_down {x} {y}"), (at + 20, f"mouse_up {x} {y}")]


def script(magic: str, duration: int, events: list[tuple[int, str]]) -> bytes:
    # Do not sort: an accidentally out-of-order fixture must fail admission.
    return (f"{magic}\nduration_ms {duration}\n" + "".join(
        f"{at} {event}\n" for at, event in events)).encode("ascii")


def holds(snapshot: dict) -> tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
    return tuple(snapshot["manual_notes"][0]), tuple(snapshot["manual_notes"][1]), tuple(snapshot["pedal_ids"])


def unique(values: list) -> list:
    return [value for index, value in enumerate(values) if index == 0 or value != values[index - 1]]


class NativeWorkspaceReplayAcceptance(unittest.TestCase):
    invocations = 0

    @classmethod
    def setUpClass(cls) -> None:
        configured = os.environ.get("HAMMOND_STANDALONE_EXECUTABLE", "")
        if not configured:
            raise RuntimeError("HAMMOND_STANDALONE_EXECUTABLE is required; build hammond_standalone first")
        cls.executable = Path(configured).resolve(strict=True)
        if not cls.executable.is_file() or not os.access(cls.executable, os.X_OK):
            raise RuntimeError(f"Native executable is not executable: {cls.executable}")
        cls.binary_hash = hashlib.sha256(cls.executable.read_bytes()).hexdigest()
        print(f"Native workspace executable SHA-256: {cls.binary_hash}", flush=True)
        evidence = os.environ.get("HAMMOND_STANDALONE_WORKSPACE_EVIDENCE", "")
        cls.evidence = Path(evidence).resolve() if evidence else None
        if cls.evidence is not None:
            cls.evidence.mkdir(parents=True, exist_ok=True)

    @classmethod
    def tearDownClass(cls) -> None:
        print(f"Actual native workspace subprocesses: {cls.invocations}", flush=True)
        if hashlib.sha256(cls.executable.read_bytes()).hexdigest() != cls.binary_hash:
            raise AssertionError("The native executable changed during workspace acceptance")

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="hammond-native-workspaces-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.sequence = 0

    @contextmanager
    def run_native(self, duration: int, events: list[tuple[int, str]], *,
                   size: tuple[int, int] = (1280, 900), final_size: tuple[int, int] | None = None,
                   flat: bool = False, state: bytes = STATE, screenshot: bool = False,
                   midi_events: list[tuple[int, str]] | None = None):
        self.sequence += 1
        directory = self.root / f"run-{self.sequence}"
        directory.mkdir()
        state_path = directory / "private controls.b3controls"
        script_path = directory / "workspace input.b3ui"
        midi_path = directory / "MIDI input.b3midi"
        report_path = directory / "diagnostics.json"
        bmp_path = directory / "painted-frame.bmp"
        source = script("B3UIREPLAY1", duration, events)
        state_path.write_bytes(state)
        script_path.write_bytes(source)
        command = [str(self.executable), "--state", str(state_path),
                   "--input-script", str(script_path), "--diagnostics", str(report_path),
                   "--width", str(size[0]), "--height", str(size[1])]
        expected_files = {state_path.name, script_path.name, report_path.name}
        midi_source = None
        if midi_events is not None:
            midi_source = script("B3MIDIREPLAY1", duration, midi_events)
            midi_path.write_bytes(midi_source)
            command += ["--midi-script", str(midi_path)]
            expected_files.add(midi_path.name)
        if flat:
            command += ["--flat"]
        if screenshot:
            command += ["--screenshot", str(bmp_path)]
            expected_files.add(bmp_path.name)
        environment = dict(os.environ, SDL_AUDIODRIVER="dummy", SDL_VIDEODRIVER="dummy")
        self.__class__.invocations += 1
        started = time.monotonic()
        process = None
        data = None
        elapsed = 0.0
        capture = None
        try:
            process = subprocess.run(command, cwd=directory, env=environment,
                                     stdin=subprocess.DEVNULL, capture_output=True, text=True,
                                     errors="replace", timeout=PROCESS_TIMEOUT, check=False)
            elapsed = time.monotonic() - started
            self.assertEqual(process.returncode, 0)
            self.assertEqual((process.stdout, process.stderr), ("", ""))
            self.assertGreaterEqual(elapsed, duration / 1000 - 0.04)
            self.assertTrue(report_path.is_file())
            data = json.loads(report_path.read_text(encoding="utf-8"),
                              object_pairs_hook=app_fixture.unique_object,
                              parse_constant=app_fixture.reject_nonfinite)
            schema = dict(app_fixture.SCHEMA)
            schema["replay"] = midi_fixture.replay_schema(data["replay"], midi_fixture.UI_REPLAY_SCHEMA)
            if midi_events is None:
                app_fixture.assert_schema(self, data, schema)
                workflow_fixture.NativeWorkflowAcceptance.assert_common(
                    self, data, source.decode("ascii"), state_path, final_size or size)
            else:
                # Reuse the strict transport/lifecycle checker, with this
                # fixture's independent notes, controls and view expectations.
                midi_fixture.NativeMidiReplayAcceptance.assert_common(
                    self, data, duration, midi_events, events, state_path, successful=True)
            app_fixture.assert_presentation(self, data)
            self.assertFalse(data["presentation"]["observations_truncated"])
            self.assertEqual(data["presentation"]["initial_workspace"], "play")
            self.assertEqual(data["presentation"]["initial_presentation"], "flat" if flat else "dimensional")
            self.assertEqual(data["runtime"]["renderer"], "software")
            self.assertEqual(data["replay"]["device_starts"], 1)
            for field in ("passed", "final_acknowledged", "snapshot_available_before_shutdown",
                          "session_running_before_shutdown"):
                self.assertTrue(data["replay"][field], field)
            for field in ("controls_pending_before_shutdown", "save_pending_before_shutdown"):
                self.assertFalse(data["replay"][field], field)
            self.assertEqual(data["replay"]["desired_controls_before_shutdown"], data["controls"])
            self.assertEqual(script_path.read_bytes(), source)
            if midi_source is not None:
                self.assertEqual(midi_path.read_bytes(), midi_source)
            self.assertEqual({path.name for path in directory.iterdir()}, expected_files)
            self.assertEqual(data["runtime"]["screenshot_written"], screenshot)
            if screenshot:
                bmp = bmp_path.read_bytes()
                self.assertGreater(len(bmp), 54)
                self.assertEqual(bmp[:2], b"BM")
                width, height = struct.unpack_from("<ii", bmp, 18)
                self.assertEqual((width, abs(height)), final_size or size)
                self.assertEqual(data["presentation"]["screenshot"], data["presentation"]["before_shutdown"])
                capture = {"sha256": hashlib.sha256(bmp).hexdigest(), "bytes": len(bmp),
                           "width": width, "height": abs(height)}
            yield workflow_fixture.WorkflowRun(data, state_path.read_bytes(), elapsed)
        except Exception as error:
            diagnostic = workflow_fixture.diagnostic_excerpt(data if data is not None else report_path)
            output = "" if process is None else process.stdout + "\n" + process.stderr
            raise AssertionError(
                f"{self._testMethodName}: {type(error).__name__}: {error}\n"
                f"Command: {command!r}\nElapsed: {elapsed:.3f}s\n{output}\n"
                f"UI input:\n{source.decode('ascii')}"
                + (f"MIDI input:\n{midi_source.decode('ascii')}" if midi_source is not None else "")
                + diagnostic
            ) from error
        finally:
            if self.evidence is not None:
                destination = self.evidence / f"{self._testMethodName}-{self.sequence}"
                destination.mkdir()
                for path in (script_path, midi_path, state_path, report_path):
                    if path.is_file():
                        shutil.copyfile(path, destination / path.name)
                (destination / "process.json").write_text(json.dumps({
                    "command": command, "elapsed_seconds": elapsed,
                    "executable_sha256": self.binary_hash,
                    "environment": {"SDL_AUDIODRIVER": "dummy", "SDL_VIDEODRIVER": "dummy"},
                    "returncode": process.returncode if process is not None else None,
                    "stdout": process.stdout if process is not None else None,
                    "stderr": process.stderr if process is not None else None,
                    "input_state_sha256": hashlib.sha256(state).hexdigest(),
                    "screenshot": capture,
                }, indent=2) + "\n", encoding="utf-8")

    def assert_control_path(self, run: workflow_fixture.WorkflowRun, expected: list[dict]) -> None:
        observed = run.diagnostics["replay"]
        self.assertEqual(unique([item["controls"] for item in observed["observations"]]), expected)
        self.assertEqual(observed["before_shutdown"]["controls"], expected[-1])
        self.assertEqual(observed["desired_controls_before_shutdown"], expected[-1])
        self.assertEqual(run.diagnostics["controls"], expected[-1])

    def assert_hold_path(self, run: workflow_fixture.WorkflowRun, expected: list[tuple]) -> None:
        observed = run.diagnostics["replay"]
        self.assertEqual(unique([holds(item) for item in observed["observations"]]), expected)
        self.assertEqual(holds(observed["before_shutdown"]), expected[-1],
                         "Joined shutdown must not substitute for the scripted release")

    def assert_commands(self, run: workflow_fixture.WorkflowRun, *, on: int, off: int,
                        control_changes: int = 0, startup_sequence: int | None = None) -> None:
        observed = run.diagnostics["replay"]
        self.assertEqual(observed["accepted_note_on_commands"], on)
        self.assertEqual(observed["accepted_note_off_commands"], off)
        if startup_sequence is None:
            initial = observed["observations"][0]
            self.assertLess(initial["elapsed_ms"], 180, "A pre-action loaded-state observation is required")
            startup_sequence = initial["last_applied_sequence"]
            self.assertEqual(initial["last_submitted_sequence"], startup_sequence)
        else:
            # A separately completed prefix supplies the acknowledged origin.
            # The full journey can first sample that applied state while its
            # first note is already submitted; submission is not application.
            self.assertGreater(startup_sequence, 0)
            for item in observed["observations"]:
                self.assertGreaterEqual(item["last_applied_sequence"], startup_sequence)
                self.assertEqual(item["resolved_sequence"], item["last_applied_sequence"])
                self.assertGreaterEqual(item["last_submitted_sequence"], item["last_applied_sequence"])
                self.assertLessEqual(item["last_submitted_sequence"], observed["last_submitted_sequence"])
        final = observed["last_submitted_sequence"]
        self.assertEqual(final - startup_sequence, on + off + control_changes,
                         "Navigation must not inject a sound command or release")
        self.assertEqual(observed["before_shutdown"]["last_applied_sequence"], final)
        self.assertEqual(observed["before_shutdown"]["resolved_sequence"], final)

    def assert_views(self, run: workflow_fixture.WorkflowRun, expected: list[tuple]) -> None:
        presentation = run.diagnostics["presentation"]
        frames = [*presentation["observations"], presentation["last_painted"]]
        actual = unique([(item["workspace"], item["presentation"],
                          item["window_width"], item["window_height"], item["overlay"])
                         for item in frames])
        self.assertEqual(actual, [(*item, "none") for item in expected])
        clocks = [item["inspection"]["frame_clock"] for item in frames
                  if item["inspection"]["snapshot_available"]]
        self.assertEqual(clocks, sorted(clocks), "View changes must not restart the Session clock")
        self.assertGreater(clocks[-1], clocks[0])
        self.assertTrue(any(item["inspection"]["snapshot_state"] == "current" for item in frames))
        self.assertIn(frames[-1]["inspection"]["snapshot_state"], ("current", "retained"))

    def test_pointer_header_matrix_preserves_keyboard_space_and_exact_save(self) -> None:
        for size, (play, rotary, service, flat, save) in HEADER_POINTS.items():
            with self.subTest(size=size):
                # Two reverse tabs focus Lower C4 without creating a pointer
                # owner. Keyboard A and Space then hold distinct original parts.
                events = tap(50, "Tab", "shift") + tap(80, "Tab", "shift")
                events += [(180, "key_down A none 0"), (320, "key_down Space none 0")]
                events += click(500, rotary) + click(700, flat) + click(900, service)
                events += tap(1050, "F3") + tap(1100, "RightBracket")
                events += click(1250, play) + click(1450, flat)
                events += [(1600, "key_up Space ctrl+meta"), (1800, "key_up A alt+shift")]
                events += click(1950, save)
                with self.run_native(2250, events, size=size, state=NONCANONICAL_STATE,
                                     screenshot=True) as run:
                    self.assert_control_path(run, [CONTROLS])
                    self.assert_hold_path(run, [EMPTY, ((60,), (), ()), ((60,), (60,), ()),
                                               ((60,), (), ()), EMPTY])
                    self.assert_commands(run, on=2, off=2)
                    self.assert_views(run, [(workspace, mode, *size) for workspace, mode in (
                        ("play", "dimensional"), ("rotary", "dimensional"), ("rotary", "flat"),
                        ("service", "flat"), ("play", "flat"), ("play", "dimensional"))])
                    self.assertEqual(run.saved_bytes, STATE,
                                     "Header Save must emit the same canonical sound-only bytes at every view size")
                    self.assertFalse(run.diagnostics["runtime"]["screenshot_while_held"])

    def test_hidden_play_regions_cannot_edit_redirect_or_audition(self) -> None:
        play, rotary, service, _, _ = HEADER_POINTS[(1280, 900)]
        for workspace, target in (("rotary", rotary), ("service", service)):
            for flat in (False, True):
                with self.subTest(workspace=workspace, flat=flat):
                    events = tap(50, "Tab", "shift") + tap(80, "Tab", "shift")
                    events += [(180, "key_down A none 0")] + click(350, target)
                    for index, point in enumerate(HIDDEN_PLAY_POINTS):
                        events += click(500 + 45 * index, point)
                    events += tap(1120, "Space") + tap(1190, "Home") + tap(1260, "End")
                    events += tap(1330, "Left") + tap(1400, "Right")
                    events += [(1490, "key_down S none 0")] + click(1680, play)
                    events += [(1860, "key_down Space none 0"), (2050, "key_up A none"),
                               (2220, "key_up S none"), (2390, "key_up Space alt+meta")]
                    with self.run_native(2600, events, flat=flat) as run:
                        self.assert_control_path(run, [CONTROLS])
                        self.assert_hold_path(run, [EMPTY, ((60,), (), ()), ((60, 62), (), ()),
                                                   ((60, 62), (60,), ()), ((62,), (60,), ()),
                                                   ((), (60,), ()), EMPTY])
                        self.assert_commands(run, on=3, off=3)
                        mode = "flat" if flat else "dimensional"
                        self.assert_views(run, [(name, mode, 1280, 900) for name in ("play", workspace, "play")])
                        self.assertEqual(run.saved_bytes, STATE)

    def test_focus_memory_restores_drawbar_save_and_load_after_returns(self) -> None:
        events = [event for index in range(25) for event in tap(20 + 20 * index, "Tab")]
        events += tap(550, "Home") + click(750, (130, 66))
        # Rotary remembers Save; Service remembers Load. Visiting their tabs
        # must not replace the remembered first Upper-B drawbar in Play.
        events += tap(900, "Tab") + tap(930, "Tab") + click(1100, (208, 66))
        events += tap(1220, "Tab") + tap(1250, "Tab") + click(1450, (52, 66))
        events += tap(1650, "Right") + click(1830, (994, 80)) + tap(2000, "Right")
        events += [(2170, "resize 960 700")] + tap(2350, "Right")
        events += click(2570, (130, 66)) + tap(2750, "Space")
        events += click(2920, (52, 66)) + tap(3090, "Right")
        events += click(3270, (208, 66)) + tap(3450, "Space")
        expected = []
        for value in (8, 0, 1, 2, 3, 4, 3):
            controls = deepcopy(CONTROLS)
            controls["manual_drawbars"][0][1][0] = value
            expected.append(controls)
        with self.run_native(3750, events, final_size=(960, 700)) as run:
            self.assert_control_path(run, expected)
            self.assert_hold_path(run, [EMPTY])
            self.assert_commands(run, on=0, off=0, control_changes=6)
            self.assert_views(run, [
                ("play", "dimensional", 1280, 900), ("rotary", "dimensional", 1280, 900),
                ("service", "dimensional", 1280, 900), ("play", "dimensional", 1280, 900),
                ("play", "flat", 1280, 900), ("play", "flat", 960, 700),
                ("rotary", "flat", 960, 700), ("play", "flat", 960, 700),
                ("service", "flat", 960, 700),
            ])
            self.assertEqual(run.saved_bytes, STATE.replace(b"bank B 8 7 6 5 4 3 2 1 0\n",
                                                            b"bank B 3 7 6 5 4 3 2 1 0\n", 1))

    def test_capture_failure_closes_parameter_gesture_before_view_and_resize(self) -> None:
        events = [(180, "key_down A none 0"), (300, "mouse_down 60 284")]
        events += tap(450, "F7") + [(550, "mouse_move 60 388")]
        events += tap(650, "F6") + [(750, "mouse_move 625 580")]
        events += tap(850, "F4") + [(1050, "resize 960 700"), (1150, "mouse_move 230 470"),
                                    (1250, "mouse_up -80 -80")]
        events += click(1450, (48, 338)) + [(1680, "key_up A alt+meta")]
        zero = deepcopy(CONTROLS)
        zero["manual_drawbars"][0][1][0] = 0
        with self.run_native(1900, events, final_size=(960, 700)) as run:
            self.assert_control_path(run, [CONTROLS, zero, CONTROLS])
            self.assert_hold_path(run, [EMPTY, ((60,), (), ()), EMPTY])
            self.assert_commands(run, on=1, off=1, control_changes=2)
            self.assert_views(run, [
                ("play", "dimensional", 1280, 900), ("play", "flat", 1280, 900),
                ("service", "flat", 1280, 900), ("play", "flat", 1280, 900),
                ("play", "flat", 960, 700),
            ])
            self.assertEqual(run.saved_bytes, STATE)

    def test_pointer_capture_failure_preserves_keyboard_owner_during_navigation(self) -> None:
        events = [(180, "key_down A none 0"), (450, "mouse_down 222 580")]
        events += tap(650, "F6") + tap(850, "F7") + [(1050, "mouse_move 625 580")]
        events += tap(1250, "F4") + [(1450, "resize 960 700"), (1650, "mouse_move 230 470"),
                                    (1850, "mouse_up -80 -80"), (2050, "key_up A alt+shift")]
        with self.run_native(2250, events, final_size=(960, 700)) as run:
            self.assert_control_path(run, [CONTROLS])
            observed = unique([holds(item) for item in run.diagnostics["replay"]["observations"]])
            # Pointer On/Off may share one audio callback; both legal published
            # paths keep keyboard C4 until its explicit original release.
            self.assertIn(observed, [
                [EMPTY, ((60,), (), ()), EMPTY],
                [EMPTY, ((60,), (), ()), ((36, 60), (), ()), ((60,), (), ()), EMPTY],
            ])
            self.assert_hold_path(run, observed)
            self.assert_commands(run, on=2, off=2)
            self.assertGreaterEqual(next(item["elapsed_ms"] for item in reversed(
                run.diagnostics["replay"]["observations"]) if holds(item) == EMPTY), 2050)
            self.assert_views(run, [
                ("play", "dimensional", 1280, 900), ("service", "dimensional", 1280, 900),
                ("service", "flat", 1280, 900), ("play", "flat", 1280, 900),
                ("play", "flat", 960, 700),
            ])
            self.assertEqual(run.saved_bytes, STATE)

    def test_synthetic_midi_and_ui_owners_survive_pointer_navigation_and_resize(self) -> None:
        events = tap(50, "Tab", "shift") + tap(80, "Tab", "shift")
        events += [(180, "key_down A none 0"), (330, "key_down Space none 0")]
        events += click(1100, (130, 66)) + click(1300, (994, 80)) + click(1500, (208, 66))
        events += [(1700, "resize 960 700"), (1900, "key_up Space ctrl+meta"),
                   (2100, "key_up A alt+shift")]
        events += click(2950, (52, 66))
        midi_events = [(50, "connect"), (450, "bytes 90 3C 64"), (650, "bytes 91 40 64"),
                       (850, "bytes 92 3C 64"), (2350, "bytes 80 3C 00"),
                       (2550, "bytes 81 40 00"), (2750, "bytes 82 3C 00")]
        # Finish the original nonmusical startup prefix before measuring its
        # sequence origin. The replay minimum is 250 ms; retain only actions
        # before the unchanged first note at 180 ms. A sampled elapsed time
        # cannot prove that no later command has already been submitted.
        prefix_ui = [event for event in events if event[0] < 180]
        prefix_midi = [event for event in midi_events if event[0] < 180]
        with self.run_native(250, prefix_ui, midi_events=prefix_midi) as prefix:
            self.assert_control_path(prefix, [CONTROLS])
            self.assert_hold_path(prefix, [EMPTY])
            observed = prefix.diagnostics["replay"]
            self.assertEqual(observed["accepted_note_on_commands"], 0)
            self.assertEqual(observed["accepted_note_off_commands"], 0)
            startup_sequence = observed["last_submitted_sequence"]
            self.assertGreater(startup_sequence, 0)
            self.assertEqual(observed["before_shutdown"]["last_applied_sequence"], startup_sequence)
            self.assertEqual(observed["before_shutdown"]["resolved_sequence"], startup_sequence)
            self.assertEqual(prefix.diagnostics["midi_replay"]["accepted_packets"], 0)
            self.assertEqual(prefix.diagnostics["midi_replay"]["dropped_packets"], 0)
            self.assertTrue(prefix.diagnostics["midi_replay"]["connected_before_shutdown"])
            self.assertEqual(prefix.saved_bytes, STATE)
        with self.run_native(3200, events, final_size=(960, 700), midi_events=midi_events) as run:
            self.assert_control_path(run, [CONTROLS])
            self.assert_hold_path(run, [
                EMPTY, ((60,), (), ()), ((60,), (60,), ()), ((60,), (60, 64), ()),
                ((60,), (60, 64), (25,)), ((60,), (64,), (25,)),
                ((), (64,), (25,)), ((), (), (25,)), EMPTY,
            ])
            self.assert_commands(run, on=5, off=5, startup_sequence=startup_sequence)
            acknowledged_after_ui_release = [item for item in run.diagnostics["replay"]["observations"]
                                            if 2100 <= item["elapsed_ms"] < 2350
                                            and item["last_applied_sequence"] == item["last_submitted_sequence"]]
            self.assertTrue(acknowledged_after_ui_release)
            self.assertEqual(holds(acknowledged_after_ui_release[-1]), ((60,), (64,), (25,)),
                             "The UI release cannot clear the independent MIDI C4 owner")
            self.assertEqual(run.diagnostics["midi_replay"]["accepted_packets"], 6)
            self.assertEqual(run.diagnostics["midi_replay"]["dropped_packets"], 0)
            self.assertTrue(run.diagnostics["midi_replay"]["connected_before_shutdown"])
            self.assert_views(run, [
                ("play", "dimensional", 1280, 900), ("rotary", "dimensional", 1280, 900),
                ("rotary", "flat", 1280, 900), ("service", "flat", 1280, 900),
                ("service", "flat", 960, 700), ("play", "flat", 960, 700),
            ])
            self.assertEqual(run.saved_bytes, STATE)


if __name__ == "__main__":
    unittest.main(verbosity=2)
