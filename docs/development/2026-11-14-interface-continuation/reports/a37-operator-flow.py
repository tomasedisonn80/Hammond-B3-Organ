#!/usr/bin/env python3
"""Two bounded final operator observations of a released, digest-pinned app.

Reuses A30's strict native schema/lifecycle runner and literal control fixture.
The two actual PNGs require separate visual review; no production layout or
renderer supplies an expectation oracle. This is not a new mandatory test suite.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
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
    parser.add_argument("--source-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.executable = args.executable.resolve(strict=True)
    args.source_report = args.source_report.resolve(strict=True)
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=False)
    a30.PIN = args.expected_sha256
    a30.CASE.assertEqual(a30.digest(args.executable), a30.PIN)
    build = json.loads(args.source_report.read_text())
    a30.CASE.assertEqual(build["executable"]["sha256"], a30.PIN)
    a30.CASE.assertEqual(build["returncode"], 0)
    a30.CASE.assertTrue(build["source_unchanged_during_build"])
    build_sources = build["source_sha256_after_build"]
    a30.CASE.assertEqual({p: a30.digest(ROOT / p) for p in build_sources}, build_sources)
    paths = [Path(__file__).resolve(), REPORTS / "a30-operator-journey.py", args.source_report,
             ROOT / "docs/INTERFACE_RUNBOOK.md", ROOT / "docs/STANDALONE_INPUT_REPLAY.md",
             *[ROOT / "apps/standalone/native_tests" / name for name in (
                 "test_standalone_app.py", "test_standalone_midi_replay.py",
                 "test_standalone_workflows.py", "test_standalone_workspace_replay.py")]]
    input_hashes = {str(p.relative_to(ROOT)): a30.digest(p) for p in paths}
    result = {
        "agent": "A37", "kind": "two bounded final native operator cases",
        "published_head_at_run": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "qualification_scope": "A34+A36 working source, independently matched to all 327 A36 build inputs; published HEAD alone does not identify these edits",
        "command": [sys.executable, *sys.argv], "cwd": str(Path.cwd()),
        "executable": str(args.executable), "executable_sha256_before": a30.PIN,
        "source_qualification_report": str(args.source_report.relative_to(ROOT)),
        "source_qualification_report_sha256": a30.digest(args.source_report),
        "build_source_count": len(build_sources), "all_build_sources_match_before": True,
        "toolchain": build["toolchain"], "configuration": build["configuration"],
        "python": platform.python_version(), "pillow": a30.pillow_version,
        "input_sha256_before": input_hashes, "runs": [], "checks": [],
        "visual_review": "pending", "failure": None, "operator_assertions_completed": False,
    }
    try:
        expected = deepcopy(a30.workflow.FIXED_CONTROLS)
        expected["manual_drawbars"][0][0][0] = 8
        sounding_b = deepcopy(expected)
        sounding_b["selected_banks"][0] = 1
        sounding_b["fixed_registrations"][0] = 0
        sounding_b["preset_selections"][0] = 11
        saved = a30.workflow.FIXED_STATE.replace(
            b"bank A 0 1 2 3 4 5 6 7 8\n", b"bank A 8 1 2 3 4 5 6 7 8\n", 1)

        # Follow the guide's held A -> Service -> Flat -> Play sequence, visit
        # Rotary, then edit a retained bank while the fixed route stays active.
        events = [(200, "key_down A none 0")] + a30.tap(350, "F6") + a30.tap(520, "F7")
        events += a30.tap(700, "F5") + a30.tap(880, "F4") + a30.tap(1040, "F7")
        events += a30.click(1180, 58, 508) + a30.tabs(1300, 14) + a30.tap(1650, "End")
        events += a30.tap(1850, "S", "ctrl") + a30.click(2060, 165, 590)
        events += a30.click(2250, 130, 508) + a30.tap(2460, "O", "ctrl")
        events += a30.tap(2660, "F7") + [(2850, "resize 960 700")]
        events += a30.tap(3060, "F6") + [(3300, "key_up A none")]
        run = a30.invoke(args, result, "01-navigation-edit-save-load", 3550, events,
                         state=a30.workflow.FIXED_STATE, final_size=(960, 700), capture=True)
        a30.controls(run, [a30.workflow.FIXED_CONTROLS, expected, sounding_b, expected])
        a30.notes(run, [a30.EMPTY, a30.UPPER_A, a30.EMPTY], 1, 1)
        a30.command_delta(run.diagnostics, 5)
        a30.CASE.assertEqual(run.saved_bytes, saved)
        a30.CASE.assertEqual(run.diagnostics["replay"]["device_starts"], 1)
        a30.views(run.diagnostics, [
            ("play", "dimensional", "none", 1280, 900),
            ("service", "dimensional", "none", 1280, 900),
            ("service", "flat", "none", 1280, 900),
            ("rotary", "flat", "none", 1280, 900),
            ("play", "flat", "none", 1280, 900),
            ("play", "dimensional", "none", 1280, 900),
            ("play", "flat", "none", 1280, 900),
            ("play", "flat", "none", 960, 700),
            ("service", "flat", "none", 960, 700)])
        observations = run.diagnostics["replay"]["observations"]
        a30.CASE.assertTrue(all(frame["controls"] == a30.workflow.FIXED_CONTROLS
                              for frame in observations if frame["elapsed_ms"] < 1600))
        restored = [frame for frame in observations if frame["elapsed_ms"] >= 2460
                    and frame["controls"] == expected
                    and frame["last_applied_sequence"] == frame["last_submitted_sequence"] == frame["resolved_sequence"]]
        a30.CASE.assertTrue(restored)
        a30.CASE.assertEqual(restored[0]["manual_notes"], [[60], []])
        capture = run.diagnostics["presentation"]["screenshot"]
        a30.CASE.assertEqual(capture["inspection"]["snapshot_state"], "current")
        a30.CASE.assertFalse(capture["inspection"]["controls_pending"])
        a30.CASE.assertGreater(capture["elapsed_ms"], restored[0]["elapsed_ms"])
        a30.CASE.assertLess(capture["elapsed_ms"], 2460 + 6000)
        result["load_observation"] = {
            "requested_at_ms": 2460, "first_restored_acknowledgment": restored[0],
            "screenshot": capture, "expected_visible_notice": "Loaded saved controls.",
            "notice_requires_separate_visual_review": True,
            "exact_canonical_saved_sha256": hashlib.sha256(saved).hexdigest(),
        }
        result["checks"].append("Held note 60 survives workspace/Flat navigation, retained-bank edit, explicit preset selection and live Load until its original release; one audio lifecycle.")
        result["checks"].append("Only Upper A drawbar 1 changes 0->8 while Fixed F# remains sounding; preset B deliberately changes the route; canonical Save and live Load restore exact controls.")

        # A minimal next launch verifies unchanged saved bytes and the semantic
        # difference between keyboard focus D# and still-applied Fixed F#.
        events = a30.tabs(100, 16) + [(500, "key_down A none 0")]
        events += a30.tap(650, "F6") + a30.tap(800, "F5") + a30.tap(950, "F4")
        events += [(1100, "key_up A none")]
        focus = a30.invoke(args, result, "02-minimum-focused-dsharp", 1400, events, state=saved,
                           extra=["--width", "960", "--height", "700", "--flat"],
                           final_size=(960, 700), capture=True)
        a30.controls(focus, [expected])
        a30.notes(focus, [a30.EMPTY, a30.UPPER_A, a30.EMPTY], 1, 1)
        a30.command_delta(focus.diagnostics, 2)
        a30.CASE.assertEqual(focus.saved_bytes, saved)
        a30.CASE.assertEqual(focus.diagnostics["replay"]["device_starts"], 1)
        a30.views(focus.diagnostics, [(w, "flat", "none", 960, 700)
                                    for w in ("play", "service", "rotary", "play")])
        a30.CASE.assertEqual(focus.diagnostics["controls"]["preset_selections"][0], 6)
        a30.CASE.assertEqual(focus.diagnostics["presentation"]["screenshot"]["inspection"]["snapshot_state"], "current")
        a30.CASE.assertFalse(focus.diagnostics["presentation"]["screenshot"]["inspection"]["controls_pending"])
        result["checks"].append("Minimum Flat launch restores exact saved controls; focusing D# and returning from Service/Rotary do not select it or rewrite state; the second PNG requires inspection of restored focus and full caption.")
        result["operator_assertions_completed"] = True
    except Exception:
        result["failure"] = traceback.format_exc()
        (args.output / "assertion-failure.txt").write_text(result["failure"])
    finally:
        result["executable_sha256_after"] = a30.digest(args.executable)
        result["executable_unchanged"] = result["executable_sha256_after"] == a30.PIN
        result["all_build_sources_match_after"] = {p: a30.digest(ROOT / p) for p in build_sources} == build_sources
        result["input_sha256_after"] = {str(p.relative_to(ROOT)): a30.digest(p) for p in paths}
        result["inputs_unchanged"] = result["input_sha256_after"] == input_hashes
        result["native_processes"] = len(result["runs"])
        result["native_successes"] = sum(run.get("returncode") == 0 for run in result["runs"])
        result["native_failures_preserved"] = sum(run.get("returncode") != 0 for run in result["runs"])
        result["output_sha256"] = {str(p.relative_to(ROOT)): a30.digest(p)
                                   for p in sorted(args.output.rglob("*")) if p.is_file()}
        result["limits"] = [
            "Dummy SDL software renderer; no physical audio/MIDI or display/DPI qualification",
            "MIDI modal not opened; prior A30 ALSA discovery failure remains separate",
            "No persistent native pointer capture; A42 owns that gate",
            "Wall-clock replay is not sample-accurate automation or a callback deadline test",
            "No repeated PCM/model/raster matrix, native accessibility or literal reference equality claim",
        ]
        a30.save_json(args.output / "result.json", result)
    print(json.dumps({key: result[key] for key in (
        "native_processes", "native_successes", "native_failures_preserved",
        "operator_assertions_completed", "executable_unchanged", "all_build_sources_match_after",
        "inputs_unchanged", "visual_review", "failure")}, indent=2))
    return 0 if result["failure"] is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
