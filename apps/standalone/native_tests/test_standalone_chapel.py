#!/usr/bin/env python3
"""Actual C++ state-load/Save and SDL audition checks for documentary chapel rows.

The expected state bytes and row values are shared independent test fixtures,
not producer constants. Requires an actual built executable; never silently skips.
"""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_standalone_app import assert_no_midi_input

ROOT = Path(__file__).resolve().parents[3]
_spec = importlib.util.spec_from_file_location("chapel_independent_oracles", ROOT / "tests/test_chapel_controls.py")
if _spec is None or _spec.loader is None:
    raise RuntimeError("Independent chapel oracle file is required")
ORACLE = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ORACLE)


def unique_object(pairs):
    result = {}
    for name, value in pairs:
        if name in result:
            raise ValueError(f"Duplicate diagnostic member {name}")
        result[name] = value
    return result


def reject_nonfinite(value):
    raise ValueError(f"Non-JSON numeric token {value}")


def expected_controls(upper: str, lower: str, bank: str, expression: float) -> dict:
    zero = [0] * 9
    u = [int(digit) for digit in ORACLE.UPPER[ORACLE.KEYS.index(upper)]] if upper != "off" else zero
    l = [int(digit) for digit in ORACLE.LOWER[ORACLE.KEYS.index(lower)]] if lower != "off" else zero
    return {
        "manual_drawbars": [[u, zero] if bank == "A" else [zero, u],
                            [l, zero] if bank == "A" else [zero, l]],
        "selected_banks": [0 if bank == "A" else 1] * 2,
        "route_enabled": [upper != "off", lower != "off"],
        "expression": expression, "pedal_drawbars": [0, 0],
        "percussion": {"enabled": False, "harmonic": 0, "volume": 0, "decay": 0},
    }


def holds(snapshot: dict) -> tuple:
    return tuple(snapshot["manual_notes"][0]), tuple(snapshot["manual_notes"][1]), tuple(snapshot["pedal_ids"])


@contextmanager
def retain_diagnostics(path: Path, case: str):
    """Retain bounded per-process evidence before temporary-directory cleanup."""
    try:
        yield
    except Exception as error:
        limit = 65536
        try:
            with path.open("rb") as source:
                raw = source.read(limit + 1)
            evidence = raw[:limit].decode("utf-8", errors="replace")
            if len(raw) > limit:
                evidence += "\n[truncated at 65536 bytes]"
        except OSError as read_error:
            evidence = f"Diagnostics unavailable: {read_error}"
        raise AssertionError(f"{case}: {type(error).__name__}: {error}\nCopied diagnostics:\n{evidence}") from error


class NativeChapelAcceptance(unittest.TestCase):
    invocations = 0
    exporter_invocations = 0

    @classmethod
    def setUpClass(cls) -> None:
        configured = os.environ.get("HAMMOND_STANDALONE_EXECUTABLE", "")
        if not configured:
            raise RuntimeError("HAMMOND_STANDALONE_EXECUTABLE is required; build the actual app first")
        cls.executable = Path(configured).resolve(strict=True)
        if not cls.executable.is_file() or not os.access(cls.executable, os.X_OK):
            raise RuntimeError(f"Native executable is unavailable: {cls.executable}")
        cls.binary_hash = hashlib.sha256(cls.executable.read_bytes()).hexdigest()
        cls.sources = {path: path.read_bytes() for path in
                       (ORACLE.TOOL, ORACLE.COMPILER, ORACLE.AUTHORING, *ORACLE.REVIEWS,
                        ROOT / "tests/test_chapel_controls.py", ROOT / "apps/standalone/main.cpp")}
        with tempfile.TemporaryDirectory(prefix="native-chapel-catalog-") as temporary:
            cls.catalog_bytes = ORACLE.make_catalog(Path(temporary) / "catalog.json")
        print(f"Native chapel executable SHA-256: {cls.binary_hash}", flush=True)
        print(f"Native chapel main SHA-256: {hashlib.sha256(cls.sources[ROOT / 'apps/standalone/main.cpp']).hexdigest()}", flush=True)

    @classmethod
    def tearDownClass(cls) -> None:
        if hashlib.sha256(cls.executable.read_bytes()).hexdigest() != cls.binary_hash:
            raise AssertionError("The native executable changed during this acceptance run")
        for path, value in cls.sources.items():
            if path.read_bytes() != value:
                raise AssertionError(f"Native acceptance source changed: {path}")
        print(f"Native chapel acceptance: {cls.exporter_invocations} exported states, "
              f"{cls.invocations} actual SDL application invocations", flush=True)

    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="native-chapel-acceptance-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def run_audition(self, upper: str, lower: str, bank: str, *, expression: str = "0.75",
                     serialized: str = "0.75", numeric: float = 0.75,
                     load_expression: str | None = None, held_endpoint: bool = False) -> None:
        directory = self.root / f"case-{self.invocations}"
        directory.mkdir()
        catalog = directory / "catalog.json"
        state = directory / "chapel audition 音.b3controls"
        script = directory / "keyboard.b3ui"
        diagnostics = directory / "observations.json"
        catalog.write_bytes(self.catalog_bytes)
        self.__class__.exporter_invocations += 1
        exported = subprocess.run([sys.executable, str(ORACLE.TOOL), "--catalog", str(catalog),
            "--output", str(state), "--upper", upper, "--lower", lower, "--bank", bank,
            "--expression", expression], capture_output=True, timeout=5,
            env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"), check=False)
        self.assertEqual((exported.returncode, exported.stdout, exported.stderr), (0, b"", b""))
        canonical = ORACLE.expected_state(upper, lower, bank, serialized)
        self.assertEqual(state.read_bytes(), canonical)
        if load_expression is not None:
            # Exercise a valid C++ parser input whose later byte change proves
            # Save really serialized the controls, beyond preserving the file.
            noncanonical = ORACLE.expected_state(upper, lower, bank, load_expression)
            self.assertNotEqual(noncanonical, canonical)
            state.write_bytes(noncanonical)
        pair = upper != "off" and lower != "off"
        self.assertFalse(held_endpoint and not pair)
        if pair:
            events = ("50 key_down F1 none 0\n60 key_up F1 none\n"
                      "150 key_down A none 0\n220 key_down F2 none 0\n230 key_up F2 none\n"
                      "300 key_down D none 0\n400 key_down S ctrl 0\n410 key_up S ctrl\n"
                      "600 key_up D none\n")
            if not held_endpoint:
                events += "700 key_up A none\n"
            duration = 650 if held_endpoint else 900
            prefixes = [((), (), ()), ((60,), (), ()), ((60,), (64,), ()), ((60,), (), ())]
            if not held_endpoint:
                prefixes.append(((), (), ()))
            note_count = 2
        else:
            target = "F1" if upper != "off" else "F2"
            events = (f"50 key_down {target} none 0\n60 key_up {target} none\n"
                      "150 key_down A none 0\n300 key_down S ctrl 0\n310 key_up S ctrl\n"
                      "500 key_up A none\n")
            duration = 700
            playing = ((60,), (), ()) if upper != "off" else ((), (60,), ())
            prefixes = [((), (), ()), playing, ((), (), ())]
            note_count = 1
        off_count = note_count - int(held_endpoint)
        source = f"B3UIREPLAY1\nduration_ms {duration}\n" + events
        script.write_text(source, encoding="ascii", newline="\n")
        self.__class__.invocations += 1
        case = f"Upper={upper}, Lower={lower}, bank={bank}, expression={expression}, held_endpoint={held_endpoint}"
        with retain_diagnostics(diagnostics, case):
            process = subprocess.run([str(self.executable), "--state", str(state),
                "--input-script", str(script), "--diagnostics", str(diagnostics)],
                cwd=directory, env=dict(os.environ, SDL_AUDIODRIVER="dummy", SDL_VIDEODRIVER="dummy"),
                stdin=subprocess.DEVNULL, capture_output=True, timeout=8, check=False)
            self.assertEqual(process.returncode, 0, process.stdout.decode(errors="replace") + process.stderr.decode(errors="replace"))
            self.assertEqual(process.stderr, b"")
            data = json.loads(diagnostics.read_text(encoding="utf-8"), object_pairs_hook=unique_object,
                              parse_constant=reject_nonfinite)
            expected = expected_controls(upper, lower, bank, numeric)
            self.assertEqual(data["schema_version"], 2)
            assert_no_midi_input(self, data)
            self.assertEqual(data["controls"], expected)
            self.assertEqual(data["errors"], {"count": 0, "last": ""})
            self.assertEqual(data["state_path"], str(state))
            self.assertEqual(data["status"], "Saved controls to " + str(state))
            self.assertEqual(data["runtime"]["video_driver"], "dummy")
            self.assertEqual(data["runtime"]["sdl_version"], "2.32.10")
            audio, session, replay = data["audio"], data["session"], data["replay"]
            self.assertIs(type(replay["observation_capacity"]), int)
            self.assertEqual(replay["observation_capacity"], 512)
            self.assertEqual(audio["driver"], "dummy")
            self.assertTrue(audio["open_before_shutdown"] and audio["running_before_shutdown"])
            self.assertGreater(audio["callback_count"], 0)
            self.assertGreater(audio["rendered_frames"], 0)
            for name in ("render_failures", "format_failures", "overrange_failures", "overrange_samples",
                         "nonfinite_failures", "nonfinite_samples"):
                self.assertEqual(audio[name], 0, name)
            self.assertTrue(session["snapshot_available"] and session["prepared"])
            self.assertFalse(session["running_after_shutdown"] or session["held_after_shutdown"])
            for name in ("recovery_count", "queue_overflows", "rejected_commands", "fault_flags"):
                self.assertEqual(session[name], 0, name)
            self.assertLessEqual(session["discarded_commands"], 1)  # At most one ordinary close cleanup.
            peak = session["maximum_observed_peak"]
            self.assertTrue(math.isfinite(peak))
            if numeric == 0:
                self.assertEqual(peak, 0)
            else:
                self.assertGreater(peak, 0)
            self.assertTrue(replay["completed"] and replay["delivered"] and replay["passed"] and replay["final_acknowledged"])
            self.assertFalse(replay["observations_truncated"])
            self.assertEqual(replay["device_starts"], 1)
            self.assertEqual(replay["scheduled_events"], len(events.splitlines()))
            self.assertEqual(replay["pushed_events"], len(events.splitlines()))
            self.assertEqual(replay["accepted_note_on_commands"], note_count)
            self.assertEqual(replay["accepted_note_off_commands"], off_count)
            self.assertEqual(replay["before_shutdown"]["controls"], expected)
            self.assertEqual(replay["before_shutdown"]["resolved_sequence"], replay["last_submitted_sequence"])
            self.assertEqual(replay["before_shutdown"]["last_applied_sequence"], replay["last_submitted_sequence"])
            self.assertEqual(holds(replay["before_shutdown"]), prefixes[-1])
            self.assertFalse(data["smoke"]["requested"] or data["smoke"]["note_on_sent"])
            # Ctrl+S traverses actual C++ serialization while a note is held. Its
            # complete canonical bytes must equal the independent grammar fixture.
            self.assertEqual(state.read_bytes(), canonical)
            self.assertEqual(catalog.read_bytes(), self.catalog_bytes)
            self.assertEqual(script.read_text(encoding="ascii"), source)
            self.assertEqual({p.name for p in directory.iterdir()},
                             {catalog.name, state.name, script.name, diagnostics.name})

            # The UI samples coherent snapshots, not every callback transition.
            # Every sampled state must match its literal accepted-command prefix.
            # The separate held endpoint makes Upper-after-Lower-release mandatory
            # without requiring a sample in the original 100 ms release interval.
            final_sequence = replay["last_submitted_sequence"]
            self.assertIs(type(final_sequence), int)
            startup_sequence = final_sequence - note_count - off_count
            self.assertGreaterEqual(startup_sequence, 1)
            previous = 0
            for observation in [*replay["observations"], replay["before_shutdown"]]:
                sequence = observation["last_applied_sequence"]
                self.assertIs(type(sequence), int)
                self.assertIn(sequence, range(1, final_sequence + 1))
                self.assertGreaterEqual(sequence, previous)
                self.assertEqual(observation["resolved_sequence"], sequence)
                submitted = observation.get("last_submitted_sequence", final_sequence)
                self.assertIs(type(submitted), int)
                self.assertLessEqual(sequence, submitted)
                self.assertLessEqual(submitted, final_sequence)
                if "elapsed_ms" in observation and observation["elapsed_ms"] < 150:
                    self.assertEqual(submitted, startup_sequence)
                prefix = max(0, sequence - startup_sequence)
                self.assertEqual(observation["controls"], expected)
                self.assertEqual(holds(observation), prefixes[prefix])
                previous = sequence
            self.assertEqual(previous, final_sequence)

    def test_all_eighteen_documentary_rows_load_play_and_resave(self) -> None:
        for manual in ("upper", "lower"):
            for index, key in enumerate(ORACLE.KEYS):
                bank = "A" if (index + (manual == "lower")) % 2 == 0 else "B"
                with self.subTest(manual=manual, key=key, bank=bank):
                    self.run_audition(key if manual == "upper" else "off",
                                      key if manual == "lower" else "off", bank)

    def test_paired_banks_and_binary64_expression_serialization(self) -> None:
        for held_endpoint in (False, True):
            with self.subTest(held_endpoint=held_endpoint, expression="0.1"):
                self.run_audition("A", "C#", "B", expression="0.1", serialized="0.10000000000000001",
                                  numeric=0.1, load_expression="0.1", held_endpoint=held_endpoint)
            with self.subTest(held_endpoint=held_endpoint, expression="0"):
                self.run_audition("D#", "G", "A", expression="0", serialized="0", numeric=0.0,
                                  held_endpoint=held_endpoint)


if __name__ == "__main__":
    unittest.main()
