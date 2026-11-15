#!/usr/bin/env python3
"""Independent calibration-state observations from the real native executable.

These bounded SDL dummy runs inspect public diagnostics, not a private decoder
or transport stand-in. No MIDI hardware is enumerated or opened. The separate
MIDI replay suite owns musical/controller acceptance; this gate distinguishes
selected, configured, pending, active and retained pre-shutdown settings.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from test_standalone_app import (
    DEFAULT_EXPRESSION_OBSERVATION, REPLAY_EXPRESSION_FIELDS, SCHEMA,
    VARIED_CONTROLS, assert_expression_calibration, assert_presentation,
    assert_schema, diagnostic_excerpt, reject_nonfinite, state_document,
    unique_object,
)
from test_standalone_midi_replay import (
    MIDI_REPLAY_SCHEMA, UI_REPLAY_SCHEMA, replay_schema,
)


CALIBRATION = {"minimum": 10, "maximum": 115, "inverted": True}
CHANNELS = {"upper": 1, "lower": 2, "pedals": 3}


def script(magic: str, duration: int, events: list[tuple[int, str]]) -> bytes:
    return (f"{magic}\nduration_ms {duration}\n" + "".join(
        f"{at} {event}\n" for at, event in events)).encode("ascii")


def tap(at: int, key: str, modifiers: str = "none") -> list[tuple[int, str]]:
    return [(at, f"key_down {key} {modifiers} 0"), (at + 4, f"key_up {key} {modifiers}")]


def tabs(at: int, count: int) -> list[tuple[int, str]]:
    return [event for index in range(count) for event in tap(at + 10 * index, "Tab")]


def complete_replay_schema(value: dict, template: dict) -> dict:
    # Retain all the existing exact replay fields, and extend each observation
    # with the reviewed public diagnostics fields. No dictionary wildcard.
    result = replay_schema(value, template)
    for observation in result["observations"]:
        observation.update(REPLAY_EXPRESSION_FIELDS)
    return result


class CalibrationDiagnosticAdmission(unittest.TestCase):
    def test_strict_checker_rejects_malformed_or_contradictory_records(self) -> None:
        baseline = {**deepcopy(DEFAULT_EXPRESSION_OBSERVATION), "pre_shutdown_active": None}
        assert_expression_calibration(self, baseline, final=True,
                                      active=False, pre_shutdown_active=False)
        mutations = []

        def altered(path: tuple[str, ...], value: object) -> None:
            candidate = deepcopy(baseline)
            parent = candidate
            for name in path[:-1]:
                parent = parent[name]
            parent[path[-1]] = value
            mutations.append(candidate)

        altered(("configured", "minimum"), False)
        altered(("configured", "minimum"), -1)
        altered(("configured", "maximum"), 128)
        altered(("configured", "maximum"), 0)
        altered(("configured", "inverted"), 1)
        altered(("selected", "maximum"), 0)  # selected_valid cannot remain true.
        altered(("selected_valid",), False)
        altered(("active",), CALIBRATION)
        altered(("pre_shutdown_active",), CALIBRATION)
        altered(("reconnect_pending",), True)
        altered(("model",), "unidentified")
        altered(("unexpected",), 1)
        missing = deepcopy(baseline)
        del missing["selected"]
        mutations.append(missing)
        for index, candidate in enumerate(mutations):
            with self.subTest(index=index), self.assertRaises(AssertionError):
                assert_expression_calibration(self, candidate, final=True,
                                              active=False, pre_shutdown_active=False)

        pending = deepcopy(DEFAULT_EXPRESSION_OBSERVATION)
        pending.update(reconnect_pending=True, release_pending=True, pending={
            "port": "", "synthetic": True, "channels": CHANNELS,
            "calibration": CALIBRATION,
        })
        assert_expression_calibration(self, pending)
        bad_pending = []
        for field, value in (("port", "unexpected hardware"), ("synthetic", 1)):
            candidate = deepcopy(pending)
            candidate["pending"][field] = value
            bad_pending.append(candidate)
        for channel in (0, 1, 17, True):
            candidate = deepcopy(pending)
            candidate["pending"]["channels"]["lower"] = channel
            bad_pending.append(candidate)
        candidate = deepcopy(pending)
        candidate["pending"]["calibration"]["minimum"] = 115
        bad_pending.append(candidate)
        for index, candidate in enumerate(bad_pending):
            with self.subTest(pending=index), self.assertRaises(AssertionError):
                assert_expression_calibration(self, candidate)


class NativeExpressionDiagnostics(unittest.TestCase):
    invocations = 0

    @classmethod
    def setUpClass(cls) -> None:
        configured = os.environ.get("HAMMOND_STANDALONE_EXECUTABLE", "")
        if not configured:
            raise RuntimeError("HAMMOND_STANDALONE_EXECUTABLE is required; build the native app first")
        cls.executable = Path(configured).resolve(strict=True)
        if not cls.executable.is_file() or not os.access(cls.executable, os.X_OK):
            raise RuntimeError(f"Native executable is not executable: {cls.executable}")
        cls.binary_hash = hashlib.sha256(cls.executable.read_bytes()).hexdigest()
        print(f"Expression diagnostics executable SHA-256: {cls.binary_hash}", flush=True)

    @classmethod
    def tearDownClass(cls) -> None:
        print(f"Actual expression diagnostics subprocesses: {cls.invocations}", flush=True)
        if hashlib.sha256(cls.executable.read_bytes()).hexdigest() != cls.binary_hash:
            raise AssertionError("Native executable changed during diagnostics acceptance")

    def execute(self, *, midi: list[tuple[int, str]] | None = None,
                ui: list[tuple[int, str]] | None = None, duration: int = 1000) -> dict:
        with tempfile.TemporaryDirectory(prefix="hammond-expression-diagnostics-") as temporary:
            root = Path(temporary)
            state, output = root / "original.b3controls", root / "diagnostics.json"
            original = state_document()
            state.write_bytes(original)
            command = [str(self.executable), "--state", str(state), "--diagnostics", str(output),
                       "--width", "960", "--height", "700", "--expression-min", "10",
                       "--expression-max", "115", "--expression-invert"]
            expected_files = {"original.b3controls", "diagnostics.json"}
            if midi is None:
                self.assertIsNone(ui)
                command += ["--smoke-ms", "600"]
            else:
                midi_path = root / "midi.txt"
                midi_source = script("B3MIDIREPLAY1", duration, midi)
                midi_path.write_bytes(midi_source)
                command += ["--midi-script", str(midi_path)]
                expected_files.add("midi.txt")
                if ui is not None:
                    ui_path = root / "ui.txt"
                    ui_source = script("B3UIREPLAY1", duration, ui)
                    ui_path.write_bytes(ui_source)
                    command += ["--input-script", str(ui_path)]
                    expected_files.add("ui.txt")
            environment = dict(os.environ, SDL_AUDIODRIVER="dummy", SDL_VIDEODRIVER="dummy")
            self.__class__.invocations += 1
            process = subprocess.run(command, cwd=root, env=environment, stdin=subprocess.DEVNULL,
                                     capture_output=True, text=True, encoding="utf-8", errors="replace",
                                     timeout=10, check=False)
            self.assertEqual(process.returncode, 0, process.stderr + "\n" + diagnostic_excerpt(output))
            self.assertEqual(process.stderr, "")
            self.assertEqual(state.read_bytes(), original)
            self.assertEqual({path.name for path in root.iterdir()}, expected_files)
            if midi is not None:
                self.assertEqual(midi_path.read_bytes(), midi_source)
                if ui is not None:
                    self.assertEqual(ui_path.read_bytes(), ui_source)
            report = json.loads(output.read_text(encoding="utf-8"), object_pairs_hook=unique_object,
                                parse_constant=reject_nonfinite)

        schema = dict(SCHEMA)
        if midi is not None:
            schema["midi_replay"] = complete_replay_schema(report["midi_replay"], MIDI_REPLAY_SCHEMA)
            if ui is not None:
                schema["replay"] = complete_replay_schema(report["replay"], UI_REPLAY_SCHEMA)
        assert_schema(self, report, schema)
        self.assertEqual(report["schema_version"], 3)
        self.assertEqual(report["application"], "hammond_standalone")
        self.assertEqual(report["controls"], VARIED_CONTROLS,
                         "Connection or editing adapter settings must not change musical controls")
        self.assertEqual(report["errors"]["count"], 0)
        self.assertEqual(report["runtime"]["video_driver"], "dummy")
        self.assertGreater(report["runtime"]["rendered_images"], 0)
        self.assertEqual(report["audio"]["driver"], "dummy")
        self.assertGreater(report["audio"]["callback_count"], 0)
        self.assertFalse(report["session"]["running_after_shutdown"])
        self.assertFalse(report["session"]["held_after_shutdown"])
        transport = report["midi"]
        self.assertFalse(transport["active_after_shutdown"])
        self.assertEqual(transport["requested_port"], "")
        self.assertEqual(transport["generation"], 0)
        self.assertTrue(all(value == 0 for value in transport["device"].values()))
        self.assertEqual(transport["discovery"]["requests"], 0)
        assert_expression_calibration(self, transport["expression_calibration"], final=True,
                                      active=transport["active_after_shutdown"],
                                      pre_shutdown_active=transport["active_before_shutdown"])
        assert_presentation(self, report)
        for section in ("replay", "midi_replay"):
            if section not in report:
                continue
            replay = report[section]
            self.assertTrue(replay["completed"])
            self.assertTrue(replay["passed"])
            self.assertTrue(replay["final_acknowledged"])
            self.assertFalse(replay["observations_truncated"])
            for observation in replay["observations"]:
                self.assertIn(observation["overlay"], ("none", "help", "audio", "midi"))
                self.assertGreaterEqual(observation["modal_focus"], 0)
                self.assertLess(observation["modal_focus"], 11)
                self.assertEqual(observation["error_count"], 0)
                assert_expression_calibration(self, observation["expression_calibration"])
        return report

    def test_configured_inverted_interval_is_inactive_without_an_epoch(self) -> None:
        report = self.execute()
        calibration = report["midi"]["expression_calibration"]
        self.assertEqual(calibration["configured"], CALIBRATION)
        self.assertEqual(calibration["selected"], CALIBRATION)
        self.assertIsNone(calibration["active"])
        self.assertIsNone(calibration["pre_shutdown_active"])
        self.assertIsNone(calibration["pending"])
        self.assertEqual(report["midi"]["decoder"]["epochs"], 0)

    def test_selected_edits_and_invalid_pair_remain_distinct_from_active_epoch(self) -> None:
        ui = (tap(150, "M", "ctrl") + tabs(200, 5) + tap(270, "Right") +
              tap(350, "Escape") + tap(430, "M", "ctrl") + tabs(480, 6) + tap(580, "Home"))
        report = self.execute(midi=[(80, "connect")], ui=ui)
        calibration = report["midi"]["expression_calibration"]
        invalid = {"minimum": 10, "maximum": 0, "inverted": True}
        edited = {"minimum": 11, "maximum": 115, "inverted": True}
        self.assertEqual(calibration["configured"], CALIBRATION)
        self.assertEqual(calibration["selected"], invalid)
        self.assertFalse(calibration["selected_valid"])
        self.assertIsNone(calibration["active"])
        self.assertEqual(calibration["pre_shutdown_active"], CALIBRATION)
        observations = report["midi_replay"]["observations"]
        edited_indices = [index for index, item in enumerate(observations)
                          if item["expression_calibration"]["selected"] == edited]
        invalid_indices = [index for index, item in enumerate(observations)
                           if item["expression_calibration"]["selected"] == invalid]
        self.assertTrue(edited_indices)
        self.assertTrue(invalid_indices)
        # Main-thread stalls may deliver several due events in one turn. Their
        # retained order, rather than wall-clock windows, proves reopening reset.
        self.assertTrue(any(item["overlay"] == "midi" and
                            item["expression_calibration"]["selected"] == CALIBRATION
                            for item in observations[edited_indices[0] + 1:invalid_indices[0]]))
        active_records = [item["expression_calibration"] for item in observations
                          if item["expression_calibration"]["active"] is not None]
        self.assertTrue(active_records)
        for value in active_records:
            self.assertEqual(value["active"], CALIBRATION)
            self.assertEqual(value["configured"], CALIBRATION)
        self.assertTrue(any(value["selected"] == invalid and not value["selected_valid"]
                            for value in active_records))
        painted = report["presentation"]["last_painted"]
        self.assertEqual(painted["overlay"], "midi")
        self.assertEqual(painted["modal_focus"], 6)
        self.assertEqual(painted["expression_calibration"]["selected"], invalid)
        self.assertEqual(painted["expression_calibration"]["active"], CALIBRATION)
        self.assertEqual(report["midi"]["decoder"]["epochs"], 1)
        self.assertEqual(report["midi"]["parameter_messages"], 0)

    def test_reconnect_copies_pending_request_and_retirement_reports_inactive(self) -> None:
        report = self.execute(midi=[(80, "connect"), (220, "connect"), (500, "disconnect")])
        calibration = report["midi"]["expression_calibration"]
        self.assertEqual(calibration["configured"], CALIBRATION)
        self.assertIsNone(calibration["active"])
        self.assertIsNone(calibration["pre_shutdown_active"])
        self.assertIsNone(calibration["pending"])
        self.assertEqual(report["midi"]["decoder"]["epochs"], 2)
        self.assertEqual(report["midi_replay"]["connections_started"], 2)
        records = [item["expression_calibration"] for item in report["midi_replay"]["observations"]]
        pending = [item for item in records if item["pending"] is not None]
        self.assertTrue(pending, "The retained observation must expose the copied reconnect request")
        for item in pending:
            self.assertTrue(item["reconnect_pending"])
            self.assertTrue(item["release_pending"])
            self.assertIsNone(item["active"])
            self.assertEqual(item["pending"], {
                "port": "", "synthetic": True, "channels": CHANNELS, "calibration": CALIBRATION,
            })
        self.assertTrue(any(item["active"] == CALIBRATION for item in records))
        self.assertIsNone(records[-1]["active"])
        self.assertEqual(report["midi"]["parameter_messages"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
