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


def applied_load_chain(history: list[dict], expected: dict, altered: dict,
                       final_sequence: int) -> tuple[dict, dict, dict] | None:
    """Find copied startup/edit/Load states in their actual observation order.

    Replay times make input eligible for delivery; they do not timestamp an
    audio callback or promise when its snapshot will be copied. A genuine
    applied edit can therefore be observed while the later Load is pending.
    See docs/reviews/STARTER_LOAD_OBSERVATION_DIAGNOSIS.md for the admission.
    """
    if not history or final_sequence <= 0:
        return None
    ordered_fields = ("elapsed_ms", "last_applied_sequence", "resolved_sequence",
                      "last_submitted_sequence")
    for index, item in enumerate(history):
        if any(item[field] < 0 for field in ordered_fields):
            return None
        if not (item["last_applied_sequence"] <= item["resolved_sequence"]
                <= item["last_submitted_sequence"] <= final_sequence):
            return None
        if index:
            previous = history[index - 1]
            if any(item[field] < previous[field] for field in ordered_fields):
                return None
            if (item["last_applied_sequence"] == previous["last_applied_sequence"]
                    and item["controls"] != previous["controls"]):
                return None

    def applied(item: dict) -> bool:
        return 0 < item["last_applied_sequence"] == item["resolved_sequence"]

    startup = next(((index, item) for index, item in enumerate(history)
                    if item["controls"] == expected and item["elapsed_ms"] < 750
                    and applied(item)), None)
    restored = next(((index, item) for index, item in enumerate(history)
                     if item["controls"] == expected and item["elapsed_ms"] >= LOAD_MS
                     and applied(item) and item["last_applied_sequence"] == final_sequence), None)
    if startup is None or restored is None or startup[0] >= restored[0]:
        return None
    edited = next((item for item in history[startup[0] + 1:restored[0]]
                   if item["controls"] == altered and applied(item)
                   and startup[1]["last_applied_sequence"] < item["last_applied_sequence"]
                   < restored[1]["last_applied_sequence"]), None)
    if edited is None:
        return None
    return startup[1], edited, restored[1]


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
        chain = applied_load_chain(history, expected, altered, observed["last_submitted_sequence"])
        self.assertIsNotNone(chain,
                             "Complete copied startup, applied edits and applied Load must occur "
                             "in chronological and strictly advancing applied-sequence order")
        self.assertGreater(endpoint["last_applied_sequence"],
                           chain[1]["last_applied_sequence"])

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


class LoadObservationOrderTests(unittest.TestCase):
    """Pure oracle checks; these never construct or run a native process."""

    def setUp(self) -> None:
        self.altered = deepcopy(SAVED_CONTROLS)
        self.altered.update(selected_banks=[1, 1], fixed_registrations=[0, 0],
                            preset_selections=[11, 11], route_enabled=[True, True],
                            expression=1, pedal_drawbars=[8, 0])
        self.altered["manual_drawbars"][0][1][0] = 0
        self.altered["percussion"]["enabled"] = False
        self.history = [
            {"elapsed_ms": 72, "last_applied_sequence": 1, "resolved_sequence": 1,
             "last_submitted_sequence": 1, "controls": deepcopy(SAVED_CONTROLS)},
            {"elapsed_ms": 2255, "last_applied_sequence": 6, "resolved_sequence": 6,
             "last_submitted_sequence": 7, "controls": deepcopy(self.altered)},
            {"elapsed_ms": 2383, "last_applied_sequence": 7, "resolved_sequence": 7,
             "last_submitted_sequence": 7, "controls": deepcopy(SAVED_CONTROLS)},
        ]

    def chain(self, history: list[dict]) -> tuple[dict, dict, dict] | None:
        return applied_load_chain(history, SAVED_CONTROLS, self.altered, 7)

    def test_accepts_complete_applied_edits_with_or_without_pending_load(self) -> None:
        for elapsed, submitted in ((2100, 6), (2255, 7), (2201, 7)):
            with self.subTest(elapsed=elapsed, submitted=submitted):
                history = deepcopy(self.history)
                history[1].update(elapsed_ms=elapsed, last_submitted_sequence=submitted)
                self.assertIsNotNone(self.chain(history))
        history = deepcopy(self.history)
        history[1]["elapsed_ms"] = history[2]["elapsed_ms"] = 2201
        self.assertIsNotNone(self.chain(history), "Equal times preserve recorded order")
        history = deepcopy(self.history)
        history[1].update(last_applied_sequence=3, resolved_sequence=3)
        self.assertIsNotNone(self.chain(history), "Strict advances do not require adjacent sequences")

    def test_rejects_missing_or_reordered_copied_states(self) -> None:
        for indices in ((), (0,), (2,), (0, 2), (0, 1), (1, 2), (1, 0, 2), (0, 2, 1)):
            with self.subTest(indices=indices):
                self.assertIsNone(self.chain([self.history[index] for index in indices]))
        history = deepcopy(self.history)
        history[1]["desired_controls"] = history[1]["controls"]
        history[1]["controls"] = deepcopy(SAVED_CONTROLS)
        self.assertIsNone(self.chain(history), "Desired edits cannot replace copied edits")

    def test_rejects_invalid_or_nonadvancing_sequences(self) -> None:
        changes = (
            (0, {"last_applied_sequence": 0, "resolved_sequence": 0}),
            (1, {"last_applied_sequence": 1, "resolved_sequence": 1}),
            (2, {"last_applied_sequence": 6, "resolved_sequence": 6}),
            (1, {"resolved_sequence": 7}),
            (1, {"resolved_sequence": 5}),
            (1, {"last_submitted_sequence": 5}),
            (1, {"last_submitted_sequence": 8}),
            (0, {"last_applied_sequence": -1}),
            (0, {"resolved_sequence": -1}),
            (0, {"last_submitted_sequence": -1}),
            (2, {"last_submitted_sequence": 6}),
        )
        for index, change in changes:
            with self.subTest(index=index, change=change):
                history = deepcopy(self.history)
                history[index].update(change)
                self.assertIsNone(self.chain(history))
        # All individual records are locally ordered, but resolved/submitted
        # progress cannot move backwards between otherwise valid chain states.
        for field in ("resolved_sequence", "last_submitted_sequence"):
            with self.subTest(regression=field):
                history = deepcopy(self.history)
                intervening = deepcopy(history[0])
                intervening.update(elapsed_ms=100, last_submitted_sequence=7)
                intervening[field] = 7
                history.insert(1, intervening)
                if field == "last_submitted_sequence":
                    history[2][field] = 6
                self.assertIsNone(self.chain(history))
        self.assertIsNone(applied_load_chain(self.history, SAVED_CONTROLS, self.altered, 8),
                          "An otherwise coherent restoration must reach the actual final sequence")

    def test_rejects_wrong_or_incomplete_full_controls(self) -> None:
        for stage in range(3):
            for field in ("expression", "manual_drawbars", "percussion", "selected_banks"):
                with self.subTest(stage=stage, field=field):
                    history = deepcopy(self.history)
                    controls = history[stage]["controls"]
                    if field == "expression":
                        controls[field] = 0.625
                    elif field == "manual_drawbars":
                        controls[field][0][1][0] = 4
                    elif field == "percussion":
                        controls[field]["enabled"] = not controls[field]["enabled"]
                    else:
                        del controls[field]
                    self.assertIsNone(self.chain(history))

    def test_rejects_backward_times_and_preserves_existing_time_checks(self) -> None:
        for index, elapsed in ((0, -1), (0, 750), (1, 71), (2, 2200), (2, 2199)):
            with self.subTest(index=index, elapsed=elapsed):
                history = deepcopy(self.history)
                history[index]["elapsed_ms"] = elapsed
                self.assertIsNone(self.chain(history))
        history = deepcopy(self.history)
        history[1]["elapsed_ms"] = 2100
        history[2]["elapsed_ms"] = 2199
        self.assertIsNone(self.chain(history), "Restoration retains its 2200 ms lower bound")

    def test_rejects_control_changes_at_unchanged_or_restored_sequence(self) -> None:
        for insertion, copied_from in ((1, 0), (2, 1), (3, 2)):
            with self.subTest(insertion=insertion):
                history = deepcopy(self.history)
                changed = deepcopy(history[copied_from])
                changed["controls"] = deepcopy(self.altered if copied_from != 1 else SAVED_CONTROLS)
                history.insert(insertion, changed)
                self.assertIsNone(self.chain(history))
        history = deepcopy(self.history)
        late_edit = deepcopy(history[1])
        late_edit["elapsed_ms"] = 2400
        history.append(late_edit)
        self.assertIsNone(self.chain(history), "An edit after restoration cannot supply the chain")


if __name__ == "__main__":
    unittest.main(verbosity=2)
