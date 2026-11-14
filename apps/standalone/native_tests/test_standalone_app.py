#!/usr/bin/env python3
"""Acceptance of the real native executable; no SDL or Engine test double.

Required: HAMMOND_STANDALONE_EXECUTABLE names a built native application.
Every invocation selects its drivers explicitly and names a private state path.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import tempfile
import time
import unittest


SMOKE_MS = 600
PROCESS_TIMEOUT = 8.0
INVALID_DRIVER = "hammond_acceptance_nonexistent_driver"
PROFILE = {
    "id": "nominal-unmeasured-v1",
    "authoring_sha256": "49791eac8d0b556b0abd2018b8cabc6f240161edab8a9fa0ef97905f2badda83",
}
DEFAULT_PERCUSSION = {"enabled": False, "harmonic": 0, "volume": 0, "decay": 0}
AUDITION_CONTROLS = {
    "manual_drawbars": [
        [[0] * 9, [8, 8, 8, 0, 0, 0, 0, 0, 0]],
        [[0] * 9, [0, 0, 8, 0, 0, 0, 0, 0, 0]],
    ],
    "selected_banks": [1, 1], "fixed_registrations": [0, 0], "preset_selections": [11, 11],
    "route_enabled": [True, True],
    "expression": 1,
    "pedal_drawbars": [8, 0],
    "percussion": DEFAULT_PERCUSSION,
}
VARIED_CONTROLS = {
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
# Literal grammar and expected fields are independent of production serialization.
MANUAL_RECORDS = """manual upper selected A route_enabled 0
bank A 0 1 2 3 4 5 6 7 8
bank B 8 7 6 5 4 3 2 1 0
manual lower selected B route_enabled 1
bank A 1 3 5 7 0 2 4 6 8
bank B 8 6 4 2 0 7 5 3 1
end
"""


def state_document(version: int = 3) -> bytes:
    text = f"B3CONTROLS{version}\nexpression +3.75e-1\n"
    if version >= 2:
        text += "percussion enabled 1 harmonic third volume soft decay fast\n"
    if version >= 3:
        text += "pedal drawbars 2 7\n"
    # Accepted noncanonical whitespace also exposes an unwanted exit-time save.
    return ("\t" + text + MANUAL_RECORDS + " \t\n").replace("\n", "\r\n").encode("ascii")


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate diagnostics member: {key}")
        result[key] = value
    return result


def reject_nonfinite(token: str) -> None:
    raise ValueError(f"Non-JSON numeric token: {token}")


MIDI_SCHEMA = {
    "source": str, "backend_available": bool, "backend": str,
    "requested_port": str, "port_name": str, "opened_port_index": int,
    "generation": int, "state_before_shutdown": str, "state_after_shutdown": str,
    "active_before_shutdown": bool, "active_after_shutdown": bool,
    "quiescent_after_shutdown": bool, "diagnostics_stable_after_shutdown": bool,
    "shutdown_failed": bool, "startup_failed": bool,
    "channels": {"upper": int, "lower": int, "pedals": int},
    "drain_budget": int, "maximum_drained_per_turn": int,
    "timing_policy": str, "arrival_time_unit": str, "arrival_time_source": str,
    "arrival_time_is_sample_time": bool, "retirements": int,
    "fault_retirements": int, "session_recoveries_observed": int,
    "open_failures": int, "submit_failures": int, "release_batches": int,
    "release_commands_accepted": int, "release_sequence": int,
    "release_pending": bool, "parameter_messages": int, "retired_fault_bits": int,
    "last_submit_status": str, "status": str,
    "discovery": {
        "requests": int, "started": int, "completed": int, "discarded_results": int,
        "failures": int, "pending_before_shutdown": bool, "shutdown_join_performed": bool,
        "pending_after_shutdown": bool,
    },
    "device": {
        "callback_messages": int, "forwarded_messages": int,
        "filtered_messages": int, "admission_failures": int,
        "backend_errors": int, "callback_contentions": int,
        "disconnects": int, "close_errors": int, "last_arrival_ns": int,
    },
    "inbox": {
        "capacity": int, "pending_packets": int, "received_packets": int,
        "accepted_packets": int, "invalid_size_packets": int,
        "faulted_packets": int, "overflow_events": int, "popped_packets": int,
        "discarded_packets": int, "resets": int, "fault_bits": int,
    },
    "decoder": {
        "packets": int, "actions": int, "unsupported": int,
        "unmapped_channels": int, "out_of_range": int, "malformed": int,
        "inactive": int, "timestamp_regressions": int, "epochs": int,
    },
}


@dataclass(frozen=True)
class ArraySchema:
    element: object


@dataclass(frozen=True)
class NullableSchema:
    element: object


def assert_schema(case: unittest.TestCase, value: object, schema: object, name: str = "$") -> None:
    """Exact keys and types; in particular, bool never satisfies an int field."""
    if isinstance(schema, NullableSchema):
        if value is not None:
            assert_schema(case, value, schema.element, name)
    elif isinstance(schema, ArraySchema):
        case.assertIs(type(value), list, name)
        for index, child in enumerate(value):
            assert_schema(case, child, schema.element, f"{name}[{index}]")
    elif isinstance(schema, dict):
        case.assertIs(type(value), dict, name)
        case.assertEqual(set(value), set(schema), name)
        for key, child in schema.items():
            assert_schema(case, value[key], child, f"{name}.{key}")
    elif isinstance(schema, list):
        case.assertIs(type(value), list, name)
        case.assertEqual(len(value), len(schema), name)
        for index, child in enumerate(schema):
            assert_schema(case, value[index], child, f"{name}[{index}]")
    elif schema == "number":
        case.assertIn(type(value), (int, float), name)
        case.assertTrue(math.isfinite(value), name)
    else:
        case.assertIs(type(value), schema, name)


def assert_no_midi_input(case: unittest.TestCase, report: dict) -> None:
    """No selected port or replay: the native transport must stay unopened.

    A compiled backend is allowed. These UI-only runs must neither enumerate
    hardware nor construct/open a native MIDI input; the exact inert state,
    empty stderr and zero lifetime counters remain required in either build.
    """
    midi = report["midi"]
    assert_schema(case, midi, MIDI_SCHEMA, "$.midi")
    case.assertNotIn("midi_replay", report)
    available = midi["backend_available"]
    if available:
        case.assertIn(midi["backend"], ("ALSA", "CoreMIDI", "WinMM"))
    else:
        case.assertEqual(midi["backend"], "unavailable")
    case.assertEqual(midi, {
        "source": "none", "backend_available": available, "backend": midi["backend"],
        "requested_port": "", "port_name": "", "opened_port_index": 0,
        "generation": 0, "state_before_shutdown": "closed" if available else "unavailable",
        "state_after_shutdown": "closed" if available else "unavailable",
        "active_before_shutdown": False, "active_after_shutdown": False,
        "quiescent_after_shutdown": True, "diagnostics_stable_after_shutdown": True,
        "shutdown_failed": False, "startup_failed": False,
        "channels": {"upper": 1, "lower": 2, "pedals": 3},
        "drain_budget": 32, "maximum_drained_per_turn": 0,
        "timing_policy": "arrival_order_next_callback_boundary",
        "arrival_time_unit": "steady_clock_nanoseconds", "arrival_time_source": "none",
        "arrival_time_is_sample_time": False, "retirements": 0,
        "fault_retirements": 0, "session_recoveries_observed": 0,
        "open_failures": 0, "submit_failures": 0, "release_batches": 0,
        "release_commands_accepted": 0, "release_sequence": 0,
        "release_pending": False, "parameter_messages": 0, "retired_fault_bits": 0,
        "last_submit_status": "ok",
        "status": "No MIDI input selected." if available else "MIDI backend unavailable in this build.",
        "discovery": {
            "requests": 0, "started": 0, "completed": 0, "discarded_results": 0,
            "failures": 0, "pending_before_shutdown": False, "shutdown_join_performed": False,
            "pending_after_shutdown": False,
        },
        "device": {
            "callback_messages": 0, "forwarded_messages": 0, "filtered_messages": 0,
            "admission_failures": 0, "backend_errors": 0, "callback_contentions": 0,
            "disconnects": 0, "close_errors": 0, "last_arrival_ns": 0,
        },
        "inbox": {
            "capacity": 256, "pending_packets": 0, "received_packets": 0,
            "accepted_packets": 0, "invalid_size_packets": 0, "faulted_packets": 0,
            "overflow_events": 0, "popped_packets": 0, "discarded_packets": 0,
            "resets": 0, "fault_bits": 0,
        },
        "decoder": {
            "packets": 0, "actions": 0, "unsupported": 0, "unmapped_channels": 0,
            "out_of_range": 0, "malformed": 0, "inactive": 0,
            "timestamp_regressions": 0, "epochs": 0,
        },
    })


PRESENTATION_FRAME_SCHEMA = {
    "elapsed_ms": int, "rendered_image": int, "workspace": str,
    "presentation": str, "overlay": str, "window_width": int, "window_height": int,
    "inspection": {
        "snapshot_available": bool, "snapshot_read_succeeded": bool,
        "snapshot_state": str, "controls_pending": bool,
        "frame_clock": int, "publication_revision": int,
    },
}
PRESENTATION_SCHEMA = {
    "initial_workspace": str, "initial_presentation": str,
    "observation_capacity": int, "observations_truncated": bool,
    "last_painted": NullableSchema(PRESENTATION_FRAME_SCHEMA),
    "screenshot": NullableSchema(PRESENTATION_FRAME_SCHEMA),
    "before_shutdown": NullableSchema(PRESENTATION_FRAME_SCHEMA),
    "observations": ArraySchema(PRESENTATION_FRAME_SCHEMA),
}


def assert_presentation(case: unittest.TestCase, report: dict) -> None:
    presentation = report["presentation"]
    assert_schema(case, presentation, PRESENTATION_SCHEMA, "$.presentation")
    case.assertIn(presentation["initial_workspace"], ("play", "rotary", "service"))
    case.assertIn(presentation["initial_presentation"], ("dimensional", "flat"))
    case.assertEqual(presentation["observation_capacity"], 512)
    case.assertLessEqual(len(presentation["observations"]), 512)
    case.assertEqual(presentation["before_shutdown"], presentation["last_painted"])
    case.assertEqual(presentation["screenshot"] is not None, report["runtime"]["screenshot_written"])
    case.assertEqual(presentation["last_painted"] is not None, report["runtime"]["rendered_images"] > 0)
    if presentation["last_painted"] is not None:
        case.assertEqual(presentation["last_painted"]["rendered_image"], report["runtime"]["rendered_images"])
    last_image = 0
    last_elapsed = 0
    for frame in presentation["observations"]:
        case.assertGreater(frame["rendered_image"], last_image)
        case.assertGreaterEqual(frame["elapsed_ms"], last_elapsed)
        last_image, last_elapsed = frame["rendered_image"], frame["elapsed_ms"]
    for frame in [*presentation["observations"], presentation["last_painted"],
                  presentation["screenshot"], presentation["before_shutdown"]]:
        if frame is None:
            continue
        case.assertIn(frame["workspace"], ("play", "rotary", "service"))
        case.assertIn(frame["presentation"], ("dimensional", "flat"))
        case.assertIn(frame["overlay"], ("none", "help", "audio", "midi"))
        case.assertGreaterEqual(frame["window_width"], 960)
        case.assertGreaterEqual(frame["window_height"], 700)
        case.assertLessEqual(max(frame["window_width"], frame["window_height"]), 8192)
        case.assertGreater(frame["rendered_image"], 0)
        case.assertLessEqual(frame["rendered_image"], report["runtime"]["rendered_images"])
        observation = frame["inspection"]
        case.assertIn(observation["snapshot_state"], ("unavailable", "unprepared", "retained", "stopped", "current"))
        case.assertGreaterEqual(observation["frame_clock"], 0)
        case.assertGreaterEqual(observation["publication_revision"], 0)
        if not observation["snapshot_available"]:
            case.assertEqual(observation["snapshot_state"], "unavailable")
            case.assertEqual(observation["frame_clock"], 0)
            case.assertEqual(observation["publication_revision"], 0)
        else:
            case.assertNotEqual(observation["snapshot_state"], "unavailable")
        if observation["snapshot_state"] == "retained":
            case.assertFalse(observation["snapshot_read_succeeded"])
        if observation["snapshot_state"] in ("current", "stopped"):
            case.assertTrue(observation["snapshot_read_succeeded"])


SCHEMA = {
    "schema_version": int,
    "application": str,
    "profile": {"id": str, "authoring_sha256": str},
    "runtime": {
        "video_driver": str, "renderer": str, "sdl_version": str,
        "window_width": int, "window_height": int,
        "drawable_width": int, "drawable_height": int, "rendered_images": int,
        "screenshot_written": bool, "screenshot_while_held": bool,
    },
    "audio": {
        "driver": str, "device_name": str, "requested_device": str,
        "requested_sample_rate": int, "requested_buffer_frames": int,
        "sample_rate": int, "buffer_frames": int, "channels": int,
        "sample_format": int, "native_float32_format": int, "buffer_bytes": int,
        "open_before_shutdown": bool, "running_before_shutdown": bool,
        "callback_count": int, "rendered_frames": int, "render_failures": int,
        "format_failures": int, "overrange_failures": int, "overrange_samples": int,
        "nonfinite_failures": int, "nonfinite_samples": int,
        "last_render_status": str, "last_lifecycle_status": str,
    },
    "midi": MIDI_SCHEMA,
    "presentation": PRESENTATION_SCHEMA,
    "session": {
        "snapshot_available": bool, "prepared": bool, "running_after_shutdown": bool,
        "sample_rate": "number", "frame_clock": int, "publication_revision": int,
        "resolved_sequence": int, "last_applied_sequence": int, "recovery_count": int,
        "queue_overflows": int, "rejected_commands": int, "discarded_commands": int,
        "fault_flags": int, "held_after_shutdown": bool, "maximum_observed_peak": "number",
    },
    "controls": {
        "manual_drawbars": [[[int] * 9, [int] * 9], [[int] * 9, [int] * 9]],
        "selected_banks": [int, int], "fixed_registrations": [int, int], "preset_selections": [int, int], "route_enabled": [bool, bool],
        "expression": "number", "pedal_drawbars": [int, int],
        "percussion": {"enabled": bool, "harmonic": int, "volume": int, "decay": int},
    },
    "smoke": {
        "requested": bool, "duration_ms": int, "completed": bool,
        "note_on_sent": bool, "note_off_sent": bool,
        "held_observed": bool, "release_observed": bool, "passed": bool,
    },
    "state_path": str, "status": str, "errors": {"count": int, "last": str},
}
AUDIO_ERRORS = (
    "render_failures", "format_failures", "overrange_failures", "overrange_samples",
    "nonfinite_failures", "nonfinite_samples",
)
NUMERIC_OPTIONS = {
    "--sample-rate": "48000", "--buffer-frames": "512", "--width": "1280",
    "--height": "900", "--smoke-ms": "600",
}
SUMMARY = re.compile(
    r"Native SDL smoke (passed|failed): callbacks=(\d+), frames=(\d+), "
    r"images=(\d+), driver=([^\r\n]*)\r?\n"
)


@dataclass(frozen=True)
class Run:
    process: subprocess.CompletedProcess[str]
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


class NativeAppAcceptance(unittest.TestCase):
    invocations = 0

    @classmethod
    def setUpClass(cls) -> None:
        configured = os.environ.get("HAMMOND_STANDALONE_EXECUTABLE", "")
        if not configured:
            raise RuntimeError("HAMMOND_STANDALONE_EXECUTABLE is required; build the native target first")
        cls.executable = Path(configured).resolve(strict=True)
        if not cls.executable.is_file() or not os.access(cls.executable, os.X_OK):
            raise RuntimeError(f"Required native executable is not executable: {cls.executable}")
        print(f"Native executable SHA-256: {hashlib.sha256(cls.executable.read_bytes()).hexdigest()}", flush=True)

    @classmethod
    def tearDownClass(cls) -> None:
        print(f"Actual native application subprocesses: {cls.invocations}", flush=True)

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="hammond-native-app-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    @staticmethod
    def environment(audio: str = "dummy", video: str = "dummy") -> dict[str, str]:
        environment = os.environ.copy()
        environment.update(SDL_AUDIODRIVER=audio, SDL_VIDEODRIVER=video)
        return environment

    def invoke(self, arguments: list[str], expected: int = 0, *,
               audio: str = "dummy", video: str = "dummy", timeout: float = PROCESS_TIMEOUT) -> Run:
        self.assertIn("--state", arguments, "Every application invocation must name its private state")
        self.__class__.invocations += 1
        started = time.monotonic()
        try:
            process = subprocess.run(
                [str(self.executable), *arguments], cwd=self.root,
                env=self.environment(audio, video), stdin=subprocess.DEVNULL,
                capture_output=True, encoding="utf-8", errors="strict", timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            self.fail(f"Native subprocess exceeded {timeout}s: {arguments!r}; {error}")
        elapsed = time.monotonic() - started
        evidence = ""
        if process.returncode != expected and "--diagnostics" in arguments:
            index = arguments.index("--diagnostics") + 1
            if index < len(arguments):
                evidence = diagnostic_excerpt(Path(arguments[index]))
        self.assertEqual(process.returncode, expected,
                         f"Arguments: {arguments!r}\nElapsed: {elapsed:.3f}s\n"
                         f"stdout: {process.stdout}\nstderr: {process.stderr}\n{evidence}")
        return Run(process, elapsed)

    def tree_snapshot(self) -> dict[str, tuple]:
        entries = {}
        for path in self.root.rglob("*"):
            relative = path.relative_to(self.root).as_posix()
            if path.is_symlink():
                entries[relative] = ("symlink", os.readlink(path))
            elif path.is_file():
                entries[relative] = ("file", path.read_bytes(), path.stat().st_mtime_ns)
            elif path.is_dir():
                entries[relative] = ("directory",)
        return entries

    def guarded_paths(self) -> dict[str, Path]:
        paths = {
            "--state": self.root / "musical controls.b3controls",
            "--screenshot": self.root / "existing image.bmp",
            "--diagnostics": self.root / "existing diagnostics.json",
        }
        paths["--state"].write_bytes(state_document())
        paths["--screenshot"].write_bytes(b"existing screenshot must survive\x00")
        paths["--diagnostics"].write_bytes(b"existing diagnostics must survive\x00")
        return paths

    @staticmethod
    def cli_arguments(paths: dict[str, Path], extra: list[str], omit: str = "") -> list[str]:
        arguments = []
        for option, path in paths.items():
            if option != omit:
                arguments += [option, str(path)]
        if omit != "--smoke-ms":
            arguments += ["--smoke-ms", str(SMOKE_MS)]
        return arguments + extra

    def reject_cli(self, paths: dict[str, Path], extra: list[str], message: str, omit: str = "") -> None:
        before = self.tree_snapshot()
        run = self.invoke(self.cli_arguments(paths, extra, omit), expected=2,
                          audio=INVALID_DRIVER, video=INVALID_DRIVER, timeout=3.0)
        self.assertEqual(run.process.stdout, "")
        self.assertIn(message, run.process.stderr)
        self.assertNotIn("Cannot initialize", run.process.stderr)
        self.assertEqual(self.tree_snapshot(), before, "Rejected CLI changed an output or state file")

    @staticmethod
    def smoke_arguments(state: Path, diagnostics: Path, screenshot: Path | None = None,
                        extra: list[str] | None = None) -> list[str]:
        arguments = ["--state", str(state), "--smoke-ms", str(SMOKE_MS),
                     "--diagnostics", str(diagnostics)]
        if screenshot is not None:
            arguments += ["--screenshot", str(screenshot)]
        return arguments + (extra or [])

    def diagnostics(self, path: Path, state: Path, *,
                    workspace: str = "play", presentation: str = "dimensional") -> dict:
        report = json.loads(path.read_text(encoding="utf-8"),
                            object_pairs_hook=unique_object, parse_constant=reject_nonfinite)
        assert_schema(self, report, SCHEMA)
        self.assertEqual(report["schema_version"], 3)
        assert_no_midi_input(self, report)
        assert_presentation(self, report)
        self.assertEqual(report["presentation"]["initial_workspace"], workspace)
        self.assertEqual(report["presentation"]["initial_presentation"], presentation)
        self.assertEqual(report["presentation"]["before_shutdown"]["workspace"], workspace)
        self.assertEqual(report["presentation"]["before_shutdown"]["presentation"], presentation)
        self.assertEqual(report["application"], "hammond_standalone")
        self.assertEqual(report["profile"], PROFILE)
        self.assertEqual(report["state_path"], str(state))
        self.assertEqual(report["runtime"]["video_driver"], "dummy")
        self.assertEqual(report["runtime"]["renderer"], "software")
        self.assertEqual(report["runtime"]["sdl_version"], "2.32.10")
        for section in ("runtime", "audio", "session", "errors"):
            for key, value in report[section].items():
                if type(value) is int:
                    self.assertGreaterEqual(value, 0, f"{section}.{key}")
                    self.assertLess(value, 1 << 64, f"{section}.{key}")
        controls = report["controls"]
        for manual in controls["manual_drawbars"]:
            for bank in manual:
                self.assertTrue(all(0 <= position <= 8 for position in bank))
        self.assertTrue(all(0 <= position <= 8 for position in controls["pedal_drawbars"]))
        self.assertTrue(all(bank in (0, 1) for bank in controls["selected_banks"]))
        self.assertTrue(all(0 <= fixed <= 9 for fixed in controls["fixed_registrations"]))
        self.assertEqual(controls["preset_selections"], [
            0 if not enabled else fixed if fixed else 10 + bank
            for bank, fixed, enabled in zip(controls["selected_banks"],
                controls["fixed_registrations"], controls["route_enabled"], strict=True)])
        self.assertTrue(all(controls["percussion"][key] in (0, 1)
                            for key in ("harmonic", "volume", "decay")))
        self.assertGreaterEqual(controls["expression"], 0)
        self.assertLessEqual(controls["expression"], 1)
        self.assertGreaterEqual(report["session"]["maximum_observed_peak"], 0)
        self.assertLessEqual(report["session"]["maximum_observed_peak"], 1)
        self.assertFalse(report["session"]["running_after_shutdown"])
        self.assertFalse(report["session"]["held_after_shutdown"])
        self.assertEqual(report["audio"]["native_float32_format"],
                         0x8120 if sys.byteorder == "little" else 0x9120)
        self.assertTrue(report["smoke"]["requested"])
        self.assertEqual(report["smoke"]["duration_ms"], SMOKE_MS)
        return report

    def assert_summary(self, run: Run, report: dict, passed: bool) -> None:
        match = SUMMARY.fullmatch(run.process.stdout)
        self.assertIsNotNone(match, run.process.stdout)
        outcome, callbacks, frames, images, driver = match.groups()
        self.assertEqual(outcome, "passed" if passed else "failed")
        self.assertEqual(int(callbacks), report["audio"]["callback_count"])
        self.assertEqual(int(frames), report["audio"]["rendered_frames"])
        self.assertEqual(int(images), report["runtime"]["rendered_images"])
        self.assertEqual(driver, report["audio"]["driver"])
        # SDL's 600 ms event interval excludes setup/join; retain broad elapsed
        # bounds, never an expected scheduler-dependent callback/image count.
        self.assertGreaterEqual(run.elapsed, SMOKE_MS / 1000 * 0.9)
        self.assertLess(run.elapsed, PROCESS_TIMEOUT)

    def assert_active_shutdown(self, report: dict, rate: int = 48000, buffer: int = 512) -> None:
        audio, session = report["audio"], report["session"]
        self.assertEqual(audio["driver"], "dummy")
        self.assertEqual(audio["device_name"], "Default output")
        self.assertEqual(audio["requested_device"], "")
        self.assertEqual(audio["requested_sample_rate"], rate)
        self.assertEqual(audio["sample_rate"], rate)
        self.assertEqual(audio["requested_buffer_frames"], buffer)
        self.assertEqual(audio["buffer_frames"], buffer)
        self.assertEqual(audio["channels"], 2)
        self.assertEqual(audio["sample_format"], audio["native_float32_format"])
        self.assertEqual(audio["buffer_bytes"], buffer * 2 * 4)
        self.assertTrue(audio["open_before_shutdown"])
        self.assertTrue(audio["running_before_shutdown"])
        self.assertGreater(audio["callback_count"], 0)
        self.assertEqual(audio["rendered_frames"], audio["callback_count"] * buffer)
        for key in AUDIO_ERRORS:
            self.assertEqual(audio[key], 0, key)
        self.assertEqual(audio["last_render_status"], "ok")
        self.assertEqual(audio["last_lifecycle_status"], "ok")
        self.assertTrue(session["snapshot_available"])
        self.assertTrue(session["prepared"])
        self.assertEqual(session["sample_rate"], rate)
        self.assertEqual(session["frame_clock"], audio["rendered_frames"])
        self.assertEqual(session["publication_revision"] % 2, 0)
        self.assertGreaterEqual(session["publication_revision"], audio["callback_count"] * 2)
        self.assertGreaterEqual(session["last_applied_sequence"], 3)
        self.assertGreaterEqual(session["resolved_sequence"], session["last_applied_sequence"])
        # A queued shutdown release may be discarded after the actual callback
        # join. A nonzero discard is not itself a native smoke failure.
        self.assertLessEqual(session["discarded_commands"], session["resolved_sequence"])
        self.assertEqual(session["resolved_sequence"] - session["last_applied_sequence"],
                         session["discarded_commands"])
        for key in ("recovery_count", "queue_overflows", "rejected_commands", "fault_flags"):
            self.assertEqual(session[key], 0, key)
        self.assertGreater(report["runtime"]["rendered_images"], 0)
        for key in ("completed", "note_on_sent", "note_off_sent", "held_observed", "release_observed"):
            self.assertTrue(report["smoke"][key], key)

    def assert_success(self, run: Run, report: dict, controls: dict = AUDITION_CONTROLS,
                       rate: int = 48000, buffer: int = 512, allow_startup_error: bool = False) -> None:
        self.assert_active_shutdown(report, rate, buffer)
        self.assertTrue(report["smoke"]["passed"])
        self.assert_summary(run, report, True)
        self.assertEqual(report["controls"], controls)
        if not allow_startup_error:
            self.assertEqual(report["errors"], {"count": 0, "last": ""})
            self.assertEqual(run.process.stderr, "")

    def assert_bmp(self, path: Path, width: int, height: int, *, held_middle_c: bool = False) -> None:
        data = path.read_bytes()
        self.assertGreaterEqual(len(data), 54)
        self.assertEqual(data[:2], b"BM")
        size, reserved1, reserved2, offset = struct.unpack_from("<IHHI", data, 2)
        header_size, actual_width, actual_height, planes, bits, compression = struct.unpack_from("<IiiHHI", data, 14)
        self.assertEqual(size, len(data))
        self.assertEqual((reserved1, reserved2), (0, 0))
        self.assertIn(header_size, (40, 108, 124))
        self.assertGreaterEqual(offset, 14 + header_size)
        self.assertEqual((actual_width, abs(actual_height)), (width, height))
        self.assertEqual(planes, 1)
        self.assertIn(bits, (24, 32))
        self.assertIn(compression, (0, 3))
        stride = ((width * bits + 31) // 32) * 4
        self.assertEqual(len(data) - offset, stride * height)
        colors = set()
        bytes_per_pixel = bits // 8
        for y in range(0, height, max(1, height // 40)):
            row = offset + y * stride
            for x in range(0, width, max(1, width // 60)):
                start = row + x * bytes_per_pixel
                colors.add(data[start:start + 3])
        self.assertGreater(len(colors), 8, "Rendered screenshot is blank or nearly uniform")
        if held_middle_c:
            # Literal interior points below the upper manual's accidentals in
            # the preset-key layout. The playing keyboard begins at (200,496)
            # with 1056 units of natural-key width at 1280x900, or (188,424)
            # with width748 at960x700. The preset rail now exists at both sizes.
            # C4/D4/E4 are naturals14/15/16. Actual held captures verify these
            # interior points; each
            # invocation still checks its own new BMP, never a retained image.
            # No production layout/paint code or diagnostic flag is imported.
            c4, d4, e4, y = {(1280, 900): (625, 655, 684, 580),
                              (960, 700): (489, 510, 531, 466)}[(width, height)]
            row = offset + (height - 1 - y if actual_height > 0 else y) * stride
            def pixel(x: int) -> bytes:
                start = row + x * bytes_per_pixel
                return data[start:start + 3]
            self.assertEqual(pixel(d4), pixel(e4), "Reference unheld white keys differ")
            self.assertNotEqual(pixel(c4), pixel(d4),
                                "The screenshot did not paint Upper MIDI 60 as held")

    def test_help_does_not_initialize_either_driver_or_write_files(self) -> None:
        paths = self.guarded_paths()
        before = self.tree_snapshot()
        run = self.invoke(self.cli_arguments(paths, ["--help"]),
                          audio=INVALID_DRIVER, video=INVALID_DRIVER, timeout=3.0)
        self.assertIn("Usage: hammond_standalone", run.process.stdout)
        for option in ("--help", "--list-audio", "--device", "--workspace", "--flat", *NUMERIC_OPTIONS, *paths):
            self.assertIn(option, run.process.stdout)
        self.assertIn("F4/F5/F6", run.process.stdout)
        self.assertIn("F7", run.process.stdout)
        self.assertIn("never automatic", run.process.stdout)
        self.assertEqual(run.process.stderr, "")
        self.assertEqual(self.tree_snapshot(), before)
        # Leading decimal zeroes are accepted; the CLI contract does not ban them.
        run = self.invoke(self.cli_arguments(paths, ["--help", "--width", "0960"]),
                          audio=INVALID_DRIVER, video=INVALID_DRIVER, timeout=3.0)
        self.assertIn("Usage: hammond_standalone", run.process.stdout)
        self.assertEqual(self.tree_snapshot(), before)

    def test_list_audio_needs_no_video_or_file_writes(self) -> None:
        paths = self.guarded_paths()
        before = self.tree_snapshot()
        run = self.invoke(self.cli_arguments(paths, ["--list-audio"]), video=INVALID_DRIVER, timeout=3.0)
        lines = run.process.stdout.splitlines()
        self.assertEqual(lines[:2], ["SDL audio driver: dummy", "Default output: omit --device"])
        self.assertGreaterEqual(len(lines), 3)
        for index, line in enumerate(lines[2:], 1):
            self.assertRegex(line, rf"^{index}: .+$")
        self.assertEqual(run.process.stderr, "")
        self.assertEqual(self.tree_snapshot(), before)

    def test_unknown_and_combined_options_reject_before_output(self) -> None:
        paths = self.guarded_paths()
        for option in ("--unknown", "--width=960", "--sample-rate=48000", "--", "positional", "-h", "--Help"):
            with self.subTest(option=option):
                self.reject_cli(paths, [option], "Unknown option")

    def test_duplicate_options_reject_before_output(self) -> None:
        paths = self.guarded_paths()
        for option in ("--help", "--list-audio", "--flat"):
            with self.subTest(option=option):
                self.reject_cli(paths, [option, option], "Repeated option")
        values = {**NUMERIC_OPTIONS, "--device": "Default output", "--workspace": "service",
                  **{option: str(path) for option, path in paths.items()}}
        for option, value in values.items():
            with self.subTest(option=option):
                self.reject_cli(paths, [option, value, option, value], "Repeated option", option)

    def test_missing_and_empty_values_reject_before_output(self) -> None:
        paths = self.guarded_paths()
        for option in (*NUMERIC_OPTIONS, "--device", "--workspace", *paths):
            for suffix in ([], [""]):
                with self.subTest(option=option, empty=bool(suffix)):
                    self.reject_cli(paths, [option, *suffix], "Missing value", option)

    def test_noninteger_and_overflow_values_reject_before_output(self) -> None:
        paths = self.guarded_paths()
        for option, value in NUMERIC_OPTIONS.items():
            tokens = (f"+{value}", f"-{value}", f" {value}", f"{value} ", f"\t{value}",
                      f"{value}.0", f"{value}e0", hex(int(value)), f"{value}x", "nan", "inf",
                      "1_000", "١٢٨", "2147483648", "99999999999999999999999999999999999999")
            for token in tokens:
                with self.subTest(option=option, token=token):
                    self.reject_cli(paths, [option, token], "Invalid integer", option)

    def test_unsupported_numeric_values_reject_before_output(self) -> None:
        paths = self.guarded_paths()
        rejected = {
            "--sample-rate": (0, 44099, 44101, 48001, 96001),
            "--buffer-frames": (0, 127, 129, 2049),
            "--width": (0, 959, 8193), "--height": (0, 699, 8193),
            "--smoke-ms": (0, 249, 10001),
        }
        for option, values in rejected.items():
            for value in values:
                with self.subTest(option=option, value=value):
                    self.reject_cli(paths, [option, str(value)], "Unsupported value", option)

    def test_invalid_workspaces_reject_before_device_or_output(self) -> None:
        paths = self.guarded_paths()
        for value in ("Play", "SERVICE", "rotary ", " service", "flat", "unknown", "0", "3", "--flat"):
            with self.subTest(value=value):
                self.reject_cli(paths, ["--workspace", value], "Unsupported value for --workspace")

    def test_workspace_and_flat_startup_preserve_controls_and_actual_painted_view(self) -> None:
        for workspace in ("play", "rotary", "service"):
            for presentation in ("dimensional", "flat"):
                with self.subTest(workspace=workspace, presentation=presentation):
                    state = self.root / f"{workspace}-{presentation}.b3controls"
                    state.write_bytes(state_document())
                    diagnostics = self.root / f"{workspace}-{presentation}.json"
                    screenshot = self.root / f"{workspace}-{presentation}.bmp"
                    extra = ["--workspace", workspace]
                    if presentation == "flat":
                        extra += ["--flat"]
                    run = self.invoke(self.smoke_arguments(state, diagnostics, screenshot, extra))
                    report = self.diagnostics(diagnostics, state, workspace=workspace, presentation=presentation)
                    self.assert_success(run, report, VARIED_CONTROLS)
                    views = report["presentation"]
                    self.assertFalse(views["observations_truncated"])
                    self.assertEqual((views["screenshot"]["workspace"], views["screenshot"]["presentation"]),
                                     (workspace, presentation))
                    self.assertLessEqual(views["screenshot"]["rendered_image"], views["last_painted"]["rendered_image"])
                    self.assertIn(views["before_shutdown"]["inspection"]["snapshot_state"], ("current", "retained"))
                    self.assertGreater(views["before_shutdown"]["inspection"]["frame_clock"], 0)
                    self.assertFalse(views["before_shutdown"]["inspection"]["controls_pending"])
                    self.assert_bmp(screenshot, 1280, 900)
                    self.assertEqual(state.read_bytes(), state_document())

    def test_workspace_shortcuts_paint_views_preserve_holds_and_respect_modal_gate(self) -> None:
        state, diagnostics, screenshot, script = (self.root / name for name in
            ("absent.b3controls", "workspaces.json", "rotary-held.bmp", "workspaces.b3uireplay"))
        events = ["150 key_down A none 0"]
        for at, key, modifiers in (
            (250, "F5", "none"), (400, "F6", "none"), (550, "F7", "none"),
            (650, "F4", "ctrl"), (850, "Slash", "shift"), (950, "F4", "none"),
            (1050, "F7", "none"), (1150, "Escape", "none"), (1250, "F4", "none"),
            (1400, "F7", "none"), (1500, "F5", "none"),
        ):
            events += [f"{at} key_down {key} {modifiers} 0", f"{at + 10} key_up {key} {modifiers}"]
        events += ["750 key_up A alt", "1650 key_down A none 0"]
        events.sort(key=lambda event: int(event.split()[0]))
        script.write_text("B3UIREPLAY1\nduration_ms 1900\n" + "\n".join(events) + "\n", encoding="ascii")
        run = self.invoke(["--state", str(state), "--input-script", str(script),
                           "--diagnostics", str(diagnostics), "--screenshot", str(screenshot)])
        self.assertEqual(run.process.stderr, "")
        report = json.loads(diagnostics.read_text(encoding="utf-8"),
                            object_pairs_hook=unique_object, parse_constant=reject_nonfinite)
        assert_schema(self, report, {**SCHEMA, "replay": dict})
        assert_no_midi_input(self, report)
        assert_presentation(self, report)
        self.assertEqual(report["schema_version"], 3)
        self.assertEqual(report["errors"], {"count": 0, "last": ""})
        self.assertEqual(report["controls"], AUDITION_CONTROLS)
        self.assertFalse(report["session"]["running_after_shutdown"])
        self.assertFalse(report["session"]["held_after_shutdown"])
        replay = report["replay"]
        for flag in ("completed", "delivered", "passed", "final_acknowledged"):
            self.assertTrue(replay[flag], diagnostic_excerpt(report))
        self.assertEqual(replay["scheduled_events"], len(events))
        self.assertEqual(replay["pushed_events"], len(events))
        self.assertEqual(replay["accepted_note_on_commands"], 2)
        self.assertEqual(replay["accepted_note_off_commands"], 1)
        self.assertEqual(replay["before_shutdown"]["manual_notes"], [[60], []])
        self.assertEqual(replay["before_shutdown"]["pedal_ids"], [])
        self.assertEqual(replay["before_shutdown"]["controls"], AUDITION_CONTROLS)
        views = report["presentation"]
        self.assertFalse(views["observations_truncated"])
        transitions = []
        for observation in views["observations"]:
            value = tuple(observation[key] for key in ("workspace", "presentation", "overlay"))
            if not transitions or transitions[-1] != value:
                transitions.append(value)
        self.assertEqual(transitions, [
            ("play", "dimensional", "none"), ("rotary", "dimensional", "none"),
            ("service", "dimensional", "none"), ("service", "flat", "none"),
            ("service", "flat", "help"), ("service", "flat", "none"),
            ("play", "flat", "none"), ("play", "dimensional", "none"),
            ("rotary", "dimensional", "none"),
        ])
        self.assertEqual(views["before_shutdown"], views["screenshot"])
        self.assertEqual(views["before_shutdown"]["workspace"], "rotary")
        self.assertIn(views["before_shutdown"]["inspection"]["snapshot_state"], ("current", "retained"))
        self.assertTrue(report["runtime"]["screenshot_while_held"])
        self.assert_bmp(screenshot, 1280, 900)
        self.assertFalse(state.exists())

    def test_reference_minimum_and_extreme_audio_smokes(self) -> None:
        configurations = (
            (1280, 900, 48000, 512), (960, 700, 48000, 512),
            (1280, 900, 44100, 2048), (1280, 900, 96000, 128),
        )
        for index, (width, height, rate, buffer) in enumerate(configurations):
            with self.subTest(width=width, height=height, rate=rate, buffer=buffer):
                state = self.root / f"absent-{index}.b3controls"
                diagnostics = self.root / f"copied-{index}.json"
                screenshot = self.root / f"held-{index}.bmp"
                extra = [] if index == 0 else ["--width", str(width), "--height", str(height),
                                               "--sample-rate", str(rate), "--buffer-frames", str(buffer)]
                run = self.invoke(self.smoke_arguments(state, diagnostics, screenshot, extra))
                report = self.diagnostics(diagnostics, state)
                self.assert_success(run, report, rate=rate, buffer=buffer)
                runtime = report["runtime"]
                self.assertEqual([runtime[key] for key in ("window_width", "window_height", "drawable_width", "drawable_height")],
                                 [width, height, width, height])
                self.assertTrue(runtime["screenshot_written"])
                self.assertTrue(runtime["screenshot_while_held"], diagnostic_excerpt(report))
                self.assertGreater(report["session"]["maximum_observed_peak"], 0)
                self.assert_bmp(screenshot, width, height, held_middle_c=True)
                self.assertFalse(state.exists(), "Exiting the application saved musical controls")

    def test_saved_controls_and_legacy_startup_on_unicode_paths(self) -> None:
        directory = self.root / "état 音 registration files"
        directory.mkdir()
        for version in (1, 2, 3):
            with self.subTest(version=version):
                state = directory / f"保存 controls version {version}.b3controls"
                diagnostics = directory / f"copied état {version}.json"
                screenshot = directory / f"held 音 {version}.bmp"
                original = state_document(version)
                state.write_bytes(original)
                expected = dict(VARIED_CONTROLS)
                if version < 3:
                    expected["pedal_drawbars"] = [0, 0]
                if version < 2:
                    expected["percussion"] = DEFAULT_PERCUSSION
                run = self.invoke(self.smoke_arguments(state, diagnostics, screenshot))
                report = self.diagnostics(diagnostics, state)
                self.assert_success(run, report, expected)
                self.assertIn("Loaded saved controls", report["status"])
                self.assertEqual(report["session"]["maximum_observed_peak"], 0,
                                 "A cancelled upper manual must remain silent during its smoke note")
                self.assertTrue(report["runtime"]["screenshot_while_held"], diagnostic_excerpt(report))
                self.assert_bmp(screenshot, 1280, 900, held_middle_c=True)
                self.assertEqual(state.read_bytes(), original, "Startup or exit rewrote the musical file")

    def test_late_malformed_startup_preserves_file_and_audition_controls(self) -> None:
        state = self.root / "malformed controls.b3controls"
        original = state_document().replace(b"bank B 8 6 4 2 0 7 5 3 1", b"bank B 8 6 4 2 0 7 5 3 9")
        state.write_bytes(original)
        diagnostics = self.root / "fallback.json"
        run = self.invoke(self.smoke_arguments(state, diagnostics))
        report = self.diagnostics(diagnostics, state)
        self.assert_success(run, report, allow_startup_error=True)
        self.assertIn("Startup state was not loaded", run.process.stderr)
        self.assertIn("Startup state was not loaded", report["errors"]["last"])
        self.assertGreater(report["errors"]["count"], 0)
        self.assertGreater(report["session"]["maximum_observed_peak"], 0)
        self.assertFalse(report["runtime"]["screenshot_written"])
        self.assertFalse(report["runtime"]["screenshot_while_held"])
        self.assertEqual(state.read_bytes(), original)

    def test_no_audio_fails_bounded_with_zero_callback_claims(self) -> None:
        state, diagnostics, screenshot = (self.root / name for name in ("absent.b3controls", "no-audio.json", "no-audio.bmp"))
        run = self.invoke(self.smoke_arguments(state, diagnostics, screenshot,
                          ["--workspace", "service", "--flat"]), expected=1, audio=INVALID_DRIVER)
        report = self.diagnostics(diagnostics, state, workspace="service", presentation="flat")
        self.assert_summary(run, report, False)
        self.assertIn("No Audio: cannot initialize selected SDL audio driver", run.process.stderr)
        self.assertFalse(report["audio"]["open_before_shutdown"])
        self.assertFalse(report["audio"]["running_before_shutdown"])
        self.assertEqual(report["audio"]["driver"], "", "Invalid audio driver silently fell back")
        for key in ("callback_count", "rendered_frames", "sample_rate", "buffer_frames", "channels", "sample_format", "buffer_bytes", *AUDIO_ERRORS):
            self.assertEqual(report["audio"][key], 0, key)
        for key in ("frame_clock", "publication_revision", "resolved_sequence", "last_applied_sequence", "recovery_count",
                    "queue_overflows", "rejected_commands", "discarded_commands", "fault_flags", "maximum_observed_peak"):
            self.assertEqual(report["session"][key], 0, key)
        self.assertFalse(report["session"]["prepared"])
        inspection = report["presentation"]["screenshot"]["inspection"]
        self.assertTrue(inspection["snapshot_available"])
        self.assertTrue(inspection["snapshot_read_succeeded"])
        self.assertEqual(inspection["snapshot_state"], "unprepared")
        self.assertEqual((inspection["frame_clock"], inspection["publication_revision"]), (0, 0))
        self.assertTrue(report["smoke"]["completed"])
        for key in ("note_on_sent", "note_off_sent", "held_observed", "release_observed", "passed"):
            self.assertFalse(report["smoke"][key], key)
        self.assertGreater(report["runtime"]["rendered_images"], 0)
        self.assertTrue(report["runtime"]["screenshot_written"])
        self.assertFalse(report["runtime"]["screenshot_while_held"])
        self.assertGreater(report["errors"]["count"], 0)
        self.assert_bmp(screenshot, 1280, 900)
        self.assertFalse(state.exists())

    def test_screenshot_failure_joins_audio_and_preserves_musical_file(self) -> None:
        state = self.root / "saved controls.b3controls"
        state.write_bytes(state_document())
        missing_parent = self.root / "uncreated screenshot parent"
        screenshot, diagnostics = missing_parent / "capture.bmp", self.root / "failure.json"
        run = self.invoke(self.smoke_arguments(state, diagnostics, screenshot), expected=1)
        report = self.diagnostics(diagnostics, state)
        self.assert_active_shutdown(report)
        self.assert_summary(run, report, False)
        self.assertFalse(report["smoke"]["passed"])
        self.assertFalse(report["runtime"]["screenshot_written"])
        self.assertFalse(report["runtime"]["screenshot_while_held"])
        self.assertEqual(report["controls"], VARIED_CONTROLS)
        self.assertIn("Cannot save screenshot", run.process.stderr)
        self.assertGreater(report["errors"]["count"], 0)
        self.assertEqual(state.read_bytes(), state_document())
        self.assertFalse(missing_parent.exists())

    def test_diagnostics_failure_returns_cleanly_and_preserves_musical_file(self) -> None:
        state = self.root / "saved controls.b3controls"
        state.write_bytes(state_document())
        missing_parent = self.root / "uncreated diagnostics parent"
        diagnostics, screenshot = missing_parent / "copied.json", self.root / "held.bmp"
        run = self.invoke(self.smoke_arguments(state, diagnostics, screenshot), expected=1)
        self.assertIn("Cannot open diagnostics output", run.process.stderr)
        match = SUMMARY.fullmatch(run.process.stdout)
        self.assertIsNotNone(match, run.process.stdout)
        self.assertEqual(match.group(1), "failed")
        self.assertTrue(all(int(match.group(index)) > 0 for index in (2, 3, 4)))
        self.assertGreaterEqual(run.elapsed, SMOKE_MS / 1000 * 0.9)
        self.assertLess(run.elapsed, PROCESS_TIMEOUT)
        self.assert_bmp(screenshot, 1280, 900)
        self.assertFalse(diagnostics.exists())
        self.assertEqual(state.read_bytes(), state_document())
        self.assertFalse(missing_parent.exists())

    def test_output_directory_leaves_reject_before_writes(self) -> None:
        for option in ("--screenshot", "--diagnostics"):
            with self.subTest(option=option):
                paths = self.guarded_paths()
                paths[option].unlink()
                paths[option].mkdir()
                before = self.tree_snapshot()
                try:
                    run = self.invoke(self.cli_arguments(paths, []), expected=1)
                    self.assertEqual(run.process.stderr,
                                     "hammond_standalone: Screenshot, diagnostics, and replay script paths "
                                     "must be regular files or new paths\n")
                    self.assertEqual(run.process.stdout, "")
                    self.assertEqual(self.tree_snapshot(), before)
                finally:
                    # A diagnostic-text failure must not turn the next
                    # independent subcase into an IsADirectoryError fixture.
                    paths[option].rmdir()

    def file_symlink(self, alias: Path, target: Path) -> None:
        try:
            alias.symlink_to(target)
        except OSError as error:
            if os.name == "nt" and getattr(error, "winerror", None) == 1314:
                self.skipTest("Windows file-symlink privilege unavailable; leaf-symlink coverage not executed")
            self.fail(f"File-symlink prerequisite unavailable: {error}")

    def test_output_symlinks_cannot_create_or_overwrite_musical_state(self) -> None:
        for existing_state in (False, True):
            for option in ("--screenshot", "--diagnostics"):
                with self.subTest(option=option, existing_state=existing_state):
                    paths = self.guarded_paths()
                    state = paths["--state"]
                    if not existing_state:
                        state.unlink()
                    paths[option].unlink()
                    self.file_symlink(paths[option], state)
                    before = self.tree_snapshot()
                    run = self.invoke(self.cli_arguments(paths, []), expected=1)
                    self.assertIn("paths must not be symbolic links", run.process.stderr)
                    self.assertEqual(run.process.stdout, "")
                    self.assertEqual(state.exists(), existing_state)
                    self.assertTrue(paths[option].is_symlink())
                    self.assertEqual(self.tree_snapshot(), before)
                    for path in self.root.iterdir():
                        if path.is_file() or path.is_symlink():
                            path.unlink()

    def test_state_symlinks_cannot_be_filled_by_outputs_or_loaded(self) -> None:
        for output_alias in ("--screenshot", "--diagnostics", None):
            with self.subTest(output_alias=output_alias):
                paths = self.guarded_paths()
                state = paths["--state"]
                state.unlink()
                target = self.root / "real musical state.b3controls"
                if output_alias is None:
                    target.write_bytes(state_document())
                else:
                    paths[output_alias] = target
                self.file_symlink(state, target)
                before = self.tree_snapshot()
                run = self.invoke(self.cli_arguments(paths, []), expected=1)
                self.assertIn("paths must not be symbolic links", run.process.stderr)
                self.assertEqual(run.process.stdout, "")
                self.assertTrue(state.is_symlink())
                self.assertEqual(target.exists(), output_alias is None)
                self.assertEqual(self.tree_snapshot(), before)
                for path in self.root.iterdir():
                    if path.is_file() or path.is_symlink():
                        path.unlink()

    def test_existing_direct_lexical_and_hardlink_collisions_preserve_files(self) -> None:
        pairs = (("--state", "--screenshot"), ("--state", "--diagnostics"), ("--screenshot", "--diagnostics"))
        for kind in ("direct", "lexical", "hardlink"):
            for first, second in pairs:
                with self.subTest(kind=kind, first=first, second=second):
                    paths = self.guarded_paths()
                    if kind == "hardlink":
                        paths[second].unlink()
                        try:
                            os.link(paths[first], paths[second])
                        except OSError as error:
                            self.fail(f"Actual hardlink prerequisite unavailable: {error}")
                    elif kind == "lexical":
                        spacer = self.root / "existing spacer"
                        spacer.mkdir(exist_ok=True)
                        paths[second] = spacer / ".." / paths[first].name
                    else:
                        paths[second] = paths[first]
                    before = self.tree_snapshot()
                    run = self.invoke(self.cli_arguments(paths, []), expected=1)
                    self.assertIn("must use different files", run.process.stderr)
                    self.assertEqual(run.process.stdout, "")
                    self.assertEqual(self.tree_snapshot(), before)
                    # Remove hardlinks before re-creating the next independent fixture.
                    for path in self.root.iterdir():
                        if path.is_file():
                            path.unlink()

    def parent_alias(self, alias: Path, target: Path) -> str:
        try:
            alias.symlink_to(target, target_is_directory=True)
            return "directory symlink"
        except OSError as error:
            if os.name != "nt":
                self.fail(f"Actual parent-alias prerequisite unavailable: {error}")
        # Windows may deny directory symlinks without developer privileges.
        # A real junction covers the required filesystem alias, without a skip.
        # Both paths contain spaces, so Windows list2cmdline quotes each operand.
        command = [os.environ.get("COMSPEC", "cmd.exe"), "/d", "/c", "mklink", "/J", str(alias), str(target)]
        try:
            result = subprocess.run(command, cwd=self.root, env=self.environment(), stdin=subprocess.DEVNULL,
                                    capture_output=True, text=True, errors="replace", timeout=3.0, check=False)
        except subprocess.TimeoutExpired as error:
            self.fail(f"Directory-junction creation exceeded 3s: {error}")
        self.assertEqual(result.returncode, 0,
                         f"Neither symlink nor directory junction is available: {result.stdout} {result.stderr}")
        self.assertTrue(alias.is_dir(), "Junction command did not produce a real directory alias")
        return "Windows directory junction (symlink unavailable)"

    def test_absent_leaf_parent_alias_collisions_cannot_create_state_or_outputs(self) -> None:
        target = self.root / "real parent 保存"
        target.mkdir()
        alias = self.root / "parent alias 链接"
        kind = self.parent_alias(alias, target)
        print(f"Absent-leaf parent-alias regression: {kind}", flush=True)
        leaf = "fresh shared result"
        pairs = (("--state", "--screenshot"), ("--state", "--diagnostics"), ("--screenshot", "--diagnostics"))
        for first, second in pairs:
            with self.subTest(first=first, second=second):
                paths = self.guarded_paths()
                paths[first], paths[second] = target / leaf, alias / leaf
                before = self.tree_snapshot()
                run = self.invoke(self.cli_arguments(paths, []), expected=1)
                self.assertIn("must use different files", run.process.stderr)
                self.assertEqual(run.process.stdout, "")
                self.assertFalse((target / leaf).exists())
                self.assertFalse((alias / leaf).exists())
                self.assertEqual(self.tree_snapshot(), before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
