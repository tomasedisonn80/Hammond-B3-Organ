#!/usr/bin/env python3
"""A29's bounded, real MIDI-off package qualification. No physical devices."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time


METADATA = {
    "STANDALONE_INSTALL.md": "docs/STANDALONE_INSTALL.md",
    "STANDALONE_APP.md": "docs/STANDALONE_APP.md",
    "STANDALONE_MODEL.md": "docs/STANDALONE_MODEL.md",
    "MIDI_UI_RUNBOOK.md": "docs/MIDI_UI_RUNBOOK.md",
    "PRESET_RUNBOOK.md": "docs/PRESET_RUNBOOK.md",
    "INTERFACE_RUNBOOK.md": "docs/INTERFACE_RUNBOOK.md",
    "THIRD_PARTY_NOTICES.md": "THIRD_PARTY_NOTICES.md",
    "LICENSE-DejaVu.txt": "assets/standalone/fonts/LICENSE-DejaVu.txt",
    "sdl2-lock.json": "data/dependencies/sdl2-lock.json",
    "font-source-manifest.json": "assets/standalone/fonts/source-manifest.json",
    "reference-source-manifest.json": "assets/standalone/reference/manifest.json",
    "atlas-reference.json": "docs/design/atlas-reference.json",
}
STATE = ("\tB3CONTROLS4\n"
         "registration_catalog atlas-chapel-nominal-v1 sha256 c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf\n"
         "expression +3.75e-1\n"
         "percussion enabled 1 harmonic third volume soft decay fast\n"
         "pedal drawbars 2 7\n"
         "manual upper selected A fixed_registration F# route_enabled 1\n"
         "bank A 0 1 2 3 4 5 6 7 8\n"
         "bank B 8 7 6 5 4 3 2 1 0\n"
         "manual lower selected B fixed_registration G# route_enabled 1\n"
         "bank A 1 3 5 7 0 2 4 6 8\n"
         "bank B 8 6 4 2 0 7 5 3 1\n"
         "end\n \t\n").replace("\n", "\r\n").encode("ascii")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identity(path: Path) -> dict:
    return {"bytes": path.stat().st_size, "sha256": sha(path)}


def inventory(root: Path) -> dict:
    assert all(not path.is_symlink() for path in root.rglob("*"))
    return {str(path.relative_to(root)): identity(path)
            for path in sorted(root.rglob("*")) if path.is_file()}


def tap(at: int, key: str, modifier: str = "none") -> list:
    return [(at, f"key_down {key} {modifier} 0"), (at + 10, f"key_up {key} {modifier}")]


def click(at: int, x: int, y: int) -> list:
    return [(at, f"mouse_down {x} {y}"), (at + 10, f"mouse_up {x} {y}")]


def collapsed(values: list) -> list:
    return [item for index, item in enumerate(values) if index == 0 or item != values[index - 1]]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("source", "build", "cmake", "sdl", "work", "reports"):
        parser.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args()
    args.work.mkdir(parents=True, exist_ok=False)
    unrelated = args.work / "unrelated cwd"
    unrelated.mkdir()
    prefix = args.work / "original organ Ω"
    moved = args.work / "relocated organ Ω"
    output = args.reports / "a29-relocation.json"
    record = {"schema": "a29-midi-off-relocation-v1", "status": "running",
              "source": str(args.source), "build": str(args.build),
              "work": str(args.work), "cwd": str(unrelated), "commands": [],
              "environment": {"SDL_AUDIODRIVER": "dummy", "SDL_VIDEODRIVER": "dummy"},
              "physical_devices_used": False, "source_or_sdk_renamed": False,
              "limits": ["Linux local Release with SDL dummy audio/video only",
                         "Source checkout and shared SDK remain present; only the installed prefix moves",
                         "No native display, physical audio/MIDI, callback deadline, or release-rights claim"]}
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith("HAMMOND_")}
    env.pop("DESTDIR", None)
    env.pop("CMAKE_INSTALL_MODE", None)
    env.update(record["environment"])

    def run(name: str, command: list, expected: int = 0, no_sdl: bool = False) -> subprocess.CompletedProcess:
        current_env = dict(env)
        if no_sdl:
            current_env.update(SDL_AUDIODRIVER="a29_no_such_driver", SDL_VIDEODRIVER="a29_no_such_driver")
        started = time.monotonic()
        process = subprocess.run(list(map(str, command)), cwd=unrelated, env=current_env,
                                 stdin=subprocess.DEVNULL, capture_output=True, text=True,
                                 encoding="utf-8", errors="replace", timeout=20, check=False)
        result = {"name": name, "command": list(map(str, command)), "returncode": process.returncode,
                  "expected_returncode": expected, "elapsed_seconds": round(time.monotonic() - started, 4),
                  "stdout": process.stdout, "stderr": process.stderr,
                  "driver_mode": "deliberately invalid" if no_sdl else "dummy"}
        record["commands"].append(result)
        print(f"{name}: exit {process.returncode}, {result['elapsed_seconds']} s", flush=True)
        assert process.returncode == expected, result
        return process

    def native(name: str, arguments: list, *, expected: int = 0, absent_state: bool = False,
               events: list | None = None, duration: int = 1600) -> tuple[dict, Path, subprocess.CompletedProcess]:
        state = unrelated / (name + " controls 音.b3controls")
        if not absent_state:
            state.write_bytes(STATE)
        report = args.reports / ("a29-" + name + "-diagnostics.json")
        command = [exe, "--state", state, "--diagnostics", report,
                   "--width", "960", "--height", "700", *arguments]
        if events is not None:
            script = args.reports / ("a29-" + name + ".b3ui")
            script.write_text(f"B3UIREPLAY1\nduration_ms {duration}\n" + "".join(
                f"{at} {event}\n" for at, event in events), encoding="ascii")
            command += ["--input-script", script]
        result = run(name, command, expected)
        data = json.loads(report.read_text(encoding="utf-8"))
        assert data["schema_version"] == 3
        assert data["application"] == "hammond_standalone"
        assert data["profile"] == {"id": "nominal-unmeasured-v1", "authoring_sha256":
                                    "49791eac8d0b556b0abd2018b8cabc6f240161edab8a9fa0ef97905f2badda83"}
        assert data["runtime"]["video_driver"] == "dummy"
        assert data["runtime"]["renderer"] == "software"
        assert data["runtime"]["sdl_version"] == "2.32.10"
        assert data["runtime"]["rendered_images"] > 0
        assert data["audio"]["driver"] == "dummy"
        assert data["audio"]["open_before_shutdown"] and data["audio"]["running_before_shutdown"]
        assert data["audio"]["callback_count"] > 0 and data["audio"]["rendered_frames"] > 0
        assert all(data["audio"][key] == 0 for key in
                   ("render_failures", "format_failures", "nonfinite_failures", "overrange_failures"))
        assert data["session"]["snapshot_available"] and data["session"]["prepared"]
        assert data["session"]["fault_flags"] == 0
        assert not data["session"]["running_after_shutdown"] and not data["session"]["held_after_shutdown"]
        midi = data["midi"]
        assert midi["backend_available"] is False and midi["backend"] == "unavailable"
        assert midi["state_after_shutdown"] == "unavailable"
        assert midi["quiescent_after_shutdown"] and midi["diagnostics_stable_after_shutdown"]
        assert not midi["active_after_shutdown"] and not midi["shutdown_failed"]
        assert not midi["discovery"]["pending_after_shutdown"]
        assert midi["device"]["callback_messages"] == midi["open_failures"] == 0
        assert data["state_path"] == str(state)
        assert not state.exists() if absent_state else state.read_bytes() == STATE
        if expected == 0:
            assert data["errors"] == {"count": 0, "last": ""}
            assert result.stderr == ""
            if "--smoke-ms" in arguments:
                summary = re.fullmatch(r"Native SDL smoke passed: callbacks=(\d+), frames=(\d+), images=(\d+), driver=dummy\n", result.stdout)
                assert summary is not None, result.stdout
                assert tuple(map(int, summary.groups())) == (data["audio"]["callback_count"],
                        data["audio"]["rendered_frames"], data["runtime"]["rendered_images"])
            else:
                assert result.stdout == ""
        if events is not None:
            assert data["replay"]["passed"] and data["replay"]["completed"]
            assert data["replay"]["final_acknowledged"]
            assert data["replay"]["scheduled_events"] == data["replay"]["pushed_events"] == len(events)
            assert not data["presentation"]["observations_truncated"]
        return data, state, result

    try:
        binary = args.build / "apps/standalone/hammond_standalone"
        source_inputs = {name: args.source / path for name, path in METADATA.items()}
        source_inputs.update({"LICENSE-SDL2.txt": args.sdl / "LICENSE.txt",
                              "standalone-capabilities.json": args.build / "generated/standalone-capabilities.json"})
        expected = {"bin/hammond_standalone": identity(binary), **{
            "share/hammond-b3-organ/standalone/" + name: identity(path)
            for name, path in source_inputs.items()}}
        assert len(expected) == 15
        record["expected_payload"] = expected
        run("install", [args.cmake, "--install", args.build, "--config", "Release",
                        "--component", "Standalone", "--prefix", prefix])
        assert inventory(prefix) == expected
        prefix.rename(moved)
        assert not prefix.exists()
        assert inventory(moved) == expected
        exe = moved / "bin/hammond_standalone"
        metadata_dir = moved / "share/hammond-b3-organ/standalone"
        cap = json.loads((metadata_dir / "standalone-capabilities.json").read_text())
        assert cap["midi"]["enabled"] is False
        assert cap["midi"]["backend"] == "unavailable" and cap["midi"]["rtmidi"] is None
        assert cap["fonts"]["embedded"] and cap["reference_art"]["embedded"]
        assert cap["profile"] == "embedded nominal-unmeasured-v1"
        assert cap["sdl2"]["license_sha256"] == sha(metadata_dir / "LICENSE-SDL2.txt")
        assert cap["fonts"]["license_sha256"] == sha(metadata_dir / "LICENSE-DejaVu.txt")
        assert not any("rtmidi" in name.lower() for name in expected)
        record["capabilities"] = cap
        for name in [n for n in METADATA if n.endswith(".md")]:
            for target in re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", (metadata_dir / name).read_text()):
                if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
                    continue
                assert (metadata_dir / target.split("#", 1)[0]).is_file(), (name, target)
        help_result = run("help", [exe, "--help"], no_sdl=True)
        assert "--workspace" in help_result.stdout and "--flat" in help_result.stdout
        assert help_result.stderr == "" and not list(unrelated.iterdir())
        listed = run("list-midi", [exe, "--list-midi"], 1, no_sdl=True)
        assert listed.stdout == "MIDI backend: unavailable\n"
        assert "MIDI backend is unavailable in this build" in listed.stderr
        assert not list(unrelated.iterdir())

        bmp = unrelated / "service-flat.bmp"
        service, _, _ = native("service-flat", ["--workspace", "service", "--flat", "--smoke-ms", "600",
                                                  "--screenshot", bmp], absent_state=True)
        assert service["smoke"]["passed"] and service["smoke"]["held_observed"] and service["smoke"]["release_observed"]
        painted = service["presentation"]
        assert painted["initial_workspace"] == "service" and painted["initial_presentation"] == "flat"
        assert painted["screenshot"]["workspace"] == "service" and painted["screenshot"]["presentation"] == "flat"
        assert painted["screenshot"]["inspection"]["snapshot_available"]
        assert painted["screenshot"]["inspection"]["snapshot_state"] in ("current", "retained")
        from PIL import Image
        png = args.reports / "a29-relocated-service-flat.png"
        with Image.open(bmp) as image:
            assert image.size == (960, 700)
            assert len(set(image.convert("RGB").tobytes())) > 32
            image.save(png)
        record["capture"] = {"png": identity(png), "bmp": identity(bmp), "painted_view": painted["screenshot"]}
        bmp.unlink()

        events = [(180, "key_down A none 0")] + tap(400, "F5") + tap(600, "F7")
        events += tap(800, "F6") + tap(1000, "F4") + tap(1200, "F7") + [(1350, "key_up A alt+shift")]
        navigation, state, _ = native("workspace-navigation", [], events=events)
        frames = navigation["presentation"]["observations"] + [navigation["presentation"]["last_painted"]]
        views = collapsed([(frame["workspace"], frame["presentation"]) for frame in frames])
        assert views == [("play", "dimensional"), ("rotary", "dimensional"), ("rotary", "flat"),
                         ("service", "flat"), ("play", "flat"), ("play", "dimensional")], views
        replay = navigation["replay"]
        assert replay["accepted_note_on_commands"] == replay["accepted_note_off_commands"] == 1
        assert all(item["controls"] == navigation["controls"] for item in replay["observations"])
        assert replay["before_shutdown"]["manual_notes"] == [[], []]
        assert navigation["controls"]["fixed_registrations"] == [6, 8]
        clocks = [frame["inspection"]["frame_clock"] for frame in frames if frame["inspection"]["snapshot_available"]]
        assert clocks == sorted(clocks) and clocks[-1] > clocks[0]
        record["navigation"] = {"views": views, "on_off_commands": [1, 1], "state_sha256": sha(state),
                                 "controls_unchanged": True, "frame_clock_monotonic": True}

        events = click(100, 830, 66) + click(300, 264, 534) + click(500, 500, 534) + click(700, 780, 130)
        events += [(850, "key_down A none 0"), (1050, "key_up A none")]
        modal, state, _ = native("no-input-modal", ["--workspace", "service", "--flat"],
                                  events=events, duration=1250)
        assert modal["midi"]["status"] == "No MIDI input selected."
        assert modal["midi"]["requested_port"] == modal["midi"]["port_name"] == ""
        assert modal["midi"]["discovery"]["started"] == 0
        assert modal["replay"]["accepted_note_on_commands"] == modal["replay"]["accepted_note_off_commands"] == 1
        frames = modal["presentation"]["observations"] + [modal["presentation"]["last_painted"]]
        assert any(frame["overlay"] == "midi" for frame in frames)
        assert frames[-1]["overlay"] == "none"
        record["no_input_modal"] = {"actions": ["MIDI header", "Apply No input", "Disconnect", "Close", "computer note"],
                                    "state_sha256": sha(state), "discovery": modal["midi"]["discovery"]}

        missing_port = " __A29_physical_port_unavailable_6f09e1_Ω__ "
        failed, state, process = native("physical-port-rejection", ["--workspace", "rotary", "--flat",
                                          "--smoke-ms", "600", "--midi-port", missing_port], expected=1)
        assert failed["midi"]["requested_port"] == missing_port
        assert failed["midi"]["startup_failed"] and not failed["smoke"]["passed"]
        assert "MIDI backend unavailable in this build." in process.stderr
        assert failed["controls"] == navigation["controls"]
        record["physical_port_rejection"] = {"state_sha256": sha(state), "state_preserved_exactly": True,
                                             "open_failures": 0, "native_callbacks": 0,
                                             "expected_errors": failed["errors"]}
        assert inventory(moved) == expected and identity(binary) == expected["bin/hammond_standalone"]
        assert all(identity(path) == expected["share/hammond-b3-organ/standalone/" + name]
                   for name, path in source_inputs.items())
        record.update(status="passed", payload_count=len(expected), relocated_prefix=str(moved),
                      payload_unchanged=True, built_binary_unchanged=True, installed_guides_exact=True,
                      native_invocations=len(record["commands"]) - 1,
                      retained_png_count=1)
    except Exception as error:
        record.update(status="failed", failure=f"{type(error).__name__}: {error}")
        raise
    finally:
        output.write_text(json.dumps(record, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
