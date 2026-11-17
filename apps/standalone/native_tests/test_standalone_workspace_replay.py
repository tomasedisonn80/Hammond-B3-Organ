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
from itertools import groupby
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
# Give the asynchronous Space command a visible Play interval before moving
# to Rotary. The original 180 ms gap could contain only a submitted snapshot
# on the actual reference-size software painter; its applied snapshot then
# first appeared in Rotary. Keep every painted-hold assertion and the process
# deadline, and shift only the later journey by this fixed observation dwell.
HEADER_VISUAL_SETTLE_MS = 600
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


def painted_holds(frame: dict) -> tuple[int, int, int]:
    return tuple(frame["held_targets"][part] for part in ("upper", "lower", "pedals"))


def unique(values: list) -> list:
    return [value for index, value in enumerate(values) if index == 0 or value != values[index - 1]]


def assert_copied_startup(case: unittest.TestCase, replay: dict, startup_sequence: int) -> None:
    """Require the full run's actual first copy of an independently proved origin."""
    case.assertGreater(startup_sequence, 0)
    case.assertTrue(replay["observations"], "The copied startup observation must be present")
    initial = replay["observations"][0]
    case.assertEqual(initial["last_applied_sequence"], startup_sequence)
    case.assertEqual(initial["resolved_sequence"], startup_sequence)
    case.assertEqual(initial["controls"], CONTROLS)
    case.assertEqual(holds(initial), EMPTY)
    # Queued acceptance may already be ahead of this retained applied copy.
    case.assertGreaterEqual(initial["last_submitted_sequence"], startup_sequence)


def assert_copied_chronology(case: unittest.TestCase, replay: dict, startup_sequence: int) -> None:
    """Check coherent copied musical state without demanding every FIFO prefix."""
    case.assertGreater(startup_sequence, 0)
    case.assertTrue(replay["observations"], "Musical copied observations are required")
    final = replay["last_submitted_sequence"]
    case.assertGreaterEqual(final, startup_sequence)
    previous_elapsed = 0
    previous_applied = previous_submitted = startup_sequence
    previous_state = None
    for item in replay["observations"]:
        applied, submitted = item["last_applied_sequence"], item["last_submitted_sequence"]
        musical_state = (item["controls"], item["manual_notes"], item["pedal_ids"])
        case.assertGreaterEqual(item["elapsed_ms"], previous_elapsed)
        case.assertGreaterEqual(applied, previous_applied)
        case.assertGreaterEqual(submitted, previous_submitted)
        case.assertEqual(item["resolved_sequence"], applied)
        case.assertLessEqual(applied, submitted)
        case.assertLessEqual(submitted, final)
        if previous_state is not None and applied == previous_applied:
            case.assertEqual(musical_state, previous_state,
                             "Unchanged applied sequence must preserve the complete copied musical state")
        previous_elapsed = item["elapsed_ms"]
        previous_applied, previous_submitted = applied, submitted
        previous_state = musical_state
    before = replay["before_shutdown"]
    if before["last_applied_sequence"] == previous_applied:
        case.assertEqual((before["controls"], before["manual_notes"], before["pedal_ids"]), previous_state,
                         "The final copied state cannot change without a newly applied command")


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
            self.assertEqual(data["runtime"]["video_driver"], "dummy")
            self.assertEqual(data["runtime"]["renderer"], "software")
            self.assertEqual(painted_holds(data["presentation"]["before_shutdown"]),
                             tuple(map(len, holds(data["replay"]["before_shutdown"]))),
                             "The last painted counts must precede joined-shutdown cleanup")
            for frame in [*data["presentation"]["observations"], data["presentation"]["last_painted"]]:
                capture = frame["pointer_capture"]
                self.assertFalse(capture["sdl_captured"])
                self.assertFalse(capture["ui_captured"])
                self.assertEqual((capture["successes"], capture["losses"], capture["release_calls"]), (0, 0, 0),
                                 "Dummy capture refusal must not be reported as an admitted/released OS capture")
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
        presentation = run.diagnostics["presentation"]
        frames = [*presentation["observations"], presentation["before_shutdown"]]
        self.assertEqual(unique([painted_holds(frame) for frame in frames]),
                         unique([tuple(map(len, state)) for state in expected]),
                         "Painted observations must retain applied held-count changes")

    def assert_commands(self, run: workflow_fixture.WorkflowRun, *, on: int, off: int,
                        control_changes: int = 0, startup_sequence: int) -> None:
        observed = run.diagnostics["replay"]
        self.assertEqual(observed["accepted_note_on_commands"], on)
        self.assertEqual(observed["accepted_note_off_commands"], off)
        assert_copied_chronology(self, observed, startup_sequence)
        final = observed["last_submitted_sequence"]
        self.assertEqual(final - startup_sequence, on + off + control_changes,
                         "Navigation must not inject a sound command or release")
        self.assertEqual(observed["before_shutdown"]["last_applied_sequence"], final)
        self.assertEqual(observed["before_shutdown"]["resolved_sequence"], final)

    def assert_startup_prefix(self, *, size: tuple[int, int] = (1280, 900),
                              flat: bool = False, state: bytes = STATE) -> int:
        # Each caller gets a fresh matching process, not a cached observation
        # or an origin inferred from that full journey's final command count.
        with self.run_native(250, [], size=size, flat=flat, state=state) as startup:
            self.assert_control_path(startup, [CONTROLS])
            self.assert_hold_path(startup, [EMPTY])
            observed = startup.diagnostics["replay"]
            startup_sequence = observed["last_submitted_sequence"]
            assert_copied_startup(self, observed, startup_sequence)
            self.assert_commands(startup, on=0, off=0, startup_sequence=startup_sequence)
            self.assertEqual(startup.saved_bytes, state,
                             "The empty startup prefix must preserve its exact input bytes")
            return startup_sequence

    def assert_views(self, run: workflow_fixture.WorkflowRun, expected: list[tuple], *,
                     held_targets: list[tuple[int, int, int]] | None = None) -> None:
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
        if held_targets is not None:
            # Group consecutive visits, so an earlier Play frame cannot stand
            # in for the held owner after returning from a hidden workspace.
            visits = [list(group) for _, group in groupby(frames, key=lambda item: (
                item["workspace"], item["presentation"], item["window_width"], item["window_height"]))]
            self.assertEqual(len(visits), len(held_targets))
            for view, visit, counts in zip(expected, visits, held_targets):
                self.assertIn(counts, [painted_holds(frame) for frame in visit],
                              f"Applied held targets must appear in the painted visit {view}")

    def assert_capture_refusals(self, run: workflow_fixture.WorkflowRun, attempts: int) -> None:
        presentation = run.diagnostics["presentation"]
        self.assertEqual(presentation["before_shutdown"]["pointer_capture"], {
            "sdl_captured": False, "ui_captured": False, "attempts": attempts,
            "successes": 0, "losses": 0, "release_calls": 0,
        })
        self.assertEqual(presentation["observations"][-1]["pointer_capture"]["attempts"], attempts,
                         "Capture counter changes must be retained even when both endpoints are uncaptured")

    def assert_header_hold_prefixes(self, run: workflow_fixture.WorkflowRun,
                                   startup_sequence: int, *, through: int) -> None:
        # These are the header journey's four original note commands, not an
        # arbitrary allowed subsequence. Only its first Upper-only sample may
        # be absent from the full run; the separate completed prefix proves it.
        self.assertIn(through, (1, 4))
        states = (EMPTY, ((60,), (), ()), ((60,), (60,), ()),
                  ((60,), (), ()), EMPTY)
        earliest = (0, 180, 320, 1600 + HEADER_VISUAL_SETTLE_MS,
                    1800 + HEADER_VISUAL_SETTLE_MS)
        replay = run.diagnostics["replay"]
        final = startup_sequence + through
        previous_applied = previous_submitted = startup_sequence
        previous_elapsed = 0
        seen = set()
        for item in replay["observations"]:
            applied, submitted = item["last_applied_sequence"], item["last_submitted_sequence"]
            self.assertEqual(item["resolved_sequence"], applied)
            self.assertGreaterEqual(applied, previous_applied)
            self.assertGreaterEqual(submitted, previous_submitted)
            self.assertLessEqual(applied, submitted)
            self.assertLessEqual(submitted, final)
            prefix = applied - startup_sequence
            self.assertIn(prefix, range(through + 1))
            self.assertEqual(holds(item), states[prefix])
            self.assertGreaterEqual(item["elapsed_ms"], previous_elapsed)
            self.assertGreaterEqual(item["elapsed_ms"], earliest[prefix])
            previous_applied, previous_submitted = applied, submitted
            previous_elapsed = item["elapsed_ms"]
            seen.add(prefix)
        required = {1} if through == 1 else {0, 2, 3, 4}
        self.assertTrue(required.issubset(seen),
                        f"Required acknowledged header stages missing: {required - seen}")
        before = replay["before_shutdown"]
        self.assertEqual(before["last_applied_sequence"], final)
        self.assertEqual(before["resolved_sequence"], final)
        self.assertEqual(holds(before), states[through],
                         "Shutdown cleanup must not substitute for a scripted owner release")

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
                events = [(at + (HEADER_VISUAL_SETTLE_MS if at >= 500 else 0), event)
                          for at, event in events]
                # Complete the original startup and first-note prefixes at each
                # size. Copied snapshots need not sample the short interval
                # between the original 180 ms Upper and 320 ms Space presses.
                with self.run_native(250, [event for event in events if event[0] < 180],
                                     size=size, state=NONCANONICAL_STATE) as startup:
                    self.assert_control_path(startup, [CONTROLS])
                    self.assert_hold_path(startup, [EMPTY])
                    observed = startup.diagnostics["replay"]
                    startup_sequence = observed["last_submitted_sequence"]
                    self.assert_commands(startup, on=0, off=0, startup_sequence=startup_sequence)
                    self.assertEqual(startup.saved_bytes, NONCANONICAL_STATE,
                                     "The startup prefix must not save or canonicalize its input")
                with self.run_native(250, [event for event in events if event[0] < 320],
                                     size=size, state=NONCANONICAL_STATE) as upper:
                    self.assert_control_path(upper, [CONTROLS])
                    self.assert_commands(upper, on=1, off=0, startup_sequence=startup_sequence)
                    self.assert_header_hold_prefixes(upper, startup_sequence, through=1)
                    self.assertEqual(upper.saved_bytes, NONCANONICAL_STATE,
                                     "The held-note prefix must not save or canonicalize its input")
                with self.run_native(2250 + HEADER_VISUAL_SETTLE_MS, events,
                                     size=size, state=NONCANONICAL_STATE,
                                     screenshot=True) as run:
                    self.assert_control_path(run, [CONTROLS])
                    self.assert_header_hold_prefixes(run, startup_sequence, through=4)
                    self.assert_commands(run, on=2, off=2, startup_sequence=startup_sequence)
                    self.assert_views(run, [(workspace, mode, *size) for workspace, mode in (
                        ("play", "dimensional"), ("rotary", "dimensional"), ("rotary", "flat"),
                        ("service", "flat"), ("play", "flat"), ("play", "dimensional"))],
                        held_targets=[(1, 1, 0)] * 6)
                    self.assert_capture_refusals(run, 6)
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
                    startup_sequence = self.assert_startup_prefix(flat=flat)
                    with self.run_native(2600, events, flat=flat) as run:
                        assert_copied_startup(self, run.diagnostics["replay"], startup_sequence)
                        self.assert_control_path(run, [CONTROLS])
                        self.assert_hold_path(run, [EMPTY, ((60,), (), ()), ((60, 62), (), ()),
                                                   ((60, 62), (60,), ()), ((62,), (60,), ()),
                                                   ((), (60,), ()), EMPTY])
                        self.assert_commands(run, on=3, off=3, startup_sequence=startup_sequence)
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
        startup_sequence = self.assert_startup_prefix()
        with self.run_native(3750, events, final_size=(960, 700)) as run:
            assert_copied_startup(self, run.diagnostics["replay"], startup_sequence)
            self.assert_control_path(run, expected)
            self.assert_hold_path(run, [EMPTY])
            self.assert_commands(run, on=0, off=0, control_changes=6, startup_sequence=startup_sequence)
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
        startup_sequence = self.assert_startup_prefix()
        with self.run_native(1900, events, final_size=(960, 700)) as run:
            assert_copied_startup(self, run.diagnostics["replay"], startup_sequence)
            self.assert_control_path(run, [CONTROLS, zero, CONTROLS])
            self.assert_hold_path(run, [EMPTY, ((60,), (), ()), EMPTY])
            self.assert_commands(run, on=1, off=1, control_changes=2, startup_sequence=startup_sequence)
            self.assert_views(run, [
                ("play", "dimensional", 1280, 900), ("play", "flat", 1280, 900),
                ("service", "flat", 1280, 900), ("play", "flat", 1280, 900),
                ("play", "flat", 960, 700),
            ], held_targets=[(1, 0, 0)] * 5)
            self.assert_capture_refusals(run, 2)
            self.assertEqual(run.saved_bytes, STATE)

    def test_pointer_capture_failure_preserves_keyboard_owner_during_navigation(self) -> None:
        events = [(180, "key_down A none 0"), (450, "mouse_down 222 580")]
        events += tap(650, "F6") + tap(850, "F7") + [(1050, "mouse_move 625 580")]
        events += tap(1250, "F4") + [(1450, "resize 960 700"), (1650, "mouse_move 230 470"),
                                    (1850, "mouse_up -80 -80"), (2050, "key_up A alt+shift")]
        startup_sequence = self.assert_startup_prefix()
        with self.run_native(2250, events, final_size=(960, 700)) as run:
            assert_copied_startup(self, run.diagnostics["replay"], startup_sequence)
            self.assert_control_path(run, [CONTROLS])
            observed = unique([holds(item) for item in run.diagnostics["replay"]["observations"]])
            # Pointer On/Off may share one audio callback; both legal published
            # paths keep keyboard C4 until its explicit original release.
            self.assertIn(observed, [
                [EMPTY, ((60,), (), ()), EMPTY],
                [EMPTY, ((60,), (), ()), ((36, 60), (), ()), ((60,), (), ()), EMPTY],
            ])
            self.assert_hold_path(run, observed)
            self.assert_commands(run, on=2, off=2, startup_sequence=startup_sequence)
            self.assertGreaterEqual(next(item["elapsed_ms"] for item in reversed(
                run.diagnostics["replay"]["observations"]) if holds(item) == EMPTY), 2050)
            self.assert_views(run, [
                ("play", "dimensional", 1280, 900), ("service", "dimensional", 1280, 900),
                ("service", "flat", 1280, 900), ("play", "flat", 1280, 900),
                ("play", "flat", 960, 700),
            ], held_targets=[(1, 0, 0)] * 5)
            self.assert_capture_refusals(run, 1)
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
            ], held_targets=[(1, 2, 1)] * 5 + [(0, 0, 0)])
            self.assert_capture_refusals(run, 4)
            self.assertEqual(run.saved_bytes, STATE)


class WorkspaceStartupChronology(unittest.TestCase):
    """Pure oracle checks; these synthetic dictionaries are not native evidence."""

    @staticmethod
    def observation(elapsed: int, applied: int, submitted: int,
                    held: tuple = EMPTY) -> dict:
        return {"elapsed_ms": elapsed, "last_applied_sequence": applied,
                "resolved_sequence": applied, "last_submitted_sequence": submitted,
                "controls": deepcopy(CONTROLS),
                "manual_notes": [list(held[0]), list(held[1])], "pedal_ids": list(held[2])}

    def setUp(self) -> None:
        self.origin = 3
        observations = [self.observation(197, 3, 4),
                        self.observation(283, 4, 4, ((60,), (), ())),
                        self.observation(500, 5, 5)]
        self.replay = {"observations": observations, "last_submitted_sequence": 5,
                       "accepted_note_on_commands": 1, "accepted_note_off_commands": 1,
                       "before_shutdown": self.before(observations[-1])}

    @staticmethod
    def before(observation: dict) -> dict:
        return {key: deepcopy(value) for key, value in observation.items()
                if key not in ("elapsed_ms", "last_submitted_sequence")}

    def check_commands(self, replay: dict, *, on: int = 1, off: int = 1,
                       control_changes: int = 0) -> workflow_fixture.WorkflowRun:
        run = workflow_fixture.WorkflowRun({"replay": replay}, STATE, 0.0)
        NativeWorkspaceReplayAcceptance.assert_commands(
            self, run, on=on, off=off, control_changes=control_changes, startup_sequence=self.origin)
        return run

    def test_queued_ahead_loaded_startup_is_accepted(self) -> None:
        # The first retained copy is later than 180 ms with its first note
        # already queued, while the independent loaded origin is still applied.
        assert_copied_startup(self, self.replay, self.origin)
        self.check_commands(self.replay)

    def test_full_run_must_retain_the_first_loaded_origin(self) -> None:
        for kind in ("empty", "omitted", "advanced_but_empty"):
            with self.subTest(kind=kind):
                replay = deepcopy(self.replay)
                if kind == "empty":
                    replay["observations"] = []
                elif kind == "omitted":
                    replay["observations"] = replay["observations"][1:]
                else:
                    replay["observations"][0].update(last_applied_sequence=4, resolved_sequence=4)
                with self.assertRaises(AssertionError):
                    assert_copied_startup(self, replay, self.origin)

    def test_first_loaded_state_requires_full_controls_and_empty_holds(self) -> None:
        for kind in ("remembered_bank", "percussion", "upper", "lower", "pedal"):
            with self.subTest(kind=kind):
                replay = deepcopy(self.replay)
                initial = replay["observations"][0]
                if kind == "remembered_bank":
                    initial["controls"]["manual_drawbars"][1][0][0] = 8
                elif kind == "percussion":
                    initial["controls"]["percussion"]["enabled"] = False
                elif kind == "pedal":
                    initial["pedal_ids"] = [1]
                else:
                    initial["manual_notes"][0 if kind == "upper" else 1] = [60]
                with self.assertRaises(AssertionError):
                    assert_copied_startup(self, replay, self.origin)

    def test_chronology_rejects_regressed_elapsed_time(self) -> None:
        self.replay["observations"][1]["elapsed_ms"] = 196
        with self.assertRaises(AssertionError):
            self.check_commands(self.replay)

    def test_chronology_rejects_regressed_applied_sequence(self) -> None:
        self.replay["observations"].insert(2, self.observation(400, 3, 5))
        with self.assertRaises(AssertionError):
            self.check_commands(self.replay)

    def test_chronology_rejects_regressed_submitted_sequence(self) -> None:
        self.replay["observations"][0]["last_submitted_sequence"] = 5
        with self.assertRaises(AssertionError):
            self.check_commands(self.replay)

    def test_chronology_rejects_inconsistent_sequences_and_bounds(self) -> None:
        for changes in ({"resolved_sequence": 4},
                        {"last_applied_sequence": 2, "resolved_sequence": 2},
                        {"last_submitted_sequence": 2},
                        {"last_submitted_sequence": 6}):
            with self.subTest(changes=changes):
                replay = deepcopy(self.replay)
                replay["observations"][0].update(changes)
                with self.assertRaises(AssertionError):
                    self.check_commands(replay)

    def test_same_applied_sequence_cannot_change_musical_state(self) -> None:
        for kind in ("controls", "manual_notes", "pedal_ids"):
            with self.subTest(kind=kind):
                replay = deepcopy(self.replay)
                duplicate = self.observation(220, 3, 4)
                if kind == "controls":
                    duplicate["controls"]["expression"] = 0.5
                elif kind == "manual_notes":
                    duplicate["manual_notes"][1] = [60]
                else:
                    duplicate["pedal_ids"] = [1]
                replay["observations"].insert(1, duplicate)
                assert_copied_startup(self, replay, self.origin)
                with self.assertRaises(AssertionError):
                    self.check_commands(replay)

    def test_final_copy_cannot_change_state_without_application(self) -> None:
        self.replay["before_shutdown"]["controls"]["pedal_drawbars"][0] = 8
        with self.assertRaises(AssertionError):
            self.check_commands(self.replay)

    def test_command_counts_delta_and_final_acknowledgment_remain_strict(self) -> None:
        for kind in ("on", "off", "delta", "applied", "resolved"):
            with self.subTest(kind=kind):
                replay = deepcopy(self.replay)
                if kind in ("on", "off"):
                    replay[f"accepted_note_{kind}_commands"] = 2
                elif kind in ("applied", "resolved"):
                    key = "last_applied_sequence" if kind == "applied" else "resolved_sequence"
                    replay["before_shutdown"][key] = 4
                with self.assertRaises(AssertionError):
                    self.check_commands(replay, control_changes=1 if kind == "delta" else 0)

    def test_nonpositive_origin_and_empty_chronology_are_rejected(self) -> None:
        for origin in (0, -1):
            with self.subTest(origin=origin), self.assertRaises(AssertionError):
                assert_copied_chronology(self, self.replay, origin)
        self.replay["observations"] = []
        with self.assertRaises(AssertionError):
            assert_copied_chronology(self, self.replay, self.origin)

    def test_existing_upper_prefix_can_first_copy_after_origin(self) -> None:
        observation = self.observation(283, 4, 4, ((60,), (), ()))
        replay = {"observations": [observation], "last_submitted_sequence": 4,
                  "accepted_note_on_commands": 1, "accepted_note_off_commands": 0,
                  "before_shutdown": self.before(observation)}
        run = self.check_commands(replay, on=1, off=0)
        NativeWorkspaceReplayAcceptance.assert_header_hold_prefixes(self, run, self.origin, through=1)

    def test_existing_header_full_prefix_coalescing_remains_legal(self) -> None:
        observations = [self.observation(197, 3, 4),
                        self.observation(320, 5, 5, ((60,), (60,), ())),
                        self.observation(2200, 6, 6, ((60,), (), ())),
                        self.observation(2400, 7, 7)]
        replay = {"observations": observations, "last_submitted_sequence": 7,
                  "accepted_note_on_commands": 2, "accepted_note_off_commands": 2,
                  "before_shutdown": self.before(observations[-1])}
        run = self.check_commands(replay, on=2, off=2)
        NativeWorkspaceReplayAcceptance.assert_header_hold_prefixes(self, run, self.origin, through=4)


if __name__ == "__main__":
    unittest.main(verbosity=2)
