#!/usr/bin/env python3
"""Real application replay limits, ordering, capture and rejection preservation.

Requires HAMMOND_STANDALONE_EXECUTABLE. No production parser/layout/serializer
is imported. Dummy drivers qualify software event delivery only.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import stat
import struct
import subprocess
import tempfile
import time
import unittest

from test_standalone_app import assert_no_midi_input


TIMEOUT = 8.0
DEFAULT_CONTROLS = {
    "manual_drawbars": [
        [[0] * 9, [8, 8, 8, 0, 0, 0, 0, 0, 0]],
        [[0] * 9, [0, 0, 8, 0, 0, 0, 0, 0, 0]],
    ],
    "selected_banks": [1, 1], "fixed_registrations": [0, 0], "preset_selections": [11, 11], "route_enabled": [True, True], "expression": 1,
    "pedal_drawbars": [8, 0],
    "percussion": {"enabled": False, "harmonic": 0, "volume": 0, "decay": 0},
}


def script(events: list[tuple[int, str]], duration: int = 250) -> bytes:
    return (f"B3UIREPLAY1\nduration_ms {duration}\n" + "".join(
        f"{at} {action}\n" for at, action in events)).encode("ascii")


def unique_members(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate diagnostics member: {key}")
        result[key] = value
    return result


def invalid_number(value: str) -> None:
    raise ValueError(f"Non-JSON numeric token: {value}")


def inventory(root: Path) -> dict:
    """Do not follow symbolic directories; retain bytes and leaf identities."""
    result = {}

    def visit(directory: Path) -> None:
        with os.scandir(directory) as entries:
            for entry in entries:
                path = Path(entry.path)
                relative = path.relative_to(root).as_posix()
                status = path.lstat()
                identity = (status.st_mode, status.st_ino, status.st_nlink)
                if stat.S_ISLNK(status.st_mode):
                    result[relative] = ("link", identity, os.readlink(path))
                elif stat.S_ISDIR(status.st_mode):
                    result[relative] = ("directory", identity)
                    visit(path)
                elif stat.S_ISREG(status.st_mode):
                    result[relative] = ("file", identity, path.read_bytes())
                else:
                    result[relative] = ("special", identity)

    visit(root)
    return result


class ReplayBoundaryAcceptance(unittest.TestCase):
    invocations = 0
    setup_rejections = 0

    @classmethod
    def setUpClass(cls) -> None:
        configured = os.environ.get("HAMMOND_STANDALONE_EXECUTABLE", "")
        if not configured:
            raise RuntimeError("HAMMOND_STANDALONE_EXECUTABLE is required; build the app first")
        cls.executable = Path(configured).resolve(strict=True)
        if not cls.executable.is_file() or not os.access(cls.executable, os.X_OK):
            raise RuntimeError(f"Native executable is not executable: {cls.executable}")
        print("Replay boundary executable SHA-256: " +
              hashlib.sha256(cls.executable.read_bytes()).hexdigest(), flush=True)

    @classmethod
    def tearDownClass(cls) -> None:
        print(f"Actual replay boundary subprocesses: {cls.invocations}; "
              f"preserved setup rejections: {cls.setup_rejections}", flush=True)

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="hammond-replay-boundaries-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.sequence = 0

    def directory(self) -> Path:
        self.sequence += 1
        directory = self.root / f"case-{self.sequence}"
        directory.mkdir()
        return directory

    def execute(self, directory: Path, arguments: list[str]) -> tuple[subprocess.CompletedProcess, float]:
        self.__class__.invocations += 1
        environment = dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy")
        started = time.monotonic()
        try:
            process = subprocess.run([str(self.executable), *arguments], cwd=directory,
                                     env=environment, stdin=subprocess.DEVNULL, capture_output=True,
                                     text=True, errors="replace", timeout=TIMEOUT, check=False)
        except subprocess.TimeoutExpired as error:
            self.fail(f"Native replay exceeded its bounded process guard: {error}")
        return process, time.monotonic() - started

    def invoke(self, source: bytes, *, screenshot: bool = False, expected_exit: int = 0) -> tuple[dict, Path]:
        directory = self.directory()
        input_path, state_path = directory / "input notes Ω.b3ui", directory / "absent controls 音.b3controls"
        diagnostics_path, image_path = directory / "diagnostics.json", directory / "screen.bmp"
        input_path.write_bytes(source)
        arguments = ["--state", str(state_path), "--input-script", str(input_path),
                     "--diagnostics", str(diagnostics_path)]
        if screenshot:
            arguments += ["--screenshot", str(image_path)]
        process, elapsed = self.execute(directory, arguments)
        self.assertEqual(process.returncode, expected_exit, process.stdout + "\n" + process.stderr)
        self.assertEqual(process.stdout, "")
        self.assertEqual(input_path.read_bytes(), source)
        self.assertFalse(state_path.exists(), "Replay must not save automatically or process Save after Quit")
        self.assertTrue(diagnostics_path.is_file())
        data = json.loads(diagnostics_path.read_text(encoding="utf-8"),
                          object_pairs_hook=unique_members, parse_constant=invalid_number)
        self.assert_joined(data)
        if expected_exit == 0:
            self.assertEqual(process.stderr, "")
            self.assertEqual(data["errors"], {"count": 0, "last": ""})
            self.assert_success(data, source)
            duration = int(source.splitlines()[1].split()[1]) / 1000
            self.assertGreaterEqual(elapsed, duration - 0.04, "Replay exited before its declared duration")
        else:
            self.assertIn("interrupted", process.stderr)
            self.assertGreater(data["errors"]["count"], 0)
        expected = {input_path.name, diagnostics_path.name}
        if screenshot:
            expected.add(image_path.name)
        self.assertEqual({path.name for path in directory.iterdir()}, expected)
        return data, image_path

    def assert_joined(self, data: dict) -> None:
        self.assertEqual(data["schema_version"], 3)
        assert_no_midi_input(self, data)
        self.assertEqual(data["application"], "hammond_standalone")
        self.assertEqual(data["runtime"]["video_driver"], "dummy")
        self.assertGreater(data["runtime"]["rendered_images"], 0)
        audio, session = data["audio"], data["session"]
        self.assertEqual(audio["driver"], "dummy")
        self.assertTrue(audio["open_before_shutdown"])
        self.assertTrue(audio["running_before_shutdown"])
        self.assertGreater(audio["callback_count"], 0)
        self.assertEqual(audio["rendered_frames"], audio["callback_count"] * audio["buffer_frames"])
        self.assertEqual(audio["buffer_bytes"], audio["buffer_frames"] * 8)
        self.assertEqual(audio["sample_format"], audio["native_float32_format"])
        for key in ("render_failures", "format_failures", "overrange_failures", "overrange_samples",
                    "nonfinite_failures", "nonfinite_samples"):
            self.assertEqual(audio[key], 0, key)
        self.assertTrue(session["snapshot_available"])
        self.assertTrue(session["prepared"])
        self.assertFalse(session["running_after_shutdown"])
        self.assertFalse(session["held_after_shutdown"])
        self.assertEqual(session["frame_clock"], audio["rendered_frames"])
        self.assertTrue(math.isfinite(session["maximum_observed_peak"]))
        for key in ("recovery_count", "queue_overflows", "rejected_commands", "fault_flags"):
            self.assertEqual(session[key], 0, key)
        self.assertEqual(data["controls"], DEFAULT_CONTROLS)
        self.assertFalse(data["smoke"]["requested"])
        self.assertFalse(data["smoke"]["note_on_sent"])
        self.assertFalse(data["smoke"]["note_off_sent"])

    def assert_success(self, data: dict, source: bytes) -> None:
        replay = data["replay"]
        self.assertIs(type(replay["observation_capacity"]), int)
        self.assertEqual(replay["observation_capacity"], 512)
        for key in ("completed", "delivered", "passed", "final_acknowledged"):
            self.assertTrue(replay[key], key)
        self.assertFalse(replay["observations_truncated"])
        count = sum(bool(line.strip()) and not line.lstrip().startswith(b"#")
                    for line in source.splitlines()[2:])
        self.assertEqual(replay["scheduled_events"], count)
        self.assertEqual(replay["pushed_events"], count)
        self.assertEqual(replay["device_starts"], 1)
        self.assertLessEqual(data["session"]["discarded_commands"], 1,
                             "Only the redundant close cleanup may be discarded in these fixtures")
        before = replay["before_shutdown"]
        self.assertGreaterEqual(before["resolved_sequence"], replay["last_submitted_sequence"])
        self.assertGreaterEqual(before["last_applied_sequence"], replay["last_submitted_sequence"])
        self.assertEqual(before["controls"], DEFAULT_CONTROLS)
        self.assertTrue(replay["observations"])
        self.assertLessEqual(len(replay["observations"]), 512)
        self.assertEqual([item["elapsed_ms"] for item in replay["observations"]],
                         sorted(item["elapsed_ms"] for item in replay["observations"]))

    def assert_holds(self, data: dict, upper: list[int], lower: list[int], pedals: list[int]) -> None:
        before = data["replay"]["before_shutdown"]
        self.assertEqual(before["manual_notes"], [upper, lower])
        self.assertEqual(before["pedal_ids"], pedals)

    def test_maximum_resize_plan_drains_without_extending_grace(self) -> None:
        for alternating in (False, True):
            with self.subTest(alternating=alternating):
                events = [(0, "resize 1280 900" if alternating and index % 2 else "resize 960 700")
                          for index in range(256)]
                data, _ = self.invoke(script(events))
                size = (1280, 900) if alternating else (960, 700)
                self.assertEqual((data["runtime"]["window_width"], data["runtime"]["window_height"]), size)
                self.assert_holds(data, [], [], [])
                self.assertEqual(data["replay"]["accepted_note_on_commands"], 0)
                self.assertEqual(data["replay"]["accepted_note_off_commands"], 0)

    def test_zero_and_maximum_nonmutating_events_have_no_smoke_note(self) -> None:
        for count in (0, 256):
            with self.subTest(count=count):
                data, _ = self.invoke(script([(0, "key_up A none")] * count))
                self.assert_holds(data, [], [], [])
                self.assertEqual(data["replay"]["accepted_note_on_commands"], 0)
                self.assertEqual(data["replay"]["accepted_note_off_commands"], 0)

    def test_equal_time_actions_preserve_source_order(self) -> None:
        for events, held, off in ((["key_down A none 0", "key_up A none"], [], 1),
                                  (["key_up A none", "key_down A none 0"], [60], 0)):
            with self.subTest(events=events):
                data, _ = self.invoke(script([(150, item) for item in events], 450))
                self.assert_holds(data, held, [], [])
                self.assertEqual(data["replay"]["accepted_note_on_commands"], 1)
                self.assertEqual(data["replay"]["accepted_note_off_commands"], off)

    def test_tied_resizes_preserve_each_pointer_geometry_and_note_owner(self) -> None:
        # Independent literal points beyond each permanent preset rail:
        # (198,560) is Lower C2 at960x700; (214,580) is Upper C2 at1280x900.
        # Each tied resize marker must apply before its following pointer
        # events. Space retains the original Lower owner after Upper refocus.
        actions = ["resize 960 700", "mouse_down 198 560", "mouse_up 198 560",
                   "key_down Space none 0", "resize 1280 900",
                   "mouse_down 214 580", "mouse_up 214 580"]
        data, _ = self.invoke(script([(200, action) for action in actions], 550))
        self.assert_holds(data, [], [36], [])
        self.assertEqual(data["replay"]["accepted_note_on_commands"], 3)
        self.assertEqual(data["replay"]["accepted_note_off_commands"], 2)
        self.assertEqual((data["runtime"]["window_width"], data["runtime"]["window_height"]), (1280, 900))

    def test_held_completion_captures_before_joined_shutdown(self) -> None:
        data, image = self.invoke(script([(150, "key_down A none 0")], 500), screenshot=True)
        self.assert_holds(data, [60], [], [])
        self.assertEqual(data["replay"]["accepted_note_on_commands"], 1)
        self.assertEqual(data["replay"]["accepted_note_off_commands"], 0)
        self.assertGreater(data["session"]["maximum_observed_peak"], 0)
        self.assertTrue(data["runtime"]["screenshot_written"])
        self.assertTrue(data["runtime"]["screenshot_while_held"])
        pixels = image.read_bytes()
        self.assertEqual(pixels[:2], b"BM")
        self.assertEqual(struct.unpack_from("<I", pixels, 2)[0], len(pixels))
        self.assertGreaterEqual(struct.unpack_from("<I", pixels, 14)[0], 40)
        width, height = struct.unpack_from("<ii", pixels, 18)
        self.assertEqual((width, abs(height)), (1280, 900))
        offset = struct.unpack_from("<I", pixels, 10)[0]
        self.assertGreater(len(pixels) - offset, width * abs(height))

    def test_quit_interrupts_and_does_not_handle_later_save_or_note(self) -> None:
        events = [(150, "key_down A none 0"), (350, "quit"),
                  (350, "key_down S ctrl 0"), (350, "key_up S ctrl"),
                  (350, "key_down D none 0")]
        data, _ = self.invoke(script(events, 1200), expected_exit=1)
        self.assertFalse(data["replay"]["completed"])
        self.assertFalse(data["replay"]["passed"])
        self.assertFalse(data["replay"]["delivered"])
        self.assertEqual(data["replay"]["accepted_note_on_commands"], 1)
        self.assertEqual(data["replay"]["accepted_note_off_commands"], 0)

    def sentinels(self, directory: Path) -> dict[str, Path]:
        paths = {name: directory / name for name in ("input.b3ui", "state.b3controls", "image.bmp", "report.json")}
        paths["input.b3ui"].write_bytes(script([]))
        for name in ("state.b3controls", "image.bmp", "report.json"):
            paths[name].write_bytes(("preserve " + name + "\n").encode("ascii"))
        return paths

    def assert_rejected_preserved(self, directory: Path, paths: dict[str, Path], *, extra: list[str] | None = None,
                                  expected_exit: int = 1) -> None:
        before = inventory(directory)
        arguments = ["--input-script", str(paths["input.b3ui"]), "--state", str(paths["state.b3controls"]),
                     "--screenshot", str(paths["image.bmp"]), "--diagnostics", str(paths["report.json"])]
        process, _ = self.execute(directory, arguments + (extra or []))
        self.assertEqual(process.returncode, expected_exit, process.stdout + "\n" + process.stderr)
        self.assertEqual(process.stdout, "")
        self.assertTrue(process.stderr.strip())
        self.assertEqual(inventory(directory), before, "Rejected input changed the complete existing tree")
        self.__class__.setup_rejections += 1

    def test_input_aliases_never_overwrite_input_or_other_destinations(self) -> None:
        for kind in ("exact", "hardlink", "parent-symlink"):
            for destination in ("state.b3controls", "image.bmp", "report.json"):
                with self.subTest(kind=kind, destination=destination):
                    directory = self.directory()
                    paths = self.sentinels(directory)
                    if kind == "exact":
                        paths[destination] = paths["input.b3ui"]
                    elif kind == "hardlink":
                        alias = directory / "input-hardlink"
                        os.link(paths["input.b3ui"], alias)
                        paths[destination] = alias
                    else:
                        alias = directory / "input-parent-alias"
                        try:
                            alias.symlink_to(directory, target_is_directory=True)
                        except OSError as error:
                            if os.name == "nt":
                                self.skipTest(f"Windows symbolic-directory creation unavailable: {error}")
                            raise
                        paths[destination] = alias / "input.b3ui"
                    self.assert_rejected_preserved(directory, paths)

    def test_rejected_input_files_and_mixed_mode_preserve_sentinels(self) -> None:
        for case in ("missing", "malformed", "non-ascii", "too-many-events", "too-many-bytes", "directory",
                     "fifo", "symlink", "dangling-symlink", "mixed-mode"):
            with self.subTest(case=case):
                if case == "fifo" and not hasattr(os, "mkfifo"):
                    self.skipTest("FIFO creation is not supported on this platform")
                directory = self.directory()
                paths = self.sentinels(directory)
                source = paths["input.b3ui"]
                if case in ("missing", "directory", "fifo", "symlink", "dangling-symlink"):
                    source.unlink()
                if case == "malformed":
                    source.write_bytes(b"B3UIREPLAY2\nduration_ms 250\n")
                elif case == "non-ascii":
                    source.write_bytes(script([]) + b"#\xff\n")
                elif case == "too-many-events":
                    source.write_bytes(script([(0, "key_up A none")] * 257))
                elif case == "too-many-bytes":
                    source.write_bytes(script([]) + b"#" + b" " * (65536 - len(script([]))))
                elif case == "directory":
                    source.mkdir()
                    (source / "child").write_bytes(b"keep directory child")
                elif case == "fifo":
                    os.mkfifo(source)
                elif case in ("symlink", "dangling-symlink"):
                    target = directory / "script-target"
                    if case == "symlink":
                        target.write_bytes(script([]))
                    try:
                        source.symlink_to(target)
                    except OSError as error:
                        if os.name == "nt":
                            self.skipTest(f"Windows symbolic-file creation unavailable: {error}")
                        raise
                self.assert_rejected_preserved(directory, paths,
                    extra=["--smoke-ms", "250"] if case == "mixed-mode" else None,
                    expected_exit=2 if case == "mixed-mode" else 1)

    def test_maximum_byte_file_preserves_unicode_path_and_loads(self) -> None:
        prefix = script([])
        source = prefix + b"#" + b" " * (65536 - len(prefix) - 1)
        self.assertEqual(len(source), 65536)
        data, _ = self.invoke(source)
        self.assert_holds(data, [], [], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
