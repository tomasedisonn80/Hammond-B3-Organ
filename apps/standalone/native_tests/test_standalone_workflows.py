#!/usr/bin/env python3
"""Independent musical workflows through the real standalone SDL event loop.

Requires HAMMOND_STANDALONE_EXECUTABLE; absence is a failed prerequisite.
All runs explicitly use SDL dummy drivers and private state/output paths.
Expected musical controls, note identities and saved bytes are literal oracles.
No UiModel, replay parser, Engine, or production serializer is imported.
"""

from __future__ import annotations

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


REPOSITORY = Path(__file__).resolve().parents[3]
EXAMPLES = REPOSITORY / "examples" / "standalone-input"
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
    "selected_banks": [0, 1],
    "route_enabled": [False, True],
    "expression": 0.375,
    "pedal_drawbars": [2, 7],
    "percussion": {"enabled": True, "harmonic": 1, "volume": 1, "decay": 1},
}

SAVED_STATE = b"""B3CONTROLS3
expression 0.375
percussion enabled 1 harmonic third volume soft decay fast
pedal drawbars 2 7
manual upper selected A route_enabled 0
bank A 0 1 2 3 4 5 6 7 8
bank B 0 7 6 5 4 3 2 1 0
manual lower selected B route_enabled 1
bank A 1 3 5 7 0 2 4 6 8
bank B 8 6 4 2 0 7 5 3 1
end
"""

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
               size: tuple[int, int] = (1280, 900)) -> WorkflowRun:
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
                 "--diagnostics", str(diagnostics_path)],
                cwd=directory, env=environment, stdin=subprocess.DEVNULL,
                capture_output=True, text=True, errors="replace", timeout=PROCESS_TIMEOUT, check=False,
            )
        except subprocess.TimeoutExpired as error:
            self.fail(f"Native replay exceeded {PROCESS_TIMEOUT}s: {error}")
        elapsed = time.monotonic() - started
        self.assertEqual(process.returncode, 0,
                         f"Native workflow failed ({elapsed:.3f}s):\n{process.stdout}\n{process.stderr}")
        duration_seconds = int(source.splitlines()[1].split()[1]) / 1000.0
        self.assertGreaterEqual(elapsed, duration_seconds - 0.04,
                                "A completed replay must reach its declared duration")
        self.assertEqual(process.stderr, "", f"Unexpected application errors: {process.stderr}")
        self.assertTrue(diagnostics_path.is_file(), "Successful replay must write requested diagnostics")
        data = json.loads(diagnostics_path.read_text(encoding="utf-8"),
                          object_pairs_hook=unique_object, parse_constant=reject_nonfinite)
        self.assert_common(data, source, state_path, size)
        self.assertEqual(script_path.read_text(encoding="ascii"), source, "Replay must not modify its input")
        self.assertEqual({path.name for path in directory.iterdir()},
                         {state_path.name, script_path.name, diagnostics_path.name},
                         "The workflow must not leave temporary saves or unexpected files")
        return WorkflowRun(data, state_path.read_bytes(), elapsed)

    def assert_common(self, data: dict, source: str, state_path: Path, size: tuple[int, int]) -> None:
        self.assertEqual(data["schema_version"], 1)
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
        # Only the replay object is new. Ordinary schema-1 diagnostics retain
        # their original meaning, including joined shutdown observations.
        metadata = data["replay"]
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
        run = self.invoke((EXAMPLES / "keyboard-notes.b3ui").read_text(encoding="ascii"))
        transitions = self.assert_hold_path(run, [
            EMPTY_HOLDS, ((60,), (), ()), ((60,), (74,), ()), ((60,), (74,), (17,)),
            ((), (74,), (17,)), ((), (), (17,)), EMPTY_HOLDS, ((72,), (), ()), EMPTY_HOLDS,
        ])
        # No target/octave change may perform one of these original releases.
        for index, earliest in ((4, 1500), (5, 1700), (6, 1900), (8, 2300)):
            self.assertGreaterEqual(transitions[index]["elapsed_ms"], earliest)
        self.assert_note_commands(run, 4, 4)
        self.assertEqual(run.diagnostics["controls"], INITIAL_CONTROLS)
        self.assertGreater(run.diagnostics["session"]["maximum_observed_peak"], 0)
        self.assertEqual(run.saved_bytes, INITIAL_STATE)

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
        run = self.invoke(replay(2000, events))
        transitions = self.assert_hold_path(run, [EMPTY_HOLDS, ((60,), (), ()), EMPTY_HOLDS, ((60,), (), ()), EMPTY_HOLDS])
        self.assertGreaterEqual(transitions[2]["elapsed_ms"], 400)
        self.assertLess(transitions[2]["elapsed_ms"], 750, "Opening Help must release while Help remains open")
        self.assert_note_commands(run, 2, 1)
        self.assertEqual(run.diagnostics["controls"], INITIAL_CONTROLS)
        self.assertEqual(run.saved_bytes, INITIAL_STATE)

    def test_edit_bank_and_sounding_bank_remain_independent(self) -> None:
        # Centers of real default-size buttons; Tab navigates their public UI
        # order. No production layout calculation is reused as an oracle.
        events = [(200, "key_down A none 0")] + click(400, 76, 136)
        events += tabs(500, 5) + tap(700, "End")
        events += click(1000, 343, 136) + click(1200, 165, 136)
        events += tabs(1300, 4) + tap(1500, "Home") + [(1900, "key_up A ctrl+meta")]
        run = self.invoke(replay(2300, events))
        edited_a = deepcopy(INITIAL_CONTROLS)
        edited_a["manual_drawbars"][0][0][0] = 8
        sounding_b = deepcopy(edited_a)
        sounding_b["selected_banks"][0] = 1
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
        events = click(200, 343, 136) + [(400, "key_down A none 0")]
        events += tap(600, "F2") + [(700, "key_down S none 0")]
        events += tap(850, "F3") + [(950, "key_down D none 0")]
        events += click(1150, 432, 136)
        # Shift+Tab from Cancel focuses Sounding B; Return reconnects it.
        events += tap(1400, "Tab", "shift") + tap(1500, "Return")
        events += click(1750, 1208, 52)
        events += [(1900, "key_down A none 1"), (1910, "key_down S none 1"),
                   (1920, "key_down D none 1"), (2000, "key_up A none"),
                   (2010, "key_up S none"), (2020, "key_up D none"),
                   (2150, "key_down A none 0"), (2300, "key_up A none")]
        run = self.invoke(replay(2600, events))
        sounding_b = deepcopy(INITIAL_CONTROLS)
        sounding_b["selected_banks"][0] = 1
        sounding_b["route_enabled"][0] = True
        cancelled = deepcopy(sounding_b)
        cancelled["route_enabled"][0] = False
        transitions = self.assert_control_path(run, [INITIAL_CONTROLS, sounding_b, cancelled, sounding_b])
        held_all = ((60,), (62,), (5,))
        self.assertEqual(self.holds(transitions[2]), held_all, "Cancel must preserve every original part")
        self.assertEqual(self.holds(transitions[3]), held_all, "Bank reselection must preserve every original part")
        self.assert_hold_path(run, [EMPTY_HOLDS, ((60,), (), ()), ((60,), (62,), ()), held_all,
                                   EMPTY_HOLDS, ((), (), (1,)), EMPTY_HOLDS])
        self.assert_note_commands(run, 4, 1)
        self.assertEqual(run.saved_bytes, INITIAL_STATE)

    def test_ctrl_save_load_roundtrip_exact_bytes_excludes_transient_notes(self) -> None:
        run = self.invoke((EXAMPLES / "save-controls.b3ui").read_text(encoding="ascii"))
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

    def test_resize_preserves_control_focus_and_original_note_release(self) -> None:
        for width, height in ((960, 700), (1600, 1000)):
            with self.subTest(width=width, height=height):
                # Header Save through Upper's first drawbar is eleven Tabs.
                events = tabs(200, 11) + tap(500, "Home")
                events += [(650, "key_down A none 0"), (850, f"resize {width} {height}")]
                events += tap(1050, "Right") + [(1250, "key_up A shift+alt")]
                run = self.invoke(replay(1600, events), size=(width, height))
                zero = deepcopy(INITIAL_CONTROLS)
                zero["manual_drawbars"][0][1][0] = 0
                one = deepcopy(zero)
                one["manual_drawbars"][0][1][0] = 1
                transitions = self.assert_control_path(run, [INITIAL_CONTROLS, zero, one])
                self.assertEqual(self.holds(transitions[2]), ((60,), (), ()),
                                 "The note must remain held through resize and the following focused edit")
                self.assert_hold_path(run, [EMPTY_HOLDS, ((60,), (), ()), EMPTY_HOLDS])
                self.assert_note_commands(run, 1, 1)
                self.assertEqual(run.saved_bytes, INITIAL_STATE)

    def test_off_window_pointer_release_preserves_independent_keyboard_owner(self) -> None:
        source = replay(1400, [
            (200, "key_down A none 0"), (450, "mouse_down 45 520"),
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
