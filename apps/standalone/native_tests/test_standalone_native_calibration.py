#!/usr/bin/env python3
"""Native calibration lifecycle through the real app and a test-only MIDI SDK.

The fixture recompiles unchanged main.cpp/MidiDevice.cpp, uses real SDL dummy
audio callbacks and the real UI replay, and substitutes only the native MIDI
dependency. Independent public observations and a calibrated dependency trace
qualify the native connection path without claiming hardware or driver timing.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from test_standalone_app import (
    ArraySchema, SCHEMA, assert_expression_calibration, assert_presentation,
    assert_schema, reject_nonfinite, unique_object,
)
from test_standalone_midi_replay import (
    DEFAULT_CONTROLS, UI_REPLAY_SCHEMA, click, held, replay_schema, script, tap, tabs,
)


OLD = {"minimum": 10, "maximum": 110, "inverted": False}
NEW = {"minimum": 20, "maximum": 100, "inverted": True}
CHANNELS = {"upper": 1, "lower": 2, "pedals": 3}
NEW_CHANNELS = {"upper": 4, "lower": 5, "pedals": 6}
INITIAL_HELD = ((60,), (64,), (3,))
FRESH_HELD = ((67,), (), ())
EMPTY_HELD = ((), (), ())
STATE = b"""B3CONTROLS3
expression 0.375
percussion enabled 0 harmonic second volume normal decay slow
pedal drawbars 8 0
manual upper selected B route_enabled 1
bank A 0 0 0 0 0 0 0 0 0
bank B 8 8 8 0 0 0 0 0 0
manual lower selected B route_enabled 1
bank A 0 0 0 0 0 0 0 0 0
bank B 0 0 8 0 0 0 0 0 0
end
"""
CONTROL_ORACLE = {**deepcopy(DEFAULT_CONTROLS), "expression": 0.375}
TRACE_COUNTS = {
    name: int for name in (
        "constructions", "destructions", "opens", "closes", "cancellations",
        "offered_messages", "delivered_messages", "errors", "cancelled_while_open",
        "destroyed_while_open", "destroyed_with_input_callback", "invalid_callbacks",
        "dropped_events",
    )
}
TRACE_EVENT = {
    "sequence": int, "operation": str, "client": int, "transport": bool,
    "open_attempt": int, "poll": int, "port": int, "registered": bool,
    "worker": bool, "bytes": [int, int, int],
}
TRACE_SCHEMA = {
    "schema_version": int, "fixture_id": str, "scenario": str, "application_exit": int,
    "production_lifecycle": bool, "physical_backend": bool, "callback_schedule": str,
    "counts": TRACE_COUNTS, "events": ArraySchema(TRACE_EVENT),
}


def calibration_edit(*, apply_at: int = 1600) -> list[tuple[int, str]]:
    """Literal keyboard actions; endpoint and output oracles remain independent."""
    events = tap(300, "M", "ctrl") + tabs(1000, 5)
    for index in range(10):
        events += tap(1060 + 12 * index, "Right")
    events += tap(1200, "Tab")
    for index in range(10):
        events += tap(1220 + 12 * index, "Left")
    events += tap(1360, "Tab") + tap(1380, "End") + tap(1400, "Tab")
    return events + tap(apply_at, "Return")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object,
                      parse_constant=reject_nonfinite)


class NativeCalibrationLifecycle(unittest.TestCase):
    invocations = 0
    native_cases = 0
    negative_replays = 0
    retained = []

    @classmethod
    def setUpClass(cls) -> None:
        configured = os.environ.get("HAMMOND_STANDALONE_CALIBRATION_PROBE", "")
        if not configured:
            raise RuntimeError("HAMMOND_STANDALONE_CALIBRATION_PROBE is required; build the native fixture")
        cls.executable = Path(configured).resolve(strict=True)
        if not cls.executable.is_file() or not os.access(cls.executable, os.X_OK):
            raise RuntimeError(f"Calibration fixture is not executable: {cls.executable}")
        cls.binary_hash = hashlib.sha256(cls.executable.read_bytes()).hexdigest()
        cls.evidence = Path(os.environ["HAMMOND_NATIVE_CALIBRATION_EVIDENCE"]).resolve() \
            if os.environ.get("HAMMOND_NATIVE_CALIBRATION_EVIDENCE") else None
        if cls.evidence:
            cls.evidence.mkdir(parents=True, exist_ok=True)
        print(f"Native calibration fixture SHA-256: {cls.binary_hash}", flush=True)

    @classmethod
    def tearDownClass(cls) -> None:
        print(f"Actual calibration fixture subprocesses: {cls.invocations}; "
              f"native lifecycles: {cls.native_cases}; deliberately failed replays: {cls.negative_replays}",
              flush=True)
        if hashlib.sha256(cls.executable.read_bytes()).hexdigest() != cls.binary_hash:
            raise AssertionError("Calibration fixture changed during acceptance")
        if cls.evidence:
            source_root = Path(__file__).resolve().parents[3]
            paths = (
                "apps/standalone/main.cpp", "apps/standalone/MidiDevice.cpp", "apps/standalone/MidiDevice.h",
                "apps/standalone/MidiInput.cpp", "apps/standalone/MidiInput.h", "apps/standalone/Session.cpp",
                "apps/standalone/Session.h", "apps/standalone/UiModel.cpp", "apps/standalone/UiModel.h",
                "apps/standalone/native_tests/calibration_lifecycle_driver.cpp",
                "apps/standalone/native_tests/fake_calibration/RtMidi.h",
                "apps/standalone/native_tests/test_standalone_native_calibration.py",
                "apps/standalone/native_tests/test_standalone_app.py",
                "apps/standalone/native_tests/test_standalone_midi_replay.py",
            )
            report = {"schema_version": 1, "fixture_id": "native-calibration-dependency-v1",
                      "binary_sha256": cls.binary_hash, "subprocesses": cls.invocations,
                      "native_lifecycles": cls.native_cases, "deliberately_failed_replays": cls.negative_replays,
                      "cases": cls.retained, "source_sha256": {
                          name: hashlib.sha256((source_root / name).read_bytes()).hexdigest() for name in paths},
                      "boundary": "Real application/adapter and SDL dummy callbacks; substituted MIDI dependency, synchronous callback offers, no hardware or driver timing qualification"}
            (cls.evidence / "summary.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")

    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="hammond-native-calibration-")
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)

    def invoke(self, scenario: str | None, arguments: list[str]) -> subprocess.CompletedProcess:
        environment = dict(os.environ, SDL_AUDIODRIVER="dummy", SDL_VIDEODRIVER="dummy",
                           HAMMOND_CALIBRATION_TRACE=str(self.directory / "dependency.json"))
        environment.pop("HAMMOND_CALIBRATION_SCENARIO", None)
        if scenario is not None:
            environment["HAMMOND_CALIBRATION_SCENARIO"] = scenario
        self.__class__.invocations += 1
        return subprocess.run([str(self.executable), *arguments], cwd=self.directory, env=environment,
                              stdin=subprocess.DEVNULL, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=15, check=False)

    def validate_trace(self, trace: dict, scenario: str, *, live: bool) -> None:
        assert_schema(self, trace, TRACE_SCHEMA)
        self.assertEqual(trace["schema_version"], 1)
        self.assertEqual(trace["fixture_id"], "native-calibration-dependency-v1")
        self.assertEqual(trace["scenario"], scenario)
        self.assertTrue(trace["production_lifecycle"])
        self.assertFalse(trace["physical_backend"])
        self.assertEqual(trace["callback_schedule"], "synchronous-native-api-boundaries")
        counts, events = trace["counts"], trace["events"]
        self.assertLessEqual(len(events), 4096)
        self.assertEqual(counts["constructions"], counts["destructions"])
        self.assertEqual(counts["opens"], counts["closes"])
        self.assertEqual(counts["opens"], counts["cancellations"])
        self.assertEqual(counts["offered_messages"], counts["delivered_messages"])
        for name in ("cancelled_while_open", "destroyed_while_open", "destroyed_with_input_callback",
                     "invalid_callbacks", "dropped_events"):
            self.assertEqual(counts[name], 0, name)
        self.assertEqual([event["sequence"] for event in events], list(range(1, len(events) + 1)))
        for event in events:
            if event["transport"]:
                self.assertFalse(event["worker"], "this fixture's callback offers are synchronous on the app thread")
            if event["operation"] == "message":
                self.assertTrue(event["registered"])
                self.assertEqual(len(event["bytes"]), 3)
                self.assertGreaterEqual(event["bytes"][0], 128)
                self.assertTrue(all(0 <= value <= 127 for value in event["bytes"][1:]))
        if live:
            self.assertTrue(any(event["operation"] == "construct" and event["worker"]
                                and not event["transport"] for event in events), "real discovery worker did not run")
        opens = [event for event in events if event["operation"] == "open"]
        self.assertEqual(len(opens), counts["opens"])
        previous_destroy = 0
        for ordinal, opening in enumerate(opens, 1):
            self.assertEqual(opening["open_attempt"], ordinal)
            self.assertGreater(opening["sequence"], previous_destroy)
            client = [event for event in events if event["client"] == opening["client"]]
            one = lambda operation: next(event for event in client if event["operation"] == operation)
            closed, cancelled, destroyed = (one(name) for name in ("closed", "cancel", "destroy"))
            self.assertLess(one("close")["sequence"], closed["sequence"])
            self.assertLess(closed["sequence"], cancelled["sequence"])
            self.assertLess(cancelled["sequence"], destroyed["sequence"])
            self.assertFalse(destroyed["registered"])
            previous_destroy = destroyed["sequence"]
            offered_during_close = [event for event in client if event["operation"] == "message"
                                    and one("close")["sequence"] < event["sequence"] < closed["sequence"]]
            self.assertEqual([event["bytes"] for event in offered_during_close],
                             [[0xB0, 11, 127], [0x90, 75, 100]])

    def run_case(self, scenario: str, events: list[tuple[int, str]], duration: int, *,
                 connected: bool = True, expected_exit: int = 0) -> tuple[dict, dict]:
        self.__class__.native_cases += 1
        if expected_exit:
            self.__class__.negative_replays += 1
        state = self.directory / "original.b3controls"
        ui = self.directory / "input.b3ui"
        diagnostics = self.directory / "diagnostics.json"
        ui_bytes = script("B3UIREPLAY1", duration, events)
        state.write_bytes(STATE)
        ui.write_bytes(ui_bytes)
        arguments = ["--state", str(state), "--input-script", str(ui), "--diagnostics", str(diagnostics),
                     "--width", "960", "--height", "700", "--expression-min", "10", "--expression-max", "110"]
        if connected:
            arguments += ["--midi-port", "Controller"]
        process = self.invoke(scenario, arguments)
        try:
            self.assertEqual(process.returncode, expected_exit, process.stderr)
            self.assertEqual(process.stdout, "")
            if expected_exit == 0:
                self.assertEqual(process.stderr, "")
            else:
                self.assertIn("Native input replay failed", process.stderr)
            self.assertEqual(state.read_bytes(), STATE)
            self.assertEqual(ui.read_bytes(), ui_bytes)
            self.assertEqual({path.name for path in self.directory.iterdir()},
                             {"original.b3controls", "input.b3ui", "diagnostics.json", "dependency.json"})
            data, trace = read_json(diagnostics), read_json(self.directory / "dependency.json")
            schema = {**SCHEMA, "replay": replay_schema(data["replay"], UI_REPLAY_SCHEMA)}
            assert_schema(self, data, schema)
            self.validate_trace(trace, scenario, live=True)
            self.assertEqual(trace["application_exit"], expected_exit)
            assert_presentation(self, data)
            self.assertEqual(data["runtime"]["video_driver"], "dummy")
            self.assertEqual(data["runtime"]["renderer"], "software")
            self.assertEqual(data["audio"]["driver"], "dummy")
            self.assertGreater(data["audio"]["callback_count"], 0)
            self.assertGreater(data["runtime"]["rendered_images"], 0)
            for name in ("render_failures", "format_failures", "nonfinite_failures", "overrange_failures"):
                self.assertEqual(data["audio"][name], 0, name)
            self.assertEqual(data["session"]["fault_flags"], 0)
            self.assertEqual(data["session"]["recovery_count"], 0)
            self.assertFalse(data["session"]["held_after_shutdown"])
            self.assertFalse(data["session"]["running_after_shutdown"])
            midi = data["midi"]
            self.assertEqual(midi["source"], "native")
            self.assertTrue(midi["backend_available"])
            self.assertEqual(midi["arrival_time_source"], "native_callback_receipt")
            self.assertTrue(midi["active_before_shutdown"])
            self.assertFalse(midi["active_after_shutdown"])
            self.assertTrue(midi["quiescent_after_shutdown"])
            self.assertTrue(midi["diagnostics_stable_after_shutdown"])
            self.assertFalse(midi["startup_failed"])
            self.assertFalse(midi["shutdown_failed"])
            self.assertEqual(midi["state_before_shutdown"], "open")
            self.assertEqual(midi["state_after_shutdown"], "closed")
            self.assertEqual(midi["submit_failures"], 0)
            self.assertEqual(midi["session_recoveries_observed"], 0)
            self.assertEqual(midi["release_commands_accepted"], 3 * midi["release_batches"])
            self.assertEqual(midi["discovery"]["started"], midi["discovery"]["completed"])
            self.assertEqual(midi["discovery"]["failures"], 0)
            self.assertFalse(midi["discovery"]["pending_after_shutdown"])
            self.assertEqual(midi["device"]["close_errors"], 0)
            self.assertEqual(midi["device"]["callback_contentions"], 0)
            self.assertEqual(midi["device"]["callback_messages"], trace["counts"]["delivered_messages"])
            self.assertEqual(midi["device"]["admission_failures"], 2 * trace["counts"]["closes"])
            self.assertEqual(midi["device"]["forwarded_messages"],
                             trace["counts"]["delivered_messages"] - midi["device"]["admission_failures"])
            self.assertEqual(midi["device"]["filtered_messages"], 0)
            self.assertEqual(midi["device"]["backend_errors"], trace["counts"]["errors"])
            self.assertEqual(midi["inbox"]["accepted_packets"], midi["device"]["forwarded_messages"])
            self.assertEqual(midi["inbox"]["popped_packets"], midi["decoder"]["packets"])
            self.assertEqual(midi["inbox"]["pending_packets"], 0)
            self.assertEqual(midi["inbox"]["fault_bits"], 0)
            self.assertEqual(midi["inbox"]["resets"], midi["retirements"])
            self.assertEqual(midi["decoder"]["timestamp_regressions"], 0)
            self.assertEqual(midi["decoder"]["malformed"], 0)
            self.assertEqual(midi["decoder"]["out_of_range"], 0)
            assert_expression_calibration(self, midi["expression_calibration"], final=True,
                                          active=False, pre_shutdown_active=True)
            replay = data["replay"]
            self.assertTrue(replay["completed"])
            self.assertTrue(replay["delivered"])
            self.assertTrue(replay["final_acknowledged"])
            self.assertEqual(replay["passed"], expected_exit == 0)
            self.assertFalse(replay["observations_truncated"])
            self.assertEqual(replay["device_starts"], 1)
            self.assertEqual(replay["scheduled_events"], len(events))
            self.assertEqual(replay["pushed_events"], len(events))
            for observation in replay["observations"]:
                assert_expression_calibration(self, observation["expression_calibration"])
                self.assertEqual({key: value for key, value in observation["controls"].items() if key != "expression"},
                                 {key: value for key, value in CONTROL_ORACLE.items() if key != "expression"})
                self.assertNotIn(72, observation["manual_notes"][0], "failed/faulted prefix reached the musical decoder")
                self.assertNotIn(75, observation["manual_notes"][0], "close-time callback crossed retired admission")
            self.__class__.retained.append({"scenario": scenario, "common_assertions_passed": True,
                                           "expected_exit": expected_exit,
                                           "native_opens": trace["counts"]["opens"],
                                           "decoder_epochs": midi["decoder"]["epochs"],
                                           "observations": len(replay["observations"]),
                                           "discarded_packets": midi["inbox"]["discarded_packets"]})
            return data, trace
        finally:
            if self.evidence:
                output = self.evidence / scenario
                output.mkdir(exist_ok=True)
                for source in self.directory.iterdir():
                    if source.is_file():
                        shutil.copyfile(source, output / source.name)
                (output / "stdout.txt").write_text(process.stdout)
                (output / "stderr.txt").write_text(process.stderr)

    def assert_transition(self, report: dict, calibration: dict, channels: dict = CHANNELS,
                          port: str = "Controller", *, extra_release_batches: int = 0) -> tuple[int, int]:
        observations = report["replay"]["observations"]
        candidates = [index for index, observation in enumerate(observations)
                      if observation["expression_calibration"]["pending"] == {
                          "port": port, "synthetic": False, "channels": channels, "calibration": calibration}]
        self.assertTrue(candidates, "copied native reconnect request was not observed")
        pending = candidates[0]
        self.assertGreater(pending, 0)
        pending_value = observations[pending]["expression_calibration"]
        self.assertIsNone(pending_value["active"])
        self.assertTrue(pending_value["release_pending"])
        self.assertEqual(pending_value["configured"], calibration)
        self.assertEqual(pending_value["selected"], calibration)
        self.assertEqual(observations[pending]["last_submitted_sequence"],
                         observations[pending - 1]["last_submitted_sequence"] + 3)
        release_sequence = observations[pending]["last_submitted_sequence"]
        active_candidates = [index for index in range(pending + 1, len(observations))
                             if observations[index]["expression_calibration"]["active"] == calibration]
        self.assertTrue(active_candidates, "explicit native reconnect did not produce an active epoch")
        active = active_candidates[0]
        endpoint = observations[active]
        self.assertIsNone(endpoint["expression_calibration"]["pending"])
        self.assertFalse(endpoint["expression_calibration"]["release_pending"])
        final_release_sequence = release_sequence + 3 * extra_release_batches
        self.assertGreaterEqual(endpoint["resolved_sequence"], final_release_sequence)
        self.assertGreaterEqual(endpoint["last_applied_sequence"], final_release_sequence)
        self.assertEqual(endpoint["last_submitted_sequence"], final_release_sequence,
                         "Apply itself submitted a musical-control change before the next CC11")
        self.assertEqual(endpoint["controls"]["expression"], 0.25)
        self.assertEqual(held(endpoint), EMPTY_HELD, "retired MIDI owners survived their release acknowledgment")
        return pending, active

    def test_fixture_rejects_missing_or_unknown_scenario_before_app_entry(self) -> None:
        for scenario in (None, "unknown"):
            with self.subTest(scenario=scenario):
                process = self.invoke(scenario, ["--help"])
                self.assertEqual(process.returncode, 2)
                self.assertEqual(process.stdout, "")
                self.assertIn("requires a declared scenario", process.stderr)
                self.assertEqual(list(self.directory.iterdir()), [])

    def test_fixture_inventory_calibrates_real_enumeration_without_audio(self) -> None:
        process = self.invoke("identical", ["--list-midi"])
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(process.stderr, "")
        self.assertIn("1: Controller\n2: Alternate\n", process.stdout)
        trace = read_json(self.directory / "dependency.json")
        self.validate_trace(trace, "identical", live=False)
        self.assertEqual(trace["counts"]["constructions"], 1)
        self.assertEqual(trace["counts"]["opens"], 0)
        self.assertEqual(trace["counts"]["offered_messages"], 0)
        self.assertEqual({path.name for path in self.directory.iterdir()}, {"dependency.json"})

    def test_healthy_identical_apply_preserves_epoch_notes_and_expression(self) -> None:
        events = tap(300, "M", "ctrl") + click(1000, 264, 579) + click(1500, 264, 579)
        data, trace = self.run_case("identical", events, 2200)
        midi, replay = data["midi"], data["replay"]
        self.assertEqual(trace["counts"]["opens"], 1)
        self.assertEqual(midi["generation"], 1)
        self.assertEqual(midi["decoder"]["epochs"], 1)
        self.assertEqual(midi["retirements"], 1)  # Ordinary final shutdown only.
        self.assertEqual(midi["release_batches"], 1)
        self.assertEqual(midi["parameter_messages"], 1)
        self.assertEqual(midi["inbox"]["discarded_packets"], 0)
        self.assertEqual(held(replay["before_shutdown"]), INITIAL_HELD)
        self.assertEqual(replay["before_shutdown"]["controls"]["expression"], 0.25)
        self.assertEqual(midi["expression_calibration"]["pre_shutdown_active"], OLD)
        for observation in replay["observations"]:
            self.assertIsNone(observation["expression_calibration"]["pending"])
            if observation["overlay"] == "midi":
                self.assertEqual(observation["expression_calibration"]["active"], OLD)
                self.assertEqual(held(observation), INITIAL_HELD)
                self.assertEqual(observation["controls"]["expression"], 0.25)

    def test_changed_calibration_reopens_only_after_ack_and_awaits_next_cc11(self) -> None:
        data, trace = self.run_case("calibration", calibration_edit(), 2600)
        pending, active = self.assert_transition(data, NEW)
        edits = [item for item in data["replay"]["observations"][:pending]
                 if item["expression_calibration"]["selected"] == NEW]
        self.assertTrue(edits, "selected endpoints and inversion were not observable before Apply")
        for item in edits:
            self.assertEqual(item["expression_calibration"]["configured"], OLD)
            self.assertEqual(item["expression_calibration"]["active"], OLD)
            self.assertIsNone(item["expression_calibration"]["pending"])
            self.assertEqual(item["controls"]["expression"], 0.25)
        self.assertEqual(trace["counts"]["opens"], 2)
        self.assertEqual(data["midi"]["generation"], 2)
        self.assertEqual(data["midi"]["decoder"]["epochs"], 2)
        self.assertEqual(data["midi"]["inbox"]["discarded_packets"], 0)
        self.assertEqual(data["midi"]["parameter_messages"], 2)
        self.assertEqual(data["midi"]["expression_calibration"]["pre_shutdown_active"], NEW)
        later = data["replay"]["observations"][active + 1:]
        self.assertTrue(any(item["controls"]["expression"] == 0.8125 and held(item) == FRESH_HELD for item in later))
        self.assertEqual(held(data["replay"]["before_shutdown"]), FRESH_HELD)
        self.assertEqual(data["replay"]["before_shutdown"]["controls"]["expression"], 0.8125)

    def test_changed_route_retires_old_owners_and_rejects_old_wire_channel(self) -> None:
        events = tap(300, "M", "ctrl")
        for at, x in ((1000, 244), (1100, 480), (1200, 716)):
            for step in range(3):
                events += click(at + 20 * step, x, 308)
        events += click(1500, 264, 579)
        data, trace = self.run_case("route", events, 2400)
        self.assert_transition(data, OLD, NEW_CHANNELS)
        self.assertEqual(trace["counts"]["opens"], 2)
        self.assertEqual(data["midi"]["channels"], NEW_CHANNELS)
        self.assertEqual(data["midi"]["decoder"]["epochs"], 2)
        self.assertEqual(data["midi"]["decoder"]["unmapped_channels"], 2)
        self.assertEqual(data["midi"]["parameter_messages"], 2)
        self.assertEqual(data["replay"]["before_shutdown"]["controls"]["expression"], 0.5)
        self.assertEqual(held(data["replay"]["before_shutdown"]), FRESH_HELD)
        self.assertTrue(all(74 not in item["manual_notes"][0] for item in data["replay"]["observations"]))

    def test_changed_exact_port_reconnects_with_unchanged_calibration(self) -> None:
        events = tap(300, "M", "ctrl") + click(1000, 802, 184) + click(1300, 264, 579)
        data, trace = self.run_case("port", events, 2200)
        self.assert_transition(data, OLD, port="Alternate")
        self.assertEqual([event["port"] for event in trace["events"] if event["operation"] == "open"], [0, 1])
        self.assertEqual(data["midi"]["requested_port"], "Alternate")
        self.assertEqual(data["midi"]["port_name"], "Alternate")
        self.assertEqual(data["midi"]["generation"], 2)
        self.assertEqual(data["replay"]["before_shutdown"]["controls"]["expression"], 0.5)
        self.assertEqual(held(data["replay"]["before_shutdown"]), FRESH_HELD)

    def test_no_input_apply_retains_calibration_without_touching_expression(self) -> None:
        events = calibration_edit() + tap(1800, "Escape") + tap(2000, "M", "ctrl")
        events += click(2500, 802, 184) + click(2700, 264, 579)
        data, trace = self.run_case("no-input", events, 3500, connected=False)
        observations = data["replay"]["observations"]
        configured = [index for index, item in enumerate(observations)
                      if item["expression_calibration"]["configured"] == NEW
                      and item["expression_calibration"]["active"] is None]
        self.assertTrue(configured)
        first_active = next(index for index, item in enumerate(observations)
                            if item["expression_calibration"]["active"] == NEW)
        self.assertGreater(first_active, configured[0])
        for item in observations[:first_active]:
            self.assertEqual(item["controls"], CONTROL_ORACLE)
            self.assertEqual(held(item), EMPTY_HELD)
            self.assertIsNone(item["expression_calibration"]["pending"])
        self.assertTrue(any(item["overlay"] == "none" and item["expression_calibration"]["configured"] == NEW
                            for item in observations[configured[0]:first_active]))
        self.assertEqual(trace["counts"]["opens"], 1)
        self.assertEqual(data["midi"]["decoder"]["epochs"], 1)
        self.assertEqual(data["midi"]["parameter_messages"], 1)
        self.assertEqual(data["midi"]["expression_calibration"]["pre_shutdown_active"], NEW)
        self.assertEqual(data["replay"]["before_shutdown"]["controls"]["expression"], 0.8125)
        self.assertEqual(held(data["replay"]["before_shutdown"]), INITIAL_HELD)

    def test_failed_reopen_discards_callback_prefix_and_requires_explicit_retry(self) -> None:
        events = calibration_edit() + click(2300, 264, 579)
        data, trace = self.run_case("failed-reopen", events, 3300, expected_exit=1)
        pending, active = self.assert_transition(data, NEW, extra_release_batches=1)
        observations = data["replay"]["observations"]
        failed = [index for index in range(pending + 1, active)
                  if observations[index]["error_count"] == 1
                  and observations[index]["expression_calibration"]["active"] is None
                  and observations[index]["expression_calibration"]["pending"] is None]
        self.assertTrue(failed, "failed activation was not retained as an inactive, non-retrying state")
        for item in observations[failed[0]:active]:
            self.assertEqual(item["controls"]["expression"], 0.25)
            self.assertEqual(item["expression_calibration"]["configured"], NEW)
        self.assertEqual(trace["counts"]["opens"], 3)
        self.assertEqual(trace["counts"]["errors"], 1)
        self.assertEqual(data["midi"]["generation"], 2)
        self.assertEqual(data["midi"]["decoder"]["epochs"], 3)
        self.assertEqual(data["midi"]["open_failures"], 1)
        self.assertEqual(data["midi"]["inbox"]["discarded_packets"], 3)
        self.assertEqual(data["midi"]["decoder"]["packets"], 6)
        self.assertEqual(data["midi"]["parameter_messages"], 2)
        self.assertEqual(data["replay"]["before_shutdown"]["controls"]["expression"], 0.8125)
        self.assertEqual(held(data["replay"]["before_shutdown"]), FRESH_HELD)

    def test_native_fault_retires_midi_owners_while_original_ui_owner_survives(self) -> None:
        events = [(80, "key_down A none 0"), (1100, "key_up A none")]
        events += tap(1300, "M", "ctrl") + click(2200, 264, 579)
        data, trace = self.run_case("fault-retry", events, 3200, expected_exit=1)
        observations = data["replay"]["observations"]
        failed = [item for item in observations if item["error_count"] == 1 and item["overlay"] == "none"
                  and item["expression_calibration"]["active"] is None and held(item) == ((60,), (), ())]
        self.assertTrue(failed, "MIDI fault released the unrelated keyboard owner or lacked its observed witness")
        self.assertTrue(any(item["overlay"] == "none" and item["error_count"] == 1 and held(item) == EMPTY_HELD
                            for item in observations), "original keyboard key-up did not retire its own owner")
        self.assertEqual(trace["counts"]["opens"], 2)
        self.assertEqual(trace["counts"]["errors"], 1)
        self.assertEqual(data["midi"]["generation"], 2)
        self.assertEqual(data["midi"]["decoder"]["epochs"], 2)
        self.assertEqual(data["midi"]["fault_retirements"], 1)
        self.assertEqual(data["midi"]["inbox"]["discarded_packets"], 2)
        self.assertEqual(data["midi"]["decoder"]["packets"], 6)
        self.assertEqual(data["midi"]["parameter_messages"], 2)
        self.assertTrue(all(item["controls"]["expression"] in (0.375, 0.25) for item in observations))
        self.assertEqual(data["replay"]["before_shutdown"]["controls"]["expression"], 0.25)
        self.assertEqual(held(data["replay"]["before_shutdown"]), FRESH_HELD)


if __name__ == "__main__":
    unittest.main(verbosity=2)
