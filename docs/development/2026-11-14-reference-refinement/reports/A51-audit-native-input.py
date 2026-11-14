#!/usr/bin/env python3
"""Read retained native-input evidence and Git blobs; never launch the application.

The optional BMP and current executable are read and hashed only. This is a
reproducible evidence audit, not a native acceptance test or a new desktop run.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_sha(value: object) -> str:
    return sha(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--published", default="0881d1f4c5a26ce9c75dda7a3adde46382e5ab6b")
    parser.add_argument("--startup-bmp", type=Path)
    parser.add_argument("--current-app", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    reports = Path("docs/development/2026-11-14-reference-refinement/reports")
    checks: dict[str, bool] = {}

    def check(name: str, condition: bool) -> None:
        checks[name] = bool(condition)

    def git(*argv: str) -> bytes:
        return subprocess.check_output(["git", "-C", str(repo), *argv])

    def read_json(name: str) -> dict:
        return json.loads((repo / reports / name).read_text())

    def identity(path: Path, label: str | None = None) -> dict:
        data = path.read_bytes()
        return {"path": label or str(path), "bytes": len(data), "sha256": sha(data)}

    source = read_json("root-desktop-acceptance-source.json")
    root_review = read_json("root-desktop-acceptance-review.json")
    report = read_json("desktop-acceptance.json")
    gallery = read_json("A46-final-native-gallery.json")
    primary_names = (
        "desktop-acceptance.json", "root-desktop-acceptance-review.json",
        "root-desktop-acceptance-source.json", "desktop-acceptance-startup.png",
        "desktop-acceptance.stdout.txt", "desktop-acceptance.stderr.txt",
    )
    primary = {name: identity(repo / reports / name, str(reports / name)) for name in primary_names}
    supporting_names = (
        "A20-result.json", "A26-identities.json", "A34-audio-state-isolation.json",
        "A40-reference-header-refinement.json", "A46-final-native-gallery.json",
        "A18-result.json", "A23-pending-independent.json",
    )
    supporting = {name: identity(repo / reports / name, str(reports / name)) for name in supporting_names}
    check("retained_diagnostics_hash_matches_root_review", primary["desktop-acceptance.json"]["sha256"] == root_review["diagnostics_sha256"])
    check("retained_startup_png_hash_matches_root_review", primary["desktop-acceptance-startup.png"]["sha256"] == root_review["startup_png_sha256"])
    check("old_binary_identity_agrees_between_records", source["binary_sha256"] == root_review["binary_sha256"])
    check("stdout_and_stderr_empty", all(primary[name]["bytes"] == 0 for name in primary_names[-2:]))

    compared = []
    for name, old_sha in sorted(source["source_sha256"].items()):
        published_bytes = git("show", f"{args.published}:{name}")
        published_sha = sha(published_bytes)
        live_sha = sha((repo / name).read_bytes())
        compared.append({"path": name, "retained_sha256": old_sha,
                         "published_sha256": published_sha, "live_sha256": live_sha})
    changed = [item for item in compared if item["retained_sha256"] != item["published_sha256"]]
    unchanged = [item["path"] for item in compared if item["retained_sha256"] == item["published_sha256"]]
    check("retained_inventory_count_161", len(compared) == 161)
    check("159_retained_paths_match_published_source", len(unchanged) == 159)
    check("all_161_live_paths_match_published_source", all(item["live_sha256"] == item["published_sha256"] for item in compared))
    check("only_painter_and_standalone_cmake_differ_in_inventory", {item["path"] for item in changed} == {
        "apps/standalone/InstrumentView.cpp", "apps/standalone/CMakeLists.txt"})

    painter_path = "apps/standalone/InstrumentView.cpp"
    old_painter = git("show", f"{source['base_commit']}:{painter_path}")
    new_painter = git("show", f"{args.published}:{painter_path}")
    check("base_commit_painter_matches_retained_inventory", sha(old_painter) == source["source_sha256"][painter_path])
    def outside_reviewed_painter_region(data: bytes) -> bytes:
        start = data.index(b"void midi_overlay(")
        end = data.index(b"[[nodiscard]] std::string focused_control_caption(", start)
        return data[:start] + data[end:]
    check("painter_bytes_outside_midi_audio_help_and_header_region_unchanged",
          outside_reviewed_painter_region(old_painter) == outside_reviewed_painter_region(new_painter))
    cmake_path = "apps/standalone/CMakeLists.txt"
    new_cmake = git("show", f"{args.published}:{cmake_path}")
    first = new_cmake.index(b"        add_executable(test_standalone_material_acceptance\n")
    last = new_cmake.index(b"        add_executable(test_standalone_scaled_view\n", first)
    reconstructed_old_cmake = new_cmake[:first] + new_cmake[last:]
    check("removing_only_material_test_registration_reproduces_old_cmake_hash",
          sha(reconstructed_old_cmake) == source["source_sha256"][cmake_path])
    critical_names = (
        "apps/standalone/main.cpp", "apps/standalone/UiModel.cpp", "apps/standalone/UiModel.h",
        "apps/standalone/Session.cpp", "apps/standalone/Session.h",
        "apps/standalone/AudioDevice.cpp", "apps/standalone/AudioDevice.h",
        "apps/standalone/MidiInput.cpp", "apps/standalone/MidiInput.h",
        "apps/standalone/StateFiles.cpp", "apps/standalone/StateFiles.h",
        "src/Engine.cpp", "include/hammond/Engine.h", "src/NoteOwnership.cpp",
        "include/hammond/NoteOwnership.h", "src/PedalNoteOwnership.cpp",
        "include/hammond/PedalNoteOwnership.h", "src/ControlStateIO.cpp",
        "data/parameter-registry.json",
    )
    critical = {name: source["source_sha256"][name] for name in critical_names}
    check("all_named_input_session_state_and_ownership_sources_unchanged", all(name in unchanged for name in critical_names))

    presentation = report["presentation"]
    observations = presentation["observations"]
    scalar_types = {"elapsed_ms": int, "rendered_image": int, "workspace": str,
                    "presentation": str, "overlay": str, "window_width": int, "window_height": int}
    inspection_types = {"snapshot_available": bool, "snapshot_read_succeeded": bool,
                        "snapshot_state": str, "controls_pending": bool,
                        "frame_clock": int, "publication_revision": int}
    capture_types = {"sdl_captured": bool, "ui_captured": bool, "attempts": int,
                     "successes": int, "losses": int, "release_calls": int}
    held_types = {"upper": int, "lower": int, "pedals": int}
    frames = observations + [presentation[name] for name in ("screenshot", "last_painted", "before_shutdown")]
    def exact_typed(record: dict, fields: dict) -> bool:
        return type(record) is dict and set(record) == set(fields) and all(type(record[key]) is kind for key, kind in fields.items())
    typed = True
    bounded = True
    for frame in frames:
        typed &= type(frame) is dict and set(frame) == set(scalar_types) | {"inspection", "held_targets", "pointer_capture"}
        typed &= all(type(frame[key]) is kind for key, kind in scalar_types.items())
        typed &= exact_typed(frame["inspection"], inspection_types)
        typed &= exact_typed(frame["pointer_capture"], capture_types)
        typed &= exact_typed(frame["held_targets"], held_types)
        bounded &= all(0 <= frame["held_targets"][part] <= count for part, count in (("upper", 61), ("lower", 61), ("pedals", 25)))
        bounded &= 960 <= frame["window_width"] <= 8192 and 700 <= frame["window_height"] <= 8192
        capture = frame["pointer_capture"]
        bounded &= all(capture[name] >= 0 for name in ("attempts", "successes", "losses", "release_calls"))
        bounded &= capture["successes"] <= capture["attempts"] and capture["losses"] + capture["release_calls"] <= capture["successes"]
        bounded &= not capture["sdl_captured"] or capture["successes"] > 0
    check("presentation_records_have_exact_scalar_types_and_fields", typed)
    check("presentation_counts_and_capture_relationships_bounded", bounded)
    check("19_observations_untruncated_in_512_capacity", len(observations) == 19 and presentation["observations_truncated"] is False and presentation["observation_capacity"] == 512)
    check("paint_image_elapsed_clock_and_capture_counters_monotonic", all(
        b["rendered_image"] > a["rendered_image"] and b["elapsed_ms"] >= a["elapsed_ms"]
        and b["inspection"]["frame_clock"] >= a["inspection"]["frame_clock"]
        and all(b["pointer_capture"][name] >= a["pointer_capture"][name] for name in ("attempts", "successes", "losses", "release_calls"))
        for a, b in zip(observations, observations[1:])))
    check("all_observation_snapshots_available_current_and_read_successful", all(
        frame["inspection"]["snapshot_available"] is True and frame["inspection"]["snapshot_read_succeeded"] is True
        and frame["inspection"]["snapshot_state"] == "current" for frame in observations))
    check("native_x11_software_dummy_audio", report["runtime"]["video_driver"] == "x11" and report["runtime"]["renderer"] == "software" and report["audio"]["driver"] == "dummy")
    check("no_replay_or_smoke_in_runner_or_diagnostics", all(option not in source["runner"] for option in ("--input-script", "--midi-script", "--smoke"))
          and report["smoke"]["requested"] is False and "replay" not in report and "midi_replay" not in report)
    check("no_physical_midi_selected", report["midi"]["source"] == "none" and report["midi"]["active_before_shutdown"] is False)
    check("service_keyboard_transition_has_no_painted_preheld_prefix", observations[1]["workspace"] == "play" and observations[1]["held_targets"]["upper"] == 0
          and observations[2]["workspace"] == "service" and observations[2]["held_targets"]["upper"] == 0
          and observations[3]["held_targets"]["upper"] == 1 and observations[4]["held_targets"]["upper"] == 0)
    check("flat_keyboard_transition_has_no_painted_preheld_prefix", observations[5]["presentation"] == "dimensional" and observations[5]["held_targets"]["upper"] == 0
          and observations[6]["presentation"] == "flat" and observations[6]["held_targets"]["upper"] == 0
          and observations[7]["held_targets"]["upper"] == 1 and observations[8]["held_targets"]["upper"] == 0)
    check("pedal_held_1400_to_1180_then_released_without_app_pointer_capture", [frame["window_width"] for frame in observations[9:12]] == [1400, 1180, 1180]
          and [frame["held_targets"]["pedals"] for frame in observations[9:12]] == [1, 1, 0]
          and all(frame["window_height"] == 820 and frame["pointer_capture"]["sdl_captured"] is False
                  and frame["pointer_capture"]["ui_captured"] is False for frame in observations[9:12]))
    check("capture_persists_through_upper_1_0_1_0", [frame["held_targets"]["upper"] for frame in observations[13:17]] == [1, 0, 1, 0]
          and all(frame["pointer_capture"] == {"sdl_captured": True, "ui_captured": True, "attempts": 1, "successes": 1, "losses": 0, "release_calls": 0}
                  for frame in observations[12:17]))
    released_capture = {"sdl_captured": False, "ui_captured": False, "attempts": 1, "successes": 1, "losses": 0, "release_calls": 1}
    check("explicit_pointer_release_and_unheld_final_paint", observations[17]["pointer_capture"] == released_capture
          and presentation["before_shutdown"]["pointer_capture"] == released_capture
          and all(value == 0 for value in presentation["before_shutdown"]["held_targets"].values()))
    check("final_snapshot_stopped_unheld_and_fault_free", report["session"]["snapshot_available"] is True
          and report["session"]["running_after_shutdown"] is False and report["session"]["held_after_shutdown"] is False
          and all(report["session"][key] == 0 for key in ("fault_flags", "queue_overflows", "rejected_commands", "recovery_count")))
    check("recorded_one_discard_and_sequence_gap_preserved", report["session"]["discarded_commands"] == 1
          and report["session"]["resolved_sequence"] == 138 and report["session"]["last_applied_sequence"] == 137)
    check("positive_callbacks_and_frames_without_sample_failures", report["audio"]["callback_count"] == 7420 and report["audio"]["rendered_frames"] == 3799040
          and all(report["audio"][key] == 0 for key in ("render_failures", "format_failures", "overrange_failures", "overrange_samples", "nonfinite_failures", "nonfinite_samples")))
    check("no_application_errors", report["errors"]["count"] == 0)
    check("startup_capture_is_first_unheld_frame", presentation["screenshot"] == observations[0]
          and presentation["screenshot"]["rendered_image"] == 1 and report["runtime"]["screenshot_while_held"] is False
          and all(value == 0 for value in presentation["screenshot"]["held_targets"].values()))

    image_evidence = {"startup_png_visual_review": "A51 inspected the retained full image: 1400x820 Dimensional Play, old header, no held-key highlight.",
                      "interactive_desktop_screenshots_retained_in_primary_bundle": False}
    if args.startup_bmp:
        import PIL
        from PIL import Image
        bmp = args.startup_bmp.resolve()
        image_evidence["pillow_version"] = PIL.__version__
        image_evidence["startup_bmp"] = identity(bmp)
        check("scratch_startup_bmp_matches_recorded_hash", image_evidence["startup_bmp"]["sha256"] == root_review["startup_bmp_sha256"])
        with Image.open(bmp) as old_image, Image.open(repo / reports / "desktop-acceptance-startup.png") as new_image:
            old_rgba, new_rgba = old_image.convert("RGBA").tobytes(), new_image.convert("RGBA").tobytes()
            image_evidence["dimensions"] = list(new_image.size)
            image_evidence["rgba_sha256"] = sha(new_rgba)
            image_evidence["decoded_rgba_equal"] = old_rgba == new_rgba
            check("startup_bmp_png_all_rgba_pixels_equal", old_image.size == new_image.size == (1400, 820) and old_rgba == new_rgba)

    current_app = {"recorded_v4_sha256": gallery["binary_after_capture"]["sha256"],
                   "recorded_published_commit": gallery["published_commit"],
                   "capture_environment": "dummy audio / dummy video / software renderer",
                   "new_native_os_input_run_by_A51": False}
    if args.current_app:
        current_app["read_only_file_identity"] = identity(args.current_app.resolve())
        check("current_app_bytes_match_v4_record_and_differ_from_old_os_run",
              current_app["read_only_file_identity"]["sha256"] == current_app["recorded_v4_sha256"] != source["binary_sha256"])

    compact_observations = [{"index": index, "elapsed_ms": frame["elapsed_ms"], "image": frame["rendered_image"],
        "workspace": frame["workspace"], "presentation": frame["presentation"],
        "size": [frame["window_width"], frame["window_height"]], "held_upper_lower_pedals": list(frame["held_targets"].values()),
        "frame_clock": frame["inspection"]["frame_clock"], "pointer_capture": frame["pointer_capture"]}
        for index, frame in enumerate(observations)]
    result = {
        "schema": "a51-retained-native-input-evidence-v1", "assignment": "A51", "wave": 9,
        "agent": "/root/w09_a51_native_input_evidence_review",
        "scope": "Read-only retained-evidence and current-source audit; no desktop, build, CTest, app or device execution.",
        "result": "pass_with_explicit_provenance_limits" if all(checks.values()) else "audit_mismatch",
        "audit_environment": {"python": platform.python_version(), "repo": str(repo), "git_head": git("rev-parse", "HEAD").decode().strip(),
            "published_commit": args.published, "published_tree": git("rev-parse", args.published + "^{tree}").decode().strip(),
            "auditor_sha256": sha(Path(__file__).read_bytes()), "argv": sys.argv,
            "initial_manual_image_read_failure": "A preliminary read used Path('.').parent, resolving the BMP in the repository and raising FileNotFoundError. Using Path.cwd().parent corrected the audit path; no product process ran."},
        "checks": checks, "checks_passed": sum(checks.values()), "checks_total": len(checks),
        "primary_evidence": primary, "supporting_evidence": supporting,
        "old_native_run": {"recorded_executable_sha256": source["binary_sha256"], "historical_executable_rehashed": False,
            "base_commit_only": source["base_commit"], "configuration": source["configuration"], "runner": source["runner"],
            "root_post_run_161_equal_attestation": root_review["post_run_checks"]["source_inputs_unchanged"],
            "exit_code_receipt_in_primary_bundle": None,
            "ordinary_close_evidence": "Root review records actual Alt+F4 and return to Terminal. Final typed diagnostics plus identical shutdown source establish stopped/unheld joined cleanup; no numeric exit code is manufactured.",
            "runtime": report["runtime"], "audio": report["audio"], "session": report["session"],
            "discarded_command_identity": "unassigned; the retained diagnostics do not identify the command",
            "observations": compact_observations, "last_painted": presentation["last_painted"]},
        "source_comparison": {"inventory_paths": len(compared), "unchanged_paths": len(unchanged), "changed": changed,
            "comparison_canonical_sha256": canonical_sha(compared), "all_live_match_published": all(item["live_sha256"] == item["published_sha256"] for item in compared),
            "critical_unchanged_sha256": critical,
            "standalone_cmake_change": "Only the ten-line material-acceptance test registration; removing it reproduces the retained old CMake SHA-256 exactly.",
            "removed_cmake_block_sha256": sha(new_cmake[first:last]),
            "painter_change": "Audio/MIDI/Help Flat material forwarding and wide Dimensional header typography; exact source outside the contiguous three-function region is identical.",
            "qualification_boundary": "159 matching retained paths establish source identity, not a native OS rerun of a different executable. The 161-path inventory is not a complete compiler/dependency/build closure."},
        "image_evidence": image_evidence, "current_v4": current_app,
        "admissible_claims": [
            "Old executable ran on native X11/software with dummy audio and no replay/smoke; 19 untruncated typed painted observations remain.",
            "Keyboard Upper targets appear after Service and Flat transitions and release; no painted pre-held keyboard prefix proves continuity across either transition.",
            "A keyboard-held pedal remains across 1400x820 to 1180x820, then releases; it was not an app-pointer-held pedal.",
            "One successfully admitted pointer capture persists through observed inside/outside/inside/outside movement, with Upper counts 1/0/1/0, then explicit release.",
            "Final painted and joined snapshots are unheld, Session is stopped, faults/overflows/rejections are zero; one discarded command remains separately recorded and unidentified.",
        ],
        "gaps": [
            "No new OS-input qualification for the current 01fe78 executable; v4 is a separate dummy-driver endpoint gallery.",
            "No retained per-step lossless desktop frames, pointer-coordinate trace or physical press identities; locations/actions use root's contemporaneous observed review.",
            "No simultaneous pre-held keyboard+pointer navigation, pointer-held pedal resize, focus-loss/reentry or post-release fresh-press journey is retained here.",
            "No complete 1672x941 to 960x700 and reverse actual display journey; the old startup window exceeded the observed desktop width by 41 pixels.",
            "No physical audio/MIDI, display scaling, DAW, semantic accessibility, audio deadline or acoustic fidelity qualification.",
            "A18/A23 pending/acknowledged Session rendering evidence is a separate windowless/device-free harness, not this OS run or current v4.",
        ],
        "next_actual_journey": [
            "Reserve one native build/display owner, freeze intended published source, retain source/dependency/configuration/executable hashes and an exact ordinary argv with fresh outputs.",
            "Use an identified physical display, OS scale, keyboard/pointer, audio device/backend and MIDI device/port; omit dummy drivers and replay/smoke for the real-device claim.",
            "At 1672x941 retain painted keyboard Upper C4 plus pointer Upper C2 holds before F5/F7/F6/F4, then resize to 960x700 and repeat in reverse.",
            "Record suppressed-pointer hold through navigation, outside movement/release, button-up return and fresh press/release; separately retain unsuppressed inside/outside hit-target behavior.",
            "Repeat branch crossing while the pointer itself holds a pedal; record before/after hold and final release, deliberate focus loss and no resurrection on return.",
            "Exercise hardware MIDI/UI overlapping owners and both release orders with exact routing; capture the chosen actual audio path separately from UI indicators.",
            "Close an ordinary separate launch via the actual close control; retain exact process exit/status, joined diagnostics, all per-step lossless frames and untruncated typed records.",
        ],
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"result": result["result"], "checks_passed": result["checks_passed"], "checks_total": result["checks_total"],
                      "source_unchanged": len(unchanged), "source_changed": len(changed), "observations": len(observations),
                      "report": str(args.output), "report_sha256": sha(args.output.read_bytes())}, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
