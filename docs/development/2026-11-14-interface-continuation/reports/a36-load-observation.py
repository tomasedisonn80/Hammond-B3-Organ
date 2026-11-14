#!/usr/bin/env python3
"""Replay only A30's retained live-Load journey against a newly pinned app.

This is a bounded operator observation, not a new CTest/string-matching test.
The status line requires separate visual review of the one retained native PNG.
The original A30 script, inputs, expected controls and failure remain unchanged.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import platform
import subprocess
import sys
import traceback

ROOT = Path(__file__).resolve().parents[4]
REPORTS = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("a30_operator", REPORTS / "a30-operator-journey.py")
assert spec and spec.loader
a30 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a30)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.executable = args.executable.resolve(strict=True)
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=False)
    a30.PIN = args.expected_sha256  # New explicit A36 identity, never an inherited A30 pass.
    a30.CASE.assertEqual(a30.digest(args.executable), a30.PIN)

    original = REPORTS / "a30-operator-evidence/02-edit-save-live-load"
    script_bytes = (original / "input.b3uireplay").read_bytes()
    lines = script_bytes.decode("ascii").splitlines()
    a30.CASE.assertEqual(lines[:2], ["B3UIREPLAY1", "duration_ms 3150"])
    events = [(int(at), event) for at, event in (line.split(" ", 1) for line in lines[2:])]
    a30.CASE.assertEqual(a30.workspace.script("B3UIREPLAY1", 3150, events), script_bytes)
    initial = (original / "initial.b3controls").read_bytes()
    a30.CASE.assertEqual(initial, a30.workflow.FIXED_STATE)
    original_paths = [original / name for name in ("input.b3uireplay", "initial.b3controls",
                      "controls.b3controls", "diagnostics.json", "frame.png", "process.json")]
    source_paths = [Path(__file__).resolve(), REPORTS / "a30-operator-journey.py",
        *[ROOT / "apps/standalone/native_tests" / name for name in (
            "test_standalone_app.py", "test_standalone_midi_replay.py",
            "test_standalone_workflows.py", "test_standalone_workspace_replay.py")],
        ROOT / "docs/INTERFACE_RUNBOOK.md", ROOT / "docs/INTERFACE_INSPECTION_CONTRACT.md",
        ROOT / "apps/standalone/main.cpp", ROOT / "apps/standalone/InstrumentView.cpp",
        ROOT / "apps/standalone/InspectionModel.cpp", ROOT / "apps/standalone/UiModel.cpp"]
    identities = {str(p.relative_to(ROOT)): a30.digest(p) for p in [*source_paths, *original_paths]}
    result = {"agent": "A36", "kind": "single live-Load operator observation",
        "published_base_at_run": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "qualification_scope": "Working source recorded by A36 build identities; no new inspection-model gate",
        "command": [sys.executable, *sys.argv], "command_cwd": str(Path.cwd()),
        "executable": str(args.executable), "executable_sha256_before": a30.PIN,
        "python": platform.python_version(), "pillow": a30.pillow_version,
        "source_and_input_sha256_before": identities,
        "runs": [], "failure": None, "operator_assertions_completed": False}
    try:
        run = a30.invoke(args, result, "02-edit-save-live-load", 3150, events,
                         state=initial, final_size=(960, 700), capture=True)
        expected = deepcopy(a30.workflow.FIXED_CONTROLS)
        expected["manual_drawbars"][0][0][0] = 8
        sounding_b = deepcopy(expected)
        sounding_b["selected_banks"][0] = 1
        sounding_b["fixed_registrations"][0] = 0
        sounding_b["preset_selections"][0] = 11
        a30.controls(run, [a30.workflow.FIXED_CONTROLS, expected, sounding_b, expected])
        a30.command_delta(run.diagnostics, 5)
        saved = initial.replace(b"bank A 0 1 2 3 4 5 6 7 8\n", b"bank A 8 1 2 3 4 5 6 7 8\n", 1)
        a30.CASE.assertEqual(run.saved_bytes, saved)
        a30.CASE.assertEqual(run.saved_bytes, (original / "controls.b3controls").read_bytes())
        a30.CASE.assertEqual(run.diagnostics["replay"]["before_shutdown"]["controls"], expected)
        a30.notes(run, [a30.EMPTY, a30.UPPER_A, a30.EMPTY], 1, 1)
        after_load = [frame for frame in run.diagnostics["replay"]["observations"]
            if frame["elapsed_ms"] >= 2100 and frame["controls"] == expected and
            frame["last_applied_sequence"] == frame["last_submitted_sequence"] == frame["resolved_sequence"]]
        a30.CASE.assertTrue(after_load)
        acknowledgment = after_load[0]
        a30.CASE.assertEqual(acknowledgment["manual_notes"], [[60], []])
        capture = run.diagnostics["presentation"]["screenshot"]
        a30.CASE.assertEqual(capture["inspection"]["snapshot_state"], "current")
        a30.CASE.assertFalse(capture["inspection"]["controls_pending"])
        a30.CASE.assertGreater(capture["elapsed_ms"], acknowledgment["elapsed_ms"])
        a30.CASE.assertLess(capture["elapsed_ms"], 2100 + 6000)
        result["observation"] = {"load_requested_at_ms": 2100,
            "first_restored_acknowledgment": acknowledgment,
            "screenshot": capture,
            "note": "The PNG is reviewed separately for the displayed static status. Diagnostics do not record that string.",
            "status_visual_review": "pending", "original_a30_evidence_preserved": True,
            "exact_original_saved_bytes": True,
            "retained_status_expiry_ms_from_load": 6000}
        result["operator_assertions_completed"] = True
    except Exception:
        result["failure"] = traceback.format_exc()
    finally:
        result["executable_sha256_after"] = a30.digest(args.executable)
        result["source_and_input_sha256_after"] = {
            str(p.relative_to(ROOT)): a30.digest(p) for p in [*source_paths, *original_paths]}
        result["source_inputs_unchanged_during_run"] = (
            result["source_and_input_sha256_after"] == identities)
        result["executable_unchanged_during_run"] = result["executable_sha256_after"] == a30.PIN
        result["output_sha256"] = {str(p.relative_to(ROOT)): a30.digest(p)
            for p in sorted(args.output.rglob("*")) if p.is_file()}
        a30.save_json(args.output / "result.json", result)
    if result["failure"]:
        print(result["failure"], file=sys.stderr)
        return 1
    a30.CASE.assertTrue(result["source_inputs_unchanged_during_run"])
    a30.CASE.assertTrue(result["executable_unchanged_during_run"])
    print(json.dumps({"native_processes": len(result["runs"]),
        "operator_assertions_completed": result["operator_assertions_completed"],
        "acknowledged_at_ms": result["observation"]["first_restored_acknowledgment"]["elapsed_ms"],
        "screenshot_at_ms": result["observation"]["screenshot"]["elapsed_ms"],
        "status_visual_review": "pending"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
