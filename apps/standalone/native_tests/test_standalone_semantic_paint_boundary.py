#!/usr/bin/env python3
"""Every scripted semantic view in one SDL event batch must actually paint.

All twelve actions are due at zero, with no resize, sleep, or synthetic frame.
The real application must paint workspace, presentation, and Audio overlay
transitions before later queued semantic input can replace them. Audio opens
and closes without Apply; dummy SDL enumeration needs no physical device and
leaves the native MIDI backend unopened. The separate resize-prefix regression
and maximum-resize fixture retain their original contracts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest

import test_standalone_app as app_fixture
import test_standalone_midi_replay as midi_fixture
import test_standalone_workflows as workflow_fixture


SOURCE = b"""B3UIREPLAY1
duration_ms 250
0 key_down F5 none 0
0 key_up F5 none
0 key_down F7 none 0
0 key_up F7 none
0 key_down Comma ctrl 0
0 key_up Comma ctrl
0 key_down Escape none 0
0 key_up Escape none
0 key_down F6 none 0
0 key_up F6 none
0 key_down F4 none 0
0 key_up F4 none
"""
# Accepted but noncanonical bytes expose an unsolicited normalization/save.
STATE = b"\t" + b"""B3CONTROLS4
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
""".replace(b"\n", b"\r\n") + b" \t\r\n"
# Independent literal complete controls, never read from application output.
CONTROLS = {
    "manual_drawbars": [
        [[0, 1, 2, 3, 4, 5, 6, 7, 8], [8, 7, 6, 5, 4, 3, 2, 1, 0]],
        [[1, 3, 5, 7, 0, 2, 4, 6, 8], [8, 6, 4, 2, 0, 7, 5, 3, 1]],
    ],
    "selected_banks": [0, 1], "fixed_registrations": [6, 8],
    "preset_selections": [6, 8], "route_enabled": [True, True],
    "expression": 0.375, "pedal_drawbars": [2, 7],
    "percussion": {"enabled": True, "harmonic": 1, "volume": 1, "decay": 1},
}
# Independent prospective sequence, admitted before production implementation.
# No initial Play frame is imposed before the timestamp-zero F5 transition.
EXPECTED = {
    "dimensional": [
        ("rotary", "dimensional", 1280, 900, "none"),
        ("rotary", "flat", 1280, 900, "none"),
        ("rotary", "flat", 1280, 900, "audio"),
        ("rotary", "flat", 1280, 900, "none"),
        ("service", "flat", 1280, 900, "none"),
        ("play", "flat", 1280, 900, "none"),
    ],
    "flat": [
        ("rotary", "flat", 1280, 900, "none"),
        ("rotary", "dimensional", 1280, 900, "none"),
        ("rotary", "dimensional", 1280, 900, "audio"),
        ("rotary", "dimensional", 1280, 900, "none"),
        ("service", "dimensional", 1280, 900, "none"),
        ("play", "dimensional", 1280, 900, "none"),
    ],
}
DRIVERS = {"SDL_AUDIODRIVER": "dummy", "SDL_VIDEODRIVER": "dummy",
           "SDL_RENDER_DRIVER": "software"}
OUTPUT_LIMIT = 64 * 1024
DIAGNOSTICS_LIMIT = 2 * 1024 * 1024


def sha256(path: Path) -> str:
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def view_key(frame: dict) -> tuple:
    return tuple(frame[key] for key in
                 ("workspace", "presentation", "window_width", "window_height", "overlay"))


def painted_visits(data: dict) -> list[dict]:
    """Retain actual first-painted records for adjacent distinct view visits."""
    visits: list[dict] = []
    # Only records emitted by render_frame count. Event-time UI observations
    # and the final last_painted record cannot fill a missing semantic visit.
    for frame in data["presentation"]["observations"]:
        if not visits or view_key(frame) != view_key(visits[-1]):
            visits.append(frame)
    return visits


def run_bounded(command: list[str], directory: Path, timeout: float) -> dict:
    """Drain both pipes concurrently, retaining at most 64 KiB from each."""
    started = time.monotonic()
    process = subprocess.Popen(command, cwd=directory, env={**os.environ, **DRIVERS},
                               stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    buffers = {"stdout": bytearray(), "stderr": bytearray()}
    exceeded = threading.Event()

    def drain(name: str, stream) -> None:
        with stream:
            while block := stream.read(4096):
                remaining = OUTPUT_LIMIT - len(buffers[name])
                buffers[name].extend(block[:remaining])
                if len(block) > remaining:
                    exceeded.set()
                    process.kill()
                    return

    readers = [threading.Thread(target=drain, args=(name, stream), daemon=True)
               for name, stream in (("stdout", process.stdout), ("stderr", process.stderr))]
    for reader in readers:
        reader.start()
    timed_out = False
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        process.kill()
        process.wait(timeout=3)
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=3)
        for reader in readers:
            reader.join(timeout=2)
    return {
        "command": command, "environment": DRIVERS,
        "elapsed_seconds": time.monotonic() - started,
        "returncode": process.returncode, "timed_out": timed_out,
        "output_limit_exceeded": exceeded.is_set(),
        "pipe_readers_joined": all(not reader.is_alive() for reader in readers),
        **{name: bytes(value).decode("utf-8", errors="replace") for name, value in buffers.items()},
    }


def verify(data: dict, initial: str, state_path: Path) -> None:
    case = unittest.TestCase()
    schema = dict(app_fixture.SCHEMA)
    schema["replay"] = midi_fixture.replay_schema(data["replay"], midi_fixture.UI_REPLAY_SCHEMA)
    app_fixture.assert_schema(case, data, schema)
    workflow_fixture.NativeWorkflowAcceptance.assert_common(
        case, data, SOURCE.decode("ascii"), state_path, (1280, 900))
    app_fixture.assert_presentation(case, data)
    runtime, replay, presentation = data["runtime"], data["replay"], data["presentation"]
    case.assertEqual(runtime["renderer"], "software")
    case.assertFalse(runtime["screenshot_written"])
    case.assertFalse(runtime["screenshot_while_held"])
    audio = data["audio"]
    case.assertEqual(audio["requested_device"], "")
    case.assertEqual((audio["requested_sample_rate"], audio["sample_rate"]), (48000, 48000))
    case.assertEqual((audio["requested_buffer_frames"], audio["buffer_frames"]), (512, 512))
    case.assertEqual(data["session"]["sample_rate"], 48000)
    case.assertEqual(replay["duration_ms"], 250)
    case.assertEqual((replay["scheduled_events"], replay["pushed_events"]), (12, 12))
    case.assertEqual(replay["device_starts"], 1)
    for field in ("passed", "final_acknowledged", "snapshot_available_before_shutdown",
                  "session_running_before_shutdown"):
        case.assertTrue(replay[field], field)
    for field in ("controls_pending_before_shutdown", "save_pending_before_shutdown",
                  "ui_observations_truncated"):
        case.assertFalse(replay[field], field)
    case.assertEqual(replay["ui_observation_capacity"], 512)
    case.assertEqual((replay["accepted_note_on_commands"], replay["accepted_note_off_commands"]), (0, 0))
    case.assertEqual(data["controls"], CONTROLS)
    case.assertEqual(replay["desired_controls_before_shutdown"], CONTROLS)
    sequence = replay["last_submitted_sequence"]
    case.assertGreater(sequence, 0)
    # Opening a modal and Escape submit genuine scoped ReleaseUiNotes commands,
    # even with empty holds. Preserve their existing acknowledgment semantics;
    # an earlier musical observation need not yet resolve the final sequence.
    sequences = []
    for observation in [*replay["observations"], replay["before_shutdown"]]:
        case.assertEqual(observation["controls"], CONTROLS)
        case.assertEqual(observation["manual_notes"], [[], []])
        case.assertEqual(observation["pedal_ids"], [])
        applied = observation["last_applied_sequence"]
        resolved = observation["resolved_sequence"]
        submitted = observation.get("last_submitted_sequence", sequence)
        case.assertGreater(applied, 0)
        case.assertEqual(applied, resolved)
        case.assertLessEqual(resolved, submitted)
        case.assertLessEqual(submitted, sequence)
        sequences.append((applied, resolved, submitted))
        if "last_submitted_sequence" in observation:
            case.assertEqual(observation["error_count"], 0)
            case.assertIn(observation["overlay"], ("none", "audio"))
    for previous, current in zip(sequences, sequences[1:]):
        case.assertTrue(all(left <= right for left, right in zip(previous, current)),
                        f"Applied, resolved, and submitted sequences must advance monotonically: {sequences}")
    case.assertEqual(sequences[-1], (sequence, sequence, sequence))
    case.assertLessEqual(len(replay["ui_observations"]), 512)
    for observation in replay["ui_observations"]:
        case.assertIn(observation["overlay"], ("none", "audio"))
        case.assertEqual(observation["modal_focus"], 0)
    case.assertEqual(presentation["initial_workspace"], "play")
    case.assertEqual(presentation["initial_presentation"], initial)
    case.assertFalse(presentation["observations_truncated"])
    case.assertIsNone(presentation["screenshot"])
    frames = [*presentation["observations"], presentation["last_painted"]]
    for frame in frames:
        case.assertEqual(frame["held_targets"], {"upper": 0, "lower": 0, "pedals": 0})
        case.assertEqual(frame["pointer_capture"], {
            "sdl_captured": False, "ui_captured": False, "attempts": 0,
            "successes": 0, "losses": 0, "release_calls": 0,
        })
        case.assertLessEqual(frame["elapsed_ms"], 2250,
                             "Keep the original 250 ms duration and 2000 ms drain bound")
    case.assertIn(frames[-1]["inspection"]["snapshot_state"], ("current", "retained"))
    case.assertFalse(frames[-1]["inspection"]["controls_pending"])
    clocks = [frame["inspection"]["frame_clock"] for frame in frames
              if frame["inspection"]["snapshot_available"]]
    case.assertTrue(clocks)
    case.assertEqual(clocks, sorted(clocks))
    visits = painted_visits(data)
    case.assertEqual([view_key(frame) for frame in visits], EXPECTED[initial],
                     "Every workspace, presentation, and overlay transition must reach an actual painted image")
    case.assertEqual(view_key(presentation["last_painted"]), EXPECTED[initial][-1])
    images = [frame["rendered_image"] for frame in visits]
    case.assertTrue(all(left < right for left, right in zip(images, images[1:])),
                    f"Required visits must be distinct actual renders: {images}")


def run_case(executable: Path, initial: str, timeout: float) -> dict:
    result = {"initial_presentation": initial, "expected_visits": EXPECTED[initial], "status": "failed"}
    with tempfile.TemporaryDirectory(prefix="hammond-semantic-paint-boundary-") as temporary:
        directory = Path(temporary)
        state_path, script_path, report_path = (directory / name for name in
                                               ("controls.b3controls", "input.b3ui", "diagnostics.json"))
        state_path.write_bytes(STATE)
        script_path.write_bytes(SOURCE)
        command = [str(executable), "--state", str(state_path), "--input-script", str(script_path),
                   "--diagnostics", str(report_path), "--width", "1280", "--height", "900"]
        if initial == "flat":
            command.append("--flat")
        try:
            process = run_bounded(command, directory, timeout)
            result["process"] = process
            case = unittest.TestCase()
            case.assertFalse(process["timed_out"], "Native child exceeded its finite timeout")
            case.assertFalse(process["output_limit_exceeded"], "Native output exceeded 64 KiB per stream")
            case.assertTrue(process["pipe_readers_joined"])
            case.assertEqual(process["returncode"], 0)
            case.assertEqual((process["stdout"], process["stderr"]), ("", ""))
            case.assertGreaterEqual(process["elapsed_seconds"], 0.21)
            case.assertLessEqual(report_path.stat().st_size, DIAGNOSTICS_LIMIT)
            raw = report_path.read_bytes()
            result["diagnostics_sha256"] = hashlib.sha256(raw).hexdigest()
            # Exact original native JSON remains reviewable in --report output.
            result["diagnostics_text"] = raw.decode("utf-8")
            data = json.loads(result["diagnostics_text"], object_pairs_hook=app_fixture.unique_object,
                              parse_constant=app_fixture.reject_nonfinite)
            result["actual_visits"] = [
                {"view": view_key(frame), "rendered_image": frame["rendered_image"],
                 "elapsed_ms": frame["elapsed_ms"]} for frame in painted_visits(data)
            ]
            case.assertEqual(script_path.read_bytes(), SOURCE)
            case.assertEqual(state_path.read_bytes(), STATE, "Presentation replay must preserve saved bytes")
            case.assertEqual({path.name for path in directory.iterdir()},
                             {state_path.name, script_path.name, report_path.name})
            verify(data, initial, state_path)
            result["status"] = "passed"
        except (AssertionError, OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
            result["failure"] = f"{type(error).__name__}: {error}"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", default=os.environ.get("HAMMOND_STANDALONE_EXECUTABLE"))
    parser.add_argument("--timeout-seconds", type=float, default=12.0)
    parser.add_argument("--report", type=Path, help="Write bounded provenance and exact native diagnostics as JSON")
    arguments = parser.parse_args()
    if not arguments.executable:
        parser.error("--executable or HAMMOND_STANDALONE_EXECUTABLE is required")
    if not math.isfinite(arguments.timeout_seconds) or not 12 <= arguments.timeout_seconds <= 30:
        parser.error("--timeout-seconds must be finite and between 12 and 30")
    executable = Path(arguments.executable).resolve(strict=True)
    if not executable.is_file() or not os.access(executable, os.X_OK):
        parser.error(f"Native application is not executable: {executable}")
    helpers = [Path(module.__file__).resolve() for module in
               (app_fixture, midi_fixture, workflow_fixture)]
    tracked = [Path(__file__).resolve(), executable, *helpers]
    hashes = {str(path): sha256(path) for path in tracked}
    results = [run_case(executable, initial, arguments.timeout_seconds) for initial in EXPECTED]
    changed = [str(path) for path in tracked if sha256(path) != hashes[str(path)]]
    passed = not changed and all(result["status"] == "passed" for result in results)
    report = {
        "schema_version": 1, "test": "standalone_semantic_paint_boundary", "status": "passed" if passed else "failed",
        "source": SOURCE.decode("ascii"), "source_sha256": hashlib.sha256(SOURCE).hexdigest(),
        "state_sha256": hashlib.sha256(STATE).hexdigest(), "file_sha256": hashes,
        "changed_inputs": changed, "timeout_seconds_per_child": arguments.timeout_seconds,
        "actual_native_subprocesses": len(results), "cases": results,
    }
    if arguments.report:
        arguments.report.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    for result in results:
        print(f"{result['initial_presentation']}: {result['status']}; actual visits: "
              f"{json.dumps(result.get('actual_visits', []))}")
        if "failure" in result:
            print(result["failure"], file=sys.stderr)
    print(f"Actual native subprocesses: {len(results)}; executable SHA-256: {hashes[str(executable)]}")
    if changed:
        print(f"Inputs changed during acceptance: {changed}", file=sys.stderr)
    if arguments.report:
        print(f"Evidence report: {arguments.report.resolve()}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
