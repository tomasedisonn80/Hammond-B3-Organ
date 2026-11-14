#!/usr/bin/env python3
"""Capture four bounded native views with explicit dummy SDL qualification.

Python 3.10+ and Pillow are authoring dependencies only. This runs a supplied
executable; it neither builds source nor substitutes artwork for app pixels.
The output must be a new directory. Every input, state and output leaf is private
to that directory, and no default application preferences are used.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time


STATE = """B3CONTROLS3
expression 1
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
PLAYER = """B3UIREPLAY1
duration_ms 1400
# UI-owned Upper C4 and Lower E4 remain held at the acknowledged endpoint.
100 key_down F1 none 0
110 key_up F1 none
200 key_down A none 0
450 key_down F2 none 0
460 key_up F2 none
650 key_down D none 0
900 key_down F1 none 0
910 key_up F1 none
"""
MODAL_UI = """B3UIREPLAY1
duration_ms 1400
# Open the real modal, focus Apply, and activate it in synthetic mode.
300 key_down M ctrl 0
310 key_up M ctrl
400 key_down Tab none 0
410 key_up Tab none
450 key_down Tab none 0
460 key_up Tab none
500 key_down Tab none 0
510 key_up Tab none
550 key_down Tab none 0
560 key_up Tab none
600 key_down Tab none 0
610 key_up Tab none
700 key_down Return none 0
710 key_up Return none
"""
MODAL_MIDI = """B3MIDIREPLAY1
duration_ms 1400
# Explicit synthetic input bypasses native MIDI opening and enumeration.
# MIDI-owned holds survive the UI focus release when the modal opens.
0 connect
100 bytes 90 3C 64
100 bytes 91 40 64
"""
CASES = (("reference-1672x941", 1672, 941, False),
         ("default-1280x900", 1280, 900, False),
         ("minimum-960x700", 960, 700, False),
         ("midi-synthetic-960x700", 960, 700, True))
CONTROLS = {
    "manual_drawbars": [[[0] * 9, [8, 8, 8, 0, 0, 0, 0, 0, 0]],
                        [[0] * 9, [0, 0, 8, 0, 0, 0, 0, 0, 0]]],
    "selected_banks": [1, 1], "route_enabled": [True, True], "expression": 1,
    "pedal_drawbars": [8, 0],
    "percussion": {"enabled": False, "harmonic": 0, "volume": 0, "decay": 0},
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def identity(path: Path) -> dict:
    if path.is_symlink():
        target = os.readlink(path)
        raw = os.fsencode(target)
        return {"kind": "symlink", "target": target, "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest()}
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return {"bytes": path.stat().st_size, "sha256": digest.hexdigest()}


def inventory(paths: list[Path], root: Path) -> dict:
    return {str(path.relative_to(root)): identity(path) for path in sorted(set(paths))}


def files_under(root: Path, names: tuple[str, ...]) -> list[Path]:
    result = []
    for name in names:
        path = root / name
        if path.is_file():
            result.append(path)
        elif path.is_dir():
            result.extend(p for p in path.rglob("*") if p.is_file()
                          and ".git" not in p.parts and "__pycache__" not in p.parts)
    return result


def bounded(command: list[str], cwd: Path, timeout: float = 10,
            environment: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(command, cwd=cwd, env=environment, stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          timeout=timeout, check=False)


def json_file(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def unique_members(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON member: {key}")
        result[key] = value
    return result


def read_json(path: Path) -> dict:
    def bad_number(value: str) -> None:
        raise ValueError(f"invalid JSON numeric token: {value}")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_members,
                      parse_constant=bad_number)


def validate(data: dict, width: int, height: int, modal: bool) -> dict:
    require(data["schema_version"] == 2, "expected native diagnostics schema 2")
    require(data["application"] == "hammond_standalone", "wrong application")
    require(data["errors"] == {"count": 0, "last": ""}, "application errors")
    require(data["controls"] == CONTROLS, "complete control state changed")
    runtime, audio, session, midi = (data[key] for key in ("runtime", "audio", "session", "midi"))
    require(runtime["video_driver"] == "dummy" and audio["driver"] == "dummy"
            and runtime["renderer"] == "software", "dummy/software qualification did not hold")
    require([runtime[key] for key in ("window_width", "window_height", "drawable_width", "drawable_height")]
            == [width, height, width, height], "actual logical/drawable dimensions differ")
    require(runtime["screenshot_written"] is True and runtime["screenshot_while_held"] is True,
            "missing held-state native screenshot")
    require(audio["callback_count"] > 0 and audio["rendered_frames"] > 0
            and runtime["rendered_images"] > 0, "no actual callback or rendering progress")
    require(audio["sample_rate"] == 48000 and audio["buffer_frames"] == 512
            and audio["channels"] == 2 and audio["sample_format"] == audio["native_float32_format"],
            "unexpected obtained audio configuration")
    for key in ("render_failures", "format_failures", "overrange_failures", "overrange_samples",
                "nonfinite_failures", "nonfinite_samples"):
        require(audio[key] == 0, f"audio.{key} is nonzero")
    for key in ("recovery_count", "queue_overflows", "rejected_commands", "fault_flags"):
        require(session[key] == 0, f"session.{key} is nonzero")
    require(session["held_after_shutdown"] is False and session["running_after_shutdown"] is False,
            "joined shutdown did not clear the running/held state")
    require(midi["generation"] == 0 and midi["requested_port"] == "" and midi["port_name"] == ""
            and midi["state_before_shutdown"] == midi["state_after_shutdown"] == "closed"
            and all(value == 0 for value in midi["device"].values()), "native MIDI device was used")
    require(midi["active_after_shutdown"] is False and midi["quiescent_after_shutdown"] is True
            and midi["diagnostics_stable_after_shutdown"] is True and midi["release_pending"] is False,
            "MIDI shutdown was not quiescent")
    for key in ("shutdown_failed", "startup_failed", "open_failures", "submit_failures", "fault_retirements"):
        require(not midi[key], f"midi.{key} indicates failure")
    require(midi["drain_budget"] == 32 and 0 <= midi["maximum_drained_per_turn"] <= 32
            and midi["inbox"]["capacity"] == 256 and midi["inbox"]["pending_packets"] == 0,
            "MIDI capacity/drain boundary differs")
    require(midi["arrival_time_is_sample_time"] is False, "arrival time mislabelled as sample time")
    replay = data["replay"]
    for record in ([replay, data["midi_replay"]] if modal else [replay]):
        for key in ("completed", "delivered", "passed", "final_acknowledged"):
            require(record[key] is True, f"replay.{key} is false")
        require(record["duration_ms"] == 1400 and record["accepted_note_on_commands"] == 2
                and record["accepted_note_off_commands"] == 0 and record["device_starts"] == 1,
                "unexpected replay duration or musical command counts")
        require(record["observations_truncated"] is False
                and record["observation_capacity"] == (8704 if modal else 512),
                "observation capacity/truncation differs")
        endpoint = record["before_shutdown"]
        require(endpoint["manual_notes"] == [[60], [64]] and endpoint["pedal_ids"] == []
                and endpoint["controls"] == CONTROLS, "expected Upper C4 and Lower E4 endpoint absent")
        require(endpoint["resolved_sequence"] >= record["last_submitted_sequence"]
                and endpoint["last_applied_sequence"] >= record["last_submitted_sequence"],
                "final replay sequence was not applied")
    require(replay["scheduled_events"] == replay["pushed_events"] == (14 if modal else 8),
            "UI script delivery count differs")
    if modal:
        record = data["midi_replay"]
        require(midi["source"] == record["source"] == "synthetic-replay", "synthetic source label absent")
        require(record["scheduled_events"] == record["delivered_events"] == 3
                and record["scheduled_packets"] == record["offered_packets"] == record["accepted_packets"] == 2
                and record["connect_events"] == record["connections_started"] == 1,
                "synthetic replay delivery counts differ")
        for key in ("dropped_packets", "ignored_while_closed", "rejected_packets", "discarded_queued_packets",
                    "disconnect_events", "intentional_backend_faults", "intentional_overflow_faults",
                    "faults_while_closed", "failure_count", "cancelled_connects", "budget_exhaustions"):
            require(record[key] == 0, f"midi_replay.{key} is nonzero")
        require(record["event_budget"] == 512 and 1 <= record["maximum_events_per_turn"] <= 512
                and record["arrival_time_is_sample_time"] is False, "MIDI event budget/timing differs")
        require(record["connected_before_shutdown"] is True and record["connected_after_shutdown"] is False
                and record["faulted_before_shutdown"] is False and record["pending_connect_before_shutdown"] is False
                and record["release_pending_before_shutdown"] is False, "synthetic lifecycle endpoint differs")
    else:
        require(midi["source"] == "none" and "midi_replay" not in data
                and midi["active_before_shutdown"] is False, "player unexpectedly used MIDI")
    return {"passed": True, "callbacks": audio["callback_count"], "frames": audio["rendered_frames"],
            "painted_images": runtime["rendered_images"], "ui_events": replay["pushed_events"],
            "final_sequence": replay["last_submitted_sequence"], "held_manual_notes": [[60], [64]],
            "note_on_commands": 2, "note_off_commands": 0, "joined_shutdown_clear": True,
            "midi_source": midi["source"], "maximum_drained_per_turn": midi["maximum_drained_per_turn"]}


def source_paths(root: Path) -> list[Path]:
    return files_under(root, ("apps/standalone", "include", "src", "assets/standalone", "cmake", "data", "tools",
                              "CMakeLists.txt", "THIRD_PARTY_NOTICES.md", "docs/design/atlas-reference.json",
                              "docs/design/atlas-cover-reference.jpg"))


def build_paths(root: Path) -> list[Path]:
    paths = files_under(root, ("CMakeCache.txt", "compile_commands.json", "generated",
                              "apps/standalone/generated", "apps/standalone/hammond_rtmidi-prepared"))
    for pattern in ("**/link.txt", "**/flags.make", "**/*.a", "**/SDL_config.h"):
        paths.extend(path for path in root.glob(pattern) if path.is_file())
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", required=True, type=Path, help="explicit already-built native executable")
    parser.add_argument("--source-root", required=True, type=Path, help="matching frozen source directory")
    parser.add_argument("--build-root", required=True, type=Path, help="matching CMake build/configuration directory")
    parser.add_argument("--output", required=True, type=Path, help="new directory; even an existing empty directory is refused")
    parser.add_argument("--dummy-sdl", action="store_true", required=True,
                        help="acknowledge dummy audio/video and software renderer; no physical-device qualification")
    parser.add_argument("--expected-exe-sha256", help="optional exact expected executable identity")
    parser.add_argument("--source-context", type=Path, help="optional existing provenance context, copied as data only")
    parser.add_argument("--timeout-seconds", default=12.0, type=float, help="finite per-app guard, 4 through 60 (default 12)")
    args = parser.parse_args()
    require(math.isfinite(args.timeout_seconds) and 4 <= args.timeout_seconds <= 60, "timeout must be finite, 4 through 60")
    require(not os.path.lexists(args.output), "output directory already exists; refusing to overwrite any files")
    exe, source, build = (path.resolve(strict=True) for path in (args.exe, args.source_root, args.build_root))
    require(exe.is_file() and os.access(exe, os.X_OK), "executable must be an executable regular file")
    require(source.is_dir() and build.is_dir(), "source/build roots must be directories")
    require((source / "apps/standalone/main.cpp").is_file(), "source root lacks native main.cpp")
    require((build / "CMakeCache.txt").is_file() and (build / "compile_commands.json").is_file(),
            "build root must retain CMakeCache.txt and compile_commands.json")
    executable_before = identity(exe)
    if args.expected_exe_sha256:
        require(executable_before["sha256"] == args.expected_exe_sha256, "executable does not match expected SHA-256")
    from PIL import Image, __version__ as pillow_version

    output = args.output.absolute()
    output.mkdir()  # Atomic fresh-directory admission; no existing tree is changed.
    for name in ("inputs", "state", "runs", "images", "diagnostics", "logs", "metadata"):
        (output / name).mkdir()
    record = {"schema_version": 1, "purpose": "actual bounded initial/reference native UI gallery",
              "started_at_utc": datetime.now(timezone.utc).isoformat(), "status": "incomplete",
              "qualification": "Dummy SDL audio/video, software renderer, synthetic modal MIDI; not a physical-device, timing, accessibility, or pixel-identical photograph pass.",
              "visual_review": "Not performed by this utility; inspect the retained PNGs separately.",
              "command": [sys.executable, *sys.argv], "platform": platform.platform(),
              "python": platform.python_version(), "pillow": pillow_version,
              "tool": {"path": str(Path(__file__).resolve()), **identity(Path(__file__))},
              "executable": {"path": str(exe), "before": executable_before}, "cases": []}
    error = None
    source_before = build_before = dependencies_before = None
    dependency_paths = []
    try:
        source_before = inventory(source_paths(source), source)
        build_before = inventory(build_paths(build), build)
        record["source"] = {"root": str(source), "before": source_before,
                            "boundary": "Exact current files, including uncommitted files; no commit alone or signed source-to-binary attestation is claimed."}
        record["build"] = {"root": str(build), "before": build_before}
        for name in ("CMakeCache.txt", "compile_commands.json"):
            shutil.copyfile(build / name, output / "metadata" / name)
        if args.source_context:
            context = args.source_context.resolve(strict=True)
            shutil.copyfile(context, output / "metadata" / "source-context.json")
            record["source"]["context"] = {"path": str(context), **identity(context),
                                            "meaning": "Copied context only; actual file hashes are independently recorded above."}
        cache = {}
        for line in (build / "CMakeCache.txt").read_text(encoding="utf-8").splitlines():
            if line and not line.startswith(("//", "#")) and ":" in line and "=" in line:
                key_type, value = line.split("=", 1)
                cache[key_type.split(":", 1)[0]] = value
        dependency_roots = {}
        for key in ("HAMMOND_SDL2_ROOT", "HAMMOND_RTMIDI_ROOT"):
            if cache.get(key):
                root = Path(cache[key]).resolve(strict=True)
                probe = bounded(["git", "-C", str(root), "ls-files", "-z"], root)
                require(probe.returncode == 0, f"cannot inventory dependency {key}")
                paths = [root / name.decode("utf-8") for name in probe.stdout.split(b"\0") if name]
                dependency_paths.extend(paths)
                revision = bounded(["git", "-C", str(root), "rev-parse", "HEAD"], root)
                dependency_roots[key] = {"path": str(root), "head": revision.stdout.decode().strip(),
                                         "files": inventory(paths, root)}
        for key in ("ALSA_LIBRARY", "CMAKE_CXX_COMPILER"):
            if cache.get(key):
                path = Path(cache[key]).resolve(strict=True)
                dependency_paths.append(path)
        dependencies_before = {str(path): identity(path) for path in sorted(set(dependency_paths))}
        record["dependencies"] = {"roots": dependency_roots, "before": dependencies_before,
                                  "scope": "Tracked SDL/RtMidi source, prepared build inputs, selected compiler and configured ALSA library. System libraries/toolchain are not a hermetic build attestation."}
        record["build"]["selected_configuration"] = {key: cache[key] for key in
            ("CMAKE_BUILD_TYPE", "CMAKE_CXX_COMPILER", "CMAKE_CXX_FLAGS_RELEASE", "CMAKE_MAKE_PROGRAM",
             "HAMMOND_BUILD_STANDALONE", "HAMMOND_ENABLE_MIDI", "SDL_ALSA", "ALSA_LIBRARY", "ALSA_INCLUDE_DIR") if key in cache}
        for name, content in (("held-manuals.b3ui", PLAYER), ("midi-modal.b3ui", MODAL_UI), ("midi-modal.b3midi", MODAL_MIDI)):
            (output / "inputs" / name).write_text(content, encoding="ascii")
        environment = {"PATH": os.defpath, "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8",
                       "SDL_AUDIODRIVER": "dummy", "SDL_VIDEODRIVER": "dummy", "SDL_RENDER_DRIVER": "software"}
        for key in ("SystemRoot", "WINDIR"):
            if key in os.environ:
                environment[key] = os.environ[key]
        record["environment"] = environment
        for name, width, height, modal in CASES:
            working = output / "runs" / name
            working.mkdir()
            state = output / "state" / (name + ".b3controls")
            state.write_text(STATE, encoding="ascii")
            ui = output / "inputs" / ("midi-modal.b3ui" if modal else "held-manuals.b3ui")
            midi = output / "inputs" / "midi-modal.b3midi"
            diagnostics = output / "diagnostics" / (name + ".json")
            bmp = output / "images" / (name + ".bmp")
            png = output / "images" / (name + ".png")
            inputs = [state, ui] + ([midi] if modal else [])
            input_before = inventory(inputs, output)
            command = [str(exe), "--state", str(state), "--width", str(width), "--height", str(height),
                       "--sample-rate", "48000", "--buffer-frames", "512", "--input-script", str(ui),
                       "--screenshot", str(bmp), "--diagnostics", str(diagnostics)]
            if modal:
                command += ["--midi-script", str(midi)]
            case = {"name": name, "width": width, "height": height, "synthetic_midi_modal": modal,
                    "cwd": str(working), "command": command, "timeout_seconds": args.timeout_seconds,
                    "inputs_before": input_before, "status": "incomplete"}
            record["cases"].append(case)
            started = time.monotonic()
            try:
                process = bounded(command, working, args.timeout_seconds, environment)
            except subprocess.TimeoutExpired as timeout:
                (output / "logs" / (name + ".stdout.txt")).write_bytes(timeout.stdout or b"")
                (output / "logs" / (name + ".stderr.txt")).write_bytes(timeout.stderr or b"")
                case["timed_out"] = True
                raise
            case["elapsed_seconds"] = time.monotonic() - started
            case["exit_code"] = process.returncode
            (output / "logs" / (name + ".stdout.txt")).write_bytes(process.stdout)
            (output / "logs" / (name + ".stderr.txt")).write_bytes(process.stderr)
            case["inputs_after"] = inventory(inputs, output)
            require(case["inputs_after"] == input_before, f"{name}: input/state bytes changed")
            require(process.returncode == 0, f"{name}: native process failed with exit {process.returncode}")
            require(not process.stdout and not process.stderr, f"{name}: unexpected process output; retained in logs")
            case["validation"] = validate(read_json(diagnostics), width, height, modal)
            case["diagnostics"] = identity(diagnostics)
            raw = bmp.read_bytes()
            with Image.open(bmp) as native:
                native.load()
                mode, size, pixels = native.mode, native.size, native.tobytes()
                rgb = native.convert("RGB").tobytes()
                require(size == (width, height), f"{name}: BMP dimensions differ")
                native.save(png, format="PNG")
            with Image.open(png) as encoded:
                encoded.load()
                require((encoded.mode, encoded.size, encoded.tobytes()) == (mode, size, pixels)
                        and encoded.convert("RGB").tobytes() == rgb, "BMP-to-PNG conversion changed decoded pixels")
            archive = bmp.with_suffix(".bmp.gz")
            archive.write_bytes(gzip.compress(raw, mtime=0))
            require(gzip.decompress(archive.read_bytes()) == raw, "raw BMP archive did not round-trip")
            case["image"] = {"bmp": identity(bmp), "bmp_gzip": identity(archive), "png": identity(png),
                             "decoded_mode": mode, "width": width, "height": height,
                             "decoded_sha256": hashlib.sha256(pixels).hexdigest(),
                             "decoded_rgb_sha256": hashlib.sha256(rgb).hexdigest(),
                             "conversion_preserved_every_decoded_pixel": True,
                             "native_bmp_archived_without_byte_changes": True}
            bmp.unlink()  # Only this tool's newly created BMP; the exact bytes remain in .bmp.gz.
            case["status"] = "passed"
        record["status"] = "passed"
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as caught:
        error = str(caught)
        record["status"] = "failed"
        record["failure"] = error
    finally:
        try:
            record["executable"]["after"] = identity(exe)
            unchanged = record["executable"]["after"] == executable_before
            if source_before is not None:
                record["source"]["after"] = inventory(source_paths(source), source)
                unchanged = unchanged and record["source"]["after"] == source_before
            if build_before is not None:
                record["build"]["after"] = inventory(build_paths(build), build)
                unchanged = unchanged and record["build"]["after"] == build_before
            if dependencies_before is not None:
                record["dependencies"]["after"] = {str(path): identity(path) for path in sorted(set(dependency_paths))}
                unchanged = unchanged and record["dependencies"]["after"] == dependencies_before
            record["all_recorded_inputs_unchanged"] = unchanged
            if not unchanged:
                record["status"] = "failed"
                record["identity_failure"] = "Executable, source, build or dependency identities changed during capture"
        except OSError as caught:
            record["status"] = "failed"
            record["identity_failure"] = str(caught)
        record["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        json_file(output / "provenance.json", record)
        json_file(output / "manifest.json", {"schema_version": 1, "files": inventory(
            [path for path in output.rglob("*") if path.is_file()], output),
            "scope": "Exact capture files; this manifest excludes itself and any subsequently authored review."})
    print(json.dumps({"status": record["status"], "output": str(output), "captures": len(record["cases"]),
                      "failure": error, "identity_failure": record.get("identity_failure")}, sort_keys=True))
    return 0 if record["status"] == "passed" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"capture_standalone_reference: {error}", file=sys.stderr)
        raise SystemExit(2)
