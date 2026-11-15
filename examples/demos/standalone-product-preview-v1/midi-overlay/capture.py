#!/usr/bin/env python3
"""Capture three native MIDI-OFF dialog frames under a separate overlay contract.

Requires the reviewed capture_standalone_interface.py identity helpers and a
qualified existing executable. This script never builds, saves controls,
opens/enumerates MIDI, edits pixels, or overwrites an existing output directory.
The CLI calibration 20/100/Inverted is illustrative, not a measured pedal.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
from itertools import groupby
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time


sys.dont_write_bytecode = True
DURATION_MS = 4800
CASES = (
    ("midi-reference-1672x941", 1672, 941, "dimensional"),
    ("midi-minimum-960x700", 960, 700, "dimensional"),
    ("midi-flat-minimum-960x700", 960, 700, "flat"),
)
CALIBRATION = {"minimum": 20, "maximum": 100, "inverted": True}
CALIBRATION_OBSERVATION = {
    "model": "midi-expression-endpoints-v1", "configured": CALIBRATION,
    "selected": CALIBRATION, "selected_valid": True, "active": None,
    "reconnect_pending": False, "release_pending": False, "pending": None,
}
FOCUS_PATH = list(range(11)) + [0, 10, 9, 8, 7]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def replay(common, presentation: str) -> tuple[str, int]:
    initial, _ = common.replay("play", presentation)
    events = [line for line in initial.splitlines() if line and line[0].isdigit()]
    events += ["1250 key_down M ctrl 0", "1260 key_up M ctrl"]
    for index in range(11):
        at = 1500 + 200 * index
        events += [f"{at} key_down Tab none 0", f"{at + 1} key_up Tab none"]
    for at in (3750, 3950, 4150, 4350):
        events += [f"{at} key_down Tab shift 0", f"{at + 1} key_up Tab shift"]
    return (f"B3UIREPLAY1\nduration_ms {DURATION_MS}\n"
            "# Hold Upper 60/64, Lower 67 and pedal 3; edit retained Upper B 16-foot 7 -> 8.\n"
            "# Ctrl+M then releases all four UI owners through the real application path.\n"
            "# Traverse all eleven modal focus stops and both wrap directions.\n"
            "# End on expression direction. No Apply, Save, MIDI replay or physical MIDI request.\n"
            + "\n".join(events) + "\n", len(events))


def validate(data: dict, width: int, height: int, presentation: str, events: int, common) -> dict:
    require(data["schema_version"] == 3 and data["application"] == "hammond_standalone",
            "expected standalone schema 3")
    require(data["errors"] == {"count": 0, "last": ""}, "application reported errors")
    runtime, audio, session, midi = (data[key] for key in ("runtime", "audio", "session", "midi"))
    require(runtime["video_driver"] == audio["driver"] == "dummy" and runtime["renderer"] == "software",
            "dummy/software environment did not hold")
    require([runtime[k] for k in ("window_width", "window_height", "drawable_width", "drawable_height")]
            == [width, height, width, height], "logical/drawable dimensions differ")
    require(runtime["screenshot_written"] is True and runtime["screenshot_while_held"] is False,
            "dialog screenshot missing or unexpectedly held")
    require(runtime["rendered_images"] > 0 and audio["callback_count"] > 0 and audio["rendered_frames"] > 0,
            "missing actual audio/paint progress")
    require(audio["sample_rate"] == 48000 and audio["buffer_frames"] == 512 and audio["channels"] == 2
            and audio["sample_format"] == audio["native_float32_format"], "unexpected audio configuration")
    for key in ("render_failures", "format_failures", "overrange_failures", "overrange_samples",
                "nonfinite_failures", "nonfinite_samples"):
        require(type(audio[key]) is int and audio[key] == 0, f"audio.{key} is nonzero or malformed")
    for key in ("recovery_count", "queue_overflows", "rejected_commands", "fault_flags"):
        require(type(session[key]) is int and session[key] == 0, f"session.{key} is nonzero or malformed")
    require(session["held_after_shutdown"] is False and session["running_after_shutdown"] is False,
            "joined shutdown did not clear ownership/running")
    require(midi["source"] == "none" and "midi_replay" not in data
            and midi["backend_available"] is False and midi["backend"] == "unavailable"
            and midi["state_before_shutdown"] == midi["state_after_shutdown"] == "unavailable",
            "overlay contract requires genuinely unavailable native MIDI and no MIDI replay")
    for key in ("generation", "opened_port_index", "maximum_drained_per_turn", "retirements",
                "fault_retirements", "session_recoveries_observed", "open_failures", "submit_failures",
                "release_batches", "release_commands_accepted", "release_sequence", "parameter_messages",
                "retired_fault_bits"):
        require(type(midi[key]) is int and midi[key] == 0, f"midi.{key} unexpectedly active")
    require(midi["requested_port"] == midi["port_name"] == "" and midi["arrival_time_source"] == "none"
            and midi["arrival_time_is_sample_time"] is False
            and midi["channels"] == {"upper": 1, "lower": 2, "pedals": 3}
            and midi["status"] == "MIDI backend unavailable in this build.", "unexpected MIDI settings/status")
    for key in ("active_before_shutdown", "active_after_shutdown", "shutdown_failed", "startup_failed", "release_pending"):
        require(midi[key] is False, f"midi.{key} is not false")
    for key in ("quiescent_after_shutdown", "diagnostics_stable_after_shutdown"):
        require(midi[key] is True, f"midi.{key} is not true")
    device_keys = ("callback_messages", "forwarded_messages", "filtered_messages", "admission_failures",
                   "backend_errors", "callback_contentions", "disconnects", "close_errors", "last_arrival_ns")
    discovery_keys = ("requests", "started", "completed", "discarded_results", "failures")
    discovery_flags = ("pending_before_shutdown", "shutdown_join_performed", "pending_after_shutdown")
    require(midi["device"] == dict.fromkeys(device_keys, 0)
            and all(type(midi["device"][key]) is int for key in device_keys), "native MIDI device activity")
    require(midi["discovery"] == {**dict.fromkeys(discovery_keys, 0), **dict.fromkeys(discovery_flags, False)}
            and all(type(midi["discovery"][key]) is int for key in discovery_keys)
            and all(midi["discovery"][key] is False for key in discovery_flags), "native MIDI discovery activity")
    require(midi["inbox"]["capacity"] == 256
            and all(type(value) is int and value == 0 for key, value in midi["inbox"].items() if key != "capacity")
            and all(type(value) is int and value == 0 for value in midi["decoder"].values()), "MIDI packet/decoder activity")
    require(midi["expression_calibration"] == {**CALIBRATION_OBSERVATION, "pre_shutdown_active": None},
            "final selected/configured/active/pending calibration differs")
    record = data["replay"]
    for key in ("completed", "delivered", "passed", "final_acknowledged", "snapshot_available_before_shutdown",
                "session_running_before_shutdown"):
        require(record[key] is True, f"replay.{key} is false")
    require(record["duration_ms"] == DURATION_MS and record["scheduled_events"] == record["pushed_events"] == events,
            "replay event delivery/duration differs")
    # Modal entry submits one scoped ReleaseUiNotes command. It is not four
    # individual Note Off commands, so the public note-off counter stays zero.
    require(record["accepted_note_on_commands"] == 4 and record["accepted_note_off_commands"] == 0
            and record["device_starts"] == 1 and record["observations_truncated"] is False,
            "four held UI notes were not released cleanly on modal entry")
    require(record["controls_pending_before_shutdown"] is False and record["save_pending_before_shutdown"] is False,
            "endpoint retains pending controls/save")
    endpoint = record["before_shutdown"]
    require(endpoint["manual_notes"] == [[], []] and endpoint["pedal_ids"] == [], "final held notes remain")
    require(data["controls"] == record["desired_controls_before_shutdown"] == endpoint["controls"] == common.FINAL_CONTROLS,
            "complete musical control state differs")
    require(endpoint["resolved_sequence"] >= record["last_submitted_sequence"]
            and endpoint["last_applied_sequence"] >= record["last_submitted_sequence"], "release/edit not acknowledged")
    observations = record["observations"]
    for controls in (common.INITIAL_CONTROLS, common.FINAL_CONTROLS):
        require(any(item["controls"] == controls and item["manual_notes"] == [[60, 64], [67]]
                    and item["pedal_ids"] == [3] and item["overlay"] == "none" for item in observations),
                "missing fully held observation before/after live edit and before modal release")
    modal = [item for item in observations if item["overlay"] == "midi"]
    require(any(item["manual_notes"] == [[], []] and item["pedal_ids"] == []
                and item["resolved_sequence"] >= item["last_submitted_sequence"]
                and item["last_applied_sequence"] >= item["last_submitted_sequence"] for item in modal),
            "no acknowledged empty-owner modal observation")
    focus_path = [focus for focus, _ in groupby(item["modal_focus"] for item in modal)]
    require(focus_path == FOCUS_PATH, "eleven-focus traversal or wrap differs")
    require(all(item["expression_calibration"] == CALIBRATION_OBSERVATION
                and item["controls"] == common.FINAL_CONTROLS and item["error_count"] == 0 for item in modal),
            "modal observations changed selected/configured calibration, musical controls or errors")
    view = data["presentation"]
    require(view["initial_workspace"] == "play" and view["initial_presentation"] == "dimensional"
            and view["observations_truncated"] is False, "unexpected startup/truncated painted history")
    painted = view["screenshot"]
    require(painted == view["before_shutdown"] == view["last_painted"] and painted["workspace"] == "play"
            and painted["presentation"] == presentation and painted["overlay"] == "midi"
            and [painted["window_width"], painted["window_height"]] == [width, height]
            and painted["elapsed_ms"] >= DURATION_MS and 0 < painted["rendered_image"] <= runtime["rendered_images"],
            "capture is not the exact final painted MIDI frame")
    require(painted["held_targets"] == {"upper": 0, "lower": 0, "pedals": 0}
            and all(type(v) is int for v in painted["held_targets"].values())
            and painted["modal_focus"] == 7 and painted["expression_calibration"] == CALIBRATION_OBSERVATION,
            "painted release, final direction focus or calibration differs")
    pointer = painted["pointer_capture"]
    require(pointer == {"sdl_captured": False, "ui_captured": False, "attempts": 0, "successes": 0,
                        "losses": 0, "release_calls": 0} and pointer["sdl_captured"] is False
            and pointer["ui_captured"] is False, "keyboard-only run unexpectedly captured a pointer")
    copied = painted["inspection"]
    require(copied["snapshot_available"] is True and copied["snapshot_read_succeeded"] is True
            and copied["snapshot_state"] == "current" and copied["controls_pending"] is False
            and copied["frame_clock"] > 0 and copied["publication_revision"] > 0, "missing current acknowledged paint")
    painted_focus = sorted({item["modal_focus"] for item in view["observations"] if item["overlay"] == "midi"})
    require(painted_focus == list(range(11)), "not all eleven focus stops were actually painted")
    return {"passed": True, "actual_painted_view": painted, "ui_events": events,
            "callbacks": audio["callback_count"], "rendered_frames": audio["rendered_frames"],
            "held_before_modal": {"manual_notes": [[60, 64], [67]], "pedal_ids": [3]},
            "live_edit": {"target": "Upper B 16-foot retained drawbar", "before": 7, "after": 8},
            "modal_released_ui_owners": 4, "release_mechanism": "scoped ReleaseUiNotes, not individual Note Offs",
            "accepted_individual_note_off_commands": 0, "final_acknowledged": True,
            "complete_control_state_checked": True, "input_state_file_unchanged": True,
            "focus_path": focus_path, "painted_focus_indices": painted_focus,
            "illustrative_calibration": CALIBRATION, "active_calibration": None,
            "native_device_activity": False, "native_discovery_activity": False,
            "joined_shutdown_clear": True, "midi_backend_available": False, "midi_backend": "unavailable"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--build-root", type=Path, required=True)
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--source-qualification", type=Path, required=True)
    parser.add_argument("--expected-exe-sha256", required=True)
    parser.add_argument("--expected-source-head", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dummy-sdl", action="store_true", required=True)
    args = parser.parse_args()
    source, build, exe, report = (path.resolve(strict=True) for path in
                                 (args.source_root, args.build_root, args.exe, args.source_qualification))
    require(not os.path.lexists(args.output), "output exists; refusing overwrite")
    helper_path = source / "tools/capture_standalone_interface.py"
    spec = importlib.util.spec_from_file_location("capture_identity_helpers", helper_path)
    common = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(common)
    from PIL import Image, __version__ as pillow_version
    tool = Path(__file__).resolve()
    tool_before, helper_before, binary_before = map(common.identity, (tool, helper_path, exe))
    require(binary_before["sha256"] == args.expected_exe_sha256, "executable SHA-256 differs")
    qualified = common.qualification(report, source, binary_before)
    source_before = common.inventory(common.production_paths(source), source)
    build_before = common.inventory(common.build_paths(build), build)
    config_before, git_before = common.configuration(build), common.git_identity(source)
    require(git_before["head"] == args.expected_source_head, "source HEAD differs")
    require(config_before["HAMMOND_ENABLE_MIDI"] == "OFF", "only a compiled MIDI-OFF build is admitted")
    environment = {"PATH": os.defpath, "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8",
                   "SDL_AUDIODRIVER": "dummy", "SDL_VIDEODRIVER": "dummy", "SDL_RENDER_DRIVER": "software"}
    for key in ("SystemRoot", "WINDIR"):
        if key in os.environ:
            environment[key] = os.environ[key]
    output = args.output.absolute()
    output.mkdir()
    for name in ("inputs", "images", "diagnostics", "runs"):
        (output / name).mkdir()
    record = {"schema_version": 1, "capture_contract": "standalone-product-midi-overlay-capture-v1",
              "status": "incomplete", "started_at_utc": datetime.now(timezone.utc).isoformat(),
              "command": [sys.executable, *sys.argv], "output_directory_at_capture": str(output),
              "platform": platform.platform(), "python": platform.python_version(), "pillow": pillow_version,
              "environment": environment, "tool": {"path": str(tool), "before": tool_before, "retained_path": "capture.py"},
              "identity_helper": {"path": str(helper_path), "before": helper_before},
              "executable": {"path": str(exe), "before": binary_before},
              "source": {"root": str(source), "git_before": git_before, "files": source_before,
                         "inventory_sha256_before": common.inventory_digest(source_before), "checked_author_report": qualified},
              "build": {"root": str(build), "files": build_before,
                        "inventory_sha256_before": common.inventory_digest(build_before),
                        "selected_configuration_before": config_before},
              "qualification": "Actual native modal pixels with explicit dummy audio/video, software renderer and compiled MIDI backend OFF. No hardware, physical display, latency/deadline, accessibility, measured pedal/instrument or literal 1:1 reference claim.",
              "boundary": "Separate from the normal gallery's held-note/no-overlay admission. Ctrl+M releases UI owners; these final modal frames have no held target. Illustrative CLI calibration is configured/selected, never active. Supplied source/build report matches; this script does not rebuild or independently attest compilation.",
              "visual_review": "Separate independent visual admission is required.", "cases": []}
    error = None
    try:
        (output / "capture.py").write_bytes(tool.read_bytes())
        (output / "inputs/source-qualification.json").write_bytes(report.read_bytes())
        require(common.identity(output / "inputs/source-qualification.json")["sha256"] == qualified["sha256"],
                "qualification changed during copy")
        state = output / "inputs/controls.b3controls"
        state.write_text(common.STATE, encoding="ascii")
        plans = {}
        for presentation in ("dimensional", "flat"):
            script, events = replay(common, presentation)
            path = output / "inputs" / f"midi-{presentation}.b3uireplay"
            path.write_text(script, encoding="ascii")
            plans[presentation] = path, events
        inputs_before = common.inventory(list((output / "inputs").iterdir()), output)
        record["inputs"] = {"before": inputs_before}
        for name, width, height, presentation in CASES:
            require(common.identity(exe) == binary_before
                    and common.inventory(common.production_paths(source), source) == source_before
                    and common.git_identity(source) == git_before, "source/executable changed before capture")
            working = output / "runs" / name
            working.mkdir()
            script, events = plans[presentation]
            diagnostics = output / "diagnostics" / f"{name}.json"
            bmp, png = output / "images" / f"{name}.bmp", output / "images" / f"{name}.png"
            command = [str(exe), "--state", str(state), "--input-script", str(script), "--workspace", "play",
                       "--width", str(width), "--height", str(height), "--sample-rate", "48000", "--buffer-frames", "512",
                       "--expression-min", "20", "--expression-max", "100", "--expression-invert",
                       "--screenshot", str(bmp), "--diagnostics", str(diagnostics)]
            case = {"name": name, "width": width, "height": height, "workspace": "play", "presentation": presentation,
                    "overlay": "midi", "cwd": str(working), "command": command, "timeout_seconds": 12, "status": "incomplete"}
            record["cases"].append(case)
            started = time.monotonic()
            try:
                process = subprocess.run(command, cwd=working, env=environment, stdin=subprocess.DEVNULL,
                                         capture_output=True, timeout=12, check=False)
            except subprocess.TimeoutExpired as timeout:
                (output / "diagnostics" / f"{name}.stdout.txt").write_bytes(timeout.stdout or b"")
                (output / "diagnostics" / f"{name}.stderr.txt").write_bytes(timeout.stderr or b"")
                case["timed_out"] = True
                raise
            case["elapsed_seconds"], case["exit_code"] = time.monotonic() - started, process.returncode
            (output / "diagnostics" / f"{name}.stdout.txt").write_bytes(process.stdout)
            (output / "diagnostics" / f"{name}.stderr.txt").write_bytes(process.stderr)
            require(process.returncode == 0 and not process.stdout and not process.stderr,
                    f"{name}: native failure/output; original logs retained")
            require(common.inventory(list((output / "inputs").iterdir()), output) == inputs_before, "input/state bytes changed")
            case["validation"] = validate(common.read_json(diagnostics), width, height, presentation, events, common)
            case["diagnostics"] = {"path": str(diagnostics.relative_to(output)), **common.identity(diagnostics)}
            bmp_identity = common.identity(bmp)
            with Image.open(bmp) as native:
                native.load()
                mode, size, pixels = native.mode, native.size, native.tobytes()
                require(size == (width, height), "native BMP dimensions differ")
                native.save(png, format="PNG", optimize=True, compress_level=9)
            with Image.open(png) as encoded:
                encoded.load()
                require((encoded.mode, encoded.size, encoded.tobytes()) == (mode, size, pixels), "PNG changed native pixels")
            case["image"] = {"path": str(png.relative_to(output)), "native_bmp": bmp_identity,
                             "png": common.identity(png), "decoded_mode": mode, "width": width, "height": height,
                             "decoded_sha256": hashlib.sha256(pixels).hexdigest(), "lossless_bmp_to_png": True,
                             "native_bmp_removed_after_verification": True}
            bmp.unlink()
            working.rmdir()
            case["status"] = "passed"
        record["status"] = "passed"
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as caught:
        error = str(caught)
        record["status"], record["failure"] = "failed", error
    finally:
        try:
            source_after = common.inventory(common.production_paths(source), source)
            build_after = common.inventory(common.build_paths(build), build)
            config_after, git_after = common.configuration(build), common.git_identity(source)
            record["executable"]["after"] = common.identity(exe)
            record["tool"]["after"] = common.identity(tool)
            record["identity_helper"]["after"] = common.identity(helper_path)
            record["source"]["git_after"] = git_after
            record["source"]["inventory_sha256_after"] = common.inventory_digest(source_after)
            record["source"]["changed_paths"] = sorted(k for k in source_before.keys() | source_after.keys()
                                                       if source_before.get(k) != source_after.get(k))
            record["build"]["inventory_sha256_after"] = common.inventory_digest(build_after)
            record["build"]["selected_configuration_after"] = config_after
            record["build"]["changed_paths"] = sorted(k for k in build_before.keys() | build_after.keys()
                                                      if build_before.get(k) != build_after.get(k))
            record["inputs"]["after"] = common.inventory(list((output / "inputs").iterdir()), output)
            unchanged = (record["executable"]["after"] == binary_before and record["tool"]["after"] == tool_before
                         and record["identity_helper"]["after"] == helper_before and source_before == source_after
                         and build_before == build_after and config_before == config_after and git_before == git_after
                         and record["inputs"]["before"] == record["inputs"]["after"]
                         and common.identity(report)["sha256"] == qualified["sha256"]
                         and common.identity(output / "capture.py") == tool_before)
            record["all_recorded_inputs_unchanged"] = unchanged
            if not unchanged:
                record["status"], record["identity_failure"] = "failed", "capture source/build/tool/input identity drift"
        except (OSError, ValueError, KeyError, subprocess.SubprocessError) as caught:
            record["status"], record["identity_failure"] = "failed", str(caught)
        record["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        common.write_json(output / "provenance.json", record)
        files = common.inventory([path for path in output.rglob("*") if path.is_file()], output)
        common.write_json(output / "manifest.json", {"schema_version": 1, "status": record["status"], "files": files,
            "total_bytes_excluding_manifest": sum(item["bytes"] for item in files.values()),
            "scope": "Exact separate MIDI-overlay payload/provenance/script; excludes this manifest and later authored README/review. It does not extend the parent normal gallery contract. Failed captures remain failures."})
        runs = output / "runs"
        if runs.is_dir() and not any(runs.iterdir()):
            runs.rmdir()
    print(json.dumps({"status": record["status"], "output": str(output), "captures": len(record["cases"]),
                      "failure": error, "identity_failure": record.get("identity_failure")}, sort_keys=True))
    return 0 if record["status"] == "passed" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"capture_midi_overlay: {error}", file=sys.stderr)
        raise SystemExit(2)
