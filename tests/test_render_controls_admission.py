#!/usr/bin/env python3
"""Independent remaining saved-control renderer acceptance.

Literal fixed rows derive from the retained page-122 transcription in
PresetTestOracle.h, not the production catalog or a state parser. This suite
adds initial restoration, changing-state provenance, and observed filesystem
ordering to test_render_controls.py; it does not repeat its rate/block sweep.
Linux inotify checks are explicitly platform limited. Missing executable/profile
inputs fail. CTest may provide HAMMOND_RENDER_EXECUTABLE/HAMMOND_TEST_PROFILE.
"""

import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import select
import signal
import stat
import struct
import subprocess
import sys
import tempfile
import time
import unittest


ROOT = Path(os.environ.get("HAMMOND_SOURCE_DIR", Path(__file__).resolve().parents[1]))
RENDERER_OVERRIDE = None
PROFILE_OVERRIDE = None
CATALOG = (
    "registration_catalog atlas-chapel-nominal-v1 sha256 "
    "c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf\n"
)
KEYS = ("C#", "D", "D#", "E", "F", "F#", "G", "G#", "A")
FIXED_ROWS = {
    "upper": ("005320000", "004432000", "008740000", "004544222", "005403000",
              "004675300", "005644320", "006876540", "327645222"),
    "lower": ("004545440", "004423220", "007373430", "004544220", "006644322",
              "005642200", "006845433", "008030000", "427866244"),
}
STATE = (
    "B3CONTROLS4\n" + CATALOG +
    "expression 0.25\n"
    "percussion enabled 1 harmonic third volume soft decay fast\n"
    "pedal drawbars 3 6\n"
    "manual upper selected B fixed_registration C# route_enabled 1\n"
    "bank A 8 0 3 0 1 0 0 2 0\n"
    "bank B 2 0 7 0 0 3 0 0 1\n"
    "manual lower selected A fixed_registration A route_enabled 1\n"
    "bank A 1 0 4 0 2 0 3 0 0\n"
    "bank B 0 3 1 0 6 0 2 0 4\n"
    "end\n"
)
HIDDEN_BANKS = {
    "upper": ("803010020", "207003001"),
    "lower": ("104020300", "031060204"),
}


def bank_events(frame, manual, bank, digits):
    return "".join(f"{frame} bank_drawbar {manual} {bank * 9 + index} {digit}\n"
                   for index, digit in enumerate(digits))


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON field: {key}")
        result[key] = value
    return result


def invalid_constant(value):
    raise ValueError(f"Nonfinite JSON constant: {value}")


class MutationWatch:
    """Observe create/delete/rename events, including staging later removed."""

    IS_DIRECTORY = 0x40000000
    CREATED = 0x00000100
    OVERFLOW = 0x00004000

    def __init__(self, directory):
        libc = ctypes.CDLL(None, use_errno=True)
        libc.inotify_init1.argtypes = [ctypes.c_int]
        libc.inotify_init1.restype = ctypes.c_int
        libc.inotify_add_watch.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32]
        libc.inotify_add_watch.restype = ctypes.c_int
        self.fd = libc.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
        if self.fd < 0:
            raise OSError(ctypes.get_errno(), "inotify_init1 failed")
        # IN_MOVED_FROM | IN_MOVED_TO | IN_CREATE | IN_DELETE | IN_MODIFY.
        if libc.inotify_add_watch(self.fd, os.fsencode(directory), 0x000003C2) < 0:
            error = ctypes.get_errno()
            self.close()
            raise OSError(error, "inotify_add_watch failed")

    def close(self):
        os.close(self.fd)

    def drain(self):
        events = []
        while True:
            try:
                data = os.read(self.fd, 65536)
            except BlockingIOError:
                return events
            if not data:
                return events
            offset = 0
            while offset < len(data):
                _, mask, _, length = struct.unpack_from("iIII", data, offset)
                offset += 16
                name = os.fsdecode(data[offset:offset + length].rstrip(b"\0"))
                offset += length
                if mask & self.OVERFLOW:
                    raise AssertionError("Filesystem observation overflowed")
                events.append((mask, name))


class RenderControlsAdmissionTests(unittest.TestCase):
    calls = 0

    @classmethod
    def setUpClass(cls):
        executable = "hammond_render.exe" if os.name == "nt" else "hammond_render"
        cls.renderer = Path(RENDERER_OVERRIDE or os.environ.get(
            "HAMMOND_RENDER_EXECUTABLE", ROOT / "build" / executable)).resolve()
        cls.profile_source = Path(PROFILE_OVERRIDE or os.environ.get(
            "HAMMOND_TEST_PROFILE", cls.renderer.parent / "nominal.b3p")).resolve()
        for path in (cls.renderer, cls.profile_source):
            if not path.is_file():
                raise RuntimeError(f"Missing configured input: {path}; build coherent inputs first")
        cls.profile_bytes = cls.profile_source.read_bytes()

    @classmethod
    def tearDownClass(cls):
        print(f"saved-controls independent admission: {cls.calls} actual CLI invocations")

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="hammond-controls-admission-")
        self.addCleanup(temporary.cleanup)
        self.work = Path(temporary.name)
        self.profile = self.work / "nominal profile.b3p"
        self.profile.write_bytes(self.profile_bytes)
        self.serial = 0

    def write(self, content, suffix):
        self.serial += 1
        path = self.work / f"input {self.serial}.{suffix}"
        path.write_bytes(content.encode("utf-8") if isinstance(content, str) else content)
        return path

    def output(self):
        self.serial += 1
        return self.work / f"output {self.serial}.wav"

    def snapshot(self):
        entries = {}
        for path in self.work.rglob("*"):
            mode = path.lstat().st_mode
            name = str(path.relative_to(self.work))
            if stat.S_ISREG(mode):
                entries[name] = ("file", hashlib.sha256(path.read_bytes()).hexdigest())
            elif stat.S_ISLNK(mode):
                entries[name] = ("link", os.readlink(path))
            else:
                entries[name] = ("other", stat.S_IFMT(mode))
        return entries

    def arguments(self, output, *, controls=None, score=None, frames=641, block=17):
        args = ["--profile", self.profile, "--output", output, "--frames", frames,
                "--sample-rate", 48000, "--block-size", block, "--seed", 191,
                "--contacts", "ideal"]
        if controls is not None:
            args += ["--controls", controls]
        if score is not None:
            args += ["--events", score]
        return list(map(str, args))

    def invoke(self, arguments):
        type(self).calls += 1
        return subprocess.run([str(self.renderer), *arguments], cwd=self.work,
                              capture_output=True, timeout=15, check=False)

    def render(self, text, *, controls=None, block=17):
        score = self.write(text, "events")
        output = self.output()
        before = self.snapshot()
        result = self.invoke(self.arguments(output, controls=controls, score=score, block=block))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stderr, b"")
        self.assertEqual(result.stdout.count(b"\n"), 1)
        report = json.loads(result.stdout.decode("utf-8"), object_pairs_hook=strict_object,
                            parse_constant=invalid_constant)
        after = self.snapshot()
        del after[output.name]
        self.assertEqual(after, before, "Rendering changed inputs or left staging")
        wav = output.read_bytes()
        self.assertEqual(len(wav), 44 + 641 * 4)
        samples = struct.unpack_from("<1282h", wav, 44)
        self.assertEqual(samples[::2], samples[1::2])
        self.assertEqual(report["status"], "ok")
        self.assertEqual(report["evidence_status"], "unmeasured")
        self.assertEqual(report["render_schema_version"], 6 if controls is not None else 3)
        self.assertEqual(report["clipped_frames"], 0)
        return wav, samples[::2], report

    def provenance(self, report, path, state):
        self.assertEqual(report["controls"], {
            "schema_version": 1,
            "restore_policy": "full-state-including-expression",
            "path": str(path.resolve()),
            "source_version": 4,
            "source_bytes": len(state.encode("utf-8")),
            "canonical_b3controls4": state,
        })

    def test_all_restored_fixed_modes_match_literal_rows_and_retained_banks(self):
        for manual, rows in FIXED_ROWS.items():
            for selection, (key, row) in enumerate(zip(KEYS, rows), 1):
                with self.subTest(manual=manual, fixed=key):
                    old = "C#" if manual == "upper" else "A"
                    state = STATE.replace(f"fixed_registration {old}",
                                          f"fixed_registration {key}", 1)
                    controls = self.write(state, "b3controls")
                    notes = "".join(f"0 note_on {manual} {note} 100\n"
                                    for note in (36, 60, 96))
                    release = "".join(f"577 note_off {manual} {note} 0\n"
                                      for note in (36, 60, 96))
                    actual_score = (notes + f"64 cancel {manual} 0 0\n"
                                    f"127 select_preset {manual} 0 {selection}\n"
                                    f"255 select_bank {manual} 0 1\n"
                                    f"383 select_bank {manual} 0 0\n" + release)
                    # The reference never selects a fixed preset or restores
                    # controls. It sounds literal A, then the two original
                    # hidden banks. A is restored before its later reveal.
                    bank_a, bank_b = HIDDEN_BANKS[manual]
                    reference = (
                        bank_events(0, manual, 0, row) + bank_events(0, manual, 1, bank_b) +
                        f"0 select_bank {manual} 0 0\n"
                        "0 percussion upper 0 1\n0 percussion upper 1 1\n"
                        "0 percussion upper 2 1\n0 percussion upper 3 1\n"
                        "0 expression upper 0 0.25\n" + notes +
                        f"64 cancel {manual} 0 0\n127 select_bank {manual} 0 0\n" +
                        bank_events(255, manual, 0, bank_a) +
                        f"255 select_bank {manual} 0 1\n383 select_bank {manual} 0 0\n" + release)
                    actual, samples, report = self.render(actual_score, controls=controls)
                    expected, _, _ = self.render(reference, block=127)
                    self.assertEqual(actual, expected)
                    for start, end in ((0, 64), (127, 255), (255, 383), (383, 577)):
                        self.assertTrue(any(samples[start:end]), (manual, key, start, end))
                    self.assertFalse(any(samples[64:127]), "Cancel must retain held notes silently")
                    self.provenance(report, controls, state)

    def test_replacing_every_saved_field_at_zero_keeps_initial_provenance(self):
        state = STATE.replace("fixed_registration C# route_enabled 1",
                              "fixed_registration C# route_enabled 0")
        controls = self.write(state, "b3controls")
        # Deliberately changes every bank position, remembered selector, fixed
        # mode, route, pedal, percussion setting and expression from the input.
        replacement = (
            bank_events(0, "upper", 0, "125242342") +
            bank_events(0, "upper", 1, "413254126") +
            bank_events(0, "lower", 0, "325361421") +
            bank_events(0, "lower", 1, "542317523") +
            "0 select_bank upper 0 0\n0 select_bank lower 0 1\n"
            "0 select_preset lower 0 6\n0 cancel lower 0 0\n"
            "0 percussion upper 0 0\n0 percussion upper 1 0\n"
            "0 percussion upper 2 0\n0 percussion upper 3 0\n"
            "0 pedal_drawbar lower 0 1\n0 pedal_drawbar lower 1 8\n"
            "0 expression upper 0 0.5\n"
        )
        phrase = ("0 note_on upper 60 100\n0 note_on lower 48 100\n"
                  "0 pedal_on lower 1 100\n127 select_bank lower 0 1\n"
                  "255 select_bank upper 0 1\n383 select_bank lower 0 0\n"
                  "577 all_notes_off upper 0 0\n577 all_notes_off lower 0 0\n"
                  "577 pedal_all_notes_off lower 0 0\n")
        actual, samples, report = self.render(replacement + phrase, controls=controls)
        expected, _, _ = self.render(replacement + phrase, block=127)
        self.assertEqual(actual, expected)
        self.assertTrue(any(samples))
        self.provenance(report, controls, state)

    def test_empty_score_restores_no_held_notes_or_percussion_history(self):
        state = STATE.replace("fixed_registration C#", "fixed_registration none")
        controls = self.write(state, "b3controls")
        _, samples, report = self.render("# no notes are present\n\n", controls=controls)
        self.assertFalse(any(samples))
        self.assertEqual(report["peak"], 0)
        self.assertEqual(report["rms"], 0)
        self.provenance(report, controls, state)

    @unittest.skipUnless(sys.platform.startswith("linux"), "Linux inotify observation")
    def test_invalid_inputs_precede_even_temporary_output_mutation(self):
        controls = self.write(STATE, "b3controls")
        invalid_controls = self.write(STATE.replace("B3CONTROLS4", "B3CONTROLS5"), "b3controls")
        invalid_profile = self.write("not a compiled profile\n", "b3p")
        invalid_score = self.write("0 note_on upper 60 100\n640 unknown upper 0 0\n", "events")
        invalid_leakage = self.write("not a leakage profile\n", "b3leakage")
        watch = MutationWatch(self.work)
        self.addCleanup(watch.close)
        # Positive witness: this watch sees a successful renderer's staging and
        # publication; a silent observer cannot make the rejection cases pass.
        self.render("", controls=controls)
        self.assertTrue(any(mask & MutationWatch.CREATED and mask & MutationWatch.IS_DIRECTORY
                            for mask, _ in watch.drain()), "Watch must see renderer-created staging")
        cases = []
        cases.append(self.arguments(self.output(), controls=invalid_controls))
        bad_profile = self.arguments(self.output(), controls=controls)
        bad_profile[bad_profile.index("--profile") + 1] = str(invalid_profile)
        cases.append(bad_profile)
        cases.append(self.arguments(self.output(), controls=controls, score=invalid_score))
        cases.append(self.arguments(self.output(), controls=controls) +
                     ["--source-leakage", str(invalid_leakage), "--leakage-input-gain", "0.5"])
        for index, arguments in enumerate(cases):
            with self.subTest(input=index):
                before = self.snapshot()
                self.assertEqual(watch.drain(), [])
                result = self.invoke(arguments)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertEqual(result.stdout, b"")
                self.assertTrue(result.stderr)
                self.assertEqual(watch.drain(), [], "Refusal created, deleted, moved or modified a file")
                self.assertEqual(self.snapshot(), before)

    @unittest.skipUnless(sys.platform.startswith("linux"), "Linux observed publication race")
    def test_destination_appearing_after_preflight_is_never_replaced(self):
        controls = self.write(STATE, "b3controls")
        output = self.output()
        before = self.snapshot()
        watch = MutationWatch(self.work)
        self.addCleanup(watch.close)
        type(self).calls += 1
        process = subprocess.Popen(
            [str(self.renderer), *self.arguments(output, controls=controls,
                                                frames=1200000, block=1)],
            cwd=self.work, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stopped = False
        try:
            self.assertTrue(select.select([watch.fd], [], [], 5)[0], "No staging event observed")
            events = watch.drain()
            self.assertTrue(any(mask & MutationWatch.CREATED and mask & MutationWatch.IS_DIRECTORY
                                for mask, _ in events), "Must observe staging after preflight")
            os.kill(process.pid, signal.SIGSTOP)
            deadline = time.monotonic() + 2
            while time.monotonic() < deadline:
                pid, status = os.waitpid(process.pid, os.WUNTRACED | os.WNOHANG)
                if pid:
                    self.assertTrue(os.WIFSTOPPED(status), "Renderer finished before controlled race")
                    stopped = True
                    break
                time.sleep(0.001)
            self.assertTrue(stopped, "Could not hold renderer after observed preflight")
            self.assertFalse(output.exists(), "Race must begin before publication")
            sentinel = b"destination created after renderer preflight; preserve every byte\n"
            with output.open("xb") as stream:
                stream.write(sentinel)
            original = output.stat()
            os.kill(process.pid, signal.SIGCONT)
            stopped = False
            # Publication follows the full 1.2M-frame/block-1 render. A measured
            # Debug ASan/UBSan completion exceeded 16s, so reserve 45s here;
            # the suite retains its 90s CTest bound and separate staging,
            # stop-confirmation, small-render and cleanup guards.
            stdout, stderr = process.communicate(timeout=45)
            self.assertEqual(process.returncode, 1, stdout + stderr)
            self.assertEqual(stdout, b"")
            self.assertIn(b"Cannot publish WAV without overwriting", stderr)
            self.assertEqual(output.read_bytes(), sentinel)
            self.assertEqual((output.stat().st_dev, output.stat().st_ino),
                             (original.st_dev, original.st_ino))
            after = self.snapshot()
            del after[output.name]
            self.assertEqual(after, before, "Publication refusal changed inputs or left staging")
        finally:
            if stopped:
                os.kill(process.pid, signal.SIGCONT)
            if process.poll() is None:
                process.kill()
            process.communicate(timeout=5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--renderer")
    parser.add_argument("--profile")
    arguments, remaining = parser.parse_known_args()
    RENDERER_OVERRIDE = arguments.renderer
    PROFILE_OVERRIDE = arguments.profile
    unittest.main(argv=[__file__, *remaining])
