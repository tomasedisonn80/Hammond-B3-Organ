#!/usr/bin/env python3
"""Capture eight real native interface views into a new, bounded gallery.

Requires Python 3.10+, Pillow, an already built standalone and a source/build
qualification JSON with ``binary_sha256`` and ``source_sha256`` members. The
qualification is checked, not treated as an independent build attestation.
SDL dummy audio/video and the software renderer must be explicitly admitted.
This utility never builds, changes application sources, saves controls, uses
image generation, overwrites a gallery, or substitutes artwork for app pixels.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import time


DURATION_MS = 1800
CASES = (
    ("play-reference-1672x941", 1672, 941, "play", "dimensional"),
    ("play-default-1280x900", 1280, 900, "play", "dimensional"),
    ("play-minimum-960x700", 960, 700, "play", "dimensional"),
    ("service-reference-1672x941", 1672, 941, "service", "dimensional"),
    ("service-minimum-960x700", 960, 700, "service", "dimensional"),
    ("rotary-reference-1672x941", 1672, 941, "rotary", "dimensional"),
    ("rotary-minimum-960x700", 960, 700, "rotary", "dimensional"),
    ("flat-minimum-960x700", 960, 700, "play", "flat"),
)
STATE = """B3CONTROLS4
registration_catalog atlas-chapel-nominal-v1 sha256 c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf
expression 0.75
percussion enabled 1 harmonic second volume normal decay slow
pedal drawbars 8 0
manual upper selected B fixed_registration C# route_enabled 1
bank A 1 2 3 4 5 6 7 8 0
bank B 7 6 5 4 3 4 2 5 3
manual lower selected A fixed_registration none route_enabled 1
bank A 7 6 5 4 3 4 2 4 2
bank B 0 0 8 0 0 0 0 0 0
end
"""
INITIAL_CONTROLS = {
    "manual_drawbars": [[[1, 2, 3, 4, 5, 6, 7, 8, 0], [7, 6, 5, 4, 3, 4, 2, 5, 3]],
                        [[7, 6, 5, 4, 3, 4, 2, 4, 2], [0, 0, 8, 0, 0, 0, 0, 0, 0]]],
    "selected_banks": [1, 0], "fixed_registrations": [1, 0], "preset_selections": [1, 10],
    "route_enabled": [True, True], "expression": 0.75, "pedal_drawbars": [8, 0],
    "percussion": {"enabled": True, "harmonic": 0, "volume": 0, "decay": 0},
}
FINAL_CONTROLS = deepcopy(INITIAL_CONTROLS)
FINAL_CONTROLS["manual_drawbars"][0][1][0] = 8
REQUIRED_QUALIFIED_SOURCES = tuple(
    f"apps/standalone/{name}{extension}"
    for name in ("InstrumentView", "UiModel", "Drawing", "InspectionModel")
    for extension in (".cpp", ".h")
) + ("apps/standalone/main.cpp", "docs/design/atlas-cover-reference.jpg")
CONFIG_KEYS = (
    "CMAKE_BUILD_TYPE", "CMAKE_CXX_COMPILER", "CMAKE_CXX_FLAGS", "CMAKE_CXX_FLAGS_RELEASE",
    "HAMMOND_BUILD_STANDALONE", "HAMMOND_ENABLE_MIDI", "HAMMOND_SDL2_ROOT",
    "HAMMOND_RTMIDI_ROOT", "SDL_ALSA", "ALSA_LIBRARY", "ALSA_INCLUDE_DIR",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def identity(path: Path) -> dict:
    require(path.is_file() and not path.is_symlink(), f"expected a regular, non-symlink file: {path}")
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
            size += len(block)
    return {"bytes": size, "sha256": digest.hexdigest()}


def inventory(paths: list[Path], root: Path) -> dict:
    return {str(path.relative_to(root)): identity(path) for path in sorted(set(paths))}


def inventory_digest(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def write_json(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def read_json(path: Path) -> dict:
    def pairs(items: list[tuple[str, object]]) -> dict:
        result = {}
        for key, value in items:
            require(key not in result, f"duplicate JSON member: {key}")
            result[key] = value
        return result

    def bad_number(value: str) -> None:
        raise ValueError(f"invalid JSON numeric token: {value}")

    result = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs, parse_constant=bad_number)
    require(isinstance(result, dict), f"expected a JSON object: {path}")
    return result


def git_identity(source: Path) -> dict:
    result = subprocess.run(["git", "-C", str(source), "rev-parse", "HEAD", "HEAD^{tree}"],
                            stdin=subprocess.DEVNULL, capture_output=True, timeout=10, check=True)
    head, tree = result.stdout.decode("ascii").splitlines()
    return {"head": head, "committed_tree": tree}


def production_paths(source: Path) -> list[Path]:
    # Pin production inputs, including untracked overlay headers. Concurrent test,
    # install-rule and documentation edits do not identify the rendered program.
    paths = [p for p in (source / "apps/standalone").iterdir() if p.suffix in (".h", ".cpp")]
    for name in ("include", "src", "assets/standalone", "data/profiles", "data/registrations",
                 "data/scanner", "data/rotary"):
        paths.extend(p for p in (source / name).rglob("*") if p.is_file())
    for name in ("data/pedal-map.json", "data/parameter-registry.json", "data/dependencies/sdl2-lock.json",
                 "data/dependencies/rtmidi-lock.json", "docs/design/atlas-reference.json",
                 "docs/design/atlas-cover-reference.jpg", "tools/compile_profile.py", "tools/embed_profile.py",
                 "tools/compile_reference_art.py", "tools/compile_chapel_presets.py"):
        path = source / name
        if path.is_file():
            paths.append(path)
    return paths


def build_paths(build: Path) -> list[Path]:
    paths = []
    for name in ("generated", "apps/standalone/generated"):
        paths.extend(p for p in (build / name).rglob("*.h") if p.is_file())
    for name in ("nominal.b3p", "libhammond_core.a"):
        if (build / name).is_file():
            paths.append(build / name)
    for pattern in ("apps/standalone/*.a", "_sdl2/*.a", "_rtmidi/*.a"):
        paths.extend(p for p in build.glob(pattern) if p.is_file())
    require((build / "apps/standalone/generated/EmbeddedProfile.h") in paths,
            "missing generated standalone profile")
    require((build / "apps/standalone/generated/ReferenceArtData.h") in paths,
            "missing generated standalone reference artwork")
    return paths


def configuration(build: Path) -> dict:
    cache = {}
    for line in (build / "CMakeCache.txt").read_text(encoding="utf-8").splitlines():
        if line and not line.startswith(("#", "//")) and ":" in line and "=" in line:
            key_type, value = line.split("=", 1)
            key = key_type.split(":", 1)[0]
            if key in CONFIG_KEYS:
                cache[key] = value
    return cache


def qualification(path: Path, source: Path, exe: dict) -> dict:
    result = read_json(path)
    expected = result.get("binary_sha256")
    require(isinstance(expected, str) and re.fullmatch(r"[0-9a-f]{64}", expected) is not None,
            "qualification needs binary_sha256")
    require(expected == exe["sha256"], "qualification executable digest differs; rebuild/requalify before capture")
    files = result.get("source_sha256")
    require(isinstance(files, dict) and all(name in files for name in REQUIRED_QUALIFIED_SOURCES),
            "qualification must pin the current renderer, model, drawing, inspection, main and reference sources")
    for name, digest in files.items():
        require(isinstance(name, str) and isinstance(digest, str)
                and re.fullmatch(r"[0-9a-f]{64}", digest) is not None, "invalid qualification source entry")
        relative = Path(name)
        require(not relative.is_absolute() and ".." not in relative.parts, "qualification source escapes its root")
        require(identity(source / relative)["sha256"] == digest, f"qualification source digest differs: {name}")
    return {"report_path_at_capture": str(path), **identity(path), "checked_source_sha256": files,
            "binary_sha256": expected,
            "meaning": "Supplied author build report matched the current files and executable. This utility did not rebuild or independently attest source-to-binary provenance."}


def replay(workspace: str, presentation: str) -> tuple[str, int]:
    # Keyboard-only replay works at every size and does not rely on dummy mouse
    # capture. Each held physical key owns a distinct logical target.
    events = [
        "100 key_down F1 none 0", "110 key_up F1 none", "200 key_down A none 0", "220 key_down D none 0",
        "300 key_down F2 none 0", "310 key_up F2 none", "350 key_down G none 0",
        "400 key_down F3 none 0", "410 key_up F3 none", "450 key_down S none 0",
        "500 key_down F1 none 0", "510 key_up F1 none",
    ]
    # The frozen workspace contract has 10 common controls, then Upper Edit A/B,
    # 12 presets and the first drawbar: the 25th Tab from initial no-focus.
    for index in range(25):
        offset = 600 + 10 * index
        events.extend((f"{offset} key_down Tab none 0", f"{offset + 1} key_up Tab none"))
    events.extend(("900 key_down Up none 0", "910 key_up Up none"))
    key = {"play": "F4", "rotary": "F5", "service": "F6"}[workspace]
    events.extend((f"1100 key_down {key} none 0", f"1110 key_up {key} none"))
    if presentation == "flat":
        events.extend(("1150 key_down F7 none 0", "1160 key_up F7 none"))
    return (f"B3UIREPLAY1\nduration_ms {DURATION_MS}\n"
            "# Upper 60/64, Lower 67 and pedal 3 stay held through the captured endpoint.\n"
            "# Change retained Upper B 16-foot drawbar 7 -> 8 while notes are held.\n"
            "# Upper fixed C# continues sounding; Lower uses adjustable A. No Save.\n"
            + "\n".join(events) + "\n", len(events))


def validate(data: dict, width: int, height: int, workspace: str, presentation: str, event_count: int) -> dict:
    require(data["schema_version"] == 3 and data["application"] == "hammond_standalone",
            "expected standalone diagnostics schema 3")
    require(data["errors"] == {"count": 0, "last": ""}, "native application reported errors")
    runtime, audio, session, midi = (data[key] for key in ("runtime", "audio", "session", "midi"))
    require(runtime["video_driver"] == audio["driver"] == "dummy" and runtime["renderer"] == "software",
            "explicit dummy/software environment did not hold")
    require([runtime[k] for k in ("window_width", "window_height", "drawable_width", "drawable_height")]
            == [width, height, width, height], "actual logical/drawable dimensions differ")
    require(runtime["screenshot_written"] is True and runtime["screenshot_while_held"] is True,
            "missing native held-state screenshot")
    require(audio["callback_count"] > 0 and audio["rendered_frames"] > 0 and runtime["rendered_images"] > 0,
            "no actual audio/render progress")
    require(audio["sample_rate"] == 48000 and audio["buffer_frames"] == 512 and audio["channels"] == 2
            and audio["sample_format"] == audio["native_float32_format"], "unexpected obtained audio configuration")
    for key in ("render_failures", "format_failures", "overrange_failures", "overrange_samples",
                "nonfinite_failures", "nonfinite_samples"):
        require(audio[key] == 0, f"audio.{key} is nonzero")
    for key in ("recovery_count", "queue_overflows", "rejected_commands", "fault_flags"):
        require(session[key] == 0, f"session.{key} is nonzero")
    require(session["held_after_shutdown"] is False and session["running_after_shutdown"] is False,
            "joined shutdown did not clear owners/running state")
    require(midi["source"] == "none" and midi["generation"] == 0 and midi["requested_port"] == ""
            and midi["port_name"] == "" and midi["state_before_shutdown"] == midi["state_after_shutdown"] == "closed"
            and all(value == 0 for value in midi["device"].values()) and midi["discovery"]["requests"] == 0,
            "capture unexpectedly opened/enumerated a native MIDI device")
    require(midi["quiescent_after_shutdown"] is True and midi["diagnostics_stable_after_shutdown"] is True
            and midi["active_after_shutdown"] is False and not midi["shutdown_failed"] and not midi["startup_failed"],
            "MIDI shutdown was not clean and quiescent")
    record = data["replay"]
    for key in ("completed", "delivered", "passed", "final_acknowledged", "snapshot_available_before_shutdown",
                "session_running_before_shutdown"):
        require(record[key] is True, f"replay.{key} is false")
    require(record["duration_ms"] == DURATION_MS and record["scheduled_events"] == record["pushed_events"] == event_count,
            "replay duration or event delivery differs")
    require(record["accepted_note_on_commands"] == 4 and record["accepted_note_off_commands"] == 0
            and record["device_starts"] == 1 and record["observations_truncated"] is False,
            "held-note ownership, device or observation counts differ")
    require(record["controls_pending_before_shutdown"] is False and record["save_pending_before_shutdown"] is False,
            "capture endpoint has pending controls/save")
    endpoint = record["before_shutdown"]
    require(endpoint["manual_notes"] == [[60, 64], [67]] and endpoint["pedal_ids"] == [3],
            "expected Upper/Lower/Pedal holds missing")
    require(data["controls"] == record["desired_controls_before_shutdown"] == endpoint["controls"] == FINAL_CONTROLS,
            "final live control state differs")
    require(endpoint["resolved_sequence"] >= record["last_submitted_sequence"]
            and endpoint["last_applied_sequence"] >= record["last_submitted_sequence"],
            "final sound command was not acknowledged")
    require(any(item["controls"] == INITIAL_CONTROLS and item["manual_notes"] == [[60, 64], [67]]
                and item["pedal_ids"] == [3] for item in record["observations"]),
            "no observed held state before the live drawbar edit")
    view = data["presentation"]
    require(view["initial_workspace"] == "play" and view["initial_presentation"] == "dimensional"
            and view["observations_truncated"] is False, "unexpected startup view or truncated presentation history")
    painted = view["screenshot"]
    require(isinstance(painted, dict), "missing actual screenshot paint observation")
    require(painted["workspace"] == workspace and painted["presentation"] == presentation
            and painted["overlay"] == "none" and [painted["window_width"], painted["window_height"]] == [width, height],
            "actual painted screenshot is not the requested view/size")
    require(painted["elapsed_ms"] >= DURATION_MS and 0 < painted["rendered_image"] <= runtime["rendered_images"]
            and painted == view["before_shutdown"] == view["last_painted"], "capture is not the final replay-painted frame")
    copied = painted["inspection"]
    require(copied["snapshot_available"] is True and copied["snapshot_read_succeeded"] is True
            and copied["snapshot_state"] == "current" and copied["controls_pending"] is False
            and copied["frame_clock"] > 0 and copied["publication_revision"] > 0,
            "captured frame lacks a current acknowledged copied state")
    return {"passed": True, "actual_painted_view": painted, "callbacks": audio["callback_count"],
            "rendered_frames": audio["rendered_frames"], "ui_events": event_count,
            "held_manual_notes": endpoint["manual_notes"], "held_pedal_ids": endpoint["pedal_ids"],
            "live_edit": {"target": "Upper B 16-foot retained drawbar", "before": 7, "after": 8},
            "complete_control_state_checked": True, "input_state_file_unchanged": True,
            "joined_shutdown_clear": True, "midi_source": midi["source"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--build-root", type=Path, required=True)
    parser.add_argument("--source-qualification", type=Path, required=True,
                        help="author report with binary_sha256 and source_sha256; every listed digest must match")
    parser.add_argument("--expected-exe-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True, help="new directory; an existing empty directory is refused")
    parser.add_argument("--dummy-sdl", action="store_true", required=True,
                        help="acknowledge dummy audio/video and software rendering; no physical device claim")
    parser.add_argument("--timeout-seconds", type=float, default=12.0)
    args = parser.parse_args()
    require(math.isfinite(args.timeout_seconds) and 4 <= args.timeout_seconds <= 60, "timeout must be finite, 4..60 seconds")
    require(not os.path.lexists(args.output), "output already exists; refusing to overwrite any gallery")
    exe, source, build, report_path = (p.resolve(strict=True) for p in
        (args.exe, args.source_root, args.build_root, args.source_qualification))
    require(source.is_dir() and build.is_dir() and os.access(exe, os.X_OK), "invalid source/build/executable input")
    executable_before = identity(exe)
    require(executable_before["sha256"] == args.expected_exe_sha256, "executable does not match expected SHA-256")
    qualified = qualification(report_path, source, executable_before)
    source_before = inventory(production_paths(source), source)
    build_before = inventory(build_paths(build), build)
    config_before = configuration(build)
    tool_path = Path(__file__).resolve()
    tool_before = identity(tool_path)
    try:
        from PIL import Image, __version__ as pillow_version
    except ImportError as error:
        raise ValueError("Pillow is an optional capture-authoring dependency; install it in your authoring Python environment") from error

    output = args.output.absolute()
    output.mkdir()  # Atomic new-directory admission. Never mutate a historical gallery.
    for name in ("inputs", "images", "diagnostics", "runs"):
        (output / name).mkdir()
    record = {
        "schema_version": 1, "capture_contract": "standalone-interface-capture-v1", "status": "incomplete",
        "started_at_utc": datetime.now(timezone.utc).isoformat(), "command": [sys.executable, *sys.argv],
        "output_directory_at_capture": str(output), "platform": platform.platform(),
        "python": platform.python_version(), "pillow": pillow_version,
        "qualification": "Actual native screenshots with SDL dummy audio/video and software renderer; no physical device, deadline, accessibility, measured instrument or literal 1:1 reference qualification.",
        "visual_review": "Not performed by this utility. Review retained PNGs separately against the source concept.",
        "tool": {"path": str(tool_path), "before": tool_before},
        "executable": {"path": str(exe), "before": executable_before},
        "source": {"root": str(source), "git_before": git_identity(source), "files": source_before,
                   "inventory_sha256_before": inventory_digest(source_before), "checked_author_report": qualified,
                   "boundary": "Observed production overlay, including untracked files; HEAD alone does not identify this UI. The author report pins its listed sources only. Extra production hashes are observed capture inputs, not an independent build attestation. Test, install-rule and unrelated documentation edits are excluded."},
        "build": {"root": str(build), "files": build_before, "inventory_sha256_before": inventory_digest(build_before),
                  "selected_configuration_before": config_before,
                  "boundary": "Generated embedded headers, nominal profile and selected native/core static libraries. Selected CMake values are checked; this is not a hermetic compiler/dependency or rebuild attestation."},
        "cases": [],
    }
    error = None
    try:
        (output / "inputs/source-qualification.json").write_bytes(report_path.read_bytes())
        require(identity(output / "inputs/source-qualification.json")["sha256"] == qualified["sha256"],
                "qualification report changed while being copied")
        state = output / "inputs/controls.b3controls"
        state.write_text(STATE, encoding="ascii")
        plans = {}
        for workspace, presentation in sorted(set((c[3], c[4]) for c in CASES)):
            script, events = replay(workspace, presentation)
            path = output / "inputs" / f"{workspace}-{presentation}.b3uireplay"
            path.write_text(script, encoding="ascii")
            plans[(workspace, presentation)] = (path, events)
        inputs_before = inventory(list((output / "inputs").iterdir()), output)
        record["inputs"] = {"before": inputs_before}
        environment = {"PATH": os.defpath, "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8",
                       "SDL_AUDIODRIVER": "dummy", "SDL_VIDEODRIVER": "dummy", "SDL_RENDER_DRIVER": "software"}
        for key in ("SystemRoot", "WINDIR"):
            if key in os.environ:
                environment[key] = os.environ[key]
        record["environment"] = environment
        for name, width, height, workspace, presentation in CASES:
            # Detect drift before launching another process as well as after the
            # complete matrix. A change invalidates the whole gallery.
            require(identity(exe) == executable_before and inventory(production_paths(source), source) == source_before,
                    "production source/executable changed during capture; gallery invalid")
            working = output / "runs" / name
            working.mkdir()
            script, events = plans[(workspace, presentation)]
            diagnostics = output / "diagnostics" / f"{name}.json"
            bmp, png = output / "images" / f"{name}.bmp", output / "images" / f"{name}.png"
            command = [str(exe), "--state", str(state), "--input-script", str(script), "--workspace", "play",
                       "--width", str(width), "--height", str(height), "--sample-rate", "48000", "--buffer-frames", "512",
                       "--screenshot", str(bmp), "--diagnostics", str(diagnostics)]
            case = {"name": name, "width": width, "height": height, "workspace": workspace,
                    "presentation": presentation, "cwd": str(working), "command": command,
                    "timeout_seconds": args.timeout_seconds, "status": "incomplete"}
            record["cases"].append(case)
            started = time.monotonic()
            try:
                process = subprocess.run(command, cwd=working, env=environment, stdin=subprocess.DEVNULL,
                                         capture_output=True, timeout=args.timeout_seconds, check=False)
            except subprocess.TimeoutExpired as timeout:
                (output / "diagnostics" / f"{name}.stdout.txt").write_bytes(timeout.stdout or b"")
                (output / "diagnostics" / f"{name}.stderr.txt").write_bytes(timeout.stderr or b"")
                case["timed_out"] = True
                raise
            case["elapsed_seconds"] = time.monotonic() - started
            case["exit_code"] = process.returncode
            (output / "diagnostics" / f"{name}.stdout.txt").write_bytes(process.stdout)
            (output / "diagnostics" / f"{name}.stderr.txt").write_bytes(process.stderr)
            require(process.returncode == 0, f"{name}: native process exited {process.returncode}")
            require(not process.stdout and not process.stderr, f"{name}: unexpected native output; logs retained")
            require(inventory(list((output / "inputs").iterdir()), output) == inputs_before,
                    f"{name}: input/state bytes changed")
            case["validation"] = validate(read_json(diagnostics), width, height, workspace, presentation, events)
            case["diagnostics"] = {"path": str(diagnostics.relative_to(output)), **identity(diagnostics)}
            bmp_identity = identity(bmp)
            with Image.open(bmp) as native:
                native.load()
                mode, size, pixels = native.mode, native.size, native.tobytes()
                require(size == (width, height), f"{name}: decoded BMP dimensions differ")
                native.save(png, format="PNG", optimize=True, compress_level=9)
            with Image.open(png) as encoded:
                encoded.load()
                require((encoded.mode, encoded.size, encoded.tobytes()) == (mode, size, pixels),
                        f"{name}: PNG conversion changed decoded pixels")
            case["image"] = {"path": str(png.relative_to(output)), "native_bmp": bmp_identity,
                             "png": identity(png), "decoded_mode": mode, "width": width, "height": height,
                             "decoded_sha256": hashlib.sha256(pixels).hexdigest(),
                             "lossless_bmp_to_png": True, "native_bmp_removed_after_verification": True}
            bmp.unlink()  # Only this fresh run's own losslessly preserved BMP.
            working.rmdir()  # Refuse removal if the app unexpectedly left any file.
            case["status"] = "passed"
        record["status"] = "passed"
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as caught:
        error = str(caught)
        record["status"] = "failed"
        record["failure"] = error
    finally:
        try:
            executable_after = identity(exe)
            source_after = inventory(production_paths(source), source)
            build_after = inventory(build_paths(build), build)
            config_after = configuration(build)
            record["executable"]["after"] = executable_after
            record["tool"]["after"] = identity(tool_path)
            record["source"]["git_after"] = git_identity(source)
            record["source"]["inventory_sha256_after"] = inventory_digest(source_after)
            record["source"]["changed_paths"] = sorted(k for k in source_before.keys() | source_after.keys()
                                                       if source_before.get(k) != source_after.get(k))
            record["build"]["inventory_sha256_after"] = inventory_digest(build_after)
            record["build"]["selected_configuration_after"] = config_after
            record["build"]["changed_paths"] = sorted(k for k in build_before.keys() | build_after.keys()
                                                      if build_before.get(k) != build_after.get(k))
            record["inputs"]["after"] = inventory(list((output / "inputs").iterdir()), output)
            unchanged = (executable_before == executable_after and source_before == source_after
                         and build_before == build_after and config_before == config_after
                         and record["tool"]["after"] == tool_before
                         and record["inputs"]["before"] == record["inputs"]["after"]
                         and identity(report_path)["sha256"] == qualified["sha256"])
            record["all_recorded_inputs_unchanged"] = unchanged
            if not unchanged:
                record["status"] = "failed"
                record["identity_failure"] = "Recorded executable/source/build/configuration/input/tool/report changed during capture; entire gallery invalid."
        except (OSError, ValueError, KeyError, subprocess.SubprocessError) as caught:
            record["status"] = "failed"
            record["identity_failure"] = str(caught)
        record["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        write_json(output / "provenance.json", record)
        files = inventory([p for p in output.rglob("*") if p.is_file()], output)
        write_json(output / "manifest.json", {"schema_version": 1, "status": record["status"], "files": files,
                  "total_bytes_excluding_manifest": sum(v["bytes"] for v in files.values()),
                  "scope": "Exact capture payload and provenance. Excludes this manifest and any subsequently authored README/review. Failed galleries are retained as failures, never promoted by a later source change."})
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
        print(f"capture_standalone_interface: {error}", file=sys.stderr)
        raise SystemExit(2)
