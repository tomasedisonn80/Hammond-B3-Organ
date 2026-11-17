#!/usr/bin/env python3
"""Starter controls through the real standalone's generic startup/Load path.

Requires matching HAMMOND_STANDALONE_EXECUTABLE and
HAMMOND_REGISTRATION_EXECUTABLE binaries. All writable inputs are private
copies; SDL audio/video are dummy and no MIDI device is selected. This is not
native LibraryModel/browser, physical-device, or accessibility acceptance.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import unittest

from test_standalone_app import assert_no_midi_input, reject_nonfinite, unique_object
from test_standalone_workflows import diagnostic_excerpt, replay, tabs, tap


REPOSITORY = Path(__file__).resolve().parents[3]
PACK = REPOSITORY / "data" / "registrations" / "starter-v1" / "entries"
RECIPE = "12 Manual Return"
CURRENT = "02 Warm Comp.b3performance"
DURATION_MS = 2700
LOAD_MS = 2200
PROCESS_TIMEOUT = 9.0

# Independent literal oracle from the reviewed recipe table, not the generator,
# manifest, application parser, serializer or diagnostics under examination.
SAVED_CONTROLS = {
    "manual_drawbars": [
        [[8, 0, 8, 0, 0, 0, 0, 0, 0], [8, 0, 8, 6, 0, 0, 0, 0, 0]],
        [[0, 0, 8, 4, 0, 0, 0, 0, 0], [0, 0, 8, 4, 4, 0, 0, 0, 0]],
    ],
    "selected_banks": [0, 1], "fixed_registrations": [8, 0],
    "preset_selections": [0, 11], "route_enabled": [False, True],
    "expression": 0.5, "pedal_drawbars": [4, 0],
    "percussion": {"enabled": True, "harmonic": 1, "volume": 1, "decay": 1},
}


def load_workflow() -> str:
    # At 1280x900 the published focus order has ten common controls, two
    # Upper EDIT buttons, twelve Upper presets, nine Upper drawbars, then the
    # Lower group and four percussion controls. These literal Tab counts do
    # not import layout/UiModel code or depend on raster samples.
    events = tabs(200, 24) + tap(750, "Return")  # Upper B: reconnect, clear fixed.
    events += tap(800, "Tab") + tap(850, "Home")  # Upper edited B first drawbar.
    # Existing tabs() uses 20 ms per stop: leave the full navigation interval.
    events += tabs(900, 36) + tap(1650, "End")  # Expression = 1.
    events += tabs(1700, 4, "shift") + tap(1800, "Return")  # Percussion Off.
    events += tabs(1850, 5) + tap(1970, "End")  # First pedal drawbar = 8.
    events += tap(LOAD_MS, "O", "ctrl")
    return replay(DURATION_MS, events)


class NativeStarterLoadAcceptance(unittest.TestCase):
    native_calls = 0
    materialize_calls = 0

    @classmethod
    def setUpClass(cls) -> None:
        cls.binaries: dict[str, Path] = {}
        cls.identities: dict[Path, str] = {}
        for key in ("HAMMOND_STANDALONE_EXECUTABLE", "HAMMOND_REGISTRATION_EXECUTABLE"):
            configured = os.environ.get(key, "")
            if not configured:
                raise RuntimeError(f"{key} is required; build both native targets first")
            path = Path(configured).resolve(strict=True)
            if not path.is_file() or not os.access(path, os.X_OK):
                raise RuntimeError(f"Required executable is not executable: {path}")
            cls.binaries[key] = path
            cls.identities[path] = hashlib.sha256(path.read_bytes()).hexdigest()
            print(f"{key} SHA-256: {cls.identities[path]}", flush=True)
        for name in (RECIPE + ".b3registration", RECIPE + ".b3performance", CURRENT):
            path = PACK / name
            cls.identities[path] = hashlib.sha256(path.read_bytes()).hexdigest()
            print(f"Starter input {name} SHA-256: {cls.identities[path]}", flush=True)

    @classmethod
    def tearDownClass(cls) -> None:
        print(f"Starter Load: {cls.native_calls} actual standalone processes; "
              f"{cls.materialize_calls} actual registration processes", flush=True)
        for path, expected in cls.identities.items():
            if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                raise AssertionError(f"Executable or source fixture changed during acceptance: {path}")

    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="hammond-starter-load-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.run_count = 0

    def run_load(self, source_path: Path, expected: dict) -> None:
        self.run_count += 1
        directory = self.root / f"native-{self.run_count}"
        directory.mkdir()
        state = directory / source_path.name
        shutil.copyfile(source_path, state)
        original = state.read_bytes()
        script = directory / "generic-load.b3ui"
        script_source = load_workflow()
        script.write_text(script_source, encoding="ascii", newline="\n")
        diagnostics = directory / "diagnostics.json"
        command = [str(self.binaries["HAMMOND_STANDALONE_EXECUTABLE"]),
                   "--state", str(state), "--input-script", str(script),
                   "--width", "1280", "--height", "900",
                   "--workspace", "play",
                   "--diagnostics", str(diagnostics)]
        environment = os.environ.copy()
        environment.update(SDL_AUDIODRIVER="dummy", SDL_VIDEODRIVER="dummy",
                           SDL_RENDER_DRIVER="software")
        type(self).native_calls += 1
        started = time.monotonic()
        try:
            process = subprocess.run(command, cwd=directory, env=environment,
                                     stdin=subprocess.DEVNULL, capture_output=True,
                                     text=True, errors="replace", timeout=PROCESS_TIMEOUT,
                                     check=False)
        except subprocess.TimeoutExpired as error:
            self.fail(f"Native Load exceeded {PROCESS_TIMEOUT}s: {error}\n"
                      + diagnostic_excerpt(diagnostics))
        elapsed = time.monotonic() - started
        self.assertEqual(process.returncode, 0,
                         f"{command!r}: {process.stdout}\n{process.stderr}\n"
                         + (diagnostic_excerpt(diagnostics) if process.returncode else ""))
        self.assertEqual(process.stderr, "")
        self.assertGreaterEqual(elapsed, DURATION_MS / 1000 - 0.04)
        self.assertTrue(diagnostics.is_file())
        data = json.loads(diagnostics.read_text(encoding="utf-8"),
                          object_pairs_hook=unique_object, parse_constant=reject_nonfinite)
        try:
            self.assert_load_diagnostics(data, expected, state, script_source)
        except AssertionError as error:
            self.fail(f"{source_path.name}: {error}\n{diagnostic_excerpt(data)}")
        self.assertEqual(state.read_bytes(), original, "Load and shutdown must not save implicitly")
        self.assertEqual(source_path.read_bytes(), original, "The copied source must remain unchanged")
        self.assertEqual(script.read_text(encoding="ascii"), script_source)
        self.assertEqual({path.name for path in directory.iterdir()},
                         {state.name, script.name, diagnostics.name})

    def assert_load_diagnostics(self, data: dict, expected: dict,
                                state: Path, script: str) -> None:
        self.assertEqual(data["schema_version"], 3)
        self.assertEqual(data["application"], "hammond_standalone")
        self.assertEqual(data["state_path"], str(state))
        self.assertEqual(data["errors"], {"count": 0, "last": ""})
        self.assertEqual(data["presentation"]["initial_workspace"], "play")
        self.assertEqual(data["presentation"]["initial_presentation"], "dimensional")
        assert_no_midi_input(self, data)
        runtime, audio, session = (data[key] for key in ("runtime", "audio", "session"))
        self.assertEqual((runtime["video_driver"], runtime["renderer"], audio["driver"]),
                         ("dummy", "software", "dummy"))
        self.assertEqual([runtime[key] for key in
                          ("window_width", "window_height", "drawable_width", "drawable_height")],
                         [1280, 900, 1280, 900])
        self.assertGreater(runtime["rendered_images"], 0)
        self.assertGreater(audio["callback_count"], 0)
        self.assertGreater(audio["rendered_frames"], 0)
        self.assertTrue(audio["open_before_shutdown"])
        self.assertTrue(audio["running_before_shutdown"])
        for field in ("render_failures", "format_failures", "overrange_failures",
                      "overrange_samples", "nonfinite_failures", "nonfinite_samples"):
            self.assertEqual(audio[field], 0, field)
        for field in ("recovery_count", "queue_overflows", "rejected_commands", "fault_flags"):
            self.assertEqual(session[field], 0, field)
        self.assertFalse(session["running_after_shutdown"])
        self.assertFalse(session["held_after_shutdown"])

        observed = data["replay"]
        for field in ("completed", "delivered", "passed", "final_acknowledged",
                      "snapshot_available_before_shutdown", "session_running_before_shutdown"):
            self.assertTrue(observed[field], field)
        for field in ("controls_pending_before_shutdown", "save_pending_before_shutdown",
                      "observations_truncated"):
            self.assertFalse(observed[field], field)
        self.assertEqual(observed["duration_ms"], DURATION_MS)
        event_count = len(script.splitlines()) - 2
        self.assertEqual(observed["scheduled_events"], event_count)
        self.assertEqual(observed["pushed_events"], event_count)
        self.assertEqual(observed["device_starts"], 1)
        self.assertEqual(observed["accepted_note_on_commands"], 0)
        self.assertEqual(observed["accepted_note_off_commands"], 0)
        # Shutdown may discard its one redundant scoped release. It must not
        # excuse any script command: the running endpoint is checked below.
        self.assertIn(session["discarded_commands"], (0, 1))
        endpoint = observed["before_shutdown"]
        self.assertEqual(data["controls"], expected)
        self.assertEqual(observed["desired_controls_before_shutdown"], expected)
        self.assertEqual(endpoint["controls"], expected)
        self.assertEqual(endpoint["manual_notes"], [[], []])
        self.assertEqual(endpoint["pedal_ids"], [])
        self.assertEqual(endpoint["resolved_sequence"], observed["last_submitted_sequence"])
        self.assertEqual(endpoint["last_applied_sequence"], observed["last_submitted_sequence"])

        altered = deepcopy(expected)
        altered.update(selected_banks=[1, 1], fixed_registrations=[0, 0],
                       preset_selections=[11, 11], route_enabled=[True, True],
                       expression=1, pedal_drawbars=[8, 0])
        altered["manual_drawbars"][0][1][0] = 0
        altered["percussion"]["enabled"] = False
        history = observed["observations"]
        self.assertTrue(any(item["controls"] == expected and item["elapsed_ms"] < 750
                            for item in history), "Startup must acknowledge the copied full state")
        acknowledged_edits = [item for item in history
                              if item["controls"] == altered and item["elapsed_ms"] < LOAD_MS
                              and item["resolved_sequence"] == item["last_applied_sequence"]
                              == item["last_submitted_sequence"]]
        self.assertTrue(acknowledged_edits,
                        "Live edits must be acknowledged before Load; startup alone is insufficient")
        self.assertGreater(endpoint["last_applied_sequence"],
                           acknowledged_edits[-1]["last_applied_sequence"])
        self.assertTrue(any(item["controls"] == expected and item["elapsed_ms"] >= LOAD_MS
                            and item["last_applied_sequence"] == observed["last_submitted_sequence"]
                            for item in history), "An applied Load observation is required before shutdown")

    def test_generic_load_restores_complete_payload_under_both_scope_suffixes(self) -> None:
        registration = PACK / (RECIPE + ".b3registration")
        performance = PACK / (RECIPE + ".b3performance")
        self.assertEqual(registration.read_bytes(), performance.read_bytes())
        for source in (registration, performance):
            with self.subTest(suffix=source.suffix):
                self.run_load(source, SAVED_CONTROLS)

    def test_materialized_scopes_keep_their_expression_when_generically_loaded(self) -> None:
        library = self.root / "private library"
        library.mkdir()
        originals = {}
        for suffix in (".b3registration", ".b3performance"):
            path = library / (RECIPE + suffix)
            shutil.copyfile(PACK / path.name, path)
            originals[path] = path.read_bytes()
        current = self.root / "supplied current.b3controls"
        shutil.copyfile(PACK / CURRENT, current)
        originals[current] = current.read_bytes()
        destination = self.root / "materialized"
        for scope, expression in (("registration", 0.625), ("performance", 0.5)):
            with self.subTest(scope=scope):
                name = "Current Expression" if scope == "registration" else "Saved Expression"
                command = [str(self.binaries["HAMMOND_REGISTRATION_EXECUTABLE"]),
                           "materialize", "--library", str(library),
                           "--key", RECIPE + ".b3" + scope,
                           "--destination", str(destination), "--name", name]
                if scope == "registration":
                    command += ["--current", str(current)]
                type(self).materialize_calls += 1
                process = subprocess.run(command, cwd=self.root, stdin=subprocess.DEVNULL,
                                         capture_output=True, timeout=15, check=False)
                self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
                self.assertEqual(process.stderr, b"")
                report = json.loads(process.stdout.decode("utf-8"),
                                    object_pairs_hook=unique_object, parse_constant=reject_nonfinite)
                self.assertEqual(report["schema"], "hammond-registration-cli-v1")
                self.assertEqual((report["command"], report["outcome"], report["code"]),
                                 ("materialize", "ok", "Saved"))
                self.assertIs(report["committed"], True)
                self.assertEqual(report["entry"]["scope"], scope)
                self.assertEqual(report["save"]["scope"], "performance")
                output = destination / (name + ".b3performance")
                original = originals[library / (RECIPE + ".b3" + scope)]
                self.assertEqual(original.count(b"expression 0.5\n"), 1)
                wanted = original.replace(b"expression 0.5\n", f"expression {expression}\n".encode("ascii"))
                self.assertEqual(output.read_bytes(), wanted,
                                 "Only the explicit materialization expression policy may change bytes")
                expected = deepcopy(SAVED_CONTROLS)
                expected["expression"] = expression
                self.run_load(output, expected)
        for path, original in originals.items():
            self.assertEqual(path.read_bytes(), original)
        self.assertEqual({path.name for path in destination.iterdir()},
                         {"Current Expression.b3performance", "Saved Expression.b3performance"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
