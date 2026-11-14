#!/usr/bin/env python3
"""Independent musical acceptance through the actual native MIDI/UI replay paths.

HAMMOND_STANDALONE_EXECUTABLE must name an already built application. No private
Engine, Session, decoder, UiModel, or MIDI transport stand-in is imported. Every
process has explicit SDL dummy drivers, a finite timeout, and private files.
Optional HAMMOND_STANDALONE_MIDI_EVIDENCE retains the exact inputs and reports.
These are synthetic callback-boundary observations, not hardware timing tests.
"""

from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import unittest

from test_standalone_app import SCHEMA, assert_schema, reject_nonfinite, unique_object


PROCESS_TIMEOUT = 9.0
EMPTY = ((), (), ())
DEFAULT_CONTROLS = {
    "manual_drawbars": [
        [[0] * 9, [8, 8, 8, 0, 0, 0, 0, 0, 0]],
        [[0] * 9, [0, 0, 8, 0, 0, 0, 0, 0, 0]],
    ],
    "selected_banks": [1, 1], "route_enabled": [True, True], "expression": 1,
    "pedal_drawbars": [8, 0],
    "percussion": {"enabled": False, "harmonic": 0, "volume": 0, "decay": 0},
}
CONTROL_STATE = b"""B3CONTROLS3
expression 1
percussion enabled 0 harmonic second volume normal decay slow
pedal drawbars 8 0
manual upper selected A route_enabled 0
bank A 0 0 0 0 0 0 0 0 0
bank B 8 8 8 0 0 0 0 0 0
manual lower selected A route_enabled 1
bank A 1 2 3 4 5 6 7 8 0
bank B 0 0 8 0 0 0 0 0 0
end
"""

# Reuse only the strict JSON type/key checker and the common public schema.
# Musical expectations below are independent literals, never computed from the
# decoder, UiModel, control bridge, app serializer, or production layout.
SNAPSHOT_SCHEMA = {
    "manual_notes": [[], []], "pedal_ids": [], "controls": SCHEMA["controls"],
    "resolved_sequence": int, "last_applied_sequence": int,
}
RESULT_SCHEMA = {
    "final_acknowledged": bool, "last_submitted_sequence": int,
    "accepted_note_on_commands": int, "accepted_note_off_commands": int,
    "device_starts": int, "observation_capacity": int, "observations_truncated": bool,
    "before_shutdown": SNAPSHOT_SCHEMA, "observations": [],
}
UI_REPLAY_SCHEMA = {
    "completed": bool, "delivered": bool, "passed": bool, "duration_ms": int,
    "scheduled_events": int, "pushed_events": int, **RESULT_SCHEMA,
}
MIDI_REPLAY_SCHEMA = {
    "source": str, "completed": bool, "delivered": bool, "passed": bool,
    "duration_ms": int, "scheduled_events": int, "delivered_events": int,
    "scheduled_packets": int, "offered_packets": int, "accepted_packets": int,
    "dropped_packets": int, "ignored_while_closed": int, "rejected_packets": int,
    "discarded_queued_packets": int, "connect_events": int, "connections_started": int,
    "disconnect_events": int, "intentional_backend_faults": int,
    "intentional_overflow_faults": int, "faults_while_closed": int, "failure_count": int,
    "connect_barriers": int, "barrier_wait_turns": int, "cancelled_connects": int,
    "event_budget": int, "maximum_events_per_turn": int, "budget_exhaustions": int,
    "arrival_time_source": str, "arrival_time_is_sample_time": bool, "last_arrival_ns": int,
    "connected_before_shutdown": bool, "faulted_before_shutdown": bool,
    "connected_after_shutdown": bool, "pending_packets_before_shutdown": int,
    "pending_connect_before_shutdown": bool, "release_pending_before_shutdown": bool,
    **RESULT_SCHEMA,
}


def script(magic: str, duration: int, events: list[tuple[int, str]]) -> bytes:
    """Serialize literal actions without sorting away accidental source disorder."""
    return (f"{magic}\nduration_ms {duration}\n" + "".join(
        f"{at} {event}\n" for at, event in events)).encode("ascii")


def tap(at: int, key: str, modifiers: str = "none") -> list[tuple[int, str]]:
    return [(at, f"key_down {key} {modifiers} 0"), (at + 4, f"key_up {key} {modifiers}")]


def tabs(at: int, count: int) -> list[tuple[int, str]]:
    return [event for index in range(count) for event in tap(at + 10 * index, "Tab")]


def click(at: int, x: int, y: int) -> list[tuple[int, str]]:
    return [(at, f"mouse_down {x} {y}"), (at + 4, f"mouse_up {x} {y}")]


def bytes_event(at: int, *values: int) -> tuple[int, str]:
    return at, "bytes " + " ".join(f"{value:02X}" for value in values)


def held(snapshot: dict) -> tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
    return tuple(snapshot["manual_notes"][0]), tuple(snapshot["manual_notes"][1]), tuple(snapshot["pedal_ids"])


def snapshot_schema(snapshot: dict, *, observation: bool = False) -> dict:
    schema = dict(SNAPSHOT_SCHEMA)
    schema["manual_notes"] = [[int] * len(notes) for notes in snapshot["manual_notes"]]
    schema["pedal_ids"] = [int] * len(snapshot["pedal_ids"])
    if observation:
        schema.update(elapsed_ms=int, last_submitted_sequence=int)
    return schema


def replay_schema(data: dict, template: dict) -> dict:
    schema = dict(template)
    schema["before_shutdown"] = snapshot_schema(data["before_shutdown"])
    schema["observations"] = [snapshot_schema(item, observation=True) for item in data["observations"]]
    return schema


@dataclass(frozen=True)
class NativeRun:
    data: dict
    elapsed: float

    @property
    def midi(self) -> dict:
        return self.data["midi_replay"]


class NativeMidiReplayAcceptance(unittest.TestCase):
    invocations = 0
    expected_interrupted = 0

    @classmethod
    def setUpClass(cls) -> None:
        configured = os.environ.get("HAMMOND_STANDALONE_EXECUTABLE", "")
        if not configured:
            raise RuntimeError("HAMMOND_STANDALONE_EXECUTABLE is required; build the app first")
        cls.executable = Path(configured).resolve(strict=True)
        if not cls.executable.is_file() or not os.access(cls.executable, os.X_OK):
            raise RuntimeError(f"Native application is not executable: {cls.executable}")
        cls.binary_hash = hashlib.sha256(cls.executable.read_bytes()).hexdigest()
        print(f"Native MIDI replay executable SHA-256: {cls.binary_hash}", flush=True)
        evidence = os.environ.get("HAMMOND_STANDALONE_MIDI_EVIDENCE", "")
        cls.evidence = Path(evidence).resolve() if evidence else None
        if cls.evidence:
            cls.evidence.mkdir(parents=True, exist_ok=True)

    @classmethod
    def tearDownClass(cls) -> None:
        print(f"Actual native MIDI replay subprocesses: {cls.invocations}; "
              f"expected interrupted replays: {cls.expected_interrupted}", flush=True)
        if hashlib.sha256(cls.executable.read_bytes()).hexdigest() != cls.binary_hash:
            raise AssertionError("The native executable changed during acceptance")

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="hammond-native-midi-replay-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.sequence = 0

    @contextmanager
    def run_native(self, duration: int, midi_events: list[tuple[int, str]], *,
                   ui_events: list[tuple[int, str]] | None = None,
                   arguments: list[str] | None = None, state: bytes | None = None,
                   expected_exit: int = 0):
        self.sequence += 1
        directory = self.root / f"run-{self.sequence}"
        directory.mkdir()
        midi_path = directory / "MIDI input 音.b3midi"
        ui_path = directory / "UI input Ω.b3ui"
        state_path = directory / "private controls.b3controls"
        report_path = directory / "diagnostics.json"
        midi_source = script("B3MIDIREPLAY1", duration, midi_events)
        midi_path.write_bytes(midi_source)
        command = [str(self.executable), "--state", str(state_path),
                   "--midi-script", str(midi_path), "--diagnostics", str(report_path)]
        expected_files = {midi_path.name, report_path.name}
        ui_source = None
        if ui_events is not None:
            ui_source = script("B3UIREPLAY1", duration, ui_events)
            ui_path.write_bytes(ui_source)
            command += ["--input-script", str(ui_path)]
            expected_files.add(ui_path.name)
        if state is not None:
            state_path.write_bytes(state)
            expected_files.add(state_path.name)
        command += arguments or []
        environment = dict(os.environ, SDL_AUDIODRIVER="dummy", SDL_VIDEODRIVER="dummy")
        process = None
        data = None
        elapsed = 0.0
        self.__class__.invocations += 1
        started = time.monotonic()
        try:
            process = subprocess.run(command, cwd=directory, env=environment,
                                     stdin=subprocess.DEVNULL, capture_output=True,
                                     text=True, errors="replace", timeout=PROCESS_TIMEOUT, check=False)
            elapsed = time.monotonic() - started
            self.assertEqual(process.returncode, expected_exit)
            self.assertEqual(process.stdout, "")
            self.assertTrue(report_path.is_file(), "The native run did not write diagnostics")
            data = json.loads(report_path.read_text(encoding="utf-8"),
                              object_pairs_hook=unique_object, parse_constant=reject_nonfinite)
            self.assert_common(data, duration, midi_events, ui_events, state_path,
                               successful=expected_exit == 0)
            self.assertEqual(midi_path.read_bytes(), midi_source)
            if ui_source is not None:
                self.assertEqual(ui_path.read_bytes(), ui_source)
            if state is None:
                self.assertFalse(state_path.exists(), "Replay unexpectedly saved controls")
            else:
                self.assertEqual(state_path.read_bytes(), state, "Replay rewrote the input controls")
            self.assertEqual({path.name for path in directory.iterdir()}, expected_files)
            if expected_exit == 0:
                self.assertEqual(process.stderr, "")
                self.assertGreaterEqual(elapsed, duration / 1000 - 0.04,
                                        "Replay completed before its declared duration")
            else:
                self.__class__.expected_interrupted += 1
                self.assertIn("Native MIDI replay failed or was interrupted", process.stderr)
            yield NativeRun(data, elapsed)
        except Exception as error:
            # Copy bounded evidence into the failure before private-file cleanup;
            # assertion failures made by the caller are covered by this context.
            if data is not None:
                diagnostic_text = json.dumps(data, sort_keys=True)
            elif report_path.is_file():
                with report_path.open("rb") as source:
                    diagnostic_text = source.read(65537).decode("utf-8", errors="replace")
            else:
                diagnostic_text = "[diagnostics unavailable]"
            output = "" if process is None else process.stdout + "\n" + process.stderr
            raise AssertionError(
                f"{self._testMethodName}: {type(error).__name__}: {error}\n"
                f"Command: {command!r}\nElapsed: {elapsed:.3f}s\n{output}\n"
                f"MIDI input:\n{midi_source.decode('ascii')}"
                + (f"UI input:\n{ui_source.decode('ascii')}" if ui_source else "")
                + f"Copied diagnostics (at most 65536 characters):\n{diagnostic_text[:65536]}"
            ) from error
        finally:
            if self.evidence is not None:
                destination = self.evidence / f"{self._testMethodName}-{self.sequence}"
                shutil.copytree(directory, destination)
                (destination / "process.json").write_text(json.dumps({
                    "command": command, "elapsed_seconds": elapsed,
                    "executable_sha256": self.binary_hash,
                    "environment": {"SDL_AUDIODRIVER": "dummy", "SDL_VIDEODRIVER": "dummy"},
                    "returncode": process.returncode if process else None,
                    "stdout": process.stdout if process else None,
                    "stderr": process.stderr if process else None,
                }, indent=2) + "\n", encoding="utf-8")

    def assert_common(self, data: dict, duration: int, midi_events: list[tuple[int, str]],
                      ui_events: list[tuple[int, str]] | None, state_path: Path, *, successful: bool) -> None:
        schema = dict(SCHEMA)
        schema["midi_replay"] = replay_schema(data["midi_replay"], MIDI_REPLAY_SCHEMA)
        if ui_events is not None:
            schema["replay"] = replay_schema(data["replay"], UI_REPLAY_SCHEMA)
        assert_schema(self, data, schema)
        self.assertEqual(data["schema_version"], 2)
        self.assertEqual(data["application"], "hammond_standalone")
        self.assertEqual(data["state_path"], str(state_path))
        audio, session, midi, replay = data["audio"], data["session"], data["midi"], data["midi_replay"]
        self.assertEqual(data["runtime"]["video_driver"], "dummy")
        self.assertGreater(data["runtime"]["rendered_images"], 0)
        self.assertFalse(data["runtime"]["screenshot_written"])
        self.assertEqual(audio["driver"], "dummy")
        self.assertTrue(audio["open_before_shutdown"])
        self.assertTrue(audio["running_before_shutdown"])
        self.assertGreater(audio["callback_count"], 0)
        self.assertGreater(audio["rendered_frames"], 0)
        self.assertEqual(audio["channels"], 2)
        self.assertEqual(audio["sample_format"], audio["native_float32_format"])
        self.assertEqual(audio["buffer_bytes"], 8 * audio["buffer_frames"])
        for field in ("render_failures", "format_failures", "overrange_failures", "overrange_samples",
                      "nonfinite_failures", "nonfinite_samples"):
            self.assertEqual(audio[field], 0, field)
        self.assertEqual(audio["last_render_status"], "ok")
        self.assertEqual(audio["last_lifecycle_status"], "ok")
        self.assertTrue(session["snapshot_available"])
        self.assertTrue(session["prepared"])
        self.assertFalse(session["running_after_shutdown"])
        self.assertFalse(session["held_after_shutdown"])
        for field in ("recovery_count", "queue_overflows", "rejected_commands", "fault_flags"):
            self.assertEqual(session[field], 0, field)
        # Each joined stop can discard its three redundant MIDI scoped releases
        # and one UI release. Earlier performance commands must be acknowledged.
        self.assertLessEqual(session["discarded_commands"], 4 * replay["device_starts"])
        self.assertGreaterEqual(session["maximum_observed_peak"], 0)
        self.assertFalse(data["smoke"]["requested"])
        self.assertFalse(data["smoke"]["note_on_sent"])
        self.assertFalse(data["smoke"]["note_off_sent"])

        self.assertEqual(midi["source"], "synthetic-replay")
        self.assertEqual(midi["requested_port"], "")
        self.assertEqual(midi["port_name"], "")
        self.assertEqual(midi["generation"], 0)
        self.assertEqual(midi["opened_port_index"], 0)
        native_state = "closed" if midi["backend_available"] else "unavailable"
        self.assertEqual(midi["state_before_shutdown"], native_state)
        self.assertEqual(midi["state_after_shutdown"], native_state)
        self.assertEqual(midi["active_before_shutdown"], replay["connected_before_shutdown"])
        self.assertFalse(midi["active_after_shutdown"])
        self.assertTrue(midi["quiescent_after_shutdown"])
        self.assertTrue(midi["diagnostics_stable_after_shutdown"])
        self.assertFalse(midi["startup_failed"])
        self.assertFalse(midi["shutdown_failed"])
        for field, value in midi["device"].items():
            self.assertEqual(value, 0, f"Synthetic input must not open a native device: {field}")
        self.assertEqual(midi["drain_budget"], 32)
        self.assertLessEqual(midi["maximum_drained_per_turn"], 32)
        self.assertEqual(midi["timing_policy"], "arrival_order_next_callback_boundary")
        self.assertEqual(midi["arrival_time_unit"], "steady_clock_nanoseconds")
        self.assertEqual(midi["arrival_time_source"], "synthetic_main_thread_receipt")
        self.assertFalse(midi["arrival_time_is_sample_time"])
        for field in ("open_failures", "submit_failures", "session_recoveries_observed"):
            self.assertEqual(midi[field], 0, field)
        self.assertEqual(midi["last_submit_status"], "ok")
        self.assertEqual(midi["retirements"], midi["release_batches"])
        self.assertEqual(midi["release_commands_accepted"], 3 * midi["release_batches"])
        self.assertFalse(midi["release_pending"])

        inbox, decoder = midi["inbox"], midi["decoder"]
        self.assertEqual(inbox["capacity"], 256)
        self.assertEqual(inbox["pending_packets"], 0)
        self.assertEqual(inbox["fault_bits"], 0)
        self.assertEqual(inbox["invalid_size_packets"], 0)
        self.assertEqual(inbox["faulted_packets"], 0)
        self.assertEqual(inbox["accepted_packets"], inbox["popped_packets"] + inbox["discarded_packets"])
        self.assertEqual(decoder["packets"], inbox["popped_packets"])
        self.assertEqual(decoder["packets"], sum(decoder[field] for field in (
            "actions", "unsupported", "unmapped_channels", "out_of_range", "malformed", "inactive")))
        self.assertEqual(decoder["inactive"], 0)
        self.assertEqual(decoder["timestamp_regressions"], 0)
        self.assertEqual(decoder["epochs"], replay["connections_started"])
        self.assertEqual(replay["source"], "synthetic-replay")
        self.assertEqual(replay["duration_ms"], duration)
        self.assertEqual(replay["scheduled_events"], len(midi_events))
        self.assertEqual(replay["scheduled_packets"], sum(action.startswith("bytes ") for _, action in midi_events))
        self.assertEqual(replay["offered_packets"], inbox["received_packets"])
        self.assertEqual(replay["accepted_packets"], inbox["accepted_packets"])
        self.assertEqual(replay["rejected_packets"], inbox["received_packets"] - inbox["accepted_packets"])
        self.assertEqual(replay["discarded_queued_packets"], inbox["discarded_packets"])
        self.assertEqual(replay["dropped_packets"], replay["ignored_while_closed"] +
                         replay["rejected_packets"] + inbox["discarded_packets"])
        self.assertEqual(replay["intentional_overflow_faults"], inbox["overflow_events"])
        self.assertEqual(replay["event_budget"], 512)
        self.assertLessEqual(replay["maximum_events_per_turn"], 512)
        self.assertEqual(replay["arrival_time_source"], "synthetic_main_thread_steady_clock_receipt")
        self.assertFalse(replay["arrival_time_is_sample_time"])
        self.assertGreater(replay["last_arrival_ns"], 0)
        self.assertFalse(replay["connected_after_shutdown"])
        self.assertEqual(replay["pending_packets_before_shutdown"], 0)
        self.assertFalse(replay["pending_connect_before_shutdown"])
        self.assertFalse(replay["release_pending_before_shutdown"])
        self.assertEqual(replay["observation_capacity"], 8704)
        self.assertFalse(replay["observations_truncated"])
        self.assertTrue(replay["observations"])
        self.assertLessEqual(len(replay["observations"]), 8704)
        elapsed = [item["elapsed_ms"] for item in replay["observations"]]
        self.assertEqual(elapsed, sorted(elapsed))
        for item in [replay["before_shutdown"], *replay["observations"]]:
            self.assertEqual(len(item["manual_notes"]), 2)
            for notes in item["manual_notes"]:
                self.assertEqual(notes, sorted(set(notes)))
                self.assertTrue(all(36 <= pitch <= 96 for pitch in notes))
            self.assertEqual(item["pedal_ids"], sorted(set(item["pedal_ids"])))
            self.assertTrue(all(1 <= pedal <= 25 for pedal in item["pedal_ids"]))
        self.assertEqual(replay["before_shutdown"]["controls"], data["controls"])
        if replay["device_starts"] == 1:
            self.assertEqual(audio["rendered_frames"], audio["callback_count"] * audio["buffer_frames"])
            self.assertEqual(session["frame_clock"], audio["rendered_frames"])
        if ui_events is not None:
            ui = data["replay"]
            self.assertEqual(ui["duration_ms"], duration)
            self.assertEqual(ui["scheduled_events"], len(ui_events))
            for field in RESULT_SCHEMA:
                self.assertEqual(ui[field], replay[field], field)
            if successful:
                self.assertEqual(ui["pushed_events"], len(ui_events))
                for field in ("completed", "delivered", "passed"):
                    self.assertTrue(ui[field], field)
        if successful:
            self.assertEqual(data["errors"], {"count": 0, "last": ""})
            self.assertEqual(replay["failure_count"], 0)
            for field in ("completed", "delivered", "passed", "final_acknowledged"):
                self.assertTrue(replay[field], field)
            self.assertEqual(replay["delivered_events"], len(midi_events))
            self.assertEqual(replay["scheduled_packets"], replay["offered_packets"] + replay["ignored_while_closed"])
            self.assertEqual(replay["scheduled_packets"], decoder["packets"] + replay["dropped_packets"])
            self.assertEqual(replay["connect_events"], sum(action == "connect" for _, action in midi_events))
            self.assertEqual(replay["disconnect_events"], sum(action == "disconnect" for _, action in midi_events))
            self.assertEqual(replay["intentional_backend_faults"], sum(action == "fault backend" for _, action in midi_events))
            before = replay["before_shutdown"]
            self.assertGreaterEqual(before["resolved_sequence"], replay["last_submitted_sequence"])
            self.assertGreaterEqual(before["last_applied_sequence"], replay["last_submitted_sequence"])

    def assert_final(self, run: NativeRun, expected: tuple, *, on: int, off: int = 0,
                     controls: dict | None = None) -> None:
        self.assertEqual(held(run.midi["before_shutdown"]), expected,
                         "Joined shutdown must not substitute for the scripted musical outcome")
        self.assertEqual(run.midi["accepted_note_on_commands"], on)
        self.assertEqual(run.midi["accepted_note_off_commands"], off)
        self.assertEqual(run.data["controls"], DEFAULT_CONTROLS if controls is None else controls)

    def assert_window(self, run: NativeRun, after: int, before: int, expected: tuple) -> None:
        # Require an actual acknowledged observation in the intended quiet gap.
        # Merely carrying an earlier correct state forward would hide a missed
        # release; requiring an exact callback millisecond would claim too much.
        candidates = [item for item in run.midi["observations"]
                      if after <= item["elapsed_ms"] < before
                      and item["last_applied_sequence"] >= item["last_submitted_sequence"]]
        self.assertTrue(candidates, f"No acknowledged musical observation in [{after}, {before}) ms")
        self.assertEqual(held(candidates[-1]), expected)

    def test_division_channel_range_routing_and_ignored_packets(self) -> None:
        for channels in ((1, 2, 3), (16, 1, 2)):
            with self.subTest(channels=channels):
                upper, lower, pedals = (channel - 1 for channel in channels)
                unselected = 3
                events = [bytes_event(0, 0x90 | upper, 60, 100), (50, "connect")]
                for wire, pitches in ((upper, (36, 96)), (lower, (36, 96)), (pedals, (36, 60))):
                    events += [bytes_event(150, 0x90 | wire, pitch, 100) for pitch in pitches]
                for wire, pitches in ((upper, (35, 97)), (lower, (35, 97)), (pedals, (35, 61))):
                    events += [bytes_event(200, 0x90 | wire, pitch, 100) for pitch in pitches]
                events += [bytes_event(200, 0x90 | unselected, 60, 100),
                           bytes_event(200, 0xB0 | unselected, 11, 0),
                           bytes_event(200, 0x90 | upper), bytes_event(200, 0x90 | upper, 128, 100),
                           bytes_event(200, 0xF8), bytes_event(200, 0xC0 | upper, 5),
                           bytes_event(200, 0xB0 | upper, 64, 127),
                           bytes_event(200, 0xB0 | upper, 120, 0),
                           bytes_event(200, 0xB0 | upper, 121, 0),
                           bytes_event(200, 0xB0 | pedals, 18, 127)]
                arguments = ["--midi-upper-channel", str(channels[0]),
                             "--midi-lower-channel", str(channels[1]),
                             "--midi-pedal-channel", str(channels[2])]
                with self.run_native(650, events, arguments=arguments) as run:
                    self.assert_final(run, ((36, 96), (36, 96), (1, 25)), on=6)
                    self.assertEqual(run.data["midi"]["channels"], dict(zip(("upper", "lower", "pedals"), channels)))
                    self.assertEqual(run.data["midi"]["decoder"], {
                        "packets": 22, "actions": 6, "unsupported": 6, "unmapped_channels": 2,
                        "out_of_range": 6, "malformed": 2, "inactive": 0,
                        "timestamp_regressions": 0, "epochs": 1,
                    })
                    self.assertEqual(run.midi["ignored_while_closed"], 1)
                    self.assertEqual(run.midi["dropped_packets"], 1)
                    self.assertEqual(run.data["midi"]["parameter_messages"], 0)
                    self.assertGreater(run.data["session"]["maximum_observed_peak"], 0)

    def test_repeated_fifo_owners_velocity_zero_and_both_release_orders(self) -> None:
        events = [(0, "connect")]
        for status, pitch in ((0x90, 60), (0x91, 64), (0x92, 36)):
            events += [bytes_event(150, status, pitch, 1), bytes_event(150, status, pitch, 127)]
        events += [bytes_event(450, 0x90, 60, 0), bytes_event(450, 0x81, 64, 127),
                   bytes_event(450, 0x92, 36, 0), bytes_event(750, 0x80, 60, 95),
                   bytes_event(750, 0x91, 64, 0), bytes_event(750, 0x82, 36, 64),
                   bytes_event(1450, 0x90, 60, 100), bytes_event(2050, 0x80, 60, 1),
                   bytes_event(2150, 0x80, 60, 1)]
        # UI releases after the first MIDI pair has exhausted its owners, then
        # a second shared note releases UI first and MIDI last. All note IDs are
        # literal pitches; velocities do not deduplicate anonymous MIDI owners.
        ui = [(100, "key_down A none 0"), (1050, "key_up A none"),
              (1400, "key_down A none 0"), (1750, "key_up A none")]
        with self.run_native(2450, events, ui_events=ui) as run:
            self.assert_window(run, 450, 730, ((60,), (64,), (1,)))
            self.assert_window(run, 750, 1030, ((60,), (), ()))
            self.assert_window(run, 1050, 1380, EMPTY)
            self.assert_window(run, 1750, 2030, ((60,), (), ()))
            self.assert_final(run, EMPTY, on=9, off=10)
            self.assertEqual(run.data["midi"]["decoder"]["actions"], 15)
            self.assertEqual(run.data["midi"]["release_batches"], 1)

    def test_cc11_and_bank_b_edits_share_pending_ui_controls(self) -> None:
        expected = deepcopy(DEFAULT_CONTROLS)
        expected["selected_banks"] = [0, 0]
        expected["route_enabled"] = [False, True]
        expected["manual_drawbars"][1][0] = [1, 2, 3, 4, 5, 6, 7, 8, 0]
        events = [(0, "connect"), bytes_event(150, 0x90, 60, 100)]
        # EDIT A is the independent literal cheek center; five Tabs select its
        # first drawbar. Sounding A remains Cancelled throughout the CC edits.
        ui = click(100, 58, 508) + tabs(180, 5)
        for index, at in enumerate((350, 500, 650, 800)):
            high = index % 2 == 0
            ui += tap(at, "End" if high else "Home")
            events += [bytes_event(at, 0xB0, 11, 96 if high else 64),
                       bytes_event(at, 0xB0, 16, 127 if high else 7),
                       bytes_event(at, 0xB0, 17, 0 if high else 8)]
        events += [bytes_event(1000, 0xB0, 24, 127), bytes_event(1000, 0xB1, 16, 64),
                   bytes_event(1000, 0xB1, 24, 0), bytes_event(1000, 0xB2, 16, 0),
                   bytes_event(1000, 0xB2, 17, 127)]
        ui += tap(1200, "Right")
        expected["manual_drawbars"][0][0][0] = 1
        expected["manual_drawbars"][0][1] = [0, 1, 8, 0, 0, 0, 0, 0, 8]
        expected["manual_drawbars"][1][1][0] = 4
        expected["pedal_drawbars"] = [0, 8]
        expected["expression"] = 64 / 127
        with self.run_native(1550, events, ui_events=ui, state=CONTROL_STATE,
                             arguments=["--sample-rate", "44100", "--buffer-frames", "2048"]) as run:
            self.assert_final(run, ((60,), (), ()), on=1, controls=expected)
            self.assertEqual(run.data["midi"]["parameter_messages"], 17)
            self.assertEqual(run.data["midi"]["decoder"]["actions"], 18)
            # Alternating groups change A plus three MIDI parameters; unchanged
            # values may emit no snapshot. A pending suffix of four commands is
            # an observed unacknowledged UI edit joined by MIDI edits, not merely a
            # claim based on equal schedule times in independent streams.
            pending = [item for item in run.midi["observations"]
                       if 350 <= item["elapsed_ms"] < 1000
                       and item["last_submitted_sequence"] - item["last_applied_sequence"] >= 4]
            self.assertTrue(pending, "No paired UI/MIDI control batch was observed while pending")
            self.assertTrue(all(item["controls"]["selected_banks"] == [0, 0]
                                and item["controls"]["route_enabled"] == [False, True]
                                for item in run.midi["observations"]))

    def test_cc123_releases_only_its_external_division_and_preserves_ui(self) -> None:
        ui = [(100, "key_down A none 0")] + tap(220, "F2")
        ui += [(260, "key_down S none 0")] + tap(330, "F3")
        ui += [(370, "key_down D none 0")]
        events = [(0, "connect")]
        for status, pitches in ((0x90, (60, 64)), (0x91, (62, 65)), (0x92, (40, 41))):
            events += [bytes_event(150, status, pitch, 100) for pitch in pitches]
        events += [bytes_event(650, 0xB0, 123, 127), bytes_event(950, 0xB1, 123, 0),
                   bytes_event(1250, 0xB2, 123, 91)]
        with self.run_native(1600, events, ui_events=ui) as run:
            self.assert_window(run, 370, 630, ((60, 64), (62, 65), (5, 6)))
            self.assert_window(run, 650, 930, ((60,), (62, 65), (5, 6)))
            self.assert_window(run, 950, 1230, ((60,), (62,), (5, 6)))
            self.assert_final(run, ((60,), (62,), (5,)), on=9)
            self.assertEqual(run.data["midi"]["decoder"]["actions"], 9)
            self.assertEqual(run.data["midi"]["retirements"], 1,
                             "CC123 must not retire the source or invoke global Panic")

    def test_fault_discard_and_fresh_epoch_barriers_preserve_ui_owner(self) -> None:
        events = [bytes_event(0, 0x91, 70, 100), (0, "fault backend"), (50, "connect"),
                  bytes_event(150, 0x90, 67, 100), bytes_event(150, 0x91, 64, 100),
                  bytes_event(150, 0x92, 36, 100), bytes_event(450, 0x91, 65, 100),
                  bytes_event(450, 0x81, 64, 0), (450, "fault backend"),
                  bytes_event(450, 0x91, 70, 100), bytes_event(650, 0x91, 70, 100),
                  (800, "connect"), bytes_event(800, 0x91, 66, 100),
                  (1100, "connect"), bytes_event(1100, 0x91, 67, 100),
                  (1400, "disconnect"), (1400, "connect"), bytes_event(1400, 0x92, 60, 100)]
        with self.run_native(1750, events, ui_events=[(100, "key_down A none 0")]) as run:
            self.assert_window(run, 150, 430, ((60, 67), (64,), (1,)))
            self.assert_window(run, 450, 780, ((60,), (), ()))
            self.assert_window(run, 800, 1080, ((60,), (66,), ()))
            self.assert_window(run, 1100, 1380, ((60,), (67,), ()))
            self.assert_final(run, ((60,), (), (25,)), on=7)
            self.assertEqual(run.midi["connections_started"], 4)
            self.assertEqual(run.midi["connect_barriers"], 2)
            self.assertGreater(run.midi["barrier_wait_turns"], 0)
            self.assertEqual(run.midi["ignored_while_closed"], 3)
            self.assertEqual(run.midi["discarded_queued_packets"], 2)
            self.assertEqual(run.midi["rejected_packets"], 0)
            self.assertEqual(run.midi["faults_while_closed"], 1)
            self.assertEqual(run.midi["cancelled_connects"], 0)
            self.assertEqual(run.data["midi"]["retired_fault_bits"], 6)
            self.assertEqual(run.data["midi"]["fault_retirements"], 1)
            self.assertEqual(run.data["midi"]["release_batches"], 4)
            for item in run.midi["observations"]:
                self.assertNotIn(65, item["manual_notes"][1], "Queued pre-fault On escaped retirement")
                self.assertNotIn(70, item["manual_notes"][1], "Closed input was replayed after reconnect")

    def test_full_inbox_drains_in_bounded_batches_without_overflow(self) -> None:
        events = [(0, "connect")] + [bytes_event(150, status, 60, velocity)
                  for _ in range(128) for status, velocity in ((0x90, 100), (0x80, 0))]
        with self.run_native(1000, events) as run:
            self.assert_final(run, EMPTY, on=128, off=128)
            self.assertEqual(run.data["midi"]["maximum_drained_per_turn"], 32)
            self.assertEqual(run.midi["accepted_packets"], 256)
            self.assertEqual(run.data["midi"]["decoder"]["packets"], 256)
            self.assertEqual(run.midi["dropped_packets"], 0)
            self.assertEqual(run.midi["intentional_overflow_faults"], 0)
            self.assertEqual(run.data["midi"]["fault_retirements"], 0)

    def test_real_overflow_discards_stale_packets_and_requires_reconnect(self) -> None:
        events = [(0, "connect"), bytes_event(150, 0x90, 67, 100),
                  bytes_event(150, 0x91, 64, 100), bytes_event(150, 0x92, 36, 100)]
        events += [bytes_event(500, status, pitch, velocity) for _ in range(300)
                   for status, pitch, velocity in ((0x90, 64, 100), (0x80, 67, 0))]
        events += [bytes_event(850, 0x91, 70, 100), (1100, "connect"), bytes_event(1100, 0x91, 69, 100)]
        with self.run_native(1450, events, ui_events=[(100, "key_down A none 0")]) as run:
            self.assert_window(run, 150, 480, ((60, 67), (64,), (1,)))
            self.assert_window(run, 500, 1080, ((60,), (), ()))
            self.assert_final(run, ((60,), (69,), ()), on=5)
            self.assertEqual(run.midi["intentional_overflow_faults"], 1)
            self.assertEqual(run.midi["accepted_packets"], 260)
            self.assertEqual(run.midi["rejected_packets"], 1)
            self.assertEqual(run.midi["discarded_queued_packets"], 256)
            self.assertEqual(run.midi["ignored_while_closed"], 344)
            self.assertEqual(run.midi["maximum_events_per_turn"], 512)
            self.assertGreaterEqual(run.midi["budget_exhaustions"], 1)
            self.assertEqual(run.data["midi"]["decoder"]["packets"], 4)
            self.assertEqual(run.data["midi"]["retired_fault_bits"], 1)
            self.assertEqual(run.data["midi"]["fault_retirements"], 1)
            self.assertEqual(run.data["midi"]["release_batches"], 2)
            self.assertEqual(run.midi["connections_started"], 2)
            for item in run.midi["observations"]:
                self.assertNotIn(64, item["manual_notes"][0], "A stale burst On survived overflow")
                self.assertNotIn(70, item["manual_notes"][1], "Input reconnected without an explicit request")

    def test_focus_resize_help_and_midi_apply_preserve_external_owners(self) -> None:
        events = [(0, "connect"), bytes_event(150, 0x90, 67, 100),
                  bytes_event(150, 0x91, 64, 100), bytes_event(150, 0x92, 36, 100)]
        ui = [(100, "key_down A none 0"), (400, "focus_lost"), (500, "resize 960 700")]
        ui += tap(600, "Slash", "shift") + tap(850, "Return") + tap(1000, "M", "ctrl")
        ui += tabs(1100, 2) + tap(1150, "End") + tabs(1200, 3) + tap(1300, "Return")
        ui += tap(1450, "Escape") + [(1550, "key_up A none")]
        with self.run_native(1750, events, ui_events=ui) as run:
            self.assert_window(run, 150, 380, ((60, 67), (64,), (1,)))
            self.assert_window(run, 400, 590, ((67,), (64,), (1,)))
            self.assert_window(run, 600, 990, ((67,), (64,), (1,)))
            self.assert_final(run, ((67,), (64,), (1,)), on=4)
            self.assertEqual(run.data["midi"]["channels"], {"upper": 1, "lower": 2, "pedals": 3})
            self.assertEqual(run.midi["connections_started"], 1)
            self.assertEqual(run.data["midi"]["retirements"], 1)
            self.assertTrue(run.midi["connected_before_shutdown"])
            self.assertEqual((run.data["runtime"]["window_width"], run.data["runtime"]["window_height"]), (960, 700))

    def test_global_panic_retires_midi_and_suppresses_old_ui_press(self) -> None:
        events = [(0, "connect"), bytes_event(150, 0x90, 64, 100),
                  bytes_event(150, 0x91, 67, 100), bytes_event(150, 0x92, 36, 100),
                  bytes_event(750, 0x91, 70, 100), (1100, "connect"), bytes_event(1100, 0x91, 65, 100)]
        ui = [(100, "key_down A none 0")] + click(500, 1228, 66)
        ui += [(850, "key_down A none 1"), (1000, "key_up A none"), (1300, "key_down A none 0")]
        with self.run_native(1650, events, ui_events=ui) as run:
            self.assert_window(run, 150, 480, ((60, 64), (67,), (1,)))
            self.assert_window(run, 500, 1080, EMPTY)
            self.assert_final(run, ((60,), (65,), ()), on=6)
            self.assertEqual(run.midi["ignored_while_closed"], 1)
            self.assertEqual(run.midi["connections_started"], 2)
            self.assertEqual(run.data["midi"]["release_batches"], 2)
            self.assertEqual(run.data["midi"]["fault_retirements"], 0)

    def test_audio_restart_retires_midi_preserves_controls_and_requires_reconnect(self) -> None:
        events = [(0, "connect"), bytes_event(150, 0x90, 64, 100),
                  bytes_event(150, 0x91, 67, 100), bytes_event(150, 0x92, 36, 100),
                  bytes_event(250, 0xB0, 11, 64), bytes_event(1100, 0x91, 70, 100),
                  (1350, "connect"), bytes_event(1350, 0x91, 69, 100)]
        ui = [(100, "key_down A none 0")] + tap(400, "Comma", "ctrl")
        ui += tabs(500, 2) + tap(550, "End") + tap(600, "Tab") + tap(650, "Home")
        ui += tap(700, "Tab") + tap(850, "Return")
        ui += [(1000, "key_up A none"), (1450, "key_down A none 0")]
        expected = deepcopy(DEFAULT_CONTROLS)
        expected["expression"] = 64 / 127
        with self.run_native(1800, events, ui_events=ui) as run:
            self.assert_window(run, 400, 830, ((64,), (67,), (1,)))
            self.assert_window(run, 850, 1330, EMPTY)
            self.assert_final(run, ((60,), (69,), ()), on=6, controls=expected)
            self.assertEqual(run.midi["device_starts"], 2)
            self.assertEqual(run.midi["connections_started"], 2)
            self.assertEqual(run.midi["ignored_while_closed"], 1)
            self.assertEqual(run.data["midi"]["release_batches"], 2)
            self.assertEqual(run.data["audio"]["sample_rate"], 96000)
            self.assertEqual(run.data["audio"]["buffer_frames"], 128)
            self.assertEqual(run.data["session"]["sample_rate"], 96000)

    def test_interruption_is_a_failed_replay_but_shutdown_still_joins(self) -> None:
        events = [(0, "connect"), bytes_event(150, 0x91, 64, 100), bytes_event(900, 0x91, 67, 100)]
        ui = [(100, "key_down A none 0"), (450, "quit"), (750, "key_down D none 0")]
        with self.run_native(1200, events, ui_events=ui, expected_exit=1) as run:
            self.assertFalse(run.midi["completed"])
            self.assertFalse(run.midi["passed"])
            self.assertFalse(run.midi["delivered"])
            self.assertFalse(run.data["replay"]["completed"])
            self.assertFalse(run.data["replay"]["passed"])
            self.assertEqual(run.midi["delivered_events"], 2)
            self.assertEqual(run.midi["accepted_note_on_commands"], 2)
            self.assertEqual(held(run.midi["before_shutdown"]), ((60,), (64,), ()))
            self.assertEqual(run.midi["failure_count"], 1)
            self.assertEqual(run.data["errors"]["count"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
