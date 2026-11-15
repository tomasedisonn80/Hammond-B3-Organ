#!/usr/bin/env python3
"""Reproduce three real percussion-state captures into a new directory.

Requires a coherently built standalone, Python 3.10+ and Pillow. No image content
is synthesized: native BMP pixels are preserved losslessly as PNG. Dummy SDL
drivers and software rendering are explicit; no physical-device claim is made.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time

from PIL import Image, __version__ as pillow_version

DURATION = 1800


def identity(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"Expected a regular non-symlink file: {path}")
    raw = path.read_bytes()
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def require(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)


def write_json(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as out:
        json.dump(value, out, indent=2, sort_keys=True, allow_nan=False)
        out.write("\n")


def script(kind: str) -> tuple[str, int]:
    events = ["100 key_down F1 none 0", "110 key_up F1 none",
              "200 key_down A none 0", "220 key_down D none 0",
              "300 key_down F2 none 0", "310 key_up F2 none",
              "350 key_down G none 0", "400 key_down F3 none 0",
              "410 key_up F3 none", "450 key_down S none 0",
              "500 key_down F1 none 0", "510 key_up F1 none"]

    def tap(at: int, key: str, modifiers: str = "none") -> None:
        events.extend((f"{at} key_down {key} {modifiers} 0",
                       f"{at + 1} key_up {key} {modifiers}"))

    def tabs(at: int, count: int) -> None:
        for index in range(count):
            tap(at + 6 * index, "Tab")

    if kind == "eligible-upper-b":
        tabs(600, 58)  # Common controls + manuals, then PERC and VOL.
        tap(1000, "Space")
        tap(1050, "Tab")
        tap(1070, "Space")
        tap(1120, "Tab")
        tap(1140, "Space")
    elif kind == "fixed-d-off":
        tabs(600, 15)  # Upper preset D.
        tap(760, "Return")
        tabs(820, 42)  # Semantic PERC, independent of the changed visual order.
        tap(1150, "Space")
    elif kind == "cancel-stored-on":
        tabs(600, 13)  # Upper preset C/Cancel.
        tap(740, "Return")
        tabs(820, 45)  # VOL.
        tap(1120, "Space")
        tap(1150, "Tab")
        tap(1170, "Space")
        tap(1200, "Tab")
        tap(1220, "Space")
        tap(1280, "Tab", "shift")  # Return semantic focus to DECAY.
    else:
        raise ValueError("Unknown fixed capture case")
    require([int(row.split()[0]) for row in events] ==
            sorted(int(row.split()[0]) for row in events), "Replay is unordered")
    return ("B3UIREPLAY1\nduration_ms 1800\n"
            "# Four physical keys remain held. No Save, pointer or MIDI device use.\n"
            "# Every route/switch change is delivered through native keyboard input.\n"
            + "\n".join(events) + "\n", len(events))


def validate(data: dict, expected: dict, width: int, height: int, events: int) -> dict:
    require(data["schema_version"] == 3 and data["application"] == "hammond_standalone",
            "Wrong application diagnostics")
    require(data["errors"] == {"count": 0, "last": ""}, "Application reported errors")
    runtime, audio, session, replay = (data[k] for k in ("runtime", "audio", "session", "replay"))
    require(runtime["video_driver"] == audio["driver"] == "dummy" and
            runtime["renderer"] == "software", "Wrong renderer/drivers")
    require([runtime[k] for k in ("window_width", "window_height", "drawable_width", "drawable_height")]
            == [width, height, width, height], "Wrong logical/drawable dimensions")
    require(runtime["screenshot_written"] and runtime["screenshot_while_held"], "Missing held-state capture")
    require(audio["callback_count"] > 0 and audio["rendered_frames"] > 0, "No actual audio progress")
    require(audio["sample_rate"] == 48000 and audio["buffer_frames"] == 512 and audio["channels"] == 2,
            "Unexpected obtained audio configuration")
    for key in ("render_failures", "format_failures", "overrange_failures", "overrange_samples",
                "nonfinite_failures", "nonfinite_samples"):
        require(audio[key] == 0, f"audio.{key} is nonzero")
    for key in ("recovery_count", "queue_overflows", "rejected_commands", "fault_flags"):
        require(session[key] == 0, f"session.{key} is nonzero")
    require(not session["held_after_shutdown"] and not session["running_after_shutdown"], "Unjoined shutdown")
    for key in ("completed", "delivered", "passed", "final_acknowledged", "snapshot_available_before_shutdown",
                "session_running_before_shutdown"):
        require(replay[key] is True, f"replay.{key} failed")
    require(replay["scheduled_events"] == replay["pushed_events"] == events and replay["duration_ms"] == DURATION,
            "Replay delivery mismatch")
    require(replay["accepted_note_on_commands"] == 4 and replay["accepted_note_off_commands"] == 0,
            "Held-note ownership differs")
    require(not replay["observations_truncated"] and not replay["controls_pending_before_shutdown"] and
            not replay["save_pending_before_shutdown"], "Pending or truncated endpoint")
    endpoint = replay["before_shutdown"]
    require(endpoint["manual_notes"] == [[60, 64], [67]] and endpoint["pedal_ids"] == [3], "Wrong held pitches")
    require(data["controls"] == replay["desired_controls_before_shutdown"] == endpoint["controls"] == expected,
            "Applied/desired controls differ from the declared target")
    require(endpoint["resolved_sequence"] >= replay["last_submitted_sequence"] and
            endpoint["last_applied_sequence"] >= replay["last_submitted_sequence"], "Unacknowledged controls")
    painted = data["presentation"]["screenshot"]
    require(painted == data["presentation"]["last_painted"] == data["presentation"]["before_shutdown"],
            "Screenshot is not the recorded final paint")
    require(painted["workspace"] == "play" and painted["presentation"] == "dimensional" and
            painted["overlay"] == "none" and painted["elapsed_ms"] >= DURATION, "Wrong painted view")
    copied = painted["inspection"]
    require(copied["snapshot_available"] and copied["snapshot_read_succeeded"] and
            copied["snapshot_state"] == "current" and not copied["controls_pending"] and copied["frame_clock"] > 0,
            "Paint lacks current acknowledged copied state")
    require(painted["held_targets"] == {"upper": 2, "lower": 1, "pedals": 1}, "Painted held targets differ")
    require(painted["pointer_capture"] == {"sdl_captured": False, "ui_captured": False,
            "attempts": 0, "successes": 0, "losses": 0, "release_calls": 0}, "Unexpected pointer capture")
    midi = data["midi"]
    require(midi["source"] == "none" and not midi["active_before_shutdown"] and
            not midi["active_after_shutdown"] and midi["quiescent_after_shutdown"] and
            midi["diagnostics_stable_after_shutdown"] and not midi["shutdown_failed"], "Unexpected MIDI use/failure")
    return {"passed": True, "full_control_snapshot": expected, "painted_view": painted,
            "held_notes": endpoint["manual_notes"], "held_pedal_ids": endpoint["pedal_ids"],
            "callbacks": audio["callback_count"], "rendered_frames": audio["rendered_frames"],
            "events": events, "midi_backend": midi["backend"], "midi_source": midi["source"],
            "no_physical_device_or_native_window_claim": True}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--build", type=Path, required=True)
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo, build, exe = (p.resolve(strict=True) for p in (args.repo, args.build, args.exe))
    output = args.output.absolute()
    require(not os.path.lexists(output), "Output already exists; choose a new directory")
    old = json.loads((repo / "examples/demos/standalone-audio-preview-v1/provenance.json").read_text())
    expected_exe = old["executable"]["before"]
    require(identity(exe) == expected_exe, "Executable differs from the admitted capture build")
    for path, expected in old["source"]["files"].items():
        require(identity(repo / path) == expected, f"Source differs: {path}")
    for path, expected in old["build"]["files"].items():
        require(identity(build / path) == expected, f"Build input differs: {path}")
    module_path = repo / "tools/capture_standalone_interface.py"
    spec = importlib.util.spec_from_file_location("capture_contract", module_path)
    capture = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(capture)
    controls = deepcopy(capture.INITIAL_CONTROLS)
    controls["fixed_registrations"][0] = 0
    controls["preset_selections"][0] = 11
    state_bytes = capture.STATE.replace("manual upper selected B fixed_registration C# route_enabled 1",
                                        "manual upper selected B fixed_registration none route_enabled 1").encode("ascii")
    output.mkdir()
    for name in ("images", "inputs", "diagnostics"):
        (output / name).mkdir()
    state = output / "inputs/controls.b3controls"
    state.write_bytes(state_bytes)
    env = {"PATH": os.defpath, "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8",
           "SDL_AUDIODRIVER": "dummy", "SDL_VIDEODRIVER": "dummy", "SDL_RENDER_DRIVER": "software"}
    report = {"schema": 1, "status": "incomplete", "started_at_utc": datetime.now(timezone.utc).isoformat(),
              "capture": "actual-native-percussion-state-v1", "command": [sys.executable, *sys.argv],
              "platform": platform.platform(), "python": platform.python_version(), "pillow": pillow_version,
              "environment": env, "executable": {"path": str(exe), **expected_exe},
              "script": identity(Path(__file__)), "source_files": old["source"]["files"],
              "build_files": old["build"]["files"], "source_base_at_capture": capture.git_identity(repo),
              "source_boundary": "The Git base does not identify uncommitted UI source. Exact production hashes match the retained, previously built capture overlay.",
              "state_before": identity(state), "cases": []}
    specs = (("eligible-upper-b", 1672, 941, "HARM", (418.5156, 150.0, 73.9615, 48.0)),
             ("fixed-d-off", 1400, 820, "PERC", (137.7182, 150.0, 61.8141, 47.4)),
             ("cancel-stored-on", 1400, 820, "DECAY", (282.2296, 150.0, 61.8141, 47.4)))
    try:
        for name, width, height, focused, bounds in specs:
            expected = deepcopy(controls)
            if name == "fixed-d-off":
                expected["fixed_registrations"][0] = 2
                expected["preset_selections"][0] = 2
                expected["percussion"]["enabled"] = False
            else:
                expected["percussion"].update(harmonic=1, volume=1, decay=1)
            if name == "cancel-stored-on":
                expected["preset_selections"][0] = 0
                expected["route_enabled"][0] = False
            replay, count = script(name)
            replay_path = output / "inputs" / f"{name}.b3uireplay"
            replay_path.write_text(replay, encoding="ascii", newline="\n")
            diag = output / "diagnostics" / f"{name}.json"
            bmp, png = (output / "images" / f"{name}.{extension}" for extension in ("bmp", "png"))
            command = [str(exe), "--state", str(state), "--input-script", str(replay_path), "--workspace", "play",
                       "--width", str(width), "--height", str(height), "--sample-rate", "48000", "--buffer-frames", "512",
                       "--screenshot", str(bmp), "--diagnostics", str(diag)]
            case = {"name": name, "command": command, "status": "incomplete", "script": identity(replay_path),
                    "expected_focus": {"caption": focused, "contracted_bounds": list(bounds),
                                       "evidence": "Keyboard replay plus observed cyan cap outline; diagnostics do not encode normal semantic focus ID."}}
            report["cases"].append(case)
            started = time.monotonic()
            result = subprocess.run(command, cwd=output, env=env, stdin=subprocess.DEVNULL,
                                    capture_output=True, timeout=15)
            case.update(exit_code=result.returncode, elapsed_seconds=time.monotonic() - started)
            (output / "diagnostics" / f"{name}.stdout.txt").write_bytes(result.stdout)
            (output / "diagnostics" / f"{name}.stderr.txt").write_bytes(result.stderr)
            require(result.returncode == 0 and not result.stdout and not result.stderr,
                    f"Native process failed or reported output: {name}")
            data = json.loads(diag.read_text())
            case["validation"] = validate(data, expected, width, height, count)
            case["diagnostics"] = identity(diag)
            native_hash = identity(bmp)
            with Image.open(bmp) as native:
                native.load()
                require(native.size == (width, height), "Wrong native screenshot dimensions")
                mode, pixels = native.mode, native.tobytes()
                native.save(png, format="PNG", optimize=True, compress_level=9)
            with Image.open(png) as encoded:
                encoded.load()
                require((encoded.mode, encoded.size, encoded.tobytes()) == (mode, (width, height), pixels),
                        "PNG conversion changed native pixels")
                x, y, w, h = bounds
                cyan = [(px, py) for py in range(max(0, int(y)-3), min(height, int(y+h)+4))
                        for px in range(max(0, int(x)-3), min(width, int(x+w)+4))
                        if encoded.getpixel((px, py))[:3] == (165, 228, 223)]
                require(len(cyan) > 150, f"Expected focused cap has no cyan outline: {name}")
                case["expected_focus"]["observed_cyan_pixels"] = len(cyan)
                case["expected_focus"]["observed_cyan_bounds"] = [min(t[0] for t in cyan), min(t[1] for t in cyan),
                                                                   max(t[0] for t in cyan)+1, max(t[1] for t in cyan)+1]
            case["image"] = {"path": f"images/{name}.png", "png": identity(png), "native_bmp": native_hash,
                             "decoded_mode": mode, "width": width, "height": height,
                             "decoded_sha256": hashlib.sha256(pixels).hexdigest(), "lossless_conversion": True,
                             "native_bmp_removed_after_verification": True}
            bmp.unlink()
            require(identity(state) == report["state_before"], "Application changed input state")
            require(identity(exe) == expected_exe, "Executable changed during capture")
            case["status"] = "passed"
        for path, expected in report["source_files"].items():
            require(identity(repo / path) == expected, f"Source changed during capture: {path}")
        for path, expected in report["build_files"].items():
            require(identity(build / path) == expected, f"Build changed during capture: {path}")
        report["status"] = "passed"
    except Exception as error:
        report["error"] = str(error)
        report["status"] = "failed"
        raise
    finally:
        report["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        write_json(output / "provenance.json", report)
    shutil.copyfile(Path(__file__), output / "reproduce.py")
    write_json(output / "manifest.json", {"schema": 1, "files": {
        str(p.relative_to(output)): identity(p) for p in sorted(output.rglob("*")) if p.is_file()}})
    print(json.dumps({"status": report["status"], "cases": len(report["cases"]),
                      "bytes": sum(p.stat().st_size for p in output.rglob("*") if p.is_file())}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
