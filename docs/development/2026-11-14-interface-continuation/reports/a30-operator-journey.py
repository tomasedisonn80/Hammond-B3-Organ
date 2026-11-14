#!/usr/bin/env python3
"""A30's bounded operator audit; uses an already built, digest-pinned executable.

This is retained audit evidence, not a new exhaustive test suite. It imports
only existing test-side schema/lifecycle helpers and literal control fixtures.
All native runs have dummy SDL drivers, private /tmp paths and a nine-second
deadline. No build/configure operation or physical MIDI connection is made.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import time
import traceback

from PIL import Image, __version__ as pillow_version

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "apps/standalone/native_tests"))
import test_standalone_app as app
import test_standalone_midi_replay as midi
import test_standalone_workflows as workflow
import test_standalone_workspace_replay as workspace

PIN = "005db1e2006bd1929e07dff3acaa40a5a6e6fa60a2bc8f07eb992d972b04b364"
EMPTY = ((), (), ())
UPPER_A = ((60,), (), ())
UPPER_S = ((62,), (), ())
CASE = workflow.NativeWorkflowAcceptance("runTest")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def tap(at: int, key: str, modifiers: str = "none") -> list[tuple[int, str]]:
    return workspace.tap(at, key, modifiers)


def click(at: int, x: int, y: int) -> list[tuple[int, str]]:
    return workspace.click(at, (x, y))


def tabs(at: int, count: int, spacing: int = 20) -> list[tuple[int, str]]:
    return [event for index in range(count) for event in tap(at + spacing * index, "Tab")]


def view_path(data: dict) -> list[tuple]:
    return workspace.unique([
        (frame["workspace"], frame["presentation"], frame["overlay"],
         frame["window_width"], frame["window_height"])
        for frame in [*data["presentation"]["observations"], data["presentation"]["before_shutdown"]]
    ])


def views(data: dict, expected: list[tuple]) -> None:
    CASE.assertEqual(view_path(data), expected)


def notes(run: workflow.WorkflowRun, expected: list[tuple], on: int, off: int) -> None:
    CASE.assert_hold_path(run, expected)
    CASE.assert_note_commands(run, on, off)


def controls(run: workflow.WorkflowRun, expected: list[dict]) -> None:
    CASE.assert_control_path(run, expected)
    CASE.assertEqual(run.diagnostics["replay"]["desired_controls_before_shutdown"], expected[-1])


def command_delta(data: dict, count: int) -> None:
    first = data["replay"]["observations"][0]
    CASE.assertLess(first["elapsed_ms"], 150)
    CASE.assertEqual(first["last_applied_sequence"], first["last_submitted_sequence"])
    CASE.assertEqual(data["replay"]["last_submitted_sequence"] - first["last_applied_sequence"], count)


def invoke(args, result: dict, name: str, duration: int, events: list[tuple[int, str]], *,
           state: bytes | None, extra: list[str] | None = None,
           final_size: tuple[int, int] = (1280, 900), capture: bool = False,
           discovery: bool = False) -> workflow.WorkflowRun:
    CASE.assertEqual(digest(args.executable), PIN)
    directory = Path(tempfile.mkdtemp(prefix=f"a30-{name}-", dir="/tmp"))
    destination = args.output / name
    destination.mkdir()
    state_path = directory / "controls.b3controls"
    if state is not None:
        state_path.write_bytes(state)
        (destination / "initial.b3controls").write_bytes(state)
    source = workspace.script("B3UIREPLAY1", duration, events)
    script_path = directory / "input.b3uireplay"
    script_path.write_bytes(source)
    diagnostic_path = directory / "diagnostics.json"
    bmp_path = directory / "frame.bmp"
    command = [str(args.executable), "--state", str(state_path), "--input-script", str(script_path),
               "--diagnostics", str(diagnostic_path), *(extra or [])]
    if capture:
        command += ["--screenshot", str(bmp_path)]
    environment = dict(os.environ, SDL_AUDIODRIVER="dummy", SDL_VIDEODRIVER="dummy")
    record = {"name": name, "command": command, "cwd": str(directory),
              "environment": {"SDL_AUDIODRIVER": "dummy", "SDL_VIDEODRIVER": "dummy"},
              "timeout_seconds": 9, "executable_sha256_before": digest(args.executable)}
    result["runs"].append(record)
    started = time.monotonic()
    data = None
    try:
        process = subprocess.run(command, cwd=directory, env=environment, stdin=subprocess.DEVNULL,
                                 capture_output=True, text=True, errors="replace", timeout=9, check=False)
        record.update(returncode=process.returncode, elapsed_seconds=time.monotonic() - started)
        (destination / "stdout.txt").write_text(process.stdout, encoding="utf-8")
        (destination / "stderr.txt").write_text(process.stderr, encoding="utf-8")
        CASE.assertGreaterEqual(record["elapsed_seconds"], duration / 1000 - 0.04)
        CASE.assertEqual(process.stdout, "")
        data = json.loads(diagnostic_path.read_text(encoding="utf-8"),
                          object_pairs_hook=app.unique_object, parse_constant=app.reject_nonfinite)
        app.assert_schema(CASE, data, {**app.SCHEMA,
            "replay": midi.replay_schema(data["replay"], midi.UI_REPLAY_SCHEMA)})
        app.assert_presentation(CASE, data)
        if not discovery:
            CASE.assertEqual(process.returncode, 0)
            CASE.assertEqual(process.stderr, "")
            CASE.assert_common(data, source.decode("ascii"), state_path, final_size)
        else:
            # Discovery can fail on this no-ALSA-device container. Preserve it
            # explicitly; never turn its false replay pass into a passing run.
            failures = data["midi"]["discovery"]["failures"]
            CASE.assertIn(failures, (0, 1))
            if failures:
                CASE.assertEqual(process.returncode, 1)
                CASE.assertFalse(data["replay"]["passed"])
                CASE.assertEqual(data["errors"], {"count": 2,
                    "last": "Native input replay failed or was interrupted; inspect the copied diagnostics"})
                application_errors = [line for line in process.stderr.splitlines()
                                      if line.startswith("hammond_standalone:")]
                CASE.assertEqual(len(application_errors), 2)
                CASE.assertTrue(application_errors[0].startswith(
                    "hammond_standalone: Cannot enumerate MIDI input ports:"))
                CASE.assertIn("Native input replay failed or was interrupted", application_errors[1])
                record["native_result"] = "failed: MIDI discovery unavailable; preserved environmental failure"
            else:
                CASE.assertEqual(process.returncode, 0)
                CASE.assertEqual(process.stderr, "")
                CASE.assertEqual(data["errors"], {"count": 0, "last": ""})
                CASE.assertTrue(data["replay"]["passed"])
                record["native_result"] = "passed; no MIDI input selected"
            CASE.assertEqual(data["schema_version"], 3)
            CASE.assertEqual(data["state_path"], str(state_path))
            CASE.assertEqual(data["application"], "hammond_standalone")
            CASE.assertFalse(data["smoke"]["requested"])
            CASE.assertEqual(data["runtime"]["video_driver"], "dummy")
            CASE.assertEqual((data["runtime"]["window_width"], data["runtime"]["window_height"]), final_size)
            CASE.assertEqual((data["runtime"]["drawable_width"], data["runtime"]["drawable_height"]), final_size)
            audio = data["audio"]
            CASE.assertEqual(audio["driver"], "dummy")
            CASE.assertTrue(audio["open_before_shutdown"])
            CASE.assertTrue(audio["running_before_shutdown"])
            CASE.assertGreater(audio["callback_count"], 0)
            CASE.assertGreater(audio["rendered_frames"], 0)
            CASE.assertEqual(audio["channels"], 2)
            CASE.assertEqual(audio["sample_format"], audio["native_float32_format"])
            CASE.assertEqual(audio["buffer_bytes"], audio["buffer_frames"] * 8)
            for field in app.AUDIO_ERRORS:
                CASE.assertEqual(audio[field], 0)
            CASE.assertEqual(audio["last_render_status"], "ok")
            CASE.assertEqual(audio["last_lifecycle_status"], "ok")
            for field in ("recovery_count", "queue_overflows", "rejected_commands", "fault_flags"):
                CASE.assertEqual(data["session"][field], 0)
            CASE.assertLessEqual(data["session"]["discarded_commands"], 1)
        replay = data["replay"]
        for field in ("completed", "delivered", "final_acknowledged", "snapshot_available_before_shutdown",
                      "session_running_before_shutdown"):
            CASE.assertTrue(replay[field], field)
        for field in ("controls_pending_before_shutdown", "save_pending_before_shutdown", "observations_truncated"):
            CASE.assertFalse(replay[field], field)
        CASE.assertEqual(replay["scheduled_events"], len(events))
        CASE.assertEqual(replay["pushed_events"], len(events))
        CASE.assertEqual(replay["observation_capacity"], 512)
        CASE.assertFalse(data["presentation"]["observations_truncated"])
        CASE.assertEqual(data["runtime"]["renderer"], "software")
        CASE.assertTrue(data["session"]["snapshot_available"])
        CASE.assertTrue(data["session"]["prepared"])
        CASE.assertFalse(data["session"]["running_after_shutdown"])
        CASE.assertFalse(data["session"]["held_after_shutdown"])
        CASE.assertEqual(replay["before_shutdown"]["controls"], data["controls"])
        CASE.assertEqual(replay["before_shutdown"]["last_applied_sequence"], replay["last_submitted_sequence"])
        CASE.assertEqual(replay["before_shutdown"]["resolved_sequence"], replay["last_submitted_sequence"])
        CASE.assertEqual(script_path.read_bytes(), source)
        CASE.assertEqual(data["runtime"]["screenshot_written"], capture)
        saved = state_path.read_bytes() if state_path.exists() else b""
        if capture:
            CASE.assertEqual(data["presentation"]["screenshot"], data["presentation"]["before_shutdown"])
            png_path = destination / "frame.png"
            with Image.open(bmp_path) as bmp:
                bmp.load()
                decoded_mode, decoded_size, pixels = bmp.mode, bmp.size, bmp.tobytes()
                CASE.assertEqual(decoded_size, final_size)
                bmp.save(png_path, format="PNG", optimize=True)
            with Image.open(png_path) as png:
                png.load()
                CASE.assertEqual((png.mode, png.size, png.tobytes()), (decoded_mode, decoded_size, pixels))
            record["capture"] = {"png": str(png_path.relative_to(ROOT)), "bmp_sha256": digest(bmp_path),
                "png_sha256": digest(png_path), "decoded_mode": decoded_mode, "size": decoded_size,
                "decoded_pixels_sha256": hashlib.sha256(pixels).hexdigest(), "decoded_pixels_equal": True}
            bmp_path.unlink()  # Only after reopened-PNG decoded equality.
        record.update(native_result=record.get("native_result", "passed"),
                      state_existed_at_start=state is not None, state_exists_after=state_path.exists(),
                      state_sha256_after=hashlib.sha256(saved).hexdigest() if saved else None,
                      painted_views=view_path(data),
                      note_on_commands=replay["accepted_note_on_commands"],
                      note_off_commands=replay["accepted_note_off_commands"],
                      device_starts=replay["device_starts"],
                      audio_callbacks=data["audio"]["callback_count"],
                      held_before_shutdown=workflow.NativeWorkflowAcceptance.holds(replay["before_shutdown"]))
        return workflow.WorkflowRun(data, saved, record["elapsed_seconds"])
    finally:
        record["executable_sha256_after"] = digest(args.executable)
        for path in (script_path, diagnostic_path, state_path):
            if path.exists():
                shutil.copyfile(path, destination / path.name)
        save_json(destination / "process.json", record)
        shutil.rmtree(directory)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--executable", type=Path, default=Path("/tmp/a30-operator-pinned/hammond_standalone"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.executable = args.executable.resolve(strict=True)
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=False)
    CASE.assertEqual(digest(args.executable), PIN)
    source_paths = ["docs/INTERFACE_RUNBOOK.md", "docs/STANDALONE_INPUT_REPLAY.md",
                    "apps/standalone/main.cpp", "apps/standalone/UiModel.cpp",
                    "apps/standalone/native_tests/test_standalone_workspace_replay.py",
                    "apps/standalone/native_tests/test_standalone_workflows.py",
                    "apps/standalone/native_tests/test_standalone_app.py",
                    "apps/standalone/native_tests/test_standalone_midi_replay.py",
                    "examples/demos/standalone-interface-preview-v1/inputs/source-qualification.json"]
    result = {"agent": "A30", "kind": "independent bounded native operator audit",
              "published_base": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "qualification_scope": "Pinned pre-A28 interface overlay; base commit alone does not contain this UI",
              "executable": str(args.executable), "executable_sha256_before": digest(args.executable),
              "python": platform.python_version(), "pillow": pillow_version,
              "source_and_guide_sha256_before": {path: digest(ROOT / path) for path in source_paths},
              "cli": [], "runs": [], "checks": [], "failure": None}
    try:
        # Help and invalid workspace admission must not initialize SDL or write
        # outputs. Bogus drivers deliberately distinguish admission from smoke.
        for name, options, code in (("help", ["--help"], 0),
                                    ("invalid-workspace", ["--workspace", "Service"], 2)):
            command = [str(args.executable), *options]
            process = subprocess.run(command, cwd=args.output, capture_output=True, text=True, timeout=9,
                env=dict(os.environ, SDL_AUDIODRIVER="a30-invalid-driver", SDL_VIDEODRIVER="a30-invalid-driver"))
            CASE.assertEqual(process.returncode, code)
            (args.output / f"{name}.stdout.txt").write_text(process.stdout, encoding="utf-8")
            (args.output / f"{name}.stderr.txt").write_text(process.stderr, encoding="utf-8")
            if name == "help":
                CASE.assertEqual(process.stderr, "")
                for literal in ("--workspace NAME", "--flat", "960..8192, default 1280", "700..8192, default 900",
                                "F4/F5/F6 select Play/Rotary/Service; F7 toggles dimensional/flat.",
                                "Save is explicit, never automatic.", "Lower B 008000000, pedals 80."):
                    CASE.assertIn(literal, process.stdout)
            else:
                CASE.assertIn("Unsupported value for --workspace", process.stderr)
            result["cli"].append({"name": name, "command": command, "returncode": process.returncode})

        events = click(150, 150, 240) + tap(400, "F5") + click(550, 650, 350) + tap(700, "F4")
        events += [(900, "key_down A none 0")] + tap(1100, "F6") + tap(1300, "F7")
        events += tap(1500, "F5") + tap(1700, "F4") + [(1900, "key_up A alt+meta")] + tap(2050, "F7")
        first = invoke(args, result, "01-first-launch", 2300, events, state=None,
                       extra=["--workspace", "service"])
        controls(first, [app.AUDITION_CONTROLS])
        notes(first, [EMPTY, UPPER_A, EMPTY], 1, 1)
        command_delta(first.diagnostics, 2)
        CASE.assertEqual(first.saved_bytes, b"")
        CASE.assertEqual(first.diagnostics["replay"]["device_starts"], 1)
        views(first.diagnostics, [(w, p, "none", 1280, 900) for w, p in
            (("service", "dimensional"), ("rotary", "dimensional"), ("play", "dimensional"),
             ("service", "dimensional"), ("service", "flat"), ("rotary", "flat"),
             ("play", "flat"), ("play", "dimensional"))])
        clocks = [frame["inspection"]["frame_clock"] for frame in first.diagnostics["presentation"]["observations"]
                  if frame["inspection"]["snapshot_available"]]
        CASE.assertEqual(clocks, sorted(clocks))
        result["checks"].append("First launch: literal audition defaults, read-only bodies, F4-F7, unchanged controls/sequence, original A release, no implicit Save")

        edited = deepcopy(workflow.FIXED_CONTROLS)
        edited["manual_drawbars"][0][0][0] = 8
        sounding_b = deepcopy(edited)
        sounding_b["selected_banks"][0] = 1
        sounding_b["fixed_registrations"][0] = 0
        sounding_b["preset_selections"][0] = 11
        saved_bytes = workflow.FIXED_STATE.replace(b"bank A 0 1 2 3 4 5 6 7 8\n", b"bank A 8 1 2 3 4 5 6 7 8\n", 1)
        events = [(200, "key_down A none 0")] + click(300, 58, 508) + tabs(420, 14) + tap(760, "End")
        events += tap(980, "F6") + tap(1150, "F5") + tap(1320, "F4") + tap(1500, "S", "ctrl")
        events += click(1700, 165, 590) + click(1900, 130, 508) + tap(2100, "O", "ctrl")
        events += tap(2320, "F7") + [(2500, "resize 960 700")] + tap(2700, "F6") + [(2900, "key_up A none")]
        edit = invoke(args, result, "02-edit-save-live-load", 3150, events, state=workflow.FIXED_STATE,
                      final_size=(960, 700), capture=True)
        controls(edit, [workflow.FIXED_CONTROLS, edited, sounding_b, edited])
        notes(edit, [EMPTY, UPPER_A, EMPTY], 1, 1)
        command_delta(edit.diagnostics, 5)
        CASE.assertEqual(edit.saved_bytes, saved_bytes)
        CASE.assertEqual(edit.diagnostics["replay"]["device_starts"], 1)
        views(edit.diagnostics, [("play", "dimensional", "none", 1280, 900),
            ("service", "dimensional", "none", 1280, 900), ("rotary", "dimensional", "none", 1280, 900),
            ("play", "dimensional", "none", 1280, 900), ("play", "flat", "none", 1280, 900),
            ("play", "flat", "none", 960, 700), ("service", "flat", "none", 960, 700)])
        result["checks"].append("Held fixed F#: EDIT A and first drawbar edit preserve route; explicit preset B changes route; canonical Save and live Load restore exact fixed/control memory without releasing A")

        cold = invoke(args, result, "03-cold-reload", 600, [], state=edit.saved_bytes, capture=True)
        controls(cold, [edited])
        notes(cold, [EMPTY], 0, 0)
        CASE.assertEqual(cold.saved_bytes, saved_bytes)
        views(cold.diagnostics, [("play", "dimensional", "none", 1280, 900)])
        CASE.assertEqual(cold.diagnostics["presentation"]["initial_workspace"], "play")
        CASE.assertEqual(cold.diagnostics["presentation"]["initial_presentation"], "dimensional")
        result["checks"].append("Cold reload: identical canonical B3CONTROLS4 sound controls; zero held targets; default Play/Dimensional and 1280x900 return after Service/Flat/960x700 exit")

        events = [(200, "key_down A none 0")] + tap(450, "Slash", "shift")
        events += tap(620, "F4") + tap(700, "F7") + tap(850, "Escape")
        events += [(950, "key_down A none 1"), (1050, "key_up A none"), (1200, "key_down S none 0")]
        events += tap(1400, "Comma", "ctrl") + tap(1530, "F6") + tabs(1640, 2, 40)
        events += tap(1770, "Home") + tap(1860, "Tab") + tap(1950, "End") + tap(2040, "Tab") + tap(2140, "Return")
        events += [(2300, "key_down S none 1"), (2420, "key_up S none"),
                   (2600, "key_down A none 0"), (2780, "key_up A none")] + tap(2920, "F6")
        modal = invoke(args, result, "04-help-audio-safe-stop", 3200, events, state=saved_bytes,
                       extra=["--workspace", "rotary", "--flat"])
        controls(modal, [edited])
        notes(modal, [EMPTY, UPPER_A, EMPTY, UPPER_S, EMPTY, UPPER_A, EMPTY], 3, 1)
        CASE.assertEqual(modal.saved_bytes, saved_bytes)
        CASE.assertEqual(modal.diagnostics["replay"]["device_starts"], 2)
        audio = modal.diagnostics["audio"]
        CASE.assertEqual((audio["requested_sample_rate"], audio["sample_rate"]), (44100, 44100))
        CASE.assertEqual((audio["requested_buffer_frames"], audio["buffer_frames"]), (2048, 2048))
        views(modal.diagnostics, [("rotary", "flat", overlay, 1280, 900) for overlay in
              ("none", "help", "none", "audio", "none")] + [("service", "flat", "none", 1280, 900)])
        clocks = [frame["inspection"]["frame_clock"] for frame in modal.diagnostics["presentation"]["observations"]
                  if frame["inspection"]["snapshot_available"]]
        CASE.assertTrue(any(right < left for left, right in zip(clocks, clocks[1:])), "Audio Apply starts a new clock lifecycle")
        result["checks"].append("Help/Audio modal gates: original UI holds clear; repeats remain suppressed until Up; Audio Apply changes 48k/512 to 44.1k/2048, retains all controls, starts one new lifecycle; fresh note works")

        events = [(200, "key_down A none 0")] + tap(450, "M", "ctrl") + tap(600, "F4") + tap(680, "F7")
        events += tap(760, "Home") + tabs(850, 5, 40) + tap(1120, "Return") + tap(1200, "Tab") + tap(1280, "Return")
        events += tap(1380, "Tab") + tap(1470, "Return")
        events += [(1560, "key_down A none 1"), (1680, "key_up A none"),
                   (1800, "key_down S none 0"), (1950, "key_up S none")] + tap(2100, "F5")
        no_input = invoke(args, result, "05-midi-no-input", 2350, events, state=saved_bytes,
                          extra=["--workspace", "service", "--flat", "--width", "960", "--height", "700"],
                          final_size=(960, 700), discovery=True)
        controls(no_input, [edited])
        notes(no_input, [EMPTY, UPPER_A, EMPTY, UPPER_S, EMPTY], 2, 1)
        CASE.assertEqual(no_input.saved_bytes, saved_bytes)
        CASE.assertEqual(no_input.diagnostics["replay"]["device_starts"], 1)
        views(no_input.diagnostics, [("service", "flat", overlay, 960, 700) for overlay in
              ("none", "midi", "none")] + [("rotary", "flat", "none", 960, 700)])
        observed_midi = no_input.diagnostics["midi"]
        baseline_midi = cold.diagnostics["midi"]
        for key in baseline_midi:
            if key != "discovery":
                CASE.assertEqual(observed_midi[key], baseline_midi[key], key)
        discovery_state = observed_midi["discovery"]
        for key in ("requests", "started", "completed"):
            CASE.assertEqual(discovery_state[key], 1, key)
        CASE.assertIn(discovery_state["discarded_results"], (0, 1))
        CASE.assertFalse(discovery_state["pending_after_shutdown"])
        result["checks"].append("MIDI No input Apply/Disconnect/Close: no native input epoch or packets; no implicit connection; modal releases/suppression and fresh keyboard play are intact; native discovery failure remains explicit")
    except Exception:
        result["failure"] = traceback.format_exc()
        (args.output / "assertion-failure.txt").write_text(result["failure"], encoding="utf-8")
    finally:
        result["executable_sha256_after"] = digest(args.executable)
        result["source_and_guide_sha256_after"] = {path: digest(ROOT / path) for path in source_paths}
        result["native_processes"] = len(result["runs"])
        result["native_successes"] = sum(run.get("returncode") == 0 for run in result["runs"])
        result["native_failures_preserved"] = sum(run.get("returncode") != 0 for run in result["runs"])
        result["operator_assertions_completed"] = result["failure"] is None
        result["limits"] = ["Dummy SDL, software renderer, no physical audio or controller evidence",
            "No native persistent pointer capture: dummy SDL_CaptureMouse fails immediately",
            "No sample-accurate replay or physical latency/deadline claim",
            "No screen-reader/accessibility or literal reference-image equality claim",
            "Pinned pre-A28 executable; no qualification of later rebuilt source"]
        save_json(args.output / "result.json", result)
    print(json.dumps({key: result[key] for key in ("native_processes", "native_successes",
        "native_failures_preserved", "operator_assertions_completed", "failure")}, indent=2))
    return 0 if result["failure"] is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
