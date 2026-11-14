#!/usr/bin/env python3
"""Independent musical workflows through the real standalone SDL event loop.

Requires HAMMOND_STANDALONE_EXECUTABLE; absence is a failed prerequisite.
All runs explicitly use SDL dummy drivers and private state/output paths.
Expected musical controls, note identities and saved bytes are literal oracles.
No UiModel, replay parser, Engine, or production serializer is imported.
"""

from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile
import time
import unittest

from test_standalone_app import assert_no_midi_input


REPOSITORY = Path(__file__).resolve().parents[3]
EXAMPLES = REPOSITORY / "examples" / "standalone-input-v2"
PROCESS_TIMEOUT = 9.0

# Accepted noncanonical input deliberately differs from canonical saved output.
INITIAL_STATE = b"\tB3CONTROLS3\r\nexpression +3.75e-1\r\n" + b"""percussion enabled 1 harmonic third volume soft decay fast
pedal drawbars 2 7
manual upper selected A route_enabled 0
bank A 0 1 2 3 4 5 6 7 8
bank B 8 7 6 5 4 3 2 1 0
manual lower selected B route_enabled 1
bank A 1 3 5 7 0 2 4 6 8
bank B 8 6 4 2 0 7 5 3 1
end
 \t
""".replace(b"\n", b"\r\n")

INITIAL_CONTROLS = {
    "manual_drawbars": [
        [[0, 1, 2, 3, 4, 5, 6, 7, 8], [8, 7, 6, 5, 4, 3, 2, 1, 0]],
        [[1, 3, 5, 7, 0, 2, 4, 6, 8], [8, 6, 4, 2, 0, 7, 5, 3, 1]],
    ],
    "selected_banks": [0, 1], "fixed_registrations": [0, 0], "preset_selections": [0, 11],
    "route_enabled": [False, True],
    "expression": 0.375,
    "pedal_drawbars": [2, 7],
    "percussion": {"enabled": True, "harmonic": 1, "volume": 1, "decay": 1},
}

SAVED_STATE = b"""B3CONTROLS4
registration_catalog atlas-chapel-nominal-v1 sha256 c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf
expression 0.375
percussion enabled 1 harmonic third volume soft decay fast
pedal drawbars 2 7
manual upper selected A fixed_registration none route_enabled 0
bank A 0 1 2 3 4 5 6 7 8
bank B 0 7 6 5 4 3 2 1 0
manual lower selected B fixed_registration none route_enabled 1
bank A 1 3 5 7 0 2 4 6 8
bank B 8 6 4 2 0 7 5 3 1
end
"""


# Independent state4 input exercises remembered banks distinct from fixed rows.
FIXED_STATE = b"""B3CONTROLS4
registration_catalog atlas-chapel-nominal-v1 sha256 c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf
expression 0.375
percussion enabled 1 harmonic third volume soft decay fast
pedal drawbars 2 7
manual upper selected A fixed_registration F# route_enabled 1
bank A 0 1 2 3 4 5 6 7 8
bank B 8 7 6 5 4 3 2 1 0
manual lower selected B fixed_registration G# route_enabled 1
bank A 1 3 5 7 0 2 4 6 8
bank B 8 6 4 2 0 7 5 3 1
end
"""
FIXED_CONTROLS = deepcopy(INITIAL_CONTROLS)
FIXED_CONTROLS.update(fixed_registrations=[6, 8], preset_selections=[6, 8], route_enabled=[True, True])
FIXED_SAVED_STATE = b"""B3CONTROLS4
registration_catalog atlas-chapel-nominal-v1 sha256 c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf
expression 0.375
percussion enabled 1 harmonic third volume soft decay fast
pedal drawbars 2 7
manual upper selected A fixed_registration F# route_enabled 0
bank A 0 1 2 3 4 5 6 7 8
bank B 8 7 6 5 4 3 2 1 0
manual lower selected A fixed_registration none route_enabled 1
bank A 1 3 5 7 0 2 4 6 8
bank B 8 6 4 2 0 7 5 3 1
end
"""
# Independent literal points in the exposed naturals/accidentals at 960x700.
# Order is C, C#, D, D#, E, F, F#, G, G#, A, A#, B.
PRESET_POINTS_MINIMUM = (
    ((34, 469), (44, 440), (54, 469), (64, 440), (74, 469), (94, 469),
     (104, 440), (114, 469), (124, 440), (134, 469), (144, 440), (154, 469)),
    ((34, 559), (44, 530), (54, 559), (64, 530), (74, 559), (94, 559),
     (104, 530), (114, 559), (124, 530), (134, 559), (144, 530), (154, 559)),
)

EMPTY_HOLDS = ((), (), ())


def tap(at_ms: int, key: str, modifiers: str = "none") -> list[tuple[int, str]]:
    return [(at_ms, f"key_down {key} {modifiers} 0"), (at_ms + 10, f"key_up {key} {modifiers}")]


def tabs(at_ms: int, count: int, modifiers: str = "none") -> list[tuple[int, str]]:
    return [event for index in range(count) for event in tap(at_ms + 20 * index, "Tab", modifiers)]


def click(at_ms: int, x: int, y: int) -> list[tuple[int, str]]:
    return [(at_ms, f"mouse_down {x} {y}"), (at_ms + 20, f"mouse_up {x} {y}")]


def replay(duration_ms: int, events: list[tuple[int, str]]) -> str:
    return f"B3UIREPLAY1\nduration_ms {duration_ms}\n" + "".join(
        f"{at_ms} {action}\n" for at_ms, action in events
    )


def replay_prefix(source: str, duration_ms: int) -> str:
    """End a known fixture before later events, retaining its original timings."""
    lines = source.splitlines()
    return f"B3UIREPLAY1\nduration_ms {duration_ms}\n" + "".join(
        line + "\n" for line in lines[2:]
        if not line.strip() or line.lstrip().startswith("#") or int(line.split()[0]) < duration_ms
    )


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate diagnostics member: {key}")
        result[key] = value
    return result


def reject_nonfinite(token: str) -> None:
    raise ValueError(f"Non-JSON numeric token: {token}")


def consecutive_unique(values: list[object]) -> list[object]:
    result: list[object] = []
    for value in values:
        if not result or result[-1] != value:
            result.append(value)
    return result


@dataclass(frozen=True)
class WorkflowRun:
    diagnostics: dict
    saved_bytes: bytes
    elapsed: float


def diagnostic_excerpt(value: dict | Path) -> str:
    """Keep bounded per-process evidence in failures before temporary cleanup."""
    limit = 65536
    if isinstance(value, Path):
        try:
            if not value.is_file():
                return "Diagnostics file is unavailable"
            with value.open("rb") as source:
                content = source.read(limit + 1).decode("utf-8", errors="replace")
        except OSError as error:
            return f"Diagnostics could not be read: {error}"
    else:
        content = json.dumps(value, sort_keys=True)
    return "Copied diagnostics:\n" + content[:limit] + ("\n[truncated at 65536 characters]" if len(content) > limit else "")


@contextmanager
def retain_workflow_failure(run: WorkflowRun, case: str):
    """Preserve diagnostics for assertions made after invoke() has returned."""
    try:
        yield
    except Exception as error:
        raise AssertionError(f"{case}: {type(error).__name__}: {error}\n"
                             + diagnostic_excerpt(run.diagnostics)) from error


class NativeWorkflowAcceptance(unittest.TestCase):
    invocations = 0

    @classmethod
    def setUpClass(cls) -> None:
        configured = os.environ.get("HAMMOND_STANDALONE_EXECUTABLE", "")
        if not configured:
            raise RuntimeError("HAMMOND_STANDALONE_EXECUTABLE is required; build hammond_standalone first")
        cls.executable = Path(configured).resolve(strict=True)
        if not cls.executable.is_file() or not os.access(cls.executable, os.X_OK):
            raise RuntimeError(f"Required native executable is not executable: {cls.executable}")
        print(f"Workflow executable SHA-256: {hashlib.sha256(cls.executable.read_bytes()).hexdigest()}", flush=True)

    @classmethod
    def tearDownClass(cls) -> None:
        print(f"Actual native workflow subprocesses: {cls.invocations}", flush=True)

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="hammond-native-workflows-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.run_count = 0

    def invoke(self, source: str, *, state: bytes = INITIAL_STATE,
               size: tuple[int, int] = (1280, 900),
               initial_size: tuple[int, int] = (1280, 900)) -> WorkflowRun:
        self.run_count += 1
        directory = self.root / f"run-{self.run_count}"
        directory.mkdir()
        state_path = directory / "musical controls.b3controls"
        script_path = directory / "input workflow.b3ui"
        diagnostics_path = directory / "diagnostics.json"
        state_path.write_bytes(state)
        script_path.write_text(source, encoding="ascii", newline="\n")
        environment = os.environ.copy()
        environment.update(SDL_AUDIODRIVER="dummy", SDL_VIDEODRIVER="dummy")
        started = time.monotonic()
        self.__class__.invocations += 1
        try:
            process = subprocess.run(
                [str(self.executable), "--state", str(state_path), "--input-script", str(script_path),
                 "--width", str(initial_size[0]), "--height", str(initial_size[1]),
                 "--diagnostics", str(diagnostics_path)],
                cwd=directory, env=environment, stdin=subprocess.DEVNULL,
                capture_output=True, text=True, errors="replace", timeout=PROCESS_TIMEOUT, check=False,
            )
        except subprocess.TimeoutExpired as error:
            self.fail(f"Native replay exceeded {PROCESS_TIMEOUT}s: {error}")
        elapsed = time.monotonic() - started
        self.assertEqual(process.returncode, 0,
                         f"Native workflow failed ({elapsed:.3f}s):\n{process.stdout}\n{process.stderr}\n"
                         + (diagnostic_excerpt(diagnostics_path) if process.returncode != 0 else ""))
        duration_seconds = int(source.splitlines()[1].split()[1]) / 1000.0
        self.assertGreaterEqual(elapsed, duration_seconds - 0.04,
                                "A completed replay must reach its declared duration")
        self.assertEqual(process.stderr, "", f"Unexpected application errors: {process.stderr}")
        self.assertTrue(diagnostics_path.is_file(), "Successful replay must write requested diagnostics")
        data = json.loads(diagnostics_path.read_text(encoding="utf-8"),
                          object_pairs_hook=unique_object, parse_constant=reject_nonfinite)
        try:
            self.assert_common(data, source, state_path, size)
        except AssertionError as error:
            self.fail(f"{error}\n{diagnostic_excerpt(data)}")
        self.assertEqual(script_path.read_text(encoding="ascii"), source, "Replay must not modify its input")
        self.assertEqual({path.name for path in directory.iterdir()},
                         {state_path.name, script_path.name, diagnostics_path.name},
                         "The workflow must not leave temporary saves or unexpected files")
        return WorkflowRun(data, state_path.read_bytes(), elapsed)

    def assert_common(self, data: dict, source: str, state_path: Path, size: tuple[int, int]) -> None:
        self.assertEqual(data["schema_version"], 3)
        assert_no_midi_input(self, data)
        self.assertEqual(data["application"], "hammond_standalone")
        self.assertEqual(data["state_path"], str(state_path))
        self.assertEqual(data["errors"], {"count": 0, "last": ""})
        runtime, audio, session = data["runtime"], data["audio"], data["session"]
        self.assertEqual(runtime["video_driver"], "dummy")
        self.assertEqual((runtime["window_width"], runtime["window_height"]), size)
        self.assertEqual((runtime["drawable_width"], runtime["drawable_height"]), size)
        self.assertGreater(runtime["rendered_images"], 0)
        self.assertEqual(audio["driver"], "dummy")
        self.assertTrue(audio["open_before_shutdown"])
        self.assertTrue(audio["running_before_shutdown"])
        self.assertGreater(audio["callback_count"], 0)
        self.assertGreater(audio["rendered_frames"], 0)
        self.assertEqual(audio["channels"], 2)
        self.assertEqual(audio["sample_format"], audio["native_float32_format"])
        self.assertEqual(audio["buffer_bytes"], audio["buffer_frames"] * 8)
        for field in ("render_failures", "format_failures", "overrange_failures", "overrange_samples",
                      "nonfinite_failures", "nonfinite_samples"):
            self.assertEqual(audio[field], 0, field)
        self.assertEqual(audio["last_render_status"], "ok")
        self.assertEqual(audio["last_lifecycle_status"], "ok")
        self.assertTrue(session["snapshot_available"])
        self.assertTrue(session["prepared"])
        self.assertFalse(session["running_after_shutdown"])
        self.assertFalse(session["held_after_shutdown"])
        self.assertGreater(session["frame_clock"], 0)
        for field in ("recovery_count", "queue_overflows", "rejected_commands", "fault_flags"):
            self.assertEqual(session[field], 0, field)
        # These fixtures can queue one redundant scoped release immediately
        # before each device close. Joined Session.stop clears every owner and
        # may discard that queued cleanup. This finite lifecycle allowance is
        # separate from the strict pre-close script acknowledgment/hold checks.
        self.assertGreaterEqual(session["discarded_commands"], 0)
        self.assertLessEqual(session["discarded_commands"], data["replay"]["device_starts"])
        self.assertTrue(math.isfinite(session["maximum_observed_peak"]))
        self.assertGreaterEqual(session["maximum_observed_peak"], 0)
        self.assertFalse(data["smoke"]["requested"])
        self.assertFalse(data["smoke"]["note_on_sent"])
        self.assertFalse(data["smoke"]["note_off_sent"])
        # Schema 2 adds inert MIDI diagnostics to these UI-only workflows;
        # joined shutdown and pre-shutdown musical observations retain meaning.
        metadata = data["replay"]
        self.assertIs(type(metadata["observation_capacity"]), int)
        self.assertEqual(metadata["observation_capacity"], 512)
        event_count = sum(bool(line.strip()) and not line.lstrip().startswith("#")
                          for line in source.splitlines()[2:])
        self.assertTrue(metadata["completed"])
        self.assertTrue(metadata["delivered"])
        self.assertEqual(metadata["scheduled_events"], event_count)
        self.assertEqual(metadata["pushed_events"], event_count)
        self.assertTrue(metadata["final_acknowledged"])
        self.assertFalse(metadata["observations_truncated"])
        self.assertGreaterEqual(metadata["device_starts"], 1)
        before = metadata["before_shutdown"]
        self.assertGreaterEqual(before["resolved_sequence"], metadata["last_submitted_sequence"])
        self.assertGreaterEqual(before["last_applied_sequence"], metadata["last_submitted_sequence"])
        self.assertEqual(before["controls"], data["controls"])
        self.assertTrue(metadata["observations"], "Pre-shutdown musical observations are required")

    @staticmethod
    def holds(observation: dict) -> tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
        return tuple(observation["manual_notes"][0]), tuple(observation["manual_notes"][1]), tuple(observation["pedal_ids"])

    def assert_hold_path(self, run: WorkflowRun, expected: list[tuple]) -> list[dict]:
        observations = run.diagnostics["replay"]["observations"]
        transitions: list[dict] = []
        for item in observations:
            if not transitions or self.holds(item) != self.holds(transitions[-1]):
                transitions.append(item)
        actual = [self.holds(item) for item in transitions]
        self.assertEqual(actual, expected, "Acknowledged held-note transitions differ from musical intent")
        self.assertEqual(self.holds(run.diagnostics["replay"]["before_shutdown"]), expected[-1],
                         "Shutdown cleanup must not stand in for the scripted release")
        return transitions

    def assert_control_path(self, run: WorkflowRun, expected: list[dict]) -> list[dict]:
        observations = run.diagnostics["replay"]["observations"]
        # Startup can publish a prepared but not yet restored snapshot. The
        # first literal loaded state is the independent baseline for edits.
        start = next((index for index, item in enumerate(observations)
                      if item["controls"] == expected[0]), None)
        self.assertIsNotNone(start, "The startup controls were never acknowledged")
        transitions: list[dict] = []
        for item in observations[start:]:
            if not transitions or item["controls"] != transitions[-1]["controls"]:
                transitions.append(item)
        actual = [item["controls"] for item in transitions]
        self.assertEqual(actual, expected)
        self.assertEqual(run.diagnostics["controls"], expected[-1])
        return transitions

    def assert_note_commands(self, run: WorkflowRun, on: int, off: int) -> None:
        metadata = run.diagnostics["replay"]
        self.assertEqual(metadata["accepted_note_on_commands"], on)
        self.assertEqual(metadata["accepted_note_off_commands"], off)

    def assert_command_prefixes(self, run: WorkflowRun, prefixes: list[tuple[int, tuple]]) -> None:
        """Check literal coherent states without requiring every UI sample."""
        metadata = run.diagnostics["replay"]
        # These two workflows have one callback sequence epoch. Device restart
        # cases need separate expectations and must not use this helper blindly.
        self.assertEqual(metadata["device_starts"], 1)
        self.assertTrue(metadata["passed"])
        final_sequence = metadata["last_submitted_sequence"]
        self.assertIs(type(final_sequence), int)
        startup_sequence = final_sequence - (len(prefixes) - 1)
        self.assertGreaterEqual(startup_sequence, 1)
        before = metadata["before_shutdown"]
        self.assertEqual(before["resolved_sequence"], final_sequence)
        self.assertEqual(before["last_applied_sequence"], final_sequence)
        self.assertEqual(before["controls"], INITIAL_CONTROLS)
        self.assertEqual(self.holds(before), prefixes[-1][1])
        previous = 0
        for observation in [*metadata["observations"], before]:
            sequence = observation["last_applied_sequence"]
            self.assertIs(type(sequence), int)
            self.assertIn(sequence, range(1, final_sequence + 1))
            self.assertGreaterEqual(sequence, previous)
            self.assertEqual(observation["resolved_sequence"], sequence)
            submitted = observation.get("last_submitted_sequence", final_sequence)
            self.assertIs(type(submitted), int)
            self.assertLessEqual(sequence, submitted)
            self.assertLessEqual(submitted, final_sequence)
            prefix = max(0, sequence - startup_sequence)
            earliest, expected_holds = prefixes[prefix]
            if "elapsed_ms" in observation:
                elapsed = observation["elapsed_ms"]
                self.assertIs(type(elapsed), int)
                self.assertGreaterEqual(elapsed, earliest)
                if elapsed < prefixes[1][0]:
                    self.assertEqual(submitted, startup_sequence)
            self.assertEqual(observation["controls"], INITIAL_CONTROLS)
            self.assertEqual(self.holds(observation), expected_holds)
            previous = sequence
        self.assertEqual(previous, final_sequence)

    def test_replay_cli_errors_preserve_state_and_output_sentinels(self) -> None:
        for case, expected in (("mixed-smoke", 2), ("missing-input", 1), ("malformed-input", 1)):
            with self.subTest(case=case):
                directory = self.root / case
                directory.mkdir()
                state_path = directory / "controls.b3controls"
                input_path = directory / "input.b3ui"
                diagnostics_path = directory / "diagnostics.json"
                screenshot_path = directory / "screenshot.bmp"
                state_path.write_bytes(INITIAL_STATE)
                diagnostics_path.write_bytes(b"existing diagnostics sentinel\n")
                screenshot_path.write_bytes(b"existing screenshot sentinel\n")
                if case != "missing-input":
                    source = replay(400, []) if case == "mixed-smoke" else "UNSUPPORTED-REPLAY\n"
                    input_path.write_text(source, encoding="ascii", newline="\n")
                before = {path.name: path.read_bytes() for path in directory.iterdir()}
                arguments = [str(self.executable), "--state", str(state_path),
                             "--input-script", str(input_path), "--diagnostics", str(diagnostics_path),
                             "--screenshot", str(screenshot_path)]
                if case == "mixed-smoke":
                    arguments += ["--smoke-ms", "400"]
                environment = os.environ.copy()
                environment.update(SDL_AUDIODRIVER="dummy", SDL_VIDEODRIVER="dummy")
                self.__class__.invocations += 1
                try:
                    process = subprocess.run(
                        arguments, cwd=directory, env=environment, stdin=subprocess.DEVNULL,
                        capture_output=True, text=True, errors="replace", timeout=PROCESS_TIMEOUT, check=False,
                    )
                except subprocess.TimeoutExpired as error:
                    self.fail(f"Replay setup rejection exceeded {PROCESS_TIMEOUT}s: {error}")
                self.assertEqual(process.returncode, expected, f"{process.stdout}\n{process.stderr}")
                self.assertEqual(process.stdout, "")
                self.assertTrue(process.stderr.strip(), "Setup rejection must report a diagnostic")
                self.assertEqual({path.name: path.read_bytes() for path in directory.iterdir()}, before,
                                 "Rejected replay input must not touch state, outputs, or its input")

    def test_empty_replay_has_no_automatic_smoke_note_or_file_write(self) -> None:
        run = self.invoke(replay(400, []))
        self.assert_hold_path(run, [EMPTY_HOLDS])
        self.assert_note_commands(run, 0, 0)
        self.assertEqual(run.diagnostics["controls"], INITIAL_CONTROLS)
        self.assertEqual(run.saved_bytes, INITIAL_STATE)

    def test_original_note_ownership_survives_target_and_octave_changes(self) -> None:
        original = (EXAMPLES / "keyboard-notes.b3ui").read_text(encoding="ascii")
        # Literal command suffix: three original owners, their three releases,
        # then a fresh Upper press/release at the retained manual octave.
        prefixes = [(0, EMPTY_HOLDS), (200, ((60,), (), ())), (650, ((60,), (74,), ())),
                    (1100, ((60,), (74,), (17,))), (1500, ((), (74,), (17,))),
                    (1700, ((), (), (17,))), (1900, EMPTY_HOLDS),
                    (2100, ((72,), (), ())), (2300, EMPTY_HOLDS)]
        # The original complete fixture remains unchanged. Independent final
        # acknowledgments make every critical ownership/release state mandatory
        # even when the full run's UI samples coalesce adjacent transitions.
        for duration, commands, on, off in ((2600, 8, 4, 4), (1450, 3, 3, 0),
                (1650, 4, 3, 1), (1850, 5, 3, 2), (2050, 6, 3, 3), (2250, 7, 4, 3)):
            with self.subTest(endpoint_ms=duration):
                source = original if duration == 2600 else replay_prefix(original, duration)
                run = self.invoke(source)
                with retain_workflow_failure(run, f"Target/octave endpoint {duration} ms"):
                    self.assert_note_commands(run, on, off)
                    self.assertEqual(run.diagnostics["controls"], INITIAL_CONTROLS)
                    self.assertGreater(run.diagnostics["session"]["maximum_observed_peak"], 0)
                    self.assertEqual(run.saved_bytes, INITIAL_STATE)
                    self.assert_command_prefixes(run, prefixes[:commands + 1])

    def test_focus_loss_suppresses_repeat_and_duplicate_down_until_release(self) -> None:
        source = replay(2000, [
            (200, "key_down A none 0"), (400, "key_down A none 1"), (600, "focus_lost"),
            (800, "key_down A none 1"), (1000, "key_down A none 0"),
            (1200, "key_up A ctrl+alt+meta"), (1400, "key_down A none 0"),
            (1600, "key_up A none"), (1700, "key_down S none 1"), (1750, "key_up S none"),
        ])
        run = self.invoke(source)
        transitions = self.assert_hold_path(run, [EMPTY_HOLDS, ((60,), (), ()), EMPTY_HOLDS, ((60,), (), ()), EMPTY_HOLDS])
        self.assertGreaterEqual(transitions[2]["elapsed_ms"], 600)
        self.assertLess(transitions[2]["elapsed_ms"], 1200, "Focus loss must release before the original key-up")
        self.assert_note_commands(run, 2, 1)
        self.assertEqual(run.diagnostics["controls"], INITIAL_CONTROLS)
        self.assertEqual(run.saved_bytes, INITIAL_STATE)

    def test_keyboard_audio_apply_retains_all_controls_and_clears_notes(self) -> None:
        run = self.invoke((EXAMPLES / "audio-settings.b3ui").read_text(encoding="ascii"))
        audio = run.diagnostics["audio"]
        self.assertEqual((audio["requested_sample_rate"], audio["sample_rate"]), (96000, 96000))
        self.assertEqual((audio["requested_buffer_frames"], audio["buffer_frames"]), (128, 128))
        self.assertEqual(run.diagnostics["session"]["sample_rate"], 96000)
        self.assertEqual(run.diagnostics["replay"]["device_starts"], 2)
        transitions = self.assert_hold_path(run, [EMPTY_HOLDS, ((), (60,), ()), EMPTY_HOLDS, ((), (60,), ()), EMPTY_HOLDS])
        self.assertGreaterEqual(transitions[2]["elapsed_ms"], 600)
        self.assertLess(transitions[2]["elapsed_ms"], 1300, "Opening Audio must release before Apply restarts it")
        self.assert_note_commands(run, 2, 1)
        self.assertEqual(run.diagnostics["controls"], INITIAL_CONTROLS)
        self.assertEqual(run.saved_bytes, INITIAL_STATE)

    def test_help_open_close_releases_notes_without_retriggering_held_keys(self) -> None:
        events = [(200, "key_down A none 0")] + tap(400, "Slash", "shift")
        events += [(600, "key_down A none 1")] + tap(750, "Return")
        events += [(900, "key_down A none 1"), (1050, "key_up A none"),
                   (1200, "key_down A none 0"), (1350, "key_up A none")]
        events += tap(1500, "Slash", "shift") + tap(1700, "Escape")
        original = replay(2000, events)
        # Opening Help and Escape each submit a scoped release. Return closes
        # the first modal without another command; the suppressed original Up
        # emits no note-off. These literal prefixes include all six commands.
        prefixes = [(0, EMPTY_HOLDS), (200, ((60,), (), ())), (400, EMPTY_HOLDS),
                    (1200, ((60,), (), ())), (1350, EMPTY_HOLDS),
                    (1500, EMPTY_HOLDS), (1700, EMPTY_HOLDS)]
        for duration, commands, on, off in ((2000, 6, 2, 1), (700, 2, 1, 0),
                                          (1000, 2, 1, 0), (1300, 3, 2, 0)):
            with self.subTest(endpoint_ms=duration):
                source = original if duration == 2000 else replay_prefix(original, duration)
                run = self.invoke(source)
                with retain_workflow_failure(run, f"Help endpoint {duration} ms"):
                    self.assert_note_commands(run, on, off)
                    self.assertEqual(run.diagnostics["controls"], INITIAL_CONTROLS)
                    self.assertEqual(run.saved_bytes, INITIAL_STATE)
                    self.assert_command_prefixes(run, prefixes[:commands + 1])

    def test_edit_bank_and_sounding_bank_remain_independent(self) -> None:
        # Literal centers in the default-size Upper cheek: EDIT A (58,508),
        # EDIT B (130,508), preset B (165,590). Tab keeps its semantic UI order;
        # no production layout calculation is reused as an oracle.
        events = [(200, "key_down A none 0")] + click(400, 58, 508)
        events += tabs(500, 14) + tap(800, "End")
        events += click(1000, 165, 590) + click(1200, 130, 508)
        events += tabs(1300, 13) + tap(1600, "Home") + [(1900, "key_up A ctrl+meta")]
        run = self.invoke(replay(2300, events))
        edited_a = deepcopy(INITIAL_CONTROLS)
        edited_a["manual_drawbars"][0][0][0] = 8
        sounding_b = deepcopy(edited_a)
        sounding_b["selected_banks"][0] = 1
        sounding_b["preset_selections"][0] = 11
        sounding_b["route_enabled"][0] = True
        edited_b = deepcopy(sounding_b)
        edited_b["manual_drawbars"][0][1][0] = 0
        transitions = self.assert_control_path(run, [INITIAL_CONTROLS, edited_a, sounding_b, edited_b])
        for item in transitions[1:]:
            self.assertEqual(self.holds(item), ((60,), (), ()), "A control edit must preserve the held key")
        self.assert_hold_path(run, [EMPTY_HOLDS, ((60,), (), ()), EMPTY_HOLDS])
        self.assert_note_commands(run, 1, 1)
        self.assertEqual(run.saved_bytes, INITIAL_STATE)

    def test_cancel_retains_held_notes_and_panic_releases_every_ui_part(self) -> None:
        events = click(200, 165, 590) + [(400, "key_down A none 0")]
        events += tap(600, "F2") + [(700, "key_down S none 0")]
        events += tap(850, "F3") + [(950, "key_down D none 0")]
        events += click(1150, 35, 590)
        # End moves preset focus from C to B without routing; Return reconnects B.
        events += tap(1400, "End") + tap(1500, "Return")
        events += click(1750, 1228, 66)
        events += [(1900, "key_down A none 1"), (1910, "key_down S none 1"),
                   (1920, "key_down D none 1"), (2000, "key_up A none"),
                   (2010, "key_up S none"), (2020, "key_up D none"),
                   (2150, "key_down A none 0"), (2300, "key_up A none")]
        run = self.invoke(replay(2600, events))
        sounding_b = deepcopy(INITIAL_CONTROLS)
        sounding_b["selected_banks"][0] = 1
        sounding_b["preset_selections"][0] = 11
        sounding_b["route_enabled"][0] = True
        cancelled = deepcopy(sounding_b)
        cancelled["route_enabled"][0] = False
        cancelled["preset_selections"][0] = 0
        transitions = self.assert_control_path(run, [INITIAL_CONTROLS, sounding_b, cancelled, sounding_b])
        held_all = ((60,), (62,), (5,))
        self.assertEqual(self.holds(transitions[2]), held_all, "Cancel must preserve every original part")
        self.assertEqual(self.holds(transitions[3]), held_all, "Bank reselection must preserve every original part")
        self.assert_hold_path(run, [EMPTY_HOLDS, ((60,), (), ()), ((60,), (62,), ()), held_all,
                                   EMPTY_HOLDS, ((), (), (1,)), EMPTY_HOLDS])
        self.assert_note_commands(run, 4, 1)
        self.assertEqual(run.saved_bytes, INITIAL_STATE)

    def test_ctrl_save_load_roundtrip_exact_bytes_excludes_transient_notes(self) -> None:
        # The archived input-v2 fixture retains its old four-Tab geometry.
        # Current literal order from EDIT B: twelve presets, then the drawbar.
        events = click(200, 130, 508) + tabs(300, 13) + tap(600, "Home")
        events += [(750, "key_down A none 0")] + tap(1000, "S", "ctrl")
        events += tap(1300, "End") + tap(1600, "O", "ctrl")
        events += [(1900, "key_down A none 1")]
        run = self.invoke(replay(2300, events))
        saved_controls = deepcopy(INITIAL_CONTROLS)
        saved_controls["manual_drawbars"][0][1][0] = 0
        transitions = self.assert_control_path(run, [INITIAL_CONTROLS, saved_controls, INITIAL_CONTROLS, saved_controls])
        self.assertEqual(self.holds(transitions[2]), ((60,), (), ()))
        self.assertEqual(self.holds(transitions[3]), ((60,), (), ()), "Load must not release the existing owner")
        self.assert_hold_path(run, [EMPTY_HOLDS, ((60,), (), ())])
        self.assert_note_commands(run, 1, 0)
        self.assertEqual(run.saved_bytes, SAVED_STATE, "Save must write the complete canonical control-only state")
        reloaded = self.invoke(replay(400, []), state=run.saved_bytes)
        self.assertEqual(reloaded.diagnostics["controls"], saved_controls)
        self.assert_hold_path(reloaded, [EMPTY_HOLDS])
        self.assert_note_commands(reloaded, 0, 0)
        self.assertEqual(reloaded.saved_bytes, SAVED_STATE)

    def test_all_twenty_four_presets_at_minimum_size_preserve_owners(self) -> None:
        for manual, points in enumerate(PRESET_POINTS_MINIMUM):
            for selection, point in enumerate(points):
                with self.subTest(manual=manual, selection=selection):
                    events = tap(50, "F1") + [(100, "key_down A none 0")]
                    events += tap(140, "F2") + [(180, "key_down S none 0")]
                    events += click(350, *point)
                    run = self.invoke(replay(750, events), state=FIXED_STATE,
                                      size=(960, 700), initial_size=(960, 700))
                    with retain_workflow_failure(run, f"Preset manual={manual}, key={selection}"):
                        expected = deepcopy(FIXED_CONTROLS)
                        expected["preset_selections"][manual] = selection
                        expected["route_enabled"][manual] = selection != 0
                        if 1 <= selection <= 9:
                            expected["fixed_registrations"][manual] = selection
                        elif selection >= 10:
                            expected["fixed_registrations"][manual] = 0
                            expected["selected_banks"][manual] = selection - 10
                        self.assertEqual(run.diagnostics["controls"], expected)
                        observed = run.diagnostics["replay"]
                        self.assertEqual(observed["before_shutdown"]["controls"], expected)
                        self.assertEqual(observed["desired_controls_before_shutdown"], expected)
                        self.assertFalse(observed["controls_pending_before_shutdown"])
                        self.assertEqual(self.holds(observed["before_shutdown"]), ((60,), (62,), ()))
                        self.assert_note_commands(run, 2, 0)
                        self.assertEqual(run.saved_bytes, FIXED_STATE, "Preset keys never save implicitly")

    def test_fixed_cancel_save_live_load_cold_load_and_audio_restart(self) -> None:
        events = tap(50, "F1") + [(100, "key_down A none 0")]
        events += tap(140, "F2") + [(180, "key_down D none 0")]
        events += click(450, 35, 590) + click(650, 154, 700)
        events += tap(900, "S", "ctrl")
        events += click(1200, 165, 590) + click(1400, 45, 700)
        events += tap(1700, "O", "ctrl")
        run = self.invoke(replay(2150, events), state=FIXED_STATE)
        expected = deepcopy(FIXED_CONTROLS)
        expected.update(selected_banks=[0, 0], fixed_registrations=[6, 0],
                        preset_selections=[0, 10], route_enabled=[False, True])
        with retain_workflow_failure(run, "Fixed selection live save/load"):
            self.assertEqual(run.diagnostics["controls"], expected)
            self.assertEqual(self.holds(run.diagnostics["replay"]["before_shutdown"]), ((60,), (64,), ()))
            self.assert_note_commands(run, 2, 0)
            self.assertEqual(run.saved_bytes, FIXED_SAVED_STATE)
        cold = self.invoke(replay(400, []), state=run.saved_bytes)
        self.assertEqual(cold.diagnostics["controls"], expected)
        self.assert_hold_path(cold, [EMPTY_HOLDS])
        self.assert_note_commands(cold, 0, 0)
        self.assertEqual(cold.saved_bytes, FIXED_SAVED_STATE)
        restarted = self.invoke((EXAMPLES / "audio-settings.b3ui").read_text(encoding="ascii"),
                                state=run.saved_bytes)
        with retain_workflow_failure(restarted, "Fixed memory across audio restart"):
            self.assertEqual(restarted.diagnostics["controls"], expected)
            self.assertEqual(restarted.diagnostics["replay"]["device_starts"], 2)
            self.assertEqual(restarted.diagnostics["audio"]["sample_rate"], 96000)
            self.assertEqual(restarted.diagnostics["audio"]["buffer_frames"], 128)
            self.assertEqual(self.holds(restarted.diagnostics["replay"]["before_shutdown"]), EMPTY_HOLDS)
            self.assertEqual(restarted.saved_bytes, FIXED_SAVED_STATE)

    def test_resize_preserves_control_focus_and_original_note_release(self) -> None:
        for width, height in ((960, 700), (1600, 1000)):
            with self.subTest(width=width, height=height):
                # Six header controls, two EDIT buttons and twelve presets
                # put the first Upper drawbar at the twenty-first Tab.
                events = tabs(100, 21) + tap(550, "Home")
                events += [(650, "key_down A none 0"), (850, f"resize {width} {height}")]
                events += tap(1050, "Right")
                zero = deepcopy(INITIAL_CONTROLS)
                zero["manual_drawbars"][0][1][0] = 0
                one = deepcopy(zero)
                one["manual_drawbars"][0][1][0] = 1
                held = ((60,), (), ())
                # Literal script prefixes: startup, Home, A-down, Right, A-up.
                # Tabs, resize and modifier changes add no script commands.
                prefixes = {0: (INITIAL_CONTROLS, EMPTY_HOLDS), 1: (zero, EMPTY_HOLDS),
                            2: (zero, held), 3: (one, held), 4: (one, EMPTY_HOLDS)}
                for release in (False, True):
                    with self.subTest(release=release):
                        # The held endpoint is an ordinary replay completion
                        # boundary. It proves the resize/edit retained the note
                        # even if intermediate UI observations were coalesced.
                        source = replay(1600, events + [(1250, "key_up A shift+alt")]) if release else replay(1100, events)
                        run = self.invoke(source, size=(width, height))
                        metadata = run.diagnostics["replay"]
                        final_sequence = metadata["last_submitted_sequence"]
                        # SDL can queue scoped releases during window startup.
                        # Locate this known command suffix without assuming a
                        # fixed number of those harmless initial commands.
                        startup_sequence = final_sequence - (4 if release else 3)
                        evidence = f"Resize release={release}, elapsed={run.elapsed:.3f}s\n{diagnostic_excerpt(run.diagnostics)}"
                        self.assertGreaterEqual(startup_sequence, 1, evidence)
                        previous = 0
                        for observation in [*metadata["observations"], metadata["before_shutdown"]]:
                            sequence = observation["last_applied_sequence"]
                            self.assertIn(sequence, range(1, final_sequence + 1), evidence)
                            self.assertGreaterEqual(sequence, previous, evidence)
                            self.assertEqual(observation["resolved_sequence"], sequence, evidence)
                            submitted = observation.get("last_submitted_sequence", metadata["last_submitted_sequence"])
                            self.assertLessEqual(sequence, submitted, evidence)
                            self.assertLessEqual(submitted, final_sequence, evidence)
                            if "elapsed_ms" in observation and observation["elapsed_ms"] < 500:
                                self.assertEqual(submitted, startup_sequence, evidence)
                            prefix = max(0, sequence - startup_sequence)
                            self.assertEqual((observation["controls"], self.holds(observation)), prefixes[prefix], evidence)
                            previous = sequence
                        self.assertEqual(previous, final_sequence, evidence)
                        self.assertEqual(run.diagnostics["controls"], one, evidence)
                        self.assert_note_commands(run, 1, int(release))
                        self.assertEqual(run.saved_bytes, INITIAL_STATE, evidence)

    def test_off_window_pointer_release_preserves_independent_keyboard_owner(self) -> None:
        source = replay(1400, [
            # Upper C2 (MIDI 36) is inside the reference keyboard at (202,580),
            # to the right of the bank rail and below its accidentals.
            (200, "key_down A none 0"), (450, "mouse_down 202 580"),
            (650, "mouse_move -100 -100"), (800, "mouse_up -80 -80"),
            (1100, "key_up A none"),
        ])
        run = self.invoke(source)
        self.assert_note_commands(run, 2, 2)
        self.assertEqual(run.diagnostics["controls"], INITIAL_CONTROLS)
        holds = consecutive_unique([self.holds(item) for item in run.diagnostics["replay"]["observations"]])
        # Dummy SDL may reject capture and place pointer On/Off in one callback.
        # Both paths must preserve the separate keyboard owner and clean up.
        self.assertIn(holds, [
            [EMPTY_HOLDS, ((60,), (), ()), EMPTY_HOLDS],
            [EMPTY_HOLDS, ((60,), (), ()), ((36, 60), (), ()), ((60,), (), ()), EMPTY_HOLDS],
        ])
        transitions = self.assert_hold_path(run, holds)
        self.assertGreaterEqual(transitions[-1]["elapsed_ms"], 1100,
                                "Pointer cleanup must not perform the later keyboard release")
        self.assertEqual(self.holds(run.diagnostics["replay"]["before_shutdown"]), EMPTY_HOLDS)
        self.assertEqual(run.saved_bytes, INITIAL_STATE)


if __name__ == "__main__":
    unittest.main(verbosity=2)
