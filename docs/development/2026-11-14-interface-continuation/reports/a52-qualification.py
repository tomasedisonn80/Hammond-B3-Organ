#!/usr/bin/env python3
"""A52: one affected native suite, retained-trace oracle checks, one legal burst.

No build, hardware enumeration, screenshot, or production-derived value oracle.
Each phase requires a fresh output directory and retains failure evidence.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import signal
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[4]
REPORTS = Path(__file__).resolve().parent
NATIVE = ROOT / "apps/standalone/native_tests"
sys.path.insert(0, str(NATIVE))
import test_standalone_app as app
import test_standalone_midi_replay as midi
import test_standalone_workflows as workflow
import test_standalone_workspace_replay as workspace

PIN = "bd4991a3b45543a01c9ce435da140af848d45f28ff535699397706e5d3925dc2"
COMMITS = ("8673713a484c40e26ac7810c7c4cbc22fa874426",
           "cdbb2beaa28bf136f9a8db6213819129514e2ae9")
FIXTURE = "apps/standalone/native_tests/test_standalone_workspace_replay.py"
METHOD = "test_synthetic_midi_and_ui_owners_survive_pointer_navigation_and_resize"
CASE = workspace.NativeWorkspaceReplayAcceptance(methodName=METHOD)
ENVIRONMENT = {"SDL_AUDIODRIVER": "dummy", "SDL_VIDEODRIVER": "dummy"}
EMPTY = ((), (), ())


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identity(path: Path) -> dict:
    return {"bytes": path.stat().st_size, "sha256": digest(path)}


def save(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def read(path: Path):
    return json.loads(path.read_text(), object_pairs_hook=app.unique_object,
                      parse_constant=app.reject_nonfinite)


def git(*arguments: str) -> str:
    return subprocess.check_output(["git", *arguments], cwd=ROOT, text=True).strip()


def source_snapshot(executable: Path) -> dict:
    reference = read(REPORTS / "a46-source-before.json")
    paths = sorted(reference["production_files"])
    observed = {name: identity(ROOT / name) for name in paths}
    CASE.assertEqual(observed, reference["production_files"])
    # Observe the committed blobs ourselves; the A46 inventory is only a path set.
    queries = [(commit, name) for commit in COMMITS for name in paths]
    payload = subprocess.check_output(["git", "cat-file", "--batch"], cwd=ROOT,
        input="".join(f"{commit}:{name}\n" for commit, name in queries).encode())
    cursor = 0
    for commit, name in queries:
        end = payload.index(b"\n", cursor)
        header = payload[cursor:end].split()
        CASE.assertEqual(header[1], b"blob")
        size = int(header[2])
        blob = payload[end + 1:end + 1 + size]
        CASE.assertEqual({"bytes": len(blob), "sha256": hashlib.sha256(blob).hexdigest()},
                         observed[name], f"Published product mismatch: {commit}:{name}")
        cursor = end + size + 2
    CASE.assertEqual(cursor, len(payload))
    build = read(REPORTS / "a36-build.json")
    CASE.assertEqual(build["executable"]["sha256"], PIN)
    CASE.assertEqual(build["returncode"], 0)
    CASE.assertTrue(build["source_unchanged_during_build"])
    overlap = set(paths) & set(build["source_sha256_after_build"])
    CASE.assertEqual(len(overlap), 96)
    for name in overlap:
        CASE.assertEqual(observed[name]["sha256"], build["source_sha256_after_build"][name])
    CASE.assertEqual(digest(executable), PIN)
    inputs = [Path(__file__).resolve(), ROOT / FIXTURE,
              NATIVE / "test_standalone_app.py", NATIVE / "test_standalone_midi_replay.py",
              NATIVE / "test_standalone_workflows.py", REPORTS / "a36-build.json",
              REPORTS / "a46-source-before.json", REPORTS / "a49-workspace-failure.json",
              REPORTS / "a49-release-ctest.log", REPORTS / "a49-release-junit.xml",
              REPORTS / "a49-workspace-failed-diagnostics.json",
              REPORTS / "a49-workspace-failed-input.b3ui",
              REPORTS / "a49-workspace-failed-midi.b3midi",
              REPORTS / "a49-workspace-state-from-fixture.b3controls"]
    return {"head": git("rev-parse", "HEAD"), "tree": git("rev-parse", "HEAD^{tree}"),
            "product_files": observed, "product_count": len(paths),
            "product_inventory_sha256": hashlib.sha256(json.dumps(observed, sort_keys=True,
                separators=(",", ":")).encode()).hexdigest(),
            "product_matches_commits": list(COMMITS), "a36_matching_product_files": len(overlap),
            "a36_excluded_reference_files": sorted(set(paths) - overlap),
            "executable": {"path": str(executable), **identity(executable)},
            "qualification_inputs": {str(path.relative_to(ROOT)): identity(path) for path in inputs},
            "a36_recorded_toolchain": build["toolchain"],
            "a36_recorded_configuration": build["configuration"],
            "a36_recorded_dependency_revisions": build["dependency_revisions"]}


def run_process(command: list[str], directory: Path, environment: dict, timeout: float) -> dict:
    started = time.monotonic()
    timed_out = False
    with (directory / "stdout.txt").open("wb") as out, (directory / "stderr.txt").open("wb") as err:
        process = subprocess.Popen(command, cwd=ROOT, env=dict(os.environ, **environment),
            stdin=subprocess.DEVNULL, stdout=out, stderr=err, start_new_session=True)
        while True:
            pid, status, usage = os.wait4(process.pid, os.WNOHANG)
            if pid:
                break
            if time.monotonic() - started >= timeout:
                timed_out = True
                os.killpg(process.pid, signal.SIGKILL)
                _, status, usage = os.wait4(process.pid, 0)
                break
            time.sleep(0.01)
        process.returncode = os.waitstatus_to_exitcode(status)
    result = {"command": command, "cwd": str(ROOT), "environment_overrides": environment,
              "timeout_seconds": timeout, "timed_out": timed_out,
              "returncode": process.returncode, "elapsed_seconds": time.monotonic() - started,
              "linux_wait4": {"max_rss_kib": usage.ru_maxrss,
                              "user_seconds": usage.ru_utime, "system_seconds": usage.ru_stime},
              "resource_scope": "one observed child process; suite child usage includes its reaped children; 10 ms polling quantization; no performance/leak/deadline inference"}
    save(directory / "process.json", result)
    CASE.assertFalse(timed_out)
    CASE.assertEqual(process.returncode, 0)
    return result


def suite(args, result: dict) -> None:
    evidence = args.output / "cases"
    environment = dict(ENVIRONMENT,
        HAMMOND_STANDALONE_EXECUTABLE=str(args.executable),
        HAMMOND_STANDALONE_WORKSPACE_EVIDENCE=str(evidence))
    result["process"] = run_process([sys.executable, "-B", str(ROOT / FIXTURE)],
                                     args.output, environment, 90.0)
    cases = sorted(evidence.glob("*/process.json"))
    CASE.assertEqual(len(cases), 16)
    CASE.assertEqual(sum(read(path)["returncode"] == 0 for path in cases), 16)
    result["native_processes"] = len(cases)
    result["unittest_methods"] = 6
    result["startup_prefix_case"] = str((evidence / f"{METHOD}-1").relative_to(ROOT))
    result["original_journey_case"] = str((evidence / f"{METHOD}-2").relative_to(ROOT))
    full = evidence / f"{METHOD}-2"
    for actual, original in (("workspace input.b3ui", "a49-workspace-failed-input.b3ui"),
                             ("MIDI input.b3midi", "a49-workspace-failed-midi.b3midi"),
                             ("private controls.b3controls", "a49-workspace-state-from-fixture.b3controls")):
        CASE.assertEqual((full / actual).read_bytes(), (REPORTS / original).read_bytes())
    result["original_journey_inputs_unchanged"] = True


def retained(args, result: dict) -> None:
    prefix_dir = args.suite_output / "cases" / f"{METHOD}-1"
    prefix = read(prefix_dir / "diagnostics.json")
    original = read(REPORTS / "a49-workspace-failed-diagnostics.json")
    full_ui = (REPORTS / "a49-workspace-failed-input.b3ui").read_bytes()
    full_midi = (REPORTS / "a49-workspace-failed-midi.b3midi").read_bytes()

    def exercise(prefix_data: dict, full_data: dict) -> None:
        case = workspace.NativeWorkspaceReplayAcceptance(methodName=METHOD)
        calls = []

        @contextmanager
        def supplied(duration, events, **keywords):
            index = len(calls)
            calls.append(duration)
            actual_ui = workspace.script("B3UIREPLAY1", duration, events)
            actual_midi = workspace.script("B3MIDIREPLAY1", duration, keywords["midi_events"])
            wanted_ui = (prefix_dir / "workspace input.b3ui").read_bytes() if index == 0 else full_ui
            wanted_midi = (prefix_dir / "MIDI input.b3midi").read_bytes() if index == 0 else full_midi
            case.assertEqual(actual_ui, wanted_ui)
            case.assertEqual(actual_midi, wanted_midi)
            yield workflow.WorkflowRun(prefix_data if index == 0 else full_data,
                                       workflow.FIXED_STATE, 0.0)
        case.run_native = supplied
        getattr(case, METHOD)()
        case.assertEqual(calls, [250, 3200])

    # Reproduce the old assertion against the retained trace without launching.
    original_source = git("show", f"{COMMITS[1]}:{FIXTURE}")
    old_class = next(node for node in ast.parse(original_source).body
                     if isinstance(node, ast.ClassDef) and node.name == "NativeWorkspaceReplayAcceptance")
    old_method = next(node for node in old_class.body
                      if isinstance(node, ast.FunctionDef) and node.name == "assert_commands")
    namespace = {}
    exec("from __future__ import annotations\n" + ast.unparse(old_method), namespace)
    try:
        namespace["assert_commands"](CASE, workflow.WorkflowRun(original, workflow.FIXED_STATE, 0), on=5, off=5)
    except AssertionError as error:
        result["original_oracle_failure_reproduced_without_native_run"] = str(error)
    else:
        raise AssertionError("Original oracle unexpectedly accepted the retained failure")
    exercise(prefix, original)
    result["repaired_method_accepts_retained_trace"] = True
    checks = []
    def packet_checks(data: dict, ui_source: bytes, midi_source: bytes) -> None:
        def events(source: bytes):
            return [(int(line.split(maxsplit=1)[0]), line.split(maxsplit=1)[1])
                    for line in source.decode().splitlines()[2:]]
        duration = int(ui_source.decode().splitlines()[1].split()[1])
        midi.NativeMidiReplayAcceptance.assert_common(CASE, data, duration,
            events(midi_source), events(ui_source), Path(data["state_path"]), successful=True)
    prefix_ui = (prefix_dir / "workspace input.b3ui").read_bytes()
    prefix_midi = (prefix_dir / "MIDI input.b3midi").read_bytes()
    packet_checks(prefix, prefix_ui, prefix_midi)
    packet_checks(original, full_ui, full_midi)
    result["shared_midi_checker_accepts_zero_and_positive_packet_traces"] = True
    for name, value, ui_source, midi_source, timestamp in (
        ("invented_zero_packet_arrival", prefix, prefix_ui, prefix_midi, 1),
        ("missing_positive_packet_arrival", original, full_ui, full_midi, 0)):
        mutated = deepcopy(value)
        mutated["midi_replay"]["last_arrival_ns"] = timestamp
        try:
            packet_checks(mutated, ui_source, midi_source)
        except AssertionError as error:
            checks.append({"mutation": name, "rejected": True, "assertion": str(error)})
        else:
            raise AssertionError(f"Oracle accepted mutation: {name}")
    for name in ("unacknowledged_prefix", "extra_command", "missing_note_off", "lost_independent_midi_owner", "dropped_packet"):
        bad_prefix, bad_full = deepcopy(prefix), deepcopy(original)
        if name == "unacknowledged_prefix":
            bad_prefix["replay"]["before_shutdown"]["resolved_sequence"] -= 1
        elif name == "extra_command":
            bad_full["replay"]["last_submitted_sequence"] += 1
        elif name == "missing_note_off":
            bad_full["replay"]["accepted_note_off_commands"] -= 1
        elif name == "lost_independent_midi_owner":
            item = next(item for item in bad_full["replay"]["observations"]
                        if item["elapsed_ms"] == 2134)
            item["manual_notes"][0] = []
        else:
            bad_full["midi_replay"]["dropped_packets"] = 1
        try:
            exercise(bad_prefix, bad_full)
        except AssertionError as error:
            checks.append({"mutation": name, "rejected": True, "assertion": str(error)})
        else:
            raise AssertionError(f"Oracle accepted mutation: {name}")
    result["negative_checks"] = checks
    result["native_processes"] = 0
    result["prefix_diagnostics"] = {"path": str((prefix_dir / "diagnostics.json").relative_to(ROOT)),
                                    **identity(prefix_dir / "diagnostics.json")}
    result["measured_startup_sequence"] = prefix["replay"]["before_shutdown"]["last_applied_sequence"]


def burst_plan() -> list[tuple[int, str]]:
    events = workspace.tap(100, "Tab", "shift") + workspace.tap(150, "Tab", "shift")
    events += [(400, "key_down A none 0")] + workspace.tap(600, "F2")
    events += [(800, "key_down S none 0")] + workspace.tap(1000, "F3")
    for at, key in ((1300, "F5"), (1600, "F7"), (1900, "F6"), (2200, "F4")):
        events += workspace.tap(at, key)
    for key in ["F5", "F7", "F6", "F4"] * 28 + ["F5", "F7"]:
        events += [(2600, f"key_down {key} none 0"), (2600, f"key_up {key} none")]
    for at, key in ((3000, "F6"), (3300, "F4"), (3600, "F7")):
        events += workspace.tap(at, key)
    events += [(4000, "key_down Space none 0"), (4300, "key_up Space none"),
               (4600, "key_up A ctrl+alt+meta"), (4900, "key_up S shift")]
    return events


def burst(args, result: dict) -> None:
    events = burst_plan()
    source = workspace.script("B3UIREPLAY1", 5400, events)
    CASE.assertEqual(len(events), 256)
    CASE.assertLessEqual(len(source), 65536)
    CASE.assertEqual([at for at, _ in events], sorted(at for at, _ in events))
    CASE.assertTrue(all(0 <= at < 5400 for at, _ in events))
    (args.output / "input.b3uireplay").write_bytes(source)
    state_path = args.output / "controls.b3controls"
    state_path.write_bytes(workflow.FIXED_STATE)
    result["budget"] = {"parser_action_limit": 256, "script_actions": len(events),
        "parser_byte_limit": 65536, "script_bytes": len(source),
        "parser_duration_range_ms": [250, 10000], "duration_ms": 5400,
        "maximum_scheduled_equal_time_actions": max(Counter(at for at, _ in events).values()),
        "main_loop_polled_event_limit_per_turn": 256, "session_command_capacity": 256,
        "musical_observation_capacity": 512, "presentation_observation_capacity": 512,
        "application_replay_drain_ms": 2000, "process_timeout_seconds": 20,
        "intended_workspace_changes": 90, "intended_presentation_toggles": 31,
        "expected_note_on_commands": 3, "expected_note_off_commands": 3,
        "expected_other_post_startup_session_commands": 0}
    command = [str(args.executable), "--state", str(state_path), "--input-script",
               str(args.output / "input.b3uireplay"), "--diagnostics", str(args.output / "diagnostics.json"),
               "--width", "1280", "--height", "900", "--sample-rate", "48000", "--buffer-frames", "512"]
    result["process"] = run_process(command, args.output, ENVIRONMENT, 20.0)
    CASE.assertEqual((args.output / "stdout.txt").read_bytes(), b"")
    CASE.assertEqual((args.output / "stderr.txt").read_bytes(), b"")
    data = read(args.output / "diagnostics.json")
    schema = dict(app.SCHEMA)
    schema["replay"] = midi.replay_schema(data["replay"], midi.UI_REPLAY_SCHEMA)
    app.assert_schema(CASE, data, schema)
    workflow.NativeWorkflowAcceptance.assert_common(CASE, data, source.decode(), state_path, (1280, 900))
    app.assert_presentation(CASE, data)
    run = workflow.WorkflowRun(data, state_path.read_bytes(), result["process"]["elapsed_seconds"])
    CASE.assert_control_path(run, [workflow.FIXED_CONTROLS])
    expected_holds = [EMPTY, ((60,), (), ()), ((60,), (62,), ()),
                      ((60,), (60, 62), ()), ((60,), (62,), ()), ((), (62,), ()), EMPTY]
    CASE.assert_hold_path(run, expected_holds)
    # Reuse an actual pre-action UI-only baseline from the just-passed suite.
    baseline_path = args.suite_output / "cases" / "test_capture_failure_closes_parameter_gesture_before_view_and_resize-1" / "diagnostics.json"
    baseline = read(baseline_path)["replay"]["observations"][0]
    CASE.assertEqual(workspace.holds(baseline), EMPTY)
    CASE.assertEqual(baseline["last_submitted_sequence"], baseline["last_applied_sequence"])
    CASE.assertLess(baseline["elapsed_ms"], 180)
    origin = baseline["last_applied_sequence"]
    CASE.assert_commands(run, on=3, off=3, startup_sequence=origin)
    observed = data["replay"]
    earliest = [0, 400, 800, 4000, 4300, 4600, 4900]
    seen = set()
    for item in observed["observations"]:
        index = item["last_applied_sequence"] - origin
        CASE.assertIn(index, range(7))
        CASE.assertEqual(workspace.holds(item), expected_holds[index])
        CASE.assertGreaterEqual(item["elapsed_ms"], earliest[index])
        seen.add(index)
    CASE.assertEqual(seen, set(range(7)))
    CASE.assert_views(run, [(view, mode, 1280, 900) for view, mode in (
        ("play", "dimensional"), ("rotary", "dimensional"), ("rotary", "flat"),
        ("service", "flat"), ("play", "flat"), ("rotary", "dimensional"),
        ("service", "dimensional"), ("play", "dimensional"), ("play", "flat"))])
    CASE.assertEqual(data["replay"]["device_starts"], 1)
    CASE.assertEqual(data["runtime"]["renderer"], "software")
    CASE.assertFalse(data["runtime"]["screenshot_written"])
    CASE.assertIsNone(data["presentation"]["screenshot"])
    CASE.assertEqual(data["presentation"]["last_painted"], data["presentation"]["before_shutdown"])
    inspection = data["presentation"]["before_shutdown"]["inspection"]
    CASE.assertTrue(inspection["snapshot_available"])
    CASE.assertEqual(inspection["snapshot_state"],
                     "current" if inspection["snapshot_read_succeeded"] else "retained")
    CASE.assertFalse(inspection["controls_pending"])
    CASE.assertFalse(data["presentation"]["observations_truncated"])
    CASE.assertEqual(observed["desired_controls_before_shutdown"], workflow.FIXED_CONTROLS)
    CASE.assertFalse(observed["controls_pending_before_shutdown"])
    CASE.assertFalse(observed["save_pending_before_shutdown"])
    CASE.assertEqual(state_path.read_bytes(), workflow.FIXED_STATE)
    CASE.assertEqual((args.output / "input.b3uireplay").read_bytes(), source)
    session = data["session"]
    CASE.assertEqual(session["resolved_sequence"], observed["last_submitted_sequence"] + 1)
    CASE.assertEqual(session["resolved_sequence"] - session["last_applied_sequence"], session["discarded_commands"])
    result["native_processes"] = 1
    result["baseline_diagnostics"] = {"path": str(baseline_path.relative_to(ROOT)), **identity(baseline_path)}
    result["startup_sequence"] = origin
    result["pre_shutdown_sequence"] = observed["last_submitted_sequence"]
    result["acknowledged_prefixes_seen"] = sorted(seen)
    result["presentation_observations"] = len(data["presentation"]["observations"])
    result["musical_observations"] = len(observed["observations"])
    result["final_focus_behavior"] = "Space auditions original remembered Lower C4 while F3 targets Pedals; original A Upper60 and S Lower62 owners remain until their modified-key releases"
    result["shutdown_discarded_commands"] = session["discarded_commands"]
    result["limits"] = ["1280x900 dummy drawable only; no giant surface or physical display qualification",
        "228 equal-time actions are scheduled, not a measured per-turn SDL dispatch count",
        "121 shortcut activations are the admitted script intent; intermediate unpainted views are not individually observed",
        "No pointer actions or persistent OS capture; earlier dummy capture failure is not OS-pointer coverage",
        "No MIDI selection or discovery, physical audio, semantic accessibility, callback deadline, leak or fidelity claim"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("suite", "retained", "burst"))
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--suite-output", type=Path)
    args = parser.parse_args()
    args.executable = args.executable.resolve(strict=True)
    args.output = args.output.resolve()
    if args.suite_output:
        args.suite_output = args.suite_output.resolve(strict=True)
    if args.phase != "suite" and args.suite_output is None:
        parser.error("--suite-output is required for retained and burst phases")
    args.output.mkdir(parents=True, exist_ok=False)
    result = {"schema": "a52-native-input-qualification-v1", "phase": args.phase,
              "assignment": 52, "worker": "/root/w09_a52_bounded_native_burst",
              "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
              "command": [sys.executable, *sys.argv], "python": platform.python_version(),
              "authorization": "Root released CPU after A49 and authorized one repaired six-method suite, retained-trace checks and one bounded burst; no native retry",
              "passed": False, "failure": None}
    try:
        before = source_snapshot(args.executable)
        save(args.output / "source-before.json", before)
        {"suite": suite, "retained": retained, "burst": burst}[args.phase](args, result)
        result["passed"] = True
    except Exception:
        result["failure"] = traceback.format_exc()
        (args.output / "failure.txt").write_text(result["failure"])
    finally:
        try:
            after = source_snapshot(args.executable)
            save(args.output / "source-after.json", after)
            CASE.assertEqual(after["product_files"], before["product_files"])
            CASE.assertEqual(after["executable"], before["executable"])
            CASE.assertEqual(after["qualification_inputs"], before["qualification_inputs"])
            result["source_executable_and_inputs_unchanged"] = True
        except Exception:
            result["passed"] = False
            result["closing_failure"] = traceback.format_exc()
        result["output_files"] = {str(path.relative_to(args.output)): identity(path)
                                  for path in sorted(args.output.rglob("*")) if path.is_file()}
        save(args.output / "result.json", result)
    print(json.dumps({key: result.get(key) for key in (
        "phase", "passed", "native_processes", "source_executable_and_inputs_unchanged", "failure", "closing_failure")}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
